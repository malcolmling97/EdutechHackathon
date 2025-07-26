"""
Pydantic schemas for quiz management endpoints.

Defines request and response models for:
- Quiz generation
- Quiz submissions
- Quiz responses
- Quiz listings with pagination
"""
from datetime import datetime
from typing import Optional, List, Dict, Any, Union
from enum import Enum
from uuid import UUID

from pydantic import BaseModel, Field, ConfigDict, field_validator
from pydantic.functional_validators import BeforeValidator
from typing_extensions import Annotated

UUIDStr = Annotated[UUID, BeforeValidator(str)]


class QuestionType(str, Enum):
    """Question type enumeration matching the database model."""
    
    mcq = "mcq"
    tf = "tf"
    short_answer = "short_answer"


class DifficultyLevel(str, Enum):
    """Difficulty level enumeration matching the database model."""
    
    easy = "easy"
    medium = "medium"
    hard = "hard"


class QuizCreate(BaseModel):
    """Schema for quiz creation request."""
    
    title: str = Field(..., min_length=1, max_length=255, description="Quiz title")
    file_ids: List[str] = Field(..., min_items=1, alias="fileIds", description="Source file IDs for quiz generation")
    question_count: int = Field(10, ge=1, le=50, alias="questionCount", description="Number of questions to generate")
    question_types: List[QuestionType] = Field(
        default=[QuestionType.mcq, QuestionType.tf], 
        alias="questionTypes",
        description="Types of questions to generate"
    )
    difficulty: DifficultyLevel = Field(DifficultyLevel.medium, description="Quiz difficulty level")
    
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

    @field_validator('question_types')
    @classmethod
    def validate_question_types(cls, v: List[QuestionType]) -> List[QuestionType]:
        """Validate at least one question type is provided."""
        if not v:
            raise ValueError('At least one question type must be specified')
        # Remove duplicates while preserving order
        seen = set()
        unique_types = []
        for qt in v:
            if qt not in seen:
                seen.add(qt)
                unique_types.append(qt)
        return unique_types


class Question(BaseModel):
    """Schema for individual quiz questions."""
    
    id: str = Field(..., description="Question identifier")
    type: QuestionType = Field(..., description="Question type")
    prompt: str = Field(..., description="Question text")
    choices: Optional[List[str]] = Field(None, description="Answer choices for MCQ")
    answer: Union[str, bool, int] = Field(..., description="Correct answer")


class QuizResponse(BaseModel):
    """Schema for quiz data in responses."""
    
    id: UUIDStr = Field(..., description="Quiz's unique identifier")
    space_id: UUIDStr = Field(..., alias="spaceId", description="Parent space ID")
    title: str = Field(..., description="Quiz title")
    questions: List[Dict[str, Any]] = Field(..., description="Quiz questions")
    created_at: datetime = Field(..., alias="createdAt", description="When the quiz was created")
    
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class QuizAnswer(BaseModel):
    """Schema for individual quiz answers in submissions."""
    
    question_id: str = Field(..., alias="questionId", description="Question identifier")
    answer: Union[str, int, bool] = Field(..., description="User's answer")
    
    @field_validator('question_id')
    @classmethod
    def validate_question_id(cls, v: str) -> str:
        """Validate question ID is not empty."""
        if not v.strip():
            raise ValueError('Question ID cannot be empty')
        return v.strip()


class QuizSubmission(BaseModel):
    """Schema for quiz answer submission request."""
    
    answers: List[QuizAnswer] = Field(..., min_items=1, description="User answers")
    
    @field_validator('answers')
    @classmethod
    def validate_answers(cls, v: List[QuizAnswer]) -> List[QuizAnswer]:
        """Validate answers and remove duplicates by question_id."""
        if not v:
            raise ValueError('At least one answer must be provided')
        
        # Remove duplicate answers for the same question (keep last one)
        answer_dict = {}
        for answer in v:
            answer_dict[answer.question_id] = answer
        
        return list(answer_dict.values())


class QuizSubmissionResponse(BaseModel):
    """Schema for quiz submission results."""
    
    score: float = Field(..., description="Total score achieved")
    total_questions: int = Field(..., alias="totalQuestions", description="Total number of questions")
    feedback: List[Dict[str, Any]] = Field(..., description="Detailed feedback for each answer")
    submitted_at: datetime = Field(..., alias="submittedAt", description="When the submission was made")
    
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class PaginationMeta(BaseModel):
    """Schema for pagination metadata."""
    
    page: int = Field(..., description="Current page number")
    limit: int = Field(..., description="Items per page")
    total: int = Field(..., description="Total number of items")


class QuizListResponse(BaseModel):
    """Schema for quiz list responses with pagination."""
    
    data: List[QuizResponse] = Field(..., description="List of quizzes")
    meta: PaginationMeta = Field(..., description="Pagination metadata")


class QuizResponseWrapper(BaseModel):
    """Wrapper for single quiz responses following API specification."""
    
    data: QuizResponse = Field(..., description="Quiz data")


class QuizSubmissionResponseWrapper(BaseModel):
    """Wrapper for quiz submission responses following API specification."""
    
    data: QuizSubmissionResponse = Field(..., description="Submission results")


class ErrorDetail(BaseModel):
    """Schema for error details."""
    
    code: str = Field(..., description="Error code")
    message: str = Field(..., description="Human-readable error message")
    details: Optional[dict] = Field(None, description="Additional error details")


class ErrorResponse(BaseModel):
    """Schema for error responses following API specification."""
    
    error: ErrorDetail = Field(..., description="Error information") 