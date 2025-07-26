"""
Chat endpoint tests for EdutechHackathon API.

Tests all chat message endpoints according to the API specification:
- POST /spaces/{spaceId}/messages - Send user message & get AI response
- GET /spaces/{spaceId}/messages - Get message history (paginated)
- DELETE /messages/{id} - Remove single message

According to API_SPECIFICATION.md:
- Chat messages have id, spaceId, role (user|assistant), content, sources, createdAt
- Sources contain fileId and page references for citations
- Supports streaming responses with Server-Sent Events
- Pagination with ?page=1&limit=20 parameters
"""
import pytest
import json
from datetime import datetime
from fastapi import status
from fastapi.testclient import TestClient
from uuid import uuid4


class TestChatMessages:
    """Test chat message endpoints."""
    
    def test_send_user_message_success(self, client: TestClient, auth_headers, chat_space):
        """Test sending a user message and receiving AI response."""
        message_data = {
            "content": "Explain the process of photosynthesis",
            "role": "user"
        }
        
        response = client.post(
            f"/api/v1/spaces/{chat_space.id}/messages",
            json=message_data,
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_201_CREATED
        
        data = response.json()
        assert "data" in data
        
        # Should return both user message and assistant response
        messages = data["data"] if isinstance(data["data"], list) else [data["data"]]
        
        # User message
        user_message = messages[0] if len(messages) > 0 else data["data"]
        assert user_message["role"] == "user"
        assert user_message["content"] == message_data["content"]
        assert user_message["spaceId"] == str(chat_space.id)
        assert "id" in user_message
        assert "createdAt" in user_message
        
        # If assistant response is included
        if len(messages) > 1:
            assistant_message = messages[1]
            assert assistant_message["role"] == "assistant"
            assert isinstance(assistant_message["content"], str)
            assert len(assistant_message["content"]) > 0
            assert assistant_message["spaceId"] == str(chat_space.id)
    
    def test_send_user_message_with_file_context(self, client: TestClient, auth_headers, chat_space, uploaded_file):
        """Test sending a message that should reference uploaded files."""
        message_data = {
            "content": "What are the key points from the uploaded document?",
            "role": "user"
        }
        
        response = client.post(
            f"/api/v1/spaces/{chat_space.id}/messages",
            json=message_data,
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_201_CREATED
        
        data = response.json()
        assert "data" in data
        
        # Check if sources are included in response (for file citations)
        messages = data["data"] if isinstance(data["data"], list) else [data["data"]]
        for message in messages:
            if message["role"] == "assistant" and "sources" in message:
                assert isinstance(message["sources"], list)
                for source in message["sources"]:
                    assert "fileId" in source
                    assert "page" in source or source["page"] is None
    
    def test_send_message_streaming_response(self, client: TestClient, auth_headers, chat_space):
        """Test streaming response for chat messages."""
        message_data = {
            "content": "Tell me about machine learning",
            "role": "user"
        }
        
        # Test with streaming enabled
        response = client.post(
            f"/api/v1/spaces/{chat_space.id}/messages?stream=true",
            json=message_data,
            headers=auth_headers
        )
        
        # For now, we'll check that the endpoint accepts the stream parameter
        # In a real implementation, this would use Server-Sent Events
        assert response.status_code in [status.HTTP_201_CREATED, status.HTTP_200_OK]
    
    def test_send_message_invalid_space(self, client: TestClient, auth_headers):
        """Test sending message to non-existent space."""
        fake_space_id = str(uuid4())
        message_data = {
            "content": "Test message",
            "role": "user"
        }
        
        response = client.post(
            f"/api/v1/spaces/{fake_space_id}/messages",
            json=message_data,
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        
        data = response.json()
        assert "error" in data
        assert data["error"]["code"] == "NOT_FOUND"
    
    def test_send_message_unauthorized_space(self, client: TestClient, auth_headers, other_user_chat_space):
        """Test sending message to space user doesn't own."""
        message_data = {
            "content": "Test message",
            "role": "user"
        }
        
        response = client.post(
            f"/api/v1/spaces/{other_user_chat_space.id}/messages",
            json=message_data,
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
        
        data = response.json()
        assert "error" in data
        assert data["error"]["code"] == "FORBIDDEN"
    
    def test_send_message_invalid_role(self, client: TestClient, auth_headers, chat_space):
        """Test sending message with invalid role."""
        message_data = {
            "content": "Test message",
            "role": "invalid_role"
        }
        
        response = client.post(
            f"/api/v1/spaces/{chat_space.id}/messages",
            json=message_data,
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_send_empty_message(self, client: TestClient, auth_headers, chat_space):
        """Test sending empty message content."""
        message_data = {
            "content": "",
            "role": "user"
        }
        
        response = client.post(
            f"/api/v1/spaces/{chat_space.id}/messages",
            json=message_data,
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_send_message_without_auth(self, client: TestClient, chat_space):
        """Test sending message without authentication."""
        message_data = {
            "content": "Test message",
            "role": "user"
        }
        
        response = client.post(
            f"/api/v1/spaces/{chat_space.id}/messages",
            json=message_data
        )
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestMessageHistory:
    """Test message history retrieval endpoints."""
    
    def test_get_message_history_empty(self, client: TestClient, auth_headers, chat_space):
        """Test getting message history for space with no messages."""
        response = client.get(
            f"/api/v1/spaces/{chat_space.id}/messages",
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert "data" in data
        assert "meta" in data
        assert data["data"] == []
        assert data["meta"]["total"] == 0
        assert data["meta"]["page"] == 1
        assert data["meta"]["limit"] == 20
    
    def test_get_message_history_with_messages(self, client: TestClient, auth_headers, chat_space_with_messages):
        """Test getting message history for space with existing messages."""
        response = client.get(
            f"/api/v1/spaces/{chat_space_with_messages.id}/messages",
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert "data" in data
        assert "meta" in data
        assert len(data["data"]) > 0
        assert data["meta"]["total"] > 0
        
        # Verify message structure
        for message in data["data"]:
            assert "id" in message
            assert "spaceId" in message
            assert "role" in message
            assert "content" in message
            assert "createdAt" in message
            assert message["role"] in ["user", "assistant"]
            assert message["spaceId"] == str(chat_space_with_messages.id)
    
    def test_get_message_history_pagination(self, client: TestClient, auth_headers, chat_space_with_many_messages):
        """Test message history pagination."""
        # Test first page
        response = client.get(
            f"/api/v1/spaces/{chat_space_with_many_messages.id}/messages?page=1&limit=5",
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert len(data["data"]) <= 5
        assert data["meta"]["page"] == 1
        assert data["meta"]["limit"] == 5
        assert data["meta"]["total"] >= 5
        
        # Test second page if there are enough messages
        if data["meta"]["total"] > 5:
            response2 = client.get(
                f"/api/v1/spaces/{chat_space_with_many_messages.id}/messages?page=2&limit=5",
                headers=auth_headers
            )
            
            assert response2.status_code == status.HTTP_200_OK
            data2 = response2.json()
            assert data2["meta"]["page"] == 2
            
            # Messages should be different between pages
            page1_ids = {msg["id"] for msg in data["data"]}
            page2_ids = {msg["id"] for msg in data2["data"]}
            assert page1_ids.isdisjoint(page2_ids)
    
    def test_get_message_history_ordering(self, client: TestClient, auth_headers, chat_space_with_messages):
        """Test that messages are returned in chronological order (newest first)."""
        response = client.get(
            f"/api/v1/spaces/{chat_space_with_messages.id}/messages",
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        messages = data["data"]
        
        if len(messages) > 1:
            # Parse timestamps and verify they're in descending order (newest first)
            timestamps = [
                datetime.fromisoformat(msg["createdAt"].replace("Z", "+00:00"))
                for msg in messages
            ]
            
            for i in range(len(timestamps) - 1):
                assert timestamps[i] >= timestamps[i + 1], "Messages should be ordered newest first"
    
    def test_get_message_history_invalid_space(self, client: TestClient, auth_headers):
        """Test getting message history for non-existent space."""
        fake_space_id = str(uuid4())
        
        response = client.get(
            f"/api/v1/spaces/{fake_space_id}/messages",
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        
        data = response.json()
        assert "error" in data
        assert data["error"]["code"] == "NOT_FOUND"
    
    def test_get_message_history_unauthorized_space(self, client: TestClient, auth_headers, other_user_chat_space):
        """Test getting message history for space user doesn't own."""
        response = client.get(
            f"/api/v1/spaces/{other_user_chat_space.id}/messages",
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
        
        data = response.json()
        assert "error" in data
        assert data["error"]["code"] == "FORBIDDEN"
    
    def test_get_message_history_invalid_pagination(self, client: TestClient, auth_headers, chat_space):
        """Test message history with invalid pagination parameters."""
        # Test negative page
        response = client.get(
            f"/api/v1/spaces/{chat_space.id}/messages?page=-1",
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        
        # Test zero page
        response = client.get(
            f"/api/v1/spaces/{chat_space.id}/messages?page=0",
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        
        # Test invalid limit (too high)
        response = client.get(
            f"/api/v1/spaces/{chat_space.id}/messages?limit=1000",
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_get_message_history_without_auth(self, client: TestClient, chat_space):
        """Test getting message history without authentication."""
        response = client.get(f"/api/v1/spaces/{chat_space.id}/messages")
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestMessageDeletion:
    """Test message deletion endpoints."""
    
    def test_delete_message_success(self, client: TestClient, auth_headers, user_message):
        """Test successful message deletion."""
        response = client.delete(
            f"/api/v1/messages/{user_message.id}",
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_204_NO_CONTENT
        
        # Verify message is deleted by trying to access message history
        # (This assumes we can check the space's messages to verify deletion)
        space_id = user_message.space_id
        history_response = client.get(
            f"/api/v1/spaces/{space_id}/messages",
            headers=auth_headers
        )
        
        if history_response.status_code == status.HTTP_200_OK:
            data = history_response.json()
            message_ids = [msg["id"] for msg in data["data"]]
            assert str(user_message.id) not in message_ids
    
    def test_delete_message_not_found(self, client: TestClient, auth_headers):
        """Test deleting non-existent message."""
        fake_message_id = str(uuid4())
        
        response = client.delete(
            f"/api/v1/messages/{fake_message_id}",
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        
        data = response.json()
        assert "error" in data
        assert data["error"]["code"] == "NOT_FOUND"
    
    def test_delete_message_unauthorized(self, client: TestClient, auth_headers, other_user_message):
        """Test deleting message from another user."""
        response = client.delete(
            f"/api/v1/messages/{other_user_message.id}",
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
        
        data = response.json()
        assert "error" in data
        assert data["error"]["code"] == "FORBIDDEN"
    
    def test_delete_message_invalid_id(self, client: TestClient, auth_headers):
        """Test deleting message with invalid ID format."""
        response = client.delete(
            "/api/v1/messages/invalid-id",
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_delete_message_without_auth(self, client: TestClient, user_message):
        """Test deleting message without authentication."""
        response = client.delete(f"/api/v1/messages/{user_message.id}")
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestMessageValidation:
    """Test message content validation and business rules."""
    
    def test_message_content_length_limits(self, client: TestClient, auth_headers, chat_space):
        """Test message content length validation."""
        # Test very long message (assuming there's a limit)
        long_content = "a" * 10000  # 10k characters
        message_data = {
            "content": long_content,
            "role": "user"
        }
        
        response = client.post(
            f"/api/v1/spaces/{chat_space.id}/messages",
            json=message_data,
            headers=auth_headers
        )
        
        # This should either succeed or return validation error
        assert response.status_code in [
            status.HTTP_201_CREATED, 
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            status.HTTP_400_BAD_REQUEST
        ]
    
    def test_message_role_validation(self, client: TestClient, auth_headers, chat_space):
        """Test that only 'user' role is accepted for new messages."""
        message_data = {
            "content": "Test message",
            "role": "assistant"  # Users shouldn't be able to create assistant messages
        }
        
        response = client.post(
            f"/api/v1/spaces/{chat_space.id}/messages",
            json=message_data,
            headers=auth_headers
        )
        
        # Should reject assistant role from users
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_message_in_non_chat_space(self, client: TestClient, auth_headers, quiz_space):
        """Test sending message to non-chat space type."""
        message_data = {
            "content": "Test message",
            "role": "user"
        }
        
        response = client.post(
            f"/api/v1/spaces/{quiz_space.id}/messages",
            json=message_data,
            headers=auth_headers
        )
        
        # Should reject messages in non-chat spaces
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        
        data = response.json()
        assert "error" in data
        assert "chat" in data["error"]["message"].lower()


class TestMessageSources:
    """Test message source citations and file references."""
    
    def test_message_with_file_sources(self, client: TestClient, auth_headers, chat_space_with_files):
        """Test that AI responses include file source citations."""
        message_data = {
            "content": "What information is available in the uploaded files?",
            "role": "user"
        }
        
        response = client.post(
            f"/api/v1/spaces/{chat_space_with_files.id}/messages",
            json=message_data,
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_201_CREATED
        
        data = response.json()
        messages = data["data"] if isinstance(data["data"], list) else [data["data"]]
        
        # Look for assistant message with sources
        for message in messages:
            if message["role"] == "assistant" and "sources" in message:
                sources = message["sources"]
                assert isinstance(sources, list)
                
                for source in sources:
                    assert "fileId" in source
                    assert isinstance(source["fileId"], str)
                    # Page can be null for non-paginated files
                    assert "page" in source
                    if source["page"] is not None:
                        assert isinstance(source["page"], int)
                        assert source["page"] > 0
    
    def test_message_sources_validation(self, client: TestClient, auth_headers, chat_space):
        """Test that source references are properly validated."""
        # This test would verify that only valid file IDs are included in sources
        # and that the user has access to those files
        message_data = {
            "content": "Test question about files",
            "role": "user"
        }
        
        response = client.post(
            f"/api/v1/spaces/{chat_space.id}/messages",
            json=message_data,
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_201_CREATED
        # Sources validation would be handled in the AI service layer 