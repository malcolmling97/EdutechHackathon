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
        from app.schemas.space import SpaceCreate
        
        space_data = SpaceCreate(
            type=SpaceType.chat,
            title="Test Chat Space",
            settings={"theme": "dark"}
        )
        
        space = SpaceService.create_space(db_session, created_user, str(created_folder.id), space_data)
        
        assert space.type == space_data.type
        assert space.title == space_data.title
        assert space.folderId == str(created_folder.id)
        assert space.id is not None
    
    def test_get_spaces_by_folder(self, db_session: Session, created_folder: Folder):
        """Test getting spaces by folder."""
        space_service = SpaceService(db_session)
        
        # Create multiple spaces
        spaces_data = [
            {"type": SpaceType.chat, "title": "Chat Space", "settings": {}, "folder_id": created_folder.id},
            {"type": SpaceType.quiz, "title": "Quiz Space", "settings": {}, "folder_id": created_folder.id},
        ]
        
        for space_data in spaces_data:
            space_service.create_space(space_data)
        
        spaces = space_service.get_spaces_by_folder(created_folder.id)
        
        assert len(spaces) == 2
        assert all(space.folder_id == created_folder.id for space in spaces)
    
    def test_get_space_by_id(self, db_session: Session, created_folder: Folder):
        """Test getting space by ID."""
        space_service = SpaceService(db_session)
        
        space_data = {
            "type": SpaceType.chat,
            "title": "Test Chat Space",
            "settings": {},
            "folder_id": created_folder.id
        }
        
        created_space = space_service.create_space(space_data)
        
        retrieved_space = space_service.get_space_by_id(created_space.id)
        
        assert retrieved_space is not None
        assert retrieved_space.id == created_space.id
        assert retrieved_space.title == space_data["title"]
    
    def test_update_space(self, db_session: Session, created_folder: Folder):
        """Test space update service."""
        space_service = SpaceService(db_session)
        
        space_data = {
            "type": SpaceType.chat,
            "title": "Original Title",
            "settings": {},
            "folder_id": created_folder.id
        }
        
        space = space_service.create_space(space_data)
        
        update_data = {
            "title": "Updated Title",
            "settings": {"theme": "light"}
        }
        
        updated_space = space_service.update_space(space.id, update_data)
        
        assert updated_space.title == update_data["title"]
        assert updated_space.settings == update_data["settings"]
    
    def test_delete_space(self, db_session: Session, created_folder: Folder):
        """Test space deletion."""
        space_service = SpaceService(db_session)
        
        space_data = {
            "type": SpaceType.chat,
            "title": "Test Chat Space",
            "settings": {},
            "folder_id": created_folder.id
        }
        
        space = space_service.create_space(space_data)
        
        space_service.delete_space(space.id)
        
        # Space should be deleted
        retrieved_space = space_service.get_space_by_id(space.id)
        assert retrieved_space is None


class TestChatService:
    """Test chat service functions."""
    
    def test_send_message(self, db_session: Session, created_space: Space):
        """Test sending a chat message."""
        chat_service = ChatService(db_session)
        
        message_data = {
            "role": "user",
            "content": "Hello, this is a test message",
            "space_id": created_space.id
        }
        
        message = chat_service.send_message(message_data)
        
        assert message.role == message_data["role"]
        assert message.content == message_data["content"]
        assert message.space_id == created_space.id
        assert message.id is not None
    
    def test_get_messages_by_space(self, db_session: Session, created_space: Space):
        """Test getting messages by space."""
        chat_service = ChatService(db_session)
        
        # Create multiple messages
        messages_data = [
            {"role": "user", "content": "Message 1", "space_id": created_space.id},
            {"role": "assistant", "content": "Response 1", "space_id": created_space.id},
            {"role": "user", "content": "Message 2", "space_id": created_space.id},
        ]
        
        for message_data in messages_data:
            chat_service.send_message(message_data)
        
        messages = chat_service.get_messages_by_space(created_space.id)
        
        assert len(messages) == 3
        assert all(message.space_id == created_space.id for message in messages)
    
    def test_delete_message(self, db_session: Session, created_space: Space):
        """Test message deletion."""
        chat_service = ChatService(db_session)
        
        message_data = {
            "role": "user",
            "content": "Test message to delete",
            "space_id": created_space.id
        }
        
        message = chat_service.send_message(message_data)
        
        chat_service.delete_message(message.id)
        
        # Message should be deleted
        messages = chat_service.get_messages_by_space(created_space.id)
        assert len(messages) == 0


class TestQuizService:
    """Test quiz service functions."""
    
    def test_generate_quiz(self, db_session: Session, created_space: Space):
        """Test quiz generation service."""
        quiz_service = QuizService(db_session)
        
        quiz_data = {
            "title": "Test Quiz",
            "space_id": created_space.id,
            "questions": [
                {
                    "id": "q1",
                    "type": "mcq",
                    "prompt": "What is 2+2?",
                    "choices": ["3", "4", "5", "6"],
                    "answer": "4"
                }
            ]
        }
        
        quiz = quiz_service.generate_quiz(quiz_data)
        
        assert quiz.title == quiz_data["title"]
        assert quiz.space_id == created_space.id
        assert len(quiz.questions) == 1
        assert quiz.id is not None
    
    def test_submit_quiz_answers(self, db_session: Session, created_space: Space):
        """Test quiz answer submission."""
        quiz_service = QuizService(db_session)
        
        # Create quiz first
        quiz_data = {
            "title": "Test Quiz",
            "space_id": created_space.id,
            "questions": [
                {
                    "id": "q1",
                    "type": "mcq",
                    "prompt": "What is 2+2?",
                    "choices": ["3", "4", "5", "6"],
                    "answer": "4"
                }
            ]
        }
        
        quiz = quiz_service.generate_quiz(quiz_data)
        
        # Submit answers
        submission_data = {
            "quiz_id": quiz.id,
            "answers": [
                {"questionId": "q1", "answer": "4"}
            ]
        }
        
        submission = quiz_service.submit_answers(submission_data)
        
        assert submission.quiz_id == quiz.id
        assert submission.score == 1.0  # Correct answer
        assert submission.id is not None
    
    def test_get_quiz_by_id(self, db_session: Session, created_space: Space):
        """Test getting quiz by ID."""
        quiz_service = QuizService(db_session)
        
        quiz_data = {
            "title": "Test Quiz",
            "space_id": created_space.id,
            "questions": []
        }
        
        created_quiz = quiz_service.generate_quiz(quiz_data)
        
        retrieved_quiz = quiz_service.get_quiz_by_id(created_quiz.id)
        
        assert retrieved_quiz is not None
        assert retrieved_quiz.id == created_quiz.id
        assert retrieved_quiz.title == quiz_data["title"]


class TestNotesService:
    """Test notes service functions."""
    
    def test_generate_notes(self, db_session: Session, created_space: Space):
        """Test notes generation service."""
        notes_service = NotesService(db_session)
        
        notes_data = {
            "space_id": created_space.id,
            "format": "markdown",
            "content": "# Generated Notes\n\nThis is test content."
        }
        
        notes = notes_service.generate_notes(notes_data)
        
        assert notes.space_id == created_space.id
        assert notes.format == notes_data["format"]
        assert notes.content == notes_data["content"]
        assert notes.id is not None
    
    def test_update_notes(self, db_session: Session, created_space: Space):
        """Test notes update service."""
        notes_service = NotesService(db_session)
        
        notes_data = {
            "space_id": created_space.id,
            "format": "markdown",
            "content": "Original content"
        }
        
        notes = notes_service.generate_notes(notes_data)
        
        update_data = {
            "content": "Updated content"
        }
        
        updated_notes = notes_service.update_notes(notes.id, update_data)
        
        assert updated_notes.content == update_data["content"]
    
    def test_get_notes_by_space(self, db_session: Session, created_space: Space):
        """Test getting notes by space."""
        notes_service = NotesService(db_session)
        
        # Create multiple notes
        notes_data = [
            {"space_id": created_space.id, "format": "markdown", "content": "Notes 1"},
            {"space_id": created_space.id, "format": "markdown", "content": "Notes 2"},
        ]
        
        for note_data in notes_data:
            notes_service.generate_notes(note_data)
        
        notes = notes_service.get_notes_by_space(created_space.id)
        
        assert len(notes) == 2
        assert all(note.space_id == created_space.id for note in notes)


class TestFlashcardService:
    """Test flashcard service functions."""
    
    def test_generate_flashcards(self, db_session: Session, created_space: Space):
        """Test flashcard generation service."""
        flashcard_service = FlashcardService(db_session)
        
        flashcard_data = {
            "title": "Test Flashcards",
            "space_id": created_space.id,
            "cards": [
                {
                    "id": "card1",
                    "front": "What is 2+2?",
                    "back": "4",
                    "difficulty": "easy"
                }
            ]
        }
        
        flashcard = flashcard_service.generate_flashcards(flashcard_data)
        
        assert flashcard.title == flashcard_data["title"]
        assert flashcard.space_id == created_space.id
        assert len(flashcard.cards) == 1
        assert flashcard.id is not None
    
    def test_shuffle_flashcards(self, db_session: Session, created_space: Space):
        """Test flashcard shuffling."""
        flashcard_service = FlashcardService(db_session)
        
        flashcard_data = {
            "title": "Test Flashcards",
            "space_id": created_space.id,
            "cards": [
                {"id": "card1", "front": "Question 1", "back": "Answer 1", "difficulty": "easy"},
                {"id": "card2", "front": "Question 2", "back": "Answer 2", "difficulty": "medium"},
                {"id": "card3", "front": "Question 3", "back": "Answer 3", "difficulty": "hard"},
            ]
        }
        
        flashcard = flashcard_service.generate_flashcards(flashcard_data)
        
        original_order = [card["id"] for card in flashcard.cards]
        
        shuffled_flashcard = flashcard_service.shuffle_flashcards(flashcard.id)
        
        shuffled_order = [card["id"] for card in shuffled_flashcard.cards]
        
        # Order should be different (though there's a small chance it could be the same)
        # We'll just verify the cards are still there
        assert len(shuffled_order) == len(original_order)
        assert set(shuffled_order) == set(original_order)


class TestOpenEndedService:
    """Test open-ended questions service functions."""
    
    def test_generate_openended_questions(self, db_session: Session, created_space: Space):
        """Test open-ended questions generation service."""
        openended_service = OpenEndedService(db_session)
        
        questions_data = {
            "title": "Test Questions",
            "space_id": created_space.id,
            "questions": [
                {
                    "id": "q1",
                    "prompt": "Explain photosynthesis.",
                    "rubric": {"criteria": ["accuracy", "completeness"], "weights": [0.5, 0.5]},
                    "wordCount": {"min": 50, "max": 200}
                }
            ]
        }
        
        questions = openended_service.generate_questions(questions_data)
        
        assert questions.title == questions_data["title"]
        assert questions.space_id == created_space.id
        assert len(questions.questions) == 1
        assert questions.id is not None
    
    def test_submit_openended_answers(self, db_session: Session, created_space: Space):
        """Test open-ended answer submission."""
        openended_service = OpenEndedService(db_session)
        
        # Create questions first
        questions_data = {
            "title": "Test Questions",
            "space_id": created_space.id,
            "questions": [
                {
                    "id": "q1",
                    "prompt": "Explain photosynthesis.",
                    "rubric": {"criteria": ["accuracy", "completeness"], "weights": [0.5, 0.5]},
                    "wordCount": {"min": 50, "max": 200}
                }
            ]
        }
        
        questions = openended_service.generate_questions(questions_data)
        
        # Submit answers
        answer_data = {
            "question_set_id": questions.id,
            "answers": [
                {
                    "question_id": "q1",
                    "answer": "Photosynthesis is the process by which plants convert light energy into chemical energy. This process occurs in the chloroplasts and involves multiple steps including light-dependent reactions and the Calvin cycle."
                }
            ]
        }
        
        submission = openended_service.submit_answers(answer_data)
        
        assert submission.question_set_id == questions.id
        assert submission.score is not None
        assert submission.id is not None
    
    def test_get_answers_by_question_set(self, db_session: Session, created_space: Space):
        """Test getting answers by question set."""
        openended_service = OpenEndedService(db_session)
        
        # Create questions and submit answers
        questions_data = {
            "title": "Test Questions",
            "space_id": created_space.id,
            "questions": [
                {
                    "id": "q1",
                    "prompt": "Explain photosynthesis.",
                    "rubric": {"criteria": ["accuracy"], "weights": [1.0]},
                    "wordCount": {"min": 10, "max": 100}
                }
            ]
        }
        
        questions = openended_service.generate_questions(questions_data)
        
        answer_data = {
            "question_set_id": questions.id,
            "answers": [
                {
                    "question_id": "q1",
                    "answer": "Photosynthesis converts light to energy."
                }
            ]
        }
        
        openended_service.submit_answers(answer_data)
        
        answers = openended_service.get_answers_by_question_set(questions.id)
        
        assert len(answers) == 1
        assert answers[0].question_set_id == questions.id 