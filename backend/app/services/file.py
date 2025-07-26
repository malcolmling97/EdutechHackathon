"""
File service for the EdutechHackathon API.

Business logic for file upload, storage, retrieval, and deletion.
Based on BACKEND_DATA_FLOWS.md section 5 - File Management Data Flows.
"""
import json
import uuid
import asyncio
from datetime import datetime
from typing import List, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc
from fastapi import HTTPException, status, UploadFile
import logging

from app.models.file import File
from app.models.folder import Folder
from app.models.user import User
from app.schemas.file import (
    FileResponse, 
    FileListResponse, 
    PaginationMeta,
    validate_file_type,
    validate_file_size,
    is_safe_filename
)
from app.utils.file_processor import file_processor

logger = logging.getLogger(__name__)


class FileService:
    """Service class for file management operations."""
    
    def __init__(self, db: Session):
        """Initialize file service with database session."""
        self.db = db
    
    async def upload_files(
        self, 
        files: List[UploadFile], 
        folder_id: str, 
        user: User
    ) -> List[FileResponse]:
        """
        Upload multiple files to a folder.
        
        Based on BACKEND_DATA_FLOWS.md section 5.1 - Upload Files Flow.
        
        Args:
            files: List of uploaded files
            folder_id: Target folder ID
            user: Current authenticated user
            
        Returns:
            List of FileResponse objects
            
        Raises:
            HTTPException: Various error conditions
        """
        # Verify folder exists and user owns it
        folder = self._get_folder_or_404(folder_id, user)
        
        uploaded_files = []
        failed_files = []
        
        for file in files:
            try:
                # Validate individual file
                await self._validate_upload_file(file)
                
                # Save file to storage
                storage_path, unique_filename = await file_processor.save_uploaded_file(file)
                
                # Detect MIME type
                mime_type = file_processor.detect_mime_type(storage_path)
                
                # Get file size
                file_size = file_processor.get_file_size(storage_path)
                
                # Extract text content asynchronously
                text_content = await file_processor.extract_text_content(storage_path, mime_type)
                
                # Create file record in database
                file_record = File(
                    folder_id=folder.id,
                    name=file.filename,
                    mime_type=mime_type,
                    size=file_size,
                    path=storage_path,
                    text_content=text_content,
                    vector_ids="[]"  # Empty for now, AI/ML engineer will populate
                )
                
                self.db.add(file_record)
                self.db.commit()
                self.db.refresh(file_record)
                
                uploaded_files.append(FileResponse.from_model(file_record))
                
                logger.info(f"Successfully uploaded file {file.filename} for user {user.id}")
                
            except HTTPException:
                # Re-raise HTTP exceptions
                raise
            except Exception as e:
                logger.error(f"Error uploading file {file.filename}: {e}")
                failed_files.append(file.filename)
                
                # Clean up file if it was saved but database insert failed
                try:
                    if 'storage_path' in locals():
                        file_processor.delete_file(storage_path)
                except:
                    pass
        
        if failed_files and not uploaded_files:
            # All files failed
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to upload files: {', '.join(failed_files)}"
            )
        
        return uploaded_files
    
    def list_files_in_folder(
        self, 
        folder_id: str, 
        user: User,
        page: int = 1,
        limit: int = 20
    ) -> FileListResponse:
        """
        List files in a folder with pagination.
        
        Based on BACKEND_DATA_FLOWS.md section 5.2 - List Files in Folder Flow.
        
        Args:
            folder_id: Folder ID to list files from
            user: Current authenticated user
            page: Page number (1-based)
            limit: Items per page
            
        Returns:
            FileListResponse with paginated files
        """
        # Verify folder exists and user owns it
        folder = self._get_folder_or_404(folder_id, user)
        
        # Calculate offset
        offset = (page - 1) * limit
        
        # Query files with pagination
        query = self.db.query(File).filter(
            and_(
                File.folder_id == folder.id,
                File.deleted_at.is_(None)  # Only active files
            )
        ).order_by(desc(File.created_at))
        
        # Get total count
        total_count = query.count()
        
        # Apply pagination
        files = query.offset(offset).limit(limit).all()
        
        # Convert to response objects
        file_responses = [FileResponse.from_model(file) for file in files]
        
        return FileListResponse(
            data=file_responses,
            meta=PaginationMeta(
                page=page,
                limit=limit,
                total=total_count
            )
        )
    
    def get_file_metadata(self, file_id: str, user: User) -> FileResponse:
        """
        Get file metadata by ID.
        
        Based on BACKEND_DATA_FLOWS.md section 5.3 - Get File Metadata Flow.
        
        Args:
            file_id: File ID
            user: Current authenticated user
            
        Returns:
            FileResponse with file metadata
        """
        file = self._get_file_or_404(file_id, user)
        return FileResponse.from_model(file)
    
    def get_file_content(self, file_id: str, user: User) -> Tuple[str, str]:
        """
        Get file content by ID.
        
        Based on BACKEND_DATA_FLOWS.md section 5.4 - Get File Content Flow.
        
        Args:
            file_id: File ID
            user: Current authenticated user
            
        Returns:
            Tuple of (content, mime_type)
        """
        file = self._get_file_or_404(file_id, user)
        
        if not file.text_content:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="File content not available or text extraction failed"
            )
        
        return file.text_content, file.mime_type
    
    def delete_file(self, file_id: str, user: User, force: bool = False) -> None:
        """
        Delete file by ID.
        
        Based on BACKEND_DATA_FLOWS.md section 5.5 - Delete File Flow.
        
        Args:
            file_id: File ID
            user: Current authenticated user
            force: If True, perform hard delete; if False, soft delete
        """
        file = self._get_file_or_404(file_id, user)
        
        if force:
            # Hard delete: Remove file from storage and database
            try:
                file_processor.delete_file(file.path)
            except Exception as e:
                logger.warning(f"Could not delete file from storage: {e}")
            
            self.db.delete(file)
            logger.info(f"Hard deleted file {file.id} for user {user.id}")
        else:
            # Soft delete: Mark as deleted
            file.soft_delete()
            logger.info(f"Soft deleted file {file.id} for user {user.id}")
        
        self.db.commit()
    
    def _get_folder_or_404(self, folder_id: str, user: User) -> Folder:
        """
        Get folder by ID and verify user ownership.
        
        Args:
            folder_id: Folder ID
            user: Current authenticated user
            
        Returns:
            Folder object
            
        Raises:
            HTTPException: If folder not found or access denied
        """
        try:
            folder_uuid = uuid.UUID(folder_id)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail={
                    "error": {
                        "code": "INVALID_UUID",
                        "message": "Invalid folder ID format",
                        "details": {"folder_id": folder_id}
                    }
                }
            )
        
        folder = self.db.query(Folder).filter(
            and_(
                Folder.id == folder_uuid,
                Folder.deleted_at.is_(None)
            )
        ).first()
        
        if not folder:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "error": {
                        "code": "FOLDER_NOT_FOUND",
                        "message": "Folder not found",
                        "details": {"folder_id": folder_id}
                    }
                }
            )
        
        if folder.owner_id != user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "error": {
                        "code": "FORBIDDEN",
                        "message": "Access denied to this folder",
                        "details": {"folder_id": folder_id}
                    }
                }
            )
        
        return folder
    
    def _get_file_or_404(self, file_id: str, user: User) -> File:
        """
        Get file by ID and verify user ownership.
        
        Args:
            file_id: File ID
            user: Current authenticated user
            
        Returns:
            File object
            
        Raises:
            HTTPException: If file not found or access denied
        """
        try:
            file_uuid = uuid.UUID(file_id)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail={
                    "error": {
                        "code": "INVALID_UUID",
                        "message": "Invalid file ID format",
                        "details": {"file_id": file_id}
                    }
                }
            )
        
        # First check if file exists at all
        file = self.db.query(File).filter(
            and_(
                File.id == file_uuid,
                File.deleted_at.is_(None)
            )
        ).first()
        
        if not file:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "error": {
                        "code": "FILE_NOT_FOUND",
                        "message": "File not found",
                        "details": {"file_id": file_id}
                    }
                }
            )
        
        # Then check if user owns the parent folder
        folder = self.db.query(Folder).filter(
            and_(
                Folder.id == file.folder_id,
                Folder.deleted_at.is_(None)
            )
        ).first()
        
        if not folder or folder.owner_id != user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "error": {
                        "code": "FORBIDDEN",
                        "message": "You don't have permission to access this file",
                        "details": {"file_id": file_id}
                    }
                }
            )
        
        return file
    
    async def _validate_upload_file(self, file: UploadFile) -> None:
        """
        Validate uploaded file for security and constraints.
        
        Args:
            file: UploadFile instance
            
        Raises:
            HTTPException: If validation fails
        """
        # Check filename safety
        if not file.filename or not is_safe_filename(file.filename):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid or unsafe filename: {file.filename}"
            )
        
        # Check file size
        # Note: FastAPI doesn't provide file size directly, so we need to read and seek
        content = await file.read()
        file_size = len(content)
        await file.seek(0)  # Reset file pointer
        
        if not validate_file_size(file_size):
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail={
                    "error": {
                        "code": "FILE_TOO_LARGE",
                        "message": "Maximum upload size is 25 MB.",
                        "details": {
                            "max_size": 26214400,  # 25MB in bytes
                            "actual_size": file_size
                        }
                    }
                }
            )
        
        # Check MIME type (basic check based on filename)
        # More thorough check will be done after saving
        if file.content_type and not validate_file_type(file.content_type):
            raise HTTPException(
                status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                detail={
                    "error": {
                        "code": "UNSUPPORTED_FORMAT",
                        "message": "File format not supported",
                        "details": {
                            "supported_types": ["PDF", "DOCX", "TXT", "MD"],
                            "received_type": file.content_type
                        }
                    }
                }
            )


# Service factory function
def get_file_service(db: Session) -> FileService:
    """Create file service instance with database session."""
    return FileService(db) 