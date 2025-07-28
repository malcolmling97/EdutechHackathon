# Edutech AI Platform: Technical Documentation


# TO ALL PPL, THIS WORKS: http://localhost:5173/chat/space-00000000-0000-0000-0000-000000000003

The chat space creation does not work yet. Need to fix.


## 1. Project Overview

### High-Level Description
The Edutech AI Platform is a comprehensive educational technology solution that leverages artificial intelligence to enhance learning experiences. At its core, the platform integrates a context-aware AI chatbot powered by OpenAI's GPT-4o model, designed to provide personalized learning assistance, answer questions, and facilitate various study activities through different interactive spaces.

### Target Users and Use Cases
- **Students**: For personalized learning assistance, question answering, and study aid
- **Educators**: For creating customized learning spaces and materials for students
- **Educational Institutions**: For deploying AI-enhanced learning tools across their curriculum

### Core Capabilities
- **AI-Powered Chatbot**: Contextual question answering using OpenAI GPT-4o
- **Organized Learning Spaces**: Folders and spaces structure for organizing different learning contexts
- **Multiple Study Formats**: Chat, quiz, notes, flashcards, and study guide spaces
- **Persistent Conversations**: Chat history maintained per user and space
- **Extensible Architecture**: Designed for future integration of document ingestion and RAG capabilities

## 2. System Architecture

### Components
1. **Frontend**: React-based single-page application with component-based UI
2. **Backend**: Node.js/Express REST API server
3. **Database**: PostgreSQL for structured data storage
4. **External AI**: OpenAI GPT-4o API for natural language processing
5. **Future Components**: 
   - Vector database (pgvector) for semantic search
   - Document processing pipeline for PDF and text ingestion
   - Embedding model for text vectorization

### Data Flow
1. **User Interaction**: User interacts with the frontend UI
2. **API Communication**: Frontend sends requests to backend API
3. **Database Operations**: Backend performs CRUD operations on PostgreSQL
4. **AI Processing**: For chat messages, backend forwards to OpenAI API
5. **Response Handling**: AI responses are stored in database and returned to frontend
6. **Future RAG Flow**: Document → Chunk → Embed → Store → Retrieve → Rerank → Respond

## 3. Feature Summary

### Current Features
- **User Management**: Basic user identification via headers
- **Folder Organization**: Create and manage folders for organizing spaces
- **Multiple Space Types**: Support for chat, quiz, notes, flashcards, and study guide spaces
- **Chat Functionality**: Send messages to AI and receive contextual responses
- **Chat History**: Persistent chat history per space with both local and server storage
- **Error Handling**: Comprehensive error handling and logging on both frontend and backend
- **Space Creation**: API endpoints for creating new spaces within folders

### Planned Features
- **Document Ingestion**: Upload and process educational materials
- **Vector Search**: Semantic search over educational content
- **Enhanced Study Tools**: Advanced quiz generation, flashcard creation, and study guides
- **User Authentication**: Proper authentication and authorization system

## 4. Frontend

### Pages/Components Structure
- **Layout**: Main application layout with navigation
- **DashboardView**: Overview of folders and spaces
- **ChatView**: Interactive chat interface with AI
- **StudyOptionsView**: Selection of study methods
- **QuizView**, **NotesView**, **FlashcardsView**, **OpenEndedView**, **StudyGuideView**: Specialized study interfaces

### State Management
- **React Hooks**: useState and useEffect for component state
- **Local Storage**: Caching chat messages for offline access and performance
- **API Integration**: Fetching and updating data via API utility functions

### Data Flow
- **API Utilities**: Centralized API functions in api.ts
- **Component State**: Local state for UI components
- **Optimistic Updates**: UI updates before API confirmation for better UX
- **Error Handling**: Comprehensive error handling with user feedback

### Routing
- **React Router**: Dynamic routing based on space types and IDs
- **URL Parameters**: Space and folder IDs encoded in URLs

## 5. Backend

### API Routes
- **/api/v1/health**: System health check
- **/api/v1/folders**: Folder management
- **/api/v1/folders/:folderId/spaces**: Space management within folders
- **/api/v1/spaces/:spaceId/messages**: Message handling for spaces

### Controllers
- **folderController**: Manage educational content folders
- **spaceController**: Handle different types of learning spaces
- **messageController**: Process chat messages and AI interactions

### Database Integration
- **PostgreSQL Pool**: Connection pooling for database operations
- **SQL Queries**: Direct SQL queries for data operations
- **Transaction Support**: For operations requiring atomicity

### OpenAI Integration
- **API Forwarding**: Forwarding processed messages to OpenAI
- **Context Management**: Maintaining conversation context
- **Response Processing**: Handling and storing AI responses

## 6. Vector Store + Embedding Pipeline (Planned)

### Embedding Model
- **Planned Integration**: Future integration with embedding models
- **Vector Storage**: Planned use of pgvector for PostgreSQL

### Chunking and Storage Strategy
- **Document Processing**: Future implementation of document chunking
- **Metadata Linking**: Design for linking chunks to original documents and spaces

## 7. Session & Chat History Management

### Chat Session Handling
- **Space-Based Sessions**: Chat sessions organized by space IDs
- **User Association**: Sessions linked to user IDs
- **Persistence**: Messages stored in PostgreSQL database

### Frontend Caching
- **localStorage**: Client-side caching of chat messages
- **Cache Invalidation**: Refreshing cache on new messages

### Message Flow
1. User sends message via frontend
2. Message stored optimistically in UI
3. Message sent to backend API
4. Backend validates and stores user message
5. Message forwarded to OpenAI API
6. AI response received and stored
7. Response returned to frontend
8. Frontend updates UI and local cache

## 8. File Ingestion & Chunking Strategy (Planned)

### Document Processing
- **Future Implementation**: Document upload and processing pipeline
- **Supported Formats**: Plans for PDF and text document support

### Chunking Methods
- **Planned Approach**: Implementation of appropriate chunking strategies
- **Metadata Preservation**: Design for maintaining document structure information

## 9. Deployment & Runtime Setup

### Fresh Git Clone Setup

#### Prerequisites
1. **Node.js and npm**:
   - Download and install Node.js (v16+ recommended) from [nodejs.org](https://nodejs.org/)
   - Verify installation with `node -v` and `npm -v`

2. **PostgreSQL Setup**:
   - Download PostgreSQL 17+ from [postgresql.org](https://www.postgresql.org/download/)
   - During installation, note down your password and port (default: 5432)
   - For Windows users, add PostgreSQL bin directory to PATH (e.g., `C:\Program Files\PostgreSQL\17\bin`)

3. **pgAdmin Setup** (optional but recommended):
   - Download pgAdmin 4 from [pgadmin.org](https://www.pgadmin.org/download/)
   - Connect to your PostgreSQL server using the credentials from installation

4. **Visual Studio Build Tools** (required for pgvector on Windows):
   - Download Visual Studio Build Tools from [visualstudio.microsoft.com](https://visualstudio.microsoft.com/visual-cpp-build-tools/)
   - During installation, select "Desktop development with C++" workload
   - Ensure you install the Windows 10/11 SDK and the MSVC v143 build tools

#### Database Setup
1. **Create Database**:
   ```sql
   CREATE DATABASE edutech;
   ```

2. **pgvector Installation** (for future vector search capabilities):
   - **Windows**:
     - Clone pgvector: `git clone https://github.com/pgvector/pgvector.git`
     - Navigate to directory: `cd pgvector`
     - Open x64 Native Tools Command Prompt for VS (as Administrator)
     - Run: `set PG_CONFIG="C:\Program Files\PostgreSQL\15\bin\pg_config.exe"` (adjust path as needed)
     - Run: `nmake /f Makefile.win`
     - Run: `nmake /f Makefile.win install`
   
   - **macOS/Linux**:
     - Clone pgvector: `git clone https://github.com/pgvector/pgvector.git`
     - Navigate to directory: `cd pgvector`
     - Run: `make`
     - Run: `make install`

   - **Enable in Database**:
     ```sql
     CREATE EXTENSION vector;
     ```

3. **Run Migrations**:
   - Navigate to the backend directory
   - Run the migration script: `psql -U postgres -d edutech -f src/db/migrations/init.sql`

#### Project Setup
1. **Clone Repository**:
   ```bash
   git clone https://github.com/your-username/EdutechHackathon.git
   cd EdutechHackathon
   ```

2. **Backend Setup**:
   ```bash
   cd backend
   npm install
   cp .env.example .env  # Create .env file from template
   ```
   
   Edit `.env` file with your configuration:
   ```
   PORT=4000
   DATABASE_URL=postgresql://postgres:yourpassword@localhost:5432/edutech
   JWT_SECRET=your_jwt_secret_key
   OPENAI_API_KEY=your_openai_api_key
   ```

3. **Frontend Setup**:
   ```bash
   cd ../frontend
   npm install
   ```

4. **Start the Application**:
   - Backend: `cd backend && npm start` or `ts-node src/index.ts`
   - Frontend: `cd frontend && npm run dev`

### Troubleshooting Common Issues

1. **PostgreSQL Connection Issues**:
   - Verify PostgreSQL service is running
   - Check DATABASE_URL format and credentials
   - Ensure firewall allows connections to PostgreSQL port

2. **pgvector Installation Errors**:
   - For Windows: Ensure you're using the x64 Native Tools Command Prompt for VS
   - Verify PG_CONFIG path points to your pg_config.exe
   - Check if you have proper permissions (run as Administrator)

3. **Node.js Dependency Issues**:
   - Clear npm cache: `npm cache clean --force`
   - Delete node_modules and reinstall: `rm -rf node_modules && npm install`

4. **CORS Errors**:
   - Verify backend CORS configuration allows requests from frontend origin
   - Check network requests in browser developer tools

### Environment Variables
- **PORT**: Backend server port (default: 4000)
- **DATABASE_URL**: PostgreSQL connection string
- **JWT_SECRET**: Secret for JWT token generation
- **OPENAI_API_KEY**: API key for OpenAI services

### Dependencies
- **Backend**: Express, PostgreSQL, CORS, dotenv, pg, OpenAI
- **Frontend**: React, React Router, Vite, TypeScript

## 10. Known Limitations

### Current Limitations
- **Limited Space Creation UI**: No frontend interface for creating spaces yet
- **Fixed User ID**: Currently using hardcoded user ID for testing
- **No Document Context**: Chat relies solely on OpenAI's knowledge, no document context
- **Limited Error Recovery**: Basic error handling without sophisticated retry logic
- **UUID Format Issues**: Potential issues with UUID format between frontend and backend

### Performance Considerations
- **API Key Management**: Need for secure API key handling
- **Database Scaling**: Potential performance issues with large message histories

## 11. Future Improvement Opportunities

### Architectural Improvements
- **Proper Authentication**: Implement JWT-based authentication system
- **API Abstraction Layer**: Create service layer between controllers and database
- **Caching Strategy**: Implement Redis for API response caching

### Feature Enhancements
- **Document Ingestion**: Add support for uploading and processing educational materials
- **Vector Search**: Implement pgvector for semantic search capabilities
- **Advanced Study Tools**: Enhance quiz, flashcard, and study guide features
- **User Management**: Add user registration, profiles, and permission management
- **Analytics**: Add learning analytics and progress tracking

### UX Improvements
- **Real-time Collaboration**: Enable collaborative learning spaces
- **Mobile Responsiveness**: Enhance mobile user experience
- **Accessibility**: Improve accessibility features for diverse users
- **Offline Mode**: Enhance offline capabilities with service workers

---

This documentation provides a comprehensive overview of the Edutech AI Platform's current implementation and future directions. As the system evolves, this documentation should be updated to reflect architectural changes and new features.
