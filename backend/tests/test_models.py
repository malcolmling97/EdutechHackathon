"""
Tests for database models in the EdutechHackathon backend.

Tests model definitions, relationships, and methods:
- Model creation and validation
- Database relationships
- Model methods and properties
- Data serialization
- Model constraints and validations
"""
import pytest
import uuid
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.models.user import User
from app.models.folder import Folder
from app.models.space import Space, SpaceType
from app.models.file import File
from app.models.chat_message import ChatMessage
from app.models.quiz import Quiz, QuizSubmission
from app.models.note import Note
from app.models.flashcard import Flashcard
from app.models.openended import OpenEndedQuestion, OpenEndedAnswer
from app.core.security import get_password_hash


class TestUserModel:
    """Test User model."""
    
    def test_create_user(self, db_session: Session):
        """Test user creation."""
        user = User(
            email="test@example.com",
            password_hash=get_password_hash("password123"),
            name="Test User"
        )
        
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        
        assert user.id is not None
        assert user.email == "test@example.com"
        assert user.name == "Test User"
        assert user.created_at is not None
        assert user.updated_at is not None
        assert user.password_hash != "password123"  # Should be hashed
    
    def test_user_email_uniqueness(self, db_session: Session):
        """Test that user emails must be unique."""
        user1 = User(
            email="test@example.com",
            password_hash=get_password_hash("password123"),
            name="Test User 1"
        )
        
        user2 = User(
            email="test@example.com",  # Same email
            password_hash=get_password_hash("password456"),
            name="Test User 2"
        )
        
        db_session.add(user1)
        db_session.commit()
        
        db_session.add(user2)
        with pytest.raises(IntegrityError):
            db_session.commit()
    
    def test_user_relationships(self, db_session: Session):
        """Test user relationships with folders."""
        user = User(
            email="test_relationships@example.com",
            password_hash=get_password_hash("password123"),
            name="Test User"
        )
        
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        
        folder = Folder(
            title="Test Folder",
            description="Test description",
            owner_id=user.id
        )
        
        db_session.add(folder)
        db_session.commit()
        db_session.refresh(user)
        db_session.refresh(folder)
        
        # Test relationship
        assert folder.owner_id == user.id
        assert folder.owner == user
    
    def test_user_soft_delete(self, db_session: Session):
        """Test user soft deletion."""
        user = User(
            email="test@example.com",
            password_hash=get_password_hash("password123"),
            name="Test User"
        )
        
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        
        # Soft delete
        user.deleted_at = datetime.utcnow()
        db_session.commit()
        
        # User should still exist in database but be marked as deleted
        assert user.deleted_at is not None


class TestFolderModel:
    """Test Folder model."""
    
    def test_create_folder(self, db_session: Session, created_user: User):
        """Test folder creation."""
        folder = Folder(
            title="Test Folder",
            description="Test folder description",
            owner_id=created_user.id
        )
        
        db_session.add(folder)
        db_session.commit()
        db_session.refresh(folder)
        
        assert folder.id is not None
        assert folder.title == "Test Folder"
        assert folder.description == "Test folder description"
        assert folder.owner_id == created_user.id
        assert folder.created_at is not None
    
    def test_folder_relationships(self, db_session: Session, created_user: User):
        """Test folder relationships with files."""
        folder = Folder(
            title="Test Folder",
            description="Test description",
            owner_id=created_user.id
        )
        
        db_session.add(folder)
        db_session.commit()
        db_session.refresh(folder)
        
        file = File(
            name="test.txt",
            mime_type="text/plain",
            size=1024,
            path="/uploads/test.txt",
            text_content="Test content",
            folder_id=folder.id
        )
        
        db_session.add(file)
        db_session.commit()
        db_session.refresh(folder)
        db_session.refresh(file)
        
        # Test relationship
        assert file.folder_id == folder.id
        assert file.folder == folder
    
    def test_folder_title_required(self, db_session: Session, created_user: User):
        """Test that folder title is required."""
        folder = Folder(
            title=None,  # Missing title
            description="Test description",
            owner_id=created_user.id
        )
        
        db_session.add(folder)
        with pytest.raises(IntegrityError):
            db_session.commit()


class TestSpaceModel:
    """Test Space model."""
    
    def test_create_space(self, db_session: Session, created_folder: Folder):
        """Test space creation."""
        space = Space(
            type=SpaceType.chat,
            title="Test Chat Space",
            settings={"theme": "dark"},
            folder_id=created_folder.id
        )
        
        db_session.add(space)
        db_session.commit()
        db_session.refresh(space)
        
        assert space.id is not None
        assert space.type == SpaceType.chat
        assert space.title == "Test Chat Space"
        assert space.settings == {"theme": "dark"}
        assert space.folder_id == created_folder.id
        assert space.created_at is not None
    
    def test_space_types(self, db_session: Session, created_folder: Folder):
        """Test all space types."""
        space_types = [
            SpaceType.chat,
            SpaceType.quiz,
            SpaceType.notes,
            SpaceType.flashcards,
            SpaceType.openended,
            SpaceType.studyguide
        ]
        
        for space_type in space_types:
            space = Space(
                type=space_type,
                title=f"Test {space_type.value} Space",
                folder_id=created_folder.id
            )
            
            db_session.add(space)
            db_session.commit()
            db_session.refresh(space)
            
            assert space.type == space_type
            assert space.title == f"Test {space_type.value} Space"
    
    def test_space_relationships(self, db_session: Session, created_folder: Folder):
        """Test space relationships."""
        space = Space(
            type=SpaceType.chat,
            title="Test Space",
            folder_id=created_folder.id
        )
        
        db_session.add(space)
        db_session.commit()
        db_session.refresh(space)
        
        # Test relationship with folder
        assert space.folder_id == created_folder.id
        assert space.folder == created_folder


class TestFileModel:
    """Test File model."""
    
    def test_create_file(self, db_session: Session, created_folder: Folder):
        """Test file creation."""
        file = File(
            name="test.txt",
            mime_type="text/plain",
            size=1024,
            path="/uploads/test.txt",
            text_content="This is test content",
            folder_id=created_folder.id
        )
        
        db_session.add(file)
        db_session.commit()
        db_session.refresh(file)
        
        assert file.id is not None
        assert file.name == "test.txt"
        assert file.mime_type == "text/plain"
        assert file.size == 1024
        assert file.path == "/uploads/test.txt"
        assert file.text_content == "This is test content"
        assert file.folder_id == created_folder.id
        assert file.created_at is not None
    
    def test_file_soft_delete(self, db_session: Session, created_folder: Folder):
        """Test file soft deletion."""
        file = File(
            name="test.txt",
            mime_type="text/plain",
            size=1024,
            path="/uploads/test.txt",
            text_content="Test content",
            folder_id=created_folder.id
        )
        
        db_session.add(file)
        db_session.commit()
        db_session.refresh(file)
        
        # Soft delete
        file.deleted_at = datetime.utcnow()
        db_session.commit()
        
        assert file.deleted_at is not None
    
    def test_file_size_validation(self, db_session: Session, created_folder: Folder):
        """Test file size validation."""
        # Test with negative size
        file = File(
            name="test.txt",
            mime_type="text/plain",
            size=-1,  # Invalid size
            path="/uploads/test.txt",
            text_content="Test content",
            folder_id=created_folder.id
        )
        
        db_session.add(file)
        with pytest.raises(IntegrityError):
            db_session.commit()


class TestChatMessageModel:
    """Test ChatMessage model."""
    
    def test_create_chat_message(self, db_session: Session, created_space: Space):
        """Test chat message creation."""
        message = ChatMessage(
            role="user",
            content="Hello, this is a test message",
            space_id=created_space.id
        )
        
        db_session.add(message)
        db_session.commit()
        db_session.refresh(message)
        
        assert message.id is not None
        assert message.role.value == "user"
        assert message.content == "Hello, this is a test message"
        assert message.space_id == created_space.id
        assert message.created_at is not None
    
    def test_chat_message_roles(self, db_session: Session, created_space: Space):
        """Test different chat message roles."""
        roles = ["user", "assistant"]
        
        for role in roles:
            message = ChatMessage(
                space_id=created_space.id,
                role=role,
                content=f"Test message with role {role}"
            )
            
            db_session.add(message)
            db_session.commit()
            db_session.refresh(message)
            
            assert message.role.value == role
    
    def test_chat_message_relationships(self, db_session: Session, created_space: Space):
        """Test chat message relationships."""
        message = ChatMessage(
            role="user",
            content="Test message",
            space_id=created_space.id
        )
        
        db_session.add(message)
        db_session.commit()
        db_session.refresh(message)
        
        assert message.space_id == created_space.id
        assert message.space == created_space


class TestQuizModel:
    """Test Quiz model."""
    
    def test_create_quiz(self, db_session: Session, created_space: Space):
        """Test quiz creation."""
        quiz = Quiz(
            title="Test Quiz",
            space_id=created_space.id,
            questions=[
                {
                    "id": "q1",
                    "type": "mcq",
                    "prompt": "What is 2+2?",
                    "choices": ["3", "4", "5", "6"],
                    "answer": "4"
                }
            ]
        )
        
        db_session.add(quiz)
        db_session.commit()
        db_session.refresh(quiz)
        
        assert quiz.id is not None
        assert quiz.title == "Test Quiz"
        assert quiz.space_id == created_space.id
        assert len(quiz.questions) == 1
        assert quiz.created_at is not None
    
    def test_quiz_submission(self, db_session: Session, created_space: Space):
        """Test quiz submission creation."""
        quiz = Quiz(
            title="Test Quiz",
            space_id=created_space.id,
            questions=[
                {
                    "id": "q1",
                    "type": "mcq",
                    "prompt": "What is 2+2?",
                    "choices": ["3", "4", "5", "6"],
                    "answer": "4"
                }
            ]
        )
        
        db_session.add(quiz)
        db_session.commit()
        db_session.refresh(quiz)
        
        # Create a user for the submission
        user = User(
            email="test_quiz@example.com",
            password_hash=get_password_hash("password123"),
            name="Test User"
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        
        submission = QuizSubmission(
            quiz_id=quiz.id,
            user_id=user.id,
            answers=[
                {"questionId": "q1", "answer": "4"}
            ],
            score=1.0
        )
        
        db_session.add(submission)
        db_session.commit()
        db_session.refresh(submission)
        
        assert submission.id is not None
        assert submission.quiz_id == quiz.id
        assert submission.score == 1.0
        assert submission.submitted_at is not None
    
    def test_quiz_relationships(self, db_session: Session, created_space: Space):
        """Test quiz relationships."""
        quiz = Quiz(
            title="Test Quiz",
            space_id=created_space.id,
            questions=[]
        )
        
        db_session.add(quiz)
        db_session.commit()
        db_session.refresh(quiz)
        
        assert quiz.space_id == created_space.id
        assert quiz.space == created_space


class TestNoteModel:
    """Test Note model."""
    
    def test_create_note(self, db_session: Session, created_space: Space):
        """Test note creation."""
        note = Note(
            space_id=created_space.id,
            format="markdown",
            content="# Test Note\n\nThis is test content."
        )
        
        db_session.add(note)
        db_session.commit()
        db_session.refresh(note)
        
        assert note.id is not None
        assert note.space_id == created_space.id
        assert note.format.value == "markdown"
        assert note.content == "# Test Note\n\nThis is test content."
        assert note.created_at is not None
        assert note.updated_at is not None
    
    def test_note_formats(self, db_session: Session, created_space: Space):
        """Test different note formats."""
        formats = ["markdown", "bullet"]
        
        for format_type in formats:
            note = Note(
                space_id=created_space.id,
                format=format_type,
                content=f"Content in {format_type} format"
            )
            
            db_session.add(note)
            db_session.commit()
            db_session.refresh(note)
            
            assert note.format.value == format_type
    
    def test_note_update_timestamp(self, db_session: Session, created_space: Space):
        """Test that note updated_at is updated when content changes."""
        note = Note(
            space_id=created_space.id,
            format="markdown",
            content="Original content"
        )
        
        db_session.add(note)
        db_session.commit()
        db_session.refresh(note)
        
        original_updated_at = note.updated_at
        
        # Update content
        note.content = "Updated content"
        db_session.commit()
        db_session.refresh(note)
        
        assert note.updated_at > original_updated_at


class TestFlashcardModel:
    """Test Flashcard model."""
    
    def test_create_flashcard(self, db_session: Session, created_space: Space):
        """Test flashcard creation."""
        flashcard = Flashcard(
            title="Test Flashcards",
            space_id=created_space.id,
            cards=[
                {
                    "id": "card1",
                    "front": "What is 2+2?",
                    "back": "4",
                    "difficulty": "easy"
                }
            ]
        )
        
        db_session.add(flashcard)
        db_session.commit()
        db_session.refresh(flashcard)
        
        assert flashcard.id is not None
        assert flashcard.title == "Test Flashcards"
        assert flashcard.space_id == created_space.id
        assert len(flashcard.cards) == 1
        assert flashcard.created_at is not None
        assert flashcard.updated_at is not None
    
    def test_flashcard_shuffle(self, db_session: Session, created_space: Space):
        """Test flashcard shuffling."""
        flashcard = Flashcard(
            title="Test Flashcards",
            space_id=created_space.id,
            cards=[
                {"id": "card1", "front": "Q1", "back": "A1", "difficulty": "easy"},
                {"id": "card2", "front": "Q2", "back": "A2", "difficulty": "medium"},
                {"id": "card3", "front": "Q3", "back": "A3", "difficulty": "hard"},
            ]
        )
        
        db_session.add(flashcard)
        db_session.commit()
        db_session.refresh(flashcard)
        
        original_order = [card["id"] for card in flashcard.cards]
        
        # Shuffle cards
        flashcard.shuffle_cards()
        db_session.commit()
        db_session.refresh(flashcard)
        
        shuffled_order = [card["id"] for card in flashcard.cards]
        
        # Verify cards are still there (order might be same by chance)
        assert len(shuffled_order) == len(original_order)
        assert set(shuffled_order) == set(original_order)
    
    def test_flashcard_update_timestamp(self, db_session: Session, created_space: Space):
        """Test that flashcard updated_at is updated when cards change."""
        flashcard = Flashcard(
            title="Test Flashcards",
            space_id=created_space.id,
            cards=[]
        )
        
        db_session.add(flashcard)
        db_session.commit()
        db_session.refresh(flashcard)
        
        original_updated_at = flashcard.updated_at
        
        # Update cards
        flashcard.cards = [{"id": "card1", "front": "Q1", "back": "A1", "difficulty": "easy"}]
        db_session.commit()
        db_session.refresh(flashcard)
        
        assert flashcard.updated_at > original_updated_at


class TestOpenEndedModel:
    """Test OpenEndedQuestion model."""
    
    def test_create_openended_questions(self, db_session: Session, created_space: Space):
        """Test open-ended questions creation."""
        questions = OpenEndedQuestion(
            title="Test Questions",
            space_id=created_space.id,
            questions=[
                {
                    "id": "q1",
                    "prompt": "Explain photosynthesis.",
                    "rubric": {"criteria": ["accuracy", "completeness"], "weights": [0.5, 0.5]},
                    "wordCount": {"min": 50, "max": 200}
                }
            ]
        )
        
        db_session.add(questions)
        db_session.commit()
        db_session.refresh(questions)
        
        assert questions.id is not None
        assert questions.title == "Test Questions"
        assert questions.space_id == created_space.id
        assert len(questions.questions) == 1
        assert questions.created_at is not None
    
    def test_openended_answer_submission(self, db_session: Session, created_space: Space):
        """Test open-ended answer submission."""
        # Create a user for the answer
        user = User(
            email="test_openended@example.com",
            password_hash=get_password_hash("password123"),
            name="Test User"
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        
        questions = OpenEndedQuestion(
            title="Test Questions",
            space_id=created_space.id,
            questions=[
                {
                    "id": "q1",
                    "prompt": "Explain photosynthesis.",
                    "rubric": {"criteria": ["accuracy"], "weights": [1.0]},
                    "wordCount": {"min": 10, "max": 100}
                }
            ]
        )
    
        db_session.add(questions)
        db_session.commit()
        db_session.refresh(questions)
    
        answer = OpenEndedAnswer(
            open_ended_question_id=questions.id,
            user_id=user.id,
            question_id="q1",
            answer="Photosynthesis converts light to energy.",
            word_count=5,
            grade={"score": 0.8, "feedback": "Good answer"}
        )
        
        db_session.add(answer)
        db_session.commit()
        db_session.refresh(answer)
        
        assert answer.id is not None
        assert answer.open_ended_question_id == questions.id
        assert answer.grade["score"] == 0.8
        assert answer.submitted_at is not None
    
    def test_openended_relationships(self, db_session: Session, created_space: Space):
        """Test open-ended questions relationships."""
        questions = OpenEndedQuestion(
            title="Test Questions",
            space_id=created_space.id,
            questions=[]
        )
        
        db_session.add(questions)
        db_session.commit()
        db_session.refresh(questions)
        
        assert questions.space_id == created_space.id
        assert questions.space == created_space


class TestModelSerialization:
    """Test model serialization methods."""
    
    def test_user_to_dict(self, db_session: Session):
        """Test user serialization to dictionary."""
        user = User(
            email="test_serialization@example.com",
            password_hash=get_password_hash("password123"),
            name="Test User"
        )
        
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        
        # Test that user can be serialized to dict-like structure
        user_dict = {
            'id': str(user.id),
            'email': user.email,
            'name': user.name,
            'created_at': user.created_at.isoformat() if user.created_at else None,
            'updated_at': user.updated_at.isoformat() if user.updated_at else None
        }
        
        assert user_dict["id"] == str(user.id)
        assert user_dict["email"] == user.email
        assert user_dict["name"] == user.name
        assert "password" not in user_dict  # Password should not be included
        assert "created_at" in user_dict
        assert "updated_at" in user_dict
    
    def test_folder_to_dict(self, db_session: Session, created_user: User):
        """Test folder serialization to dictionary."""
        folder = Folder(
            title="Test Folder",
            description="Test description",
            owner_id=created_user.id
        )
        
        db_session.add(folder)
        db_session.commit()
        db_session.refresh(folder)
        
        # Test that folder can be serialized to dict-like structure
        folder_dict = {
            'id': str(folder.id),
            'title': folder.title,
            'description': folder.description,
            'owner_id': str(folder.owner_id),
            'created_at': folder.created_at.isoformat() if folder.created_at else None
        }
        
        assert folder_dict["id"] == str(folder.id)
        assert folder_dict["title"] == folder.title
        assert folder_dict["description"] == folder.description
        assert folder_dict["owner_id"] == str(folder.owner_id)
        assert "created_at" in folder_dict
    
    def test_space_to_dict(self, db_session: Session, created_folder: Folder):
        """Test space serialization to dictionary."""
        space = Space(
            type=SpaceType.chat,
            title="Test Space",
            settings={"theme": "dark"},
            folder_id=created_folder.id
        )
        
        db_session.add(space)
        db_session.commit()
        db_session.refresh(space)
        
        # Test that space can be serialized to dict-like structure
        space_dict = {
            'id': str(space.id),
            'type': space.type.value,
            'title': space.title,
            'settings': space.settings,
            'folder_id': str(space.folder_id),
            'created_at': space.created_at.isoformat() if space.created_at else None
        }
        
        assert space_dict["id"] == str(space.id)
        assert space_dict["type"] == space.type.value
        assert space_dict["title"] == space.title
        assert space_dict["settings"] == space.settings
        assert space_dict["folder_id"] == str(space.folder_id)
        assert "created_at" in space_dict


class TestModelConstraints:
    """Test model constraints and validations."""
    
    def test_user_email_format(self, db_session: Session):
        """Test user email format validation."""
        # This would typically be handled by Pydantic validation
        # Here we test database-level constraints
        user = User(
            email="invalid-email",  # Invalid email format
            password_hash=get_password_hash("password123"),
            name="Test User"
        )
        
        db_session.add(user)
        # Should not raise an error as email format validation is typically at API level
        db_session.commit()
    
    def test_folder_title_length(self, db_session: Session, created_user: User):
        """Test folder title length constraint."""
        # Create a very long title
        long_title = "A" * 300  # Exceeds typical 255 character limit
        
        folder = Folder(
            title=long_title,
            description="Test description",
            owner_id=created_user.id
        )
        
        db_session.add(folder)
        with pytest.raises(IntegrityError):
            db_session.commit()
    
    def test_file_size_constraint(self, db_session: Session, created_folder: Folder):
        """Test file size constraint."""
        file = File(
            name="test.txt",
            mime_type="text/plain",
            size=-1,  # Negative size
            path="/uploads/test.txt",
            text_content="Test content",
            folder_id=created_folder.id
        )
        
        db_session.add(file)
        with pytest.raises(IntegrityError):
            db_session.commit() 