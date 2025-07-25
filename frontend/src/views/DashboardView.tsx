import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import ChatInput from '../components/chat/ChatInput';
import DropZoneWrapper from '../components/common/DropZoneWrapper';
import { MainDropIcon } from '../components/common/Icons';
import { ChatMessage } from '../components/common/Types';
import { createSpace } from '../utils/createSpace';

const DashboardView = () => {
  const navigate = useNavigate();
  const [selectedFile, setSelectedFile] = useState<File | null>(null);

  //when backend is set up
  /*

  const handleStartChat = async (message: string, file?: File | null) => {
  try {
    const title = message.slice(0, 30) || file?.name || 'New Chat';

    // 1. Create the space first
    const space = await createSpace({ title });

    // 2. Optionally store initial message locally
    const userText = message || `📎 Uploaded PDF: ${file?.name}`;
    const initialMessages = [
      {
        id: crypto.randomUUID(),
        spaceId: space.id,
        role: 'user',
        content: userText,
        sources: [],
        createdAt: new Date().toISOString(),
      },
      {
        id: crypto.randomUUID(),
        spaceId: space.id,
        role: 'assistant',
        content: 'Got it! Let me help.',
        sources: [],
        createdAt: new Date().toISOString(),
      },
    ];
    localStorage.setItem(`chat-messages-${space.id}`, JSON.stringify(initialMessages));

    // 3. Dispatch to sidebar if needed
    const event = new CustomEvent('add-chat', {
      detail: { id: space.id, title: space.title },
    });
    window.dispatchEvent(event);

    // 4. Navigate to new chat
    navigate(`/chat/${space.id}`);
  } catch (err) {
    console.error('Failed to start chat:', err);
  }
};

*/

  const handleStartChat = (message: string, file?: File | null) => {
    const id = `${Date.now()}-${Math.floor(Math.random() * 100000)}`;
    const title = message.slice(0, 30) || file?.name || 'New Chat';
    const userText = message || `📎 Uploaded PDF: ${file?.name}`;
    const now = new Date().toISOString();
  
    const initialMessages: ChatMessage[] = [
      {
        id: crypto.randomUUID(),
        spaceId: id,
        role: 'user',
        content: userText,
        createdAt: now,
        sources: [],
      },
      {
        id: crypto.randomUUID(),
        spaceId: id,
        role: 'assistant',
        content: 'Got it! Let me help.',
        createdAt: now,
        sources: [],
      },
    ];
  
    localStorage.setItem(`chat-messages-${id}`, JSON.stringify(initialMessages));
  
    const event = new CustomEvent('add-chat', {
      detail: { id, title },
    });
    window.dispatchEvent(event);
  
    navigate(`/chat/${id}`);
  };

  return (
    <DropZoneWrapper onFileDrop={(file) => setSelectedFile(file)}>
      <div className="flex h-screen bg-primary text-white">
        <main className="flex-1 flex flex-col items-center px-8 pt-8 pb-10">
          <div className="flex-grow" />
          <div className="text-center">
            <MainDropIcon className="h-28 w-24 mx-auto mb-6 text-gray-500" />
            <h1 className="text-3xl font-medium text-white mb-8">
              Drag and drop your material, or start a chat!
            </h1>
          </div>
          <div className="flex-grow-[1]" />
          <div className="w-full max-w-3xl">
            <ChatInput
              onSend={handleStartChat}
              dispatchChatEvent={false}
              selectedFile={selectedFile}
              setSelectedFile={setSelectedFile}
              clearSelectedFile={() => setSelectedFile(null)}
            />
          </div>
        </main>
      </div>
    </DropZoneWrapper>
  );
};

export default DashboardView;
