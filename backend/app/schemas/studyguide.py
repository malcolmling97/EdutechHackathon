"""
Pydantic schemas for study guide management endpoints.

Defines request and response models for:
- Study guide creation
- Study guide updates
- Study guide responses
- Study guide listings with pagination
- Study session completion
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from uuid import UUID

from pydantic import BaseModel, Field, ConfigDict, field_validator
from pydantic.functional_validators import BeforeValidator
from typing_extensions import Annotated

UUIDStr = Annotated[UUID, BeforeValidator(str)]


class StudyGuideCreate(BaseModel):
    """Schema for study guide creation request."""
    
    title: str = Field(..., min_length=1, max_length=255, description="Study guide title")
    deadline: datetime = Field(..., description="Target completion date")
    preferences: Dict[str, Any] = Field(..., description="User study preferences")
    file_ids: List[str] = Field(..., min_length=1, description="List of file UUIDs to generate study guide from")
    topics: Optional[List[str]] = Field(default_factory=list, description="List of topics to cover")
    
    @field_validator('title')
    @classmethod
    def validate_title(cls, v: str) -> str:
        """Validate title is not empty after stripping whitespace."""
        if not v.strip():
            raise ValueError('Title cannot be empty')
        return v.strip()
    
    @field_validator('deadline')
    @classmethod
    def validate_deadline(cls, v: datetime) -> datetime:
        """Validate deadline format."""
        # Ensure timezone info is present
        from datetime import timezone
        if v.tzinfo is None:
            v = v.replace(tzinfo=timezone.utc)
        return v
    
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
    
    @field_validator('preferences')
    @classmethod
    def validate_preferences(cls, v: Dict[str, Any]) -> Dict[str, Any]:
        """Validate study preferences."""
        if not isinstance(v, dict):
            raise ValueError('Preferences must be a dictionary')
        
        # Validate required fields
        required_fields = ['dailyStudyHours', 'preferredTimes', 'breakInterval', 'studyMethods']
        for field in required_fields:
            if field not in v:
                raise ValueError(f'Missing required preference field: {field}')
        
        # Validate dailyStudyHours
        if not isinstance(v['dailyStudyHours'], (int, float)) or v['dailyStudyHours'] <= 0:
            raise ValueError('dailyStudyHours must be a positive number')
        
        # Validate preferredTimes
        if not isinstance(v['preferredTimes'], list) or not v['preferredTimes']:
            raise ValueError('preferredTimes must be a non-empty list')
        
        # Validate breakInterval
        if not isinstance(v['breakInterval'], int) or v['breakInterval'] <= 0:
            raise ValueError('breakInterval must be a positive integer')
        
        # Validate studyMethods
        if not isinstance(v['studyMethods'], list) or not v['studyMethods']:
            raise ValueError('studyMethods must be a non-empty list')
        
        return v


class StudyGuideUpdate(BaseModel):
    """Schema for study guide update request (partial update)."""
    
    title: Optional[str] = Field(None, min_length=1, max_length=255, description="Study guide title")
    deadline: Optional[datetime] = Field(None, description="Target completion date")
    preferences: Optional[Dict[str, Any]] = Field(None, description="User study preferences")
    
    @field_validator('title')
    @classmethod
    def validate_title(cls, v: Optional[str]) -> Optional[str]:
        """Validate title is not empty after stripping whitespace."""
        if v is not None and not v.strip():
            raise ValueError('Title cannot be empty')
        return v.strip() if v else v
    
    @field_validator('deadline')
    @classmethod
    def validate_deadline(cls, v: Optional[datetime]) -> Optional[datetime]:
        """Validate deadline is in the future."""
        if v is not None:
            from datetime import timezone
            # Convert to UTC for comparison
            if v.tzinfo is None:
                v = v.replace(tzinfo=timezone.utc)
            if v <= datetime.now(timezone.utc):
                raise ValueError('Deadline must be in the future')
        return v
    
    @field_validator('preferences')
    @classmethod
    def validate_preferences(cls, v: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Validate study preferences."""
        if v is not None:
            if not isinstance(v, dict):
                raise ValueError('Preferences must be a dictionary')
            
            # Validate dailyStudyHours if present
            if 'dailyStudyHours' in v:
                if not isinstance(v['dailyStudyHours'], (int, float)) or v['dailyStudyHours'] <= 0:
                    raise ValueError('dailyStudyHours must be a positive number')
            
            # Validate preferredTimes if present
            if 'preferredTimes' in v:
                if not isinstance(v['preferredTimes'], list) or not v['preferredTimes']:
                    raise ValueError('preferredTimes must be a non-empty list')
            
            # Validate breakInterval if present
            if 'breakInterval' in v:
                if not isinstance(v['breakInterval'], int) or v['breakInterval'] <= 0:
                    raise ValueError('breakInterval must be a positive integer')
            
            # Validate studyMethods if present
            if 'studyMethods' in v:
                if not isinstance(v['studyMethods'], list) or not v['studyMethods']:
                    raise ValueError('studyMethods must be a non-empty list')
        
        return v


class StudyGuideResponse(BaseModel):
    """Schema for study guide data in responses."""
    
    id: UUIDStr = Field(..., description="Study guide's unique identifier")
    space_id: UUIDStr = Field(..., alias="spaceId", description="Parent space ID")
    title: str = Field(..., description="Study guide title")
    deadline: datetime = Field(..., description="Target completion date")
    total_study_hours: int = Field(..., alias="totalStudyHours", description="Total hours allocated for study")
    schedule: List[Dict[str, Any]] = Field(..., description="Study sessions schedule")
    preferences: Dict[str, Any] = Field(..., description="User study preferences")
    progress: Dict[str, Any] = Field(..., description="Progress tracking")
    created_at: datetime = Field(..., alias="createdAt", description="When the study guide was created")
    updated_at: datetime = Field(..., alias="updatedAt", description="When the study guide was last updated")
    
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class PaginationMeta(BaseModel):
    """Schema for pagination metadata."""
    
    page: int = Field(..., description="Current page number")
    limit: int = Field(..., description="Items per page")
    total: int = Field(..., description="Total number of items")


class StudyGuideListResponse(BaseModel):
    """Schema for study guide list responses with pagination."""
    
    data: List[StudyGuideResponse] = Field(..., description="List of study guides")
    meta: PaginationMeta = Field(..., description="Pagination metadata")


class StudyGuideResponseWrapper(BaseModel):
    """Wrapper for single study guide responses following API specification."""
    
    data: StudyGuideResponse = Field(..., description="Study guide data")


class StudySessionCompleteResponse(BaseModel):
    """Schema for study session completion response."""
    
    data: StudyGuideResponse = Field(..., description="Updated study guide data")


class ErrorDetail(BaseModel):
    """Schema for error details."""
    
    code: str = Field(..., description="Error code")
    message: str = Field(..., description="Human-readable error message")
    details: Optional[dict] = Field(None, description="Additional error details")


class ErrorResponse(BaseModel):
    """Schema for error responses following API specification."""
    
    error: ErrorDetail = Field(..., description="Error information") 