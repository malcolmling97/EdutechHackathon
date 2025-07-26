# REST API Specification

## 1. URI Conventions & Versioning

| Concept | Convention | Example |
| :---- | :---- | :---- |
| Base URL | `/api/v1` | `/api/v1/folders` |
| Resource collection | plural noun | `/spaces` |
| Single resource | `/resource/{id}` | `/files/42` |
| Nested sub-resource | `/parent/{id}/children` | `/folders/7/spaces` |
| Soft delete | `DELETE` verb → 204 No Content | `/quizzes/15` |
| Hard purge (admin) | `DELETE /{id}?force=true` | `/files/42?force=true` |
| Pagination | `?page=1&limit=20` |  |
| Filtering | `?type=pdf` |  |
| Search | `?q=photosynthesis` |  |

## 2. Authentication & Headers

```
Authorization: Bearer <token>        // simple JWT for hackathon
Content-Type: application/json
X-User-Id: <uuid>                    // mirrors current header pattern
```

## 3. JSON Envelope Pattern

All successful responses wrap data, while errors share a uniform shape.

**Success Response:**
```json
{
  "data": { /* resource(s) */ },
  "meta": { "page": 1, "limit": 20, "total": 63 }
}
```

**Error Response:**
```json
{
  "error": {
    "code": "FILE_TOO_LARGE",
    "message": "Maximum upload size is 25 MB.",
    "details": null
  }
}
```

## 4. Resource Schemas

### 4.1 User

```json
{
  "id": "uuid",
  "name": "Alice Tan",
  "email": "alice@example.com",
  "createdAt": "ISO-8601",
  "updatedAt": "ISO-8601"
}
```

### 4.2 Folder

```json
{
  "id": "uuid",
  "ownerId": "uuid",
  "title": "Biology 101",
  "description": "Semester 1 lecture notes",
  "createdAt": "ISO-8601"
}
```

### 4.3 Space

```json
{
  "id": "uuid",
  "folderId": "uuid",
  "type": "chat | quiz | notes | openended | flashcards | studyguide",
  "title": "Photosynthesis Q&A",
  "settings": { /* per-type options */ },
  "createdAt": "ISO-8601"
}
```

### 4.4 File

```json
{
  "id": "uuid",
  "folderId": "uuid",
  "name": "chapter-3.pdf",
  "mime": "application/pdf",
  "size": 1324020,
  "text": "...extracted plaintext...",
  "createdAt": "ISO-8601"
}
```

### 4.5 Chat Message

```json
{
  "id": "uuid",
  "spaceId": "uuid",
  "role": "user | assistant",
  "content": "Answer with citations...",
  "sources": [
    { "fileId": "uuid", "page": 12 }
  ],
  "createdAt": "ISO-8601"
}
```

### 4.6 Quiz

```json
{
  "id": "uuid",
  "spaceId": "uuid",
  "title": "Chapter 3 quiz",
  "questions": [
    {
      "id": "uuid",
      "type": "mcq | tf | short",
      "prompt": "What is chlorophyll?",
      "choices": ["..."],
      "answer": "B"
    }
  ],
  "createdAt": "ISO-8601"
}
```

### 4.7 Notes

```json
{
  "id": "uuid",
  "spaceId": "uuid",
  "format": "markdown",
  "content": "# Summary ...",
  "createdAt": "ISO-8601",
  "updatedAt": "ISO-8601"
}
```

### 4.8 Open-ended Question

```json
{
  "id": "uuid",
  "spaceId": "uuid",
  "title": "Chapter 3 Long Questions",
  "questions": [
    {
      "id": "uuid",
      "prompt": "Explain the process of photosynthesis in detail, including the light-dependent and light-independent reactions.",
      "maxWords": 500,
      "rubric": {
        "criteria": [
          {
            "name": "Understanding of light reactions",
            "weight": 0.3,
            "description": "Demonstrates clear understanding of photosystem I and II"
          },
          {
            "name": "Calvin cycle explanation",
            "weight": 0.3,
            "description": "Accurately describes the Calvin cycle steps"
          },
          {
            "name": "Overall coherence",
            "weight": 0.4,
            "description": "Answer is well-structured and coherent"
          }
        ]
      }
    }
  ],
  "createdAt": "ISO-8601"
}
```

### 4.9 Open-ended Answer & Grade

```json
{
  "id": "uuid",
  "questionId": "uuid",
  "userId": "uuid",
  "answer": "Photosynthesis is a complex process...",
  "wordCount": 487,
  "grade": {
    "totalScore": 85,
    "maxScore": 100,
    "breakdown": [
      {
        "criterion": "Understanding of light reactions",
        "score": 25,
        "maxScore": 30,
        "feedback": "Good explanation of photosystems but missing detail on electron transport chain"
      }
    ],
    "overallFeedback": "Strong answer with good understanding of the key concepts...",
    "gradedAt": "ISO-8601"
  },
  "submittedAt": "ISO-8601"
}
```

### 4.10 Flashcard

```json
{
  "id": "uuid",
  "spaceId": "uuid",
  "title": "Biology Terms Set 1",
  "cards": [
    {
      "id": "uuid",
      "front": "What is chlorophyll?",
      "back": "A green pigment found in plants that captures light energy for photosynthesis",
      "difficulty": "easy | medium | hard",
      "tags": ["photosynthesis", "pigments"]
    }
  ],
  "createdAt": "ISO-8601",
  "updatedAt": "ISO-8601"
}
```

### 4.11 Study Guide

```json
{
  "id": "uuid",
  "spaceId": "uuid",
  "title": "Final Exam Study Plan",
  "deadline": "ISO-8601",
  "totalStudyHours": 40,
  "schedule": [
    {
      "id": "uuid",
      "date": "ISO-8601",
      "startTime": "09:00",
      "endTime": "11:00",
      "topic": "Photosynthesis",
      "activities": [
        {
          "type": "review",
          "resourceId": "uuid",
          "resourceType": "file",
          "duration": 60
        },
        {
          "type": "flashcards",
          "resourceId": "uuid",
          "resourceType": "flashcard",
          "duration": 60
        }
      ],
      "completed": false
    }
  ],
  "preferences": {
    "dailyStudyHours": 2,
    "preferredTimes": ["morning", "evening"],
    "breakInterval": 25,
    "studyMethods": ["reading", "flashcards", "practice"]
  },
  "progress": {
    "completedHours": 12,
    "completedSessions": 6,
    "totalSessions": 20
  },
  "createdAt": "ISO-8601",
  "updatedAt": "ISO-8601"
}
```

## 5. Endpoint Catalogue

### 5.1 Authentication

| Method | Path | Description |
| :---- | :---- | :---- |
| POST | `/auth/register` | Create user account |
| POST | `/auth/login` | Obtain JWT |
| POST | `/auth/logout` | Invalidate token |
| GET | `/auth/profile` | Current user profile |

### 5.2 Folders

| Method | Path | Purpose |
| :---- | :---- | :---- |
| GET | `/folders` | List user folders |
| POST | `/folders` | Create folder |
| GET | `/folders/{id}` | Retrieve folder |
| PATCH | `/folders/{id}` | Update metadata |
| DELETE | `/folders/{id}` | Delete folder (+ cascade) |

### 5.3 Spaces

| Method | Path | Purpose |
| :---- | :---- | :---- |
| GET | `/folders/{folderId}/spaces` | List spaces in folder |
| POST | `/folders/{folderId}/spaces` | Create space (`type` required) |
| GET | `/spaces/{id}` | Retrieve space |
| PATCH | `/spaces/{id}` | Rename / update settings |
| DELETE | `/spaces/{id}` | Delete space |

### 5.4 Files

| Method | Path | Purpose |
| :---- | :---- | :---- |
| POST | `/files/upload` (multipart) | Upload one or many |
| GET | `/folders/{folderId}/files` | List files in folder |
| GET | `/files/{id}` | File metadata |
| GET | `/files/{id}/content` | Raw or extracted text |
| DELETE | `/files/{id}` | Delete file |

### 5.5 Chat

| Method | Path | Purpose |
| :---- | :---- | :---- |
| POST | `/spaces/{spaceId}/messages` | Send user message & stream assistant reply |
| GET | `/spaces/{spaceId}/messages` | History (paginated) |
| DELETE | `/messages/{id}` | Remove single message |

### 5.6 Quiz

| Method | Path | Purpose |
| :---- | :---- | :---- |
| POST | `/spaces/{spaceId}/quizzes` | Generate quiz from selected fields + params |
| GET | `/spaces/{spaceId}/quizzes` | List quizzes |
| GET | `/quizzes/{id}` | Quiz detail |
| POST | `/quizzes/{id}/submit` | Grade answers |
| DELETE | `/quizzes/{id}` | Delete quiz |

### 5.7 Notes

| Method | Path | Purpose |
| :---- | :---- | :---- |
| POST | `/spaces/{spaceId}/notes` | Generate notes |
| GET | `/spaces/{spaceId}/notes` | List notes |
| GET | `/notes/{id}` | Retrieve note |
| PATCH | `/notes/{id}` | Update content |
| DELETE | `/notes/{id}` | Delete note |

### 5.8 Open-ended Questions

| Method | Path | Purpose |
| :---- | :---- | :---- |
| POST | `/spaces/{spaceId}/openended` | Generate open-ended questions |
| GET | `/spaces/{spaceId}/openended` | List open-ended question sets |
| GET | `/openended/{id}` | Retrieve question set |
| POST | `/openended/{id}/submit` | Submit answers for AI grading |
| GET | `/openended/{id}/answers` | Get user's submitted answers and grades |
| DELETE | `/openended/{id}` | Delete question set |

### 5.9 Flashcards

| Method | Path | Purpose |
| :---- | :---- | :---- |
| POST | `/spaces/{spaceId}/flashcards` | Generate flashcard deck |
| GET | `/spaces/{spaceId}/flashcards` | List flashcard decks |
| GET | `/flashcards/{id}` | Retrieve flashcard deck |
| PATCH | `/flashcards/{id}` | Update deck or individual cards |
| DELETE | `/flashcards/{id}` | Delete flashcard deck |
| POST | `/flashcards/{id}/shuffle` | Get shuffled card order for study session |

### 5.10 Study Guides

| Method | Path | Purpose |
| :---- | :---- | :---- |
| POST | `/spaces/{spaceId}/studyguides` | Create study schedule |
| GET | `/spaces/{spaceId}/studyguides` | List study guides |
| GET | `/studyguides/{id}` | Retrieve study guide |
| PATCH | `/studyguides/{id}` | Update schedule or mark sessions complete |
| DELETE | `/studyguides/{id}` | Delete study guide |
| POST | `/studyguides/{id}/sessions/{sessionId}/complete` | Mark study session as completed |

## 6. Example Contracts

### 6.1 Create Space

**Request**
```http
POST /api/v1/folders/7/spaces
Content-Type: application/json

{
  "type": "chat",
  "title": "Exam Prep Chat"
}
```

**Success 201**
```json
{
  "data": {
    "id": "bd89...",
    "folderId": "7",
    "type": "chat",
    "title": "Exam Prep Chat",
    "settings": {},
    "createdAt": "2025-07-13T00:02:11Z"
  }
}
```

### 6.2 Delete File

**Request**
```http
DELETE /api/v1/files/42
```

**Response**
```
204 No Content
```

**To purge permanently:**
```http
DELETE /api/v1/files/42?force=true
```

### 6.3 Stream Chat Reply (SSE)

**Request**
```http
POST /api/v1/spaces/bd89/messages?stream=true
Content-Type: application/json

{
  "content": "Explain photosynthesis",
  "role": "user"
}
```

**Response**
```
Content-Type: text/event-stream

data: {"role":"assistant","content":"Photosynthesis converts ..."}
data: {"done":true}
```

### 6.4 Upload Files

**Request**
```http
POST /api/v1/files/upload
Content-Type: multipart/form-data

folderId=123&files=@chapter1.pdf&files=@chapter2.pdf
```

**Success 201**
```json
{
  "data": [
    {
      "id": "uuid1",
      "folderId": "123",
      "name": "chapter1.pdf",
      "mime": "application/pdf",
      "size": 1024000,
      "createdAt": "2025-01-15T10:30:00Z"
    },
    {
      "id": "uuid2",
      "folderId": "123",
      "name": "chapter2.pdf",
      "mime": "application/pdf",
      "size": 2048000,
      "createdAt": "2025-01-15T10:30:01Z"
    }
  ]
}
```

### 6.5 Generate Quiz

**Request**
```http
POST /api/v1/spaces/bd89/quizzes
Content-Type: application/json

{
  "title": "Chapter 3 Quiz",
  "fileIds": ["uuid1", "uuid2"],
  "questionCount": 10,
  "questionTypes": ["mcq", "tf"],
  "difficulty": "medium"
}
```

**Success 201**
```json
{
  "data": {
    "id": "quiz-uuid",
    "spaceId": "bd89",
    "title": "Chapter 3 Quiz",
    "questions": [
      {
        "id": "q1",
        "type": "mcq",
        "prompt": "What is chlorophyll?",
        "choices": ["A green pigment", "A protein", "A carbohydrate", "A lipid"],
        "answer": "A"
      }
    ],
    "createdAt": "2025-01-15T10:30:00Z"
  }
}
```

### 6.6 Generate Open-ended Questions

**Request**
```http
POST /api/v1/spaces/bd89/openended
Content-Type: application/json

{
  "title": "Photosynthesis Essay Questions",
  "fileIds": ["uuid1", "uuid2"],
  "questionCount": 3,
  "difficulty": "medium",
  "maxWords": 500,
  "topics": ["light reactions", "calvin cycle", "chloroplast structure"]
}
```

**Success 201**
```json
{
  "data": {
    "id": "openended-uuid",
    "spaceId": "bd89",
    "title": "Photosynthesis Essay Questions",
    "questions": [
      {
        "id": "q1",
        "prompt": "Explain the process of photosynthesis in detail, including the light-dependent and light-independent reactions.",
        "maxWords": 500,
        "rubric": {
          "criteria": [
            {
              "name": "Understanding of light reactions",
              "weight": 0.3,
              "description": "Demonstrates clear understanding of photosystem I and II"
            },
            {
              "name": "Calvin cycle explanation", 
              "weight": 0.3,
              "description": "Accurately describes the Calvin cycle steps"
            },
            {
              "name": "Overall coherence",
              "weight": 0.4,
              "description": "Answer is well-structured and coherent"
            }
          ]
        }
      }
    ],
    "createdAt": "2025-01-15T10:30:00Z"
  }
}
```

### 6.7 Submit Open-ended Answer

**Request**
```http
POST /api/v1/openended/openended-uuid/submit
Content-Type: application/json

{
  "answers": [
    {
      "questionId": "q1",
      "answer": "Photosynthesis is a complex biological process that converts light energy into chemical energy..."
    }
  ]
}
```

**Success 201**
```json
{
  "data": {
    "id": "answer-uuid",
    "questionId": "q1",
    "userId": "user-uuid",
    "answer": "Photosynthesis is a complex biological process...",
    "wordCount": 487,
    "grade": {
      "totalScore": 85,
      "maxScore": 100,
      "breakdown": [
        {
          "criterion": "Understanding of light reactions",
          "score": 25,
          "maxScore": 30,
          "feedback": "Good explanation of photosystems but missing detail on electron transport chain"
        },
        {
          "criterion": "Calvin cycle explanation",
          "score": 27,
          "maxScore": 30,
          "feedback": "Excellent description of the Calvin cycle steps"
        },
        {
          "criterion": "Overall coherence",
          "score": 33,
          "maxScore": 40,
          "feedback": "Well-structured answer with logical flow"
        }
      ],
      "overallFeedback": "Strong answer with good understanding of the key concepts. Consider adding more detail about the electron transport chain.",
      "gradedAt": "2025-01-15T10:35:00Z"
    },
    "submittedAt": "2025-01-15T10:30:00Z"
  }
}
```

### 6.8 Generate Flashcards

**Request**
```http
POST /api/v1/spaces/bd89/flashcards
Content-Type: application/json

{
  "title": "Biology Terms - Chapter 3",
  "fileIds": ["uuid1", "uuid2"],
  "cardCount": 20,
  "difficulty": "mixed",
  "topics": ["photosynthesis", "cellular respiration", "chloroplasts"]
}
```

**Success 201**
```json
{
  "data": {
    "id": "flashcard-uuid",
    "spaceId": "bd89",
    "title": "Biology Terms - Chapter 3",
    "cards": [
      {
        "id": "card1",
        "front": "What is chlorophyll?",
        "back": "A green pigment found in plants that captures light energy for photosynthesis",
        "difficulty": "easy",
        "tags": ["photosynthesis", "pigments"]
      },
      {
        "id": "card2",
        "front": "Where does the Calvin cycle occur?",
        "back": "In the stroma of chloroplasts",
        "difficulty": "medium",
        "tags": ["calvin cycle", "chloroplasts"]
      }
    ],
    "createdAt": "2025-01-15T10:30:00Z",
    "updatedAt": "2025-01-15T10:30:00Z"
  }
}
```

### 6.9 Create Study Guide

**Request**
```http
POST /api/v1/spaces/bd89/studyguides
Content-Type: application/json

{
  "title": "Final Exam Study Plan",
  "deadline": "2025-01-30T09:00:00Z",
  "preferences": {
    "dailyStudyHours": 2,
    "preferredTimes": ["morning", "evening"],
    "breakInterval": 25,
    "studyMethods": ["reading", "flashcards", "practice"]
  },
  "fileIds": ["uuid1", "uuid2"],
  "topics": ["photosynthesis", "cellular respiration", "genetics"]
}
```

**Success 201**
```json
{
  "data": {
    "id": "studyguide-uuid",
    "spaceId": "bd89",
    "title": "Final Exam Study Plan",
    "deadline": "2025-01-30T09:00:00Z",
    "totalStudyHours": 40,
    "schedule": [
      {
        "id": "session1",
        "date": "2025-01-16T00:00:00Z",
        "startTime": "09:00",
        "endTime": "11:00",
        "topic": "Photosynthesis",
        "activities": [
          {
            "type": "review",
            "resourceId": "uuid1",
            "resourceType": "file",
            "duration": 60
          },
          {
            "type": "flashcards",
            "resourceId": "flashcard-uuid",
            "resourceType": "flashcard",
            "duration": 60
          }
        ],
        "completed": false
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
      "totalSessions": 20
    },
    "createdAt": "2025-01-15T10:30:00Z",
    "updatedAt": "2025-01-15T10:30:00Z"
  }
}
```

## 7. Error Codes

| Code | HTTP Status | Description |
| :---- | :---- | :---- |
| `UNAUTHORIZED` | 401 | Invalid or missing authentication token |
| `FORBIDDEN` | 403 | User lacks permission for this resource |
| `NOT_FOUND` | 404 | Resource does not exist |
| `VALIDATION_ERROR` | 400 | Request data validation failed |
| `FILE_TOO_LARGE` | 413 | Uploaded file exceeds size limit |
| `UNSUPPORTED_FORMAT` | 415 | File format not supported |
| `QUOTA_EXCEEDED` | 429 | User has exceeded rate/storage limits |
| `ANSWER_TOO_LONG` | 400 | Answer exceeds maximum word count |
| `INVALID_DEADLINE` | 400 | Study guide deadline is in the past |
| `INSUFFICIENT_CONTENT` | 400 | Not enough file content to generate requested items |
| `INTERNAL_ERROR` | 500 | Unexpected server error |

## 8. Implementation Notes

### 8.1 File Processing
- Supported formats: PDF, DOCX, TXT, MD
- Maximum file size: 25MB per file
- Text extraction is performed asynchronously
- OCR support for scanned PDFs

### 8.2 AI Integration
- Chat responses use streaming (Server-Sent Events)
- Quiz generation leverages uploaded file content
- Open-ended questions include AI-generated rubrics for consistent grading
- Flashcard generation extracts key terms and concepts automatically
- Study guides use AI to optimize scheduling based on learning patterns
- Citations include file references and page numbers
- Notes generation supports markdown formatting

### 8.3 Open-ended Question Grading
- AI grading uses rubric-based scoring for consistency
- Scores are provided per criterion with detailed feedback
- Word count validation enforced before submission
- Grade history is maintained for progress tracking

### 8.4 Flashcard Features
- Cards can be filtered by difficulty and tags
- Shuffle endpoint provides randomized study sessions
- Spaced repetition algorithms can be implemented using difficulty ratings
- Support for image-based cards planned for future releases

### 8.5 Study Guide Scheduling
- AI analyzes user preferences and available study time
- Automatic rescheduling when sessions are missed
- Integration with other learning resources (files, flashcards, quizzes)
- Progress tracking with completion percentages
- Deadline-based prioritization of topics

### 8.6 Security
- JWT tokens expire after 24 hours
- File access is restricted to folder owners
- Rate limiting: 100 requests per minute per user
- All file uploads are scanned for malware
- User answers are encrypted at rest

### 8.7 Performance
- Pagination default: 20 items per page
- File text extraction cached for 7 days
- Chat history limited to last 100 messages
- Search results limited to 50 items
- Study guide schedules cached for quick access
- Flashcard shuffling uses server-side randomization 