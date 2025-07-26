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
from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from fastapi.testclient import TestClient

# Add the app directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.main import app
from app.core.database import Base, get_db
from app.models.user import User
from app.api import deps
from app.models.folder import Folder
from app.models.space import Space
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


@pytest.fixture
def db_session(test_db) -> Generator[Session, None, None]:
    """Create a fresh database session for each test."""
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_db)
    session = TestingSessionLocal()
    
    # Set the test session for the dependency override
    deps._test_db_session = session
    
    try:
        yield session
    finally:
        session.close()
        deps._test_db_session = None # Clear the test session


@pytest.fixture(autouse=True)
def clear_token_blacklist():
    """Clear the in-memory token blacklist before each test."""
    from app.core.security import token_blacklist
    token_blacklist.clear()


@pytest.fixture
def client(db_session) -> Generator[TestClient, None, None]:
    """Create a test client with dependency overrides."""
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
    """Sample user registration data."""
    import random
    import string
    random_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
    return {
        "email": f"test_{random_suffix}@example.com",
        "password": "password123",
        "name": "Test User"
    }


@pytest.fixture
def sample_user_2_data():
    """Second sample user registration data."""
    import random
    import string
    random_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
    return {
        "email": f"test2_{random_suffix}@example.com",
        "password": "password456",
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
def auth_headers(created_user):
    """Create authentication headers with JWT token."""
    token = create_access_token(str(created_user.id))
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def sample_folder_data():
    """Sample folder data."""
    return {
        "title": "Test Folder",
        "description": "A test folder description"
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