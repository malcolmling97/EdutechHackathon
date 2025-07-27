import React, { useState, useRef, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import ChatInput from '../components/chat/ChatInput';
import DropZoneWrapper from '../components/common/DropZoneWrapper';
import GenerationModal from '../components/common/GenerationModal';
import { createSpace } from '../utils/createSpace';
import { ChatMessage } from '../components/common/Types';

const DashboardView = () => {
  const navigate = useNavigate();
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);
  
  useEffect(() => {
    const CHAT_LIST_KEY = 'chat-list';
    const storedChats = localStorage.getItem(CHAT_LIST_KEY);
    if (storedChats) {
      const chats = JSON.parse(storedChats);
      if (chats.length > 0) {
        navigate(`/chat/${chats[0].id}`);
      }
    }
  }, [navigate]);

  const handleStartChat = async (content: string, file?: File | null) => {
    if (file) {
      handleFileDrop(file);
    } else {
      const { id } = await createSpace({ title: content });
      const now = new Date().toISOString();
      const initialMessages: ChatMessage[] = [
        {
          id: crypto.randomUUID(),
          spaceId: id,
          role: 'user',
          content,
          createdAt: now,
        },
        {
          id: crypto.randomUUID(),
          spaceId: id,
          role: 'assistant',
          content: 'Got it! Let me help.',
          createdAt: now,
        },
      ];
      localStorage.setItem(`chat-messages-${id}`, JSON.stringify(initialMessages));
      navigate(`/chat/${id}`);
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
      e.target.value = ''; // Reset file input
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
          onGenerate={(options) => {
            console.log(`Generating: ${options.join(', ')} for file: ${selectedFile?.name}`);
            // We will implement the logic for this in the next steps
            setIsModalOpen(false);
            setSelectedFile(null);
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
