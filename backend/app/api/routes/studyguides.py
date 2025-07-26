"""
Study Guides routes for the EdutechHackathon API.

Endpoints:
- POST /spaces/{spaceId}/studyguides - Create study guide
- GET /spaces/{spaceId}/studyguides - List study guides
- GET /studyguides/{id} - Get specific study guide
- PATCH /studyguides/{id} - Update study guide
- DELETE /studyguides/{id} - Delete study guide
- POST /studyguides/{id}/sessions/{sessionId}/complete - Mark session complete
"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query, Path, Response
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.schemas.studyguide import (
    StudyGuideCreate,
    StudyGuideUpdate,
    StudyGuideListResponse,
    StudyGuideResponseWrapper,
    StudySessionCompleteResponse
)
from app.services.studyguide import StudyGuideService


router = APIRouter()


@router.post(
    "/spaces/{space_id}/studyguides",
    response_model=StudyGuideResponseWrapper,
    status_code=status.HTTP_201_CREATED,
    summary="Create study guide",
    description="Create a study guide with schedule in a studyguide space using AI (mock implementation for backend developer)."
)
async def create_study_guide(
    space_id: str = Path(..., description="Space UUID"),
    study_guide_data: StudyGuideCreate = ...,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a study guide in a studyguide space.
    
    **Backend Developer Implementation:**
    - Validates space ownership and type (must be 'studyguide')
    - Validates file ownership and existence
    - Creates mock AI-generated schedule (placeholder for AI/ML Engineer)
    - Stores study guide in database
    
    **Parameters:**
    - **space_id**: UUID of the studyguide space
    - **title**: Study guide title (required)
    - **deadline**: Target completion date (required, must be in future)
    - **preferences**: User study preferences (required)
    - **file_ids**: List of file UUIDs to generate study guide from (required)
    - **topics**: List of topics to cover (optional)
    
    **Returns:**
    Created study guide with generated schedule.
    
    **Note:** The AI schedule generation is currently mocked. 
    Actual AI integration will be implemented by the AI/ML Engineer.
    """
    study_guide_response = StudyGuideService.create_study_guide(
        db=db,
        user=current_user,
        space_id=space_id,
        study_guide_data=study_guide_data
    )
    
    return StudyGuideResponseWrapper(data=study_guide_response)


@router.get(
    "/spaces/{space_id}/studyguides",
    response_model=StudyGuideListResponse,
    status_code=status.HTTP_200_OK,
    summary="List study guides",
    description="Get a paginated list of study guides in a studyguide space owned by the current user."
)
async def list_study_guides(
    space_id: str = Path(..., description="Space UUID"),
    page: int = Query(1, ge=1, description="Page number (1-based)"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    List study guides in a studyguide space for the current user.
    
    **Parameters:**
    - **space_id**: UUID of the studyguide space
    - **page**: Page number starting from 1
    - **limit**: Number of items per page (1-100)
    
    **Returns:**
    Paginated list of study guides with metadata.
    
    **Requirements:**
    - Space must be of type 'studyguide'
    - User must own the parent folder
    """
    return StudyGuideService.list_study_guides(
        db=db,
        user=current_user,
        space_id=space_id,
        page=page,
        limit=limit
    )


@router.get(
    "/studyguides/{study_guide_id}",
    response_model=StudyGuideResponseWrapper,
    status_code=status.HTTP_200_OK,
    summary="Get study guide",
    description="Get a specific study guide by ID, ensuring user owns the parent folder."
)
async def get_study_guide(
    study_guide_id: str = Path(..., description="Study Guide UUID"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get a specific study guide by ID.
    
    **Parameters:**
    - **study_guide_id**: UUID of the study guide to retrieve
    
    **Returns:**
    The study guide data if user has access.
    
    **Access Control:**
    User must own the folder containing the space that contains the study guide.
    """
    study_guide_response = StudyGuideService.get_study_guide(
        db=db,
        user=current_user,
        study_guide_id=study_guide_id
    )
    
    return StudyGuideResponseWrapper(data=study_guide_response)


@router.patch(
    "/studyguides/{study_guide_id}",
    response_model=StudyGuideResponseWrapper,
    status_code=status.HTTP_200_OK,
    summary="Update study guide",
    description="Update a study guide's title, deadline, or preferences, ensuring user owns the parent folder."
)
async def update_study_guide(
    study_guide_id: str = Path(..., description="Study Guide UUID"),
    study_guide_data: StudyGuideUpdate = ...,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update an existing study guide.
    
    **Parameters:**
    - **study_guide_id**: UUID of the study guide to update
    - **title**: New study guide title (optional)
    - **deadline**: New target completion date (optional, must be in future)
    - **preferences**: Updated study preferences (optional)
    
    **Returns:**
    The updated study guide data.
    
    **Validation:**
    - Title cannot be empty or contain only whitespace
    - Deadline must be in the future
    - User must own the folder containing the space that contains the study guide
    
    **Note:** Only title, deadline, and preferences can be updated. 
    Schedule and other metadata are managed by the AI system.
    """
    study_guide_response = StudyGuideService.update_study_guide(
        db=db,
        user=current_user,
        study_guide_id=study_guide_id,
        study_guide_data=study_guide_data
    )
    
    return StudyGuideResponseWrapper(data=study_guide_response)


@router.delete(
    "/studyguides/{study_guide_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete study guide",
    description="Delete a study guide (soft delete), ensuring user owns the parent folder."
)
async def delete_study_guide(
    study_guide_id: str = Path(..., description="Study Guide UUID"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete an existing study guide.
    
    **Parameters:**
    - **study_guide_id**: UUID of the study guide to delete
    
    **Returns:**
    204 No Content on successful deletion.
    
    **Implementation:**
    This is a soft delete - the study guide is marked as deleted but not removed from the database.
    The study guide will cascade delete when the parent space is deleted.
    
    **Access Control:**
    User must own the folder containing the space that contains the study guide.
    """
    StudyGuideService.delete_study_guide(
        db=db,
        user=current_user,
        study_guide_id=study_guide_id
    )
    
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post(
    "/studyguides/{study_guide_id}/sessions/{session_id}/complete",
    response_model=StudySessionCompleteResponse,
    status_code=status.HTTP_200_OK,
    summary="Complete study session",
    description="Mark a study session as completed and update progress tracking."
)
async def complete_study_session(
    study_guide_id: str = Path(..., description="Study Guide UUID"),
    session_id: str = Path(..., description="Session ID"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Mark a study session as completed.
    
    **Parameters:**
    - **study_guide_id**: UUID of the study guide
    - **session_id**: ID of the session to mark as completed
    
    **Returns:**
    Updated study guide data with progress tracking.
    
    **Implementation:**
    - Marks the specified session as completed
    - Updates progress tracking (completed hours and sessions)
    - Returns the updated study guide with current progress
    
    **Access Control:**
    User must own the folder containing the space that contains the study guide.
    """
    study_guide_response = StudyGuideService.complete_study_session(
        db=db,
        user=current_user,
        study_guide_id=study_guide_id,
        session_id=session_id
    )
    
    return StudySessionCompleteResponse(data=study_guide_response) 