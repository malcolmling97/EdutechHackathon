"""
Folder service for folder management operations.

Handles:
- Folder listing with pagination and search
- Folder creation with validation
- Folder retrieval with ownership verification
- Folder updates with validation
- Folder deletion with cascading operations
"""
from typing import Optional, List, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from fastapi import HTTPException, status

from app.models.folder import Folder
from app.models.user import User
from app.schemas.folder import (
    FolderCreate, 
    FolderUpdate, 
    FolderResponse, 
    FolderListResponse,
    PaginationMeta
)


class FolderService:
    """Service class for folder management operations."""
    
    @staticmethod
    def list_folders(
        db: Session, 
        user: User, 
        page: int = 1, 
        limit: int = 20, 
        search_query: Optional[str] = None
    ) -> FolderListResponse:
        """
        List folders for a user with pagination and optional search.
        
        Args:
            db: Database session
            user: Current authenticated user
            page: Page number (1-based)
            limit: Items per page
            search_query: Optional search term for folder titles
            
        Returns:
            FolderListResponse with folders and pagination metadata
        """
        # Build base query for user's folders (excluding deleted)
        query = db.query(Folder).filter(
            and_(
                Folder.owner_id == user.id,
                Folder.deleted_at.is_(None)
            )
        )
        
        # Add search filter if provided
        if search_query:
            search_term = f"%{search_query.lower()}%"
            query = query.filter(
                or_(
                    Folder.title.ilike(search_term),
                    Folder.description.ilike(search_term)
                )
            )
        
        # Get total count for pagination
        total = query.count()
        
        # Apply pagination and ordering
        folders = query.order_by(Folder.created_at.desc()).offset(
            (page - 1) * limit
        ).limit(limit).all()
        
        # Convert to response schemas
        folder_responses = [
            FolderResponse.model_validate(folder) for folder in folders
        ]
        
        # Create pagination metadata
        meta = PaginationMeta(page=page, limit=limit, total=total)
        
        return FolderListResponse(data=folder_responses, meta=meta)
    
    @staticmethod
    def create_folder(db: Session, user: User, folder_data: FolderCreate) -> FolderResponse:
        """
        Create a new folder for the user.
        
        Args:
            db: Database session
            user: Current authenticated user
            folder_data: Folder creation data
            
        Returns:
            FolderResponse with created folder data
        """
        # Create folder instance
        db_folder = Folder(
            owner_id=user.id,
            title=folder_data.title,
            description=folder_data.description
        )
        
        # Save to database
        db.add(db_folder)
        db.commit()
        db.refresh(db_folder)
        
        return FolderResponse.model_validate(db_folder)
    
    @staticmethod
    def get_folder(db: Session, user: User, folder_id: str) -> FolderResponse:
        """
        Get a specific folder by ID, ensuring user ownership.
        
        Args:
            db: Database session
            user: Current authenticated user
            folder_id: Folder UUID
            
        Returns:
            FolderResponse with folder data
            
        Raises:
            HTTPException: If folder not found or user doesn't own it
        """
        folder = db.query(Folder).filter(
            and_(
                Folder.id == folder_id,
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
        
        if folder.owner_id != user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "error": {
                        "code": "ACCESS_FORBIDDEN",
                        "message": "You do not have permission to access this folder",
                        "details": {"folder_id": folder_id}
                    }
                }
            )
        
        return FolderResponse.model_validate(folder)
    
    @staticmethod
    def update_folder(
        db: Session, 
        user: User, 
        folder_id: str, 
        folder_data: FolderUpdate
    ) -> FolderResponse:
        """
        Update an existing folder, ensuring user ownership.
        
        Args:
            db: Database session
            user: Current authenticated user
            folder_id: Folder UUID
            folder_data: Folder update data
            
        Returns:
            FolderResponse with updated folder data
            
        Raises:
            HTTPException: If folder not found or user doesn't own it
        """
        folder = db.query(Folder).filter(
            and_(
                Folder.id == folder_id,
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
        
        if folder.owner_id != user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "error": {
                        "code": "ACCESS_FORBIDDEN",
                        "message": "You do not have permission to update this folder",
                        "details": {"folder_id": folder_id}
                    }
                }
            )
        
        # Update provided fields
        update_data = folder_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(folder, field, value)
        
        db.commit()
        db.refresh(folder)
        
        return FolderResponse.model_validate(folder)
    
    @staticmethod
    def delete_folder(db: Session, user: User, folder_id: str) -> None:
        """
        Delete a folder (soft delete), ensuring user ownership.
        
        Args:
            db: Database session
            user: Current authenticated user
            folder_id: Folder UUID
            
        Raises:
            HTTPException: If folder not found or user doesn't own it
        """
        folder = db.query(Folder).filter(
            and_(
                Folder.id == folder_id,
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
        
        if folder.owner_id != user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "error": {
                        "code": "ACCESS_FORBIDDEN",
                        "message": "You do not have permission to delete this folder",
                        "details": {"folder_id": folder_id}
                    }
                }
            )
        
        # Soft delete the folder
        from datetime import datetime
        folder.deleted_at = datetime.utcnow()
        
        # Note: According to BACKEND_DATA_FLOWS.md section 3.5, folder deletion
        # should cascade to delete all spaces and files in the folder.
        # This will be implemented when space and file models are created.
        
        db.commit() 