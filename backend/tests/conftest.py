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