export interface Message {
    sender: 'user' | 'ai';
    text: string;
  }
  
  export interface Chat {
    id: number;
    title: string;
    messages: Message[];
  }
  
  export interface Project {
    title: string;
    summary: string;
  }
  
  export interface Quiz {
    title: string;
    questions: { q: string; a: string }[];
  }
  