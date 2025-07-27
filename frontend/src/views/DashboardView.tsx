import React, { useState, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import ChatInput from '../components/chat/ChatInput';
import DropZoneWrapper from '../components/common/DropZoneWrapper';
import GenerationModal from '../components/common/GenerationModal';
import { createSpace } from '../utils/createSpace';
import { ChatMessage, CreatedSpace } from '../components/common/Types';

const CHAT_LIST_KEY = 'chat-list';

const DashboardView = () => {
  const navigate = useNavigate();
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleStartChat = async (content: string) => {
    try {
      const title = content.slice(0, 30) || 'New Chat';

      // 1. Create new chat space
      const space = await createSpace({
        type: 'chat',
        title,
        folderId: 'mock-folder',
        settings: {},
      });

      // 2. Save to chat list
      const existingChats = JSON.parse(localStorage.getItem(CHAT_LIST_KEY) || '[]');
      existingChats.push({ id: space.id, title });
      localStorage.setItem(CHAT_LIST_KEY, JSON.stringify(existingChats));

      // 3. Save initial messages
      const now = new Date().toISOString();
      const initialMessages: ChatMessage[] = [
        {
          id: crypto.randomUUID(),
          spaceId: space.id,
          role: 'user',
          content,
          createdAt: now,
          sources: [],
        },
        {
          id: crypto.randomUUID(),
          spaceId: space.id,
          role: 'assistant',
          content: 'Got it! Let me help.',
          createdAt: now,
          sources: [],
        },
      ];
      localStorage.setItem(`chat-messages-${space.id}`, JSON.stringify(initialMessages));

      // 4. Redirect to chat view
      navigate(`/chat/${space.id}`);
    } catch (err) {
      console.error('Failed to start chat:', err);
    }
  };

  const handleFileDrop = (file: File) => {
    setSelectedFile(file);
    setIsModalOpen(true);
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      handleFileDrop(file);
      e.target.value = '';
    }
  };

  const openFileDialog = () => {
    fileInputRef.current?.click();
  };

  return (
    <>
      <input
        type="file"
        ref={fileInputRef}
        onChange={handleFileChange}
        className="hidden"
        accept="application/pdf"
      />
      <DropZoneWrapper onFileDrop={handleFileDrop}>
        <div className="flex h-screen bg-primary text-white">
          <main className="flex-1 flex flex-col items-center px-8 pt-8 pb-10">
            <div className="flex-grow" />
            <div className="text-center cursor-pointer" onClick={openFileDialog}>
              <h1 className="text-4xl font-medium text-white mb-4">
                What are we diving into today?
              </h1>
              <p className="text-lg text-gray-400 mb-8">
                Drag and drop your material, or start a chat!
              </p>
            </div>
            <div className="flex-grow-[1]" />
            <div className="w-full max-w-3xl">
              <ChatInput
                onSend={handleStartChat}
                dispatchChatEvent={false}
                selectedFile={selectedFile}
                setSelectedFile={(file) => file && handleFileDrop(file)}
                clearSelectedFile={() => {
                  setSelectedFile(null);
                  setIsModalOpen(false);
                }}
              />
            </div>
          </main>
        </div>
      </DropZoneWrapper>

      {isModalOpen && selectedFile && (
        <GenerationModal
          onGenerate={async (options) => {
            const selectedType = options[0];

            const typeMap: Record<string, CreatedSpace['type']> = {
              'Summarise Notes': 'notes',
              'Study Guide': 'studyguide',
              'Flashcards': 'flashcards',
              'Quiz': 'quiz',
              'Comprehension': 'openended',
            };

            const type = typeMap[selectedType] || 'notes';

            const space = await createSpace({
              type,
              title: `${selectedType} - ${selectedFile?.name ?? 'Untitled'}`,
              folderId: 'mock-folder',
              settings: {},
            });

            const list = JSON.parse(localStorage.getItem(CHAT_LIST_KEY) || '[]');
            list.push({ id: space.id, title: space.title });
            localStorage.setItem(CHAT_LIST_KEY, JSON.stringify(list));

            setIsModalOpen(false);
            setSelectedFile(null);
            navigate(`/${type}/${space.id}`);
          }}
          onClose={() => {
            setIsModalOpen(false);
            setSelectedFile(null);
          }}
        />
      )}
    </>
  );
};

export default DashboardView;
