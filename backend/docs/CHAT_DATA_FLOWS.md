# Chat Data Flows Documentation

## Overview

The Chat Data Flows implementation provides a complete chat messaging system within the EdutechHackathon platform. Users can send messages in chat spaces and receive AI-generated responses with source citations from uploaded documents.

## Features

### Core Functionality
- **Message Creation**: Send user messages and receive AI responses
- **Message History**: Retrieve paginated conversation history
- **Message Deletion**: Remove individual messages from conversations
- **Source Citations**: AI responses include references to uploaded files
- **Access Control**: Users can only access messages in their own spaces

### Technical Features
- **Database Integration**: SQLAlchemy models with proper relationships
- **API Validation**: Pydantic schemas for request/response validation
- **Error Handling**: Comprehensive error responses following API specification
- **Pagination**: Efficient message history retrieval with pagination
- **Authentication**: JWT-based user authentication and authorization

## Database Schema

### ChatMessage Model
```sql
CREATE TABLE chat_messages (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    space_id UUID NOT NULL REFERENCES spaces(id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL CHECK (role IN ('user', 'assistant')),
    content TEXT NOT NULL,
    sources JSON NOT NULL DEFAULT '[]',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_chat_messages_space_id ON chat_messages(space_id);
CREATE INDEX idx_chat_messages_created_at ON chat_messages(created_at);
CREATE INDEX idx_chat_messages_role ON chat_messages(role);
```

### Relationships
- **Space → Messages**: One-to-many relationship with cascade delete
- **Message Sources**: JSON array referencing File IDs with optional page numbers

## API Endpoints

### 1. Send Message
**POST** `/api/v1/spaces/{spaceId}/messages`

**Purpose**: Send a user message and receive an AI response

**Request Body**:
```json
{
    "content": "What is photosynthesis?",
    "role": "user"
}
```

**Response**:
```json
{
    "data": [
        {
            "id": "user-message-uuid",
            "spaceId": "space-uuid",
            "role": "user",
            "content": "What is photosynthesis?",
            "sources": [],
            "createdAt": "2025-01-15T10:30:00Z"
        },
        {
            "id": "assistant-message-uuid",
            "spaceId": "space-uuid",
            "role": "assistant",
            "content": "Photosynthesis is the process by which plants convert light energy...",
            "sources": [
                {
                    "fileId": "file-uuid",
                    "page": 12
                }
            ],
            "createdAt": "2025-01-15T10:30:05Z"
        }
    ]
}
```

### 2. Get Message History
**GET** `/api/v1/spaces/{spaceId}/messages?page=1&limit=20`

**Purpose**: Retrieve paginated message history for a space

**Query Parameters**:
- `page`: Page number (1-based, default: 1)
- `limit`: Messages per page (1-100, default: 20)

**Response**:
```json
{
    "data": [
        {
            "id": "message-uuid",
            "spaceId": "space-uuid",
            "role": "user",
            "content": "Message content",
            "sources": [],
            "createdAt": "2025-01-15T10:30:00Z"
        }
    ],
    "meta": {
        "page": 1,
        "limit": 20,
        "total": 45
    }
}
```

### 3. Delete Message
**DELETE** `/api/v1/messages/{messageId}`

**Purpose**: Delete a specific message

**Response**: `204 No Content`

## Service Layer Architecture

### ChatService Class
The `ChatService` class handles all chat-related business logic:

#### Key Methods:
1. **`send_message()`**: Creates user message and generates AI response
2. **`get_message_history()`**: Retrieves paginated message history
3. **`delete_message()`**: Deletes a specific message
4. **`_validate_space_access()`**: Ensures user has permission to access space
5. **`_generate_ai_response()`**: Placeholder for AI response generation

#### AI Integration Placeholder
The current implementation includes placeholder AI responses. The AI/ML Engineer will integrate actual AI services in the `_generate_ai_response()` method.

## Manual Testing Instructions

### Prerequisites
1. **Environment Setup**:
   ```bash
   cd EdutechHackathon/backend
   cp .env.example .env
   # Edit .env with your configuration
   ```

2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Start the Server**:
   ```bash
   python3 -m uvicorn app.main:app --reload --port 8000
   ```

### Test Scenarios

#### 1. User Registration and Authentication
```bash
# Register a user
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "testuser@example.com",
    "password": "testpassword123",
    "name": "Test User"
  }'

# Save the token from the response for subsequent requests
export TOKEN="your-jwt-token-here"
```

#### 2. Create Folder and Chat Space
```bash
# Create a folder
curl -X POST "http://localhost:8000/api/v1/folders" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "title": "Test Folder",
    "description": "Folder for chat testing"
  }'

# Save the folder ID
export FOLDER_ID="folder-uuid-from-response"

# Create a chat space
curl -X POST "http://localhost:8000/api/v1/folders/$FOLDER_ID/spaces" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "type": "chat",
    "title": "Test Chat Space"
  }'

# Save the space ID
export SPACE_ID="space-uuid-from-response"
```

#### 3. Upload a Test File (Optional)
```bash
# Upload a test file to provide context for AI responses
curl -X POST "http://localhost:8000/api/v1/files/upload" \
  -H "Authorization: Bearer $TOKEN" \
  -F "folderId=$FOLDER_ID" \
  -F "files=@test_document.txt"
```

#### 4. Send Messages and Test Chat Functionality

**Send a User Message**:
```bash
curl -X POST "http://localhost:8000/api/v1/spaces/$SPACE_ID/messages" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "content": "Hello, can you help me understand photosynthesis?",
    "role": "user"
  }'
```

**Expected Response**:
- Status: 201 Created
- Body: Array containing both user message and AI response
- AI response should include placeholder content about photosynthesis

**Get Message History**:
```bash
curl -X GET "http://localhost:8000/api/v1/spaces/$SPACE_ID/messages?page=1&limit=10" \
  -H "Authorization: Bearer $TOKEN"
```

**Expected Response**:
- Status: 200 OK
- Body: Paginated list of messages with metadata
- Messages ordered newest first

**Send Another Message**:
```bash
curl -X POST "http://localhost:8000/api/v1/spaces/$SPACE_ID/messages" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "content": "Can you summarize the key points from the uploaded document?",
    "role": "user"
  }'
```

**Get Updated History**:
```bash
curl -X GET "http://localhost:8000/api/v1/spaces/$SPACE_ID/messages" \
  -H "Authorization: Bearer $TOKEN"
```

#### 5. Test Message Deletion

**Get Message ID from History**:
```bash
# From the message history response, copy a message ID
export MESSAGE_ID="message-uuid-to-delete"

# Delete the message
curl -X DELETE "http://localhost:8000/api/v1/messages/$MESSAGE_ID" \
  -H "Authorization: Bearer $TOKEN"
```

**Expected Response**:
- Status: 204 No Content
- No response body

**Verify Deletion**:
```bash
curl -X GET "http://localhost:8000/api/v1/spaces/$SPACE_ID/messages" \
  -H "Authorization: Bearer $TOKEN"
```

#### 6. Test Error Scenarios

**Send Message to Non-existent Space**:
```bash
curl -X POST "http://localhost:8000/api/v1/spaces/00000000-0000-0000-0000-000000000000/messages" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "content": "Test message",
    "role": "user"
  }'
```

**Expected Response**:
- Status: 404 Not Found
- Error code: "NOT_FOUND"

**Send Message to Non-chat Space**:
```bash
# First create a quiz space
curl -X POST "http://localhost:8000/api/v1/folders/$FOLDER_ID/spaces" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "type": "quiz",
    "title": "Test Quiz Space"
  }'

export QUIZ_SPACE_ID="quiz-space-uuid-from-response"

# Try to send message to quiz space
curl -X POST "http://localhost:8000/api/v1/spaces/$QUIZ_SPACE_ID/messages" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "content": "Test message",
    "role": "user"
  }'
```

**Expected Response**:
- Status: 400 Bad Request
- Error code: "INVALID_SPACE_TYPE"

**Send Empty Message**:
```bash
curl -X POST "http://localhost:8000/api/v1/spaces/$SPACE_ID/messages" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "content": "",
    "role": "user"
  }'
```

**Expected Response**:
- Status: 422 Unprocessable Entity
- Validation error about empty content

**Test Pagination Limits**:
```bash
# Test invalid page number
curl -X GET "http://localhost:8000/api/v1/spaces/$SPACE_ID/messages?page=0" \
  -H "Authorization: Bearer $TOKEN"

# Test limit too high
curl -X GET "http://localhost:8000/api/v1/spaces/$SPACE_ID/messages?limit=1000" \
  -H "Authorization: Bearer $TOKEN"
```

**Expected Response**:
- Status: 422 Unprocessable Entity
- Validation errors for invalid parameters

### Testing Without Authentication

**Try to send message without token**:
```bash
curl -X POST "http://localhost:8000/api/v1/spaces/$SPACE_ID/messages" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "Test message",
    "role": "user"
  }'
```

**Expected Response**:
- Status: 401 Unauthorized

## Verification Checklist

### ✅ API Endpoints
- [ ] POST `/spaces/{spaceId}/messages` creates user message and AI response
- [ ] GET `/spaces/{spaceId}/messages` returns paginated message history
- [ ] DELETE `/messages/{id}` removes specific message
- [ ] All endpoints require authentication
- [ ] Proper error responses for invalid requests

### ✅ Database Operations
- [ ] Messages are stored with correct relationships
- [ ] Space access validation works
- [ ] Message deletion cascades properly
- [ ] Pagination queries are efficient

### ✅ Business Logic
- [ ] Only chat spaces accept messages
- [ ] AI responses include placeholder content
- [ ] Source citations are included when relevant
- [ ] Message ordering (newest first) works correctly

### ✅ Error Handling
- [ ] Invalid space IDs return 404
- [ ] Unauthorized access returns 403
- [ ] Validation errors return 422
- [ ] Non-chat spaces reject messages

### ✅ Response Format
- [ ] All responses follow API specification envelope pattern
- [ ] Message timestamps are ISO-8601 formatted
- [ ] Source citations include fileId and optional page
- [ ] Pagination metadata is accurate

## Integration Notes

### For AI/ML Engineer
The current implementation provides placeholder AI responses in the `ChatService._generate_ai_response()` method. To integrate actual AI functionality:

1. **Replace Placeholder Logic**: Update `_create_placeholder_response()` with actual AI service calls
2. **Implement Source Citation**: Enhance `_get_relevant_sources()` to use vector search or similar techniques
3. **Add Streaming Support**: Implement Server-Sent Events in the chat route for real-time responses
4. **Context Management**: Use conversation history and uploaded files for contextual responses

### For Frontend Developer
The chat API provides:
- **Real-time Messaging**: Send messages and receive immediate responses
- **History Management**: Retrieve and display conversation history
- **Error Handling**: Comprehensive error responses for user feedback
- **Pagination**: Efficient loading of message history
- **Source Display**: File citations for AI response verification

## Performance Considerations

### Database Optimization
- **Indexes**: Created on `space_id`, `created_at`, and `role` for efficient queries
- **Pagination**: Uses OFFSET/LIMIT for memory-efficient history retrieval
- **Cascade Deletes**: Automatic cleanup when spaces are deleted

### API Optimization
- **Lazy Loading**: Messages are loaded on-demand with pagination
- **Response Size**: Only essential message data is included in responses
- **Caching Opportunities**: Message history could be cached for frequently accessed spaces

### Future Enhancements
- **Message Search**: Full-text search across message content
- **Message Editing**: Allow users to edit their messages
- **Thread Management**: Support for conversation threads
- **Real-time Updates**: WebSocket support for live message updates 