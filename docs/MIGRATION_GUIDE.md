# API Migration Guide

This guide helps developers transition from the previous simple API structure to the new comprehensive REST API design.

## Overview of Changes

### Old API Structure
```
/api/chats        → Basic chat endpoints
/api/projects     → Simple project management
/api/quizzes      → Basic quiz functionality
```

### New API Structure
```
/api/v1/auth      → Authentication & user management
/api/v1/folders   → Learning units/folders
/api/v1/spaces    → Chat, quiz, and notes spaces
/api/v1/files     → Document upload and management
/api/v1/messages  → Chat messages with AI responses
/api/v1/quizzes   → Advanced quiz generation
/api/v1/notes     → Notes generation
```

## Key Architectural Changes

### 1. Resource Hierarchy
**Old:** Flat structure with independent resources
**New:** Hierarchical structure with proper relationships

```
Old: Chat → Messages
New: User → Folder → Space → Messages/Quizzes/Notes
                  ↓
                Files
```

### 2. Authentication
**Old:** No authentication specified
**New:** JWT Bearer tokens with user identification

```javascript
// Old
fetch('/api/chats')

// New
fetch('/api/v1/folders', {
  headers: {
    'Authorization': 'Bearer <token>',
    'X-User-Id': '<uuid>',
    'Content-Type': 'application/json'
  }
})
```

### 3. Response Format
**Old:** Direct data responses
**New:** Consistent JSON envelope pattern

```json
// Old
{ "id": "123", "title": "Chat" }

// New
{
  "data": { "id": "123", "title": "Chat" },
  "meta": { "page": 1, "limit": 20, "total": 1 }
}
```

## Migration Mappings

### Chat Functionality

| Old Endpoint | New Endpoint | Notes |
|-------------|-------------|--------|
| `GET /api/chats` | `GET /api/v1/folders/{id}/spaces?type=chat` | Now organized by folder |
| `POST /api/chats` | `POST /api/v1/folders/{id}/spaces` | Requires folder context |
| `GET /api/chats/{id}` | `GET /api/v1/spaces/{id}/messages` | Space-based messages |
| `POST /api/chat/respond` | `POST /api/v1/spaces/{id}/messages` | Streaming support added |
| `DELETE /api/chats/{id}` | `DELETE /api/v1/spaces/{id}` | Space deletion |

### Project → Folder Migration

| Old Endpoint | New Endpoint | Notes |
|-------------|-------------|--------|
| `GET /api/projects` | `GET /api/v1/folders` | Projects are now folders |
| `POST /api/projects` | `POST /api/v1/folders` | Enhanced with descriptions |
| `GET /api/projects/{id}` | `GET /api/v1/folders/{id}` | More detailed response |

### Quiz Enhancement

| Old Endpoint | New Endpoint | Notes |
|-------------|-------------|--------|
| `GET /api/quizzes` | `GET /api/v1/spaces/{id}/quizzes` | Space-scoped quizzes |
| `POST /api/quizzes` | `POST /api/v1/spaces/{id}/quizzes` | File-based generation |
| `GET /api/quizzes/{id}` | `GET /api/v1/quizzes/{id}` | Enhanced with metadata |

## Frontend Code Migration Examples

### 1. Authentication Setup

```javascript
// Old (no auth)
const chatResponse = await fetch('/api/chats');

// New (with auth)
const authHeaders = {
  'Authorization': `Bearer ${token}`,
  'X-User-Id': userId,
  'Content-Type': 'application/json'
};

const foldersResponse = await fetch('/api/v1/folders', {
  headers: authHeaders
});
```

### 2. Chat Creation

```javascript
// Old
const newChat = await fetch('/api/chats', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ title: 'New Chat' })
});

// New
const newChatSpace = await fetch(`/api/v1/folders/${folderId}/spaces`, {
  method: 'POST',
  headers: authHeaders,
  body: JSON.stringify({ 
    type: 'chat',
    title: 'New Chat' 
  })
});
```

### 3. Message Sending

```javascript
// Old
const response = await fetch('/api/chat/respond', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ 
    chatId: '123',
    message: 'Hello' 
  })
});

// New (with streaming)
const response = await fetch(`/api/v1/spaces/${spaceId}/messages?stream=true`, {
  method: 'POST',
  headers: authHeaders,
  body: JSON.stringify({ 
    content: 'Hello',
    role: 'user' 
  })
});

// Handle streaming response
const reader = response.body.getReader();
while (true) {
  const { done, value } = await reader.read();
  if (done) break;
  // Process streaming chunk
}
```

### 4. Quiz Generation

```javascript
// Old
const quiz = await fetch('/api/quizzes', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ 
    title: 'Quiz',
    questions: [...]
  })
});

// New (file-based generation)
const quiz = await fetch(`/api/v1/spaces/${spaceId}/quizzes`, {
  method: 'POST',
  headers: authHeaders,
  body: JSON.stringify({ 
    title: 'Chapter 1 Quiz',
    fileIds: ['file1', 'file2'],
    questionCount: 10,
    questionTypes: ['mcq', 'tf']
  })
});
```

## Response Handling Migration

### Old Response Handling
```javascript
const data = await response.json();
// Direct access to data
console.log(data.id);
```

### New Response Handling
```javascript
const response = await fetch('/api/v1/folders');
const result = await response.json();

// Access through data envelope
const folders = result.data;
const pagination = result.meta;

// Error handling
if (!response.ok) {
  const error = result.error;
  throw new Error(`${error.code}: ${error.message}`);
}
```

## New Features Available

### 1. File Upload and Management
```javascript
// Upload files to a folder
const formData = new FormData();
formData.append('folderId', folderId);
formData.append('files', pdfFile1);
formData.append('files', pdfFile2);

const uploadResponse = await fetch('/api/v1/files/upload', {
  method: 'POST',
  headers: { 'Authorization': `Bearer ${token}` },
  body: formData
});
```

### 2. Notes Generation
```javascript
// Generate notes from uploaded files
const notes = await fetch(`/api/v1/spaces/${spaceId}/notes`, {
  method: 'POST',
  headers: authHeaders,
  body: JSON.stringify({ 
    fileIds: ['file1', 'file2'],
    format: 'markdown'
  })
});
```

### 3. Advanced Search and Filtering
```javascript
// Search with pagination and filtering
const searchResults = await fetch('/api/v1/folders?q=biology&page=1&limit=20', {
  headers: authHeaders
});
```

## Migration Checklist

### Backend Development
- [ ] Implement JWT authentication
- [ ] Create folder management endpoints
- [ ] Build space management system
- [ ] Add file upload and processing
- [ ] Implement streaming chat responses
- [ ] Build quiz generation from files
- [ ] Add notes generation capability
- [ ] Implement proper error handling
- [ ] Add pagination support
- [ ] Create comprehensive logging

### Frontend Development
- [ ] Add authentication state management
- [ ] Update API client with new endpoints
- [ ] Implement folder/space hierarchy UI
- [ ] Add file upload components
- [ ] Update chat interface for streaming
- [ ] Enhance quiz creation workflow
- [ ] Add notes management features
- [ ] Implement error boundary handling
- [ ] Add loading states for async operations
- [ ] Update routing for new structure

### Testing
- [ ] Unit tests for all new endpoints
- [ ] Integration tests for API flows
- [ ] Frontend component tests
- [ ] End-to-end user workflows
- [ ] Performance testing for file uploads
- [ ] Streaming response testing
- [ ] Authentication and authorization testing

## Breaking Changes Summary

1. **All endpoints moved to `/api/v1/`**
2. **Authentication required for all endpoints**
3. **Response format changed to envelope pattern**
4. **Chat functionality now space-based**
5. **Quiz generation now file-based**
6. **New folder hierarchy required**
7. **Streaming support for chat responses**

## Support and Resources

- [Full API Specification](./API_SPECIFICATION.md)
- [Error Codes Reference](./API_SPECIFICATION.md#7-error-codes)
- [Authentication Guide](./API_SPECIFICATION.md#2-authentication--headers)
- [Example Implementations](./API_SPECIFICATION.md#6-example-contracts) 