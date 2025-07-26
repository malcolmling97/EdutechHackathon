"""
Pydantic schemas for open-ended question management endpoints.

Defines request and response models for:
- Open-ended question generation
- Open-ended answer submissions
- Open-ended question responses
- Open-ended question listings with pagination
"""
from datetime import datetime
from typing import Optional, List, Dict, Any, Union
from enum import Enum
from uuid import UUID

from pydantic import BaseModel, Field, ConfigDict, field_validator
from pydantic.functional_validators import BeforeValidator
from typing_extensions import Annotated

UUIDStr = Annotated[UUID, BeforeValidator(str)]


class OpenEndedQuestionType(str, Enum):
    """Open-ended question type enumeration matching the database model."""
    
    short_answer = "short_answer"
    essay = "essay"
    analysis = "analysis"


class DifficultyLevel(str, Enum):
    """Difficulty level enumeration matching the database model."""
    
    easy = "easy"
    medium = "medium"
    hard = "hard"


class OpenEndedQuestionCreate(BaseModel):
    """Schema for open-ended question creation request."""
    
    space_id: str = Field(..., alias="spaceId", description="Space UUID")
    title: str = Field(..., min_length=1, max_length=255, description="Open-ended question title")
    file_ids: List[str] = Field(..., min_items=1, alias="fileIds", description="Source file IDs for question generation")
    question_count: int = Field(10, ge=1, le=50, alias="questionCount", description="Number of questions to generate")
    difficulty: DifficultyLevel = Field(DifficultyLevel.medium, description="Question difficulty level")
    max_words: Optional[int] = Field(500, ge=50, le=2000, alias="maxWords", description="Maximum words per answer")
    topics: Optional[List[str]] = Field(None, alias="topics", description="Specific topics to focus on")
    
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

    @field_validator('topics')
    @classmethod
    def validate_topics(cls, v: Optional[List[str]]) -> Optional[List[str]]:
        """Validate topics if provided."""
        if v is not None:
            if not v:
                raise ValueError('Topics list cannot be empty if provided')
            # Remove duplicates while preserving order
            seen = set()
            unique_topics = []
            for topic in v:
                if topic not in seen:
                    seen.add(topic)
                    unique_topics.append(topic)
            return unique_topics
        return v


class RubricCriterion(BaseModel):
    """Schema for individual rubric criteria."""
    
    name: str = Field(..., description="Criterion name")
    weight: float = Field(..., ge=0.0, le=1.0, description="Criterion weight (0.0-1.0)")
    description: str = Field(..., description="Criterion description")


class QuestionRubric(BaseModel):
    """Schema for question grading rubric."""
    
    criteria: List[RubricCriterion] = Field(..., min_items=1, description="Grading criteria")
    
    @field_validator('criteria')
    @classmethod
    def validate_criteria_weights(cls, v: List[RubricCriterion]) -> List[RubricCriterion]:
        """Validate that criteria weights sum to approximately 1.0."""
        total_weight = sum(criterion.weight for criterion in v)
        if abs(total_weight - 1.0) > 0.01:  # Allow small floating point differences
            raise ValueError(f'Criteria weights must sum to 1.0, got {total_weight}')
        return v


class OpenEndedQuestionItem(BaseModel):
    """Schema for individual open-ended questions."""
    
    id: str = Field(..., description="Question identifier")
    prompt: str = Field(..., description="Question prompt")
    max_words: int = Field(..., alias="maxWords", description="Maximum words allowed")
    rubric: QuestionRubric = Field(..., description="Grading rubric")


class OpenEndedQuestionResponse(BaseModel):
    """Schema for open-ended question data in responses."""
    
    id: UUIDStr = Field(..., description="Open-ended question's unique identifier")
    space_id: UUIDStr = Field(..., alias="spaceId", description="Parent space ID")
    title: str = Field(..., description="Open-ended question title")
    questions: List[Dict[str, Any]] = Field(..., description="Open-ended questions")
    created_at: datetime = Field(..., alias="createdAt", description="When the open-ended question was created")
    
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class OpenEndedAnswer(BaseModel):
    """Schema for individual open-ended answers in submissions."""
    
    question_id: str = Field(..., alias="questionId", description="Question identifier")
    answer: str = Field(..., min_length=1, description="User's answer")
    
    @field_validator('question_id')
    @classmethod
    def validate_question_id(cls, v: str) -> str:
        """Validate question ID is not empty."""
        if not v.strip():
            raise ValueError('Question ID cannot be empty')
        return v.strip()

    @field_validator('answer')
    @classmethod
    def validate_answer(cls, v: str) -> str:
        """Validate answer is not empty after stripping whitespace."""
        if not v.strip():
            raise ValueError('Answer cannot be empty')
        return v.strip()


class OpenEndedSubmission(BaseModel):
    """Schema for open-ended answer submission request."""
    
    answers: List[OpenEndedAnswer] = Field(..., min_items=1, description="User answers")
    
    @field_validator('answers')
    @classmethod
    def validate_answers(cls, v: List[OpenEndedAnswer]) -> List[OpenEndedAnswer]:
        """Validate answers and remove duplicates by question_id."""
        if not v:
            raise ValueError('At least one answer must be provided')
        
        # Remove duplicate answers for the same question (keep last one)
        answer_dict = {}
        for answer in v:
            answer_dict[answer.question_id] = answer
        
        return list(answer_dict.values())


class GradeBreakdown(BaseModel):
    """Schema for individual criterion grading breakdown."""
    
    criterion: str = Field(..., description="Criterion name")
    score: float = Field(..., description="Score achieved")
    max_score: float = Field(..., alias="maxScore", description="Maximum possible score")
    feedback: str = Field(..., description="Detailed feedback")


class GradeResult(BaseModel):
    """Schema for AI grading results."""
    
    total_score: float = Field(..., alias="totalScore", description="Total score achieved")
    max_score: float = Field(..., alias="maxScore", description="Maximum possible score")
    breakdown: List[GradeBreakdown] = Field(..., description="Detailed breakdown by criterion")
    overall_feedback: str = Field(..., alias="overallFeedback", description="Overall feedback")
    graded_at: datetime = Field(..., alias="gradedAt", description="When grading was completed")


class OpenEndedAnswerResponse(BaseModel):
    """Schema for open-ended answer submission results."""
    
    id: UUIDStr = Field(..., description="Answer's unique identifier")
    question_id: str = Field(..., alias="questionId", description="Question identifier")
    user_id: UUIDStr = Field(..., alias="userId", description="User identifier")
    answer: str = Field(..., description="Submitted answer")
    word_count: int = Field(..., alias="wordCount", description="Answer word count")
    grade: GradeResult = Field(..., description="AI grading results")
    submitted_at: datetime = Field(..., alias="submittedAt", description="When the answer was submitted")
    
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class PaginationMeta(BaseModel):
    """Schema for pagination metadata."""
    
    page: int = Field(..., description="Current page number")
    limit: int = Field(..., description="Items per page")
    total: int = Field(..., description="Total number of items")


class OpenEndedListResponse(BaseModel):
    """Schema for open-ended question list responses with pagination."""
    
    data: List[OpenEndedQuestionResponse] = Field(..., description="List of open-ended questions")
    meta: PaginationMeta = Field(..., description="Pagination metadata")


class OpenEndedResponseWrapper(BaseModel):
    """Wrapper for single open-ended question responses following API specification."""
    
    data: OpenEndedQuestionResponse = Field(..., description="Open-ended question data")


class OpenEndedAnswerResponseWrapper(BaseModel):
    """Wrapper for open-ended answer submission responses following API specification."""
    
    data: OpenEndedAnswerResponse = Field(..., description="Answer submission results")


class OpenEndedAnswersListResponse(BaseModel):
    """Schema for open-ended answers list responses."""
    
    data: List[OpenEndedAnswerResponse] = Field(..., description="List of user's answers")


class ErrorDetail(BaseModel):
    """Schema for error details."""
    
    code: str = Field(..., description="Error code")
    message: str = Field(..., description="Human-readable error message")
    details: Optional[dict] = Field(None, description="Additional error details")


class ErrorResponse(BaseModel):
    """Schema for error responses following API specification."""
    
    error: ErrorDetail = Field(..., description="Error information") 