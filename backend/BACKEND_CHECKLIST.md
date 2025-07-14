# Backend Implementation Checklist

This checklist tracks the required tasks for building the EdutechHackathon backend according to the API specification.

---

## 1. Project Setup & Infrastructure
- [x] Initialize Express + TypeScript project
- [x] Set up folder structure (`routes/`, `controllers/`, `models/`, `middleware/`, `utils/`)
- [x] Add sample health route and test
- [x] Add `.env.example` and config loader
- [x] Add Jest + Supertest for testing
- [x] Add README with setup instructions

---

## 2. Core Features (by API Spec)

### Authentication
- [ ] Implement user registration (`POST /auth/register`)
- [ ] Implement user login (JWT issuance) (`POST /auth/login`)
- [ ] Implement user logout (`POST /auth/logout`)
- [ ] Implement get current user profile (`GET /auth/profile`)
- [ ] Middleware for JWT authentication and user extraction

### User Management
- [ ] User model/schema (with password hashing)
- [ ] User CRUD operations (as needed)

### Folders
- [ ] Folder model/schema
- [ ] List folders (`GET /folders`)
- [ ] Create folder (`POST /folders`)
- [ ] Get folder by ID (`GET /folders/{id}`)
- [ ] Update folder (`PATCH /folders/{id}`)
- [ ] Delete folder (`DELETE /folders/{id}`)

### Spaces (Chat/Quiz/Notes)
- [ ] Space model/schema
- [ ] List spaces in folder (`GET /folders/{folderId}/spaces`)
- [ ] Create space (`POST /folders/{folderId}/spaces`)
- [ ] Get space by ID (`GET /spaces/{id}`)
- [ ] Update space (`PATCH /spaces/{id}`)
- [ ] Delete space (`DELETE /spaces/{id}`)

### Files
- [ ] File model/schema
- [ ] File upload endpoint (`POST /files/upload`)
- [ ] List files in folder (`GET /folders/{folderId}/files`)
- [ ] Get file metadata (`GET /files/{id}`)
- [ ] Get file content (`GET /files/{id}/content`)
- [ ] Delete file (`DELETE /files/{id}`)
- [ ] Integrate file storage (local or cloud)
- [ ] Text extraction/OCR for PDFs

### Chat
- [ ] Chat message model/schema
- [ ] Send message & stream AI reply (`POST /spaces/{spaceId}/messages`)
- [ ] Get chat history (`GET /spaces/{spaceId}/messages`)
- [ ] Delete message (`DELETE /messages/{id}`)
- [ ] Integrate with AI/LLM backend (for assistant replies)
- [ ] SSE (Server-Sent Events) for streaming

### Quiz
- [ ] Quiz model/schema
- [ ] Generate quiz from files (`POST /spaces/{spaceId}/quizzes`)
- [ ] List quizzes (`GET /spaces/{spaceId}/quizzes`)
- [ ] Get quiz detail (`GET /quizzes/{id}`)
- [ ] Submit quiz answers (`POST /quizzes/{id}/submit`)
- [ ] Delete quiz (`DELETE /quizzes/{id}`)

### Notes
- [ ] Notes model/schema
- [ ] Generate notes (`POST /spaces/{spaceId}/notes`)
- [ ] List notes (`GET /spaces/{spaceId}/notes`)
- [ ] Get note (`GET /notes/{id}`)
- [ ] Update note (`PATCH /notes/{id}`)
- [ ] Delete note (`DELETE /notes/{id}`)

---

## 3. Cross-Cutting Concerns
- [ ] Error handling middleware (consistent error responses)
- [ ] Request validation (e.g., using `joi` or `zod`)
- [ ] Logging (requests, errors)
- [ ] Rate limiting middleware
- [ ] Security headers (Helmet, CORS)
- [ ] Pagination, filtering, and search utilities
- [ ] Role-based access control (if needed)

---

## 4. Testing
- [ ] Unit tests for all controllers/services
- [ ] Integration tests for all endpoints
- [ ] Authentication/authorization tests
- [ ] File upload and processing tests
- [ ] SSE/streaming tests

---

## 5. DevOps/Deployment
- [ ] Dockerfile for backend
- [ ] Production environment config
- [ ] Database setup/migrations (MongoDB or other)
- [ ] CI/CD pipeline (optional, but recommended)

---

**Tip:**
- Track progress by checking off items as you complete them.
- Use this checklist to create GitHub issues or project board cards for team collaboration. 