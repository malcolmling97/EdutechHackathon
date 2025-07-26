"""
Folder routes for the EdutechHackathon API.

Endpoints:
- GET /folders - List user folders with pagination and search
- POST /folders - Create new folder
- GET /folders/{id} - Get specific folder
- PATCH /folders/{id} - Update folder
- DELETE /folders/{id} - Delete folder
"""
from uuid import UUID
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query, Path, Response
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.schemas.folder import (
    FolderCreate,
    FolderUpdate,
    FolderListResponse,
    FolderResponseWrapper
)
from app.schemas.file import FileListResponse
from app.services.folder import FolderService


router = APIRouter()


@router.get(
    "",
    response_model=FolderListResponse,
    status_code=status.HTTP_200_OK,
    summary="List user folders",
    description="Get a paginated list of folders owned by the current user, with optional search."
)
async def list_folders(
    page: int = Query(1, ge=1, description="Page number (1-based)"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    q: Optional[str] = Query(None, description="Search query for folder titles"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    List folders for the current user.
    
    - **page**: Page number starting from 1
    - **limit**: Number of items per page (1-100)
    - **q**: Optional search term to filter folders by title (case-insensitive)
    
    Returns paginated list of folders with metadata.
    """
    return FolderService.list_folders(
        db=db,
        user=current_user,
        page=page,
        limit=limit,
        search_query=q
    )


@router.post(
    "",
    response_model=FolderResponseWrapper,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new folder",
    description="Create a new folder for the current user."
)
async def create_folder(
    folder_data: FolderCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new folder.
    
    - **title**: Folder title (required, 1-255 characters)
    - **description**: Optional folder description (max 1000 characters)
    
    Returns the created folder data.
    """
    folder_response = FolderService.create_folder(
        db=db,
        user=current_user,
        folder_data=folder_data
    )
    
    return FolderResponseWrapper(data=folder_response)


@router.get(
    "/{folder_id}",
    response_model=FolderResponseWrapper,
    status_code=status.HTTP_200_OK,
    summary="Get folder by ID",
    description="Get a specific folder by its ID. User must own the folder."
)
async def get_folder(
    folder_id: UUID = Path(..., description="Folder UUID"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get folder details by ID.
    
    - **folder_id**: UUID of the folder to retrieve
    
    Returns folder details if user owns the folder.
    """
    folder_response = FolderService.get_folder(
        db=db,
        user=current_user,
        folder_id=folder_id
    )
    
    return FolderResponseWrapper(data=folder_response)


@router.patch(
    "/{folder_id}",
    response_model=FolderResponseWrapper,
    status_code=status.HTTP_200_OK,
    summary="Update folder",
    description="Update folder title and/or description. User must own the folder."
)
async def update_folder(
    folder_id: UUID = Path(..., description="Folder UUID"),
    folder_data: FolderUpdate = ...,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update folder information.
    
    - **folder_id**: UUID of the folder to update
    - **title**: New folder title (optional, 1-255 characters)
    - **description**: New folder description (optional, max 1000 characters)
    
    Only provided fields will be updated. Returns updated folder data.
    """
    folder_response = FolderService.update_folder(
        db=db,
        user=current_user,
        folder_id=folder_id,
        folder_data=folder_data
    )
    
    return FolderResponseWrapper(data=folder_response)


@router.delete(
    "/{folder_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete folder",
    description="Delete a folder and all its contents. User must own the folder."
)
async def delete_folder(
    folder_id: UUID = Path(..., description="Folder UUID"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete folder.
    
    - **folder_id**: UUID of the folder to delete
    
    This will soft-delete the folder and cascade to delete all spaces and files
    within the folder. The operation cannot be undone.
    """
    FolderService.delete_folder(
        db=db,
        user=current_user,
        folder_id=folder_id
    )
    
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get(
    "/{folder_id}/files",
    response_model=FileListResponse,
    status_code=status.HTTP_200_OK,
    summary="List files in folder",
    description="Get a paginated list of files in a folder owned by the current user."
)
async def list_files_in_folder(
    folder_id: str = Path(..., description="Folder ID"),
    page: int = Query(1, ge=1, description="Page number (1-based)"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    List files in a folder.
    
    - **folder_id**: Folder ID to list files from
    - **page**: Page number starting from 1
    - **limit**: Number of items per page (1-100)
    
    Returns paginated list of files with metadata.
    """
    from app.services.file import get_file_service
    
    file_service = get_file_service(db)
    
    try:
        return file_service.list_files_in_folder(folder_id, current_user, page, limit)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list files: {str(e)}"
        ) 