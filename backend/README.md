# EdutechHackathon Backend

A well-organized, scalable FastAPI backend built with Python following modern software architecture patterns.

## 🏗 **Architecture Overview**

This backend follows a **layered architecture** with clear separation of concerns:

- **Routes**: Handle HTTP requests/responses with automatic validation via Pydantic
- **Services**: Business logic and operations
- **Models**: Data structures and storage using Pydantic models
- **Dependencies**: Authentication, validation, error handling
- **Schemas**: Pydantic models for request/response validation
- **Config**: Centralized configuration management
- **Database**: Repository pattern for data access with SQLAlchemy/SQLite

## 🛠 **Tech Stack**

### **Core Framework & Language**
- **Python 3.9+** - Modern Python with latest features and performance improvements
- **FastAPI 0.104+** - High-performance, modern web framework with automatic API documentation
- **Uvicorn** - Lightning-fast ASGI server for serving FastAPI applications
- **Pydantic 2.0+** - Data validation and serialization using Python type hints

### **Database & ORM**
- **SQLAlchemy 2.0+** - The Python SQL toolkit and Object-Relational Mapping library
- **SQLite** - Lightweight database for development and small deployments
- **PostgreSQL** - Production-ready relational database (optional upgrade)
- **Alembic** - Database migration tool for SQLAlchemy (optional)

### **Authentication & Security**
- **python-jose[cryptography]** - JSON Web Token implementation for Python
- **passlib[bcrypt]** - Password hashing library with bcrypt support
- **python-multipart** - Form data parsing for file uploads
- **cryptography** - Cryptographic recipes and primitives

### **AI/ML Integration**
- **OpenAI API (openai)** - Official OpenAI Python client for GPT models
- **httpx** - Async HTTP client for external API calls
- **tiktoken** - Token counting for OpenAI models (optional)
- **langchain** - Framework for developing AI applications (optional advanced features)

### **File Processing & Storage**
- **PyPDF2** or **pdfplumber** - PDF text extraction and processing
- **python-docx** - Microsoft Word document processing
- **aiofiles** - Async file I/O for Python
- **Pillow (PIL)** - Image processing capabilities (optional)

### **Testing Framework**
- **pytest** - Modern testing framework for Python
- **pytest-asyncio** - Async testing support for pytest
- **httpx** - TestClient for FastAPI integration testing
- **pytest-cov** - Coverage reporting for tests
- **factory-boy** - Test data generation (optional)

### **Development Tools**
- **Black** - Code formatter for Python
- **isort** - Import sorting utility
- **flake8** - Linting and style guide enforcement
- **mypy** - Static type checking for Python
- **pre-commit** - Git hooks for code quality
- **python-dotenv** - Environment variable management

### **Performance & Monitoring**
- **slowapi** - Rate limiting for FastAPI applications
- **prometheus-fastapi-instrumentator** - Metrics collection (optional)
- **structlog** - Structured logging for better observability
- **redis** - Caching and session storage (optional)

### **Deployment & DevOps**
- **Docker** - Containerization for consistent deployments
- **docker-compose** - Multi-container development environment
- **gunicorn** - WSGI HTTP server for production deployments
- **nginx** - Reverse proxy and static file serving (production)

### **Package Management**
- **pip** - Standard Python package installer
- **pip-tools** - Dependency management and pinning
- **Poetry** - Alternative modern dependency management (optional)
- **requirements.txt** - Traditional dependency specification

### **Optional Enhancements**
- **Celery** - Distributed task queue for background jobs
- **Redis** - In-memory data structure store for caching
- **Sentry** - Error tracking and performance monitoring
- **GitHub Actions** - CI/CD pipeline automation
- **Swagger UI** - Interactive API documentation (built into FastAPI)
- **ReDoc** - Alternative API documentation (built into FastAPI)

### **Development Environment**
- **VS Code** - Recommended IDE with Python extensions
- **Python Extension Pack** - Essential VS Code extensions for Python development
- **Thunder Client** or **Postman** - API testing tools
- **Git** - Version control system
- **pyenv** - Python version management (optional)

### **AI Model Integration Options**
- **OpenAI GPT-4** - Primary LLM for chat, quiz generation, and notes
- **OpenAI GPT-3.5-turbo** - Cost-effective alternative for less complex tasks
- **Hugging Face Transformers** - Open-source model alternatives (optional)
- **Anthropic Claude** - Alternative AI provider (optional)

### **File Format Support**
- **PDF** - Portable Document Format processing
- **DOCX** - Microsoft Word document processing
- **TXT** - Plain text file processing
- **MD** - Markdown file processing
- **JSON** - Data interchange format
- **CSV** - Comma-separated values (optional)

### **Database Schema Management**
- **SQLAlchemy Core** - Database schema definition
- **SQLAlchemy ORM** - Object-relational mapping
- **UUID** - Universally unique identifiers for primary keys
- **DateTime** - Timestamp management with timezone support
- **JSON** - JSON field support for flexible data storage

### **API Features**
- **OpenAPI 3.0** - API specification standard
- **JSON Schema** - Request/response validation
- **Server-Sent Events (SSE)** - Real-time streaming for chat responses
- **Multipart Forms** - File upload support
- **CORS** - Cross-origin resource sharing
- **HTTP/2** - Modern HTTP protocol support

This comprehensive tech stack provides a robust, scalable, and modern foundation for building the EdutechHackathon backend with AI capabilities, ensuring high performance, developer productivity, and maintainability.

## 📁 **Project Structure**

```
backend/
├── app/
│   ├── api/
│   │   ├── deps.py                # Dependency injection (auth, db)
│   │   └── routes/                # API route handlers
│   │       ├── auth.py           # Authentication endpoints
│   │       ├── folders.py        # Folder management
│   │       ├── spaces.py         # Space management
│   │       ├── chat.py           # Chat/AI endpoints
│   │       ├── files.py          # File upload/management
│   │       └── health.py         # Health check
│   │
│   ├── core/                      # Core application settings
│   │   ├── config.py             # Configuration management
│   │   ├── security.py           # JWT/password utilities
│   │   └── database.py           # Database configuration
│   │
│   ├── schemas/                   # Pydantic models for validation
│   │   ├── auth.py               # Authentication schemas
│   │   ├── folder.py             # Folder schemas
│   │   ├── space.py              # Space schemas
│   │   ├── chat.py               # Chat/message schemas
│   │   └── common.py             # Common/shared schemas
│   │
│   ├── models/                    # SQLAlchemy database models
│   │   ├── user.py               # User entity
│   │   ├── folder.py             # Folder entity
│   │   ├── space.py              # Space entity
│   │   ├── message.py            # Chat message entity
│   │   └── file.py               # File entity
│   │
│   ├── services/                  # Business logic layer
│   │   ├── auth.py               # Authentication business logic
│   │   ├── ai_service.py         # AI/ML integration (OpenAI, etc.)
│   │   ├── file_service.py       # File processing and text extraction
│   │   └── quiz_service.py       # Quiz generation logic
│   │
│   ├── db/                        # Database layer
│   │   ├── base.py               # Base model class
│   │   ├── session.py            # Database session management
│   │   └── repositories/         # Repository pattern
│   │       └── base.py
│   │
│   ├── utils/                     # Utility functions
│   │   ├── security.py           # Security utilities
│   │   ├── file_processing.py    # File text extraction
│   │   └── validators.py         # Custom validation functions
│   │
│   ├── main.py                    # FastAPI app configuration and startup
│   └── constants.py               # Application constants
│
├── tests/                         # Test organization
│   ├── conftest.py               # Pytest configuration and fixtures
│   ├── test_auth.py              # Authentication tests
│   ├── test_folders.py           # Folder endpoint tests
│   ├── test_spaces.py            # Space endpoint tests
│   ├── test_chat.py              # Chat/AI endpoint tests
│   └── utils/                    # Test utilities
│       └── test_helpers.py       # Test helper functions
│
├── docs/                          # Documentation
│   ├── api/                       # API documentation
│   │   ├── FOLDER_MANUAL_TESTING.md
│   │   └── SPACE_MANUAL_TESTING.md
│   │
│   └── development/               # Development docs
│       ├── BACKEND_DATA_FLOWS.md
│       └── BACKEND_CHECKLIST.md
│
├── data/                          # SQLite database storage
├── uploads/                       # File upload storage
├── requirements.txt               # Python dependencies
├── pyproject.toml                # Project configuration (Poetry/pip)
├── .env.example                  # Environment variables template
└── alembic/                      # Database migrations (optional)
```

## 🚀 **Getting Started**

### Prerequisites
- Python 3.9+ 
- pip or Poetry

### Installation

1. **Create virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   # Or with Poetry:
   poetry install
   ```

3. **Configure environment:**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

4. **Required Environment Variables:**
   ```bash
   JWT_SECRET="your-super-secret-jwt-key-at-least-32-characters"
   PORT=8000                    # Optional, defaults to 8000
   ENVIRONMENT=development      # development | production | test
   DATABASE_URL="sqlite:///./data/edutech.db"
   OPENAI_API_KEY="your-openai-api-key"  # For AI features
   ```

   > 📝 **Note**: For a complete list of all configuration options, see [`docs/development/CONFIGURATION.md`](docs/development/CONFIGURATION.md)

### Development

1. **Start development server:**
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

2. **View API documentation:**
   - Swagger UI: `http://localhost:8000/docs`
   - ReDoc: `http://localhost:8000/redoc`

3. **Run tests:**
   ```bash
   pytest
   # With coverage:
   pytest --cov=app
   ```

4. **Run specific test file:**
   ```bash
   pytest tests/test_auth.py -v
   ```

## 🔧 **Architecture Benefits**

### 1. **Separation of Concerns**
- **Routes**: Handle HTTP concerns with automatic Pydantic validation
- **Services**: Pure business logic, easily testable
- **Models**: SQLAlchemy ORM models for database interaction
- **Schemas**: Pydantic models for request/response validation

### 2. **Configuration Management**
- Centralized configuration using Pydantic Settings
- Environment-specific settings with validation
- Type-safe configuration access

### 3. **Type Safety**
- Full type hints throughout the application
- Pydantic models for automatic validation and serialization
- Better IDE support and error catching

### 4. **Scalability**
- Repository pattern ready for complex database operations
- Service layer for business logic separation
- Modular structure for feature additions
- Async/await support for high-performance concurrent operations

### 5. **Testing**
- Pytest with async support
- Fixture-based test setup
- Integration tests for API endpoints
- Test database isolation

## 📡 **API Endpoints**

### Authentication
- `POST /api/v1/auth/register` - User registration
- `POST /api/v1/auth/login` - User login
- `GET /api/v1/auth/profile` - Get user profile
- `POST /api/v1/auth/logout` - User logout

### Folders
- `GET /api/v1/folders` - List user folders
- `POST /api/v1/folders` - Create folder
- `GET /api/v1/folders/{id}` - Get folder
- `PATCH /api/v1/folders/{id}` - Update folder
- `DELETE /api/v1/folders/{id}` - Delete folder

### Spaces
- `GET /api/v1/folders/{folderId}/spaces` - List spaces in folder
- `POST /api/v1/folders/{folderId}/spaces` - Create space
- `GET /api/v1/spaces/{id}` - Get space
- `PATCH /api/v1/spaces/{id}` - Update space
- `DELETE /api/v1/spaces/{id}` - Delete space

### Chat & AI
- `POST /api/v1/spaces/{spaceId}/messages` - Send message and get AI response
- `GET /api/v1/spaces/{spaceId}/messages` - Get chat history
- `DELETE /api/v1/messages/{id}` - Delete message

### Files
- `POST /api/v1/files/upload` - Upload files
- `GET /api/v1/folders/{folderId}/files` - List files in folder
- `GET /api/v1/files/{id}` - Get file metadata
- `GET /api/v1/files/{id}/content` - Get file content
- `DELETE /api/v1/files/{id}` - Delete file

### Health Check
- `GET /api/v1/health` - API health status

## 🧪 **Testing**

### Test Organization
- **Integration Tests**: Test complete API workflows using TestClient
- **Unit Tests**: Test individual services and utilities
- **Fixtures**: Shared test setup using pytest fixtures

### Running Tests
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_auth.py

# Run tests with output
pytest -v

# Run tests in parallel
pytest -n auto
```

### Manual Testing
See documentation in `/docs/api/` for comprehensive manual testing guides.

## 🛠 **Development Patterns**

### Adding New Features

1. **Define Schemas** (Pydantic models)
   ```python
   # app/schemas/new_entity.py
   from pydantic import BaseModel
   from typing import Optional
   
   class NewEntityCreate(BaseModel):
       name: str
       description: Optional[str] = None
   
   class NewEntityResponse(BaseModel):
       id: str
       name: str
       description: Optional[str]
       created_at: datetime
       
       class Config:
           from_attributes = True
   ```

2. **Create Database Model**
   ```python
   # app/models/new_entity.py
   from sqlalchemy import Column, String, DateTime
   from app.db.base import Base
   
   class NewEntity(Base):
       __tablename__ = "new_entities"
       
       id = Column(String, primary_key=True)
       name = Column(String, nullable=False)
       description = Column(String)
       created_at = Column(DateTime, default=datetime.utcnow)
   ```

3. **Add Service** (for business logic)
   ```python
   # app/services/new_entity.py
   from app.models.new_entity import NewEntity
   from app.schemas.new_entity import NewEntityCreate
   
   class NewEntityService:
       def create(self, db: Session, entity_data: NewEntityCreate) -> NewEntity:
           # Business logic here
           pass
   ```

4. **Create Routes**
   ```python
   # app/api/routes/new_entity.py
   from fastapi import APIRouter, Depends
   from app.api.deps import get_current_user, get_db
   
   router = APIRouter()
   
   @router.post("/", response_model=NewEntityResponse)
   async def create_entity(
       entity: NewEntityCreate,
       db: Session = Depends(get_db),
       current_user: User = Depends(get_current_user)
   ):
       return NewEntityService.create(db, entity)
   ```

5. **Write Tests**
   ```python
   # tests/test_new_entity.py
   def test_create_new_entity(client: TestClient, auth_headers: dict):
       response = client.post("/api/v1/new-entities/", 
                            json={"name": "Test"}, 
                            headers=auth_headers)
       assert response.status_code == 201
   ```

### Error Handling
- FastAPI automatic error handling with Pydantic validation
- Custom exception handlers for business logic errors
- Consistent error response format using HTTPException

### Validation
- Automatic request/response validation with Pydantic
- Custom validators for complex business rules
- Type hints for better development experience

## 🔐 **Security Features**

- JWT-based authentication with python-jose
- Password hashing with passlib and bcrypt
- Token blacklisting for logout
- Automatic request validation with Pydantic
- CORS configuration
- Request size limits
- SQL injection protection with SQLAlchemy ORM

## 📈 **Performance & Monitoring**

- Async/await for high-performance concurrent operations
- Connection pooling with SQLAlchemy
- Structured logging with Python logging
- Health check endpoint
- Graceful shutdown handling
- Request timeout handling

## 🔄 **AI Integration**

### Supported AI Features
- **Chat**: OpenAI GPT integration for conversational AI
- **Quiz Generation**: AI-powered quiz creation from documents
- **Notes Generation**: Automatic note summarization
- **File Processing**: Text extraction from PDF, DOCX, and other formats
- **Streaming Responses**: Server-Sent Events for real-time AI responses

### AI Configuration
```python
# app/core/config.py
class Settings(BaseSettings):
    openai_api_key: str
    ai_model: str = "gpt-4"
    ai_temperature: float = 0.7
    max_tokens: int = 1000
```

## 🐳 **Docker Support**

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## 📚 **Key Dependencies**

- **FastAPI**: Modern, fast web framework
- **Uvicorn**: ASGI server
- **SQLAlchemy**: SQL toolkit and ORM
- **Pydantic**: Data validation using Python type hints
- **python-jose**: JWT token handling
- **passlib**: Password hashing
- **openai**: OpenAI API integration
- **pytest**: Testing framework
- **httpx**: HTTP client for testing

> 📋 **Note**: For specific versions and a complete list of dependencies, see [`requirements.txt`](requirements.txt)

## 📚 **Documentation**

- **API Documentation**: Automatic generation at `/docs` and `/redoc`
- **Development Guides**: `/docs/development/`
- **Configuration Guide**: [`docs/development/CONFIGURATION.md`](docs/development/CONFIGURATION.md)
- **Manual Testing**: Comprehensive guides for each feature
- **Data Flow Documentation**: Detailed API specifications

## 🤝 **Contributing**

1. Follow the established architecture patterns
2. Add type hints to all functions
3. Write tests for new features
4. Update documentation
5. Use Pydantic models for validation
6. Follow PEP 8 style guidelines

---

**Built with ❤️ using FastAPI for the EdutechHackathon** 