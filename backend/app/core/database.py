"""
Database configuration and session management.

Sets up SQLAlchemy engine, session maker, and base model.
"""
import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.config import settings


# Create data directory if it doesn't exist
os.makedirs("data", exist_ok=True)

# Create SQLAlchemy engine
engine = create_engine(
    settings.database_url,
    connect_args={"check_same_thread": False} if "sqlite" in settings.database_url else {},
    poolclass=StaticPool if "sqlite" in settings.database_url else None,
)

# Create session maker
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Test database setup
TEST_DATABASE_URL = "sqlite:///./test_data/test_edutech.db"
test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

# Create declarative base for models
Base = declarative_base()


def get_db():
    """
    Database dependency for FastAPI.
    
    Yields a database session and ensures it's properly closed.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_tables():
    """
    Create all database tables.
    """
    # Import models to register them with SQLAlchemy
    from app.models import user, folder, space, file, chat_message
    
    Base.metadata.create_all(bind=engine)


def drop_tables():
    """
    Drop all database tables.
    """
    Base.metadata.drop_all(bind=engine)