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

  useEffect(() => {
    const stored = localStorage.getItem(`chat-messages-${spaceId}`);
    if (stored) {
      setMessages(JSON.parse(stored));
    } else {
      setMessages([]); // reset messages if no stored data
    }
  }, [spaceId]);

  const handleSendMessage = async (content: string, file?: File | null) => {
    if (!spaceId) return;

    try {
      const now = new Date().toISOString();

      const userMessage: ChatMessage = {
        id: crypto.randomUUID(),
        spaceId,
        role: 'user',
        content: file?.name || content,
        createdAt: now,
        sources: [],
      };

      const aiMessage: ChatMessage = {
        id: crypto.randomUUID(),
        spaceId,
        role: 'assistant',
        content: 'Got it!',
        createdAt: now,
        sources: [],
      };

      const newMessages = [...messages, userMessage, aiMessage];
      setMessages(newMessages);
      localStorage.setItem(`chat-messages-${spaceId}`, JSON.stringify(newMessages));
    } catch (err) {
      console.error('Failed to send message:', err);
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
