"""
File schemas for the EdutechHackathon API.

Pydantic models for file upload, response, and validation.
Based on API_SPECIFICATION.md and BACKEND_DATA_FLOWS.md.
"""
from datetime import datetime
from typing import List, Optional, Any, Dict
from pydantic import BaseModel, Field, validator
from uuid import UUID

from app.schemas.folder import PaginationMeta


class FileResponse(BaseModel):
    """
    Schema for file metadata response.
    
    Based on API_SPECIFICATION.md section 4.4 File schema.
    """
    
    id: str = Field(..., description="Unique file identifier")
    folder_id: str = Field(..., description="Parent folder identifier")
    name: str = Field(..., description="Original filename")
    mime_type: str = Field(..., description="File MIME type")
    size: int = Field(..., description="File size in bytes")
    created_at: datetime = Field(..., description="Upload timestamp")
    
    class Config:
        from_attributes = True
        
    @classmethod
    def from_model(cls, file_model):
        """Create FileResponse from File model instance."""
        return cls(
            id=str(file_model.id),
            folder_id=str(file_model.folder_id),
            name=file_model.name,
            mime_type=file_model.mime_type,
            size=file_model.size,
            created_at=file_model.created_at
        )


class FileContentResponse(BaseModel):
    """Schema for file content response."""
    
    content: str = Field(..., description="File text content")
    mime_type: str = Field(..., description="File MIME type")
    
    
class FileContentWrapper(BaseModel):
    """Wrapper for file content responses following API specification."""
    
    data: FileContentResponse = Field(..., description="File content data")


class FileListResponse(BaseModel):
    """Schema for file list responses with pagination."""
    
    data: List[FileResponse] = Field(..., description="List of files")
    meta: PaginationMeta = Field(..., description="Pagination metadata")


class FileResponseWrapper(BaseModel):
    """Wrapper for single file responses following API specification."""
    
    data: FileResponse = Field(..., description="File data")


class FileUploadResponse(BaseModel):
    """Schema for file upload response (multiple files)."""
    
    data: List[FileResponse] = Field(..., description="List of uploaded files")


class FileUploadRequest(BaseModel):
    """
    Schema for file upload validation.
    
    Note: This is mainly for documentation since file uploads use multipart/form-data.
    The actual validation happens in the endpoint.
    """
    
    folder_id: str = Field(..., description="Target folder ID")
    # files: List[UploadFile] - handled by FastAPI UploadFile


class FileValidationError(BaseModel):
    """Schema for file validation errors."""
    
    filename: str = Field(..., description="Name of the problematic file")
    error_code: str = Field(..., description="Error code")
    message: str = Field(..., description="Error message")


class FileUploadError(BaseModel):
    """Schema for file upload errors with file-specific details."""
    
    message: str = Field(..., description="General error message")
    files: Optional[List[FileValidationError]] = Field(None, description="File-specific errors")
    max_size: Optional[int] = Field(None, description="Maximum allowed file size")
    allowed_types: Optional[List[str]] = Field(None, description="Allowed file types")


# File upload constants and validators
ALLOWED_MIME_TYPES = [
    "application/pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "text/plain",
    "text/markdown"
]

MAX_FILE_SIZE = 26214400  # 25MB in bytes


def validate_file_type(mime_type: str) -> bool:
    """Validate if file MIME type is supported."""
    return mime_type in ALLOWED_MIME_TYPES


def validate_file_size(size: int) -> bool:
    """Validate if file size is within limits."""
    return size <= MAX_FILE_SIZE


def get_file_extension(filename: str) -> str:
    """Extract file extension from filename."""
    return filename.split('.')[-1].lower() if '.' in filename else ''


def is_safe_filename(filename: str) -> bool:
    """Check if filename is safe (no path traversal attacks)."""
    dangerous_chars = ['..', '/', '\\', '<', '>', ':', '"', '|', '?', '*']
    return not any(char in filename for char in dangerous_chars)


class FileMetrics(BaseModel):
    """Schema for file processing metrics and status."""
    
    total_files: int = Field(..., description="Total number of files processed")
    successful_uploads: int = Field(..., description="Number of successful uploads")
    failed_uploads: int = Field(..., description="Number of failed uploads")
    total_size: int = Field(..., description="Total size of uploaded files in bytes")
    processing_time: float = Field(..., description="Time taken to process uploads in seconds")


class FileSearchRequest(BaseModel):
    """Schema for file search requests."""
    
    query: Optional[str] = Field(None, description="Search query for file names")
    mime_types: Optional[List[str]] = Field(None, description="Filter by MIME types")
    min_size: Optional[int] = Field(None, description="Minimum file size filter")
    max_size: Optional[int] = Field(None, description="Maximum file size filter")
    date_from: Optional[datetime] = Field(None, description="Filter files from this date")
    date_to: Optional[datetime] = Field(None, description="Filter files to this date") 