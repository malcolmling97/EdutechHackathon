"""
Chat message API routes for EdutechHackathon.

Implements chat endpoints:
- POST /spaces/{spaceId}/messages - Send user message & get AI response
- GET /spaces/{spaceId}/messages - Get message history (paginated)
- DELETE /messages/{id} - Remove single message

Follows API_SPECIFICATION.md patterns for:
- Error handling and response formatting
- Authentication and authorization
- Pagination and query parameters
- JSON envelope responses
"""
import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.services.chat import ChatService
from app.schemas.chat import (
    MessageRequest,
    MessageResponse,
    MessageListResponse,
    MessageBatchCreateResponse,
    MessageCreateResponse,
    PaginationParams,
    StreamingParams,
    ErrorResponse
)

router = APIRouter()


@router.post(
    "/spaces/{space_id}/messages",
    response_model=MessageBatchCreateResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Send chat message",
    description="""
    Send a user message to a chat space and receive an AI response.
    
    **Features:**
    - Stores user message in the conversation history
    - Generates contextual AI response based on uploaded files
    - Includes source citations from relevant documents
    - Supports streaming responses (query parameter `stream=true`)
    
    **Requirements:**
    - Space must be of type 'chat'
    - User must own the folder containing the space
    - Message content must not be empty
    
    **Response:**
    Returns both the user message and AI assistant response in the data array.
    The assistant response may include source citations referencing uploaded files.
    
    **Error Codes:**
    - `INVALID_SPACE_TYPE`: Space is not a chat space
    - `NOT_FOUND`: Space does not exist
    - `FORBIDDEN`: User lacks permission to access space
    - `VALIDATION_ERROR`: Invalid message content or format
    """,
    responses={
        201: {
            "description": "Message sent successfully",
            "model": MessageBatchCreateResponse
        },
        400: {
            "description": "Invalid space type or message content",
            "model": ErrorResponse
        },
        401: {
            "description": "Authentication required",
            "model": ErrorResponse
        },
        403: {
            "description": "Access denied to space",
            "model": ErrorResponse
        },
        404: {
            "description": "Space not found",
            "model": ErrorResponse
        },
        422: {
            "description": "Validation error",
            "model": ErrorResponse
        }
    }
)
async def send_message(
    space_id: str,
    message_request: MessageRequest,
    stream: Optional[bool] = Query(False, description="Enable streaming response"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Send a message to a chat space and get AI response."""
    try:
        space_uuid = uuid.UUID(space_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "error": {
                    "code": "VALIDATION_ERROR",
                    "message": "Invalid space ID format",
                    "details": None
                }
            }
        )
    
    chat_service = ChatService(db)
    
    # For streaming implementation, this would use Server-Sent Events
    # For now, we return the standard response
    if stream:
        # TODO: Implement Server-Sent Events streaming
        # This would be handled by the AI/ML Engineer
        pass
    
    messages = chat_service.send_message(
        space_id=space_uuid,
        message_request=message_request,
        user_id=current_user.id
    )
    
    return MessageBatchCreateResponse(data=messages)


@router.get(
    "/spaces/{space_id}/messages",
    response_model=MessageListResponse,
    summary="Get message history",
    description="""
    Retrieve paginated message history for a chat space.
    
    **Features:**
    - Returns messages in chronological order (newest first)
    - Supports pagination with page and limit parameters
    - Includes message sources and citations
    - Filters to only show messages from the specified space
    
    **Pagination:**
    - Default: page=1, limit=20
    - Maximum limit: 100 messages per page
    - Returns total count for client-side pagination
    
    **Response Format:**
    ```json
    {
      "data": [...messages...],
      "meta": {
        "page": 1,
        "limit": 20,
        "total": 45
      }
    }
    ```
    
    **Error Codes:**
    - `NOT_FOUND`: Space does not exist
    - `FORBIDDEN`: User lacks permission to access space
    - `VALIDATION_ERROR`: Invalid pagination parameters
    """,
    responses={
        200: {
            "description": "Message history retrieved successfully",
            "model": MessageListResponse
        },
        401: {
            "description": "Authentication required",
            "model": ErrorResponse
        },
        403: {
            "description": "Access denied to space",
            "model": ErrorResponse
        },
        404: {
            "description": "Space not found",
            "model": ErrorResponse
        },
        422: {
            "description": "Invalid pagination parameters",
            "model": ErrorResponse
        }
    }
)
async def get_message_history(
    space_id: str,
    page: int = Query(1, ge=1, description="Page number (1-based)"),
    limit: int = Query(20, ge=1, le=100, description="Messages per page (max 100)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get paginated message history for a space."""
    try:
        space_uuid = uuid.UUID(space_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "error": {
                    "code": "VALIDATION_ERROR",
                    "message": "Invalid space ID format",
                    "details": None
                }
            }
        )
    
    chat_service = ChatService(db)
    
    result = chat_service.get_message_history(
        space_id=space_uuid,
        user_id=current_user.id,
        page=page,
        limit=limit
    )
    
    return MessageListResponse(**result)


@router.delete(
    "/messages/{message_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete message",
    description="""
    Delete a specific chat message.
    
    **Requirements:**
    - User must own the space containing the message
    - Message must exist and be accessible
    
    **Behavior:**
    - Permanently removes the message from the conversation
    - Does not affect other messages in the conversation
    - Returns 204 No Content on successful deletion
    
    **Error Codes:**
    - `NOT_FOUND`: Message does not exist
    - `FORBIDDEN`: User lacks permission to delete message
    - `VALIDATION_ERROR`: Invalid message ID format
    """,
    responses={
        204: {
            "description": "Message deleted successfully"
        },
        401: {
            "description": "Authentication required",
            "model": ErrorResponse
        },
        403: {
            "description": "Access denied to message",
            "model": ErrorResponse
        },
        404: {
            "description": "Message not found",
            "model": ErrorResponse
        },
        422: {
            "description": "Invalid message ID format",
            "model": ErrorResponse
        }
    }
)
async def delete_message(
    message_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a specific message."""
    try:
        message_uuid = uuid.UUID(message_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "error": {
                    "code": "VALIDATION_ERROR",
                    "message": "Invalid message ID format",
                    "details": None
                }
            }
        )
    
    chat_service = ChatService(db)
    
    chat_service.delete_message(
        message_id=message_uuid,
        user_id=current_user.id
    )
    
    # Return 204 No Content (no response body) 