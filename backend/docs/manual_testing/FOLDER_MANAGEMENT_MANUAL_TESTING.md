# Folder Management API Manual Testing Guide

This guide provides step-by-step instructions for manually testing all folder management endpoints in the EdutechHackathon backend API.

## Prerequisites

1. **Start the Backend Server:**
   ```bash
   cd EdutechHackathon/backend
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

2. **Get Authentication Token:**
   You need a valid JWT token to test folder endpoints. First register or login:
   ```bash
   # Register a new user
   curl -X POST "http://localhost:8000/api/v1/auth/register" \
   -H "Content-Type: application/json" \
   -d '{
     "email": "testuser@example.com",
     "password": "securepassword123",
     "name": "Test User"
   }'
   ```

   **Save the token from the response for use in folder API calls.**

3. **Access API Documentation:**
   - Swagger UI: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc

## Folder Management Endpoints

### 1. List User Folders

**Endpoint:** `GET /api/v1/folders`

**Test Case: List Folders (Default Pagination)**
```bash
curl -X GET "http://localhost:8000/api/v1/folders" \
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

**Test Case: List Folders with Custom Pagination**
```bash
curl -X GET "http://localhost:8000/api/v1/folders?page=2&limit=5" \
-H "Authorization: Bearer YOUR_JWT_TOKEN"
```

**Expected Response (200 OK):**
```json
{
  "data": [],
  "meta": {
    "page": 2,
    "limit": 5,
    "total": 0
  }
}
```

**Test Case: Search Folders**
```bash
curl -X GET "http://localhost:8000/api/v1/folders?q=biology" \
-H "Authorization: Bearer YOUR_JWT_TOKEN"
```

**Test Case: Unauthorized Access**
```bash
curl -X GET "http://localhost:8000/api/v1/folders"
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

### 2. Create Folder

**Endpoint:** `POST /api/v1/folders`

**Test Case: Successful Folder Creation**
```bash
curl -X POST "http://localhost:8000/api/v1/folders" \
-H "Content-Type: application/json" \
-H "Authorization: Bearer YOUR_JWT_TOKEN" \
-d '{
  "title": "Biology 101",
  "description": "First semester biology course materials"
}'
```

**Expected Response (201 Created):**
```json
{
  "data": {
    "id": "a1b2c3d4-e5f6-7890-1234-567890abcdef",
    "ownerId": "user-id-here",
    "title": "Biology 101",
    "description": "First semester biology course materials",
    "createdAt": "2025-01-25T10:30:00Z"
  }
}
```

**Test Case: Create Folder with Minimal Data**
```bash
curl -X POST "http://localhost:8000/api/v1/folders" \
-H "Content-Type: application/json" \
-H "Authorization: Bearer YOUR_JWT_TOKEN" \
-d '{
  "title": "Chemistry Lab"
}'
```

**Expected Response (201 Created):**
```json
{
  "data": {
    "id": "b2c3d4e5-f6g7-8901-2345-678901bcdefg",
    "ownerId": "user-id-here",
    "title": "Chemistry Lab",
    "description": null,
    "createdAt": "2025-01-25T10:31:00Z"
  }
}
```

**Test Case: Missing Title (Should Fail)**
```bash
curl -X POST "http://localhost:8000/api/v1/folders" \
-H "Content-Type: application/json" \
-H "Authorization: Bearer YOUR_JWT_TOKEN" \
-d '{
  "description": "Folder without title"
}'
```

**Expected Response (422 Unprocessable Entity):**
```json
{
  "detail": [
    {
      "loc": ["body", "title"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

**Test Case: Empty Title (Should Fail)**
```bash
curl -X POST "http://localhost:8000/api/v1/folders" \
-H "Content-Type: application/json" \
-H "Authorization: Bearer YOUR_JWT_TOKEN" \
-d '{
  "title": "",
  "description": "Empty title test"
}'
```

**Test Case: Title Too Long (Should Fail)**
```bash
curl -X POST "http://localhost:8000/api/v1/folders" \
-H "Content-Type: application/json" \
-H "Authorization: Bearer YOUR_JWT_TOKEN" \
-d '{
  "title": "'$(printf 'A%.0s' {1..256})'",
  "description": "Title with 256 characters"
}'
```

**Test Case: Description Too Long (Should Fail)**
```bash
curl -X POST "http://localhost:8000/api/v1/folders" \
-H "Content-Type: application/json" \
-H "Authorization: Bearer YOUR_JWT_TOKEN" \
-d '{
  "title": "Valid Title",
  "description": "'$(printf 'A%.0s' {1..1001})'"
}'
```

**Test Case: Unauthorized Creation**
```bash
curl -X POST "http://localhost:8000/api/v1/folders" \
-H "Content-Type: application/json" \
-d '{
  "title": "Unauthorized Folder"
}'
```

### 3. Get Folder by ID

**Endpoint:** `GET /api/v1/folders/{id}`

**Test Case: Successful Folder Retrieval**
```bash
# First create a folder and note the ID from the response
curl -X GET "http://localhost:8000/api/v1/folders/FOLDER_ID_HERE" \
-H "Authorization: Bearer YOUR_JWT_TOKEN"
```

**Expected Response (200 OK):**
```json
{
  "data": {
    "id": "a1b2c3d4-e5f6-7890-1234-567890abcdef",
    "ownerId": "user-id-here",
    "title": "Biology 101",
    "description": "First semester biology course materials",
    "createdAt": "2025-01-25T10:30:00Z"
  }
}
```

**Test Case: Folder Not Found**
```bash
curl -X GET "http://localhost:8000/api/v1/folders/00000000-0000-0000-0000-000000000000" \
-H "Authorization: Bearer YOUR_JWT_TOKEN"
```

**Expected Response (404 Not Found):**
```json
{
  "error": {
    "code": "FOLDER_NOT_FOUND",
    "message": "Folder not found or you don't have permission to access it",
    "details": {
      "folder_id": "00000000-0000-0000-0000-000000000000"
    }
  }
}
```

**Test Case: Invalid UUID Format**
```bash
curl -X GET "http://localhost:8000/api/v1/folders/invalid-uuid" \
-H "Authorization: Bearer YOUR_JWT_TOKEN"
```

**Expected Response (422 Unprocessable Entity):**
```json
{
  "detail": [
    {
      "loc": ["path", "folder_id"],
      "msg": "value is not a valid uuid",
      "type": "type_error.uuid"
    }
  ]
}
```

**Test Case: Unauthorized Access**
```bash
curl -X GET "http://localhost:8000/api/v1/folders/FOLDER_ID_HERE"
```

### 4. Update Folder

**Endpoint:** `PATCH /api/v1/folders/{id}`

**Test Case: Successful Folder Update**
```bash
curl -X PATCH "http://localhost:8000/api/v1/folders/FOLDER_ID_HERE" \
-H "Content-Type: application/json" \
-H "Authorization: Bearer YOUR_JWT_TOKEN" \
-d '{
  "title": "Advanced Biology",
  "description": "Updated description for advanced course"
}'
```

**Expected Response (200 OK):**
```json
{
  "data": {
    "id": "a1b2c3d4-e5f6-7890-1234-567890abcdef",
    "ownerId": "user-id-here",
    "title": "Advanced Biology",
    "description": "Updated description for advanced course",
    "createdAt": "2025-01-25T10:30:00Z"
  }
}
```

**Test Case: Partial Update (Title Only)**
```bash
curl -X PATCH "http://localhost:8000/api/v1/folders/FOLDER_ID_HERE" \
-H "Content-Type: application/json" \
-H "Authorization: Bearer YOUR_JWT_TOKEN" \
-d '{
  "title": "Biology Fundamentals"
}'
```

**Test Case: Partial Update (Description Only)**
```bash
curl -X PATCH "http://localhost:8000/api/v1/folders/FOLDER_ID_HERE" \
-H "Content-Type: application/json" \
-H "Authorization: Bearer YOUR_JWT_TOKEN" \
-d '{
  "description": "Updated description only"
}'
```

**Test Case: Update Non-existent Folder**
```bash
curl -X PATCH "http://localhost:8000/api/v1/folders/00000000-0000-0000-0000-000000000000" \
-H "Content-Type: application/json" \
-H "Authorization: Bearer YOUR_JWT_TOKEN" \
-d '{
  "title": "Non-existent Folder"
}'
```

**Test Case: Invalid Update Data (Title Too Long)**
```bash
curl -X PATCH "http://localhost:8000/api/v1/folders/FOLDER_ID_HERE" \
-H "Content-Type: application/json" \
-H "Authorization: Bearer YOUR_JWT_TOKEN" \
-d '{
  "title": "'$(printf 'A%.0s' {1..256})'"
}'
```

**Test Case: Unauthorized Update**
```bash
curl -X PATCH "http://localhost:8000/api/v1/folders/FOLDER_ID_HERE" \
-H "Content-Type: application/json" \
-d '{
  "title": "Unauthorized Update"
}'
```

### 5. Delete Folder

**Endpoint:** `DELETE /api/v1/folders/{id}`

**Test Case: Successful Folder Deletion**
```bash
curl -X DELETE "http://localhost:8000/api/v1/folders/FOLDER_ID_HERE" \
-H "Authorization: Bearer YOUR_JWT_TOKEN"
```

**Expected Response (204 No Content):**
```
(Empty response body)
```

**Verify Deletion:**
```bash
curl -X GET "http://localhost:8000/api/v1/folders/FOLDER_ID_HERE" \
-H "Authorization: Bearer YOUR_JWT_TOKEN"
```

**Expected Response (404 Not Found):**
```json
{
  "error": {
    "code": "FOLDER_NOT_FOUND",
    "message": "Folder not found or you don't have permission to access it",
    "details": {
      "folder_id": "FOLDER_ID_HERE"
    }
  }
}
```

**Test Case: Delete Non-existent Folder**
```bash
curl -X DELETE "http://localhost:8000/api/v1/folders/00000000-0000-0000-0000-000000000000" \
-H "Authorization: Bearer YOUR_JWT_TOKEN"
```

**Test Case: Invalid UUID Format**
```bash
curl -X DELETE "http://localhost:8000/api/v1/folders/invalid-uuid" \
-H "Authorization: Bearer YOUR_JWT_TOKEN"
```

**Test Case: Unauthorized Deletion**
```bash
curl -X DELETE "http://localhost:8000/api/v1/folders/FOLDER_ID_HERE"
```

## Complete Folder Lifecycle Test

**Comprehensive Test Workflow:**

```bash
# 1. Register/Login and get token
TOKEN=$(curl -s -X POST "http://localhost:8000/api/v1/auth/register" \
-H "Content-Type: application/json" \
-d '{
  "email": "lifecycle@test.com",
  "password": "testpass123",
  "name": "Lifecycle Test"
}' | jq -r '.data.token')

echo "Token: $TOKEN"

# 2. Create a folder
FOLDER_RESPONSE=$(curl -s -X POST "http://localhost:8000/api/v1/folders" \
-H "Content-Type: application/json" \
-H "Authorization: Bearer $TOKEN" \
-d '{
  "title": "Test Lifecycle Folder",
  "description": "Testing complete folder lifecycle"
}')

echo "Created folder: $FOLDER_RESPONSE"

FOLDER_ID=$(echo $FOLDER_RESPONSE | jq -r '.data.id')
echo "Folder ID: $FOLDER_ID"

# 3. Get the folder
curl -s -X GET "http://localhost:8000/api/v1/folders/$FOLDER_ID" \
-H "Authorization: Bearer $TOKEN" | jq

# 4. Update the folder
curl -s -X PATCH "http://localhost:8000/api/v1/folders/$FOLDER_ID" \
-H "Content-Type: application/json" \
-H "Authorization: Bearer $TOKEN" \
-d '{
  "title": "Updated Lifecycle Folder",
  "description": "Updated description"
}' | jq

# 5. List folders to see the updated folder
curl -s -X GET "http://localhost:8000/api/v1/folders" \
-H "Authorization: Bearer $TOKEN" | jq

# 6. Delete the folder
curl -s -X DELETE "http://localhost:8000/api/v1/folders/$FOLDER_ID" \
-H "Authorization: Bearer $TOKEN"

# 7. Verify deletion
curl -s -X GET "http://localhost:8000/api/v1/folders/$FOLDER_ID" \
-H "Authorization: Bearer $TOKEN" | jq
```

## Testing Notes

1. **Replace Placeholders:** Always replace `YOUR_JWT_TOKEN` and `FOLDER_ID_HERE` with actual values.

2. **Error Responses:** The API returns structured error responses following the API specification format.

3. **Pagination:** Default pagination is 20 items per page, maximum 100 items per page.

4. **Search:** Search is case-insensitive and matches folder titles.

5. **Soft Delete:** Folders are soft-deleted (marked as deleted but not physically removed).

6. **UUID Validation:** All folder IDs must be valid UUIDs.

7. **Authorization:** All endpoints except unauthorized test cases require a valid JWT token.

## Common HTTP Status Codes

- **200 OK**: Successful retrieval
- **201 Created**: Successful creation
- **204 No Content**: Successful deletion
- **400 Bad Request**: Invalid request data
- **401 Unauthorized**: Missing or invalid authentication
- **404 Not Found**: Resource not found
- **422 Unprocessable Entity**: Validation errors
- **500 Internal Server Error**: Server error

## Security Testing

**Test Rate Limiting:**
```bash
# Run multiple requests quickly to test rate limiting
for i in {1..110}; do
  curl -s -o /dev/null -w "%{http_code} " "http://localhost:8000/api/v1/folders" \
  -H "Authorization: Bearer $TOKEN"
done
```

**Test Token Expiration:**
```bash
# Use an old or invalid token
curl -X GET "http://localhost:8000/api/v1/folders" \
-H "Authorization: Bearer invalid-token-here"
```

This comprehensive testing guide ensures all folder management functionality works correctly according to the API specification and data flow requirements. 