
# Frontend Architecture Blueprint: Edutech AI Learning App

This document outlines a high-level frontend architecture for the Edutech AI Learning application. It is based on the initial Figma design and assumes a modern tech stack of **React (with TypeScript)** and **Tailwind CSS**.

The goal of this architecture is to be scalable, maintainable, and to provide a clear separation of concerns, allowing for iterative development.

---

## 1. Core Concepts & Philosophy

-   **Component-Driven:** The UI will be built as a composition of small, reusable components.
-   **View-Based Routing:** The application is divided into distinct "views" or "pages," each corresponding to a major feature accessible from the main navigation (e.g., the sidebar).
-   **Centralized State Management:** Global state (like user info, authentication status, or the current set of resources) will be managed in a dedicated location to avoid prop-drilling.
-   **Layouts for Consistency:** A shared "layout" component will provide the consistent application shell (sidebar, header, etc.) for all authenticated views.

---

## 2. Proposed Folder Structure

A clean folder structure is essential for scalability. Here is the proposed layout within the `frontend/src/` directory:

```
frontend/src/
│
├── api/
│   ├── chatAPI.ts         # Functions for interacting with the chat/AI backend
│   └── resourcesAPI.ts    # Functions for uploading/managing user documents
│
├── assets/
│   └── icons/             # SVG icons used throughout the application
│
├── components/
│   ├── common/            # Small, highly reusable "dumb" components
│   │   ├── Button.tsx
│   │   ├── Spinner.tsx
│   │   └── Modal.tsx
│   │
│   └── specific/          # More complex components, specific to a feature
│       ├── MessageBubble.tsx
│       ├── ResourceCard.tsx
│       └── CollapsibleSection.tsx
│
├── hooks/
│   ├── useAuth.ts         # Hook for authentication logic
│   └── useChat.ts         # Hook for managing chat session state & logic
│
├── layouts/
│   ├── AppLayout.tsx      # The main authenticated layout (with sidebar)
│   └── AuthLayout.tsx     # A simple centered layout for Login/Signup pages
│
├── state/
│   ├── userStore.ts       # State management for user data (using Zustand/Jotai/etc.)
│   └── resourcesStore.ts  # State management for the user's documents
│
├── types/
│   └── index.ts           # Centralized TypeScript type definitions
│
├── utils/
│   └── dateUtils.ts       # Example utility functions
│
└── views/
    ├── Auth/
    │   ├── LoginView.tsx
    │   └── SignupView.tsx
    │
    ├── DashboardView.tsx    # The main landing page after login ("drag and drop" view)
    ├── ResourcesView.tsx    # View to manage uploaded documents
    ├── ChatView.tsx         # The main conversational interface
    ├── NotesView.tsx        # View for creating and managing notes
    ├── StudyView.tsx        # View for quizzes, flashcards, or study sessions
    └── SettingsView.tsx     # View for user account settings
```

---

## 3. Key Views & Main Sections

These are the primary top-level pages of the application, corresponding to the routes a user can visit.

### a. `Auth` Views (`/login`, `/signup`)

-   **Purpose:** Handle user authentication.
-   **Sections:** A simple form centered on the page.
-   **Layout:** Uses `AuthLayout.tsx`.

### b. `DashboardView.tsx` (`/`)

-   **Purpose:** The initial screen for an authenticated user. It serves as a starting point to either upload new material or start a conversation.
-   **Sections:**
    -   **Welcome/Instruction Text:** "Drag and drop your material..."
    -   **Dropzone:** An area for file uploads.
    -   **Chat Input:** The primary call-to-action at the bottom of the screen.
-   **Layout:** Uses `AppLayout.tsx`.

### c. `ResourcesView.tsx` (`/resources`)

-   **Purpose:** Allows users to see, manage, and delete the documents they have uploaded.
-   **Sections:**
    -   **Resource List/Grid:** A display of `ResourceCard` components.
    -   **Upload Button:** An alternative way to upload files.
    -   **Search/Filter Bar:** To find specific documents.
-   **Layout:** Uses `AppLayout.tsx`.

### d. `ChatView.tsx` (`/chat` or `/chat/:id`)

-   **Purpose:** The core interactive feature where users converse with the AI about their resources.
-   **Sections:**
    -   **Chat History:** A scrollable list of `MessageBubble` components.
    -   **Chat Input Form:** The text area and send button at the bottom.
    -   **Context Sidebar (Optional):** A panel showing which resources are active in the current conversation.
-   **Layout:** Uses `AppLayout.tsx`.

### e. `NotesView.tsx` (`/notes`)

-   **Purpose:** A dedicated space for users to take notes, which could be linked to their resources or chats.
-   **Sections:**
    -   **Note List:** A sidebar listing all created notes.
    -   **Editor Pane:** A rich text editor for the selected note.
-   **Layout:** Uses `AppLayout.tsx`.

### f. `StudyView.tsx` (`/study`)

-   **Purpose:** Provides focused study tools generated from the user's materials.
-   **Sections:**
    -   **Tool Selector:** Buttons to choose between "Quiz," "Flashcards," or "Summary."
    -   **Interactive Area:** The main content area where the selected study tool is displayed.
-   **Layout:** Uses `AppLayout.tsx`.

---

## 4. Layouts & Key Components

-   **`AppLayout.tsx`:** This is a critical component that will wrap most of the views. It is responsible for rendering the persistent UI shell, primarily the **Main Sidebar**. The sidebar component itself will contain the navigation links seen in the Figma design (`Resources`, `Chats`, etc.).

-   **`MessageBubble.tsx`:** A component to display a single chat message, with variations for user messages vs. AI responses.

-   **`ResourceCard.tsx`:** A component to display a single uploaded document in the `ResourcesView`, showing its name, type, and providing options to delete or chat about it.

This blueprint provides a solid foundation. The next step is to use the "Page Scaffolder" workflow to create the initial code for each of these views, starting with `DashboardView.tsx`. 