"""
Flashcard routes for the EdutechHackathon API.

Endpoints:
- POST /spaces/{spaceId}/flashcards - Generate flashcards from selected files + params
- GET /spaces/{spaceId}/flashcards - List flashcards
- GET /flashcards/{id} - Flashcard detail
- PATCH /flashcards/{id} - Update flashcard deck or individual cards
- DELETE /flashcards/{id} - Delete flashcard deck
- POST /flashcards/{id}/shuffle - Get shuffled card order for study session
"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query, Path, Response
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.schemas.flashcard import (
    FlashcardCreate,
    FlashcardListResponse,
    FlashcardResponseWrapper,
    FlashcardUpdate,
    FlashcardShuffleResponseWrapper
)
from app.services.flashcard import FlashcardService


router = APIRouter()


@router.post(
    "/spaces/{space_id}/flashcards",
    response_model=FlashcardResponseWrapper,
    status_code=status.HTTP_201_CREATED,
    summary="Generate flashcards",
    description="Generate a new flashcard deck from selected files with customizable parameters using AI."
)
async def generate_flashcards(
    space_id: str = Path(..., description="Space UUID"),
    flashcard_data: FlashcardCreate = ...,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Generate a new flashcard deck from file content using AI.
    
    - **space_id**: UUID of the parent space
    - **title**: Flashcard deck title (required)
    - **fileIds**: List of file UUIDs to generate flashcards from (required)
    - **cardCount**: Number of cards to generate (default: 20, max: 100)
    - **cardTypes**: Types of cards to include (default: ["mcq", "tf"])
    - **difficulty**: Flashcard difficulty level (default: "medium")
    
    Returns the generated flashcard deck with cards and metadata.
    
    **Example Request:**
    ```json
    {
        "title": "Biology Terms Set 1",
        "fileIds": ["uuid1", "uuid2"],
        "cardCount": 20,
        "cardTypes": ["mcq", "tf"],
        "difficulty": "medium"
    }
    ```
    """
    flashcard = FlashcardService.generate_flashcards(
        db=db,
        user=current_user,
        space_id=space_id,
        flashcard_data=flashcard_data
    )
    
    return FlashcardResponseWrapper(data=flashcard)


@router.get(
    "/spaces/{space_id}/flashcards",
    response_model=FlashcardListResponse,
    status_code=status.HTTP_200_OK,
    summary="List flashcards",
    description="Get a paginated list of flashcard decks in a space owned by the current user."
)
async def list_flashcards(
    space_id: str = Path(..., description="Space UUID"),
    page: int = Query(1, ge=1, description="Page number (1-based)"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    List flashcard decks in a space for the current user.
    
    - **space_id**: UUID of the parent space
    - **page**: Page number starting from 1
    - **limit**: Number of items per page (1-100)
    
    Returns a paginated list of flashcard decks with metadata.
    
    **Response includes:**
    - Flashcard metadata (id, title, creation date, update date)
    - Pagination information (page, limit, total)
    """
    return FlashcardService.list_flashcards(
        db=db,
        user=current_user,
        space_id=space_id,
        page=page,
        limit=limit
    )


@router.get(
    "/flashcards/{flashcard_id}",
    response_model=FlashcardResponseWrapper,
    status_code=status.HTTP_200_OK,
    summary="Get flashcard detail",
    description="Retrieve a specific flashcard deck with all cards and metadata."
)
async def get_flashcard(
    flashcard_id: str = Path(..., description="Flashcard UUID"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get detailed information about a specific flashcard deck.
    
    - **flashcard_id**: UUID of the flashcard deck to retrieve
    
    Returns complete flashcard data including:
    - Flashcard metadata (id, title, creation date, update date)
    - All cards with front/back content, difficulty, and tags
    - Source file references
    
    **Note:** Only accessible to the owner of the flashcard deck.
    """
    flashcard = FlashcardService.get_flashcard(
        db=db,
        user=current_user,
        flashcard_id=flashcard_id
    )
    
    return FlashcardResponseWrapper(data=flashcard)


@router.patch(
    "/flashcards/{flashcard_id}",
    response_model=FlashcardResponseWrapper,
    status_code=status.HTTP_200_OK,
    summary="Update flashcard deck",
    description="Update a flashcard deck title or individual cards."
)
async def update_flashcard(
    flashcard_id: str = Path(..., description="Flashcard UUID"),
    update_data: FlashcardUpdate = ...,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update a flashcard deck or individual cards.
    
    - **flashcard_id**: UUID of the flashcard deck to update
    - **title**: New title for the flashcard deck (optional)
    - **cards**: New cards array to replace existing cards (optional)
    
    **Update Options:**
    - Update only the title
    - Update only the cards
    - Update both title and cards
    
    **Example Request:**
    ```json
    {
        "title": "Updated Biology Terms",
        "cards": [
            {
                "id": "card1",
                "front": "What is chlorophyll?",
                "back": "A green pigment found in plants",
                "difficulty": "easy",
                "tags": ["photosynthesis", "pigments"]
            }
        ]
    }
    ```
    
    **Note:** Only accessible to the owner of the flashcard deck.
    """
    flashcard = FlashcardService.update_flashcard(
        db=db,
        user=current_user,
        flashcard_id=flashcard_id,
        update_data=update_data
    )
    
    return FlashcardResponseWrapper(data=flashcard)


@router.post(
    "/flashcards/{flashcard_id}/shuffle",
    response_model=FlashcardShuffleResponseWrapper,
    status_code=status.HTTP_200_OK,
    summary="Shuffle flashcards",
    description="Get a shuffled order of cards for study sessions."
)
async def shuffle_flashcards(
    flashcard_id: str = Path(..., description="Flashcard UUID"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get a shuffled order of cards for study sessions.
    
    - **flashcard_id**: UUID of the flashcard deck to shuffle
    
    **Returns:**
    - **cardOrder**: Array of card IDs in shuffled order
    - **sessionId**: Unique identifier for this study session
    - **createdAt**: Timestamp when shuffle was created
    
    **Use Case:**
    - Frontend can use the shuffled order to present cards in random sequence
    - Session ID can be used to track study progress
    - Each call generates a new random order
    
    **Note:** Only accessible to the owner of the flashcard deck.
    """
    shuffle_result = FlashcardService.shuffle_flashcards(
        db=db,
        user=current_user,
        flashcard_id=flashcard_id
    )
    
    return FlashcardShuffleResponseWrapper(data=shuffle_result)


@router.delete(
    "/flashcards/{flashcard_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete flashcard deck",
    description="Delete a flashcard deck permanently."
)
async def delete_flashcard(
    flashcard_id: str = Path(..., description="Flashcard UUID"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete a flashcard deck.
    
    - **flashcard_id**: UUID of the flashcard deck to delete
    
    **Warning:** This operation is permanent and will:
    - Delete the flashcard deck and all cards
    - Remove all associated data
    
    **Note:** Only accessible to the owner of the flashcard deck.
    """
    FlashcardService.delete_flashcard(
        db=db,
        user=current_user,
        flashcard_id=flashcard_id
    )
    
    return Response(status_code=status.HTTP_204_NO_CONTENT) 