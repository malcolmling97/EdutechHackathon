## Features
- Sidebar with navigation, chat history and search
- Light/Dark mode toggle
- PDF upload button

## Prerequisites
- [Node.js](https://nodejs.org/) (v18 or newer recommended)
- [npm](https://www.npmjs.com/) (comes with Node.js)

## Getting Started

### 1. Clone or Download the Repository
If you haven't already, clone this repo or download the source code to your machine.

```
# Example:
git clone <your-repo-url>
cd edutech
```

### 2. Install Dependencies
Install all required npm packages:

```
npm install
```

### 3. Run the Development Server
Start the Vite development server:

```
npm run dev
```

## API Documentation

This project uses a comprehensive REST API design with proper versioning, authentication, and resource organization. The API is organized around the concept of **Folders** (learning units) containing **Spaces** (chat, quiz, or notes sessions) and **Files** (uploaded documents).

### API Specification

For complete API documentation, including:
- URI conventions and versioning
- Authentication requirements
- Resource schemas
- Endpoint catalogue
- Request/response examples
- Error codes and handling

See: **[API Specification](./docs/API_SPECIFICATION.md)**

### Key API Concepts

**Resource Hierarchy:**
```
User → Folders → Spaces (chat/quiz/notes) → Messages/Quizzes/Notes
           ↓
         Files (PDFs, documents)
```

**Base URL:** `/api/v1`

**Authentication:** JWT Bearer tokens with `X-User-Id` header

**Response Format:** All responses use a consistent JSON envelope pattern

### Core Endpoints Summary

| Resource | Method | Endpoint | Purpose |
|----------|---------|-----------|---------|
| **Auth** | POST | `/auth/login` | User authentication |
| **Folders** | GET | `/folders` | List user folders |
| **Folders** | POST | `/folders` | Create new folder |
| **Spaces** | GET | `/folders/{id}/spaces` | List spaces in folder |
| **Spaces** | POST | `/folders/{id}/spaces` | Create chat/quiz/notes space |
| **Files** | POST | `/files/upload` | Upload documents |
| **Chat** | POST | `/spaces/{id}/messages` | Send message & get AI response |
| **Quiz** | POST | `/spaces/{id}/quizzes` | Generate quiz from files |
| **Notes** | POST | `/spaces/{id}/notes` | Generate notes from files |

### Frontend Integration Status

**Current Implementation:**
- Frontend uses local state management
- Static mock data for AI responses
- No backend connectivity

**Migration Plan:**
- Replace local state with API calls
- Implement JWT authentication
- Add file upload functionality
- Enable real-time chat streaming
- Connect quiz and notes generation

### Development Notes

- The API supports both REST and streaming endpoints
- File processing includes text extraction and OCR
- AI features include citation tracking and source references
- All endpoints include proper error handling and validation

## File Structure

```
<project-root>/
├── docs/                 # API and development documentation
│   ├── README.md         # Documentation index and overview
│   ├── API_SPECIFICATION.md  # Complete REST API reference
│   └── MIGRATION_GUIDE.md    # Transition guide from legacy API
├── frontend/             # React frontend application
│   ├── public/           # Static assets (icons, images)
│   ├── src/              # Main source code
│   │   ├── components/   # Reusable React components
│   │   ├── App.tsx       # Main application component
│   │   ├── utils.tsx     # Utility functions
│   │   ├── types.ts      # TypeScript type definitions
│   │   └── ...           # Other app files
│   ├── package.json      # Frontend dependencies
│   ├── tailwind.config.js # Tailwind CSS configuration
│   ├── tsconfig.json     # TypeScript configuration
│   └── vite.config.ts    # Vite build tool configuration
├── backend/              # Node.js/Express backend API
│   └── ...               # Backend implementation (to be developed)
├── shared/               # Shared types and utilities
│   └── ...               # Common code between frontend/backend
├── .gitignore            # Git ignore rules
└── README.md             # Project overview and setup
