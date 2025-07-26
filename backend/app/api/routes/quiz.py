"""
Quiz routes for the EdutechHackathon API.

Endpoints:
- POST /spaces/{spaceId}/quizzes - Generate quiz from selected files + params
- GET /spaces/{spaceId}/quizzes - List quizzes
- GET /quizzes/{id} - Quiz detail
- POST /quizzes/{id}/submit - Grade answers
- DELETE /quizzes/{id} - Delete quiz
"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query, Path, Response
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.schemas.quiz import (
    QuizCreate,
    QuizListResponse,
    QuizResponseWrapper,
    QuizSubmission,
    QuizSubmissionResponseWrapper
)
from app.services.quiz import QuizService


router = APIRouter()


@router.post(
    "/spaces/{space_id}/quizzes",
    response_model=QuizResponseWrapper,
    status_code=status.HTTP_201_CREATED,
    summary="Generate quiz",
    description="Generate a new quiz from selected files with customizable parameters using AI."
)
async def generate_quiz(
    space_id: str = Path(..., description="Space UUID"),
    quiz_data: QuizCreate = ...,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Generate a new quiz from file content using AI.
    
    - **space_id**: UUID of the parent space
    - **title**: Quiz title (required)
    - **fileIds**: List of file UUIDs to generate quiz from (required)
    - **questionCount**: Number of questions to generate (default: 10, max: 50)
    - **questionTypes**: Types of questions to include (default: ["mcq", "tf"])
    - **difficulty**: Quiz difficulty level (default: "medium")
    
    Returns the generated quiz with questions and metadata.
    
    **Example Request:**
    ```json
    {
        "title": "Chapter 3 Quiz",
        "fileIds": ["uuid1", "uuid2"],
        "questionCount": 10,
        "questionTypes": ["mcq", "tf"],
        "difficulty": "medium"
    }
    ```
    """
    quiz = QuizService.generate_quiz(
        db=db,
        user=current_user,
        space_id=space_id,
        quiz_data=quiz_data
    )
    
    return QuizResponseWrapper(data=quiz)


@router.get(
    "/spaces/{space_id}/quizzes",
    response_model=QuizListResponse,
    status_code=status.HTTP_200_OK,
    summary="List quizzes",
    description="Get a paginated list of quizzes in a space owned by the current user."
)
async def list_quizzes(
    space_id: str = Path(..., description="Space UUID"),
    page: int = Query(1, ge=1, description="Page number (1-based)"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    List quizzes in a space for the current user.
    
    - **space_id**: UUID of the parent space
    - **page**: Page number starting from 1
    - **limit**: Number of items per page (1-100)
    
    Returns a paginated list of quizzes with metadata.
    
    **Response includes:**
    - Quiz metadata (id, title, creation date)
    - Pagination information (page, limit, total)
    """
    return QuizService.list_quizzes(
        db=db,
        user=current_user,
        space_id=space_id,
        page=page,
        limit=limit
    )


@router.get(
    "/quizzes/{quiz_id}",
    response_model=QuizResponseWrapper,
    status_code=status.HTTP_200_OK,
    summary="Get quiz detail",
    description="Retrieve a specific quiz with all questions and answers."
)
async def get_quiz(
    quiz_id: str = Path(..., description="Quiz UUID"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get detailed information about a specific quiz.
    
    - **quiz_id**: UUID of the quiz to retrieve
    
    Returns complete quiz data including:
    - Quiz metadata (id, title, creation date)
    - All questions with prompts, choices, and correct answers
    - Source file references
    
    **Note:** Only accessible to the owner of the quiz.
    """
    quiz = QuizService.get_quiz(
        db=db,
        user=current_user,
        quiz_id=quiz_id
    )
    
    return QuizResponseWrapper(data=quiz)


@router.post(
    "/quizzes/{quiz_id}/submit",
    response_model=QuizSubmissionResponseWrapper,
    status_code=status.HTTP_201_CREATED,
    summary="Submit quiz answers",
    description="Submit answers for a quiz and receive grading results with AI-powered feedback."
)
async def submit_quiz_answers(
    quiz_id: str = Path(..., description="Quiz UUID"),
    submission: QuizSubmission = ...,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Submit answers for a quiz and get automated grading.
    
    - **quiz_id**: UUID of the quiz to submit answers for
    - **answers**: List of answers with question IDs and responses
    
    **Grading Process:**
    - Multiple choice and true/false questions are graded automatically
    - Short answer questions are graded using AI (mock implementation)
    - Partial credit may be awarded for short answers
    - Detailed feedback is provided for each question
    
    **Example Request:**
    ```json
    {
        "answers": [
            {"questionId": "q1", "answer": "A"},
            {"questionId": "q2", "answer": true},
            {"questionId": "q3", "answer": "Photosynthesis converts light energy..."}
        ]
    }
    ```
    
    **Returns:**
    - Total score and percentage
    - Question-by-question feedback
    - Submission timestamp
    """
    result = QuizService.submit_quiz(
        db=db,
        user=current_user,
        quiz_id=quiz_id,
        submission_data=submission
    )
    
    return QuizSubmissionResponseWrapper(data=result)


@router.delete(
    "/quizzes/{quiz_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete quiz",
    description="Delete a quiz and all associated submissions permanently."
)
async def delete_quiz(
    quiz_id: str = Path(..., description="Quiz UUID"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete a quiz and all its submissions.
    
    - **quiz_id**: UUID of the quiz to delete
    
    **Warning:** This operation is permanent and will:
    - Delete the quiz and all questions
    - Delete all user submissions for this quiz
    - Remove all associated data
    
    **Note:** Only accessible to the owner of the quiz.
    """
    QuizService.delete_quiz(
        db=db,
        user=current_user,
        quiz_id=quiz_id
    )
    
    return Response(status_code=status.HTTP_204_NO_CONTENT) 