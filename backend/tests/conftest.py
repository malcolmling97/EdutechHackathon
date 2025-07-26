"""
Pytest configuration and shared fixtures for EdutechHackathon backend tests.

Provides:
- Test database setup and teardown
- FastAPI test client
- Authentication fixtures
- Sample data factories
"""
import os
import sys
import pytest
import tempfile
import uuid
from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from fastapi.testclient import TestClient
from datetime import datetime

# Add the app directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.main import app
from app.core.database import Base
from app.api.deps import get_db
from app.models.user import User
from app.api import deps
from app.models.folder import Folder
from app.models.space import Space, SpaceType
from app.models.file import File
from app.core.security import get_password_hash, create_access_token


@pytest.fixture(scope="function")
def test_db():
    """Create a temporary test database."""
    # Create a temporary file for the test database
    db_file = tempfile.NamedTemporaryFile(delete=False)
    db_file.close()
    
    # Create test database engine
    engine = create_engine(f"sqlite:///{db_file.name}", echo=False)
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    yield engine
    
    # Cleanup
    Base.metadata.drop_all(bind=engine)
    os.unlink(db_file.name)


@pytest.fixture(scope="function")
def db_session(test_db):
    """Create a database session for testing."""
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_db)
    session = SessionLocal()
    
    yield session
    
    session.close()


@pytest.fixture(scope="function")
def client(db_session):
    """Create a test client with database dependency override."""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()


@pytest.fixture
def sample_user_data():
    """Sample user data for testing."""
    return {
        "email": "test@example.com",
        "password": "testpassword123",
        "name": "Test User"
    }


@pytest.fixture
def sample_user_data_2():
    """Second sample user data for testing."""
    return {
        "email": "test2@example.com",
        "password": "testpassword123",
        "name": "Test User 2"
    }


@pytest.fixture
def created_user(db_session, sample_user_data):
    """Create a user in the database for testing."""
    user = User(
        email=sample_user_data["email"],
        name=sample_user_data["name"],
        password_hash=get_password_hash(sample_user_data["password"])
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def created_user_2(db_session, sample_user_data_2):
    """Create a second user in the database for testing."""
    user = User(
        email=sample_user_data_2["email"],
        name=sample_user_data_2["name"],
        password_hash=get_password_hash(sample_user_data_2["password"])
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def auth_headers(created_user):
    """Generate authentication headers for testing."""
    token = create_access_token(subject=str(created_user.id))
    return {
        "Authorization": f"Bearer {token}",
        "X-User-Id": str(created_user.id)
    }


@pytest.fixture
def auth_headers_2(created_user_2):
    """Generate authentication headers for second user."""
    token = create_access_token(subject=str(created_user_2.id))
    return {
        "Authorization": f"Bearer {token}",
        "X-User-Id": str(created_user_2.id)
    }


@pytest.fixture
def sample_folder_data():
    """Sample folder data for testing."""
    return {
        "title": "Test Folder",
        "description": "A test folder for unit testing"
    }


@pytest.fixture
def sample_folder_data_2():
    """Second sample folder data for testing."""
    return {
        "title": "Second Test Folder",
        "description": "Another test folder for unit testing"
    }


@pytest.fixture
def created_folder(db_session, created_user, sample_folder_data):
    """Create a folder in the database for testing."""
    folder = Folder(
        title=sample_folder_data["title"],
        description=sample_folder_data["description"],
        owner_id=created_user.id
    )
    db_session.add(folder)
    db_session.commit()
    db_session.refresh(folder)
    return folder


@pytest.fixture
def created_folder_2(db_session, created_user_2, sample_folder_data_2):
    """Create a folder for second user in the database for testing."""
    folder = Folder(
        title=sample_folder_data_2["title"],
        description=sample_folder_data_2["description"],
        owner_id=created_user_2.id
    )
    db_session.add(folder)
    db_session.commit()
    db_session.refresh(folder)
    return folder


@pytest.fixture
def sample_space_data():
    """Sample space data."""
    return {
        "type": "chat",
        "title": "Test Chat Space",
        "settings": {}
    }


@pytest.fixture
def created_space(db_session, created_folder, sample_space_data):
    """Create a space in the database for testing."""
    space = Space(
        type=sample_space_data["type"],
        title=sample_space_data["title"],
        settings=sample_space_data["settings"],
        folder_id=created_folder.id
    )
    db_session.add(space)
    db_session.commit()
    db_session.refresh(space)
    return space


@pytest.fixture
def sample_file_content():
    """Sample file content for testing."""
    return b"This is test file content for upload testing."


@pytest.fixture
def temp_test_file(sample_file_content):
    """Create a temporary test file."""
    with tempfile.NamedTemporaryFile(delete=False, suffix=".txt") as f:
        f.write(sample_file_content)
        f.flush()
        yield f.name
    
    # Cleanup
    os.unlink(f.name)


# ===== CHAT-SPECIFIC FIXTURES =====

@pytest.fixture
def chat_space(db_session, created_folder):
    """Create a chat space for testing."""
    space = Space(
        type=SpaceType.chat,
        title="Test Chat Space",
        settings={},
        folder_id=created_folder.id
    )
    db_session.add(space)
    db_session.commit()
    db_session.refresh(space)
    return space


@pytest.fixture
def quiz_space(db_session, created_folder):
    """Create a quiz space for testing."""
    space = Space(
        type=SpaceType.quiz,
        title="Test Quiz Space",
        settings={},
        folder_id=created_folder.id
    )
    db_session.add(space)
    db_session.commit()
    db_session.refresh(space)
    return space


@pytest.fixture
def other_user_chat_space(db_session, created_folder_2):
    """Create a chat space owned by another user."""
    space = Space(
        type=SpaceType.chat,
        title="Other User Chat Space",
        settings={},
        folder_id=created_folder_2.id
    )
    db_session.add(space)
    db_session.commit()
    db_session.refresh(space)
    return space


@pytest.fixture
def uploaded_file(db_session, created_folder):
    """Create an uploaded file for testing."""
    file = File(
        name="test_document.txt",
        mime_type="text/plain",
        size=1024,
        path="/uploads/test_document.txt",
        text_content="This is sample content from an uploaded document for testing.",
        folder_id=created_folder.id
    )
    db_session.add(file)
    db_session.commit()
    db_session.refresh(file)
    return file


@pytest.fixture
def chat_space_with_files(db_session, created_folder, uploaded_file):
    """Create a chat space in a folder that has uploaded files."""
    space = Space(
        type=SpaceType.chat,
        title="Chat Space With Files",
        settings={},
        folder_id=created_folder.id
    )
    db_session.add(space)
    db_session.commit()
    db_session.refresh(space)
    return space


# Chat message fixtures with real ChatMessage model

@pytest.fixture
def user_message(db_session, chat_space):
    """Create a user message for testing."""
    from app.models.chat_message import ChatMessage, MessageRole
    
    message = ChatMessage(
        space_id=chat_space.id,
        role=MessageRole.user,
        content="Test user message for deletion testing",
        sources=[]
    )
    db_session.add(message)
    db_session.commit()
    db_session.refresh(message)
    return message


@pytest.fixture
def other_user_message(db_session, other_user_chat_space):
    """Create a message from another user for testing."""
    from app.models.chat_message import ChatMessage, MessageRole
    
    message = ChatMessage(
        space_id=other_user_chat_space.id,
        role=MessageRole.user,
        content="Other user message for authorization testing",
        sources=[]
    )
    db_session.add(message)
    db_session.commit()
    db_session.refresh(message)
    return message


@pytest.fixture
def chat_space_with_messages(db_session, chat_space):
    """Create a chat space with some existing messages."""
    from app.models.chat_message import ChatMessage, MessageRole
    
    # Create a few test messages
    messages = [
        ChatMessage(
            space_id=chat_space.id,
            role=MessageRole.user,
            content="First user message",
            sources=[]
        ),
        ChatMessage(
            space_id=chat_space.id,
            role=MessageRole.assistant,
            content="First assistant response",
            sources=[{"fileId": str(uuid.uuid4()), "page": 1}]
        ),
        ChatMessage(
            space_id=chat_space.id,
            role=MessageRole.user,
            content="Second user message",
            sources=[]
        )
    ]
    
    for message in messages:
        db_session.add(message)
    
    db_session.commit()
    
    for message in messages:
        db_session.refresh(message)
    
    return chat_space


@pytest.fixture
def chat_space_with_many_messages(db_session, chat_space):
    """Create a chat space with many messages for pagination testing."""
    from app.models.chat_message import ChatMessage, MessageRole
    
    # Create 25 messages to test pagination
    messages = []
    for i in range(25):
        user_msg = ChatMessage(
            space_id=chat_space.id,
            role=MessageRole.user,
            content=f"User message {i + 1}",
            sources=[]
        )
        assistant_msg = ChatMessage(
            space_id=chat_space.id,
            role=MessageRole.assistant,
            content=f"Assistant response {i + 1}",
            sources=[{"fileId": str(uuid.uuid4()), "page": i + 1}]
        )
        messages.extend([user_msg, assistant_msg])
    
    for message in messages:
        db_session.add(message)
    
    db_session.commit()
    
    for message in messages:
        db_session.refresh(message)
    
    return chat_space 


@pytest.fixture
def other_user(created_user_2):
    """Alias for created_user_2 to provide other_user for permission testing."""
    return created_user_2


@pytest.fixture
def uploaded_files(test_db, db_session, created_folder):
    """Create sample uploaded files for testing."""
    files = []
    
    # Create sample files with text content
    for i in range(3):
        file = File(
            id=uuid.uuid4(),
            folder_id=created_folder.id,
            name=f"test_file_{i}.pdf",
            mime_type="application/pdf",
            size=1024000 + i * 100000,  # Different sizes
            path=f"test_file_{i}.pdf",
            text_content=f"This is the extracted text content for file {i}. " * 100,
            vector_ids=[],
            created_at=datetime.utcnow()
        )
        files.append(file)
    
    for file in files:
        db_session.add(file)
    
    db_session.commit()
    
    for file in files:
        db_session.refresh(file)
    
    return files


@pytest.fixture  
def other_user_files(test_db, db_session, other_user, other_user_folder):
    """Create files owned by another user for permission testing."""
    files = []
    
    for i in range(2):
        file = File(
            id=uuid.uuid4(),
            folder_id=other_user_folder.id,
            name=f"other_user_file_{i}.pdf",
            mime_type="application/pdf", 
            size=1024000,
            path=f"other_user_file_{i}.pdf",
            text_content=f"Other user's file content {i}.",
            vector_ids=[],
            created_at=datetime.utcnow()
        )
        files.append(file)
    
    for file in files:
        db_session.add(file)
    
    db_session.commit()
    
    for file in files:
        db_session.refresh(file)
    
    return files


@pytest.fixture
def created_quiz(test_db, db_session, created_space, uploaded_files):
    """Create a sample quiz for testing."""
    from app.models.quiz import Quiz
    
    # Sample quiz questions matching the data flows specification
    sample_questions = [
        {
            "id": "q1",
            "type": "mcq",
            "prompt": "What is photosynthesis?",
            "choices": [
                "Process of converting light to chemical energy",
                "Process of cellular respiration", 
                "Process of protein synthesis",
                "Process of cell division"
            ],
            "answer": "A"
        },
        {
            "id": "q2", 
            "type": "tf",
            "prompt": "Chlorophyll is green.",
            "answer": True
        },
        {
            "id": "q3",
            "type": "short_answer",
            "prompt": "Explain the Calvin cycle in 2 sentences.",
            "answer": "The Calvin cycle is the light-independent reaction of photosynthesis. It produces glucose from CO2 using ATP and NADPH."
        }
    ]
    
    quiz = Quiz(
        id=uuid.uuid4(),
        space_id=created_space.id,
        title="Sample Biology Quiz",
        questions=sample_questions,
        file_ids=[str(uploaded_files[0].id), str(uploaded_files[1].id)],
        created_at=datetime.utcnow()
    )
    
    db_session.add(quiz)
    db_session.commit()
    db_session.refresh(quiz)
    
    return quiz


@pytest.fixture
def other_user_quiz(test_db, db_session, other_user_space, other_user_files):
    """Create a quiz owned by another user for permission testing."""
    from app.models.quiz import Quiz
    
    sample_questions = [
        {
            "id": "q1",
            "type": "mcq", 
            "prompt": "What is mitosis?",
            "choices": ["Cell division", "Cell death", "Cell growth", "Cell repair"],
            "answer": "A"
        }
    ]
    
    quiz = Quiz(
        id=uuid.uuid4(),
        space_id=other_user_space.id,
        title="Other User's Quiz", 
        questions=sample_questions,
        file_ids=[str(other_user_files[0].id)],
        created_at=datetime.utcnow()
    )
    
    db_session.add(quiz)
    db_session.commit() 
    db_session.refresh(quiz)
    
    return quiz


@pytest.fixture
def other_user_space(test_db, db_session, other_user_folder):
    """Create a space owned by another user for permission testing."""
    space = Space(
        id=uuid.uuid4(),
        folder_id=other_user_folder.id,
        type=SpaceType.quiz,
        title="Other User's Quiz Space",
        settings={},
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    
    db_session.add(space)
    db_session.commit()
    db_session.refresh(space)
    
    return space


@pytest.fixture
def other_user_folder(test_db, db_session, other_user):
    """Create a folder owned by another user for permission testing."""
    folder = Folder(
        id=uuid.uuid4(),
        owner_id=other_user.id,
        title="Other User's Folder",
        description="Folder for testing permissions",
        created_at=datetime.utcnow()
    )
    
    db_session.add(folder)
    db_session.commit()
    db_session.refresh(folder)
    
    return folder


# === NOTES TESTING FIXTURES ===

@pytest.fixture
def created_space_notes(test_db, db_session, created_folder):
    """Create a notes-type space for testing."""
    space = Space(
        id=uuid.uuid4(),
        folder_id=created_folder.id,
        type=SpaceType.notes,
        title="Notes Space",
        settings={},
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    
    db_session.add(space)
    db_session.commit()
    db_session.refresh(space)
    
    return space


@pytest.fixture
def created_space_notes_other_user(test_db, db_session, other_user_folder):
    """Create a notes-type space owned by another user for permission testing."""
    space = Space(
        id=uuid.uuid4(),
        folder_id=other_user_folder.id,
        type=SpaceType.notes,
        title="Other User's Notes Space",
        settings={},
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    
    db_session.add(space)
    db_session.commit()
    db_session.refresh(space)
    
    return space


@pytest.fixture
def created_file_2(test_db, db_session, created_folder):
    """Create a second file for testing multi-file operations."""
    file = File(
        id=uuid.uuid4(),
        folder_id=created_folder.id,
        name="test_file_2.pdf",
        mime_type="application/pdf",
        size=2048000,
        path="test_file_2.pdf",
        text_content="This is the second test file with different content. " * 50,
        vector_ids=[],
        created_at=datetime.utcnow()
    )
    
    db_session.add(file)
    db_session.commit()
    db_session.refresh(file)
    
    return file


@pytest.fixture
def created_file_other_user(test_db, db_session, other_user_folder):
    """Create a file owned by another user for permission testing."""
    file = File(
        id=uuid.uuid4(),
        folder_id=other_user_folder.id,
        name="other_user_file.pdf",
        mime_type="application/pdf",
        size=1024000,
        path="other_user_file.pdf",
        text_content="This file belongs to another user and should not be accessible.",
        vector_ids=[],
        created_at=datetime.utcnow()
    )
    
    db_session.add(file)
    db_session.commit()
    db_session.refresh(file)
    
    return file


@pytest.fixture
def created_note(test_db, db_session, created_space_notes):
    """Create a sample note for testing."""
    from app.models.note import Note
    
    note = Note(
        id=uuid.uuid4(),
        space_id=created_space_notes.id,
        format="markdown",
        content="# Sample Notes\n\nThis is a sample note content.\n\n## Key Points\n\n- Point 1\n- Point 2\n- Point 3",
        file_ids=[],
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    
    db_session.add(note)
    db_session.commit()
    db_session.refresh(note)
    
    return note


@pytest.fixture
def created_note_other_user(test_db, db_session, created_space_notes_other_user):
    """Create a note owned by another user for permission testing."""
    from app.models.note import Note
    
    note = Note(
        id=uuid.uuid4(),
        space_id=created_space_notes_other_user.id,
        format="markdown",
        content="# Other User's Notes\n\nThis note belongs to another user.",
        file_ids=[],
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    
    db_session.add(note)
    db_session.commit()
    db_session.refresh(note)
    
    return note


@pytest.fixture
def created_file(test_db, db_session, created_folder):
    """Create a basic file for testing."""
    file = File(
        id=uuid.uuid4(),
        folder_id=created_folder.id,
        name="test_file.pdf",
        mime_type="application/pdf",
        size=1024000,
        path="test_file.pdf",
        text_content="This is test file content for notes generation. " * 100,
        vector_ids=[],
        created_at=datetime.utcnow()
    )
    
    db_session.add(file)
    db_session.commit()
    db_session.refresh(file)
    
    return file


@pytest.fixture
def created_space_openended(test_db, db_session, created_folder):
    """Create a space for open-ended questions testing."""
    from app.models.space import Space, SpaceType
    
    space = Space(
        id=uuid.uuid4(),
        folder_id=created_folder.id,
        type=SpaceType.openended,
        title="Open-ended Questions Space",
        settings={},
        created_at=datetime.utcnow()
    )
    
    db_session.add(space)
    db_session.commit()
    db_session.refresh(space)
    
    return space


@pytest.fixture
def created_space_openended_other_user(test_db, db_session, other_user_folder):
    """Create a space for open-ended questions testing owned by another user."""
    from app.models.space import Space, SpaceType
    
    space = Space(
        id=uuid.uuid4(),
        folder_id=other_user_folder.id,
        type=SpaceType.openended,
        title="Other User's Open-ended Questions Space",
        settings={},
        created_at=datetime.utcnow()
    )
    
    db_session.add(space)
    db_session.commit()
    db_session.refresh(space)
    
    return space


@pytest.fixture
def created_openended(test_db, db_session, created_space_openended, uploaded_files):
    """Create a sample open-ended question set for testing."""
    from app.models.openended import OpenEndedQuestion
    
    openended = OpenEndedQuestion(
        id=uuid.uuid4(),
        space_id=created_space_openended.id,
        title="Sample Essay Questions",
        questions=[
            {
                "id": "q1",
                "prompt": "Explain the process of photosynthesis in detail, including the light-dependent and light-independent reactions.",
                "maxWords": 500,
                "rubric": {
                    "criteria": [
                        {
                            "name": "Understanding of light reactions",
                            "weight": 0.3,
                            "description": "Demonstrates clear understanding of photosystem I and II"
                        },
                        {
                            "name": "Calvin cycle explanation",
                            "weight": 0.3,
                            "description": "Accurately describes the Calvin cycle steps"
                        },
                        {
                            "name": "Overall coherence",
                            "weight": 0.4,
                            "description": "Answer is well-structured and coherent"
                        }
                    ]
                }
            },
            {
                "id": "q2",
                "prompt": "Describe the structure and function of chloroplasts in plant cells.",
                "maxWords": 300,
                "rubric": {
                    "criteria": [
                        {
                            "name": "Structural description",
                            "weight": 0.5,
                            "description": "Accurately describes chloroplast structure"
                        },
                        {
                            "name": "Functional explanation",
                            "weight": 0.5,
                            "description": "Explains chloroplast function clearly"
                        }
                    ]
                }
            }
        ],
        file_ids=[str(uploaded_files[0].id)],
        created_at=datetime.utcnow()
    )
    
    db_session.add(openended)
    db_session.commit()
    db_session.refresh(openended)
    
    return openended


@pytest.fixture
def created_openended_in_space(test_db, db_session, created_space, uploaded_files):
    """Create a sample open-ended question set in a specific space for testing."""
    from app.models.openended import OpenEndedQuestion
    
    openended = OpenEndedQuestion(
        id=uuid.uuid4(),
        space_id=created_space.id,
        title="Sample Essay Questions in Space",
        questions=[
            {
                "id": "q1",
                "prompt": "Explain the process of photosynthesis in detail, including the light-dependent and light-independent reactions.",
                "maxWords": 500,
                "rubric": {
                    "criteria": [
                        {
                            "name": "Understanding of light reactions",
                            "weight": 0.3,
                            "description": "Demonstrates clear understanding of photosystem I and II"
                        },
                        {
                            "name": "Calvin cycle explanation",
                            "weight": 0.3,
                            "description": "Accurately describes the Calvin cycle steps"
                        },
                        {
                            "name": "Overall coherence",
                            "weight": 0.4,
                            "description": "Answer is well-structured and coherent"
                        }
                    ]
                }
            }
        ],
        file_ids=[str(uploaded_files[0].id)],
        created_at=datetime.utcnow()
    )
    
    db_session.add(openended)
    db_session.commit()
    db_session.refresh(openended)
    
    return openended


@pytest.fixture
def other_user_openended(test_db, db_session, created_space_openended_other_user, other_user_files):
    """Create an open-ended question set owned by another user for permission testing."""
    from app.models.openended import OpenEndedQuestion
    
    openended = OpenEndedQuestion(
        id=uuid.uuid4(),
        space_id=created_space_openended_other_user.id,
        title="Other User's Essay Questions",
        questions=[
            {
                "id": "q1",
                "prompt": "Explain a concept from another user's content.",
                "maxWords": 400,
                "rubric": {
                    "criteria": [
                        {
                            "name": "Content understanding",
                            "weight": 1.0,
                            "description": "Demonstrates understanding of the concept"
                        }
                    ]
                }
            }
        ],
        file_ids=[str(other_user_files[0].id)],
        created_at=datetime.utcnow()
    )
    
    db_session.add(openended)
    db_session.commit()
    db_session.refresh(openended)
    
    return openended 