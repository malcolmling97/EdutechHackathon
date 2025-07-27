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

  const handleStartChat = async (content: string, file?: File | null) => {
    const title = content.slice(0, 30) || file?.name || 'New Chat';

    try {
      const now = new Date().toISOString();

      // 1. Create new space
      const space = await createSpace({
        type: 'chat',
        title,
        folderId: 'mock-folder',
        settings: {},
      });

      // 2. Save space to chat list
      const existingChats = JSON.parse(localStorage.getItem(CHAT_LIST_KEY) || '[]');
      existingChats.push({ id: space.id, title });
      localStorage.setItem(CHAT_LIST_KEY, JSON.stringify(existingChats));

      // 3. Save initial messages
      const initialMessages: ChatMessage[] = [];
      if (content) {
        initialMessages.push({
          id: crypto.randomUUID(),
          spaceId: space.id,
          role: 'user',
          content,
          createdAt: now,
          sources: [],
        });

        initialMessages.push({
          id: crypto.randomUUID(),
          spaceId: space.id,
          role: 'assistant',
          content: 'Got it! Let me help.',
          createdAt: now,
          sources: [],
        });
      }
      localStorage.setItem(`chat-messages-${space.id}`, JSON.stringify(initialMessages));

      // 4. Notify sidebar
      const event = new CustomEvent('add-chat', {
        detail: { id: space.id, title },
      });
      window.dispatchEvent(event);

      // 5. Navigate to chat
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
            const chatList = JSON.parse(localStorage.getItem(CHAT_LIST_KEY) || '[]');
          
            const typeMap: Record<string, CreatedSpace['type']> = {
              'summarise notes': 'notes',
              'notes': 'notes',
              'study guide': 'studyguide',
              'flashcards': 'flashcards',
              'quiz': 'quiz',
              'comprehension': 'openended',
            };
          
            const studyTypes: CreatedSpace['type'][] = [];
            let firstStudyType: CreatedSpace['type'] | null = null;
            let noteSpaceId: string | null = null;
          
            for (const option of options) {
              const normalized = option.trim().toLowerCase();
              const mappedType = typeMap[normalized];
          
              console.log('Option:', option, '→', mappedType);
          
              if (!mappedType) {
                console.warn('Unknown option:', option);
                continue;
              }
          
              if (mappedType === 'notes') {
                const noteSpace = await createSpace({
                  type: 'notes',
                  title: `Notes - ${selectedFile?.name ?? 'Untitled'}`,
                  folderId: 'mock-folder',
                  settings: {},
                });
          
                chatList.push({
                  id: noteSpace.id,
                  title: noteSpace.title,
                  type: 'notes',
                });
          
                noteSpaceId = noteSpace.id;
              } else {
                if (!firstStudyType) firstStudyType = mappedType;
                studyTypes.push(mappedType);
              }
            }
          
            if (studyTypes.length > 0 && firstStudyType) {
              const readableStudyLabels = options
                .filter(opt => typeMap[opt.trim().toLowerCase()] !== 'notes')
                .join(', ');
              const studyTitle = `${readableStudyLabels} - ${selectedFile?.name ?? 'Untitled'}`;
          
              const studySpace = await createSpace({
                type: firstStudyType,
                title: studyTitle,
                folderId: 'mock-folder',
                settings: { generatedTypes: studyTypes },
              });
          
              chatList.push({
                id: studySpace.id,
                title: studySpace.title,
                type: firstStudyType,
                settings: { generatedTypes: studyTypes },
              });
            } 
          
            localStorage.setItem(CHAT_LIST_KEY, JSON.stringify(chatList));
            window.dispatchEvent(new CustomEvent('spaces-added'));
          
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
