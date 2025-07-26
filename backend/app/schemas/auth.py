"""
Pydantic schemas for authentication endpoints.

Defines request and response models for:
- User registration
- User login
- User profile
- Authentication responses
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, field_validator, ConfigDict
from uuid import UUID
from pydantic.functional_validators import BeforeValidator
from typing_extensions import Annotated

UUIDStr = Annotated[UUID, BeforeValidator(str)]


class UserRegistration(BaseModel):
    """Schema for user registration request."""
    
    email: EmailStr = Field(..., description="User's email address")
    password: str = Field(..., min_length=8, description="User's password (minimum 8 characters)")
    name: str = Field(..., min_length=1, max_length=255, description="User's display name")
    
    @field_validator('password')
    @classmethod
    def validate_password(cls, v: str) -> str:
        """Validate password strength."""
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        return v
    
    @field_validator('name')
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Validate name is not empty."""
        if not v.strip():
            raise ValueError('Name cannot be empty')
        return v.strip()


class UserLogin(BaseModel):
    """Schema for user login request."""
    
    email: EmailStr = Field(..., description="User's email address")
    password: str = Field(..., description="User's password")


class UserResponse(BaseModel):
    """Schema for user data in responses."""
    
    id: UUIDStr = Field(..., description="User's unique identifier")
    email: str = Field(..., description="User's email address")
    name: str = Field(..., description="User's display name")
    created_at: datetime = Field(..., description="When the user was created")
    updated_at: Optional[datetime] = Field(None, description="When the user was last updated")
    
    model_config = ConfigDict(from_attributes=True, json_encoders={datetime: lambda v: v.isoformat()})


class AuthResponse(BaseModel):
    """Schema for authentication responses with user and token."""
    
    user: UserResponse = Field(..., description="User information")
    token: str = Field(..., description="JWT access token")


class AuthResponseWrapper(BaseModel):
    """Wrapper for authentication responses following API specification."""
    
    data: AuthResponse = Field(..., description="Authentication data")


class ProfileResponseWrapper(BaseModel):
    """Wrapper for profile responses following API specification."""
    
    data: dict = Field(..., description="Profile data")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "data": {
                    "user": {
                        "id": "123e4567-e89b-12d3-a456-426614174000",
                        "email": "user@example.com",
                        "name": "John Doe",
                        "created_at": "2025-01-15T10:30:00Z"
                    }
                }
            }
        }
    )


class ErrorDetail(BaseModel):
    """Schema for error details."""
    
    code: str = Field(..., description="Error code")
    message: str = Field(..., description="Human-readable error message")
    details: Optional[dict] = Field(None, description="Additional error details")


class ErrorResponse(BaseModel):
    """Schema for error responses following API specification."""
    
    error: ErrorDetail = Field(..., description="Error information") 