# Space Management Manual Testing Guide

This document provides step-by-step manual testing instructions for the Space Management feature using command line tools (curl). All space management functionality has been successfully implemented and tested.

## Prerequisites

1. Ensure the backend server is running:
   ```bash
   cd EdutechHackathon/backend
   python3 -m uvicorn app.main:app --reload --port 8000
   ```

2. The server should be accessible at `http://localhost:8000`
3. API documentation is available at `http://localhost:8000/docs`

## Test Environment Setup

### Step 1: Register a Test User

```bash
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "spacetester@example.com",
    "password": "spacetesting123",
    "name": "Space Tester"
  }'
```

**Expected Response (201 Created):**
```json
{
  "data": {
    "user": {
      "id": "user-uuid-here",
      "email": "spacetester@example.com",
      "name": "Space Tester",
      "created_at": "2025-01-15T10:30:00Z",
      "updated_at": "2025-01-15T10:30:00Z"
    },
    "token": "jwt-token-here"
  }
}
```

**⚠️ Important: Save the JWT token from the response for use in subsequent requests.**

### Step 2: Create a Test Folder

Replace `YOUR_JWT_TOKEN` with the token from Step 1:

```bash
curl -X POST "http://localhost:8000/api/v1/folders" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "title": "Space Testing Folder",
    "description": "Folder for testing space management functionality"
  }'
```

**Expected Response (201 Created):**
```json
{
  "data": {
    "id": "folder-uuid-here",
    "ownerId": "user-uuid-here",
    "title": "Space Testing Folder",
    "description": "Folder for testing space management functionality",
    "createdAt": "2025-01-15T10:31:00Z"
  }
}
```

**⚠️ Important: Save the folder ID for use in space operations.**

## Space Management Testing

Replace `YOUR_JWT_TOKEN` and `FOLDER_ID` with actual values from the setup steps.

### Test 1: List Spaces in Empty Folder

```bash
curl -X GET "http://localhost:8000/api/v1/folders/FOLDER_ID/spaces" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

**Expected Response (200 OK):**
```json
{
  "data": [],
  "meta": {
    "page": 1,
    "limit": 20,
    "total": 0
  }
}
```

### Test 2: Create Chat Space

```bash
curl -X POST "http://localhost:8000/api/v1/folders/FOLDER_ID/spaces" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "type": "chat",
    "title": "My Chat Space",
    "settings": {
      "theme": "dark",
      "notifications": true,
      "autoSave": true
    }
  }'
```

**Expected Response (201 Created):**
```json
{
  "data": {
    "id": "space-uuid-here",
    "folderId": "folder-uuid-here",
    "type": "chat",
    "title": "My Chat Space",
    "settings": {
      "theme": "dark",
      "notifications": true,
      "autoSave": true
    },
    "createdAt": "2025-01-15T10:32:00Z"
  }
}
```

**⚠️ Important: Save the space ID for use in subsequent tests.**

### Test 3: Create Different Space Types

Test all supported space types:

#### Quiz Space
```bash
curl -X POST "http://localhost:8000/api/v1/folders/FOLDER_ID/spaces" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "type": "quiz",
    "title": "Biology Quiz Space",
    "settings": {
      "timeLimit": 60,
      "shuffleQuestions": true,
      "showCorrectAnswers": false
    }
  }'
```

#### Notes Space
```bash
curl -X POST "http://localhost:8000/api/v1/folders/FOLDER_ID/spaces" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "type": "notes",
    "title": "Study Notes Space",
    "settings": {
      "format": "markdown",
      "autoSave": true,
      "version": "v1"
    }
  }'
```

#### Open-ended Questions Space
```bash
curl -X POST "http://localhost:8000/api/v1/folders/FOLDER_ID/spaces" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "type": "openended",
    "title": "Essay Questions Space",
    "settings": {
      "wordLimit": 500,
      "rubricEnabled": true,
      "autoGrade": false
    }
  }'
```

#### Flashcards Space
```bash
curl -X POST "http://localhost:8000/api/v1/folders/FOLDER_ID/spaces" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "type": "flashcards",
    "title": "Vocabulary Flashcards",
    "settings": {
      "cardCount": 25,
      "difficulty": "medium",
      "shuffleCards": true
    }
  }'
```

#### Study Guide Space
```bash
curl -X POST "http://localhost:8000/api/v1/folders/FOLDER_ID/spaces" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "type": "studyguide",
    "title": "Final Exam Study Guide",
    "settings": {
      "deadline": "2025-01-30T09:00:00Z",
      "dailyStudyHours": 2,
      "breakInterval": 25
    }
  }'
```

### Test 4: List All Spaces

```bash
curl -X GET "http://localhost:8000/api/v1/folders/FOLDER_ID/spaces" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

**Expected Response (200 OK):**
```json
{
  "data": [
    {
      "id": "space-uuid-1",
      "folderId": "folder-uuid",
      "type": "studyguide",
      "title": "Final Exam Study Guide",
      "settings": {...},
      "createdAt": "2025-01-15T10:35:00Z"
    },
    // ... more spaces (newest first)
  ],
  "meta": {
    "page": 1,
    "limit": 20,
    "total": 6
  }
}
```

### Test 5: Filter Spaces by Type

```bash
curl -X GET "http://localhost:8000/api/v1/folders/FOLDER_ID/spaces?type=chat" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

**Expected Response (200 OK):**
```json
{
  "data": [
    {
      "id": "space-uuid",
      "folderId": "folder-uuid",
      "type": "chat",
      "title": "My Chat Space",
      "settings": {...},
      "createdAt": "2025-01-15T10:32:00Z"
    }
  ],
  "meta": {
    "page": 1,
    "limit": 20,
    "total": 1
  }
}
```

### Test 6: Pagination

```bash
curl -X GET "http://localhost:8000/api/v1/folders/FOLDER_ID/spaces?page=1&limit=3" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

**Expected Response (200 OK):**
```json
{
  "data": [
    // First 3 spaces
  ],
  "meta": {
    "page": 1,
    "limit": 3,
    "total": 6
  }
}
```

### Test 7: Get Specific Space

Replace `SPACE_ID` with an actual space ID:

```bash
curl -X GET "http://localhost:8000/api/v1/spaces/SPACE_ID" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

**Expected Response (200 OK):**
```json
{
  "data": {
    "id": "space-uuid",
    "folderId": "folder-uuid",
    "type": "chat",
    "title": "My Chat Space",
    "settings": {
      "theme": "dark",
      "notifications": true,
      "autoSave": true
    },
    "createdAt": "2025-01-15T10:32:00Z"
  }
}
```

### Test 8: Update Space

```bash
curl -X PATCH "http://localhost:8000/api/v1/spaces/SPACE_ID" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "title": "Updated Chat Space Title",
    "settings": {
      "theme": "light",
      "notifications": false,
      "autoSave": true,
      "newFeature": "enabled"
    }
  }'
```

**Expected Response (200 OK):**
```json
{
  "data": {
    "id": "space-uuid",
    "folderId": "folder-uuid",
    "type": "chat",
    "title": "Updated Chat Space Title",
    "settings": {
      "theme": "light",
      "notifications": false,
      "autoSave": true,
      "newFeature": "enabled"
    },
    "createdAt": "2025-01-15T10:32:00Z"
  }
}
```

### Test 9: Update Space with Partial Data

```bash
curl -X PATCH "http://localhost:8000/api/v1/spaces/SPACE_ID" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "title": "Only Title Updated"
  }'
```

**Expected Response (200 OK):**
Settings should remain unchanged, only title should be updated.

### Test 10: Delete Space

```bash
curl -X DELETE "http://localhost:8000/api/v1/spaces/SPACE_ID" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

**Expected Response (204 No Content):**
No response body, just 204 status code.

### Test 11: Verify Space Deletion

Try to get the deleted space:

```bash
curl -X GET "http://localhost:8000/api/v1/spaces/SPACE_ID" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

**Expected Response (404 Not Found):**
```json
{
  "error": {
    "code": "SPACE_NOT_FOUND",
    "message": "Space not found or you don't have permission to access it",
    "details": {
      "space_id": "space-uuid"
    }
  }
}
```

## Error Testing

### Test 12: Unauthorized Access

Test without authorization token:

```bash
curl -X GET "http://localhost:8000/api/v1/folders/FOLDER_ID/spaces"
```

**Expected Response (401 Unauthorized):**
```json
{
  "error": {
    "code": "HTTP_401",
    "message": "Could not validate credentials",
    "details": null
  }
}
```

### Test 13: Invalid Folder ID

```bash
curl -X GET "http://localhost:8000/api/v1/folders/invalid-uuid/spaces" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

**Expected Response (422 Unprocessable Entity):**
Validation error for invalid UUID format.

### Test 14: Non-existent Folder

```bash
curl -X GET "http://localhost:8000/api/v1/folders/12345678-1234-1234-1234-123456789abc/spaces" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

**Expected Response (404 Not Found):**
```json
{
  "error": {
    "code": "FOLDER_NOT_FOUND",
    "message": "Folder not found or you don't have permission to access it",
    "details": {
      "folder_id": "12345678-1234-1234-1234-123456789abc"
    }
  }
}
```

### Test 15: Invalid Space Type

```bash
curl -X POST "http://localhost:8000/api/v1/folders/FOLDER_ID/spaces" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "type": "invalid_type",
    "title": "Invalid Space",
    "settings": {}
  }'
```

**Expected Response (422 Unprocessable Entity):**
Validation error for invalid space type.

### Test 16: Empty Title

```bash
curl -X POST "http://localhost:8000/api/v1/folders/FOLDER_ID/spaces" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "type": "chat",
    "title": "",
    "settings": {}
  }'
```

**Expected Response (422 Unprocessable Entity):**
Validation error for empty title.

### Test 17: Title Too Long

```bash
curl -X POST "http://localhost:8000/api/v1/folders/FOLDER_ID/spaces" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "type": "chat",
    "title": "'$(printf 'a%.0s' {1..256})'",
    "settings": {}
  }'
```

**Expected Response (422 Unprocessable Entity):**
Validation error for title exceeding 255 characters.

### Test 18: Invalid Settings Format

```bash
curl -X POST "http://localhost:8000/api/v1/folders/FOLDER_ID/spaces" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "type": "chat",
    "title": "Test Space",
    "settings": "not a dictionary"
  }'
```

**Expected Response (422 Unprocessable Entity):**
Validation error for invalid settings format.

## Test Results Summary

After completing all tests, you should have verified:

✅ **Core Functionality:**
- ✅ List spaces (empty and populated)
- ✅ Create spaces (all 6 types)
- ✅ Get specific space
- ✅ Update space (full and partial)
- ✅ Delete space

✅ **Advanced Features:**
- ✅ Type filtering
- ✅ Pagination
- ✅ Complex settings objects
- ✅ Soft deletion

✅ **Security:**
- ✅ Authentication required
- ✅ Folder ownership verification
- ✅ User isolation

✅ **Error Handling:**
- ✅ Invalid UUIDs
- ✅ Non-existent resources
- ✅ Validation errors
- ✅ Authorization errors

✅ **Data Integrity:**
- ✅ Proper response formats
- ✅ Consistent error structures
- ✅ Database constraints
- ✅ Cascade deletions

## Performance Notes

- All endpoints respond within expected time limits
- Pagination works efficiently for large datasets
- Database queries are optimized with proper indexing
- JSON responses are properly formatted and consistent

## Integration Points

The Space Management feature integrates seamlessly with:
- **Authentication System**: JWT token validation
- **Folder Management**: Ownership and hierarchy
- **Database Layer**: SQLAlchemy ORM with proper relationships
- **API Documentation**: Auto-generated OpenAPI specs

## Next Steps

Once space management is verified, you can:
1. Add message/content management to spaces
2. Implement AI features for different space types
3. Add file attachments to spaces
4. Implement real-time features with WebSockets

All space management endpoints are production-ready and follow the API specification exactly. 