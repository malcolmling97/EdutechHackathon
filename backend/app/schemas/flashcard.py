"""
Pydantic schemas for flashcard management endpoints.

Defines request and response models for:
- Flashcard generation
- Flashcard responses
- Flashcard listings with pagination
- Flashcard updates
- Flashcard shuffling
"""
from datetime import datetime
from typing import Optional, List, Dict, Any, Union
from enum import Enum
from uuid import UUID

from pydantic import BaseModel, Field, ConfigDict, field_validator
from pydantic.functional_validators import BeforeValidator
from typing_extensions import Annotated

UUIDStr = Annotated[UUID, BeforeValidator(str)]


class CardType(str, Enum):
    """Card type enumeration matching the database model."""
    
    mcq = "mcq"
    tf = "tf"
    short_answer = "short_answer"


class DifficultyLevel(str, Enum):
    """Difficulty level enumeration matching the database model."""
    
    easy = "easy"
    medium = "medium"
    hard = "hard"


class FlashcardCreate(BaseModel):
    """Schema for flashcard creation request."""
    
    title: str = Field(..., min_length=1, max_length=255, description="Flashcard deck title")
    file_ids: List[str] = Field(..., min_items=1, alias="fileIds", description="Source file IDs for flashcard generation")
    card_count: int = Field(20, ge=1, le=100, alias="cardCount", description="Number of cards to generate")
    card_types: List[CardType] = Field(
        default=[CardType.mcq, CardType.tf], 
        alias="cardTypes",
        description="Types of cards to generate"
    )
    difficulty: DifficultyLevel = Field(DifficultyLevel.medium, description="Flashcard difficulty level")
    
    @field_validator('title')
    @classmethod
    def validate_title(cls, v: str) -> str:
        """Validate title is not empty after stripping whitespace."""
        if not v.strip():
            raise ValueError('Title cannot be empty')
        return v.strip()

    @field_validator('file_ids')
    @classmethod
    def validate_file_ids(cls, v: List[str]) -> List[str]:
        """Validate file IDs are valid UUIDs."""
        for file_id in v:
            try:
                UUID(file_id)
            except ValueError:
                raise ValueError(f'Invalid file ID format: {file_id}')
        return v

    @field_validator('card_types')
    @classmethod
    def validate_card_types(cls, v: List[CardType]) -> List[CardType]:
        """Validate at least one card type is provided."""
        if not v:
            raise ValueError('At least one card type must be specified')
        # Remove duplicates while preserving order
        seen = set()
        unique_types = []
        for ct in v:
            if ct not in seen:
                seen.add(ct)
                unique_types.append(ct)
        return unique_types


class FlashcardCard(BaseModel):
    """Schema for individual flashcard cards."""
    
    id: str = Field(..., description="Card identifier")
    front: str = Field(..., description="Front side of the card (question)")
    back: str = Field(..., description="Back side of the card (answer)")
    difficulty: DifficultyLevel = Field(..., description="Card difficulty level")
    tags: List[str] = Field(default_factory=list, description="Tags for categorizing the card")


class FlashcardResponse(BaseModel):
    """Schema for flashcard data in responses."""
    
    id: UUIDStr = Field(..., description="Flashcard's unique identifier")
    space_id: UUIDStr = Field(..., alias="spaceId", description="Parent space ID")
    title: str = Field(..., description="Flashcard deck title")
    cards: List[Dict[str, Any]] = Field(..., description="Flashcard cards")
    created_at: datetime = Field(..., alias="createdAt", description="When the flashcard was created")
    updated_at: datetime = Field(..., alias="updatedAt", description="When the flashcard was last updated")
    
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class FlashcardUpdate(BaseModel):
    """Schema for flashcard update request."""
    
    title: Optional[str] = Field(None, min_length=1, max_length=255, description="Flashcard deck title")
    cards: Optional[List[Dict[str, Any]]] = Field(None, description="Flashcard cards")
    
    @field_validator('title')
    @classmethod
    def validate_title(cls, v: Optional[str]) -> Optional[str]:
        """Validate title is not empty if provided."""
        if v is not None and not v.strip():
            raise ValueError('Title cannot be empty')
        return v.strip() if v is not None else v


class FlashcardShuffleResponse(BaseModel):
    """Schema for flashcard shuffle response."""
    
    card_order: List[str] = Field(..., alias="cardOrder", description="Shuffled order of card IDs")
    session_id: str = Field(..., alias="sessionId", description="Study session identifier")
    created_at: datetime = Field(..., alias="createdAt", description="When the shuffle was created")
    
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class PaginationMeta(BaseModel):
    """Schema for pagination metadata."""
    
    page: int = Field(..., description="Current page number")
    limit: int = Field(..., description="Items per page")
    total: int = Field(..., description="Total number of items")


class FlashcardListResponse(BaseModel):
    """Schema for flashcard list responses with pagination."""
    
    data: List[FlashcardResponse] = Field(..., description="List of flashcards")
    meta: PaginationMeta = Field(..., description="Pagination metadata")


class FlashcardResponseWrapper(BaseModel):
    """Wrapper for single flashcard responses following API specification."""
    
    data: FlashcardResponse = Field(..., description="Flashcard data")


class FlashcardShuffleResponseWrapper(BaseModel):
    """Wrapper for flashcard shuffle responses following API specification."""
    
    data: FlashcardShuffleResponse = Field(..., description="Shuffle results")


class ErrorDetail(BaseModel):
    """Schema for error details."""
    
    code: str = Field(..., description="Error code")
    message: str = Field(..., description="Human-readable error message")
    details: Optional[dict] = Field(None, description="Additional error details")


class ErrorResponse(BaseModel):
    """Schema for error responses following API specification."""
    
    error: ErrorDetail = Field(..., description="Error information") 