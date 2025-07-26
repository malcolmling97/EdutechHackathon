"""
Space routes for the EdutechHackathon API.

Endpoints:
- GET /folders/{folderId}/spaces - List spaces in folder with pagination and filtering
- POST /folders/{folderId}/spaces - Create new space
- GET /spaces/{id} - Get specific space
- PATCH /spaces/{id} - Update space
- DELETE /spaces/{id} - Delete space
"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query, Path, Response
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.models.space import SpaceType
from app.schemas.space import (
    SpaceCreate,
    SpaceUpdate,
    SpaceListResponse,
    SpaceResponseWrapper
)
from app.services.space import SpaceService


router = APIRouter()


@router.get(
    "/folders/{folder_id}/spaces",
    response_model=SpaceListResponse,
    status_code=status.HTTP_200_OK,
    summary="List spaces in folder",
    description="Get a paginated list of spaces in a folder owned by the current user, with optional type filtering."
)
async def list_spaces_in_folder(
    folder_id: str = Path(..., description="Folder UUID"),
    page: int = Query(1, ge=1, description="Page number (1-based)"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    type: Optional[SpaceType] = Query(None, description="Filter by space type"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    List spaces in a folder for the current user.
    
    - **folder_id**: UUID of the parent folder
    - **page**: Page number starting from 1
    - **limit**: Number of items per page (1-100)
    - **type**: Optional space type filter (chat, quiz, notes, openended, flashcards, studyguide)
    
    Returns paginated list of spaces with metadata.
    """
    return SpaceService.list_spaces(
        db=db,
        user=current_user,
        folder_id=folder_id,
        page=page,
        limit=limit,
        space_type=type
    )


@router.post(
    "/folders/{folder_id}/spaces",
    response_model=SpaceResponseWrapper,
    status_code=status.HTTP_201_CREATED,
    summary="Create space",
    description="Create a new space in a folder owned by the current user."
)
async def create_space(
    folder_id: str = Path(..., description="Folder UUID"),
    space_data: SpaceCreate = ...,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new space in the specified folder.
    
    - **folder_id**: UUID of the parent folder
    - **type**: Type of space to create (required)
    - **title**: Space title (required)
    - **settings**: Optional type-specific settings
    
    Returns the created space data.
    """
    space_response = SpaceService.create_space(
        db=db,
        user=current_user,
        folder_id=folder_id,
        space_data=space_data
    )
    
    return SpaceResponseWrapper(data=space_response)


@router.get(
    "/spaces/{space_id}",
    response_model=SpaceResponseWrapper,
    status_code=status.HTTP_200_OK,
    summary="Get space",
    description="Get a specific space by ID, ensuring user owns the parent folder."
)
async def get_space(
    space_id: str = Path(..., description="Space UUID"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get a specific space by ID.
    
    - **space_id**: UUID of the space to retrieve
    
    Returns the space data if user has access.
    """
    space_response = SpaceService.get_space(
        db=db,
        user=current_user,
        space_id=space_id
    )
    
    return SpaceResponseWrapper(data=space_response)


@router.patch(
    "/spaces/{space_id}",
    response_model=SpaceResponseWrapper,
    status_code=status.HTTP_200_OK,
    summary="Update space",
    description="Update a space's title and/or settings, ensuring user owns the parent folder."
)
async def update_space(
    space_id: str = Path(..., description="Space UUID"),
    space_data: SpaceUpdate = ...,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update an existing space.
    
    - **space_id**: UUID of the space to update
    - **title**: New space title (optional)
    - **settings**: New type-specific settings (optional)
    
    Returns the updated space data.
    """
    space_response = SpaceService.update_space(
        db=db,
        user=current_user,
        space_id=space_id,
        space_data=space_data
    )
    
    return SpaceResponseWrapper(data=space_response)


@router.delete(
    "/spaces/{space_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete space",
    description="Delete a space (soft delete), ensuring user owns the parent folder."
)
async def delete_space(
    space_id: str = Path(..., description="Space UUID"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete an existing space.
    
    - **space_id**: UUID of the space to delete
    
    Returns 204 No Content on successful deletion.
    This is a soft delete - the space is marked as deleted but not removed from the database.
    """
    SpaceService.delete_space(
        db=db,
        user=current_user,
        space_id=space_id
    )
    
    return Response(status_code=status.HTTP_204_NO_CONTENT) 