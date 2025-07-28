export interface ChatMessage {
    id: string;
    spaceId: string;
    role: 'user' | 'assistant' | 'system';
    content: string;
    sources?: MessageSource[]; // optional for non-file messages
    createdAt: string;
    isLoading?: boolean;
    isError?: boolean;
  }
  
  export interface ChatSession {
  id: string;
  course: string;
  title: string;
}

export interface FileMetadata {
    id: string;
    name: string;
    size: number;
    mime: string;
    text: string;
    folderId: string;
    createdAt: string;
  }
  
export interface MessageSource {
    fileId: string;
    page: number;
  }
  
export interface SendChatOptions {
    spaceId: string;
    content: string;
    file?: File | null;
    folderId?: string;
    role?: 'user' | 'assistant';
  }

  export interface CreateSpacePayload {
    title: string;
    type: 'chat' | 'notes' | 'quiz' | 'flashcards' | 'studyguide' | 'openended'| 'resources'; // strict string union
    folderId: string;
    settings?: Record<string, any>; // optional customization
  }
  
  export type CreatedSpace = {
    id: string;
    folderId: string;
    type: 'chat' | 'quiz' | 'notes' | 'openended' | 'flashcards' | 'studyguide' | 'resources'; 
    title: string;
    settings: Record<string, any>;
  };

export interface GenerateQuizOptions {
    spaceId: string;
    title?: string;
    fileIds?: string[];
    questionCount?: number;
    questionTypes?: ('mcq' | 'tf' | 'short')[];
    difficulty?: 'easy' | 'medium' | 'hard';
    token: string;
    userId: string;
  }
  
  export interface GetQuizOptions {
    quizId: string;
    token: string;
    userId: string;
  }

  export interface Flashcard {
    id: string;
    front: string;
    back: string;
  }  

  type Question = {
    id: string;
    prompt: string;
    choices: string[];
    answer: string;
    explanation?: string;
  };
  
  type QuizType = {
    id: string;
    title: string;
    questions: Question[];
  };
  

  