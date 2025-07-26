"""
Quiz service for quiz management operations.

Handles:
- Quiz generation with mock AI integration
- Quiz listing with pagination
- Quiz retrieval with ownership verification
- Quiz submission and grading with mock AI
- Quiz deletion with cascading operations
"""
import uuid
from typing import Optional, List, Tuple, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc
from fastapi import HTTPException, status
from datetime import datetime

from app.models.quiz import Quiz, QuizSubmission
from app.models.space import Space, SpaceType
from app.models.file import File
from app.models.folder import Folder
from app.models.user import User
from app.schemas.quiz import (
    QuizCreate, 
    QuizResponse, 
    QuizListResponse,
    QuizSubmission as QuizSubmissionSchema,
    QuizSubmissionResponse,
    PaginationMeta,
    QuestionType,
    DifficultyLevel
)


class MockAIService:
    """Mock AI service for quiz generation and grading (Backend Developer responsibility)."""
    
    @staticmethod
    def generate_quiz_questions(file_contents: List[str], params: QuizCreate) -> List[Dict[str, Any]]:
        """
        Mock AI service to generate quiz questions from file content.
        
        In production, this would call OpenAI API for question generation.
        For now, returns mock questions based on parameters.
        """
        questions = []
        
        for i in range(params.question_count):
            question_type = params.question_types[i % len(params.question_types)]
            
            if question_type == QuestionType.mcq:
                question = {
                    "id": f"q{i+1}",
                    "type": "mcq",
                    "prompt": f"Mock MCQ question {i+1} about {params.title}?",
                    "choices": [
                        f"Option A for question {i+1}",
                        f"Option B for question {i+1}",
                        f"Option C for question {i+1}",
                        f"Option D for question {i+1}"
                    ],
                    "answer": "A"
                }
            elif question_type == QuestionType.tf:
                question = {
                    "id": f"q{i+1}",
                    "type": "tf",
                    "prompt": f"Mock True/False question {i+1} about {params.title}.",
                    "answer": True if i % 2 == 0 else False
                }
            else:  # short_answer
                question = {
                    "id": f"q{i+1}",
                    "type": "short_answer",
                    "prompt": f"Mock short answer question {i+1}: Explain the concept related to {params.title}.",
                    "answer": f"Sample answer for question {i+1}"
                }
            
            questions.append(question)
        
        return questions
    
    @staticmethod
    def grade_quiz_submission(quiz: Quiz, submission_data: QuizSubmissionSchema) -> Tuple[float, List[Dict[str, Any]]]:
        """
        Mock AI service to grade quiz submissions.
        
        In production, this would use AI for grading short answers.
        For now, implements basic automatic grading.
        """
        score = 0.0
        feedback = []
        total_questions = len(quiz.questions)
        
        # Create a map of user answers
        user_answers = {answer.question_id: answer.answer for answer in submission_data.answers}
        
        for question in quiz.questions:
            question_id = question["id"]
            correct_answer = question["answer"]
            user_answer = user_answers.get(question_id)
            
            feedback_item = {
                "questionId": question_id,
                "userAnswer": user_answer,
                "correctAnswer": correct_answer,
                "isCorrect": False,
                "feedback": ""
            }
            
            if user_answer is None:
                feedback_item["feedback"] = "No answer provided"
            elif question["type"] in ["mcq", "tf"]:
                # Automatic grading for MCQ and T/F
                if str(user_answer).upper() == str(correct_answer).upper():
                    score += 1.0
                    feedback_item["isCorrect"] = True
                    feedback_item["feedback"] = "Correct!"
                else:
                    feedback_item["feedback"] = f"Incorrect. The correct answer is {correct_answer}"
            else:
                # Mock AI grading for short answers
                # In production, this would use OpenAI API
                if isinstance(user_answer, str) and len(user_answer.strip()) > 10:
                    # Give partial credit for substantial answers
                    score += 0.7
                    feedback_item["isCorrect"] = True
                    feedback_item["feedback"] = "Good answer! (Mock AI grading)"
                else:
                    feedback_item["feedback"] = "Answer too short or missing details"
            
            feedback.append(feedback_item)
        
        return score, feedback


class QuizService:
    """Service class for quiz management operations."""
    
    @staticmethod
    def generate_quiz(
        db: Session, 
        user: User, 
        space_id: str,
        quiz_data: QuizCreate
    ) -> QuizResponse:
        """
        Generate a new quiz from file content using AI.
        
        Args:
            db: Database session
            user: Current authenticated user
            space_id: Parent space UUID
            quiz_data: Quiz creation parameters
            
        Returns:
            QuizResponse with generated quiz
            
        Raises:
            HTTPException: If space not found, user doesn't own it, or files are invalid
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
        
        # Verify space exists and user owns it
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
        
        # Check folder ownership through space relationship
        folder = db.query(Folder).filter(Folder.id == space.folder_id).first()
        if not folder or folder.owner_id != user.id:
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
        file_contents = []
        validated_file_ids = []
        
        for file_id_str in quiz_data.file_ids:
            try:
                file_id = uuid.UUID(file_id_str)
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail={
                        "error": {
                            "code": "INVALID_UUID",
                            "message": f"Invalid file ID format: {file_id_str}",
                            "details": {"file_id": file_id_str}
                        }
                    }
                )
            
            # Check if file exists and user owns it
            file = db.query(File).filter(File.id == file_id).first()
            if not file:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail={
                        "error": {
                            "code": "FILE_NOT_FOUND",
                            "message": f"File not found: {file_id_str}",
                            "details": {"file_id": file_id_str}
                        }
                    }
                )
            
            # Verify file belongs to user through folder ownership
            file_folder = db.query(Folder).filter(Folder.id == file.folder_id).first()
            if not file_folder or file_folder.owner_id != user.id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail={
                        "error": {
                            "code": "FORBIDDEN",
                            "message": f"You do not have permission to access file: {file_id_str}",
                            "details": {"file_id": file_id_str}
                        }
                    }
                )
            
            file_contents.append(file.text_content or "")
            validated_file_ids.append(file_id_str)
        
        # Generate quiz questions using mock AI service
        questions = MockAIService.generate_quiz_questions(file_contents, quiz_data)
        
        # Create quiz record
        quiz = Quiz(
            id=uuid.uuid4(),
            space_id=space_uuid,
            title=quiz_data.title,
            questions=questions,
            file_ids=validated_file_ids,
            created_at=datetime.utcnow()
        )
        
        db.add(quiz)
        db.commit()
        db.refresh(quiz)
        
        return QuizResponse(
            id=str(quiz.id),
            space_id=str(quiz.space_id),
            title=quiz.title,
            questions=quiz.questions,
            created_at=quiz.created_at
        )
    
    @staticmethod
    def list_quizzes(
        db: Session, 
        user: User, 
        space_id: str,
        page: int = 1, 
        limit: int = 20
    ) -> QuizListResponse:
        """
        List quizzes in a space for a user with pagination.
        
        Args:
            db: Database session
            user: Current authenticated user
            space_id: Parent space UUID
            page: Page number (1-based)
            limit: Items per page
            
        Returns:
            QuizListResponse with quizzes and pagination metadata
            
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
        
        # Verify space exists and user owns it
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
        
        # Check folder ownership through space relationship
        folder = db.query(Folder).filter(Folder.id == space.folder_id).first()
        if not folder or folder.owner_id != user.id:
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
        
        # Calculate pagination offset
        offset = (page - 1) * limit
        
        # Query quizzes with pagination
        quizzes_query = db.query(Quiz).filter(
            Quiz.space_id == space_uuid
        ).order_by(desc(Quiz.created_at))
        
        total = quizzes_query.count()
        quizzes = quizzes_query.offset(offset).limit(limit).all()
        
        # Convert to response format
        quiz_responses = []
        for quiz in quizzes:
            quiz_responses.append(QuizResponse(
                id=str(quiz.id),
                space_id=str(quiz.space_id),
                title=quiz.title,
                questions=quiz.questions,
                created_at=quiz.created_at
            ))
        
        return QuizListResponse(
            data=quiz_responses,
            meta=PaginationMeta(
                page=page,
                limit=limit,
                total=total
            )
        )
    
    @staticmethod
    def get_quiz(
        db: Session, 
        user: User, 
        quiz_id: str
    ) -> QuizResponse:
        """
        Get a specific quiz by ID.
        
        Args:
            db: Database session
            user: Current authenticated user
            quiz_id: Quiz UUID
            
        Returns:
            QuizResponse with quiz data
            
        Raises:
            HTTPException: If quiz not found or user doesn't own it
        """
        # Validate quiz_id is a valid UUID
        try:
            quiz_uuid = uuid.UUID(quiz_id)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail={
                    "error": {
                        "code": "INVALID_UUID",
                        "message": "Invalid quiz ID format",
                        "details": {"quiz_id": quiz_id}
                    }
                }
            )
        
        # Fetch quiz
        quiz = db.query(Quiz).filter(Quiz.id == quiz_uuid).first()
        
        if not quiz:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "error": {
                        "code": "QUIZ_NOT_FOUND",
                        "message": "Quiz not found",
                        "details": {"quiz_id": quiz_id}
                    }
                }
            )
        
        # Check ownership through space -> folder relationship
        space = db.query(Space).filter(Space.id == quiz.space_id).first()
        if not space:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "error": {
                        "code": "SPACE_NOT_FOUND",
                        "message": "Parent space not found",
                        "details": None
                    }
                }
            )
        
        folder = db.query(Folder).filter(Folder.id == space.folder_id).first()
        if not folder or folder.owner_id != user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "error": {
                        "code": "FORBIDDEN",
                        "message": "You do not have permission to access this quiz",
                        "details": None
                    }
                }
            )
        
        return QuizResponse(
            id=str(quiz.id),
            space_id=str(quiz.space_id),
            title=quiz.title,
            questions=quiz.questions,
            created_at=quiz.created_at
        )
    
    @staticmethod
    def submit_quiz(
        db: Session, 
        user: User, 
        quiz_id: str,
        submission_data: QuizSubmissionSchema
    ) -> QuizSubmissionResponse:
        """
        Submit quiz answers and get grading results.
        
        Args:
            db: Database session
            user: Current authenticated user
            quiz_id: Quiz UUID
            submission_data: User's answers
            
        Returns:
            QuizSubmissionResponse with score and feedback
            
        Raises:
            HTTPException: If quiz not found or user doesn't own it
        """
        # Validate quiz_id is a valid UUID
        try:
            quiz_uuid = uuid.UUID(quiz_id)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail={
                    "error": {
                        "code": "INVALID_UUID",
                        "message": "Invalid quiz ID format",
                        "details": {"quiz_id": quiz_id}
                    }
                }
            )
        
        # Fetch quiz and verify ownership
        quiz = db.query(Quiz).filter(Quiz.id == quiz_uuid).first()
        
        if not quiz:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "error": {
                        "code": "QUIZ_NOT_FOUND",
                        "message": "Quiz not found",
                        "details": {"quiz_id": quiz_id}
                    }
                }
            )
        
        # Check ownership through space -> folder relationship
        space = db.query(Space).filter(Space.id == quiz.space_id).first()
        if not space:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "error": {
                        "code": "SPACE_NOT_FOUND",
                        "message": "Parent space not found",
                        "details": None
                    }
                }
            )
        
        folder = db.query(Folder).filter(Folder.id == space.folder_id).first()
        if not folder or folder.owner_id != user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "error": {
                        "code": "FORBIDDEN",
                        "message": "You do not have permission to submit answers for this quiz",
                        "details": None
                    }
                }
            )
        
        # Grade the submission using mock AI service
        score, feedback = MockAIService.grade_quiz_submission(quiz, submission_data)
        
        # Save submission to database
        submission = QuizSubmission(
            id=uuid.uuid4(),
            quiz_id=quiz_uuid,
            user_id=user.id,
            answers=[answer.model_dump() for answer in submission_data.answers],
            score=score,
            feedback=feedback,
            submitted_at=datetime.utcnow()
        )
        
        db.add(submission)
        db.commit()
        db.refresh(submission)
        
        return QuizSubmissionResponse(
            score=score,
            total_questions=len(quiz.questions),
            feedback=feedback,
            submitted_at=submission.submitted_at
        )
    
    @staticmethod
    def delete_quiz(
        db: Session, 
        user: User, 
        quiz_id: str
    ) -> None:
        """
        Delete a quiz and all its submissions.
        
        Args:
            db: Database session
            user: Current authenticated user
            quiz_id: Quiz UUID
            
        Raises:
            HTTPException: If quiz not found or user doesn't own it
        """
        # Validate quiz_id is a valid UUID
        try:
            quiz_uuid = uuid.UUID(quiz_id)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail={
                    "error": {
                        "code": "INVALID_UUID",
                        "message": "Invalid quiz ID format",
                        "details": {"quiz_id": quiz_id}
                    }
                }
            )
        
        # Fetch quiz
        quiz = db.query(Quiz).filter(Quiz.id == quiz_uuid).first()
        
        if not quiz:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "error": {
                        "code": "QUIZ_NOT_FOUND",
                        "message": "Quiz not found",
                        "details": {"quiz_id": quiz_id}
                    }
                }
            )
        
        # Check ownership through space -> folder relationship
        space = db.query(Space).filter(Space.id == quiz.space_id).first()
        if not space:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "error": {
                        "code": "SPACE_NOT_FOUND",
                        "message": "Parent space not found",
                        "details": None
                    }
                }
            )
        
        folder = db.query(Folder).filter(Folder.id == space.folder_id).first()
        if not folder or folder.owner_id != user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "error": {
                        "code": "FORBIDDEN",
                        "message": "You do not have permission to delete this quiz",
                        "details": None
                    }
                }
            )
        
        # Delete quiz (submissions will be deleted automatically due to CASCADE)
        db.delete(quiz)
        db.commit() 