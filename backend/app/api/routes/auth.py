"""
Authentication routes for the EdutechHackathon API.

Endpoints:
- POST /register - User registration
- POST /login - User login
- GET /profile - Get current user profile
- POST /logout - User logout
"""
from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user, get_token_from_credentials
from app.models.user import User
from app.schemas.auth import (
    UserRegistration, 
    UserLogin, 
    AuthResponseWrapper,
    ProfileResponseWrapper,
    UserResponse
)
from app.services.auth import AuthService


router = APIRouter()


@router.post(
    "/register",
    response_model=AuthResponseWrapper,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
    description="Create a new user account with email, password, and name. Returns user data and JWT token."
)
async def register(
    user_data: UserRegistration,
    db: Session = Depends(get_db)
):
    """
    Register a new user.
    
    - **email**: Valid email address (will be used for login)
    - **password**: Password with minimum 8 characters
    - **name**: User's display name
    
    Returns user information and JWT access token for immediate use.
    """
    auth_response = AuthService.register_user(db, user_data)
    return AuthResponseWrapper(data=auth_response)


@router.post(
    "/login",
    response_model=AuthResponseWrapper,
    status_code=status.HTTP_200_OK,
    summary="Login user",
    description="Authenticate user with email and password. Returns user data and JWT token."
)
async def login(
    login_data: UserLogin,
    db: Session = Depends(get_db)
):
    """
    Authenticate user and create login session.
    
    - **email**: User's registered email address
    - **password**: User's password
    
    Returns user information and JWT access token.
    """
    auth_response = AuthService.login_user(db, login_data)
    return AuthResponseWrapper(data=auth_response)


@router.get(
    "/profile",
    response_model=ProfileResponseWrapper,
    status_code=status.HTTP_200_OK,
    summary="Get current user profile",
    description="Get the profile information of the currently authenticated user."
)
async def get_profile(
    current_user: User = Depends(get_current_user)
):
    """
    Get current user's profile.
    
    Requires valid JWT token in Authorization header.
    Returns detailed user information.
    """
    user_response = UserResponse(
        id=str(current_user.id),
        email=current_user.email,
        name=current_user.name,
        created_at=current_user.created_at,
        updated_at=current_user.updated_at
    )
    
    return ProfileResponseWrapper(data={"user": user_response})


@router.post(
    "/logout",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Logout user",
    description="Invalidate the current JWT token and logout the user."
)
async def logout(
    token: str = Depends(get_token_from_credentials),
    current_user: User = Depends(get_current_user)
):
    """
    Logout the current user.
    
    Requires valid JWT token in Authorization header.
    Blacklists the token to prevent further use.
    """
    AuthService.logout_user(token)
    return Response(status_code=status.HTTP_204_NO_CONTENT) 