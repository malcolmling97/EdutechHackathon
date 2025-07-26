# Quiz Implementation Documentation

This document provides detailed information about the Quiz functionality implementation in the EdutechHackathon backend API.

## Overview

The Quiz functionality allows users to generate AI-powered quizzes from uploaded files, submit answers, and receive automated grading with feedback. This implementation follows the backend developer responsibilities outlined in the data flows documentation.

## Architecture Overview

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Quiz Routes   │───▶│  Quiz Service   │───▶│   Quiz Models   │
│   (FastAPI)     │    │   (Business     │    │  (SQLAlchemy)   │
│                 │    │    Logic)       │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│ Quiz Schemas    │    │  Mock AI        │    │   Database      │
│  (Pydantic)     │    │  Service        │    │  (PostgreSQL)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## Components

### 1. Database Models (`app/models/quiz.py`)

#### Quiz Model
- **Table**: `quizzes`
- **Purpose**: Stores generated quizzes with questions and metadata
- **Key Fields**:
  - `id`: UUID primary key
  - `space_id`: Foreign key to spaces table
  - `title`: Quiz title
  - `questions`: JSON field containing quiz questions
  - `file_ids`: JSON field with source file references
  - `created_at`: Creation timestamp

#### QuizSubmission Model
- **Table**: `quiz_submissions`
- **Purpose**: Stores user submissions and grading results
- **Key Fields**:
  - `id`: UUID primary key
  - `quiz_id`: Foreign key to quizzes table
  - `user_id`: Foreign key to users table
  - `answers`: JSON field with user answers
  - `score`: Calculated score (float)
  - `feedback`: JSON field with grading feedback
  - `submitted_at`: Submission timestamp

#### Relationships
- Quiz → Space (many-to-one)
- Quiz → QuizSubmission (one-to-many, cascade delete)
- QuizSubmission → User (many-to-one)

### 2. Pydantic Schemas (`app/schemas/quiz.py`)

#### Request Schemas
- **QuizCreate**: Quiz generation parameters
  - Validates file IDs are valid UUIDs
  - Ensures at least one question type is specified
  - Supports default values for optional fields

- **QuizSubmission**: Answer submission data
  - Validates answers format
  - Removes duplicate answers for same question
  - Ensures at least one answer is provided

#### Response Schemas
- **QuizResponse**: Quiz data in API responses
- **QuizSubmissionResponse**: Grading results
- **QuizListResponse**: Paginated quiz listings

#### Validation Features
- UUID format validation for file IDs
- Question type enumeration validation
- Title trimming and empty string detection
- Answer deduplication by question ID

### 3. Service Layer (`app/services/quiz.py`)

#### QuizService Class
Implements all business logic for quiz operations:

**Key Methods:**
- `generate_quiz()`: Creates new quiz from file content
- `list_quizzes()`: Paginated quiz listing with ownership verification
- `get_quiz()`: Retrieves individual quiz with access control
- `submit_quiz()`: Processes answer submissions and grading
- `delete_quiz()`: Removes quiz and all submissions

**Security Features:**
- Ownership verification through space → folder relationships
- UUID validation for all ID parameters
- Access control on all operations
- Consistent error handling with standardized error codes

#### MockAIService Class
Provides mock AI functionality for development and testing:

**generate_quiz_questions():**
- Generates mock questions based on parameters
- Supports MCQ, True/False, and Short Answer types
- Creates realistic question structures
- Uses configurable question counts and difficulty levels

**grade_quiz_submission():**
- Automatic grading for MCQ and True/False questions
- Mock AI grading for short answer questions
- Partial credit support
- Detailed feedback generation

### 4. API Routes (`app/api/routes/quiz.py`)

#### Endpoints Implemented

| Method | Path | Purpose | Status Codes |
|--------|------|---------|-------------|
| POST | `/spaces/{space_id}/quizzes` | Generate quiz | 201, 400, 401, 403, 404, 422 |
| GET | `/spaces/{space_id}/quizzes` | List quizzes | 200, 401, 403, 404, 422 |
| GET | `/quizzes/{quiz_id}` | Get quiz detail | 200, 401, 403, 404, 422 |
| POST | `/quizzes/{quiz_id}/submit` | Submit answers | 201, 400, 401, 403, 404, 422 |
| DELETE | `/quizzes/{quiz_id}` | Delete quiz | 204, 401, 403, 404, 422 |

#### Route Features
- Comprehensive OpenAPI documentation
- Input validation with FastAPI dependencies
- Consistent error handling
- Proper HTTP status codes
- Request/response examples in documentation

### 5. Database Integration

#### Table Creation
Quiz models are automatically registered with SQLAlchemy through the database initialization in `app/core/database.py`.

#### Relationships
- Space model updated to include `quizzes` relationship
- Cascade deletion ensures data integrity
- Foreign key constraints maintain referential integrity

## Implementation Details

### Quiz Generation Flow

1. **Input Validation**
   - Validate space ID format and existence
   - Verify user ownership through folder relationship
   - Check file IDs exist and belong to user
   - Validate quiz generation parameters

2. **Content Processing**
   - Retrieve file text content from database
   - Pass content to MockAIService
   - Generate questions based on parameters

3. **Database Storage**
   - Create quiz record with generated questions
   - Store file references for traceability
   - Return formatted response

### Answer Submission Flow

1. **Quiz Validation**
   - Verify quiz exists and user has access
   - Validate answer format and structure

2. **Grading Process**
   - Automatic grading for objective questions
   - Mock AI grading for subjective questions
   - Calculate total score and generate feedback

3. **Result Storage**
   - Save submission to database
   - Include detailed feedback for each question
   - Return grading results to user

### Security Implementation

#### Access Control
- All operations verify user ownership through space → folder relationships
- UUID validation prevents injection attacks
- Consistent permission checking across all endpoints

#### Error Handling
- Standardized error response format
- Specific error codes for different failure scenarios
- Detailed error messages for debugging

## Mock AI Integration

### Design Philosophy
The mock AI service is designed to:
- Provide realistic responses for development and testing
- Demonstrate the expected AI integration patterns
- Allow backend development without OpenAI API dependencies
- Maintain consistent interfaces for future AI integration

### Question Generation
```python
# Mock AI generates questions like:
{
    "id": "q1",
    "type": "mcq",
    "prompt": "Mock MCQ question 1 about Photosynthesis Quiz?",
    "choices": ["Option A", "Option B", "Option C", "Option D"],
    "answer": "A"
}
```

### Grading Logic
- MCQ/True-False: Exact match comparison
- Short Answer: Length-based scoring with partial credit
- Feedback generation based on answer correctness

## Testing

### Automated Testing
- **27 test cases** covering all functionality
- Test fixtures for consistent test data
- Permission testing with multiple users
- Validation error testing
- Edge case coverage

### Test Categories
1. **Quiz Generation Tests**
   - Success scenarios with various parameters
   - Invalid input validation
   - Permission checking
   - File ownership verification

2. **Quiz Listing Tests**
   - Empty space handling
   - Pagination functionality
   - Access control verification

3. **Quiz Detail Tests**
   - Successful retrieval
   - Non-existent quiz handling
   - Permission verification

4. **Answer Submission Tests**
   - Complete submissions
   - Partial submissions
   - Validation errors
   - Grading accuracy

5. **Quiz Deletion Tests**
   - Successful deletion
   - Cascade deletion verification
   - Permission checking

### Manual Testing
Comprehensive manual testing guide available in `QUIZ_MANUAL_TESTING.md` with:
- Step-by-step curl commands
- Expected responses
- Error scenarios
- Performance testing
- API documentation verification

## Database Schema

### Quiz Table
```sql
CREATE TABLE quizzes (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    space_id UUID NOT NULL REFERENCES spaces(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    questions JSONB NOT NULL DEFAULT '[]',
    file_ids JSONB NOT NULL DEFAULT '[]',
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_quizzes_space_id ON quizzes(space_id);
CREATE INDEX idx_quizzes_created_at ON quizzes(created_at);
```

### Quiz Submissions Table
```sql
CREATE TABLE quiz_submissions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    quiz_id UUID NOT NULL REFERENCES quizzes(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    answers JSONB NOT NULL DEFAULT '[]',
    score FLOAT NOT NULL DEFAULT 0.0,
    feedback JSONB NOT NULL DEFAULT '[]',
    submitted_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_quiz_submissions_quiz_id ON quiz_submissions(quiz_id);
CREATE INDEX idx_quiz_submissions_user_id ON quiz_submissions(user_id);
CREATE INDEX idx_quiz_submissions_submitted_at ON quiz_submissions(submitted_at);
```

## Configuration

### Environment Variables
No additional environment variables required for basic Quiz functionality. The mock AI service operates without external dependencies.

### Feature Flags
Quiz functionality can be controlled through existing configuration:
- `QUIZ_FEATURE_ENABLED`: Enable/disable quiz endpoints
- `AI_QUIZ_GENERATION_ENABLED`: Control AI integration

## Performance Considerations

### Database Optimization
- Indexes on foreign keys for efficient joins
- JSON fields for flexible question/answer storage
- Cascade deletion for data integrity

### Scalability
- Stateless service design
- Efficient pagination implementation
- Mock AI service eliminates external API dependencies

### Memory Usage
- JSON serialization for complex data structures
- Efficient SQLAlchemy query patterns
- Minimal object creation in service layer

## Future Enhancements

### AI Integration Readiness
The current mock implementation can be easily replaced with real AI integration:

1. **Replace MockAIService methods**:
   ```python
   # Current mock implementation
   def generate_quiz_questions(self, file_contents, params):
       # Mock logic
   
   # Future AI implementation
   def generate_quiz_questions(self, file_contents, params):
       # OpenAI API calls
   ```

2. **Add configuration for AI models**
3. **Implement error handling for AI service failures**
4. **Add retry logic for API calls**

### Additional Features
- Question difficulty analysis
- Learning analytics
- Question bank management
- Collaborative quiz creation
- Export functionality

## Error Codes Reference

| Code | Description | HTTP Status |
|------|-------------|-------------|
| `INVALID_UUID` | Invalid ID format | 422 |
| `SPACE_NOT_FOUND` | Space does not exist | 404 |
| `QUIZ_NOT_FOUND` | Quiz does not exist | 404 |
| `FILE_NOT_FOUND` | File does not exist | 404 |
| `FORBIDDEN` | Access denied | 403 |
| `VALIDATION_ERROR` | Input validation failed | 422 |

## API Documentation

The Quiz API is fully documented with OpenAPI/Swagger:
- Interactive documentation at `/docs`
- ReDoc documentation at `/redoc`
- OpenAPI specification at `/openapi.json`

Each endpoint includes:
- Parameter descriptions
- Request/response schemas
- Example requests and responses
- Error scenario documentation

## Conclusion

The Quiz functionality implementation provides a complete, production-ready system for quiz generation and management. The mock AI integration allows for immediate development and testing while maintaining clear interfaces for future AI service integration. The comprehensive testing suite ensures reliability and maintainability of the codebase. 