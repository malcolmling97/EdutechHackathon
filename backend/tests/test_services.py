"""
Tests for service layer functions in the EdutechHackathon backend.

Tests business logic and service functions:
- Authentication services
- File processing services
- Content generation services
- Data validation and transformation
- Error handling in services
"""
import pytest
import uuid
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock
from sqlalchemy.orm import Session

from app.services.auth import AuthService
from app.services.file import FileService
from app.services.folder import FolderService
from app.services.space import SpaceService
from app.services.chat import ChatService
from app.services.quiz import QuizService
from app.services.note import NotesService
from app.services.flashcard import FlashcardService
from app.services.openended import OpenEndedService
from app.models.user import User
from app.models.folder import Folder
from app.models.space import Space, SpaceType
from app.models.file import File
from app.models.chat_message import ChatMessage
from app.models.quiz import Quiz, QuizSubmission
from app.models.note import Note
from app.models.flashcard import Flashcard
from app.models.openended import OpenEndedQuestion, OpenEndedAnswer
from app.core.security import get_password_hash, create_access_token
from app.schemas.space import SpaceCreate, SpaceUpdate
from app.schemas.chat import MessageRequest
from app.schemas.quiz import QuizCreate, QuizSubmission as QuizSubmissionSchema
from app.schemas.note import NotesCreate, NotesUpdate
from app.schemas.flashcard import FlashcardCreate
from app.schemas.openended import OpenEndedQuestionCreate, OpenEndedSubmission


class TestAuthService:
    """Test authentication service functions."""
    
    def test_register_user(self, db_session: Session):
        """Test user registration service."""
        from app.schemas.auth import UserRegistration
        
        user_data = UserRegistration(
            email="test@example.com",
            password="testpassword123",
            name="Test User"
        )
        
        response = AuthService.register_user(db_session, user_data)
        
        assert response.user.email == user_data.email
        assert response.user.name == user_data.name
        assert response.token is not None
        assert response.user.id is not None
    
    def test_login_user_success(self, db_session: Session):
        """Test successful user login."""
        from app.schemas.auth import UserLogin
        
        # Create user first
        password = "testpassword123"
        hashed_password = get_password_hash(password)
        user = User(
            email="test@example.com",
            password_hash=hashed_password,
            name="Test User"
        )
        db_session.add(user)
        db_session.commit()
        
        # Login
        login_data = UserLogin(email="test@example.com", password=password)
        response = AuthService.login_user(db_session, login_data)
        
        assert response.user.email == "test@example.com"
        assert response.token is not None
    
    def test_login_user_invalid_password(self, db_session: Session):
        """Test user login with invalid password."""
        from app.schemas.auth import UserLogin
        from fastapi import HTTPException
        
        # Create user
        password = "testpassword123"
        hashed_password = get_password_hash(password)
        user = User(
            email="test@example.com",
            password_hash=hashed_password,
            name="Test User"
        )
        db_session.add(user)
        db_session.commit()
        
        # Try to login with wrong password
        login_data = UserLogin(email="test@example.com", password="wrongpassword")
        
        with pytest.raises(HTTPException) as exc_info:
            AuthService.login_user(db_session, login_data)
        
        assert exc_info.value.status_code == 401
    
    def test_login_user_not_found(self, db_session: Session):
        """Test user login with non-existent user."""
        from app.schemas.auth import UserLogin
        from fastapi import HTTPException
        
        # Try to login with non-existent user
        login_data = UserLogin(email="nonexistent@example.com", password="anypassword")
        
        with pytest.raises(HTTPException) as exc_info:
            AuthService.login_user(db_session, login_data)
        
        assert exc_info.value.status_code == 401
    
    def test_get_user_by_id(self, db_session: Session):
        """Test getting user by ID."""
        user = User(
            email="test@example.com",
            password_hash=get_password_hash("password"),
            name="Test User"
        )
        db_session.add(user)
        db_session.commit()
        
        found_user = AuthService.get_user_by_id(db_session, str(user.id))
        
        assert found_user is not None
        assert found_user.email == "test@example.com"
    
    def test_logout_user(self, db_session: Session):
        """Test user logout."""
        token = "test_token_123"
        AuthService.logout_user(token)
        
        # Note: In a real implementation, this would verify the token is blacklisted
        # For now, we just test that the method doesn't raise an exception
        assert True


class TestFileService:
    """Test file service functions."""
    
    @pytest.mark.asyncio
    async def test_list_files_in_folder(self, db_session: Session, created_folder: Folder, created_user: User):
        """Test listing files in folder."""
        file_service = FileService(db_session)
        
        # Create a test file in the database
        test_file = File(
            folder_id=created_folder.id,
            name="test.txt",
            mime_type="text/plain",
            size=1024,
            path="/uploads/test.txt",
            text_content="Test content"
        )
        db_session.add(test_file)
        db_session.commit()
        
        # List files
        result = file_service.list_files_in_folder(str(created_folder.id), created_user)
        
        assert len(result.data) == 1
        assert result.data[0].name == "test.txt"
        assert result.meta.total == 1
    
    def test_get_file_metadata(self, db_session: Session, created_folder: Folder, created_user: User):
        """Test getting file metadata."""
        file_service = FileService(db_session)
        
        # Create a test file
        test_file = File(
            folder_id=created_folder.id,
            name="test.txt",
            mime_type="text/plain",
            size=1024,
            path="/uploads/test.txt",
            text_content="Test content"
        )
        db_session.add(test_file)
        db_session.commit()
        
        # Get file metadata
        result = file_service.get_file_metadata(str(test_file.id), created_user)
        
        assert result.name == "test.txt"
        assert result.mime_type == "text/plain"
        assert result.size == 1024
    
    def test_get_file_content(self, db_session: Session, created_folder: Folder, created_user: User):
        """Test getting file content."""
        file_service = FileService(db_session)
        
        # Create a test file
        test_file = File(
            folder_id=created_folder.id,
            name="test.txt",
            mime_type="text/plain",
            size=1024,
            path="/uploads/test.txt",
            text_content="Test content"
        )
        db_session.add(test_file)
        db_session.commit()
        
        # Get file content
        content, mime_type = file_service.get_file_content(str(test_file.id), created_user)
        
        assert content == "Test content"
        assert mime_type == "text/plain"
    
    def test_delete_file_soft(self, db_session: Session, created_folder: Folder, created_user: User):
        """Test soft file deletion."""
        file_service = FileService(db_session)
        
        # Create a test file
        test_file = File(
            folder_id=created_folder.id,
            name="test.txt",
            mime_type="text/plain",
            size=1024,
            path="/uploads/test.txt",
            text_content="Test content"
        )
        db_session.add(test_file)
        db_session.commit()
        
        # Delete file (soft delete)
        file_service.delete_file(str(test_file.id), created_user, force=False)
        
        # File should be marked as deleted
        db_session.refresh(test_file)
        assert test_file.deleted_at is not None
    
    def test_delete_file_hard(self, db_session: Session, created_folder: Folder, created_user: User):
        """Test hard file deletion."""
        file_service = FileService(db_session)
        
        # Create a test file
        test_file = File(
            folder_id=created_folder.id,
            name="test.txt",
            mime_type="text/plain",
            size=1024,
            path="/uploads/test.txt",
            text_content="Test content"
        )
        db_session.add(test_file)
        db_session.commit()
        file_id = str(test_file.id)
        
        # Delete file (hard delete)
        file_service.delete_file(file_id, created_user, force=True)
        
        # File should be completely removed
        deleted_file = db_session.query(File).filter(File.id == test_file.id).first()
        assert deleted_file is None


class TestFolderService:
    """Test folder service functions."""
    
    def test_create_folder(self, db_session: Session, created_user: User):
        """Test folder creation service."""
        from app.schemas.folder import FolderCreate
        
        folder_data = FolderCreate(
            title="Test Folder",
            description="Test folder description"
        )
        
        folder = FolderService.create_folder(db_session, created_user, folder_data)
        
        assert folder.title == folder_data.title
        assert folder.description == folder_data.description
        assert folder.owner_id == created_user.id
        assert folder.id is not None
    
    def test_list_folders(self, db_session: Session, created_user: User):
        """Test listing folders by owner."""
        from app.schemas.folder import FolderCreate
        
        # Create multiple folders
        folders_data = [
            FolderCreate(title="Folder 1", description="First folder"),
            FolderCreate(title="Folder 2", description="Second folder"),
        ]
        
        for folder_data in folders_data:
            FolderService.create_folder(db_session, created_user, folder_data)
        
        result = FolderService.list_folders(db_session, created_user)
        
        assert len(result.data) == 2
        assert all(folder.owner_id == created_user.id for folder in result.data)
    
    def test_get_folder(self, db_session: Session, created_user: User):
        """Test getting folder by ID."""
        from app.schemas.folder import FolderCreate
        
        folder_data = FolderCreate(
            title="Test Folder",
            description="Test folder description"
        )
        
        created_folder = FolderService.create_folder(db_session, created_user, folder_data)
        
        retrieved_folder = FolderService.get_folder(db_session, created_user, created_folder.id)
        
        assert retrieved_folder is not None
        assert retrieved_folder.id == created_folder.id
        assert retrieved_folder.title == folder_data.title
    
    def test_update_folder(self, db_session: Session, created_user: User):
        """Test folder update service."""
        from app.schemas.folder import FolderCreate, FolderUpdate
        
        folder_data = FolderCreate(
            title="Original Title",
            description="Original description"
        )
        
        folder = FolderService.create_folder(db_session, created_user, folder_data)
        
        update_data = FolderUpdate(
            title="Updated Title",
            description="Updated description"
        )
        
        updated_folder = FolderService.update_folder(db_session, created_user, folder.id, update_data)
        
        assert updated_folder.title == update_data.title
        assert updated_folder.description == update_data.description
    
    def test_delete_folder(self, db_session: Session, created_user: User):
        """Test folder deletion."""
        from app.schemas.folder import FolderCreate
        
        folder_data = FolderCreate(
            title="Test Folder",
            description="Test folder description"
        )
        
        folder = FolderService.create_folder(db_session, created_user, folder_data)
        
        FolderService.delete_folder(db_session, created_user, folder.id)
        
        # Folder should be marked as deleted
        # Note: The get_folder method should raise an exception for deleted folders
        from fastapi import HTTPException
        with pytest.raises(HTTPException):
            FolderService.get_folder(db_session, created_user, folder.id)


class TestSpaceService:
    """Test space service functions."""
    
    def test_create_space(self, db_session: Session, created_folder: Folder, created_user: User):
        """Test space creation service."""
        
        space_data = SpaceCreate(
            type=SpaceType.chat,
            title="Test Chat Space",
            settings={"theme": "dark"}
        )
        
        space = SpaceService.create_space(db_session, created_user, str(created_folder.id), space_data)
        
        assert space.type == space_data.type
        assert space.title == space_data.title
        assert str(space.folder_id) == str(created_folder.id)
        assert space.id is not None
    
    def test_get_spaces_by_folder(self, db_session: Session, created_folder: Folder, created_user: User):
        """Test getting spaces by folder."""
        # Create multiple spaces using static methods
        spaces_data = [
            SpaceCreate(type=SpaceType.chat, title="Chat Space", settings={}),
            SpaceCreate(type=SpaceType.quiz, title="Quiz Space", settings={}),
        ]
        
        created_spaces = []
        for space_data in spaces_data:
            space = SpaceService.create_space(db_session, created_user, str(created_folder.id), space_data)
            created_spaces.append(space)
        
        spaces_response = SpaceService.list_spaces(db_session, created_user, str(created_folder.id))
        
        assert len(spaces_response.data) == 2
        assert all(space.folder_id == created_folder.id for space in spaces_response.data)
    
    def test_get_space_by_id(self, db_session: Session, created_folder: Folder, created_user: User):
        """Test getting space by ID."""
        space_data = SpaceCreate(
            type=SpaceType.chat,
            title="Test Chat Space",
            settings={}
        )
        
        created_space = SpaceService.create_space(db_session, created_user, str(created_folder.id), space_data)
        
        retrieved_space = SpaceService.get_space(db_session, created_user, str(created_space.id))
        
        assert retrieved_space is not None
        assert retrieved_space.id == created_space.id
        assert retrieved_space.title == space_data.title
    
    def test_update_space(self, db_session: Session, created_folder: Folder, created_user: User):
        """Test space update service."""
        space_data = SpaceCreate(
            type=SpaceType.chat,
            title="Original Title",
            settings={}
        )
        
        space = SpaceService.create_space(db_session, created_user, str(created_folder.id), space_data)
        
        update_data = SpaceUpdate(
            title="Updated Title",
            settings={"theme": "light"}
        )
        
        updated_space = SpaceService.update_space(db_session, created_user, str(space.id), update_data)
        
        assert updated_space.title == update_data.title
        assert updated_space.settings == update_data.settings
    
    def test_delete_space(self, db_session: Session, created_folder: Folder, created_user: User):
        """Test space deletion."""
        space_data = SpaceCreate(
            type=SpaceType.chat,
            title="Test Chat Space",
            settings={}
        )
        
        space = SpaceService.create_space(db_session, created_user, str(created_folder.id), space_data)
        
        SpaceService.delete_space(db_session, created_user, str(space.id))
        
        # Space should be deleted - this will raise an exception
        with pytest.raises(Exception):
            SpaceService.get_space(db_session, created_user, str(space.id))


class TestChatService:
    """Test chat service functions."""
    
    def test_send_message(self, db_session: Session, created_space: Space, created_user: User):
        """Test sending a chat message."""
        chat_service = ChatService(db_session)
        
        message_request = MessageRequest(
            content="Hello, this is a test message"
        )
        
        messages = chat_service.send_message(
            space_id=created_space.id,
            message_request=message_request,
            user_id=created_user.id
        )
        
        assert len(messages) == 2  # User message + AI response
        assert messages[0].role == "user"
        assert messages[0].content == "Hello, this is a test message"
        assert messages[0].spaceId == created_space.id
        assert messages[0].id is not None
    
    def test_get_messages_by_space(self, db_session: Session, created_space: Space, created_user: User):
        """Test getting messages by space."""
        chat_service = ChatService(db_session)
        
        # Create multiple messages
        message_requests = [
            MessageRequest(content="Message 1"),
            MessageRequest(content="Message 2"),
        ]
        
        for message_request in message_requests:
            chat_service.send_message(
                space_id=created_space.id,
                message_request=message_request,
                user_id=created_user.id
            )
        
        messages_response = chat_service.get_message_history(
            space_id=created_space.id,
            user_id=created_user.id
        )
        
        assert len(messages_response["data"]) >= 4  # 2 user messages + 2 AI responses
        assert all(msg.spaceId == str(created_space.id) for msg in messages_response["data"])
    
    def test_delete_message(self, db_session: Session, created_space: Space, created_user: User):
        """Test message deletion."""
        chat_service = ChatService(db_session)
        
        message_request = MessageRequest(content="Test message to delete")
        
        messages = chat_service.send_message(
            space_id=created_space.id,
            message_request=message_request,
            user_id=created_user.id
        )
        
        # Delete the user message
        chat_service.delete_message(messages[0].id, created_user.id)
        
        # Check that message is deleted
        messages_response = chat_service.get_message_history(
            space_id=created_space.id,
            user_id=created_user.id
        )
        
        # Should only have the AI response left
        assert len(messages_response["data"]) == 1


class TestQuizService:
    """Test quiz service functions."""
    
    def test_generate_quiz(self, db_session: Session, created_space: Space, created_user: User):
        """Test quiz generation service."""
        
        quiz_data = QuizCreate(
            title="Test Quiz",
            fileIds=["123e4567-e89b-12d3-a456-426614174000"],  # Valid UUID
            questionCount=1,
            questionTypes=["mcq"],
            difficulty="easy"
        )
        
        quiz = QuizService.generate_quiz(db_session, created_user, str(created_space.id), quiz_data)
        
        assert quiz.title == quiz_data.title
        assert quiz.space_id == created_space.id
        assert len(quiz.questions) == 1
        assert quiz.id is not None
    
    def test_submit_quiz_answers(self, db_session: Session, created_space: Space, created_user: User):
        """Test quiz answer submission."""
        
        # Create quiz first
        quiz_data = QuizCreate(
            title="Test Quiz",
            fileIds=["123e4567-e89b-12d3-a456-426614174000"],
            questionCount=1,
            questionTypes=["mcq"],
            difficulty="easy"
        )
        
        quiz = QuizService.generate_quiz(db_session, created_user, str(created_space.id), quiz_data)
        
        # Submit answers
        submission_data = QuizSubmissionSchema(
            answers=[
                {"questionId": "q1", "answer": "4"}
            ]
        )
        
        submission = QuizService.submit_answers(db_session, created_user, str(quiz.id), submission_data)
        
        assert submission.quiz_id == quiz.id
        assert submission.score == 1.0  # Correct answer
        assert submission.id is not None
    
    def test_get_quiz_by_id(self, db_session: Session, created_space: Space, created_user: User):
        """Test getting quiz by ID."""
        
        quiz_data = QuizCreate(
            title="Test Quiz",
            fileIds=["123e4567-e89b-12d3-a456-426614174000"],
            questionCount=1,
            questionTypes=["mcq"],
            difficulty="easy"
        )
        
        created_quiz = QuizService.generate_quiz(db_session, created_user, str(created_space.id), quiz_data)
        
        retrieved_quiz = QuizService.get_quiz_by_id(db_session, created_user, str(created_quiz.id))
        
        assert retrieved_quiz is not None
        assert retrieved_quiz.id == created_quiz.id
        assert retrieved_quiz.title == quiz_data.title


class TestNotesService:
    """Test notes service functions."""
    
    def test_generate_notes(self, db_session: Session, created_space: Space, created_user: User):
        """Test notes generation service."""
        
        notes_data = NotesCreate(
            file_ids=["123e4567-e89b-12d3-a456-426614174000"],
            format="markdown"
        )
        
        notes = NotesService.generate_notes(db_session, created_user, str(created_space.id), notes_data)
        
        assert notes.space_id == created_space.id
        assert notes.format == notes_data.format
        assert notes.id is not None
    
    def test_update_notes(self, db_session: Session, created_space: Space, created_user: User):
        """Test notes update service."""
        
        notes_data = NotesCreate(
            file_ids=["123e4567-e89b-12d3-a456-426614174000"],
            format="markdown"
        )
        
        notes = NotesService.generate_notes(db_session, created_user, str(created_space.id), notes_data)
        
        update_data = NotesUpdate(
            content="Updated content"
        )
        
        updated_notes = NotesService.update_notes(db_session, created_user, str(notes.id), update_data)
        
        assert updated_notes.content == update_data.content
    
    def test_get_notes_by_space(self, db_session: Session, created_space: Space, created_user: User):
        """Test getting notes by space."""
        
        # Create multiple notes
        notes_data = [
            NotesCreate(file_ids=["123e4567-e89b-12d3-a456-426614174000"], format="markdown"),
            NotesCreate(file_ids=["123e4567-e89b-12d3-a456-426614174000"], format="markdown"),
        ]
        
        for note_data in notes_data:
            NotesService.generate_notes(db_session, created_user, str(created_space.id), note_data)
        
        notes = NotesService.get_notes_by_space(db_session, created_user, str(created_space.id))
        
        assert len(notes) == 2
        assert all(note.space_id == created_space.id for note in notes)


class TestFlashcardService:
    """Test flashcard service functions."""
    
    def test_generate_flashcards(self, db_session: Session, created_space: Space, created_user: User):
        """Test flashcard generation service."""
        
        flashcard_data = FlashcardCreate(
            title="Test Flashcards",
            fileIds=["123e4567-e89b-12d3-a456-426614174000"],
            cardCount=1,
            cardTypes=["mcq"],
            difficulty="easy"
        )
        
        flashcard = FlashcardService.generate_flashcards(db_session, created_user, str(created_space.id), flashcard_data)
        
        assert flashcard.title == flashcard_data.title
        assert flashcard.space_id == created_space.id
        assert flashcard.id is not None
    
    def test_shuffle_flashcards(self, db_session: Session, created_space: Space, created_user: User):
        """Test flashcard shuffling."""
        
        flashcard_data = FlashcardCreate(
            title="Test Flashcards",
            fileIds=["123e4567-e89b-12d3-a456-426614174000"],
            cardCount=3,
            cardTypes=["mcq"],
            difficulty="easy"
        )
        
        flashcard = FlashcardService.generate_flashcards(db_session, created_user, str(created_space.id), flashcard_data)
        
        shuffled_flashcard = FlashcardService.shuffle_flashcards(db_session, created_user, str(flashcard.id))
        
        # Verify the flashcard still exists and has the same number of cards
        assert shuffled_flashcard.id == flashcard.id
        assert shuffled_flashcard.title == flashcard.title


class TestOpenEndedService:
    """Test open-ended questions service functions."""
    
    def test_generate_openended_questions(self, db_session: Session, created_space: Space, created_user: User):
        """Test open-ended questions generation service."""
        
        questions_data = OpenEndedQuestionCreate(
            title="Test Questions",
            spaceId=str(created_space.id),
            fileIds=["123e4567-e89b-12d3-a456-426614174000"],
            questionCount=1,
            questionTypes=["short_answer"],
            difficulty="medium"
        )
        
        questions = OpenEndedService.generate_openended_questions(db_session, created_user, questions_data)
        
        assert questions.title == questions_data.title
        assert questions.space_id == created_space.id
        assert questions.id is not None
    
    def test_submit_openended_answers(self, db_session: Session, created_space: Space, created_user: User):
        """Test open-ended answer submission."""
        
        # Create questions first
        questions_data = OpenEndedQuestionCreate(
            title="Test Questions",
            spaceId=str(created_space.id),
            fileIds=["123e4567-e89b-12d3-a456-426614174000"],
            questionCount=1,
            questionTypes=["short_answer"],
            difficulty="medium"
        )
        
        questions = OpenEndedService.generate_openended_questions(db_session, created_user, questions_data)
        
        # Submit answers
        answer_data = OpenEndedSubmission(
            answers=[
                {
                    "question_id": "q1",
                    "answer": "Photosynthesis is the process by which plants convert light energy into chemical energy. This process occurs in the chloroplasts and involves multiple steps including light-dependent reactions and the Calvin cycle."
                }
            ]
        )
        
        submission = OpenEndedService.submit_openended_answers(db_session, created_user, str(questions.id), answer_data)
        
        assert submission.open_ended_question_id == questions.id
        assert submission.score is not None
        assert submission.id is not None
    
    def test_get_answers_by_question_set(self, db_session: Session, created_space: Space, created_user: User):
        """Test getting answers by question set."""
        
        # Create questions and submit answers
        questions_data = OpenEndedQuestionCreate(
            title="Test Questions",
            spaceId=str(created_space.id),
            fileIds=["123e4567-e89b-12d3-a456-426614174000"],
            questionCount=1,
            questionTypes=["short_answer"],
            difficulty="medium"
        )
        
        questions = OpenEndedService.generate_openended_questions(db_session, created_user, questions_data)
        
        answer_data = OpenEndedSubmission(
            answers=[
                {
                    "question_id": "q1",
                    "answer": "Photosynthesis converts light to energy."
                }
            ]
        )
        
        OpenEndedService.submit_openended_answers(db_session, created_user, str(questions.id), answer_data)
        
        answers = OpenEndedService.get_answers_by_question_set(db_session, created_user, str(questions.id))
        
        assert len(answers) == 1
        assert answers[0].open_ended_question_id == questions.id 