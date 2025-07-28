import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import ChatInput from '../components/chat/ChatInput';
import ChatWindow from '../components/chat/ChatWindow';
import DropZoneWrapper from '../components/common/DropZoneWrapper';

import { fetchChatHistory, sendChatMessage } from '../utils/api';
import type { ChatMessage } from '../components/common/Types';

const ChatView = () => {
  const { id: spaceId } = useParams(); // spaceId = chatId
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);

  useEffect(() => {
    if (!spaceId) return;
    
    console.log(`[ChatView] Initializing chat for spaceId: ${spaceId}`);
    
    // First try to load from localStorage for immediate display
    const stored = localStorage.getItem(`chat-messages-${spaceId}`);
    if (stored) {
      console.log(`[ChatView] Found cached messages for spaceId: ${spaceId}`);
      setMessages(JSON.parse(stored));
    } else {
      console.log(`[ChatView] No cached messages found for spaceId: ${spaceId}`);
      setMessages([]); // reset messages if no stored data
    }
    
    // Then fetch from API
    const loadMessages = async () => {
      try {
        console.log(`[ChatView] Fetching messages from API for spaceId: ${spaceId}`);
        const chatMessages = await fetchChatHistory(spaceId);
        console.log(`[ChatView] Received ${chatMessages.length} messages from API`);
        
        if (chatMessages.length > 0) {
          setMessages(chatMessages);
          localStorage.setItem(`chat-messages-${spaceId}`, JSON.stringify(chatMessages));
          console.log(`[ChatView] Updated messages from API and saved to localStorage`);
        }
      } catch (error) {
        console.error(`[ChatView] Error loading chat history for spaceId: ${spaceId}:`, error);
        // Add system error message to chat
        setMessages(prev => [...prev, {
          id: crypto.randomUUID(),
          spaceId,
          role: 'system',
          content: 'Failed to load chat history. Please try refreshing the page.',
          createdAt: new Date().toISOString(),
          sources: [],
          isError: true
        }]);
      }
    };
    
    loadMessages();
  }, [spaceId]);

  const handleSendMessage = async (content: string, file?: File | null) => {
    if (!spaceId || !content.trim()) return;

    try {
      console.log(`[ChatView] Sending message to spaceId: ${spaceId}, content length: ${content.length}`);
      
      // Optimistically add user message to UI
      const tempId = crypto.randomUUID();
      const now = new Date().toISOString();
      
      const userMessage: ChatMessage = {
        id: tempId,
        spaceId,
        role: 'user',
        content: content,
        createdAt: now,
        sources: [],
      };
      
      console.log(`[ChatView] Added user message with id: ${tempId}`);
      
      // Show loading state
      const loadingMessage: ChatMessage = {
        id: crypto.randomUUID(),
        spaceId,
        role: 'assistant',
        content: 'Thinking...',
        createdAt: now,
        sources: [],
        isLoading: true
      };
      
      const updatedMessages = [...messages, userMessage, loadingMessage];
      setMessages(updatedMessages);
      console.log(`[ChatView] Added loading message, waiting for API response...`);
      
      // Send to API
      console.log(`[ChatView] Calling sendChatMessage API with spaceId: ${spaceId}`);
      const response = await sendChatMessage(spaceId, content);
      console.log(`[ChatView] Received API response:`, response);
      
      // Replace loading message with actual response
      const finalMessages = updatedMessages.filter(msg => !msg.isLoading);
      finalMessages.push({
        id: response.assistantMessage.id,
        spaceId,
        role: 'assistant',
        content: response.assistantMessage.content,
        createdAt: response.assistantMessage.createdAt,
        sources: [],
      });
      
      console.log(`[ChatView] Updated messages with AI response`);
      setMessages(finalMessages);
      localStorage.setItem(`chat-messages-${spaceId}`, JSON.stringify(finalMessages));
    } catch (err) {
      console.error(`[ChatView] Failed to send message to spaceId: ${spaceId}:`, err);
      
      // Remove loading message on error
      const errorMessages = messages.filter(msg => !msg.isLoading);
      setMessages(errorMessages);
      
      // Add detailed error message
      const errorContent = err instanceof Error 
        ? `Error: ${err.message}` 
        : 'Sorry, there was an error processing your message. Please try again.';
      
      const errorMessage: ChatMessage = {
        id: crypto.randomUUID(),
        spaceId,
        role: 'system',
        content: errorContent,
        createdAt: new Date().toISOString(),
        sources: [],
        isError: true
      };
      
      console.log(`[ChatView] Added error message to chat`);
      setMessages([...errorMessages, errorMessage]);
    }
  };

  return (
    <DropZoneWrapper onFileDrop={setSelectedFile}>
      <div className="flex flex-col h-full px-8 pt-8 pb-4 max-w-5xl mx-auto">
        <ChatWindow messages={messages} />
        <ChatInput
          onSend={handleSendMessage}
          dispatchChatEvent={false}   // ✅ Prevent redundant event
          spaceId={spaceId}           // ✅ Maintain context
          selectedFile={selectedFile}
          setSelectedFile={setSelectedFile}
          clearSelectedFile={() => setSelectedFile(null)}
        />
      </div>
    </DropZoneWrapper>
  );
};

export default ChatView;
