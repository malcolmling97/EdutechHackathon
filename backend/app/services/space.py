"""
Space service for space management operations.

Handles:
- Space listing with pagination and filtering by type
- Space creation with validation and folder ownership verification
- Space retrieval with ownership verification
- Space updates with validation
- Space deletion with cascading operations
"""
import uuid
from typing import Optional, List, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from fastapi import HTTPException, status

from app.models.space import Space, SpaceType
from app.models.folder import Folder
from app.models.user import User
from app.schemas.space import (
    SpaceCreate, 
    SpaceUpdate, 
    SpaceResponse, 
    SpaceListResponse,
    PaginationMeta
)


class SpaceService:
    """Service class for space management operations."""
    
    @staticmethod
    def list_spaces(
        db: Session, 
        user: User, 
        folder_id: str,
        page: int = 1, 
        limit: int = 20, 
        space_type: Optional[SpaceType] = None
    ) -> SpaceListResponse:
        """
        List spaces in a folder for a user with pagination and optional type filtering.
        
        Args:
            db: Database session
            user: Current authenticated user
            folder_id: Parent folder UUID
            page: Page number (1-based)
            limit: Items per page
            space_type: Optional space type filter
            
        Returns:
            SpaceListResponse with spaces and pagination metadata
            
        Raises:
            HTTPException: If folder not found or user doesn't own it
        """
        # Validate folder_id is a valid UUID
        try:
            folder_uuid = uuid.UUID(folder_id)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail={
                    "error": {
                        "code": "INVALID_UUID",
                        "message": "Invalid folder ID format",
                        "details": {"folder_id": folder_id}
                    }
                }
            )
        
        # First check if folder exists at all
        folder = db.query(Folder).filter(
            and_(
                Folder.id == folder_uuid,
                Folder.deleted_at.is_(None)
            )
        ).first()
        
        if not folder:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "error": {
                        "code": "FOLDER_NOT_FOUND",
                        "message": "Folder not found",
                        "details": {"folder_id": folder_id}
                    }
                }
            )
        
        # Then check if user owns the folder
        if folder.owner_id != user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "error": {
                        "code": "FORBIDDEN",
                        "message": "You do not have permission to access this folder",
                        "details": {"folder_id": folder_id}
                    }
                }
            )

        # Build base query for spaces in the folder (excluding deleted)
        query = db.query(Space).filter(
            and_(
                Space.folder_id == folder_uuid,
                Space.deleted_at.is_(None)
            )
        )
        
        # Add type filter if provided
        if space_type:
            query = query.filter(Space.type == space_type)
        
        # Get total count for pagination
        total = query.count()
        
        # Apply pagination and ordering (newest first)
        spaces = query.order_by(Space.created_at.desc()).offset(
            (page - 1) * limit
        ).limit(limit).all()
        
        # Convert to response schemas
        space_responses = [
            SpaceResponse.model_validate(space) for space in spaces
        ]
        
        # Create pagination metadata
        meta = PaginationMeta(page=page, limit=limit, total=total)
        
        return SpaceListResponse(data=space_responses, meta=meta)
    
    @staticmethod
    def create_space(
        db: Session, 
        user: User, 
        folder_id: str, 
        space_data: SpaceCreate
    ) -> SpaceResponse:
        """
        Create a new space in a folder for the user.
        
        Args:
            db: Database session
            user: Current authenticated user
            folder_id: Parent folder UUID
            space_data: Space creation data
            
        Returns:
            SpaceResponse with created space data
            
        Raises:
            HTTPException: If folder not found or user doesn't own it
        """
        # Validate folder_id is a valid UUID
        try:
            folder_uuid = uuid.UUID(folder_id)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail={
                    "error": {
                        "code": "INVALID_UUID",
                        "message": "Invalid folder ID format",
                        "details": {"folder_id": folder_id}
                    }
                }
            )
        
        # First check if folder exists at all
        folder = db.query(Folder).filter(
            and_(
                Folder.id == folder_uuid,
                Folder.deleted_at.is_(None)
            )
        ).first()
        
        if not folder:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "error": {
                        "code": "FOLDER_NOT_FOUND",
                        "message": "Folder not found",
                        "details": {"folder_id": folder_id}
                    }
                }
            )
        
        # Then check if user owns the folder
        if folder.owner_id != user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "error": {
                        "code": "FORBIDDEN",
                        "message": "You do not have permission to access this folder",
                        "details": {"folder_id": folder_id}
                    }
                }
            )

        # Create space instance
        db_space = Space(
            folder_id=folder_uuid,
            type=SpaceType(space_data.type),
            title=space_data.title,
            settings=space_data.settings
        )
        
        # Save to database
        db.add(db_space)
        db.commit()
        db.refresh(db_space)
        
        return SpaceResponse.model_validate(db_space)
    
    @staticmethod
    def get_space(db: Session, user: User, space_id: str) -> SpaceResponse:
        """
        Get a specific space by ID, ensuring user owns the parent folder.
        
        Args:
            db: Database session
            user: Current authenticated user
            space_id: Space UUID
            
        Returns:
            SpaceResponse with space data
            
        Raises:
            HTTPException: If space not found or user doesn't own parent folder
        """
        # Validate space_id is a valid UUID
        try:
            space_uuid = uuid.UUID(space_id)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail={
                    "error": {
                        "code": "INVALID_UUID",
                        "message": "Invalid space ID format",
                        "details": {"space_id": space_id}
                    }
                }
            )
        
        # First check if space exists at all
        space = db.query(Space).filter(
            and_(
                Space.id == space_uuid,
                Space.deleted_at.is_(None)
            )
        ).first()
        
        if not space:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "error": {
                        "code": "SPACE_NOT_FOUND",
                        "message": "Space not found",
                        "details": {"space_id": space_id}
                    }
                }
            )
        
        # Then check if user owns the parent folder
        folder = db.query(Folder).filter(
            and_(
                Folder.id == space.folder_id,
                Folder.deleted_at.is_(None)
            )
        ).first()
        
        if not folder or folder.owner_id != user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "error": {
                        "code": "FORBIDDEN",
                        "message": "You don't have permission to access this space",
                        "details": {"space_id": space_id}
                    }
                }
            )
        
        return SpaceResponse.model_validate(space)
    
    @staticmethod
    def update_space(
        db: Session, 
        user: User, 
        space_id: str, 
        space_data: SpaceUpdate
    ) -> SpaceResponse:
        """
        Update an existing space, ensuring user owns the parent folder.
        
        Args:
            db: Database session
            user: Current authenticated user
            space_id: Space UUID
            space_data: Space update data
            
        Returns:
            SpaceResponse with updated space data
            
        Raises:
            HTTPException: If space not found or user doesn't own parent folder
        """
        # Validate space_id is a valid UUID
        try:
            space_uuid = uuid.UUID(space_id)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail={
                    "error": {
                        "code": "INVALID_UUID",
                        "message": "Invalid space ID format",
                        "details": {"space_id": space_id}
                    }
                }
            )
        
        # First check if space exists at all
        space = db.query(Space).filter(
            and_(
                Space.id == space_uuid,
                Space.deleted_at.is_(None)
            )
        ).first()
        
        if not space:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "error": {
                        "code": "SPACE_NOT_FOUND",
                        "message": "Space not found",
                        "details": {"space_id": space_id}
                    }
                }
            )
        
        # Then check if user owns the parent folder
        folder = db.query(Folder).filter(
            and_(
                Folder.id == space.folder_id,
                Folder.deleted_at.is_(None)
            )
        ).first()
        
        if not folder or folder.owner_id != user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "error": {
                        "code": "FORBIDDEN",
                        "message": "You don't have permission to access this space",
                        "details": {"space_id": space_id}
                    }
                }
            )

        # Update provided fields
        update_data = space_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(space, field, value)
        
        db.commit()
        db.refresh(space)
        
        return SpaceResponse.model_validate(space)
    
    @staticmethod
    def delete_space(db: Session, user: User, space_id: str) -> None:
        """
        Delete a space (soft delete), ensuring user owns the parent folder.
        
        Args:
            db: Database session
            user: Current authenticated user
            space_id: Space UUID
            
        Raises:
            HTTPException: If space not found or user doesn't own parent folder
        """
        # Validate space_id is a valid UUID
        try:
            space_uuid = uuid.UUID(space_id)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail={
                    "error": {
                        "code": "INVALID_UUID",
                        "message": "Invalid space ID format",
                        "details": {"space_id": space_id}
                    }
                }
            )
        
        # First check if space exists at all
        space = db.query(Space).filter(
            and_(
                Space.id == space_uuid,
                Space.deleted_at.is_(None)
            )
        ).first()
        
        if not space:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "error": {
                        "code": "SPACE_NOT_FOUND",
                        "message": "Space not found",
                        "details": {"space_id": space_id}
                    }
                }
            )
        
        # Then check if user owns the parent folder
        folder = db.query(Folder).filter(
            and_(
                Folder.id == space.folder_id,
                Folder.deleted_at.is_(None)
            )
        ).first()
        
        if not folder or folder.owner_id != user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "error": {
                        "code": "FORBIDDEN",
                        "message": "You don't have permission to access this space",
                        "details": {"space_id": space_id}
                    }
                }
            )

        # Soft delete the space
        from datetime import datetime
        space.deleted_at = datetime.utcnow()
        
        # Note: According to BACKEND_DATA_FLOWS.md section 4.5, space deletion
        # should cascade to delete all messages, quizzes, notes, etc. in the space.
        # This will be implemented when those models are created.
        
        db.commit()
    
    @staticmethod
    def verify_folder_ownership(db: Session, user: User, folder_id: str) -> Folder:
        """
        Verify that the user owns the specified folder.
        
        Args:
            db: Database session
            user: Current authenticated user
            folder_id: Folder UUID to verify
            
        Returns:
            Folder: The folder if owned by user
            
        Raises:
            HTTPException: If folder not found or user doesn't own it
        """
        folder = db.query(Folder).filter(
            and_(
                Folder.id == folder_id,
                Folder.owner_id == user.id,
                Folder.deleted_at.is_(None)
            )
        ).first()
        
        if not folder:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "error": {
                        "code": "FORBIDDEN",
                        "message": "Not enough permissions",
                        "details": {"folder_id": folder_id}
                    }
                }
            )
        
        return folder 