"""
Notes service for note management operations.

Handles:
- Notes generation with mock AI integration (backend developer portion only)
- Notes listing with pagination and space validation
- Notes retrieval with ownership verification
- Notes updates with validation
- Notes deletion with cascading operations
"""
import uuid
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc
from fastapi import HTTPException, status

from app.models.note import Note, NotesFormat
from app.models.space import Space, SpaceType
from app.models.file import File
from app.models.folder import Folder
from app.models.user import User
from app.schemas.note import (
    NotesCreate, 
    NotesUpdate, 
    NotesResponse, 
    NotesListResponse,
    PaginationMeta
)


class NotesService:
    """Service class for notes management operations."""
    
    @staticmethod
    def generate_notes(
        db: Session, 
        user: User, 
        space_id: str,
        notes_data: NotesCreate
    ) -> NotesResponse:
        """
        Generate notes from files in a space.
        
        Backend Developer Implementation:
        - Validates space ownership and type
        - Validates file ownership and existence
        - Creates mock AI-generated content (placeholder for AI/ML Engineer)
        - Stores note in database
        
        Args:
            db: Database session
            user: Current authenticated user
            space_id: UUID of the target space
            notes_data: Notes creation parameters
            
        Returns:
            NotesResponse with generated note
            
        Raises:
            HTTPException: If validation fails or user lacks permission
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
        
        # Fetch and validate space
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
        
        # Verify space type is 'notes'
        if space.type != SpaceType.notes:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "error": {
                        "code": "INVALID_SPACE_TYPE",
                        "message": f"Space type must be 'notes', got '{space.type.value}'",
                        "details": {"space_type": space.type.value, "expected": "notes"}
                    }
                }
            )
        
        # Verify user owns the parent folder
        if space.folder.owner_id != user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "error": {
                        "code": "FORBIDDEN",
                        "message": "You do not have permission to access this space",
                        "details": None
                    }
                }
            )
        
        # Validate and fetch files
        file_uuids = []
        for file_id in notes_data.file_ids:
            try:
                file_uuid = uuid.UUID(file_id)
                file_uuids.append(file_uuid)
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail={
                        "error": {
                            "code": "INVALID_UUID",
                            "message": f"Invalid file ID format: {file_id}",
                            "details": {"file_id": file_id}
                        }
                    }
                )
        
        # Fetch files and verify ownership
        files = db.query(File).join(Folder).filter(
            and_(
                File.id.in_(file_uuids),
                File.deleted_at.is_(None),
                Folder.owner_id == user.id
            )
        ).all()
        
        if len(files) != len(file_uuids):
            found_ids = {str(f.id) for f in files}
            missing_ids = [fid for fid in notes_data.file_ids if fid not in found_ids]
            
            if missing_ids:
                # Check if files exist but user doesn't own them
                existing_files = db.query(File).filter(
                    and_(
                        File.id.in_([uuid.UUID(fid) for fid in missing_ids]),
                        File.deleted_at.is_(None)
                    )
                ).all()
                
                if existing_files:
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail={
                            "error": {
                                "code": "FORBIDDEN",
                                "message": "You do not have permission to access some of the specified files",
                                "details": {"inaccessible_files": missing_ids}
                            }
                        }
                    )
                else:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail={
                            "error": {
                                "code": "FILE_NOT_FOUND",
                                "message": "One or more files not found",
                                "details": {"missing_files": missing_ids}
                            }
                        }
                    )
        
        # Mock AI content generation (Backend Developer portion only)
        # TODO: This will be replaced by AI/ML Engineer with actual AI generation
        generated_content = NotesService._mock_ai_generate_notes(files, notes_data.format)
        
        # Create note record
        note = Note(
            id=uuid.uuid4(),
            space_id=space_uuid,
            format=notes_data.format,
            content=generated_content,
            file_ids=[str(f.id) for f in files]
        )
        
        db.add(note)
        db.commit()
        db.refresh(note)
        
        return NotesResponse.model_validate(note)
    
    @staticmethod
    def _mock_ai_generate_notes(files: List[File], format: NotesFormat) -> str:
        """
        Mock AI notes generation (Backend Developer placeholder).
        
        This is a placeholder implementation that will be replaced by the AI/ML Engineer
        with actual AI-powered content generation using OpenAI API.
        
        Args:
            files: List of files to generate notes from
            format: Desired format for the notes
            
        Returns:
            Mock generated content string
        """
        file_names = [f.name for f in files]
        total_content_length = sum(len(f.text_content or "") for f in files)
        
        if format == NotesFormat.markdown:
            content = f"""# Generated Notes

## Summary

These notes were generated from {len(files)} files: {', '.join(file_names)}

## Key Points

Based on the analysis of {total_content_length} characters of content, here are the main points:

### Important Concepts
- **File Analysis**: Content extracted from multiple sources
- **Information Synthesis**: Key information identified and organized
- **Structured Format**: Notes formatted for easy reading

### Details
The analysis covered content from the following files:
"""
            for i, file in enumerate(files, 1):
                content += f"\n{i}. **{file.name}** ({file.mime_type})"
                if file.text_content:
                    preview = file.text_content[:100].replace('\n', ' ')
                    content += f"\n   - Preview: {preview}..."
            
            content += "\n\n### Conclusion\nThis is mock-generated content. Actual AI generation will be implemented by the AI/ML Engineer."
            
        else:  # bullet format
            content = f"""Generated Notes from {len(files)} files

Key Points:
• Files analyzed: {', '.join(file_names)}
• Total content: {total_content_length} characters
• Format: Bullet points for easy scanning

Main Topics:
"""
            for i, file in enumerate(files, 1):
                content += f"• File {i}: {file.name}\n"
                if file.text_content:
                    preview = file.text_content[:100].replace('\n', ' ')
                    content += f"  - Preview: {preview}...\n"
            
            content += "\n• Note: This is mock-generated content\n• Actual AI generation will be implemented by the AI/ML Engineer"
        
        return content
    
    @staticmethod
    def list_notes(
        db: Session, 
        user: User, 
        space_id: str,
        page: int = 1, 
        limit: int = 20
    ) -> NotesListResponse:
        """
        List notes in a space for a user with pagination.
        
        Args:
            db: Database session
            user: Current authenticated user
            space_id: Parent space UUID
            page: Page number (1-based)
            limit: Items per page
            
        Returns:
            NotesListResponse with notes and pagination metadata
            
        Raises:
            HTTPException: If space not found or user doesn't own it
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
        
        # Fetch and validate space
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
        
        # Verify space type is 'notes'
        if space.type != SpaceType.notes:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "error": {
                        "code": "INVALID_SPACE_TYPE",
                        "message": f"Space type must be 'notes', got '{space.type.value}'",
                        "details": {"space_type": space.type.value, "expected": "notes"}
                    }
                }
            )
        
        # Verify user owns the parent folder
        if space.folder.owner_id != user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "error": {
                        "code": "FORBIDDEN",
                        "message": "You do not have permission to access this space",
                        "details": None
                    }
                }
            )
        
        # Query notes with pagination
        offset = (page - 1) * limit
        
        query = db.query(Note).filter(
            and_(
                Note.space_id == space_uuid,
                Note.deleted_at.is_(None)
            )
        ).order_by(desc(Note.created_at))
        
        total = query.count()
        notes = query.offset(offset).limit(limit).all()
        
        # Convert to response models
        note_responses = [NotesResponse.model_validate(note) for note in notes]
        
        return NotesListResponse(
            data=note_responses,
            meta=PaginationMeta(
                page=page,
                limit=limit,
                total=total
            )
        )
    
    @staticmethod
    def get_note(
        db: Session, 
        user: User, 
        note_id: str
    ) -> NotesResponse:
        """
        Get a specific note by ID with ownership verification.
        
        Args:
            db: Database session
            user: Current authenticated user
            note_id: UUID of the note to retrieve
            
        Returns:
            NotesResponse with note data
            
        Raises:
            HTTPException: If note not found or user doesn't own it
        """
        # Validate note_id is a valid UUID
        try:
            note_uuid = uuid.UUID(note_id)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail={
                    "error": {
                        "code": "INVALID_UUID",
                        "message": "Invalid note ID format",
                        "details": {"note_id": note_id}
                    }
                }
            )
        
        # Fetch note with relationships
        note = db.query(Note).join(Space).join(Folder).filter(
            and_(
                Note.id == note_uuid,
                Note.deleted_at.is_(None),
                Space.deleted_at.is_(None),
                Folder.deleted_at.is_(None)
            )
        ).first()
        
        if not note:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "error": {
                        "code": "NOTE_NOT_FOUND",
                        "message": "Note not found",
                        "details": {"note_id": note_id}
                    }
                }
            )
        
        # Verify user owns the parent folder through space
        if note.space.folder.owner_id != user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "error": {
                        "code": "FORBIDDEN",
                        "message": "You do not have permission to access this note",
                        "details": None
                    }
                }
            )
        
        return NotesResponse.model_validate(note)
    
    @staticmethod
    def update_note(
        db: Session, 
        user: User, 
        note_id: str,
        notes_data: NotesUpdate
    ) -> NotesResponse:
        """
        Update an existing note with validation.
        
        Args:
            db: Database session
            user: Current authenticated user
            note_id: UUID of the note to update
            notes_data: Update data
            
        Returns:
            NotesResponse with updated note data
            
        Raises:
            HTTPException: If note not found or user doesn't own it
        """
        # Validate note_id is a valid UUID
        try:
            note_uuid = uuid.UUID(note_id)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail={
                    "error": {
                        "code": "INVALID_UUID",
                        "message": "Invalid note ID format",
                        "details": {"note_id": note_id}
                    }
                }
            )
        
        # Fetch note with relationships
        note = db.query(Note).join(Space).join(Folder).filter(
            and_(
                Note.id == note_uuid,
                Note.deleted_at.is_(None),
                Space.deleted_at.is_(None),
                Folder.deleted_at.is_(None)
            )
        ).first()
        
        if not note:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "error": {
                        "code": "NOTE_NOT_FOUND",
                        "message": "Note not found",
                        "details": {"note_id": note_id}
                    }
                }
            )
        
        # Verify user owns the parent folder through space
        if note.space.folder.owner_id != user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "error": {
                        "code": "FORBIDDEN",
                        "message": "You do not have permission to update this note",
                        "details": None
                    }
                }
            )
        
        # Update fields if provided
        if notes_data.content is not None:
            note.content = notes_data.content
        
        db.commit()
        db.refresh(note)
        
        return NotesResponse.model_validate(note)
    
    @staticmethod
    def delete_note(
        db: Session, 
        user: User, 
        note_id: str
    ) -> None:
        """
        Delete an existing note (soft delete).
        
        Args:
            db: Database session
            user: Current authenticated user
            note_id: UUID of the note to delete
            
        Raises:
            HTTPException: If note not found or user doesn't own it
        """
        # Validate note_id is a valid UUID
        try:
            note_uuid = uuid.UUID(note_id)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail={
                    "error": {
                        "code": "INVALID_UUID",
                        "message": "Invalid note ID format",
                        "details": {"note_id": note_id}
                    }
                }
            )
        
        # Fetch note with relationships
        note = db.query(Note).join(Space).join(Folder).filter(
            and_(
                Note.id == note_uuid,
                Note.deleted_at.is_(None),
                Space.deleted_at.is_(None),
                Folder.deleted_at.is_(None)
            )
        ).first()
        
        if not note:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "error": {
                        "code": "NOTE_NOT_FOUND",
                        "message": "Note not found",
                        "details": {"note_id": note_id}
                    }
                }
            )
        
        # Verify user owns the parent folder through space
        if note.space.folder.owner_id != user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "error": {
                        "code": "FORBIDDEN",
                        "message": "You do not have permission to delete this note",
                        "details": None
                    }
                }
            )
        
        # Soft delete the note
        from datetime import datetime
        note.deleted_at = datetime.utcnow()
        
        db.commit() 