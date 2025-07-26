# Quiz Functionality Manual Testing Guide

This guide provides step-by-step instructions for manually testing the Quiz API endpoints using command line tools.

## Prerequisites

1. **Start the FastAPI Server:**
   ```bash
   cd EdutechHackathon/backend
   python3 -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

2. **Verify Server is Running:**
   ```bash
   curl -X GET "http://localhost:8000/health"
   ```
   Expected response:
   ```json
   {
     "status": "healthy",
     "version": "1.0.0",
     "environment": "development"
   }
   ```

## Test Data Setup

### Step 1: Create a User Account

```bash
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "testuser@example.com",
    "password": "testpassword123",
    "name": "Test User"
  }'
```

Expected response (save the token for later use):
```json
{
  "data": {
    "user": {
      "id": "user-uuid",
      "email": "testuser@example.com",
      "name": "Test User",
      "created_at": "2025-01-15T10:30:00Z"
    },
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
  }
}
```

### Step 2: Create a Folder

```bash
# Replace YOUR_TOKEN with the token from Step 1
export TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."

curl -X POST "http://localhost:8000/api/v1/folders" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "title": "Biology Study Materials",
    "description": "Folder for biology quiz testing"
  }'
```

Expected response (save the folder ID):
```json
{
  "data": {
    "id": "folder-uuid",
    "ownerId": "user-uuid",
    "title": "Biology Study Materials",
    "description": "Folder for biology quiz testing",
    "createdAt": "2025-01-15T10:31:00Z"
  }
}
```

### Step 3: Create a Quiz Space

```bash
# Replace FOLDER_ID with the folder ID from Step 2
export FOLDER_ID="folder-uuid"

curl -X POST "http://localhost:8000/api/v1/folders/$FOLDER_ID/spaces" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "type": "quiz",
    "title": "Biology Quiz Space"
  }'
```

Expected response (save the space ID):
```json
{
  "data": {
    "id": "space-uuid",
    "folderId": "folder-uuid",
    "type": "quiz",
    "title": "Biology Quiz Space",
    "settings": {},
    "createdAt": "2025-01-15T10:32:00Z"
  }
}
```

### Step 4: Upload Test Files

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

Expected response (save the file ID):
```json
{
  "data": [
    {
      "id": "file-uuid",
      "folderId": "folder-uuid",
      "name": "test_biology.txt",
      "mime": "text/plain",
      "size": 256,
      "createdAt": "2025-01-15T10:33:00Z"
    }
  ]
}
```

## Quiz API Testing

### Test 1: Generate Quiz (Success Case)

```bash
# Replace SPACE_ID and FILE_ID with actual values
export SPACE_ID="space-uuid"
export FILE_ID="file-uuid"

curl -X POST "http://localhost:8000/api/v1/spaces/$SPACE_ID/quizzes" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "title": "Photosynthesis Quiz",
    "fileIds": ["'$FILE_ID'"],
    "questionCount": 5,
    "questionTypes": ["mcq", "tf"],
    "difficulty": "medium"
  }'
```

Expected response (save the quiz ID):
```json
{
  "data": {
    "id": "quiz-uuid",
    "spaceId": "space-uuid",
    "title": "Photosynthesis Quiz",
    "questions": [
      {
        "id": "q1",
        "type": "mcq",
        "prompt": "Mock MCQ question 1 about Photosynthesis Quiz?",
        "choices": [
          "Option A for question 1",
          "Option B for question 1",
          "Option C for question 1",
          "Option D for question 1"
        ],
        "answer": "A"
      },
      {
        "id": "q2",
        "type": "tf",
        "prompt": "Mock True/False question 2 about Photosynthesis Quiz.",
        "answer": false
      }
    ],
    "createdAt": "2025-01-15T10:34:00Z"
  }
}
```

### Test 2: Generate Quiz (Validation Error)

```bash
# Test with empty title
curl -X POST "http://localhost:8000/api/v1/spaces/$SPACE_ID/quizzes" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "title": "",
    "fileIds": ["'$FILE_ID'"]
  }'
```

Expected response (422 status):
```json
{
  "detail": [
    {
      "loc": ["body", "title"],
      "msg": "Title cannot be empty",
      "type": "value_error"
    }
  ]
}
```

### Test 3: List Quizzes

```bash
curl -X GET "http://localhost:8000/api/v1/spaces/$SPACE_ID/quizzes?page=1&limit=10" \
  -H "Authorization: Bearer $TOKEN"
```

Expected response:
```json
{
  "data": [
    {
      "id": "quiz-uuid",
      "spaceId": "space-uuid",
      "title": "Photosynthesis Quiz",
      "questions": [...],
      "createdAt": "2025-01-15T10:34:00Z"
    }
  ],
  "meta": {
    "page": 1,
    "limit": 10,
    "total": 1
  }
}
```

### Test 4: Get Quiz Detail

```bash
# Replace QUIZ_ID with actual quiz ID from Test 1
export QUIZ_ID="quiz-uuid"

curl -X GET "http://localhost:8000/api/v1/quizzes/$QUIZ_ID" \
  -H "Authorization: Bearer $TOKEN"
```

Expected response:
```json
{
  "data": {
    "id": "quiz-uuid",
    "spaceId": "space-uuid",
    "title": "Photosynthesis Quiz",
    "questions": [
      {
        "id": "q1",
        "type": "mcq",
        "prompt": "Mock MCQ question 1 about Photosynthesis Quiz?",
        "choices": [
          "Option A for question 1",
          "Option B for question 1",
          "Option C for question 1",
          "Option D for question 1"
        ],
        "answer": "A"
      }
    ],
    "createdAt": "2025-01-15T10:34:00Z"
  }
}
```

### Test 5: Submit Quiz Answers (Success)

```bash
curl -X POST "http://localhost:8000/api/v1/quizzes/$QUIZ_ID/submit" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "answers": [
      {
        "questionId": "q1",
        "answer": "A"
      },
      {
        "questionId": "q2",
        "answer": false
      }
    ]
  }'
```

Expected response:
```json
{
  "data": {
    "score": 2.0,
    "totalQuestions": 5,
    "feedback": [
      {
        "questionId": "q1",
        "userAnswer": "A",
        "correctAnswer": "A",
        "isCorrect": true,
        "feedback": "Correct!"
      },
      {
        "questionId": "q2",
        "userAnswer": false,
        "correctAnswer": false,
        "isCorrect": true,
        "feedback": "Correct!"
      }
    ],
    "submittedAt": "2025-01-15T10:35:00Z"
  }
}
```

### Test 6: Submit Quiz Answers (Validation Error)

```bash
curl -X POST "http://localhost:8000/api/v1/quizzes/$QUIZ_ID/submit" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "answers": []
  }'
```

Expected response (422 status):
```json
{
  "detail": [
    {
      "loc": ["body", "answers"],
      "msg": "At least one answer must be provided",
      "type": "value_error"
    }
  ]
}
```

### Test 7: Delete Quiz

```bash
curl -X DELETE "http://localhost:8000/api/v1/quizzes/$QUIZ_ID" \
  -H "Authorization: Bearer $TOKEN"
```

Expected response (204 status, no content).

Verify deletion:
```bash
curl -X GET "http://localhost:8000/api/v1/quizzes/$QUIZ_ID" \
  -H "Authorization: Bearer $TOKEN"
```

Expected response (404 status):
```json
{
  "error": {
    "code": "QUIZ_NOT_FOUND",
    "message": "Quiz not found",
    "details": {"quiz_id": "quiz-uuid"}
  }
}
```

## Error Cases Testing

### Test 8: Unauthorized Access

```bash
# Test without token
curl -X GET "http://localhost:8000/api/v1/spaces/$SPACE_ID/quizzes"
```

Expected response (401 status):
```json
{
  "detail": "Not authenticated"
}
```

### Test 9: Invalid Space ID

```bash
curl -X POST "http://localhost:8000/api/v1/spaces/invalid-uuid/quizzes" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "title": "Test Quiz",
    "fileIds": ["'$FILE_ID'"]
  }'
```

Expected response (422 status):
```json
{
  "error": {
    "code": "INVALID_UUID",
    "message": "Invalid space ID format",
    "details": {"space_id": "invalid-uuid"}
  }
}
```

### Test 10: Non-existent Quiz

```bash
curl -X GET "http://localhost:8000/api/v1/quizzes/00000000-0000-0000-0000-000000000000" \
  -H "Authorization: Bearer $TOKEN"
```

Expected response (404 status):
```json
{
  "error": {
    "code": "QUIZ_NOT_FOUND",
    "message": "Quiz not found",
    "details": {"quiz_id": "00000000-0000-0000-0000-000000000000"}
  }
}
```

## Advanced Testing Scenarios

### Test 11: Generate Quiz with All Question Types

```bash
# Create another file for more content
echo "Cellular respiration is the process of breaking down glucose to produce ATP.
It occurs in three stages: glycolysis, Krebs cycle, and electron transport chain.
The mitochondria are the powerhouse of the cell where most ATP is produced." > test_biology2.txt

# Upload the second file
curl -X POST "http://localhost:8000/api/v1/files/upload" \
  -H "Authorization: Bearer $TOKEN" \
  -F "folderId=$FOLDER_ID" \
  -F "files=@test_biology2.txt"

# Get the file ID from response and set it
export FILE_ID_2="file-uuid-2"

# Generate quiz with all question types
curl -X POST "http://localhost:8000/api/v1/spaces/$SPACE_ID/quizzes" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "title": "Comprehensive Biology Quiz",
    "fileIds": ["'$FILE_ID'", "'$FILE_ID_2'"],
    "questionCount": 15,
    "questionTypes": ["mcq", "tf", "short_answer"],
    "difficulty": "hard"
  }'
```

### Test 12: Test Pagination

```bash
# Generate multiple quizzes first
for i in {1..5}; do
  curl -X POST "http://localhost:8000/api/v1/spaces/$SPACE_ID/quizzes" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer $TOKEN" \
    -d '{
      "title": "Quiz '$i'",
      "fileIds": ["'$FILE_ID'"]
    }'
done

# Test pagination
curl -X GET "http://localhost:8000/api/v1/spaces/$SPACE_ID/quizzes?page=1&limit=3" \
  -H "Authorization: Bearer $TOKEN"

curl -X GET "http://localhost:8000/api/v1/spaces/$SPACE_ID/quizzes?page=2&limit=3" \
  -H "Authorization: Bearer $TOKEN"
```

### Test 13: Submit Partial Answers

```bash
# Generate a new quiz for this test
curl -X POST "http://localhost:8000/api/v1/spaces/$SPACE_ID/quizzes" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "title": "Partial Answer Test Quiz",
    "fileIds": ["'$FILE_ID'"],
    "questionCount": 5
  }'

# Get the quiz ID from response and submit partial answers
export PARTIAL_QUIZ_ID="partial-quiz-uuid"

curl -X POST "http://localhost:8000/api/v1/quizzes/$PARTIAL_QUIZ_ID/submit" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "answers": [
      {
        "questionId": "q1",
        "answer": "A"
      }
    ]
  }'
```

## Performance Testing

### Test 14: Large Quiz Generation

```bash
curl -X POST "http://localhost:8000/api/v1/spaces/$SPACE_ID/quizzes" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "title": "Large Quiz Test",
    "fileIds": ["'$FILE_ID'"],
    "questionCount": 50,
    "questionTypes": ["mcq", "tf", "short_answer"],
    "difficulty": "medium"
  }'
```

### Test 15: Concurrent Quiz Generation

Open multiple terminal windows and run quiz generation simultaneously:

Terminal 1:
```bash
curl -X POST "http://localhost:8000/api/v1/spaces/$SPACE_ID/quizzes" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"title": "Concurrent Quiz 1", "fileIds": ["'$FILE_ID'"]}'
```

Terminal 2:
```bash
curl -X POST "http://localhost:8000/api/v1/spaces/$SPACE_ID/quizzes" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"title": "Concurrent Quiz 2", "fileIds": ["'$FILE_ID'"]}'
```

## API Documentation Testing

### Test 16: Verify OpenAPI Documentation

```bash
# Access the interactive API documentation
curl -X GET "http://localhost:8000/docs"

# Access the ReDoc documentation
curl -X GET "http://localhost:8000/redoc"

# Get the OpenAPI specification
curl -X GET "http://localhost:8000/openapi.json"
```

## Cleanup

After testing, clean up test data:

```bash
# Delete all quizzes (you'll need to get quiz IDs first)
curl -X GET "http://localhost:8000/api/v1/spaces/$SPACE_ID/quizzes" \
  -H "Authorization: Bearer $TOKEN"

# For each quiz ID in the response:
curl -X DELETE "http://localhost:8000/api/v1/quizzes/{quiz-id}" \
  -H "Authorization: Bearer $TOKEN"

# Delete test files
rm test_biology.txt test_biology2.txt
```

## Expected Behavior Summary

1. **Quiz Generation**: Creates mock quizzes with specified parameters
2. **Question Types**: Supports MCQ, True/False, and Short Answer questions
3. **Mock AI Integration**: Generates sample questions and provides basic grading
4. **Validation**: Proper input validation with clear error messages
5. **Authorization**: Ensures users can only access their own quizzes
6. **Pagination**: Supports paginated quiz listing
7. **Cascade Deletion**: Deleting quizzes removes all submissions
8. **Error Handling**: Consistent error response format
9. **Performance**: Handles concurrent requests and large quiz generation

## Troubleshooting

If you encounter issues:

1. **Server not starting**: Check if port 8000 is available
2. **Database errors**: Ensure the data directory exists and has write permissions
3. **Token expired**: Re-authenticate to get a new token
4. **File upload fails**: Check file size limits and MIME types
5. **Tests failing**: Verify all prerequisite data is created correctly

This completes the manual testing guide for the Quiz functionality! 