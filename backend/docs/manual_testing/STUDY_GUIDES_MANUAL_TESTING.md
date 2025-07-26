# Study Guides Manual Testing Guide

This guide provides step-by-step instructions for manually testing all study guides endpoints in the EdutechHackathon backend API.

## Prerequisites

1. **Start the Backend Server:**
   ```bash
   cd EdutechHackathon/backend
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

2. **Get Authentication Token:**
   You need a valid JWT token to test study guide endpoints. First register or login:
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

   **Save the token from the response for use in study guide API calls.**

3. **Access API Documentation:**
   - Swagger UI: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc

## Test Data Setup

### Step 1: Create a Folder

```bash
# Replace YOUR_TOKEN with the token from registration
export TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."

curl -X POST "http://localhost:8000/api/v1/folders" \
-H "Content-Type: application/json" \
-H "Authorization: Bearer $TOKEN" \
-d '{
  "title": "Biology Study Materials",
  "description": "Folder for biology study guides"
}'
```

**Expected Response (201 Created):**
```json
{
  "data": {
    "id": "folder-uuid",
    "ownerId": "user-uuid",
    "title": "Biology Study Materials",
    "description": "Folder for biology study guides",
    "createdAt": "2025-01-25T10:30:00Z"
  }
}
```

### Step 2: Create a Study Guide Space

```bash
# Replace FOLDER_ID with the folder ID from Step 1
export FOLDER_ID="folder-uuid"

curl -X POST "http://localhost:8000/api/v1/folders/$FOLDER_ID/spaces" \
-H "Content-Type: application/json" \
-H "Authorization: Bearer $TOKEN" \
-d '{
  "type": "studyguide",
  "title": "Biology Study Guide Space"
}'
```

**Expected Response (201 Created):**
```json
{
  "data": {
    "id": "space-uuid",
    "folderId": "folder-uuid",
    "type": "studyguide",
    "title": "Biology Study Guide Space",
    "settings": {},
    "createdAt": "2025-01-25T10:31:00Z"
  }
}
```

### Step 3: Upload Test Files

Create a test file first:
```bash
echo "Photosynthesis is the process by which plants convert light energy into chemical energy. 
It occurs in the chloroplasts and involves two main stages: light-dependent reactions and the Calvin cycle.
Chlorophyll is the green pigment that captures light energy.
The overall equation for photosynthesis is: 6CO2 + 6H2O + light energy → C6H12O6 + 6O2" > test_biology.txt
```

Upload the file:
```bash
curl -X POST "http://localhost:8000/api/v1/files/upload" \
-H "Authorization: Bearer $TOKEN" \
-F "folderId=$FOLDER_ID" \
-F "files=@test_biology.txt"
```

**Expected Response (201 Created):**
```json
{
  "data": [
    {
      "id": "file-uuid",
      "folderId": "folder-uuid",
      "name": "test_biology.txt",
      "mime": "text/plain",
      "size": 256,
      "createdAt": "2025-01-25T10:32:00Z"
    }
  ]
}
```

## Study Guides API Testing

### 1. Create Study Guide

**Endpoint:** `POST /api/v1/spaces/{spaceId}/studyguides`

**Test Case: Successful Study Guide Creation**
```bash
# Replace SPACE_ID and FILE_ID with actual values
export SPACE_ID="space-uuid"
export FILE_ID="file-uuid"

curl -X POST "http://localhost:8000/api/v1/spaces/$SPACE_ID/studyguides" \
-H "Content-Type: application/json" \
-H "Authorization: Bearer $TOKEN" \
-d '{
  "title": "Final Exam Study Plan",
  "deadline": "2025-02-15T23:59:59Z",
  "preferences": {
    "dailyStudyHours": 2,
    "preferredTimes": ["morning", "evening"],
    "breakInterval": 25,
    "studyMethods": ["reading", "flashcards", "practice"]
  },
  "file_ids": ["'$FILE_ID'"],
  "topics": ["photosynthesis", "cellular respiration"]
}'
```

**Expected Response (201 Created):**
```json
{
  "data": {
    "id": "studyguide-uuid",
    "spaceId": "space-uuid",
    "title": "Final Exam Study Plan",
    "deadline": "2025-02-15T23:59:59Z",
    "totalStudyHours": 28,
    "schedule": [
      {
        "id": "session1",
        "date": "2025-01-26T09:00:00Z",
        "duration": 120,
        "topics": ["photosynthesis"],
        "methods": ["reading", "flashcards"]
      }
    ],
    "preferences": {
      "dailyStudyHours": 2,
      "preferredTimes": ["morning", "evening"],
      "breakInterval": 25,
      "studyMethods": ["reading", "flashcards", "practice"]
    },
    "progress": {
      "completedHours": 0,
      "completedSessions": 0,
      "totalSessions": 14
    },
    "createdAt": "2025-01-25T10:33:00Z",
    "updatedAt": "2025-01-25T10:33:00Z"
  }
}
```

**Test Case: Create Study Guide with Multiple Files**
```bash
# Create a second test file
echo "Cellular respiration is the process of breaking down glucose to produce ATP.
It occurs in three stages: glycolysis, Krebs cycle, and electron transport chain.
The mitochondria are the powerhouse of the cell where most ATP is produced." > test_biology2.txt

# Upload the second file
curl -X POST "http://localhost:8000/api/v1/files/upload" \
-H "Authorization: Bearer $TOKEN" \
-F "folderId=$FOLDER_ID" \
-F "files=@test_biology2.txt"

# Get the second file ID from response
export FILE_ID_2="file-uuid-2"

# Create study guide with multiple files
curl -X POST "http://localhost:8000/api/v1/spaces/$SPACE_ID/studyguides" \
-H "Content-Type: application/json" \
-H "Authorization: Bearer $TOKEN" \
-d '{
  "title": "Comprehensive Biology Study Plan",
  "deadline": "2025-03-01T23:59:59Z",
  "preferences": {
    "dailyStudyHours": 3,
    "preferredTimes": ["morning"],
    "breakInterval": 30,
    "studyMethods": ["reading", "practice"]
  },
  "file_ids": ["'$FILE_ID'", "'$FILE_ID_2'"],
  "topics": ["biology", "chemistry"]
}'
```

**Test Case: Invalid Space Type (Should Fail)**
```bash
# Create a regular space (not studyguide type)
curl -X POST "http://localhost:8000/api/v1/folders/$FOLDER_ID/spaces" \
-H "Content-Type: application/json" \
-H "Authorization: Bearer $TOKEN" \
-d '{
  "type": "quiz",
  "title": "Quiz Space"
}'

# Try to create study guide in quiz space
export QUIZ_SPACE_ID="quiz-space-uuid"

curl -X POST "http://localhost:8000/api/v1/spaces/$QUIZ_SPACE_ID/studyguides" \
-H "Content-Type: application/json" \
-H "Authorization: Bearer $TOKEN" \
-d '{
  "title": "Test Study Guide",
  "deadline": "2025-02-15T23:59:59Z",
  "preferences": {
    "dailyStudyHours": 2,
    "preferredTimes": ["morning"],
    "breakInterval": 25,
    "studyMethods": ["reading"]
  },
  "file_ids": ["'$FILE_ID'"]
}'
```

**Expected Response (400 Bad Request):**
```json
{
  "error": {
    "code": "INVALID_SPACE_TYPE",
    "message": "Study guides can only be created in studyguide spaces",
    "details": {"space_type": "quiz"}
  }
}
```

**Test Case: Past Deadline (Should Fail)**
```bash
curl -X POST "http://localhost:8000/api/v1/spaces/$SPACE_ID/studyguides" \
-H "Content-Type: application/json" \
-H "Authorization: Bearer $TOKEN" \
-d '{
  "title": "Past Deadline Study Guide",
  "deadline": "2024-01-01T23:59:59Z",
  "preferences": {
    "dailyStudyHours": 2,
    "preferredTimes": ["morning"],
    "breakInterval": 25,
    "studyMethods": ["reading"]
  },
  "file_ids": ["'$FILE_ID'"]
}'
```

**Expected Response (400 Bad Request):**
```json
{
  "error": {
    "code": "INVALID_DEADLINE",
    "message": "Deadline must be in the future",
    "details": {"deadline": "2024-01-01T23:59:59Z"}
  }
}
```

**Test Case: No Files (Should Fail)**
```bash
curl -X POST "http://localhost:8000/api/v1/spaces/$SPACE_ID/studyguides" \
-H "Content-Type: application/json" \
-H "Authorization: Bearer $TOKEN" \
-d '{
  "title": "No Files Study Guide",
  "deadline": "2025-02-15T23:59:59Z",
  "preferences": {
    "dailyStudyHours": 2,
    "preferredTimes": ["morning"],
    "breakInterval": 25,
    "studyMethods": ["reading"]
  },
  "file_ids": []
}'
```

**Expected Response (422 Unprocessable Entity):**
```json
{
  "detail": [
    {
      "loc": ["body", "file_ids"],
      "msg": "At least one file must be provided",
      "type": "value_error"
    }
  ]
}
```

### 2. List Study Guides

**Endpoint:** `GET /api/v1/spaces/{spaceId}/studyguides`

**Test Case: List Study Guides (Empty)**
```bash
curl -X GET "http://localhost:8000/api/v1/spaces/$SPACE_ID/studyguides" \
-H "Authorization: Bearer $TOKEN"
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

**Test Case: List Study Guides with Data**
```bash
# After creating study guides, list them
curl -X GET "http://localhost:8000/api/v1/spaces/$SPACE_ID/studyguides" \
-H "Authorization: Bearer $TOKEN"
```

**Expected Response (200 OK):**
```json
{
  "data": [
    {
      "id": "studyguide-uuid",
      "spaceId": "space-uuid",
      "title": "Final Exam Study Plan",
      "deadline": "2025-02-15T23:59:59Z",
      "totalStudyHours": 28,
      "preferences": {
        "dailyStudyHours": 2,
        "preferredTimes": ["morning", "evening"],
        "breakInterval": 25,
        "studyMethods": ["reading", "flashcards", "practice"]
      },
      "progress": {
        "completedHours": 0,
        "completedSessions": 0,
        "totalSessions": 14
      },
      "createdAt": "2025-01-25T10:33:00Z"
    }
  ],
  "meta": {
    "page": 1,
    "limit": 20,
    "total": 1
  }
}
```

**Test Case: List Study Guides with Pagination**
```bash
# Create multiple study guides first
for i in {1..5}; do
  curl -X POST "http://localhost:8000/api/v1/spaces/$SPACE_ID/studyguides" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "title": "Study Guide '$i'",
    "deadline": "2025-02-15T23:59:59Z",
    "preferences": {
      "dailyStudyHours": 2,
      "preferredTimes": ["morning"],
      "breakInterval": 25,
      "studyMethods": ["reading"]
    },
    "file_ids": ["'$FILE_ID'"]
  }'
done

# Test pagination
curl -X GET "http://localhost:8000/api/v1/spaces/$SPACE_ID/studyguides?page=1&limit=3" \
-H "Authorization: Bearer $TOKEN"
```

**Expected Response (200 OK):**
```json
{
  "data": [
    // First 3 study guides
  ],
  "meta": {
    "page": 1,
    "limit": 3,
    "total": 6
  }
}
```

### 3. Get Study Guide Detail

**Endpoint:** `GET /api/v1/studyguides/{id}`

**Test Case: Get Study Guide Success**
```bash
# Replace STUDY_GUIDE_ID with actual study guide ID
export STUDY_GUIDE_ID="studyguide-uuid"

curl -X GET "http://localhost:8000/api/v1/studyguides/$STUDY_GUIDE_ID" \
-H "Authorization: Bearer $TOKEN"
```

**Expected Response (200 OK):**
```json
{
  "data": {
    "id": "studyguide-uuid",
    "spaceId": "space-uuid",
    "title": "Final Exam Study Plan",
    "deadline": "2025-02-15T23:59:59Z",
    "totalStudyHours": 28,
    "schedule": [
      {
        "id": "session1",
        "date": "2025-01-26T09:00:00Z",
        "duration": 120,
        "topics": ["photosynthesis"],
        "methods": ["reading", "flashcards"]
      },
      {
        "id": "session2",
        "date": "2025-01-27T09:00:00Z",
        "duration": 120,
        "topics": ["cellular respiration"],
        "methods": ["reading", "practice"]
      }
    ],
    "preferences": {
      "dailyStudyHours": 2,
      "preferredTimes": ["morning", "evening"],
      "breakInterval": 25,
      "studyMethods": ["reading", "flashcards", "practice"]
    },
    "progress": {
      "completedHours": 0,
      "completedSessions": 0,
      "totalSessions": 14
    },
    "createdAt": "2025-01-25T10:33:00Z",
    "updatedAt": "2025-01-25T10:33:00Z"
  }
}
```

**Test Case: Get Non-existent Study Guide**
```bash
curl -X GET "http://localhost:8000/api/v1/studyguides/00000000-0000-0000-0000-000000000000" \
-H "Authorization: Bearer $TOKEN"
```

**Expected Response (404 Not Found):**
```json
{
  "error": {
    "code": "STUDY_GUIDE_NOT_FOUND",
    "message": "Study guide not found",
    "details": {"study_guide_id": "00000000-0000-0000-0000-000000000000"}
  }
}
```

### 4. Update Study Guide

**Endpoint:** `PATCH /api/v1/studyguides/{id}`

**Test Case: Update Study Guide Success**
```bash
curl -X PATCH "http://localhost:8000/api/v1/studyguides/$STUDY_GUIDE_ID" \
-H "Content-Type: application/json" \
-H "Authorization: Bearer $TOKEN" \
-d '{
  "title": "Updated Final Exam Study Plan",
  "preferences": {
    "dailyStudyHours": 3,
    "preferredTimes": ["evening"],
    "breakInterval": 30,
    "studyMethods": ["reading", "practice"]
  }
}'
```

**Expected Response (200 OK):**
```json
{
  "data": {
    "id": "studyguide-uuid",
    "spaceId": "space-uuid",
    "title": "Updated Final Exam Study Plan",
    "deadline": "2025-02-15T23:59:59Z",
    "totalStudyHours": 28,
    "schedule": [...],
    "preferences": {
      "dailyStudyHours": 3,
      "preferredTimes": ["evening"],
      "breakInterval": 30,
      "studyMethods": ["reading", "practice"]
    },
    "progress": {
      "completedHours": 0,
      "completedSessions": 0,
      "totalSessions": 14
    },
    "createdAt": "2025-01-25T10:33:00Z",
    "updatedAt": "2025-01-25T10:34:00Z"
  }
}
```

**Test Case: Partial Update**
```bash
curl -X PATCH "http://localhost:8000/api/v1/studyguides/$STUDY_GUIDE_ID" \
-H "Content-Type: application/json" \
-H "Authorization: Bearer $TOKEN" \
-d '{
  "title": "Biology Final Exam Study Plan"
}'
```

**Expected Response (200 OK):**
```json
{
  "data": {
    "id": "studyguide-uuid",
    "title": "Biology Final Exam Study Plan",
    // Other fields remain unchanged
  }
}
```

### 5. Complete Study Session

**Endpoint:** `POST /api/v1/studyguides/{id}/sessions/{sessionId}/complete`

**Test Case: Complete Study Session Success**
```bash
# Get session ID from study guide detail
SESSION_ID="session1"

curl -X POST "http://localhost:8000/api/v1/studyguides/$STUDY_GUIDE_ID/sessions/$SESSION_ID/complete" \
-H "Authorization: Bearer $TOKEN"
```

**Expected Response (200 OK):**
```json
{
  "data": {
    "studyGuideId": "studyguide-uuid",
    "sessionId": "session1",
    "completedAt": "2025-01-25T10:35:00Z",
    "progress": {
      "completedHours": 2,
      "completedSessions": 1,
      "totalSessions": 14
    }
  }
}
```

**Test Case: Complete Non-existent Session**
```bash
curl -X POST "http://localhost:8000/api/v1/studyguides/$STUDY_GUIDE_ID/sessions/nonexistent-session/complete" \
-H "Authorization: Bearer $TOKEN"
```

**Expected Response (404 Not Found):**
```json
{
  "error": {
    "code": "SESSION_NOT_FOUND",
    "message": "Study session not found",
    "details": {"session_id": "nonexistent-session"}
  }
}
```

### 6. Delete Study Guide

**Endpoint:** `DELETE /api/v1/studyguides/{id}`

**Test Case: Delete Study Guide Success**
```bash
curl -X DELETE "http://localhost:8000/api/v1/studyguides/$STUDY_GUIDE_ID" \
-H "Authorization: Bearer $TOKEN"
```

**Expected Response (204 No Content):**
```
(Empty response body)
```

**Verify Deletion:**
```bash
curl -X GET "http://localhost:8000/api/v1/studyguides/$STUDY_GUIDE_ID" \
-H "Authorization: Bearer $TOKEN"
```

**Expected Response (404 Not Found):**
```json
{
  "error": {
    "code": "STUDY_GUIDE_NOT_FOUND",
    "message": "Study guide not found",
    "details": {"study_guide_id": "studyguide-uuid"}
  }
}
```

## Error Cases Testing

### Test Case: Unauthorized Access

```bash
# Test without token
curl -X GET "http://localhost:8000/api/v1/spaces/$SPACE_ID/studyguides"
```

**Expected Response (401 Unauthorized):**
```json
{
  "detail": "Not authenticated"
}
```

### Test Case: Invalid Space ID

```bash
curl -X POST "http://localhost:8000/api/v1/spaces/invalid-uuid/studyguides" \
-H "Content-Type: application/json" \
-H "Authorization: Bearer $TOKEN" \
-d '{
  "title": "Test Study Guide",
  "deadline": "2025-02-15T23:59:59Z",
  "preferences": {
    "dailyStudyHours": 2,
    "preferredTimes": ["morning"],
    "breakInterval": 25,
    "studyMethods": ["reading"]
  },
  "file_ids": ["'$FILE_ID'"]
}'
```

**Expected Response (422 Unprocessable Entity):**
```json
{
  "detail": [
    {
      "loc": ["path", "space_id"],
      "msg": "value is not a valid uuid",
      "type": "type_error.uuid"
    }
  ]
}
```

### Test Case: Non-existent Files

```bash
curl -X POST "http://localhost:8000/api/v1/spaces/$SPACE_ID/studyguides" \
-H "Content-Type: application/json" \
-H "Authorization: Bearer $TOKEN" \
-d '{
  "title": "Test Study Guide",
  "deadline": "2025-02-15T23:59:59Z",
  "preferences": {
    "dailyStudyHours": 2,
    "preferredTimes": ["morning"],
    "breakInterval": 25,
    "studyMethods": ["reading"]
  },
  "file_ids": ["00000000-0000-0000-0000-000000000000"]
}'
```

**Expected Response (404 Not Found):**
```json
{
  "error": {
    "code": "FILE_NOT_FOUND",
    "message": "One or more files not found",
    "details": {"file_ids": ["00000000-0000-0000-0000-000000000000"]}
  }
}
```

## Complete Workflow Testing

**Test the complete study guide workflow:**

```bash
# 1. Create study guide
STUDY_GUIDE_RESPONSE=$(curl -s -X POST "http://localhost:8000/api/v1/spaces/$SPACE_ID/studyguides" \
-H "Content-Type: application/json" \
-H "Authorization: Bearer $TOKEN" \
-d '{
  "title": "Workflow Test Study Guide",
  "deadline": "2025-02-15T23:59:59Z",
  "preferences": {
    "dailyStudyHours": 2,
    "preferredTimes": ["morning"],
    "breakInterval": 25,
    "studyMethods": ["reading"]
  },
  "file_ids": ["'$FILE_ID'"]
}')

echo "Created study guide: $STUDY_GUIDE_RESPONSE"

STUDY_GUIDE_ID=$(echo $STUDY_GUIDE_RESPONSE | jq -r '.data.id')
echo "Study Guide ID: $STUDY_GUIDE_ID"

# 2. List study guides
curl -s -X GET "http://localhost:8000/api/v1/spaces/$SPACE_ID/studyguides" \
-H "Authorization: Bearer $TOKEN" | jq

# 3. Get study guide detail
curl -s -X GET "http://localhost:8000/api/v1/studyguides/$STUDY_GUIDE_ID" \
-H "Authorization: Bearer $TOKEN" | jq

# 4. Update study guide
curl -s -X PATCH "http://localhost:8000/api/v1/studyguides/$STUDY_GUIDE_ID" \
-H "Content-Type: application/json" \
-H "Authorization: Bearer $TOKEN" \
-d '{
  "title": "Updated Workflow Test Study Guide"
}' | jq

# 5. Complete a study session
SESSION_ID=$(curl -s -X GET "http://localhost:8000/api/v1/studyguides/$STUDY_GUIDE_ID" \
-H "Authorization: Bearer $TOKEN" | jq -r '.data.schedule[0].id')

curl -s -X POST "http://localhost:8000/api/v1/studyguides/$STUDY_GUIDE_ID/sessions/$SESSION_ID/complete" \
-H "Authorization: Bearer $TOKEN" | jq

# 6. Delete study guide
curl -s -X DELETE "http://localhost:8000/api/v1/studyguides/$STUDY_GUIDE_ID" \
-H "Authorization: Bearer $TOKEN"

# 7. Verify deletion
curl -s -X GET "http://localhost:8000/api/v1/studyguides/$STUDY_GUIDE_ID" \
-H "Authorization: Bearer $TOKEN" | jq
```

## Performance Testing

### Test Case: Large Study Guide Generation

```bash
# Create a large text file
for i in {1..100}; do
  echo "Chapter $i: This is a comprehensive study material for biology. It covers various topics including cell biology, genetics, evolution, and ecology. Each chapter contains detailed explanations and examples to help students understand the concepts thoroughly." >> large_biology.txt
done

# Upload the large file
curl -X POST "http://localhost:8000/api/v1/files/upload" \
-H "Authorization: Bearer $TOKEN" \
-F "folderId=$FOLDER_ID" \
-F "files=@large_biology.txt"

# Get the large file ID
export LARGE_FILE_ID="large-file-uuid"

# Generate study guide from large file
curl -X POST "http://localhost:8000/api/v1/spaces/$SPACE_ID/studyguides" \
-H "Content-Type: application/json" \
-H "Authorization: Bearer $TOKEN" \
-d '{
  "title": "Large Biology Study Guide",
  "deadline": "2025-03-15T23:59:59Z",
  "preferences": {
    "dailyStudyHours": 4,
    "preferredTimes": ["morning", "afternoon"],
    "breakInterval": 45,
    "studyMethods": ["reading", "practice", "flashcards"]
  },
  "file_ids": ["'$LARGE_FILE_ID'"],
  "topics": ["cell biology", "genetics", "evolution", "ecology"]
}'
```

## Security Testing

### Test Case: Access Other User's Study Guide

```bash
# Create a second user
curl -X POST "http://localhost:8000/api/v1/auth/register" \
-H "Content-Type: application/json" \
-d '{
  "email": "otheruser@example.com",
  "password": "otherpassword123",
  "name": "Other User"
}'

# Save the second user's token
export TOKEN_2="second-user-token"

# Try to access first user's study guide
curl -X GET "http://localhost:8000/api/v1/studyguides/$STUDY_GUIDE_ID" \
-H "Authorization: Bearer $TOKEN_2"
```

**Expected Response (403 Forbidden):**
```json
{
  "error": {
    "code": "ACCESS_DENIED",
    "message": "You don't have permission to access this study guide",
    "details": {"study_guide_id": "studyguide-uuid"}
  }
}
```

## Cleanup

After testing, clean up test data:

```bash
# Delete test files
rm test_biology.txt test_biology2.txt large_biology.txt

# Delete all study guides (you'll need to get study guide IDs first)
curl -X GET "http://localhost:8000/api/v1/spaces/$SPACE_ID/studyguides" \
-H "Authorization: Bearer $TOKEN"

# For each study guide ID in the response:
curl -X DELETE "http://localhost:8000/api/v1/studyguides/{study-guide-id}" \
-H "Authorization: Bearer $TOKEN"
```

## Expected Behavior Summary

1. **Study Guide Creation**: Creates study guides with AI-generated schedules
2. **Schedule Generation**: Mock AI generates realistic study schedules
3. **Progress Tracking**: Tracks completed sessions and hours
4. **Validation**: Proper input validation with clear error messages
5. **Authorization**: Ensures users can only access their own study guides
6. **Pagination**: Supports paginated study guide listing
7. **Session Completion**: Allows marking study sessions as complete
8. **Error Handling**: Consistent error response format
9. **Performance**: Handles large files and complex schedules

## Troubleshooting

If you encounter issues:

1. **Server not starting**: Check if port 8000 is available
2. **Database errors**: Ensure the data directory exists and has write permissions
3. **Token expired**: Re-authenticate to get a new token
4. **File upload fails**: Check file size limits and MIME types
5. **Tests failing**: Verify all prerequisite data is created correctly
6. **Schedule generation**: Mock AI generates sample schedules; real AI integration pending

This completes the manual testing guide for the Study Guides functionality! 