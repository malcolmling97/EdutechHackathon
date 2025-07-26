"""
Pydantic schemas for chat message endpoints.

Defines request and response models for:
- Sending chat messages
- Retrieving message history
- Message responses with sources
"""
from datetime import datetime
from typing import List, Optional, Literal
from pydantic import BaseModel, Field, field_validator, ConfigDict
from uuid import UUID
from pydantic.functional_validators import BeforeValidator
from typing_extensions import Annotated

UUIDStr = Annotated[UUID, BeforeValidator(str)]


class MessageSource(BaseModel):
    """Schema for message source citations."""
    
    fileId: UUIDStr = Field(..., description="ID of the referenced file")
    page: Optional[int] = Field(None, description="Page number in the file (if applicable)")
    
    @field_validator('page')
    @classmethod
    def validate_page(cls, v: Optional[int]) -> Optional[int]:
        """Validate page number is positive."""
        if v is not None and v <= 0:
            raise ValueError('Page number must be positive')
        return v


class MessageRequest(BaseModel):
    """Schema for sending a chat message."""
    
    content: str = Field(..., min_length=1, max_length=10000, description="Message content")
    role: Literal["user"] = Field("user", description="Message role (only 'user' allowed for requests)")
    
    @field_validator('content')
    @classmethod
    def validate_content(cls, v: str) -> str:
        """Validate message content is not empty."""
        if not v.strip():
            raise ValueError('Message content cannot be empty')
        return v.strip()


class MessageResponse(BaseModel):
    """Schema for chat message in responses."""
    
    id: UUIDStr = Field(..., description="Message unique identifier")
    spaceId: UUIDStr = Field(..., description="Space ID this message belongs to")
    role: Literal["user", "assistant"] = Field(..., description="Message role")
    content: str = Field(..., description="Message content")
    sources: List[MessageSource] = Field(default_factory=list, description="Source citations for the message")
    createdAt: datetime = Field(..., description="When the message was created")
    
    model_config = ConfigDict(
        from_attributes=True,
        json_encoders={datetime: lambda v: v.isoformat() + "Z"}
    )


class MessageListResponse(BaseModel):
    """Schema for paginated message history response."""
    
    data: List[MessageResponse] = Field(..., description="List of messages")
    meta: dict = Field(..., description="Pagination metadata")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "data": [
                    {
                        "id": "123e4567-e89b-12d3-a456-426614174000",
                        "spaceId": "456e7890-e89b-12d3-a456-426614174000",
                        "role": "user",
                        "content": "What is photosynthesis?",
                        "sources": [],
                        "createdAt": "2025-01-15T10:30:00Z"
                    },
                    {
                        "id": "789e0123-e89b-12d3-a456-426614174000",
                        "spaceId": "456e7890-e89b-12d3-a456-426614174000",
                        "role": "assistant",
                        "content": "Photosynthesis is the process by which plants convert light energy into chemical energy...",
                        "sources": [
                            {
                                "fileId": "abc1234-e89b-12d3-a456-426614174000",
                                "page": 12
                            }
                        ],
                        "createdAt": "2025-01-15T10:30:05Z"
                    }
                ],
                "meta": {
                    "page": 1,
                    "limit": 20,
                    "total": 2
                }
            }
        }
    )


class MessageCreateResponse(BaseModel):
    """Schema for message creation response."""
    
    data: MessageResponse = Field(..., description="Created message")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "data": {
                    "id": "123e4567-e89b-12d3-a456-426614174000",
                    "spaceId": "456e7890-e89b-12d3-a456-426614174000",
                    "role": "user",
                    "content": "Explain the process of photosynthesis",
                    "sources": [],
                    "createdAt": "2025-01-15T10:30:00Z"
                }
            }
        }
    )


class MessageBatchCreateResponse(BaseModel):
    """Schema for batch message creation response (user + assistant)."""
    
    data: List[MessageResponse] = Field(..., description="Created messages (user and assistant)")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "data": [
                    {
                        "id": "123e4567-e89b-12d3-a456-426614174000",
                        "spaceId": "456e7890-e89b-12d3-a456-426614174000",
                        "role": "user",
                        "content": "Explain the process of photosynthesis",
                        "sources": [],
                        "createdAt": "2025-01-15T10:30:00Z"
                    },
                    {
                        "id": "456e7890-e89b-12d3-a456-426614174000",
                        "spaceId": "456e7890-e89b-12d3-a456-426614174000",
                        "role": "assistant",
                        "content": "Photosynthesis is a complex biological process...",
                        "sources": [
                            {
                                "fileId": "abc1234-e89b-12d3-a456-426614174000",
                                "page": 12
                            }
                        ],
                        "createdAt": "2025-01-15T10:30:05Z"
                    }
                ]
            }
        }
    )


class PaginationParams(BaseModel):
    """Schema for pagination parameters."""
    
    page: int = Field(1, ge=1, description="Page number (1-based)")
    limit: int = Field(20, ge=1, le=100, description="Items per page (max 100)")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "page": 1,
                "limit": 20
            }
        }
    )


class StreamingParams(BaseModel):
    """Schema for streaming parameters."""
    
    stream: bool = Field(False, description="Enable streaming response")


class ErrorDetail(BaseModel):
    """Schema for error details."""
    
    code: str = Field(..., description="Error code")
    message: str = Field(..., description="Human-readable error message")
    details: Optional[dict] = Field(None, description="Additional error details")


class ErrorResponse(BaseModel):
    """Schema for error responses following API specification."""
    
    error: ErrorDetail = Field(..., description="Error information")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "error": {
                    "code": "NOT_FOUND",
                    "message": "Space not found",
                    "details": None
                }
            }
        }
    ) 