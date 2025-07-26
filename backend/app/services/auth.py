"""
Authentication service for user management and authentication operations.

Handles:
- User registration with validation and password hashing
- User login with credential verification
- User profile retrieval
- Token blacklisting for logout
"""
from typing import Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.user import User
from app.schemas.auth import UserRegistration, UserLogin, UserResponse, AuthResponse
from app.core.security import (
    get_password_hash, 
    verify_password, 
    create_access_token,
    blacklist_token
)


class AuthService:
    """Service class for authentication operations."""
    
    @staticmethod
    def register_user(db: Session, user_data: UserRegistration) -> AuthResponse:
        """
        Register a new user.
        
        Args:
            db: Database session
            user_data: User registration data
            
        Returns:
            AuthResponse with user data and JWT token
            
        Raises:
            HTTPException: If email already exists or other validation errors
        """
        # Check if user already exists
        existing_user = db.query(User).filter(User.email == user_data.email).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "error": {
                        "code": "EMAIL_ALREADY_EXISTS",
                        "message": "A user with this email already exists",
                        "details": {"email": user_data.email}
                    }
                }
            )
        
        # Hash password
        password_hash = get_password_hash(user_data.password)
        
        # Create user
        db_user = User(
            email=user_data.email,
            name=user_data.name,
            password_hash=password_hash
        )
        
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        
        # Create access token
        access_token = create_access_token(subject=str(db_user.id))
        
        # Prepare response
        user_response = UserResponse(
            id=str(db_user.id),
            email=db_user.email,
            name=db_user.name,
            created_at=db_user.created_at,
            updated_at=db_user.updated_at
        )
        
        return AuthResponse(user=user_response, token=access_token)
    
    @staticmethod
    def login_user(db: Session, login_data: UserLogin) -> AuthResponse:
        """
        Authenticate user and create login session.
        
        Args:
            db: Database session
            login_data: User login credentials
            
        Returns:
            AuthResponse with user data and JWT token
            
        Raises:
            HTTPException: If credentials are invalid
        """
        # Find user by email
        user = db.query(User).filter(User.email == login_data.email).first()
        
        if not user or not verify_password(login_data.password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={
                    "error": {
                        "code": "INVALID_CREDENTIALS",
                        "message": "Invalid email or password",
                        "details": None
                    }
                }
            )
        
        # Create access token
        access_token = create_access_token(subject=str(user.id))
        
        # Prepare response
        user_response = UserResponse(
            id=str(user.id),
            email=user.email,
            name=user.name,
            created_at=user.created_at,
            updated_at=user.updated_at
        )
        
        return AuthResponse(user=user_response, token=access_token)
    
    @staticmethod
    def get_user_by_id(db: Session, user_id: str) -> Optional[User]:
        """
        Get user by ID.
        
        Args:
            db: Database session
            user_id: User's unique identifier
            
        Returns:
            User object if found, None otherwise
        """
        return db.query(User).filter(User.id == user_id).first()
    
    @staticmethod
    def logout_user(token: str) -> None:
        """
        Logout user by blacklisting their token.
        
        Args:
            token: JWT token to blacklist
        """
        blacklist_token(token) 