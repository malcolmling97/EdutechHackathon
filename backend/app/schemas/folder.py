"""
Pydantic schemas for folder management endpoints.

Defines request and response models for:
- Folder creation
- Folder updates
- Folder responses
- Folder listings with pagination
"""
from datetime import datetime
from datetime import datetime
from typing import Optional, List
from uuid import UUID
from pydantic.functional_validators import BeforeValidator
from typing_extensions import Annotated

UUIDStr = Annotated[UUID, BeforeValidator(str)]
from pydantic import BaseModel, Field, field_validator, ConfigDict


class FolderCreate(BaseModel):
    """Schema for folder creation request."""
    
    title: str = Field(..., min_length=1, max_length=255, description="Folder title")
    description: Optional[str] = Field(None, max_length=1000, description="Optional folder description")
    
    @field_validator('title')
    @classmethod
    def validate_title(cls, v: str) -> str:
        """Validate title is not empty after stripping whitespace."""
        if not v.strip():
            raise ValueError('Title cannot be empty')
        return v.strip()

    @field_validator('description')
    @classmethod
    def validate_description(cls, v: Optional[str]) -> Optional[str]:
        """Validate and clean description."""
        if v is not None:
            return v.strip() if v.strip() else None
        return v


class FolderUpdate(BaseModel):
    """Schema for folder update request (partial update)."""
    
    title: Optional[str] = Field(None, min_length=1, max_length=255, description="Folder title")
    description: Optional[str] = Field(None, max_length=1000, description="Folder description")
    
    @field_validator('title')
    @classmethod
    def validate_title(cls, v: Optional[str]) -> Optional[str]:
        """Validate title is not empty after stripping whitespace."""
        if v is not None and not v.strip():
            raise ValueError('Title cannot be empty')
        return v.strip() if v else v

    @field_validator('description')
    @classmethod
    def validate_description(cls, v: Optional[str]) -> Optional[str]:
        """Validate and clean description."""
        if v is not None:
            return v.strip() if v.strip() else None
        return v


class FolderResponse(BaseModel):
    """Schema for folder data in responses."""
    
    id: UUIDStr = Field(..., description="Folder's unique identifier")
    owner_id: UUIDStr = Field(..., alias="ownerId", description="Owner's user ID")
    title: str = Field(..., description="Folder title")
    description: Optional[str] = Field(None, description="Folder description")
    created_at: datetime = Field(..., alias="createdAt", description="When the folder was created")
    
    model_config = ConfigDict(from_attributes=True, populate_by_name=True, json_encoders={datetime: lambda v: v.isoformat()})

    


class PaginationMeta(BaseModel):
    """Schema for pagination metadata."""
    
    page: int = Field(..., description="Current page number")
    limit: int = Field(..., description="Items per page")
    total: int = Field(..., description="Total number of items")


class FolderListResponse(BaseModel):
    """Schema for folder list responses with pagination."""
    
    data: List[FolderResponse] = Field(..., description="List of folders")
    meta: PaginationMeta = Field(..., description="Pagination metadata")


class FolderResponseWrapper(BaseModel):
    """Wrapper for single folder responses following API specification."""
    
    data: FolderResponse = Field(..., description="Folder data")


class ErrorDetail(BaseModel):
    """Schema for error details."""
    
    code: str = Field(..., description="Error code")
    message: str = Field(..., description="Human-readable error message")
    details: Optional[dict] = Field(None, description="Additional error details")


class ErrorResponse(BaseModel):
    """Schema for error responses following API specification."""
    
    error: ErrorDetail = Field(..., description="Error information") 