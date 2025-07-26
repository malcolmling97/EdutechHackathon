"""
File routes for the EdutechHackathon API.

Endpoints:
- POST /files/upload - Upload files to folder
- GET /folders/{folderId}/files - List files in folder  
- GET /files/{id} - Get file metadata
- GET /files/{id}/content - Get file content
- DELETE /files/{id} - Delete file

Based on API_SPECIFICATION.md section 5.4 and BACKEND_DATA_FLOWS.md section 5.
"""
from typing import List, Optional
from fastapi import (
    APIRouter, 
    Depends, 
    HTTPException, 
    status, 
    Query, 
    Path, 
    Form, 
    File, 
    UploadFile
)
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.schemas.file import (
    FileUploadResponse,
    FileListResponse,
    FileResponseWrapper,
    FileContentWrapper,
    FileContentResponse
)
from app.services.file import get_file_service


router = APIRouter()


@router.post(
    "/upload",
    response_model=FileUploadResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload files to folder",
    description="Upload one or more files to a specified folder. Supports PDF, DOCX, TXT, and MD files up to 25MB each."
)
async def upload_files(
    folder_id: str = Form(..., description="Target folder ID"),
    files: List[UploadFile] = File(..., description="Files to upload"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Upload files to a folder.
    
    - **folder_id**: Target folder ID (form field)
    - **files**: One or more files to upload (multipart/form-data)
    
    Validates file types, sizes, and security constraints before uploading.
    Extracts text content for AI processing asynchronously.
    
    Returns list of uploaded file metadata.
    """
    if not files:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="No files provided"
        )
    
    file_service = get_file_service(db)
    
    try:
        uploaded_files = await file_service.upload_files(files, folder_id, current_user)
        return FileUploadResponse(data=uploaded_files)
    except HTTPException:
        # Re-raise known HTTP exceptions
        raise
    except Exception as e:
        # Handle unexpected errors
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"File upload failed: {str(e)}"
        )


# This route moved to folders.py to match API specification
# GET /api/v1/folders/{folder_id}/files


@router.get(
    "/{file_id}",
    response_model=FileResponseWrapper,
    status_code=status.HTTP_200_OK,
    summary="Get file metadata",
    description="Get metadata for a specific file by ID."
)
async def get_file_metadata(
    file_id: str = Path(..., description="File ID"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get file metadata by ID.
    
    - **file_id**: Unique file identifier
    
    Returns file metadata including name, size, MIME type, and upload timestamp.
    """
    file_service = get_file_service(db)
    
    try:
        file_data = file_service.get_file_metadata(file_id, current_user)
        return FileResponseWrapper(data=file_data)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get file metadata: {str(e)}"
        )


@router.get(
    "/{file_id}/content",
    response_model=FileContentWrapper,
    status_code=status.HTTP_200_OK,
    summary="Get file content",
    description="Get extracted text content of a file by ID."
)
async def get_file_content(
    file_id: str = Path(..., description="File ID"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get file content by ID.
    
    - **file_id**: Unique file identifier
    
    Returns extracted text content and MIME type.
    Content extraction is performed during upload for supported file types.
    """
    file_service = get_file_service(db)
    
    try:
        content, mime_type = file_service.get_file_content(file_id, current_user)
        
        return FileContentWrapper(
            data=FileContentResponse(
                content=content,
                mime_type=mime_type
            )
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get file content: {str(e)}"
        )


@router.delete(
    "/{file_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete file",
    description="Delete a file by ID. Supports both soft delete (default) and hard delete (force=true)."
)
async def delete_file(
    file_id: str = Path(..., description="File ID"),
    force: bool = Query(False, description="If true, permanently delete file and remove from storage"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete file by ID.
    
    - **file_id**: Unique file identifier
    - **force**: If true, perform hard delete (remove from storage); if false, soft delete
    
    Soft delete (default): Marks file as deleted but keeps it in database and storage.
    Hard delete (force=true): Permanently removes file from both database and storage.
    """
    file_service = get_file_service(db)
    
    try:
        file_service.delete_file(file_id, current_user, force)
        # 204 No Content - successful deletion with no response body
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete file: {str(e)}"
        )


# Additional utility endpoints for file management

# File count endpoint also moved to folders.py 