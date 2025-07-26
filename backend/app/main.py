"""
Main FastAPI application for the EdutechHackathon backend.

Configures the FastAPI app with:
- Authentication routes
- Folder management routes
- CORS middleware
- Database initialization
- API documentation
"""
import json
from uuid import UUID
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.core.database import create_tables
from app.api.routes import auth, folders, spaces, files, chat, quiz, notes, openended, flashcards, studyguides


class UUIDEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, UUID):
            # if the obj is uuid, we simply return the value of uuid
            return str(obj)
        return super().default(obj)


async def http_exception_handler(request: Request, exc: HTTPException):
    """Custom HTTP exception handler to format errors according to API spec."""
    # If the detail is already a dict with error, return it as is
    if isinstance(exc.detail, dict) and "error" in exc.detail:
        return JSONResponse(
            status_code=exc.status_code,
            content=json.loads(json.dumps(exc.detail, cls=UUIDEncoder))
        )
    
    # If the detail is a dict but doesn't have "error" key, wrap it
    if isinstance(exc.detail, dict):
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": exc.detail
            }
        )
    
    # Otherwise, format as a simple error
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": f"HTTP_{exc.status_code}",
                "message": str(exc.detail),
                "details": None
            }
        }
    )


def create_application() -> FastAPI:
    """
    Create and configure the FastAPI application.
    
    Returns:
        Configured FastAPI application instance
    """
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        docs_url=settings.docs_url,
        redoc_url=settings.redoc_url,
        openapi_url=settings.openapi_url,
        description="""
        # EdutechHackathon API
        
        A modern educational technology platform API built with FastAPI.
        
        ## Features
        
        * **Authentication**: User registration, login, and JWT-based authentication
        * **Folder Management**: Create, update, delete, and organize folders
        * **User Management**: Profile management and user operations
        * **File Processing**: Document upload and text extraction
        * **AI Integration**: Chat, quiz generation, and notes creation
        * **Real-time Features**: Streaming responses and live updates
        
        ## Authentication
        
        This API uses JWT (JSON Web Token) for authentication. Include the token in the Authorization header:
        
        ```
        Authorization: Bearer <your-jwt-token>
        ```
        
        ## Getting Started
        
        1. Register a new user account using `/api/v1/auth/register`
        2. Login to get your JWT token using `/api/v1/auth/login`
        3. Create folders to organize your content using `/api/v1/folders`
        4. Use the token for authenticated endpoints
        
        For detailed API documentation, explore the endpoints below.
        """,
    )
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Add custom exception handler
    app.add_exception_handler(HTTPException, http_exception_handler)
    
    # Include routers
    app.include_router(
        auth.router,
        prefix=f"{settings.api_v1_prefix}/auth",
        tags=["authentication"],
    )
    
    app.include_router(
        folders.router,
        prefix=f"{settings.api_v1_prefix}/folders",
        tags=["folders"],
    )
    
    app.include_router(
        spaces.router,
        prefix=f"{settings.api_v1_prefix}",
        tags=["spaces"],
    )
    
    app.include_router(
        files.router,
        prefix=f"{settings.api_v1_prefix}/files",
        tags=["files"],
    )
    
    app.include_router(
        chat.router,
        prefix=f"{settings.api_v1_prefix}",
        tags=["chat"],
    )
    
    app.include_router(
        quiz.router,
        prefix=f"{settings.api_v1_prefix}",
        tags=["quiz"],
    )
    
    app.include_router(
        notes.router,
        prefix=f"{settings.api_v1_prefix}",
        tags=["notes"],
    )
    
    app.include_router(
        openended.router,
        prefix=f"{settings.api_v1_prefix}",
        tags=["open-ended questions"],
    )

    app.include_router(
        flashcards.router,
        prefix=f"{settings.api_v1_prefix}",
        tags=["flashcards"],
    )

    app.include_router(
        studyguides.router,
        prefix=f"{settings.api_v1_prefix}",
        tags=["study guides"],
    )

    app.include_router(
        spaces.router,
        prefix=f"{settings.api_v1_prefix}",
        tags=["spaces"],
    )
    
    @app.get("/test_route")
    async def test_route():
        return {"message": "Test route successful!"}
    
    return app


# Create the FastAPI app instance
app = create_application()


@app.on_event("startup")
async def startup_event():
    """Initialize the application on startup."""
    # Create database tables
    create_tables()


@app.get("/", tags=["root"])
async def root():
    """Root endpoint with basic API information."""
    return {
        "message": "Welcome to EdutechHackathon API",
        "version": settings.app_version,
        "docs": "/docs",
        "redoc": "/redoc",
        "status": "healthy"
    }


@app.get("/health", tags=["health"])
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "version": settings.app_version,
        "environment": settings.environment
    } 