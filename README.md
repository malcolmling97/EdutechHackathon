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

## Planned Frontend–Backend Integration Requirements

The following describes the expected backend endpoints and data contracts that the frontend will require as the project evolves. This is to inform the backend team of upcoming integration needs.

### 1. Chat Functionality

The chat feature allows users to:
- Create new chat sessions
- List all existing chats
- Send messages and receive AI responses (planned: via backend)
- Delete chats
- Retrieve chat history

**Current Implementation:**
- All chat data is managed locally in the frontend state.
- AI responses are static placeholders.

**Planned Backend Integration:**
- All chat data and AI responses will be managed by the backend.

**Expected Endpoints:**
- **Create New Chat**
  - `POST /api/chats`
  - Request: `{ "title": "string" }`
  - Response: `{ "id": "string", "title": "string" }`

- **List Chats**
  - `GET /api/chats`
  - Response: `[ { "id": "string", "title": "string" } ]`

- **Send Message & Get AI Response**
  - `POST /api/chat/respond`
  - Request: `{ "chatId": "string", "message": "string" }`
  - Response: `{ "response": "string" }`

- **Get Chat History**
  - `GET /api/chats/{chatId}`
  - Response: `{ "id": "string", "title": "string", "messages": [ { "sender": "user" | "ai", "text": "string" } ] }`

- **Delete Chat**
  - `DELETE /api/chats/{chatId}`
  - Response: `{ "success": true }`

### 2. Projects
- **List Projects**
  - **Endpoint:** `GET /api/projects`
  - **Response:**
    ```json
    [
      { "id": "string", "title": "string" }
    ]
    ```

- **Get Project Details**
  - **Endpoint:** `GET /api/projects/{projectId}`
  - **Response:**
    ```json
    {
      "id": "string",
      "title": "string",
      "summary": "string"
    }
    ```

- **Create Project (from summary)**
  - **Endpoint:** `POST /api/projects`
  - **Request Body:**
    ```json
    {
      "title": "string",
      "summary": "string"
    }
    ```
  - **Response:**
    ```json
    { "id": "string" }
    ```

### 3. Quizzes
- **List Quizzes**
  - **Endpoint:** `GET /api/quizzes`
  - **Response:**
    ```json
    [
      { "id": "string", "title": "string" }
    ]
    ```

- **Get Quiz Details**
  - **Endpoint:** `GET /api/quizzes/{quizId}`
  - **Response:**
    ```json
    {
      "id": "string",
      "title": "string",
      "questions": [
        { "q": "string", "a": "string" }
      ]
    }
    ```

- **Create Quiz (from chat)**
  - **Endpoint:** `POST /api/quizzes`
  - **Request Body:**
    ```json
    {
      "title": "string",
      "questions": [
        { "q": "string", "a": "string" }
      ]
    }
    ```
  - **Response:**
    ```json
    { "id": "string" }
    ```

---

**Note:** These endpoints and data structures are suggestions based on current and planned frontend features. Please coordinate with the frontend team to finalize contracts and adjust as needed during implementation.

## File Structure

```
<project-root>/
├── public/               # Static assets (e.g., icons, images)
├── src/                  # Main source code
│   ├── components/       # Reusable React components (e.g., CollapsibleSection, MessageBubble)
│   ├── App.tsx           # Main application component and logic
│   ├── utils.tsx         # Utility functions (e.g., ID generation)
│   ├── types.ts          # TypeScript type definitions (Chat, Project, Quiz, etc.)
│   └── ...               # Other app files (styles, assets)
├── package.json          # Project metadata and dependencies
├── tailwind.config.js    # Tailwind CSS configuration
├── tsconfig.json         # TypeScript configuration
├── vite.config.ts        # Vite build tool configuration
└── README.md             # Project documentation
