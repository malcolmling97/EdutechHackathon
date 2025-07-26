"""
Open-ended Question routes for the EdutechHackathon API.

Endpoints:
- POST /spaces/{spaceId}/openended - Generate open-ended questions from selected files + params
- GET /spaces/{spaceId}/openended - List open-ended question sets
- GET /openended/{id} - Retrieve question set
- POST /openended/{id}/submit - Submit answers for AI grading
- GET /openended/{id}/answers - Get user's submitted answers and grades
- DELETE /openended/{id} - Delete question set
"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query, Path, Response
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.schemas.openended import (
    OpenEndedQuestionCreate,
    OpenEndedListResponse,
    OpenEndedResponseWrapper,
    OpenEndedSubmission,
    OpenEndedAnswerResponseWrapper,
    OpenEndedAnswersListResponse
)
from app.services.openended import OpenEndedService


router = APIRouter()


@router.post(
    "/openended/generate",
    response_model=OpenEndedResponseWrapper,
    status_code=status.HTTP_201_CREATED,
    summary="Generate open-ended questions",
    description="Generate a new set of open-ended questions from selected files with customizable parameters using AI."
)
async def generate_openended_questions(
    openended_data: OpenEndedQuestionCreate = ...,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Generate a new set of open-ended questions from file content using AI.
    
    - **space_id**: UUID of the parent space
    - **title**: Open-ended question set title (required)
    - **fileIds**: List of file UUIDs to generate questions from (required)
    - **questionCount**: Number of questions to generate (default: 10, max: 50)
    - **difficulty**: Question difficulty level (default: "medium")
    - **maxWords**: Maximum words per answer (default: 500, max: 2000)
    - **topics**: Specific topics to focus on (optional)
    
    Returns the generated open-ended question set with prompts and rubrics.
    
    **Example Request:**
    ```json
    {
        "title": "Photosynthesis Essay Questions",
        "fileIds": ["uuid1", "uuid2"],
        "questionCount": 3,
        "difficulty": "medium",
        "maxWords": 500,
        "topics": ["light reactions", "calvin cycle", "chloroplast structure"]
    }
    ```
    """
    openended = OpenEndedService.generate_openended_questions(
        db=db,
        user=current_user,
        openended_data=openended_data
    )
    
    return OpenEndedResponseWrapper(data=openended)


@router.get(
    "/openended/list",
    response_model=OpenEndedListResponse,
    status_code=status.HTTP_200_OK,
    summary="List open-ended question sets",
    description="Get a paginated list of open-ended question sets in a space owned by the current user."
)
async def list_openended_questions(
    space_id: str = Query(..., description="Space UUID"),
    page: int = Query(1, ge=1, description="Page number (1-based)"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    List open-ended question sets in a space for the current user.
    
    - **space_id**: UUID of the parent space
    - **page**: Page number starting from 1
    - **limit**: Number of items per page (1-100)
    
    Returns a paginated list of open-ended question sets with metadata.
    
    **Response includes:**
    - Open-ended question set metadata (id, title, creation date)
    - Pagination information (page, limit, total)
    """
    return OpenEndedService.list_openended_questions(
        db=db,
        user=current_user,
        space_id=space_id,
        page=page,
        limit=limit
    )


@router.get(
    "/openended/{openended_id}",
    response_model=OpenEndedResponseWrapper,
    status_code=status.HTTP_200_OK,
    summary="Get open-ended question set detail",
    description="Retrieve a specific open-ended question set with all prompts and rubrics."
)
async def get_openended_question(
    openended_id: str = Path(..., description="Open-ended question UUID"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get detailed information about a specific open-ended question set.
    
    - **openended_id**: UUID of the open-ended question set to retrieve
    
    Returns complete open-ended question set data including:
    - Open-ended question set metadata (id, title, creation date)
    - All questions with prompts, word limits, and grading rubrics
    - Source file references
    
    **Note:** Only accessible to the owner of the open-ended question set.
    """
    openended = OpenEndedService.get_openended_question(
        db=db,
        user=current_user,
        openended_id=openended_id
    )
    
    return OpenEndedResponseWrapper(data=openended)


@router.post(
    "/openended/{openended_id}/submit",
    status_code=status.HTTP_201_CREATED,
    summary="Submit open-ended answers",
    description="Submit answers for open-ended questions and receive AI-powered grading with detailed feedback."
)
async def submit_openended_answers(
    openended_id: str = Path(..., description="Open-ended question UUID"),
    submission: OpenEndedSubmission = ...,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Submit answers for open-ended questions and get automated AI grading.
    
    - **openended_id**: UUID of the open-ended question set to submit answers for
    - **answers**: List of answers with question IDs and responses
    
    **Grading Process:**
    - Each answer is graded using AI based on the question's rubric
    - Word count validation is performed
    - Detailed feedback is provided for each criterion
    - Overall score and feedback are calculated
    
    **Example Request:**
    ```json
    {
        "answers": [
            {
                "questionId": "q1",
                "answer": "Photosynthesis is a complex biological process that converts light energy into chemical energy..."
            }
        ]
    }
    ```
    
    **Returns:**
    - Individual answer grading with rubric breakdown
    - Word count validation
    - Detailed feedback for each criterion
    - Overall score and feedback
    - Submission timestamp
    """
    result = OpenEndedService.submit_openended_answer(
        db=db,
        user=current_user,
        openended_id=openended_id,
        submission_data=submission
    )
    
    return {"data": result}


@router.get(
    "/openended/{openended_id}/answers",
    response_model=OpenEndedAnswersListResponse,
    status_code=status.HTTP_200_OK,
    summary="Get user's answers and grades",
    description="Retrieve all answers submitted by the current user for a specific open-ended question set."
)
async def get_user_answers(
    openended_id: str = Path(..., description="Open-ended question UUID"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get all answers submitted by the user for a specific open-ended question set.
    
    - **openended_id**: UUID of the open-ended question set
    
    Returns all user submissions including:
    - Submitted answers with word counts
    - AI grading results with rubric breakdown
    - Detailed feedback for each criterion
    - Submission timestamps
    
    **Note:** Only accessible to the owner of the open-ended question set.
    """
    answers = OpenEndedService.get_user_answers(
        db=db,
        user=current_user,
        openended_id=openended_id
    )
    
    return OpenEndedAnswersListResponse(data=answers)


@router.delete(
    "/openended/{openended_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete open-ended question set",
    description="Delete an open-ended question set and all associated answers permanently."
)
async def delete_openended_question(
    openended_id: str = Path(..., description="Open-ended question UUID"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete an open-ended question set and all its answers.
    
    - **openended_id**: UUID of the open-ended question set to delete
    
    **Warning:** This operation is permanent and will:
    - Delete the open-ended question set and all questions
    - Delete all user answers and grades for this set
    - Remove all associated data
    
    **Note:** Only accessible to the owner of the open-ended question set.
    """
    OpenEndedService.delete_openended_question(
        db=db,
        user=current_user,
        openended_id=openended_id
    )
    
    return Response(status_code=status.HTTP_204_NO_CONTENT) 