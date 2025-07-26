"""
Notes routes for the EdutechHackathon API.

Endpoints:
- POST /spaces/{spaceId}/notes - Generate notes from files
- GET /spaces/{spaceId}/notes - List notes in space with pagination
- GET /notes/{id} - Get specific note
- PATCH /notes/{id} - Update note content
- DELETE /notes/{id} - Delete note
"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query, Path, Response
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.schemas.note import (
    NotesCreate,
    NotesUpdate,
    NotesListResponse,
    NotesResponseWrapper
)
from app.services.note import NotesService


router = APIRouter()


@router.post(
    "/spaces/{space_id}/notes",
    response_model=NotesResponseWrapper,
    status_code=status.HTTP_201_CREATED,
    summary="Generate notes",
    description="Generate notes from selected files in a notes space using AI (mock implementation for backend developer)."
)
async def generate_notes(
    space_id: str = Path(..., description="Space UUID"),
    notes_data: NotesCreate = ...,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Generate notes from files in a notes space.
    
    **Backend Developer Implementation:**
    - Validates space ownership and type (must be 'notes')
    - Validates file ownership and existence
    - Creates mock AI-generated content (placeholder for AI/ML Engineer)
    - Stores note in database
    
    **Parameters:**
    - **space_id**: UUID of the notes space
    - **file_ids**: List of file UUIDs to generate notes from (required)
    - **format**: Format for the generated notes (markdown or bullet, default: markdown)
    
    **Returns:**
    Created note with generated content.
    
    **Note:** The AI content generation is currently mocked. 
    Actual AI integration will be implemented by the AI/ML Engineer.
    """
    notes_response = NotesService.generate_notes(
        db=db,
        user=current_user,
        space_id=space_id,
        notes_data=notes_data
    )
    
    return NotesResponseWrapper(data=notes_response)


@router.get(
    "/spaces/{space_id}/notes",
    response_model=NotesListResponse,
    status_code=status.HTTP_200_OK,
    summary="List notes",
    description="Get a paginated list of notes in a notes space owned by the current user."
)
async def list_notes(
    space_id: str = Path(..., description="Space UUID"),
    page: int = Query(1, ge=1, description="Page number (1-based)"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    List notes in a notes space for the current user.
    
    **Parameters:**
    - **space_id**: UUID of the notes space
    - **page**: Page number starting from 1
    - **limit**: Number of items per page (1-100)
    
    **Returns:**
    Paginated list of notes with metadata.
    
    **Requirements:**
    - Space must be of type 'notes'
    - User must own the parent folder
    """
    return NotesService.list_notes(
        db=db,
        user=current_user,
        space_id=space_id,
        page=page,
        limit=limit
    )


@router.get(
    "/notes/{note_id}",
    response_model=NotesResponseWrapper,
    status_code=status.HTTP_200_OK,
    summary="Get note",
    description="Get a specific note by ID, ensuring user owns the parent folder."
)
async def get_note(
    note_id: str = Path(..., description="Note UUID"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get a specific note by ID.
    
    **Parameters:**
    - **note_id**: UUID of the note to retrieve
    
    **Returns:**
    The note data if user has access.
    
    **Access Control:**
    User must own the folder containing the space that contains the note.
    """
    notes_response = NotesService.get_note(
        db=db,
        user=current_user,
        note_id=note_id
    )
    
    return NotesResponseWrapper(data=notes_response)


@router.patch(
    "/notes/{note_id}",
    response_model=NotesResponseWrapper,
    status_code=status.HTTP_200_OK,
    summary="Update note",
    description="Update a note's content, ensuring user owns the parent folder."
)
async def update_note(
    note_id: str = Path(..., description="Note UUID"),
    notes_data: NotesUpdate = ...,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update an existing note.
    
    **Parameters:**
    - **note_id**: UUID of the note to update
    - **content**: New note content (optional)
    
    **Returns:**
    The updated note data.
    
    **Validation:**
    - Content cannot be empty or contain only whitespace
    - User must own the folder containing the space that contains the note
    
    **Note:** Only the content field can be updated. Format and other metadata are immutable.
    """
    notes_response = NotesService.update_note(
        db=db,
        user=current_user,
        note_id=note_id,
        notes_data=notes_data
    )
    
    return NotesResponseWrapper(data=notes_response)


@router.delete(
    "/notes/{note_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete note",
    description="Delete a note (soft delete), ensuring user owns the parent folder."
)
async def delete_note(
    note_id: str = Path(..., description="Note UUID"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete an existing note.
    
    **Parameters:**
    - **note_id**: UUID of the note to delete
    
    **Returns:**
    204 No Content on successful deletion.
    
    **Implementation:**
    This is a soft delete - the note is marked as deleted but not removed from the database.
    The note will cascade delete when the parent space is deleted.
    
    **Access Control:**
    User must own the folder containing the space that contains the note.
    """
    NotesService.delete_note(
        db=db,
        user=current_user,
        note_id=note_id
    )
    
    return Response(status_code=status.HTTP_204_NO_CONTENT) 