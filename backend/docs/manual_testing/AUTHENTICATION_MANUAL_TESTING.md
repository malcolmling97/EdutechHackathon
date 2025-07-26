# Authentication API Manual Testing Guide

This guide provides step-by-step instructions for manually testing all authentication endpoints in the EdutechHackathon backend API.

## Prerequisites

1. **Start the Backend Server:**
   ```bash
   cd EdutechHackathon/backend
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

2. **Access API Documentation:**
   - Swagger UI: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc

## Authentication Endpoints

### 1. User Registration

**Endpoint:** `POST /api/v1/auth/register`

**Test Case: Successful Registration**
```bash
curl -X POST "http://localhost:8000/api/v1/auth/register" \
-H "Content-Type: application/json" \
-d '{
  "email": "testuser@example.com",
  "password": "securepassword123",
  "name": "Test User"
}'
```

**Expected Response (201 Created):**
```json
{
  "data": {
    "user": {
      "id": "a1b2c3d4-e5f6-7890-1234-567890abcdef",
      "email": "testuser@example.com",
      "name": "Test User",
      "created_at": "2025-01-25T10:30:00Z",
      "updated_at": "2025-01-25T10:30:00Z"
    },
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
  }
}
```

**Test Case: Duplicate Email (Should Fail)**
```bash
# Run the same registration again
curl -X POST "http://localhost:8000/api/v1/auth/register" \
-H "Content-Type: application/json" \
-d '{
  "email": "testuser@example.com",
  "password": "differentpassword",
  "name": "Another User"
}'
```

**Expected Response (400 Bad Request):**
```json
{
  "error": {
    "code": "EMAIL_ALREADY_EXISTS",
    "message": "A user with this email already exists",
    "details": {"email": "testuser@example.com"}
  }
}
```

**Test Case: Invalid Email Format**
```bash
curl -X POST "http://localhost:8000/api/v1/auth/register" \
-H "Content-Type: application/json" \
-d '{
  "email": "invalid-email",
  "password": "securepassword123",
  "name": "Test User"
}'
```

**Expected Response (422 Unprocessable Entity):**
```json
{
  "detail": [
    {
      "loc": ["body", "email"],
      "msg": "value is not a valid email address",
      "type": "value_error.email"
    }
  ]
}
```

**Test Case: Password Too Short**
```bash
curl -X POST "http://localhost:8000/api/v1/auth/register" \
-H "Content-Type: application/json" \
-d '{
  "email": "shortpass@example.com",
  "password": "123",
  "name": "Test User"
}'
```

### 2. User Login

**Endpoint:** `POST /api/v1/auth/login`

**Test Case: Successful Login**
```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
-H "Content-Type: application/json" \
-d '{
  "email": "testuser@example.com",
  "password": "securepassword123"
}'
```

**Expected Response (200 OK):**
```json
{
  "data": {
    "user": {
      "id": "a1b2c3d4-e5f6-7890-1234-567890abcdef",
      "email": "testuser@example.com",
      "name": "Test User",
      "created_at": "2025-01-25T10:30:00Z",
      "updated_at": "2025-01-25T10:30:00Z"
    },
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
  }
}
```

**Test Case: Invalid Credentials**
```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
-H "Content-Type: application/json" \
-d '{
  "email": "testuser@example.com",
  "password": "wrongpassword"
}'
```

**Expected Response (401 Unauthorized):**
```json
{
  "error": {
    "code": "INVALID_CREDENTIALS",
    "message": "Invalid email or password",
    "details": null
  }
}
```

**Test Case: Non-existent User**
```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
-H "Content-Type: application/json" \
-d '{
  "email": "nonexistent@example.com",
  "password": "anypassword"
}'
```

### 3. Get User Profile

**Endpoint:** `GET /api/v1/auth/profile`

**Test Case: Valid Token**
```bash
# Replace YOUR_JWT_TOKEN with token from registration or login
curl -X GET "http://localhost:8000/api/v1/auth/profile" \
-H "Authorization: Bearer YOUR_JWT_TOKEN"
```

**Expected Response (200 OK):**
```json
{
  "data": {
    "user": {
      "id": "a1b2c3d4-e5f6-7890-1234-567890abcdef",
      "email": "testuser@example.com",
      "name": "Test User",
      "created_at": "2025-01-25T10:30:00Z",
      "updated_at": "2025-01-25T10:30:00Z"
    }
  }
}
```

**Test Case: No Token**
```bash
curl -X GET "http://localhost:8000/api/v1/auth/profile"
```

**Expected Response (401 Unauthorized):**
```json
{
  "detail": "Not authenticated"
}
```

**Test Case: Invalid Token**
```bash
curl -X GET "http://localhost:8000/api/v1/auth/profile" \
-H "Authorization: Bearer invalid-token-12345"
```

**Test Case: Malformed Authorization Header**
```bash
curl -X GET "http://localhost:8000/api/v1/auth/profile" \
-H "Authorization: InvalidFormat"
```

### 4. User Logout

**Endpoint:** `POST /api/v1/auth/logout`

**Test Case: Valid Token**
```bash
curl -X POST "http://localhost:8000/api/v1/auth/logout" \
-H "Authorization: Bearer YOUR_JWT_TOKEN"
```

**Expected Response (204 No Content):**
No body content, just status code 204.

**Test Case: Using Token After Logout (Should Fail)**
```bash
# Try to access profile with the same token after logout
curl -X GET "http://localhost:8000/api/v1/auth/profile" \
-H "Authorization: Bearer YOUR_LOGGED_OUT_TOKEN"
```

**Expected Response (401 Unauthorized):**
```json
{
  "detail": "Could not validate credentials"
}
```

## Complete Workflow Testing

**Test the complete authentication flow:**

1. **Register a new user and save the token:**
   ```bash
   curl -X POST "http://localhost:8000/api/v1/auth/register" \
   -H "Content-Type: application/json" \
   -d '{
     "email": "workflow@example.com",
     "password": "workflowtest123",
     "name": "Workflow User"
   }'
   ```

2. **Login with the same user and get a new token:**
   ```bash
   curl -X POST "http://localhost:8000/api/v1/auth/login" \
   -H "Content-Type: application/json" \
   -d '{
     "email": "workflow@example.com",
     "password": "workflowtest123"
   }'
   ```

3. **Access profile with login token:**
   ```bash
   curl -X GET "http://localhost:8000/api/v1/auth/profile" \
   -H "Authorization: Bearer LOGIN_TOKEN_HERE"
   ```

4. **Logout:**
   ```bash
   curl -X POST "http://localhost:8000/api/v1/auth/logout" \
   -H "Authorization: Bearer LOGIN_TOKEN_HERE"
   ```

5. **Verify token is blacklisted:**
   ```bash
   curl -X GET "http://localhost:8000/api/v1/auth/profile" \
   -H "Authorization: Bearer LOGIN_TOKEN_HERE"
   ```

## Testing with Postman/Insomnia

1. **Import the API collection:**
   - Use the OpenAPI spec at: http://localhost:8000/openapi.json

2. **Set up environment variables:**
   - `base_url`: http://localhost:8000
   - `token`: (copy from login/register response)

3. **Test sequence:**
   - Register → Login → Profile → Logout → Profile (should fail)

## Validation Testing

**Test all validation scenarios:**

1. **Email validation:**
   - Invalid format: "not-an-email"
   - Missing @ symbol: "usergmail.com"
   - Missing domain: "user@"

2. **Password validation:**
   - Too short: "123"
   - Empty: ""
   - Only spaces: "   "

3. **Name validation:**
   - Empty string: ""
   - Only spaces: "   "
   - Missing field

## Security Testing

1. **JWT Token Security:**
   - Tampered tokens
   - Expired tokens (wait 24 hours or modify JWT_EXPIRATION_HOURS)
   - Malformed tokens

2. **Rate Limiting:** (if implemented)
   - Send many requests quickly
   - Verify rate limit responses

3. **CORS Testing:**
   - Cross-origin requests from different domains

## Troubleshooting

**Common Issues:**

1. **Connection Refused:**
   - Ensure server is running on port 8000
   - Check if port is already in use

2. **Database Errors:**
   - Check if `data/` directory exists
   - Verify SQLite permissions

3. **Import Errors:**
   - Ensure all dependencies are installed: `pip3 install -r requirements.txt`
   - Check Python version (3.9+ required)

4. **Token Issues:**
   - Verify JWT_SECRET_KEY is set correctly
   - Check token expiration time

**Server Logs:**
Monitor the uvicorn console output for detailed error information during testing. 