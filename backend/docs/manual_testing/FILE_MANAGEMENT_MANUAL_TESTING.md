# File Management Manual Testing Guide

This document provides comprehensive manual testing instructions for the File Management functionality implemented for the EdutechHackathon backend API.

## Overview

The File Management system provides complete CRUD operations for file upload, storage, text extraction, and management. It supports PDF, DOCX, TXT, and MD files up to 25MB each with automatic text extraction for AI processing.

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

### 2. Create Test Folder

Create a folder to upload files to:

```bash
curl -X POST "http://localhost:8000/api/v1/folders" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "title": "Test Files Folder",
    "description": "Folder for testing file operations"
  }'
```

**Expected Response**: 
- Status: `201 Created`
- Response body contains folder data with `id` field
- Save the folder ID for file upload tests

### 3. File Upload Tests

#### 3.1 Upload Single Text File

```bash
curl -X POST "http://localhost:8000/api/v1/files/upload" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -F "folder_id=YOUR_FOLDER_ID" \
  -F "files=@test.txt"
```

**Expected Response**:
- Status: `201 Created`
- Response body: Array with uploaded file metadata
- Includes: `id`, `folder_id`, `name`, `mime_type`, `size`, `created_at`

#### 3.2 Upload Multiple Files

```bash
curl -X POST "http://localhost:8000/api/v1/files/upload" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -F "folder_id=YOUR_FOLDER_ID" \
  -F "files=@document.pdf" \
  -F "files=@notes.docx" \
  -F "files=@readme.md"
```

**Expected Response**:
- Status: `201 Created`
- Response body: Array with all uploaded files
- Each file should have proper MIME type detection

#### 3.3 Upload Large File (Should Fail)

Create a file larger than 25MB and attempt upload:

```bash
# Create large test file
dd if=/dev/zero of=large_file.txt bs=1M count=26

# Attempt upload
curl -X POST "http://localhost:8000/api/v1/files/upload" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -F "folder_id=YOUR_FOLDER_ID" \
  -F "files=@large_file.txt"
```

**Expected Response**:
- Status: `413 Request Entity Too Large`
- Error message about file size limit

#### 3.4 Upload Unsupported File Type

```bash
curl -X POST "http://localhost:8000/api/v1/files/upload" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -F "folder_id=YOUR_FOLDER_ID" \
  -F "files=@test.exe"
```

**Expected Response**:
- Status: `415 Unsupported Media Type`
- Error message about unsupported file type

### 4. File Listing Tests

#### 4.1 List Files in Folder

```bash
curl -X GET "http://localhost:8000/api/v1/folders/YOUR_FOLDER_ID/files" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

**Expected Response**:
- Status: `200 OK`
- Response body contains `data` array with files and `meta` with pagination info

#### 4.2 List Files with Pagination

```bash
curl -X GET "http://localhost:8000/api/v1/folders/YOUR_FOLDER_ID/files?page=1&limit=2" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

**Expected Response**:
- Status: `200 OK`
- Maximum 2 files in response
- Pagination metadata: `page=1`, `limit=2`, `total` count

### 5. File Metadata Tests

#### 5.1 Get File Metadata

```bash
curl -X GET "http://localhost:8000/api/v1/files/YOUR_FILE_ID" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

**Expected Response**:
- Status: `200 OK`
- Complete file metadata including name, size, MIME type, timestamps

#### 5.2 Get Non-existent File

```bash
curl -X GET "http://localhost:8000/api/v1/files/non-existent-file-id" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

**Expected Response**:
- Status: `404 Not Found`
- Error message about file not found

### 6. File Content Tests

#### 6.1 Get File Content

```bash
curl -X GET "http://localhost:8000/api/v1/files/YOUR_FILE_ID/content" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

**Expected Response**:
- Status: `200 OK`
- Response body contains extracted text content and MIME type
- For text files: original content
- For PDF/DOCX: extracted text

#### 6.2 Get Content of Large PDF

Upload a PDF with text and retrieve its content:

**Expected Response**:
- Status: `200 OK`
- Extracted text content from all pages
- Proper text formatting preservation

### 7. File Deletion Tests

#### 7.1 Soft Delete File

```bash
curl -X DELETE "http://localhost:8000/api/v1/files/YOUR_FILE_ID" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

**Expected Response**:
- Status: `204 No Content`
- File should be marked as deleted but remain in database
- File should not appear in folder listings

#### 7.2 Hard Delete File

```bash
curl -X DELETE "http://localhost:8000/api/v1/files/YOUR_FILE_ID?force=true" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

**Expected Response**:
- Status: `204 No Content`
- File completely removed from database and storage

### 8. Authorization Tests

#### 8.1 Access File from Different User

1. Create second user account
2. Attempt to access files from first user

```bash
curl -X GET "http://localhost:8000/api/v1/files/FIRST_USER_FILE_ID" \
  -H "Authorization: Bearer SECOND_USER_JWT_TOKEN"
```

**Expected Response**:
- Status: `403 Forbidden`
- Error message about access denied

#### 8.2 Upload to Other User's Folder

```bash
curl -X POST "http://localhost:8000/api/v1/files/upload" \
  -H "Authorization: Bearer SECOND_USER_JWT_TOKEN" \
  -F "folder_id=FIRST_USER_FOLDER_ID" \
  -F "files=@test.txt"
```

**Expected Response**:
- Status: `403 Forbidden`
- Error message about folder access

### 9. Error Handling Tests

#### 9.1 Missing Authentication

```bash
curl -X GET "http://localhost:8000/api/v1/files/YOUR_FILE_ID"
```

**Expected Response**:
- Status: `401 Unauthorized`
- Error about missing credentials

#### 9.2 Invalid Folder ID Format

```bash
curl -X POST "http://localhost:8000/api/v1/files/upload" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -F "folder_id=invalid-uuid-format" \
  -F "files=@test.txt"
```

**Expected Response**:
- Status: `400 Bad Request` or `404 Not Found`
- Error about invalid folder ID

## File Processing Verification

### Text Extraction Testing

1. **PDF Files**: Upload PDF with text content
   - Verify extracted text appears in content endpoint
   - Check text quality and formatting

2. **DOCX Files**: Upload Word document
   - Verify text from paragraphs is extracted
   - Check table content extraction

3. **Text Files**: Upload plain text and markdown
   - Verify content is preserved exactly
   - Check encoding handling (UTF-8, etc.)

## Performance Testing

### Large File Handling

1. Upload files near the 25MB limit
2. Monitor processing time for text extraction
3. Verify system remains responsive

### Multiple File Upload

1. Upload 5-10 files simultaneously
2. Verify all files process correctly
3. Check for any race conditions

## Security Testing

### File Safety

1. Upload files with unusual names (special characters)
2. Verify path traversal protection
3. Test filename sanitization

### Access Control

1. Verify users can only access their own files
2. Test folder ownership enforcement
3. Confirm JWT token validation

## Database Verification

After running tests, verify database state:

```sql
-- Check file records
SELECT id, name, mime_type, size, deleted_at FROM files;

-- Check text extraction
SELECT id, name, LENGTH(text_content) as text_length FROM files;

-- Check soft deletion
SELECT COUNT(*) FROM files WHERE deleted_at IS NULL;
```

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure all dependencies installed
   ```bash
   pip install -r requirements.txt
   ```

2. **File Processing Errors**: Check if system dependencies are installed
   ```bash
   sudo apt-get install libmagic1
   ```

3. **Permission Errors**: Verify upload/temp directories are writable
   ```bash
   chmod 755 uploads/ temp/
   ```

4. **Database Errors**: Ensure file model is imported
   ```python
   from app.models import file  # In database.py create_tables()
   ```

## Success Criteria

All tests should pass with:
- ✅ Correct HTTP status codes
- ✅ Proper error messages for failures
- ✅ Complete file metadata in responses
- ✅ Successful text extraction for supported formats
- ✅ Proper access control enforcement
- ✅ File storage in correct locations
- ✅ Database records created correctly

## Implementation Status

**✅ Completed Features:**
- File upload (single and multiple)
- File listing with pagination
- File metadata retrieval
- File content extraction
- File deletion (soft and hard)
- Text extraction (PDF, DOCX, TXT, MD)
- Access control and authorization
- File validation and security
- Error handling and responses

**📝 Notes:**
- All endpoints follow the API specification
- Implementation is backend developer focused (no AI/ML features)
- Text extraction is ready for future AI/ML integration
- Comprehensive error handling for edge cases 