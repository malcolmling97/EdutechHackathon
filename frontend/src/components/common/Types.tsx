export interface ChatMessage {
    id: string;
    spaceId: string;
    role: 'user' | 'assistant';
    content: string;
    sources?: MessageSource[]; // optional for non-file messages
    createdAt: string;
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
    course?: string;
  }
  
  export interface CreatedSpace {
    id: string;
    title: string;
    folderId: string;
    createdAt: string;
  }

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