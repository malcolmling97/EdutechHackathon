# Open-ended Questions Manual Testing Guide

This document provides comprehensive manual testing instructions for the Open-ended Questions functionality implemented for the EdutechHackathon backend API.

## Overview

The Open-ended Questions system provides AI-powered generation of long-form questions with detailed rubrics, automated grading with feedback, and comprehensive answer analysis. It supports various question types with customizable difficulty levels and word count requirements.

## Prerequisites

1. **Server Running**: Start the FastAPI development server
   ```bash
   cd EdutechHackathon/backend
   uvicorn app.main:app --reload
   ```

2. **Authentication Token**: Get a valid JWT token through registration/login
3. **Test Files**: Prepare sample files (PDF, DOCX, TXT, MD) for testing
4. **API Client**: Use curl, Postman, or similar tool

## Testing Endpoints

### 1. Authentication Setup

First, create a user account and get an authentication token:

```bash
# Register a new user
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "testpassword123",
    "name": "Test User"
  }'

# Login to get token
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "testpassword123"
  }'
```

**Expected Response**: Save the JWT token from the login response for subsequent requests.

### 2. Create Test Environment

Create a folder and space for open-ended questions:

```bash
# Create folder
curl -X POST "http://localhost:8000/api/v1/folders" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "title": "Open-ended Test Folder",
    "description": "Folder for testing open-ended questions"
  }'

# Create openended space
curl -X POST "http://localhost:8000/api/v1/folders/YOUR_FOLDER_ID/spaces" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "type": "openended",
    "title": "Test Open-ended Space",
    "settings": {}
  }'
```

**Expected Response**: 
- Status: `201 Created`
- Response body contains folder and space data with `id` fields
- Save both IDs for subsequent tests

### 3. Upload Test Files

Upload files to use for question generation:

```bash
# Upload test files
curl -X POST "http://localhost:8000/api/v1/files/upload" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -F "folder_id=YOUR_FOLDER_ID" \
  -F "files=@test_document.pdf" \
  -F "files=@notes.txt"
```

**Expected Response**:
- Status: `201 Created`
- Response body: Array with uploaded file metadata
- Save file IDs for question generation

### 4. Generate Open-ended Questions Tests

#### 4.1 Generate Basic Questions

```bash
curl -X POST "http://localhost:8000/api/v1/spaces/YOUR_SPACE_ID/openended" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "title": "Test Open-ended Questions",
    "file_ids": ["YOUR_FILE_ID_1", "YOUR_FILE_ID_2"],
    "question_count": 3,
    "question_types": ["short_answer"],
    "difficulty": "medium"
  }'
```

**Expected Response**:
- Status: `201 Created`
- Response body contains generated questions with:
  - `id`: Unique question set ID
  - `space_id`: Space identifier
  - `title`: Question set title
  - `questions`: Array of generated questions with prompts and rubrics
  - `file_ids`: Source files used
  - `created_at`: Creation timestamp

#### 4.2 Generate Questions with Custom Parameters

```bash
curl -X POST "http://localhost:8000/api/v1/spaces/YOUR_SPACE_ID/openended" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "title": "Advanced Open-ended Questions",
    "file_ids": ["YOUR_FILE_ID_1"],
    "question_count": 5,
    "question_types": ["short_answer"],
    "difficulty": "hard"
  }'
```

**Expected Response**:
- Status: `201 Created`
- 5 questions generated with "hard" difficulty
- More complex prompts and detailed rubrics

#### 4.3 Generate Questions with Invalid Parameters

```bash
# Test with empty file_ids
curl -X POST "http://localhost:8000/api/v1/spaces/YOUR_SPACE_ID/openended" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "title": "Invalid Questions",
    "file_ids": [],
    "question_count": 3
  }'
```

**Expected Response**:
- Status: `422 Unprocessable Entity`
- Validation error about empty file_ids

#### 4.4 Generate Questions with Non-existent Files

```bash
curl -X POST "http://localhost:8000/api/v1/spaces/YOUR_SPACE_ID/openended" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "title": "Invalid File Questions",
    "file_ids": ["non-existent-file-id"],
    "question_count": 3
  }'
```

**Expected Response**:
- Status: `404 Not Found`
- Error message about file not found

### 5. List Open-ended Questions Tests

#### 5.1 List Questions in Space

```bash
curl -X GET "http://localhost:8000/api/v1/spaces/YOUR_SPACE_ID/openended" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

**Expected Response**:
- Status: `200 OK`
- Response body contains `data` array with question sets
- `meta` object with pagination information

#### 5.2 List Questions with Pagination

```bash
curl -X GET "http://localhost:8000/api/v1/spaces/YOUR_SPACE_ID/openended?page=1&limit=2" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

**Expected Response**:
- Status: `200 OK`
- Maximum 2 question sets in response
- Pagination metadata: `page=1`, `limit=2`, `total` count

#### 5.3 List Questions in Empty Space

```bash
# Create new empty space
curl -X POST "http://localhost:8000/api/v1/folders/YOUR_FOLDER_ID/spaces" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "type": "openended",
    "title": "Empty Space",
    "settings": {}
  }'

# List questions in empty space
curl -X GET "http://localhost:8000/api/v1/spaces/NEW_EMPTY_SPACE_ID/openended" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

**Expected Response**:
- Status: `200 OK`
- Empty `data` array
- `meta.total` should be 0

### 6. Get Question Set Details Tests

#### 6.1 Get Question Set by ID

```bash
curl -X GET "http://localhost:8000/api/v1/openended/YOUR_QUESTION_SET_ID" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

**Expected Response**:
- Status: `200 OK`
- Complete question set details including:
  - All questions with prompts
  - Detailed rubrics for each question
  - Word count requirements
  - Source file information

#### 6.2 Get Non-existent Question Set

```bash
curl -X GET "http://localhost:8000/api/v1/openended/non-existent-id" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

**Expected Response**:
- Status: `404 Not Found`
- Error message about question set not found

### 7. Submit Answers Tests

#### 7.1 Submit Complete Answers

```bash
curl -X POST "http://localhost:8000/api/v1/openended/YOUR_QUESTION_SET_ID/submit" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "answers": [
      {
        "question_id": "question_1",
        "answer": "This is a comprehensive answer that addresses the question thoroughly. It includes multiple points and demonstrates understanding of the topic."
      },
      {
        "question_id": "question_2", 
        "answer": "Another detailed response that meets the word count requirements and shows depth of knowledge."
      }
    ]
  }'
```

**Expected Response**:
- Status: `201 Created`
- Response body contains:
  - `score`: Overall score (0-100)
  - `total_questions`: Number of questions
  - `feedback`: Detailed feedback for each answer
  - `rubric_scores`: Individual rubric component scores
  - `submitted_at`: Submission timestamp

#### 7.2 Submit Answers with Word Count Violations

```bash
curl -X POST "http://localhost:8000/api/v1/openended/YOUR_QUESTION_SET_ID/submit" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "answers": [
      {
        "question_id": "question_1",
        "answer": "Too short"
      }
    ]
  }'
```

**Expected Response**:
- Status: `422 Unprocessable Entity`
- Validation error about minimum word count requirement

#### 7.3 Submit Incomplete Answers

```bash
curl -X POST "http://localhost:8000/api/v1/openended/YOUR_QUESTION_SET_ID/submit" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "answers": [
      {
        "question_id": "question_1",
        "answer": "This is a complete answer for the first question."
      }
    ]
  }'
```

**Expected Response**:
- Status: `422 Unprocessable Entity`
- Validation error about missing answers for required questions

### 8. Get Answer History Tests

#### 8.1 Get User's Answers and Grades

```bash
curl -X GET "http://localhost:8000/api/v1/openended/YOUR_QUESTION_SET_ID/answers" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

**Expected Response**:
- Status: `200 OK`
- Response body contains:
  - `answers`: Array of submitted answers
  - `score`: Overall grade
  - `feedback`: Detailed feedback for each answer
  - `rubric_breakdown`: Individual rubric scores
  - `submitted_at`: Submission timestamp

#### 8.2 Get Answers for Question Set with No Submissions

```bash
# Create new question set and try to get answers without submitting
curl -X GET "http://localhost:8000/api/v1/openended/NEW_QUESTION_SET_ID/answers" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

**Expected Response**:
- Status: `404 Not Found`
- Error message about no submissions found

### 9. Delete Question Set Tests

#### 9.1 Delete Question Set

```bash
curl -X DELETE "http://localhost:8000/api/v1/openended/YOUR_QUESTION_SET_ID" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

**Expected Response**:
- Status: `204 No Content`
- Question set and all associated data deleted

#### 9.2 Delete Non-existent Question Set

```bash
curl -X DELETE "http://localhost:8000/api/v1/openended/non-existent-id" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

**Expected Response**:
- Status: `404 Not Found`
- Error message about question set not found

### 10. Authorization Tests

#### 10.1 Access Question Set from Different User

1. Create second user account
2. Attempt to access question sets from first user

```bash
curl -X GET "http://localhost:8000/api/v1/openended/FIRST_USER_QUESTION_SET_ID" \
  -H "Authorization: Bearer SECOND_USER_JWT_TOKEN"
```

**Expected Response**:
- Status: `403 Forbidden`
- Error message about access denied

#### 10.2 Generate Questions in Other User's Space

```bash
curl -X POST "http://localhost:8000/api/v1/spaces/FIRST_USER_SPACE_ID/openended" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer SECOND_USER_JWT_TOKEN" \
  -d '{
    "title": "Unauthorized Questions",
    "file_ids": ["SOME_FILE_ID"],
    "question_count": 3
  }'
```

**Expected Response**:
- Status: `403 Forbidden`
- Error message about space access

#### 10.3 Submit Answers to Other User's Questions

```bash
curl -X POST "http://localhost:8000/api/v1/openended/FIRST_USER_QUESTION_SET_ID/submit" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer SECOND_USER_JWT_TOKEN" \
  -d '{
    "answers": [
      {
        "question_id": "question_1",
        "answer": "Unauthorized submission attempt"
      }
    ]
  }'
```

**Expected Response**:
- Status: `403 Forbidden`
- Error message about access denied

### 11. Error Handling Tests

#### 11.1 Missing Authentication

```bash
curl -X GET "http://localhost:8000/api/v1/openended/YOUR_QUESTION_SET_ID"
```

**Expected Response**:
- Status: `401 Unauthorized`
- Error about missing credentials

#### 11.2 Invalid Question Set ID Format

```bash
curl -X GET "http://localhost:8000/api/v1/openended/invalid-uuid-format" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

**Expected Response**:
- Status: `422 Unprocessable Entity`
- Error about invalid UUID format

#### 11.3 Invalid Space ID

```bash
curl -X POST "http://localhost:8000/api/v1/spaces/invalid-space-id/openended" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "title": "Test",
    "file_ids": ["YOUR_FILE_ID"],
    "question_count": 3
  }'
```

**Expected Response**:
- Status: `422 Unprocessable Entity`
- Error about invalid space ID format

## Mock AI Service Verification

### Question Generation Testing

1. **Verify Mock Questions**: Check that generated questions are realistic
   - Questions should be relevant to uploaded content
   - Prompts should be clear and specific
   - Rubrics should have appropriate criteria

2. **Rubric Validation**: Verify rubric structure
   - Each question should have a detailed rubric
   - Rubric should include multiple criteria
   - Weight distribution should be logical

### Grading System Testing

1. **Answer Evaluation**: Submit various quality answers
   - Test excellent answers (should score high)
   - Test poor answers (should score low)
   - Test medium quality answers

2. **Rubric Scoring**: Verify individual rubric components
   - Check that each rubric criterion is evaluated
   - Verify weight calculations
   - Confirm total score accuracy

## Performance Testing

### Question Generation Performance

1. Generate questions from large files (10+ pages)
2. Monitor generation time
3. Verify system remains responsive

### Grading Performance

1. Submit answers with high word counts
2. Test multiple simultaneous submissions
3. Verify grading response time

## Security Testing

### Input Validation

1. Submit answers with special characters
2. Test with very long answers
3. Verify XSS protection

### Access Control

1. Verify users can only access their own question sets
2. Test space ownership enforcement
3. Confirm JWT token validation

## Database Verification

After running tests, verify database state:

```sql
-- Check open-ended question sets
SELECT id, title, space_id, created_at FROM open_ended_questions;

-- Check answer submissions
SELECT id, question_set_id, user_id, score, submitted_at FROM open_ended_answers;

-- Check cascade deletion
SELECT COUNT(*) FROM open_ended_questions WHERE deleted_at IS NULL;
```

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure all dependencies installed
   ```bash
   pip install -r requirements.txt
   ```

2. **Database Errors**: Ensure openended model is imported
   ```python
   from app.models import openended  # In database.py create_tables()
   ```

3. **Mock AI Errors**: Verify MockAIService is properly configured
   ```python
   # Check service initialization in openended.py
   ```

4. **Validation Errors**: Check request body format
   - Ensure all required fields are present
   - Verify UUID formats are correct
   - Check word count requirements

## Success Criteria

All tests should pass with:
- ✅ Correct HTTP status codes
- ✅ Proper error messages for failures
- ✅ Complete question generation with rubrics
- ✅ Successful answer submission and grading
- ✅ Proper access control enforcement
- ✅ Database records created correctly
- ✅ Mock AI service functioning properly
- ✅ Comprehensive feedback and scoring

## Implementation Status

**✅ Completed Features:**
- Open-ended question generation with AI integration
- Detailed rubric creation for each question
- Answer submission with word count validation
- Automated grading with detailed feedback
- Rubric-based scoring system
- Answer history and grade retrieval
- Question set management (CRUD operations)
- Access control and authorization
- Comprehensive error handling
- Mock AI service for development

**📝 Notes:**
- All endpoints follow the API specification
- Implementation uses MockAIService for development
- Ready for integration with real AI services (OpenAI API)
- Comprehensive validation and security measures
- Full TDD approach with comprehensive test coverage 