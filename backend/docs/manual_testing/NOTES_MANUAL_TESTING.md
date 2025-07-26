# Notes Management Manual Testing Guide

This guide provides step-by-step instructions for manually testing the Notes API endpoints using curl commands. The Notes functionality allows users to generate AI-powered notes from uploaded files within notes-type spaces.

## Prerequisites

1. **Backend server running**: Ensure the FastAPI server is running on `http://localhost:8000`
2. **Environment setup**: Backend should be properly configured with database
3. **Test data**: You'll need a user account, folder, notes space, and uploaded files

## Authentication Setup

All Notes endpoints require authentication. First, register and login to get your JWT token:

### 1. Register a Test User

```bash
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "notes-test@example.com",
    "password": "testpassword123",
    "name": "Notes Test User"
  }'
```

**Expected Response:**
```json
{
  "data": {
    "user": {
      "id": "user-uuid",
      "email": "notes-test@example.com",
      "name": "Notes Test User",
      "created_at": "2025-01-15T10:30:00Z"
    },
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
  }
}
```

### 2. Set Environment Variables

```bash
export TOKEN="your-jwt-token-here"
export USER_ID="your-user-id-here"
```

## Test Data Setup

### 3. Create a Folder

```bash
curl -X POST "http://localhost:8000/api/v1/folders" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -H "X-User-Id: $USER_ID" \
  -d '{
    "title": "Biology Study Materials",
    "description": "Folder for biology course materials"
  }'
```

**Save the folder ID from the response:**
```bash
export FOLDER_ID="folder-uuid-here"
```

### 4. Create a Notes Space

```bash
curl -X POST "http://localhost:8000/api/v1/folders/$FOLDER_ID/spaces" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -H "X-User-Id: $USER_ID" \
  -d '{
    "type": "notes",
    "title": "Biology Notes Space",
    "settings": {}
  }'
```

**Save the space ID from the response:**
```bash
export NOTES_SPACE_ID="space-uuid-here"
```

### 5. Upload Test Files

Create test files and upload them:

```bash
# Create a sample text file
echo "Photosynthesis is the process by which plants convert light energy into chemical energy. This process occurs in the chloroplasts and involves two main stages: light-dependent reactions and the Calvin cycle." > biology_content.txt

# Upload the file
curl -X POST "http://localhost:8000/api/v1/files/upload" \
  -H "Authorization: Bearer $TOKEN" \
  -H "X-User-Id: $USER_ID" \
  -F "folder_id=$FOLDER_ID" \
  -F "files=@biology_content.txt"
```

**Save the file ID from the response:**
```bash
export FILE_ID="file-uuid-here"
```

## Notes API Testing

### 6. Generate Notes (POST /spaces/{spaceId}/notes)

Test the core notes generation functionality:

#### 6.1 Basic Notes Generation

```bash
curl -X POST "http://localhost:8000/api/v1/spaces/$NOTES_SPACE_ID/notes" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -H "X-User-Id: $USER_ID" \
  -d '{
    "file_ids": ["'$FILE_ID'"],
    "format": "markdown"
  }'
```

**Expected Response (201 Created):**
```json
{
  "data": {
    "id": "note-uuid",
    "spaceId": "space-uuid",
    "format": "markdown",
    "content": "# Generated Notes\n\n## Summary\n\nThese notes were generated from 1 files: biology_content.txt\n\n## Key Points\n\nBased on the analysis of 183 characters of content, here are the main points:\n\n### Important Concepts\n- **File Analysis**: Content extracted from multiple sources\n- **Information Synthesis**: Key information identified and organized\n- **Structured Format**: Notes formatted for easy reading\n\n### Details\nThe analysis covered content from the following files:\n\n1. **biology_content.txt** (text/plain)\n   - Preview: Photosynthesis is the process by which plants convert light energy into chemical energy. This process...\n\n### Conclusion\nThis is mock-generated content. Actual AI generation will be implemented by the AI/ML Engineer.",
    "createdAt": "2025-01-15T10:30:00Z",
    "updatedAt": "2025-01-15T10:30:00Z"
  }
}
```

**Save the note ID:**
```bash
export NOTE_ID="note-uuid-here"
```

#### 6.2 Generate Notes with Bullet Format

```bash
curl -X POST "http://localhost:8000/api/v1/spaces/$NOTES_SPACE_ID/notes" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -H "X-User-Id: $USER_ID" \
  -d '{
    "file_ids": ["'$FILE_ID'"],
    "format": "bullet"
  }'
```

**Expected Response (201 Created):** Similar to above but with bullet-point formatting.

#### 6.3 Test Error Cases

**Invalid Space Type:**
```bash
# First create a chat space
curl -X POST "http://localhost:8000/api/v1/folders/$FOLDER_ID/spaces" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -H "X-User-Id: $USER_ID" \
  -d '{
    "type": "chat",
    "title": "Chat Space",
    "settings": {}
  }'

# Try to generate notes in chat space (should fail)
curl -X POST "http://localhost:8000/api/v1/spaces/CHAT_SPACE_ID/notes" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -H "X-User-Id: $USER_ID" \
  -d '{
    "file_ids": ["'$FILE_ID'"],
    "format": "markdown"
  }'
```

**Expected Response (400 Bad Request):**
```json
{
  "error": {
    "code": "INVALID_SPACE_TYPE",
    "message": "Space type must be 'notes', got 'chat'",
    "details": {
      "space_type": "chat",
      "expected": "notes"
    }
  }
}
```

**Empty File List:**
```bash
curl -X POST "http://localhost:8000/api/v1/spaces/$NOTES_SPACE_ID/notes" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -H "X-User-Id: $USER_ID" \
  -d '{
    "file_ids": [],
    "format": "markdown"
  }'
```

**Expected Response (422 Unprocessable Entity):**
```json
{
  "detail": [
    {
      "type": "too_short",
      "loc": ["body", "file_ids"],
      "msg": "List should have at least 1 item after validation, not 0",
      "input": []
    }
  ]
}
```

### 7. List Notes (GET /spaces/{spaceId}/notes)

#### 7.1 Basic Notes Listing

```bash
curl -X GET "http://localhost:8000/api/v1/spaces/$NOTES_SPACE_ID/notes" \
  -H "Authorization: Bearer $TOKEN" \
  -H "X-User-Id: $USER_ID"
```

**Expected Response (200 OK):**
```json
{
  "data": [
    {
      "id": "note-uuid",
      "spaceId": "space-uuid",
      "format": "markdown",
      "content": "# Generated Notes...",
      "createdAt": "2025-01-15T10:30:00Z",
      "updatedAt": "2025-01-15T10:30:00Z"
    }
  ],
  "meta": {
    "page": 1,
    "limit": 20,
    "total": 1
  }
}
```

#### 7.2 Test Pagination

```bash
curl -X GET "http://localhost:8000/api/v1/spaces/$NOTES_SPACE_ID/notes?page=1&limit=5" \
  -H "Authorization: Bearer $TOKEN" \
  -H "X-User-Id: $USER_ID"
```

### 8. Get Specific Note (GET /notes/{id})

```bash
curl -X GET "http://localhost:8000/api/v1/notes/$NOTE_ID" \
  -H "Authorization: Bearer $TOKEN" \
  -H "X-User-Id: $USER_ID"
```

**Expected Response (200 OK):**
```json
{
  "data": {
    "id": "note-uuid",
    "spaceId": "space-uuid",
    "format": "markdown",
    "content": "# Generated Notes...",
    "createdAt": "2025-01-15T10:30:00Z",
    "updatedAt": "2025-01-15T10:30:00Z"
  }
}
```

#### 8.1 Test Error Cases

**Nonexistent Note:**
```bash
curl -X GET "http://localhost:8000/api/v1/notes/00000000-0000-0000-0000-000000000000" \
  -H "Authorization: Bearer $TOKEN" \
  -H "X-User-Id: $USER_ID"
```

**Expected Response (404 Not Found):**
```json
{
  "error": {
    "code": "NOTE_NOT_FOUND",
    "message": "Note not found",
    "details": {
      "note_id": "00000000-0000-0000-0000-000000000000"
    }
  }
}
```

### 9. Update Note (PATCH /notes/{id})

#### 9.1 Update Note Content

```bash
curl -X PATCH "http://localhost:8000/api/v1/notes/$NOTE_ID" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -H "X-User-Id: $USER_ID" \
  -d '{
    "content": "# Updated Biology Notes\n\nThis content has been manually updated by the user.\n\n## Key Concepts\n\n- Photosynthesis\n- Chloroplasts\n- Light reactions\n- Calvin cycle"
  }'
```

**Expected Response (200 OK):**
```json
{
  "data": {
    "id": "note-uuid",
    "spaceId": "space-uuid",
    "format": "markdown",
    "content": "# Updated Biology Notes\n\nThis content has been manually updated by the user.\n\n## Key Concepts\n\n- Photosynthesis\n- Chloroplasts\n- Light reactions\n- Calvin cycle",
    "createdAt": "2025-01-15T10:30:00Z",
    "updatedAt": "2025-01-15T10:32:00Z"
  }
}
```

#### 9.2 Test Error Cases

**Empty Content:**
```bash
curl -X PATCH "http://localhost:8000/api/v1/notes/$NOTE_ID" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -H "X-User-Id: $USER_ID" \
  -d '{
    "content": ""
  }'
```

**Expected Response (422 Unprocessable Entity):**
```json
{
  "detail": [
    {
      "type": "value_error",
      "loc": ["body", "content"],
      "msg": "Value error, Content cannot be empty or contain only whitespace",
      "input": ""
    }
  ]
}
```

### 10. Delete Note (DELETE /notes/{id})

```bash
curl -X DELETE "http://localhost:8000/api/v1/notes/$NOTE_ID" \
  -H "Authorization: Bearer $TOKEN" \
  -H "X-User-Id: $USER_ID"
```

**Expected Response (204 No Content):** Empty response body.

#### 10.1 Verify Deletion

```bash
curl -X GET "http://localhost:8000/api/v1/notes/$NOTE_ID" \
  -H "Authorization: Bearer $TOKEN" \
  -H "X-User-Id: $USER_ID"
```

**Expected Response (404 Not Found):**
```json
{
  "error": {
    "code": "NOTE_NOT_FOUND",
    "message": "Note not found",
    "details": {
      "note_id": "note-uuid"
    }
  }
}
```

## Complete Workflow Test

### 11. End-to-End Testing

Test the complete workflow in sequence:

```bash
# 1. Generate new note
NOTE_RESPONSE=$(curl -s -X POST "http://localhost:8000/api/v1/spaces/$NOTES_SPACE_ID/notes" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -H "X-User-Id: $USER_ID" \
  -d '{
    "file_ids": ["'$FILE_ID'"],
    "format": "markdown"
  }')

# Extract note ID
NEW_NOTE_ID=$(echo $NOTE_RESPONSE | jq -r '.data.id')
echo "Created note: $NEW_NOTE_ID"

# 2. List notes (should show 1)
curl -s -X GET "http://localhost:8000/api/v1/spaces/$NOTES_SPACE_ID/notes" \
  -H "Authorization: Bearer $TOKEN" \
  -H "X-User-Id: $USER_ID" | jq '.meta.total'

# 3. Get the specific note
curl -s -X GET "http://localhost:8000/api/v1/notes/$NEW_NOTE_ID" \
  -H "Authorization: Bearer $TOKEN" \
  -H "X-User-Id: $USER_ID" | jq '.data.content' | head -n 3

# 4. Update the note
curl -s -X PATCH "http://localhost:8000/api/v1/notes/$NEW_NOTE_ID" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -H "X-User-Id: $USER_ID" \
  -d '{
    "content": "# Final Updated Content\n\nThis note has been updated successfully."
  }' | jq '.data.content'

# 5. Delete the note
curl -s -X DELETE "http://localhost:8000/api/v1/notes/$NEW_NOTE_ID" \
  -H "Authorization: Bearer $TOKEN" \
  -H "X-User-Id: $USER_ID"

# 6. Verify deletion (should return 404)
curl -s -X GET "http://localhost:8000/api/v1/notes/$NEW_NOTE_ID" \
  -H "Authorization: Bearer $TOKEN" \
  -H "X-User-Id: $USER_ID" | jq '.error.code'
```

## Authentication and Permission Testing

### 12. Unauthorized Access Tests

#### 12.1 No Authentication Token

```bash
curl -X GET "http://localhost:8000/api/v1/spaces/$NOTES_SPACE_ID/notes"
```

**Expected Response (401 Unauthorized):**
```json
{
  "detail": "Not authenticated"
}
```

#### 12.2 Access Other User's Notes

Create a second user and try to access the first user's notes:

```bash
# Register second user
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "notes-test-2@example.com",
    "password": "testpassword123",
    "name": "Notes Test User 2"
  }'

# Set second user's token
export TOKEN_2="second-user-jwt-token"
export USER_ID_2="second-user-id"

# Try to access first user's notes (should fail)
curl -X GET "http://localhost:8000/api/v1/spaces/$NOTES_SPACE_ID/notes" \
  -H "Authorization: Bearer $TOKEN_2" \
  -H "X-User-Id: $USER_ID_2"
```

**Expected Response (403 Forbidden):**
```json
{
  "error": {
    "code": "FORBIDDEN",
    "message": "You do not have permission to access this space",
    "details": null
  }
}
```

## Testing Notes Integration with Spaces

### 13. Space Deletion Cascade Test

Verify that deleting a space also deletes all associated notes:

```bash
# 1. Create notes in the space
curl -X POST "http://localhost:8000/api/v1/spaces/$NOTES_SPACE_ID/notes" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -H "X-User-Id: $USER_ID" \
  -d '{
    "file_ids": ["'$FILE_ID'"],
    "format": "markdown"
  }'

# Get the note ID from response and save it
export CASCADE_NOTE_ID="note-id-from-response"

# 2. Verify note exists
curl -X GET "http://localhost:8000/api/v1/notes/$CASCADE_NOTE_ID" \
  -H "Authorization: Bearer $TOKEN" \
  -H "X-User-Id: $USER_ID"

# 3. Delete the space
curl -X DELETE "http://localhost:8000/api/v1/spaces/$NOTES_SPACE_ID" \
  -H "Authorization: Bearer $TOKEN" \
  -H "X-User-Id: $USER_ID"

# 4. Verify note is also deleted (cascade)
curl -X GET "http://localhost:8000/api/v1/notes/$CASCADE_NOTE_ID" \
  -H "Authorization: Bearer $TOKEN" \
  -H "X-User-Id: $USER_ID"
```

**Expected Response:** 404 Not Found (note should be deleted via cascade)

## Error Code Reference

| HTTP Status | Error Code | Description |
|-------------|------------|-------------|
| 400 | `INVALID_SPACE_TYPE` | Space type must be 'notes' |
| 401 | `UNAUTHORIZED` | Invalid or missing authentication token |
| 403 | `FORBIDDEN` | User lacks permission for this resource |
| 404 | `NOTE_NOT_FOUND` | Note does not exist |
| 404 | `SPACE_NOT_FOUND` | Space does not exist |
| 404 | `FILE_NOT_FOUND` | One or more files not found |
| 422 | `INVALID_UUID` | Invalid UUID format |
| 422 | `VALIDATION_ERROR` | Request data validation failed |

## Implementation Notes

### Backend Developer Scope

The current implementation includes:

- ✅ Complete CRUD operations for notes
- ✅ Proper authentication and authorization
- ✅ Input validation and error handling
- ✅ Database relationships and cascade deletion
- ✅ Mock AI content generation

### AI/ML Engineer Integration Points

The mock AI generation will be replaced by:

1. **Real AI Integration**: OpenAI API calls for content generation
2. **Vector Search**: Semantic search using file embeddings
3. **Advanced Prompting**: Context-aware note generation
4. **Content Analysis**: Intelligent topic extraction and organization

The mock implementation provides realistic placeholders that demonstrate the expected input/output format for seamless integration.

## Troubleshooting

### Common Issues

1. **Database Connection**: Ensure SQLite database is accessible
2. **JWT Token Expiry**: Tokens expire after 24 hours, re-login if needed
3. **UUID Format**: Ensure all UUIDs are properly formatted
4. **File Permissions**: Verify file uploads are successful before generating notes
5. **Space Type**: Only 'notes' type spaces can be used for notes generation

### Debugging Commands

```bash
# Check server health
curl http://localhost:8000/health

# View API documentation
open http://localhost:8000/docs

# Check database tables (if using SQLite)
sqlite3 data/edutech.db ".tables"
```

This comprehensive manual testing guide covers all Notes API functionality and ensures proper implementation of the backend developer's responsibilities according to the BACKEND_DATA_FLOWS.md specification. 