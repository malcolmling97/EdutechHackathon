"""
Pydantic schemas for note management endpoints.

Defines request and response models for:
- Note generation
- Note updates
- Note responses
- Note listings with pagination
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from enum import Enum
from uuid import UUID

from pydantic import BaseModel, Field, ConfigDict, field_validator
from pydantic.functional_validators import BeforeValidator
from typing_extensions import Annotated

UUIDStr = Annotated[UUID, BeforeValidator(str)]


class NotesFormat(str, Enum):
    """Notes format enumeration matching the database model."""
    
    markdown = "markdown"
    bullet = "bullet"


class NotesCreate(BaseModel):
    """Schema for notes generation request."""
    
    file_ids: List[str] = Field(..., min_items=1, description="List of file UUIDs to generate notes from")
    format: NotesFormat = Field(NotesFormat.markdown, description="Format for the generated notes")
    
    @field_validator('file_ids')
    @classmethod
    def validate_file_ids(cls, v: List[str]) -> List[str]:
        """Validate that all file_ids are valid UUIDs."""
        if not v:
            raise ValueError('At least one file ID is required')
        
        validated_ids = []
        for file_id in v:
            try:
                # Validate UUID format
                uuid_obj = UUID(file_id)
                validated_ids.append(str(uuid_obj))
            except ValueError:
                raise ValueError(f'Invalid UUID format: {file_id}')
        
        return validated_ids


class NotesUpdate(BaseModel):
    """Schema for notes update request (partial update)."""
    
    content: Optional[str] = Field(None, min_length=1, description="Updated note content")
    
    @field_validator('content')
    @classmethod
    def validate_content(cls, v: Optional[str]) -> Optional[str]:
        """Validate content is not empty after stripping whitespace."""
        if v is not None:
            stripped = v.strip()
            if not stripped:
                raise ValueError('Content cannot be empty or contain only whitespace')
            return stripped
        return v


class NotesResponse(BaseModel):
    """Schema for note data in responses."""
    
    id: UUIDStr = Field(..., description="Note's unique identifier")
    space_id: UUIDStr = Field(..., alias="spaceId", description="Parent space ID")
    format: NotesFormat = Field(..., description="Note format")
    content: str = Field(..., description="Note content")
    created_at: datetime = Field(..., alias="createdAt", description="When the note was created")
    updated_at: datetime = Field(..., alias="updatedAt", description="When the note was last updated")
    
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class PaginationMeta(BaseModel):
    """Schema for pagination metadata."""
    
    page: int = Field(..., description="Current page number")
    limit: int = Field(..., description="Items per page")
    total: int = Field(..., description="Total number of items")


class NotesListResponse(BaseModel):
    """Schema for notes list responses with pagination."""
    
    data: List[NotesResponse] = Field(..., description="List of notes")
    meta: PaginationMeta = Field(..., description="Pagination metadata")


class NotesResponseWrapper(BaseModel):
    """Wrapper for single note responses following API specification."""
    
    data: NotesResponse = Field(..., description="Note data")


class ErrorDetail(BaseModel):
    """Schema for error details."""
    
    code: str = Field(..., description="Error code")
    message: str = Field(..., description="Human-readable error message")
    details: Optional[dict] = Field(None, description="Additional error details")


class ErrorResponse(BaseModel):
    """Schema for error responses following API specification."""
    
    error: ErrorDetail = Field(..., description="Error information") 