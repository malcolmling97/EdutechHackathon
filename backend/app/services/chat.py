"""
Chat service for managing chat messages and conversations.

Handles:
- Creating and storing chat messages
- Retrieving message history with pagination
- Message deletion and cleanup
- Space access validation
- File source citation management

Note: AI integration placeholder - actual AI responses would be implemented
by the AI/ML Engineer in a separate service layer.
"""
import uuid
from typing import List, Optional, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import desc, and_
from fastapi import HTTPException, status

from app.models.chat_message import ChatMessage, MessageRole
from app.models.space import Space, SpaceType
from app.models.folder import Folder
from app.models.file import File
from app.schemas.chat import MessageRequest, MessageResponse, MessageSource


class ChatService:
    """Service for managing chat messages and conversations."""
    
    def __init__(self, db: Session):
        """Initialize the chat service with database session."""
        self.db = db
    
    def send_message(
        self, 
        space_id: uuid.UUID, 
        message_request: MessageRequest, 
        user_id: uuid.UUID
    ) -> List[MessageResponse]:
        """
        Send a user message and generate AI response.
        
        Args:
            space_id: UUID of the space to send message to
            message_request: Message content and metadata
            user_id: ID of the user sending the message
            
        Returns:
            List of MessageResponse objects (user message + AI response)
            
        Raises:
            HTTPException: If space not found, access denied, or invalid space type
        """
        # Validate space access and type
        space = self._validate_space_access(space_id, user_id)
        
        # Ensure the space is a chat space
        if space.type != SpaceType.chat:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "error": {
                        "code": "INVALID_SPACE_TYPE",
                        "message": "Messages can only be sent in chat spaces",
                        "details": {"space_type": space.type.value}
                    }
                }
            )
        
        # Create user message
        user_message = ChatMessage(
            space_id=space_id,
            role=MessageRole.user,
            content=message_request.content,
            sources=[]  # User messages don't have sources
        )
        
        self.db.add(user_message)
        self.db.flush()  # Flush to get ID but don't commit yet
        
        # Generate AI response (placeholder for AI/ML Engineer implementation)
        assistant_message = self._generate_ai_response(
            space_id=space_id,
            user_message_content=message_request.content,
            conversation_history=self._get_recent_messages(space_id, limit=10)
        )
        
        self.db.add(assistant_message)
        self.db.commit()
        
        # Refresh objects to get updated fields
        self.db.refresh(user_message)
        self.db.refresh(assistant_message)
        
        # Convert to response format
        return [
            self._message_to_response(user_message),
            self._message_to_response(assistant_message)
        ]
    
    def get_message_history(
        self, 
        space_id: uuid.UUID, 
        user_id: uuid.UUID,
        page: int = 1,
        limit: int = 20
    ) -> Dict[str, Any]:
        """
        Get paginated message history for a space.
        
        Args:
            space_id: UUID of the space
            user_id: ID of the requesting user
            page: Page number (1-based)
            limit: Number of messages per page
            
        Returns:
            Dictionary with 'data' (messages) and 'meta' (pagination info)
            
        Raises:
            HTTPException: If space not found or access denied
        """
        # Validate space access
        self._validate_space_access(space_id, user_id)
        
        # Calculate offset
        offset = (page - 1) * limit
        
        # Get total count
        total = self.db.query(ChatMessage).filter(
            ChatMessage.space_id == space_id
        ).count()
        
        # Get messages (ordered by creation time, newest first)
        messages = self.db.query(ChatMessage).filter(
            ChatMessage.space_id == space_id
        ).order_by(desc(ChatMessage.created_at)).offset(offset).limit(limit).all()
        
        # Convert to response format
        message_responses = [self._message_to_response(msg) for msg in messages]
        
        return {
            "data": message_responses,
            "meta": {
                "page": page,
                "limit": limit,
                "total": total
            }
        }
    
    def delete_message(self, message_id: uuid.UUID, user_id: uuid.UUID) -> None:
        """
        Delete a specific message.
        
        Args:
            message_id: UUID of the message to delete
            user_id: ID of the requesting user
            
        Raises:
            HTTPException: If message not found or access denied
        """
        # Get message
        message = self.db.query(ChatMessage).filter(
            ChatMessage.id == message_id
        ).first()
        
        if not message:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "error": {
                        "code": "NOT_FOUND",
                        "message": "Message not found",
                        "details": None
                    }
                }
            )
        
        # Validate space access (user can only delete messages in their spaces)
        self._validate_space_access(message.space_id, user_id)
        
        # Delete the message
        self.db.delete(message)
        self.db.commit()
    
    def _validate_space_access(self, space_id: uuid.UUID, user_id: uuid.UUID) -> Space:
        """
        Validate that user has access to the space.
        
        Args:
            space_id: UUID of the space
            user_id: ID of the user
            
        Returns:
            Space object if access is valid
            
        Raises:
            HTTPException: If space not found or access denied
        """
        try:
            space_uuid = uuid.UUID(str(space_id))
        except (ValueError, TypeError):
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
        
        # Get space with folder relationship
        space = self.db.query(Space).join(Folder).filter(
            and_(
                Space.id == space_uuid,
                Space.deleted_at.is_(None),
                Folder.deleted_at.is_(None)
            )
        ).first()
        
        if not space:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "error": {
                        "code": "NOT_FOUND",
                        "message": "Space not found",
                        "details": None
                    }
                }
            )
        
        # Check if user owns the folder containing this space
        if space.folder.owner_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "error": {
                        "code": "FORBIDDEN",
                        "message": "You don't have permission to access this space",
                        "details": None
                    }
                }
            )
        
        return space
    
    def _get_recent_messages(self, space_id: uuid.UUID, limit: int = 10) -> List[ChatMessage]:
        """
        Get recent messages from the space for context.
        
        Args:
            space_id: UUID of the space
            limit: Number of recent messages to retrieve
            
        Returns:
            List of recent ChatMessage objects
        """
        return self.db.query(ChatMessage).filter(
            ChatMessage.space_id == space_id
        ).order_by(desc(ChatMessage.created_at)).limit(limit).all()
    
    def _generate_ai_response(
        self, 
        space_id: uuid.UUID,
        user_message_content: str,
        conversation_history: List[ChatMessage]
    ) -> ChatMessage:
        """
        Generate AI response to user message.
        
        This is a placeholder implementation. The actual AI integration
        would be implemented by the AI/ML Engineer.
        
        Args:
            space_id: UUID of the space
            user_message_content: Content of the user's message
            conversation_history: Recent conversation context
            
        Returns:
            ChatMessage object with AI response
        """
        # Placeholder AI response
        ai_content = self._create_placeholder_response(user_message_content)
        
        # Get relevant files for source citations (placeholder)
        sources = self._get_relevant_sources(space_id, user_message_content)
        
        return ChatMessage(
            space_id=space_id,
            role=MessageRole.assistant,
            content=ai_content,
            sources=sources
        )
    
    def _create_placeholder_response(self, user_message: str) -> str:
        """
        Create a placeholder AI response.
        
        In the actual implementation, this would be replaced with
        real AI/ML processing.
        
        Args:
            user_message: The user's message content
            
        Returns:
            Placeholder response string
        """
        # Simple placeholder responses based on keywords
        message_lower = user_message.lower()
        
        if any(word in message_lower for word in ["photosynthesis", "plant", "chlorophyll"]):
            return ("Photosynthesis is the process by which plants convert light energy into "
                   "chemical energy using chlorophyll. This process involves light-dependent "
                   "and light-independent reactions that produce glucose and oxygen.")
        
        elif any(word in message_lower for word in ["hello", "hi", "greeting"]):
            return ("Hello! I'm here to help you with your questions about the uploaded "
                   "documents. What would you like to know?")
        
        elif any(word in message_lower for word in ["summarize", "summary", "key points"]):
            return ("Based on the uploaded documents, here are the key points: "
                   "1. Important concepts and definitions, "
                   "2. Main processes and mechanisms, "
                   "3. Practical applications and examples.")
        
        else:
            return ("I understand you're asking about the content in your uploaded documents. "
                   "While I can help answer questions based on those materials, I need more "
                   "specific information to provide a detailed response. Could you clarify "
                   "what particular aspect you'd like me to explain?")
    
    def _get_relevant_sources(self, space_id: uuid.UUID, user_message: str) -> List[Dict[str, Any]]:
        """
        Get relevant file sources for citations.
        
        This is a placeholder for source citation logic.
        The actual implementation would use vector search or similar
        techniques to find relevant document sections.
        
        Args:
            space_id: UUID of the space
            user_message: The user's message content
            
        Returns:
            List of source citation dictionaries
        """
        # Get files from the folder containing this space
        space = self.db.query(Space).filter(Space.id == space_id).first()
        if not space:
            return []
        
        files = self.db.query(File).filter(
            File.folder_id == space.folder_id
        ).limit(3).all()  # Limit to first 3 files as example
        
        # Create placeholder source citations
        sources = []
        for file in files:
            # In a real implementation, this would determine relevant pages/sections
            sources.append({
                "fileId": str(file.id),
                "page": 1 if file.mime_type == "application/pdf" else None
            })
        
        return sources
    
    def _message_to_response(self, message: ChatMessage) -> MessageResponse:
        """
        Convert ChatMessage model to MessageResponse schema.
        
        Args:
            message: ChatMessage database object
            
        Returns:
            MessageResponse object
        """
        # Convert sources to MessageSource objects
        sources = []
        for source in message.sources:
            sources.append(MessageSource(
                fileId=source["fileId"],
                page=source.get("page")
            ))
        
        return MessageResponse(
            id=str(message.id),
            spaceId=str(message.space_id),
            role=message.role.value,
            content=message.content,
            sources=sources,
            createdAt=message.created_at
        ) 