"""
Open-ended Question service for open-ended question management operations.

Handles:
- Open-ended question generation with mock AI integration
- Open-ended question listing with pagination
- Open-ended question retrieval with ownership verification
- Open-ended answer submission and AI grading with mock implementation
- Open-ended question deletion with cascading operations
"""
import uuid
import re
from typing import Optional, List, Tuple, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc
from fastapi import HTTPException, status
from datetime import datetime

from app.models.openended import OpenEndedQuestion, OpenEndedAnswer
from app.models.space import Space, SpaceType
from app.models.file import File
from app.models.folder import Folder
from app.models.user import User
from app.schemas.openended import OpenEndedSubmission as OpenEndedSubmissionSchema
from app.schemas.openended import (
    OpenEndedQuestionCreate, 
    OpenEndedQuestionResponse, 
    OpenEndedListResponse,
    OpenEndedSubmission as OpenEndedSubmissionSchema,
    OpenEndedAnswerResponse,
    PaginationMeta,
    DifficultyLevel
)


class MockAIService:
    """Mock AI service for open-ended question generation and grading (Backend Developer responsibility)."""
    
    @staticmethod
    def generate_openended_questions(file_contents: List[str], params: OpenEndedQuestionCreate) -> List[Dict[str, Any]]:
        """
        Mock AI service to generate open-ended questions from file content.
        
        In production, this would call OpenAI API for question generation.
        For now, returns mock questions based on parameters.
        """
        questions = []
        
        for i in range(params.question_count):
            question = {
                "id": f"q{i+1}",
                "prompt": f"Mock open-ended question {i+1} about {params.title}. " + 
                         f"Please provide a detailed explanation in {params.max_words} words or less.",
                "maxWords": params.max_words,
                "rubric": {
                    "criteria": [
                        {
                            "name": "Content understanding",
                            "weight": 0.4,
                            "description": "Demonstrates clear understanding of the topic"
                        },
                        {
                            "name": "Explanation quality",
                            "weight": 0.3,
                            "description": "Provides clear and coherent explanation"
                        },
                        {
                            "name": "Use of examples",
                            "weight": 0.2,
                            "description": "Includes relevant examples and details"
                        },
                        {
                            "name": "Writing quality",
                            "weight": 0.1,
                            "description": "Well-written with good structure"
                        }
                    ]
                }
            }
            
            questions.append(question)
        
        return questions
    
    @staticmethod
    def grade_openended_answer(answer: str, rubric: Dict[str, Any], max_words: int) -> Tuple[float, Dict[str, Any]]:
        """
        Mock AI service to grade open-ended answers.
        
        In production, this would use AI for grading based on the rubric.
        For now, implements basic grading logic.
        """
        # Calculate word count
        word_count = len(re.findall(r'\b\w+\b', answer))
        
        # Check if answer exceeds word limit
        if word_count > max_words:
            return 0.0, {
                "totalScore": 0,
                "maxScore": 100,
                "breakdown": [
                    {
                        "criterion": "Word limit",
                        "score": 0,
                        "maxScore": 100,
                        "feedback": f"Answer exceeds maximum word limit of {max_words} words (submitted: {word_count} words)"
                    }
                ],
                "overallFeedback": f"Your answer exceeds the maximum word limit of {max_words} words. Please revise and resubmit.",
                "gradedAt": datetime.utcnow().isoformat()
            }
        
        # Mock grading based on answer length and content
        base_score = min(85, (word_count / max_words) * 100)  # Base score from length
        
        # Add some variation based on content
        content_bonus = 0
        if "explain" in answer.lower() or "describe" in answer.lower():
            content_bonus += 5
        if len(answer) > 100:
            content_bonus += 5
        if "example" in answer.lower() or "instance" in answer.lower():
            content_bonus += 5
        
        final_score = min(100, base_score + content_bonus)
        
        # Create breakdown based on rubric criteria
        breakdown = []
        criteria = rubric.get("criteria", [])
        
        for criterion in criteria:
            criterion_score = (final_score * criterion["weight"])
            breakdown.append({
                "criterion": criterion["name"],
                "score": round(criterion_score, 1),
                "maxScore": round(100 * criterion["weight"], 1),
                "feedback": f"Good work on {criterion['name'].lower()}. " + 
                           f"Score: {round(criterion_score, 1)}/{round(100 * criterion['weight'], 1)}"
            })
        
        overall_feedback = f"Good answer with {word_count} words. " + \
                          f"Your response demonstrates understanding of the topic. " + \
                          f"Consider adding more specific examples to improve your score."
        
        grade_result = {
            "totalScore": round(final_score, 1),
            "maxScore": 100,
            "breakdown": breakdown,
            "overallFeedback": overall_feedback,
            "gradedAt": datetime.utcnow().isoformat()
        }
        
        return final_score, grade_result


class OpenEndedService:
    """Service class for open-ended question operations."""
    
    @staticmethod
    def generate_openended_questions(
        db: Session, 
        user: User, 
        openended_data: OpenEndedQuestionCreate
    ) -> OpenEndedQuestionResponse:
        """Generate open-ended questions from file content using AI."""
        try:
            space_uuid = uuid.UUID(openended_data.space_id)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail={
                    "error": {
                        "code": "INVALID_UUID",
                        "message": "Invalid space ID format",
                        "details": {"space_id": openended_data.space_id}
                    }
                }
            )
        
        # Verify space exists and is of correct type
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
                        "details": {"space_id": openended_data.space_id}
                    }
                }
            )
        
        # Verify user owns the space's parent folder
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
                        "message": "You do not have permission to access this space",
                        "details": None
                    }
                }
            )
        
        # Validate file IDs and verify ownership
        file_contents = []
        for file_id in openended_data.file_ids:
            try:
                file_uuid = uuid.UUID(file_id)
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
            
            # Verify user owns the file through folder ownership
            file_folder = db.query(Folder).filter(
                and_(
                    Folder.id == file.folder_id,
                    Folder.owner_id == user.id,
                    Folder.deleted_at.is_(None)
                )
            ).first()
            
            if not file_folder:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail={
                        "error": {
                            "code": "FILE_ACCESS_DENIED",
                            "message": f"You do not have permission to access file: {file_id}",
                            "details": {"file_id": file_id}
                        }
                    }
                )
            
            # Get file content
            if file.text_content:
                file_contents.append(file.text_content)
            else:
                file_contents.append(f"Content from {file.name}")
        
        # Generate questions using mock AI service
        questions = MockAIService.generate_openended_questions(file_contents, openended_data)
        
        # Create and save the open-ended question
        openended_question = OpenEndedQuestion(
            id=uuid.uuid4(),
            space_id=space_uuid,
            title=openended_data.title,
            questions=questions,
            file_ids=openended_data.file_ids,
            created_at=datetime.utcnow()
        )
        
        db.add(openended_question)
        db.commit()
        db.refresh(openended_question)
        
        return OpenEndedQuestionResponse(
            id=openended_question.id,
            space_id=openended_question.space_id,
            title=openended_question.title,
            questions=openended_question.questions,
            created_at=openended_question.created_at
        )
    
    @staticmethod
    def list_openended_questions(
        db: Session,
        user: User,
        space_id: str,
        page: int = 1,
        limit: int = 20
    ) -> OpenEndedListResponse:
        """List open-ended questions in a space with pagination."""
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
        
        # Verify user has access to the space
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
                        "message": "You do not have permission to access this space",
                        "details": None
                    }
                }
            )
        
        # Query open-ended questions with pagination
        offset = (page - 1) * limit
        
        questions_query = db.query(OpenEndedQuestion).filter(
            and_(
                OpenEndedQuestion.space_id == space_uuid,
                OpenEndedQuestion.deleted_at.is_(None)
            )
        ).order_by(desc(OpenEndedQuestion.created_at))
        
        total = questions_query.count()
        questions = questions_query.offset(offset).limit(limit).all()
        
        # Convert to response format
        question_responses = [
            OpenEndedQuestionResponse(
                id=q.id,
                space_id=q.space_id,
                title=q.title,
                questions=q.questions,
                created_at=q.created_at
            ) for q in questions
        ]
        
        return OpenEndedListResponse(
            data=question_responses,
            meta=PaginationMeta(
                page=page,
                limit=limit,
                total=total
            )
        )
    
    @staticmethod
    def get_openended_question(
        db: Session,
        user: User,
        openended_id: str
    ) -> OpenEndedQuestionResponse:
        """Get a specific open-ended question by ID."""
        try:
            question_uuid = uuid.UUID(openended_id)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail={
                    "error": {
                        "code": "INVALID_UUID",
                        "message": "Invalid question ID format",
                        "details": {"openended_id": openended_id}
                    }
                }
            )
        
        question = db.query(OpenEndedQuestion).filter(
            and_(
                OpenEndedQuestion.id == question_uuid,
                OpenEndedQuestion.deleted_at.is_(None)
            )
        ).first()
        
        if not question:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "error": {
                        "code": "OPENENDED_QUESTION_NOT_FOUND",
                        "message": "Open-ended question not found",
                        "details": {"openended_id": openended_id}
                    }
                }
            )
        
        # Verify user has access through space ownership
        space = db.query(Space).filter(
            and_(
                Space.id == question.space_id,
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
                        "details": {"space_id": str(question.space_id)}
                    }
                }
            )
        
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
                        "message": "You do not have permission to access this question",
                        "details": None
                    }
                }
            )
        
        return OpenEndedQuestionResponse(
            id=question.id,
            space_id=question.space_id,
            title=question.title,
            questions=question.questions,
            created_at=question.created_at
        )
    
    @staticmethod
    def submit_openended_answer(
        db: Session,
        user: User,
        openended_id: str,
        submission_data: OpenEndedSubmissionSchema
    ) -> Dict[str, Any]:
        """Submit answers for open-ended questions and get AI grading."""
        try:
            question_uuid = uuid.UUID(openended_id)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail={
                    "error": {
                        "code": "INVALID_UUID",
                        "message": "Invalid question ID format",
                        "details": {"openended_id": openended_id}
                    }
                }
            )
        
        # Get the question and verify access
        question = db.query(OpenEndedQuestion).filter(
            and_(
                OpenEndedQuestion.id == question_uuid,
                OpenEndedQuestion.deleted_at.is_(None)
            )
        ).first()
        
        if not question:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "error": {
                        "code": "OPENENDED_QUESTION_NOT_FOUND",
                        "message": "Open-ended question not found",
                        "details": {"openended_id": openended_id}
                    }
                }
            )
        
        # Verify user has access through space ownership
        space = db.query(Space).filter(
            and_(
                Space.id == question.space_id,
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
                        "details": {"space_id": str(question.space_id)}
                    }
                }
            )
        
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
                        "message": "You do not have permission to submit answers to this question",
                        "details": None
                    }
                }
            )
        
        # Process each answer
        feedback_list = []
        total_score = 0
        max_score = 0
        
        for answer_data in submission_data.answers:
            # Find the corresponding question
            question_found = False
            for q in question.questions:
                if q["id"] == answer_data.question_id:
                    question_found = True
                    # Grade the answer using mock AI service
                    score, grade_result = MockAIService.grade_openended_answer(
                        answer_data.answer,
                        q["rubric"],
                        q["maxWords"]
                    )
                    
                    # Create answer record
                    answer = OpenEndedAnswer(
                        id=uuid.uuid4(),
                        open_ended_question_id=question_uuid,
                        user_id=user.id,
                        question_id=answer_data.question_id,
                        answer=answer_data.answer,
                        word_count=len(re.findall(r'\b\w+\b', answer_data.answer)),
                        grade=grade_result,
                        submitted_at=datetime.utcnow()
                    )
                    
                    db.add(answer)
                    
                    # Add to feedback list
                    feedback_list.append({
                        "questionId": answer_data.question_id,
                        "userAnswer": answer_data.answer,
                        "correctAnswer": "Mock correct answer",  # In real implementation, this would be AI-generated
                        "isCorrect": score > 0.5,  # Simple threshold
                        "feedback": grade_result.get("overallFeedback", "Good answer")
                    })
                    
                    total_score += score * 100  # Convert to percentage
                    max_score += 100
                    break
            
            if not question_found:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail={
                        "error": {
                            "code": "INVALID_QUESTION_ID",
                            "message": f"Question ID not found: {answer_data.question_id}",
                            "details": {"question_id": answer_data.question_id}
                        }
                    }
                )
        
        db.commit()
        
        # Return response in the format expected by tests
        return {
            "score": total_score,
            "totalQuestions": len(question.questions),
            "feedback": feedback_list,
            "submittedAt": datetime.utcnow().isoformat()
        }
    
    @staticmethod
    def get_user_answers(
        db: Session,
        user: User,
        openended_id: str
    ) -> List[OpenEndedAnswerResponse]:
        """Get all answers submitted by the user for a specific question set."""
        try:
            question_uuid = uuid.UUID(openended_id)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail={
                    "error": {
                        "code": "INVALID_UUID",
                        "message": "Invalid question ID format",
                        "details": {"openended_id": openended_id}
                    }
                }
            )
        
        # Verify question exists and user has access
        question = db.query(OpenEndedQuestion).filter(
            and_(
                OpenEndedQuestion.id == question_uuid,
                OpenEndedQuestion.deleted_at.is_(None)
            )
        ).first()
        
        if not question:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "error": {
                        "code": "OPENENDED_QUESTION_NOT_FOUND",
                        "message": "Open-ended question not found",
                        "details": {"openended_id": openended_id}
                    }
                }
            )
        
        # Verify user has access through space ownership
        space = db.query(Space).filter(
            and_(
                Space.id == question.space_id,
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
                        "details": {"space_id": str(question.space_id)}
                    }
                }
            )
        
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
                        "message": "You do not have permission to access this question",
                        "details": None
                    }
                }
            )
        
        # Get user's answers
        answers = db.query(OpenEndedAnswer).filter(
            and_(
                OpenEndedAnswer.open_ended_question_id == question_uuid,
                OpenEndedAnswer.user_id == user.id
            )
        ).order_by(desc(OpenEndedAnswer.submitted_at)).all()
        
        if not answers:
            return [] # Return empty list instead of 404
        
        return [
            OpenEndedAnswerResponse(
                id=answer.id,
                question_id=answer.question_id,
                user_id=answer.user_id,
                answer=answer.answer,
                word_count=answer.word_count,
                grade=answer.grade,
                submitted_at=answer.submitted_at
            ) for answer in answers
        ]
    
    @staticmethod
    def delete_openended_question(
        db: Session,
        user: User,
        openended_id: str
    ) -> None:
        """Delete an open-ended question set and all associated answers."""
        try:
            question_uuid = uuid.UUID(openended_id)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail={
                    "error": {
                        "code": "INVALID_UUID",
                        "message": "Invalid question ID format",
                        "details": {"openended_id": openended_id}
                    }
                }
            )
        
        # Get the question and verify access
        question = db.query(OpenEndedQuestion).filter(
            and_(
                OpenEndedQuestion.id == question_uuid,
                OpenEndedQuestion.deleted_at.is_(None)
            )
        ).first()
        
        if not question:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "error": {
                        "code": "OPENENDED_QUESTION_NOT_FOUND",
                        "message": "Open-ended question not found",
                        "details": {"openended_id": openended_id}
                    }
                }
            )
        
        # Verify user has access through space ownership
        space = db.query(Space).filter(
            and_(
                Space.id == question.space_id,
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
                        "details": {"space_id": str(question.space_id)}
                    }
                }
            )
        
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
                        "message": "You do not have permission to delete this question",
                        "details": None
                    }
                }
            )
        
        # Soft delete the question
        question.deleted_at = datetime.utcnow()
        
        # Soft delete all associated answers
        answers = db.query(OpenEndedAnswer).filter(
            OpenEndedAnswer.open_ended_question_id == question_uuid
        ).all()
        
        for answer in answers:
            answer.deleted_at = datetime.utcnow()
        
        db.commit() 