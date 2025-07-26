# Flashcards Manual Testing Guide

This guide provides step-by-step instructions for manually testing all flashcard endpoints in the EdutechHackathon backend API.

## Prerequisites

1. **Start the Backend Server:**
   ```bash
   cd EdutechHackathon/backend
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

2. **Get Authentication Token:**
   You need a valid JWT token to test flashcard endpoints. First register or login:
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

   **Save the token from the response for use in flashcard API calls.**

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
  "description": "Folder for biology flashcards"
}'
```

**Expected Response (201 Created):**
```json
{
  "data": {
    "id": "folder-uuid",
    "ownerId": "user-uuid",
    "title": "Biology Study Materials",
    "description": "Folder for biology flashcards",
    "createdAt": "2025-01-25T10:30:00Z"
  }
}
```

### Step 2: Create a Space

```bash
# Replace FOLDER_ID with the folder ID from Step 1
export FOLDER_ID="folder-uuid"

curl -X POST "http://localhost:8000/api/v1/folders/$FOLDER_ID/spaces" \
-H "Content-Type: application/json" \
-H "Authorization: Bearer $TOKEN" \
-d '{
  "type": "quiz",
  "title": "Biology Flashcard Space"
}'
```

**Expected Response (201 Created):**
```json
{
  "data": {
    "id": "space-uuid",
    "folderId": "folder-uuid",
    "type": "quiz",
    "title": "Biology Flashcard Space",
    "settings": {},
    "createdAt": "2025-01-25T10:31:00Z"
  }
}
```

### Step 3: Upload Test Files

Create test files first:
```bash
echo "Photosynthesis is the process by which plants convert light energy into chemical energy. 
It occurs in the chloroplasts and involves two main stages: light-dependent reactions and the Calvin cycle.
Chlorophyll is the green pigment that captures light energy.
The overall equation for photosynthesis is: 6CO2 + 6H2O + light energy → C6H12O6 + 6O2" > test_biology.txt

echo "Cellular respiration is the process of breaking down glucose to produce ATP.
It occurs in three stages: glycolysis, Krebs cycle, and electron transport chain.
The mitochondria are the powerhouse of the cell where most ATP is produced." > test_biology2.txt
```

Upload the files:
```bash
curl -X POST "http://localhost:8000/api/v1/files/upload" \
-H "Authorization: Bearer $TOKEN" \
-F "folderId=$FOLDER_ID" \
-F "files=@test_biology.txt" \
-F "files=@test_biology2.txt"
```

**Expected Response (201 Created):**
```json
{
  "data": [
    {
      "id": "file-uuid-1",
      "folderId": "folder-uuid",
      "name": "test_biology.txt",
      "mime": "text/plain",
      "size": 256,
      "createdAt": "2025-01-25T10:32:00Z"
    },
    {
      "id": "file-uuid-2",
      "folderId": "folder-uuid",
      "name": "test_biology2.txt",
      "mime": "text/plain",
      "size": 198,
      "createdAt": "2025-01-25T10:32:00Z"
    }
  ]
}
```

## Flashcards API Testing

### 1. Generate Flashcards

**Endpoint:** `POST /api/v1/spaces/{spaceId}/flashcards`

**Test Case: Successful Flashcard Generation**
```bash
# Replace SPACE_ID and FILE_IDs with actual values
export SPACE_ID="space-uuid"
export FILE_ID_1="file-uuid-1"
export FILE_ID_2="file-uuid-2"

curl -X POST "http://localhost:8000/api/v1/spaces/$SPACE_ID/flashcards" \
-H "Content-Type: application/json" \
-H "Authorization: Bearer $TOKEN" \
-d '{
  "title": "Biology Terms Set 1",
  "fileIds": ["'$FILE_ID_1'", "'$FILE_ID_2'"],
  "cardCount": 20,
  "cardTypes": ["mcq", "tf"],
  "difficulty": "medium"
}'
```

**Expected Response (201 Created):**
```json
{
  "data": {
    "id": "flashcard-uuid",
    "spaceId": "space-uuid",
    "title": "Biology Terms Set 1",
    "cards": [
      {
        "id": "card1",
        "front": "What is the process by which plants convert light energy into chemical energy?",
        "back": "Photosynthesis",
        "difficulty": "medium",
        "tags": ["photosynthesis", "plants", "energy"]
      },
      {
        "id": "card2",
        "front": "True or False: Chlorophyll is the green pigment that captures light energy.",
        "back": "True",
        "difficulty": "easy",
        "tags": ["chlorophyll", "pigment", "light"]
      },
      {
        "id": "card3",
        "front": "Which organelle is known as the powerhouse of the cell?",
        "back": "Mitochondria",
        "difficulty": "medium",
        "tags": ["mitochondria", "organelle", "ATP"]
      }
    ],
    "createdAt": "2025-01-25T10:33:00Z",
    "updatedAt": "2025-01-25T10:33:00Z"
  }
}
```

**Test Case: Generate Flashcards with Minimal Data**
```bash
curl -X POST "http://localhost:8000/api/v1/spaces/$SPACE_ID/flashcards" \
-H "Content-Type: application/json" \
-H "Authorization: Bearer $TOKEN" \
-d '{
  "title": "Simple Flashcards",
  "fileIds": ["'$FILE_ID_1'"]
}'
```

**Expected Response (201 Created):**
```json
{
  "data": {
    "id": "flashcard-uuid-2",
    "spaceId": "space-uuid",
    "title": "Simple Flashcards",
    "cards": [
      // 20 default cards generated
    ],
    "createdAt": "2025-01-25T10:34:00Z",
    "updatedAt": "2025-01-25T10:34:00Z"
  }
}
```

**Test Case: Generate Flashcards with All Question Types**
```bash
curl -X POST "http://localhost:8000/api/v1/spaces/$SPACE_ID/flashcards" \
-H "Content-Type: application/json" \
-H "Authorization: Bearer $TOKEN" \
-d '{
  "title": "Comprehensive Biology Flashcards",
  "fileIds": ["'$FILE_ID_1'", "'$FILE_ID_2'"],
  "cardCount": 30,
  "cardTypes": ["mcq", "tf", "short_answer"],
  "difficulty": "hard"
}'
```

**Expected Response (201 Created):**
```json
{
  "data": {
    "id": "flashcard-uuid-3",
    "spaceId": "space-uuid",
    "title": "Comprehensive Biology Flashcards",
    "cards": [
      {
        "id": "card1",
        "front": "What is the process by which plants convert light energy into chemical energy?",
        "back": "Photosynthesis",
        "difficulty": "hard",
        "tags": ["photosynthesis", "plants", "energy"]
      },
      {
        "id": "card2",
        "front": "True or False: The mitochondria produces most of the cell's ATP.",
        "back": "True",
        "difficulty": "medium",
        "tags": ["mitochondria", "ATP", "energy"]
      },
      {
        "id": "card3",
        "front": "Explain the three stages of cellular respiration.",
        "back": "The three stages are: 1) Glycolysis - breaking down glucose, 2) Krebs cycle - processing pyruvate, 3) Electron transport chain - producing ATP",
        "difficulty": "hard",
        "tags": ["cellular respiration", "glycolysis", "krebs cycle", "electron transport"]
      }
    ],
    "createdAt": "2025-01-25T10:35:00Z",
    "updatedAt": "2025-01-25T10:35:00Z"
  }
}
```

**Test Case: Invalid Space ID (Should Fail)**
```bash
curl -X POST "http://localhost:8000/api/v1/spaces/invalid-uuid/flashcards" \
-H "Content-Type: application/json" \
-H "Authorization: Bearer $TOKEN" \
-d '{
  "title": "Test Flashcards",
  "fileIds": ["'$FILE_ID_1'"]
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

**Test Case: Non-existent Files (Should Fail)**
```bash
curl -X POST "http://localhost:8000/api/v1/spaces/$SPACE_ID/flashcards" \
-H "Content-Type: application/json" \
-H "Authorization: Bearer $TOKEN" \
-d '{
  "title": "Test Flashcards",
  "fileIds": ["00000000-0000-0000-0000-000000000000"]
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

**Test Case: Empty Title (Should Fail)**
```bash
curl -X POST "http://localhost:8000/api/v1/spaces/$SPACE_ID/flashcards" \
-H "Content-Type: application/json" \
-H "Authorization: Bearer $TOKEN" \
-d '{
  "title": "",
  "fileIds": ["'$FILE_ID_1'"]
}'
```

**Expected Response (422 Unprocessable Entity):**
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

### 2. List Flashcards

**Endpoint:** `GET /api/v1/spaces/{spaceId}/flashcards`

**Test Case: List Flashcards (Empty)**
```bash
curl -X GET "http://localhost:8000/api/v1/spaces/$SPACE_ID/flashcards" \
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

**Test Case: List Flashcards with Data**
```bash
# After creating flashcards, list them
curl -X GET "http://localhost:8000/api/v1/spaces/$SPACE_ID/flashcards" \
-H "Authorization: Bearer $TOKEN"
```

**Expected Response (200 OK):**
```json
{
  "data": [
    {
      "id": "flashcard-uuid",
      "spaceId": "space-uuid",
      "title": "Biology Terms Set 1",
      "cardCount": 20,
      "createdAt": "2025-01-25T10:33:00Z"
    },
    {
      "id": "flashcard-uuid-2",
      "spaceId": "space-uuid",
      "title": "Simple Flashcards",
      "cardCount": 20,
      "createdAt": "2025-01-25T10:34:00Z"
    }
  ],
  "meta": {
    "page": 1,
    "limit": 20,
    "total": 2
  }
}
```

**Test Case: List Flashcards with Pagination**
```bash
# Create multiple flashcard sets first
for i in {1..5}; do
  curl -X POST "http://localhost:8000/api/v1/spaces/$SPACE_ID/flashcards" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "title": "Flashcard Set '$i'",
    "fileIds": ["'$FILE_ID_1'"]
  }'
done

# Test pagination
curl -X GET "http://localhost:8000/api/v1/spaces/$SPACE_ID/flashcards?page=1&limit=3" \
-H "Authorization: Bearer $TOKEN"
```

**Expected Response (200 OK):**
```json
{
  "data": [
    // First 3 flashcard sets
  ],
  "meta": {
    "page": 1,
    "limit": 3,
    "total": 7
  }
}
```

### 3. Get Flashcard Detail

**Endpoint:** `GET /api/v1/flashcards/{id}`

**Test Case: Get Flashcard Success**
```bash
# Replace FLASHCARD_ID with actual flashcard ID
export FLASHCARD_ID="flashcard-uuid"

curl -X GET "http://localhost:8000/api/v1/flashcards/$FLASHCARD_ID" \
-H "Authorization: Bearer $TOKEN"
```

**Expected Response (200 OK):**
```json
{
  "data": {
    "id": "flashcard-uuid",
    "spaceId": "space-uuid",
    "title": "Biology Terms Set 1",
    "cards": [
      {
        "id": "card1",
        "front": "What is the process by which plants convert light energy into chemical energy?",
        "back": "Photosynthesis",
        "difficulty": "medium",
        "tags": ["photosynthesis", "plants", "energy"]
      },
      {
        "id": "card2",
        "front": "True or False: Chlorophyll is the green pigment that captures light energy.",
        "back": "True",
        "difficulty": "easy",
        "tags": ["chlorophyll", "pigment", "light"]
      }
    ],
    "createdAt": "2025-01-25T10:33:00Z",
    "updatedAt": "2025-01-25T10:33:00Z"
  }
}
```

**Test Case: Get Non-existent Flashcard**
```bash
curl -X GET "http://localhost:8000/api/v1/flashcards/00000000-0000-0000-0000-000000000000" \
-H "Authorization: Bearer $TOKEN"
```

**Expected Response (404 Not Found):**
```json
{
  "error": {
    "code": "FLASHCARD_NOT_FOUND",
    "message": "Flashcard not found",
    "details": {"flashcard_id": "00000000-0000-0000-0000-000000000000"}
  }
}
```

### 4. Update Flashcard

**Endpoint:** `PATCH /api/v1/flashcards/{id}`

**Test Case: Update Flashcard Title Success**
```bash
curl -X PATCH "http://localhost:8000/api/v1/flashcards/$FLASHCARD_ID" \
-H "Content-Type: application/json" \
-H "Authorization: Bearer $TOKEN" \
-d '{
  "title": "Updated Biology Terms Set 1"
}'
```

**Expected Response (200 OK):**
```json
{
  "data": {
    "id": "flashcard-uuid",
    "spaceId": "space-uuid",
    "title": "Updated Biology Terms Set 1",
    "cards": [
      // Same cards as before
    ],
    "createdAt": "2025-01-25T10:33:00Z",
    "updatedAt": "2025-01-25T10:36:00Z"
  }
}
```

**Test Case: Update Flashcard Cards Success**
```bash
curl -X PATCH "http://localhost:8000/api/v1/flashcards/$FLASHCARD_ID" \
-H "Content-Type: application/json" \
-H "Authorization: Bearer $TOKEN" \
-d '{
  "cards": [
    {
      "id": "card1",
      "front": "What is the primary function of mitochondria?",
      "back": "To produce ATP through cellular respiration",
      "difficulty": "medium",
      "tags": ["mitochondria", "ATP", "cellular respiration"]
    },
    {
      "id": "card2",
      "front": "Which pigment is responsible for capturing light in photosynthesis?",
      "back": "Chlorophyll",
      "difficulty": "easy",
      "tags": ["chlorophyll", "photosynthesis", "pigment"]
    }
  ]
}'
```

**Expected Response (200 OK):**
```json
{
  "data": {
    "id": "flashcard-uuid",
    "spaceId": "space-uuid",
    "title": "Updated Biology Terms Set 1",
    "cards": [
      {
        "id": "card1",
        "front": "What is the primary function of mitochondria?",
        "back": "To produce ATP through cellular respiration",
        "difficulty": "medium",
        "tags": ["mitochondria", "ATP", "cellular respiration"]
      },
      {
        "id": "card2",
        "front": "Which pigment is responsible for capturing light in photosynthesis?",
        "back": "Chlorophyll",
        "difficulty": "easy",
        "tags": ["chlorophyll", "photosynthesis", "pigment"]
      }
    ],
    "createdAt": "2025-01-25T10:33:00Z",
    "updatedAt": "2025-01-25T10:37:00Z"
  }
}
```

**Test Case: Update Non-existent Flashcard**
```bash
curl -X PATCH "http://localhost:8000/api/v1/flashcards/00000000-0000-0000-0000-000000000000" \
-H "Content-Type: application/json" \
-H "Authorization: Bearer $TOKEN" \
-d '{
  "title": "Non-existent Flashcard"
}'
```

**Expected Response (404 Not Found):**
```json
{
  "error": {
    "code": "FLASHCARD_NOT_FOUND",
    "message": "Flashcard not found",
    "details": {"flashcard_id": "00000000-0000-0000-0000-000000000000"}
  }
}
```

### 5. Shuffle Flashcards

**Endpoint:** `POST /api/v1/flashcards/{id}/shuffle`

**Test Case: Shuffle Flashcards Success**
```bash
curl -X POST "http://localhost:8000/api/v1/flashcards/$FLASHCARD_ID/shuffle" \
-H "Authorization: Bearer $TOKEN"
```

**Expected Response (200 OK):**
```json
{
  "data": {
    "flashcardId": "flashcard-uuid",
    "shuffledOrder": ["card2", "card1", "card3", "card4"],
    "shuffledAt": "2025-01-25T10:38:00Z"
  }
}
```

**Test Case: Shuffle Non-existent Flashcard**
```bash
curl -X POST "http://localhost:8000/api/v1/flashcards/00000000-0000-0000-0000-000000000000/shuffle" \
-H "Authorization: Bearer $TOKEN"
```

**Expected Response (404 Not Found):**
```json
{
  "error": {
    "code": "FLASHCARD_NOT_FOUND",
    "message": "Flashcard not found",
    "details": {"flashcard_id": "00000000-0000-0000-0000-000000000000"}
  }
}
```

### 6. Delete Flashcard

**Endpoint:** `DELETE /api/v1/flashcards/{id}`

**Test Case: Delete Flashcard Success**
```bash
curl -X DELETE "http://localhost:8000/api/v1/flashcards/$FLASHCARD_ID" \
-H "Authorization: Bearer $TOKEN"
```

**Expected Response (204 No Content):**
```
(Empty response body)
```

**Verify Deletion:**
```bash
curl -X GET "http://localhost:8000/api/v1/flashcards/$FLASHCARD_ID" \
-H "Authorization: Bearer $TOKEN"
```

**Expected Response (404 Not Found):**
```json
{
  "error": {
    "code": "FLASHCARD_NOT_FOUND",
    "message": "Flashcard not found",
    "details": {"flashcard_id": "flashcard-uuid"}
  }
}
```

**Test Case: Delete Non-existent Flashcard**
```bash
curl -X DELETE "http://localhost:8000/api/v1/flashcards/00000000-0000-0000-0000-000000000000" \
-H "Authorization: Bearer $TOKEN"
```

**Expected Response (404 Not Found):**
```json
{
  "error": {
    "code": "FLASHCARD_NOT_FOUND",
    "message": "Flashcard not found",
    "details": {"flashcard_id": "00000000-0000-0000-0000-000000000000"}
  }
}
```

## Error Cases Testing

### Test Case: Unauthorized Access

```bash
# Test without token
curl -X GET "http://localhost:8000/api/v1/spaces/$SPACE_ID/flashcards"
```

**Expected Response (401 Unauthorized):**
```json
{
  "detail": "Not authenticated"
}
```

### Test Case: Invalid Card Count

```bash
curl -X POST "http://localhost:8000/api/v1/spaces/$SPACE_ID/flashcards" \
-H "Content-Type: application/json" \
-H "Authorization: Bearer $TOKEN" \
-d '{
  "title": "Test Flashcards",
  "fileIds": ["'$FILE_ID_1'"],
  "cardCount": 150
}'
```

**Expected Response (422 Unprocessable Entity):**
```json
{
  "detail": [
    {
      "loc": ["body", "cardCount"],
      "msg": "Card count must be between 1 and 100",
      "type": "value_error"
    }
  ]
}
```

### Test Case: Invalid Difficulty Level

```bash
curl -X POST "http://localhost:8000/api/v1/spaces/$SPACE_ID/flashcards" \
-H "Content-Type: application/json" \
-H "Authorization: Bearer $TOKEN" \
-d '{
  "title": "Test Flashcards",
  "fileIds": ["'$FILE_ID_1'"],
  "difficulty": "expert"
}'
```

**Expected Response (422 Unprocessable Entity):**
```json
{
  "detail": [
    {
      "loc": ["body", "difficulty"],
      "msg": "Difficulty must be one of: easy, medium, hard",
      "type": "value_error"
    }
  ]
}
```

## Complete Workflow Testing

**Test the complete flashcard workflow:**

```bash
# 1. Generate flashcards
FLASHCARD_RESPONSE=$(curl -s -X POST "http://localhost:8000/api/v1/spaces/$SPACE_ID/flashcards" \
-H "Content-Type: application/json" \
-H "Authorization: Bearer $TOKEN" \
-d '{
  "title": "Workflow Test Flashcards",
  "fileIds": ["'$FILE_ID_1'"],
  "cardCount": 10,
  "cardTypes": ["mcq", "tf"],
  "difficulty": "medium"
}')

echo "Created flashcards: $FLASHCARD_RESPONSE"

FLASHCARD_ID=$(echo $FLASHCARD_RESPONSE | jq -r '.data.id')
echo "Flashcard ID: $FLASHCARD_ID"

# 2. List flashcards
curl -s -X GET "http://localhost:8000/api/v1/spaces/$SPACE_ID/flashcards" \
-H "Authorization: Bearer $TOKEN" | jq

# 3. Get flashcard detail
curl -s -X GET "http://localhost:8000/api/v1/flashcards/$FLASHCARD_ID" \
-H "Authorization: Bearer $TOKEN" | jq

# 4. Update flashcard
curl -s -X PATCH "http://localhost:8000/api/v1/flashcards/$FLASHCARD_ID" \
-H "Content-Type: application/json" \
-H "Authorization: Bearer $TOKEN" \
-d '{
  "title": "Updated Workflow Test Flashcards"
}' | jq

# 5. Shuffle flashcards
curl -s -X POST "http://localhost:8000/api/v1/flashcards/$FLASHCARD_ID/shuffle" \
-H "Authorization: Bearer $TOKEN" | jq

# 6. Delete flashcards
curl -s -X DELETE "http://localhost:8000/api/v1/flashcards/$FLASHCARD_ID" \
-H "Authorization: Bearer $TOKEN"

# 7. Verify deletion
curl -s -X GET "http://localhost:8000/api/v1/flashcards/$FLASHCARD_ID" \
-H "Authorization: Bearer $TOKEN" | jq
```

## Performance Testing

### Test Case: Large Flashcard Generation

```bash
# Create a large text file
for i in {1..50}; do
  echo "Chapter $i: This is comprehensive study material for biology. It covers various topics including cell biology, genetics, evolution, and ecology. Each chapter contains detailed explanations and examples to help students understand the concepts thoroughly." >> large_biology.txt
done

# Upload the large file
curl -X POST "http://localhost:8000/api/v1/files/upload" \
-H "Authorization: Bearer $TOKEN" \
-F "folderId=$FOLDER_ID" \
-F "files=@large_biology.txt"

# Get the large file ID
export LARGE_FILE_ID="large-file-uuid"

# Generate large flashcard set
curl -X POST "http://localhost:8000/api/v1/spaces/$SPACE_ID/flashcards" \
-H "Content-Type: application/json" \
-H "Authorization: Bearer $TOKEN" \
-d '{
  "title": "Large Biology Flashcard Set",
  "fileIds": ["'$LARGE_FILE_ID'"],
  "cardCount": 100,
  "cardTypes": ["mcq", "tf", "short_answer"],
  "difficulty": "hard"
}'
```

### Test Case: Concurrent Flashcard Generation

Open multiple terminal windows and run flashcard generation simultaneously:

Terminal 1:
```bash
curl -X POST "http://localhost:8000/api/v1/spaces/$SPACE_ID/flashcards" \
-H "Content-Type: application/json" \
-H "Authorization: Bearer $TOKEN" \
-d '{"title": "Concurrent Flashcard Set 1", "fileIds": ["'$FILE_ID_1'"]}'
```

Terminal 2:
```bash
curl -X POST "http://localhost:8000/api/v1/spaces/$SPACE_ID/flashcards" \
-H "Content-Type: application/json" \
-H "Authorization: Bearer $TOKEN" \
-d '{"title": "Concurrent Flashcard Set 2", "fileIds": ["'$FILE_ID_2'"]}'
```

## Security Testing

### Test Case: Access Other User's Flashcards

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

# Try to access first user's flashcards
curl -X GET "http://localhost:8000/api/v1/flashcards/$FLASHCARD_ID" \
-H "Authorization: Bearer $TOKEN_2"
```

**Expected Response (403 Forbidden):**
```json
{
  "error": {
    "code": "ACCESS_DENIED",
    "message": "You don't have permission to access this flashcard set",
    "details": {"flashcard_id": "flashcard-uuid"}
  }
}
```

## Cleanup

After testing, clean up test data:

```bash
# Delete test files
rm test_biology.txt test_biology2.txt large_biology.txt

# Delete all flashcards (you'll need to get flashcard IDs first)
curl -X GET "http://localhost:8000/api/v1/spaces/$SPACE_ID/flashcards" \
-H "Authorization: Bearer $TOKEN"

# For each flashcard ID in the response:
curl -X DELETE "http://localhost:8000/api/v1/flashcards/{flashcard-id}" \
-H "Authorization: Bearer $TOKEN"
```

## Expected Behavior Summary

1. **Flashcard Generation**: Creates flashcard sets with AI-generated cards
2. **Card Types**: Supports MCQ, True/False, and Short Answer questions
3. **Mock AI Integration**: Generates sample cards and provides realistic content
4. **Validation**: Proper input validation with clear error messages
5. **Authorization**: Ensures users can only access their own flashcards
6. **Pagination**: Supports paginated flashcard listing
7. **Shuffling**: Provides randomized card order for study sessions
8. **Error Handling**: Consistent error response format
9. **Performance**: Handles concurrent requests and large flashcard generation

## Troubleshooting

If you encounter issues:

1. **Server not starting**: Check if port 8000 is available
2. **Database errors**: Ensure the data directory exists and has write permissions
3. **Token expired**: Re-authenticate to get a new token
4. **File upload fails**: Check file size limits and MIME types
5. **Tests failing**: Verify all prerequisite data is created correctly
6. **Card generation**: Mock AI generates sample cards; real AI integration pending

This completes the manual testing guide for the Flashcards functionality! 