import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import ChatInput from '../components/chat/ChatInput';
import ChatWindow from '../components/chat/ChatWindow';
import DropZoneWrapper from '../components/common/DropZoneWrapper';

import { sendChatMessage } from '../utils/sendChatMessage';
import type { ChatMessage } from '../components/common/Types';



const ChatView = () => {
  const { id: spaceId } = useParams(); // spaceId = chatId
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  

  // Load messages from localStorage or backend
  useEffect(() => {
    const stored = localStorage.getItem(`chat-messages-${spaceId}`);
    if (stored) {
      setMessages(JSON.parse(stored));
    }

    // TODO: Replace with real backend fetch
    // fetch(`/api/messages?spaceId=${spaceId}`).then(...)
  }, [spaceId]);

  const handleSendMessage = async (content: string, file?: File | null) => {
    if (!spaceId) return;
  
    try {
      // Mock the user's message manually instead of relying on sendChatMessage
      const newMessage: ChatMessage = {
        id: crypto.randomUUID(),
        spaceId,
        role: 'user',
        content,
        createdAt: new Date().toISOString(),
        sources: [],
      };
  
      const newMessages: ChatMessage[] = [
        ...messages,
        newMessage,
        {
          id: crypto.randomUUID(),
          spaceId,
          role: 'assistant',
          content: 'Got it!',
          createdAt: new Date().toISOString(),
          sources: [],
        },
      ];
  
      setMessages(newMessages);
      localStorage.setItem(`chat-messages-${spaceId}`, JSON.stringify(newMessages));
    } catch (err) {
      console.error('Failed to send message:', err);
    }
  };
  
/* Until backend is ready
  // Handle sending message
  const handleSendMessage = async (content: string, file?: File | null) => {
    if (!spaceId) return;

    try {
      const newMessage = await sendChatMessage({
        spaceId,
        content,
        file,
        role: 'user',
      });

      // Add user message + placeholder AI response (optional) can remove once fetch works
      const newMessages: ChatMessage[] = [
        ...messages,
        newMessage,
        {
          id: crypto.randomUUID(),
          spaceId,
          role: 'assistant',
          content: 'Got it!',
          createdAt: new Date().toISOString(),
          sources: [],
        },
      ];

      setMessages(newMessages);
      localStorage.setItem(`chat-messages-${spaceId}`, JSON.stringify(newMessages));
    } catch (err) {
      console.error('Failed to send message:', err);
    }
  };
*/
  return (
    <DropZoneWrapper onFileDrop={setSelectedFile}>
    <div className="flex flex-col h-full px-8 pt-8 pb-4 max-w-5xl mx-auto">
      <ChatWindow messages={messages} />
      <ChatInput
        onSend={handleSendMessage}
        selectedFile={selectedFile}
        setSelectedFile={setSelectedFile}
        clearSelectedFile={() => setSelectedFile(null)}
      />
    </div>
  </DropZoneWrapper>
  );
};

export default ChatView;
