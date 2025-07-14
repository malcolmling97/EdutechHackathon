# Documentation Index

This directory contains comprehensive documentation for the EdutechHackathon API and development guidelines.

## 📋 Documentation Overview

### Core API Documentation
- **[API Specification](./API_SPECIFICATION.md)** - Complete REST API reference
  - URI conventions and versioning
  - Authentication requirements
  - Resource schemas and relationships
  - Complete endpoint catalogue
  - Request/response examples
  - Error codes and handling
  - Implementation notes

### Migration and Development
- **[Migration Guide](./MIGRATION_GUIDE.md)** - Transition from old API to new structure
  - Endpoint mappings
  - Code migration examples
  - Breaking changes summary
  - Frontend/backend migration checklists

## 🏗️ API Architecture

### Resource Hierarchy
```
User
├── Folders (Learning Units)
│   ├── Spaces (Chat/Quiz/Notes Sessions)
│   │   ├── Messages (Chat history)
│   │   ├── Quizzes (Generated from files)
│   │   └── Notes (Generated summaries)
│   └── Files (Uploaded documents)
└── Authentication (JWT tokens)
```

### Key Design Principles
1. **RESTful Design** - Standard HTTP methods and status codes
2. **Resource-Oriented** - Clear resource hierarchy and relationships
3. **Versioned** - `/api/v1/` for future compatibility
4. **Consistent** - Uniform response format and error handling
5. **Secure** - JWT authentication with proper authorization
6. **Scalable** - Pagination, filtering, and search capabilities

## 🚀 Quick Start

### 1. Authentication
```javascript
// Login to get JWT token
const response = await fetch('/api/v1/auth/login', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ 
    email: 'user@example.com',
    password: 'password' 
  })
});

const { token } = await response.json();
```

### 2. Create Learning Folder
```javascript
const folder = await fetch('/api/v1/folders', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    title: 'Biology 101',
    description: 'Semester 1 materials'
  })
});
```

### 3. Upload Files
```javascript
const formData = new FormData();
formData.append('folderId', folderId);
formData.append('files', pdfFile);

const upload = await fetch('/api/v1/files/upload', {
  method: 'POST',
  headers: { 'Authorization': `Bearer ${token}` },
  body: formData
});
```

### 4. Create Chat Space
```javascript
const chatSpace = await fetch(`/api/v1/folders/${folderId}/spaces`, {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    type: 'chat',
    title: 'Study Discussion'
  })
});
```

## 📊 Response Format

All API responses follow a consistent envelope pattern:

### Success Response
```json
{
  "data": { /* resource data */ },
  "meta": { 
    "page": 1, 
    "limit": 20, 
    "total": 100 
  }
}
```

### Error Response
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Title is required",
    "details": { "field": "title" }
  }
}
```

## 🔧 Development Tools

### Testing Endpoints
Use tools like:
- **Postman** - For interactive API testing
- **curl** - For command-line testing
- **Insomnia** - For API development

### Example curl Request
```bash
curl -X POST '/api/v1/folders' \
  -H 'Authorization: Bearer <token>' \
  -H 'Content-Type: application/json' \
  -d '{"title": "Test Folder"}'
```

## 📈 Performance Considerations

### Pagination
- Default page size: 20 items
- Maximum page size: 100 items
- Use `?page=1&limit=20` parameters

### File Uploads
- Maximum file size: 25MB
- Supported formats: PDF, DOCX, TXT, MD
- Asynchronous text extraction

### Streaming
- Chat responses support Server-Sent Events
- Real-time message delivery
- Automatic reconnection handling

## 🛡️ Security

### Authentication
- JWT tokens with 24-hour expiration
- Include `X-User-Id` header for user identification
- Refresh tokens for session management

### Authorization
- Resource-based permissions
- Users can only access their own folders
- Admin endpoints require elevated permissions

### Rate Limiting
- 100 requests per minute per user
- File upload limits apply separately
- Burst capacity for normal usage

## 🐛 Error Handling

### Common Error Codes
- `401 UNAUTHORIZED` - Invalid/missing token
- `403 FORBIDDEN` - Insufficient permissions
- `404 NOT_FOUND` - Resource doesn't exist
- `413 FILE_TOO_LARGE` - Upload size exceeded
- `429 QUOTA_EXCEEDED` - Rate limit reached

### Error Response Pattern
All errors include:
- **code** - Machine-readable error identifier
- **message** - Human-readable description
- **details** - Additional context (optional)

## 🔄 Integration Examples

### React Frontend
```javascript
// API client setup
const apiClient = {
  baseURL: '/api/v1',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  }
};

// React hook for API calls
const useApi = () => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const request = async (endpoint, options = {}) => {
    setLoading(true);
    try {
      const response = await fetch(`${apiClient.baseURL}${endpoint}`, {
        ...options,
        headers: { ...apiClient.headers, ...options.headers }
      });
      const result = await response.json();
      if (!response.ok) throw new Error(result.error.message);
      setData(result.data);
      return result.data;
    } catch (err) {
      setError(err.message);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  return { data, loading, error, request };
};
```

### Node.js Backend
```javascript
// Express.js route handler
app.post('/api/v1/folders', authenticateToken, async (req, res) => {
  try {
    const { title, description } = req.body;
    const folder = await folderService.create({
      title,
      description,
      ownerId: req.user.id
    });
    
    res.status(201).json({
      data: folder,
      meta: {}
    });
  } catch (error) {
    res.status(400).json({
      error: {
        code: 'VALIDATION_ERROR',
        message: error.message,
        details: error.details
      }
    });
  }
});
```

## 📚 Additional Resources

- [Frontend Implementation Guide](../README.md#frontend-integration-status)
- [Backend Development Setup](../README.md#getting-started)
- [File Structure Overview](../README.md#file-structure)
- [Contributing Guidelines](../README.md#getting-started)

## 🔄 Version History

| Version | Date | Changes |
|---------|------|---------|
| v1.0 | 2025-01-15 | Initial comprehensive API specification |
| v1.0 | 2025-01-15 | Migration guide from legacy API |
| v1.0 | 2025-01-15 | Complete documentation structure |

---

**Need Help?** 
- Check the [API Specification](./API_SPECIFICATION.md) for detailed endpoint information
- Review the [Migration Guide](./MIGRATION_GUIDE.md) for transition assistance
- Refer to the main [README](../README.md) for project setup and overview 