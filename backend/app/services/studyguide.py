"""
Study Guide service for study guide management operations.

Handles:
- Study guide creation with mock AI integration (backend developer portion only)
- Study guide listing with pagination and space validation
- Study guide retrieval with ownership verification
- Study guide updates with validation
- Study guide deletion with cascading operations
- Study session completion tracking
"""
import uuid
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc
from fastapi import HTTPException, status

from app.models.studyguide import StudyGuide
from app.models.space import Space, SpaceType
from app.models.file import File
from app.models.folder import Folder
from app.models.user import User
from app.schemas.studyguide import (
    StudyGuideCreate, 
    StudyGuideUpdate, 
    StudyGuideResponse, 
    StudyGuideListResponse,
    PaginationMeta
)


class StudyGuideService:
    """Service class for study guide management operations."""
    
    @staticmethod
    def create_study_guide(
        db: Session, 
        user: User, 
        space_id: str,
        study_guide_data: StudyGuideCreate
    ) -> StudyGuideResponse:
        """
        Create a study guide in a space.
        
        Backend Developer Implementation:
        - Validates space ownership and type
        - Validates file ownership and existence
        - Creates mock AI-generated schedule (placeholder for AI/ML Engineer)
        - Stores study guide in database
        
        Args:
            db: Database session
            user: Current authenticated user
            space_id: UUID of the target space
            study_guide_data: Study guide creation parameters
            
        Returns:
            StudyGuideResponse with created study guide
            
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
        
        # Verify space type is 'studyguide'
        if space.type != SpaceType.studyguide:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "error": {
                        "code": "INVALID_SPACE_TYPE",
                        "message": "Space must be of type 'studyguide'",
                        "details": {"space_type": space.type.value}
                    }
                }
            )
        
        # Verify user owns the folder containing the space
        folder = db.query(Folder).filter(
            and_(
                Folder.id == space.folder_id,
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
                        "message": "You don't have permission to access this space",
                        "details": {"space_id": space_id}
                    }
                }
            )
        
        # Validate deadline is in the future
        from datetime import timezone
        deadline = study_guide_data.deadline
        if deadline.tzinfo is None:
            deadline = deadline.replace(tzinfo=timezone.utc)
        if deadline <= datetime.now(timezone.utc):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "error": {
                        "code": "INVALID_DEADLINE",
                        "message": "Deadline must be in the future",
                        "details": {"deadline": study_guide_data.deadline.isoformat()}
                    }
                }
            )
        
        # Validate and fetch files
        files = []
        for file_id in study_guide_data.file_ids:
            try:
                file_uuid = uuid.UUID(file_id)
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail={
                        "error": {
                            "code": "INVALID_FILE_ID",
                            "message": f"Invalid file ID format: {file_id}",
                            "details": {"file_id": file_id}
                        }
                    }
                )
            
            # First check if file exists at all
            file = db.query(File).filter(
                and_(
                    File.id == file_uuid,
                    File.deleted_at.is_(None)
                )
            ).first()
            
            if not file:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail={
                        "error": {
                            "code": "FILE_NOT_FOUND",
                            "message": f"File not found: {file_id}",
                            "details": {"file_id": file_id}
                        }
                    }
                )
            
            # Then check if user has access to the file
            if file.folder_id != folder.id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail={
                        "error": {
                            "code": "FORBIDDEN",
                            "message": f"You don't have permission to access file: {file_id}",
                            "details": {"file_id": file_id}
                        }
                    }
                )
            
            files.append(file)
        
        # 🔄 **MOCK AI INTEGRATION** - Generate study schedule (placeholder for AI/ML Engineer)
        schedule, total_hours = StudyGuideService._mock_ai_generate_schedule(
            files=files,
            preferences=study_guide_data.preferences,
            deadline=study_guide_data.deadline,
            topics=study_guide_data.topics
        )
        
        # Create study guide
        study_guide = StudyGuide(
            id=uuid.uuid4(),
            space_id=space.id,
            title=study_guide_data.title,
            deadline=study_guide_data.deadline,
            total_study_hours=total_hours,
            schedule=schedule,
            preferences=study_guide_data.preferences,
            progress={
                "completedHours": 0,
                "completedSessions": 0,
                "totalSessions": len(schedule)
            },
            file_ids=study_guide_data.file_ids,
            topics=study_guide_data.topics or [],
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        db.add(study_guide)
        db.commit()
        db.refresh(study_guide)
        
        return StudyGuideResponse.model_validate(study_guide)
    
    @staticmethod
    def _mock_ai_generate_schedule(
        files: List[File], 
        preferences: Dict[str, Any],
        deadline: datetime,
        topics: List[str]
    ) -> tuple[List[Dict[str, Any]], int]:
        """
        Mock AI service for generating study schedule.
        
        This is a placeholder implementation for the backend developer.
        The actual AI/ML Engineer will implement the real AI integration.
        
        Args:
            files: List of files to generate schedule from
            preferences: User study preferences
            deadline: Target completion date
            topics: List of topics to cover
            
        Returns:
            Tuple of (schedule, total_hours)
        """
        # Mock schedule generation based on preferences and deadline
        daily_hours = preferences.get('dailyStudyHours', 2)
        preferred_times = preferences.get('preferredTimes', ['morning'])
        study_methods = preferences.get('studyMethods', ['reading'])
        
        # Calculate total days until deadline
        from datetime import timezone
        now = datetime.now(timezone.utc)
        if deadline.tzinfo is None:
            deadline = deadline.replace(tzinfo=timezone.utc)
        days_until_deadline = (deadline - now).days
        if days_until_deadline <= 0:
            days_until_deadline = 1
        
        # Generate mock schedule
        schedule = []
        total_hours = 0
        
        for day in range(1, min(days_until_deadline + 1, 30)):  # Max 30 days
            session_date = datetime.now(timezone.utc) + timedelta(days=day)
            
            # Create morning session
            if 'morning' in preferred_times:
                session = {
                    "id": f"session_{day}_morning",
                    "date": session_date.isoformat() + "Z",
                    "startTime": "09:00",
                    "endTime": "11:00",
                    "topic": f"Topic {day}" if not topics else topics[min(day - 1, len(topics) - 1)],
                    "activities": [
                        {
                            "type": "review",
                            "resourceId": str(files[0].id) if files else "mock-file-id",
                            "resourceType": "file",
                            "duration": 60
                        },
                        {
                            "type": "practice",
                            "resourceId": "mock-quiz-id",
                            "resourceType": "quiz",
                            "duration": 60
                        }
                    ],
                    "completed": False
                }
                schedule.append(session)
                total_hours += 2
            
            # Create evening session if needed
            if 'evening' in preferred_times and daily_hours > 2:
                session = {
                    "id": f"session_{day}_evening",
                    "date": session_date.isoformat() + "Z",
                    "startTime": "19:00",
                    "endTime": "21:00",
                    "topic": f"Evening Review {day}",
                    "activities": [
                        {
                            "type": "flashcards",
                            "resourceId": "mock-flashcard-id",
                            "resourceType": "flashcard",
                            "duration": 120
                        }
                    ],
                    "completed": False
                }
                schedule.append(session)
                total_hours += 2
            
            # Stop if we've reached the daily hours limit
            if len(schedule) >= daily_hours * days_until_deadline:
                break
        
        return schedule, total_hours
    
    @staticmethod
    def list_study_guides(
        db: Session, 
        user: User, 
        space_id: str,
        page: int = 1, 
        limit: int = 20
    ) -> StudyGuideListResponse:
        """
        List study guides in a space with pagination.
        
        Args:
            db: Database session
            user: Current authenticated user
            space_id: UUID of the target space
            page: Page number (1-based)
            limit: Number of items per page
            
        Returns:
            StudyGuideListResponse with paginated study guides
            
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
        
        # Verify space type is 'studyguide'
        if space.type != SpaceType.studyguide:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "error": {
                        "code": "INVALID_SPACE_TYPE",
                        "message": "Space must be of type 'studyguide'",
                        "details": {"space_type": space.type.value}
                    }
                }
            )
        
        # Verify user owns the folder containing the space
        folder = db.query(Folder).filter(
            and_(
                Folder.id == space.folder_id,
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
                        "message": "You don't have permission to access this space",
                        "details": {"space_id": space_id}
                    }
                }
            )
        
        # Query study guides with pagination
        offset = (page - 1) * limit
        
        study_guides_query = db.query(StudyGuide).filter(
            and_(
                StudyGuide.space_id == space.id,
                StudyGuide.deleted_at.is_(None)
            )
        ).order_by(desc(StudyGuide.created_at))
        
        total = study_guides_query.count()
        study_guides = study_guides_query.offset(offset).limit(limit).all()
        
        # Convert to response models
        study_guide_responses = [
            StudyGuideResponse.model_validate(study_guide) 
            for study_guide in study_guides
        ]
        
        return StudyGuideListResponse(
            data=study_guide_responses,
            meta=PaginationMeta(
                page=page,
                limit=limit,
                total=total
            )
        )
    
    @staticmethod
    def get_study_guide(
        db: Session, 
        user: User, 
        study_guide_id: str
    ) -> StudyGuideResponse:
        """
        Get a specific study guide by ID.
        
        Args:
            db: Database session
            user: Current authenticated user
            study_guide_id: UUID of the study guide
            
        Returns:
            StudyGuideResponse with study guide data
            
        Raises:
            HTTPException: If study guide not found or user lacks permission
        """
        # Validate study_guide_id is a valid UUID
        try:
            study_guide_uuid = uuid.UUID(study_guide_id)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail={
                    "error": {
                        "code": "INVALID_UUID",
                        "message": "Invalid study guide ID format",
                        "details": {"study_guide_id": study_guide_id}
                    }
                }
            )
        
        # Fetch study guide with space and folder information
        study_guide = db.query(StudyGuide).join(Space).filter(
            and_(
                StudyGuide.id == study_guide_uuid,
                StudyGuide.deleted_at.is_(None),
                Space.deleted_at.is_(None)  # Check that parent space is not deleted
            )
        ).first()
        
        if not study_guide:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "error": {
                        "code": "STUDY_GUIDE_NOT_FOUND",
                        "message": "Study guide not found",
                        "details": {"study_guide_id": study_guide_id}
                    }
                }
            )
        
        # Verify user owns the folder containing the space
        folder = db.query(Folder).join(Space).filter(
            and_(
                Space.id == study_guide.space_id,
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
                        "message": "You don't have permission to access this study guide",
                        "details": {"study_guide_id": study_guide_id}
                    }
                }
            )
        
        return StudyGuideResponse.model_validate(study_guide)
    
    @staticmethod
    def update_study_guide(
        db: Session, 
        user: User, 
        study_guide_id: str,
        study_guide_data: StudyGuideUpdate
    ) -> StudyGuideResponse:
        """
        Update an existing study guide.
        
        Args:
            db: Database session
            user: Current authenticated user
            study_guide_id: UUID of the study guide to update
            study_guide_data: Update data
            
        Returns:
            StudyGuideResponse with updated study guide data
            
        Raises:
            HTTPException: If validation fails or user lacks permission
        """
        # Validate study_guide_id is a valid UUID
        try:
            study_guide_uuid = uuid.UUID(study_guide_id)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail={
                    "error": {
                        "code": "INVALID_UUID",
                        "message": "Invalid study guide ID format",
                        "details": {"study_guide_id": study_guide_id}
                    }
                }
            )
        
        # Fetch study guide
        study_guide = db.query(StudyGuide).filter(
            and_(
                StudyGuide.id == study_guide_uuid,
                StudyGuide.deleted_at.is_(None)
            )
        ).first()
        
        if not study_guide:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "error": {
                        "code": "STUDY_GUIDE_NOT_FOUND",
                        "message": "Study guide not found",
                        "details": {"study_guide_id": study_guide_id}
                    }
                }
            )
        
        # Verify user owns the folder containing the space
        folder = db.query(Folder).join(Space).filter(
            and_(
                Space.id == study_guide.space_id,
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
                        "message": "You don't have permission to access this study guide",
                        "details": {"study_guide_id": study_guide_id}
                    }
                }
            )
        
        # Update fields if provided
        update_data = study_guide_data.model_dump(exclude_unset=True)
        
        if update_data:
            for field, value in update_data.items():
                setattr(study_guide, field, value)
            
            study_guide.updated_at = datetime.utcnow()
            db.commit()
            db.refresh(study_guide)
        
        return StudyGuideResponse.model_validate(study_guide)
    
    @staticmethod
    def delete_study_guide(
        db: Session, 
        user: User, 
        study_guide_id: str
    ) -> None:
        """
        Delete a study guide (soft delete).
        
        Args:
            db: Database session
            user: Current authenticated user
            study_guide_id: UUID of the study guide to delete
            
        Raises:
            HTTPException: If study guide not found or user lacks permission
        """
        # Validate study_guide_id is a valid UUID
        try:
            study_guide_uuid = uuid.UUID(study_guide_id)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail={
                    "error": {
                        "code": "INVALID_UUID",
                        "message": "Invalid study guide ID format",
                        "details": {"study_guide_id": study_guide_id}
                    }
                }
            )
        
        # Fetch study guide
        study_guide = db.query(StudyGuide).filter(
            and_(
                StudyGuide.id == study_guide_uuid,
                StudyGuide.deleted_at.is_(None)
            )
        ).first()
        
        if not study_guide:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "error": {
                        "code": "STUDY_GUIDE_NOT_FOUND",
                        "message": "Study guide not found",
                        "details": {"study_guide_id": study_guide_id}
                    }
                }
            )
        
        # Verify user owns the folder containing the space
        folder = db.query(Folder).join(Space).filter(
            and_(
                Space.id == study_guide.space_id,
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
                        "message": "You don't have permission to access this study guide",
                        "details": {"study_guide_id": study_guide_id}
                    }
                }
            )
        
        # Soft delete
        study_guide.deleted_at = datetime.utcnow()
        db.commit()
    
    @staticmethod
    def complete_study_session(
        db: Session, 
        user: User, 
        study_guide_id: str,
        session_id: str
    ) -> StudyGuideResponse:
        """
        Mark a study session as completed.
        
        Args:
            db: Database session
            user: Current authenticated user
            study_guide_id: UUID of the study guide
            session_id: ID of the session to mark as completed
            
        Returns:
            StudyGuideResponse with updated study guide data
            
        Raises:
            HTTPException: If validation fails or user lacks permission
        """
        # Validate study_guide_id is a valid UUID
        try:
            study_guide_uuid = uuid.UUID(study_guide_id)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail={
                    "error": {
                        "code": "INVALID_UUID",
                        "message": "Invalid study guide ID format",
                        "details": {"study_guide_id": study_guide_id}
                    }
                }
            )
        
        # Fetch study guide
        study_guide = db.query(StudyGuide).filter(
            and_(
                StudyGuide.id == study_guide_uuid,
                StudyGuide.deleted_at.is_(None)
            )
        ).first()
        
        if not study_guide:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "error": {
                        "code": "STUDY_GUIDE_NOT_FOUND",
                        "message": "Study guide not found",
                        "details": {"study_guide_id": study_guide_id}
                    }
                }
            )
        
        # Verify user owns the folder containing the space
        folder = db.query(Folder).join(Space).filter(
            and_(
                Space.id == study_guide.space_id,
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
                        "message": "You don't have permission to access this study guide",
                        "details": {"study_guide_id": study_guide_id}
                    }
                }
            )
        
        # Find and update the session
        session_found = False
        for session in study_guide.schedule:
            if session.get("id") == session_id:
                session["completed"] = True
                session_found = True
                break
        
        if not session_found:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "error": {
                        "code": "SESSION_NOT_FOUND",
                        "message": "Study session not found",
                        "details": {"session_id": session_id}
                    }
                }
            )
        
        # Update progress
        completed_sessions = sum(1 for session in study_guide.schedule if session.get("completed", False))
        completed_hours = completed_sessions * 2  # Assume 2 hours per session
        
        study_guide.progress = {
            "completedHours": completed_hours,
            "completedSessions": completed_sessions,
            "totalSessions": len(study_guide.schedule)
        }
        
        study_guide.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(study_guide)
        
        return StudyGuideResponse.model_validate(study_guide) 