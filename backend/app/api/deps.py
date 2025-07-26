"""
FastAPI dependencies for authentication and database session management.

Provides:
- Database session dependency
- Current user dependency from JWT token
- Authentication utilities
"""
from typing import Generator, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.core.database import SessionLocal

_test_db_session = None
from app.core.security import verify_token
from app.models.user import User
from app.services.auth import AuthService
from app.core.config import settings


# HTTP Bearer token security scheme  
security = HTTPBearer(auto_error=False)


def get_db() -> Generator:
    """
    Database dependency that provides a database session.
    
    Yields:
        Database session that is automatically closed after use
    """
    if _test_db_session:
        yield _test_db_session
    else:
        db = SessionLocal()
        try:
            yield db
        finally:
            db.close()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """
    Get the current authenticated user from JWT token.
    
    Args:
        credentials: HTTP authorization credentials containing JWT token
        db: Database session
        
    Returns:
        Current authenticated user
        
    Raises:
        HTTPException: If token is invalid or user not found
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    token = credentials.credentials
    
    # Verify token and extract user ID
    user_id = verify_token(token)
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Get user from database
    user = AuthService.get_user_by_id(db, user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user


def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db)
) -> Optional[User]:
    """
    Get the current authenticated user from JWT token (optional).
    
    Similar to get_current_user but returns None instead of raising exception
    if no valid token is provided.
    
    Args:
        credentials: Optional HTTP authorization credentials
        db: Database session
        
    Returns:
        Current authenticated user or None if not authenticated
    """
    if not credentials:
        return None
    
    try:
        return get_current_user(credentials, db)
    except HTTPException:
        return None


def get_token_from_credentials(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> str:
    """
    Extract token string from authorization credentials.
    
    Args:
        credentials: HTTP authorization credentials
        
    Returns:
        JWT token string
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return credentials.credentials 