"""
Pydantic schemas for space management endpoints.

Defines request and response models for:
- Space creation
- Space updates
- Space responses
- Space listings with pagination
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from enum import Enum
from uuid import UUID

from pydantic import BaseModel, Field, ConfigDict, field_validator
from pydantic.functional_validators import BeforeValidator
from typing_extensions import Annotated

UUIDStr = Annotated[UUID, BeforeValidator(str)]


class SpaceType(str, Enum):
    """Space type enumeration matching the database model."""
    
    chat = "chat"
    quiz = "quiz"
    notes = "notes"
    openended = "openended"
    flashcards = "flashcards"
    studyguide = "studyguide"


class SpaceCreate(BaseModel):
    """Schema for space creation request."""
    
    type: SpaceType = Field(..., description="Type of space to create")
    title: str = Field(..., min_length=1, max_length=255, description="Space title")
    settings: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Type-specific settings")
    
    @field_validator('title')
    @classmethod
    def validate_title(cls, v: str) -> str:
        """Validate title is not empty after stripping whitespace."""
        if not v.strip():
            raise ValueError('Title cannot be empty')
        return v.strip()

    @field_validator('settings')
    @classmethod
    def validate_settings(cls, v: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Validate and clean settings."""
        if v is None:
            return {}
        # Ensure it's a dictionary
        if not isinstance(v, dict):
            raise ValueError('Settings must be a dictionary')
        return v


class SpaceUpdate(BaseModel):
    """Schema for space update request (partial update)."""
    
    title: Optional[str] = Field(None, min_length=1, max_length=255, description="Space title")
    settings: Optional[Dict[str, Any]] = Field(None, description="Type-specific settings")
    
    @field_validator('title')
    @classmethod
    def validate_title(cls, v: Optional[str]) -> Optional[str]:
        """Validate title is not empty after stripping whitespace."""
        if v is not None and not v.strip():
            raise ValueError('Title cannot be empty')
        return v.strip() if v else v

    @field_validator('settings')
    @classmethod
    def validate_settings(cls, v: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Validate and clean settings."""
        if v is not None:
            # Ensure it's a dictionary
            if not isinstance(v, dict):
                raise ValueError('Settings must be a dictionary')
        return v


class SpaceResponse(BaseModel):
    """Schema for space data in responses."""
    
    id: UUIDStr = Field(..., description="Space's unique identifier")
    folder_id: UUIDStr = Field(..., alias="folderId", description="Parent folder ID")
    type: SpaceType = Field(..., description="Space type")
    title: str = Field(..., description="Space title")
    settings: Dict[str, Any] = Field(..., description="Type-specific settings")
    created_at: datetime = Field(..., alias="createdAt", description="When the space was created")
    
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class PaginationMeta(BaseModel):
    """Schema for pagination metadata."""
    
    page: int = Field(..., description="Current page number")
    limit: int = Field(..., description="Items per page")
    total: int = Field(..., description="Total number of items")


class SpaceListResponse(BaseModel):
    """Schema for space list responses with pagination."""
    
    data: List[SpaceResponse] = Field(..., description="List of spaces")
    meta: PaginationMeta = Field(..., description="Pagination metadata")


class SpaceResponseWrapper(BaseModel):
    """Wrapper for single space responses following API specification."""
    
    data: SpaceResponse = Field(..., description="Space data")


class ErrorDetail(BaseModel):
    """Schema for error details."""
    
    code: str = Field(..., description="Error code")
    message: str = Field(..., description="Human-readable error message")
    details: Optional[dict] = Field(None, description="Additional error details")


class ErrorResponse(BaseModel):
    """Schema for error responses following API specification."""
    
    error: ErrorDetail = Field(..., description="Error information") 