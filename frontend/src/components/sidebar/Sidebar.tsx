import React, { useEffect, useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import SidebarLink from './SidebarLink';
import { getSpaces } from '../../utils/getSpaces';
import { CreatedSpace } from '../common/Types';
import { createSpace } from '../../utils/createSpace';
import {
  UserSpaceIcon, ResourcesIcon, ChatsIcon, NotesIcon, StudyIcon, SettingsIcon, SidebarToggleIcon, PlusIcon, PDFIcon, ChatAttachIcon,
} from '../common/Icons';

const CHAT_LIST_KEY = 'chat-list';

type ActiveTab = 'Resources' | 'Chats' | 'Notes' | 'Study';

const Sidebar = ({ isCollapsed, onToggle }: { isCollapsed: boolean, onToggle: () => void }) => {
  const [chats, setChats] = useState<{ id: string; title: string }[]>([]);
  const [activeTab, setActiveTab] = useState<ActiveTab>('Chats');
  const navigate = useNavigate();
  const location = useLocation();

  const getResourceIcon = (type: string) => {
    switch (type) {
      case 'PDF':
        return <PDFIcon className="w-4 h-4 text-white" />;
      case 'Note':
        return <NotesIcon className="w-4 h-4 text-white" />;
      case 'Link':
        return <ChatAttachIcon className="w-4 h-4 text-white" />;
      default:
        return <ResourcesIcon className="w-4 h-4 text-white" />;
    }
  };

  const [spaces, setSpaces] = useState<CreatedSpace[]>([]);

  useEffect(() => {
    const fetchSpacesData = async () => {
      try {
        const token = localStorage.getItem('token')!;
        const userId = localStorage.getItem('user-id')!;
        const data = await getSpaces(token, userId);
        setSpaces(data);
      } catch (err) {
        console.error('Error fetching spaces:', err);
      }
    };
  
    fetchSpacesData();
  }, []);

  const chatSpaces = spaces.filter(s => s.type === 'chat');
  const noteSpaces = spaces.filter(s => s.type === 'notes');
  const studySpaces = spaces.filter(s => s.type === 'studyguide' || s.type === 'quiz' || s.type === 'flashcards' || s.type === 'openended');
  //const resourceSpaces = spaces.filter(s => s.type === 'resources'); // only if "resources" is a valid type

  // Load chats from localStorage on mount or fetch from backend
  useEffect(() => {
    const stored = localStorage.getItem(CHAT_LIST_KEY);
    if (stored) {
      setChats(JSON.parse(stored));
    }
  }, []);

  // Save chats to localStorage whenever they change and/or sync with backend
  useEffect(() => {
    localStorage.setItem(CHAT_LIST_KEY, JSON.stringify(chats));
  }, [chats]);

  // Listen for global event to add new chat
  useEffect(() => {
    const listener = (e: Event) => {
      const detail = (e as CustomEvent).detail;
      const newChat = {
        id: detail.id, // Use the id from the event
        title: detail.title || `New Chat ${chats.length + 1}`,
      };
      setChats(prev => [...prev, newChat]);
      navigate(`/chat/${newChat.id}`);
    };

    window.addEventListener('add-chat', listener);
    return () => window.removeEventListener('add-chat', listener);
  }, [chats, navigate]);

  return (
    <div className={`flex flex-col h-screen bg-secondary border-r border-border-primary text-white p-2 transition-all duration-300 ${isCollapsed ? 'w-20' : 'w-64'}`}>
      <div className="flex-grow">
        <div className={`flex items-center mb-2 h-[42px] ${isCollapsed ? 'justify-center' : 'justify-between'}`}>
          {!isCollapsed && (
            <SidebarLink text="Malcolm's Space" icon={UserSpaceIcon} isCollapsed={isCollapsed} isButton={false} hasHover={false} iconClassName="text-white" />
          )}
          <button onClick={onToggle} className="p-1 rounded-lg text-white mr-1 cursor-pointer">
            <SidebarToggleIcon isCollapsed={isCollapsed} className="w-4 h-4 text-white" />
          </button>
        </div>
        <hr className="border-t border-border-primary -mx-2" />
        <nav className="flex flex-col gap-2 mt-2">
          {/*<SidebarLink text="Resources" icon={ResourcesIcon} isCollapsed={isCollapsed} iconClassName="text-white" onClick={() => setActiveTab('Resources')} />*/}
          <SidebarLink text="Chats" icon={ChatsIcon} isCollapsed={isCollapsed} iconClassName="text-white" onClick={() => setActiveTab('Chats')} />
          <SidebarLink text="Notes" icon={NotesIcon} isCollapsed={isCollapsed} iconClassName="text-white" onClick={() => setActiveTab('Notes')} />
          <SidebarLink text="Study" icon={StudyIcon} isCollapsed={isCollapsed} iconClassName="text-white" onClick={() => setActiveTab('Study')} />
        </nav>
        <hr className="border-t border-border-primary -mx-2 mt-2" />

        {/* Show chats only if sidebar is expanded */}
        {!isCollapsed && activeTab === 'Chats' && (
          <div className="mt-2 ml-2 flex flex-col gap-1">
            <div className="flex justify-between items-center mb-1">
              <h2 className="text-sm font-semibold text-white">Chats</h2>
              <button
                onClick={async () => {
                  try {
                    // Create empty chat space immediately
                    const newChat = await createSpace({
                      type: 'chat',
                      title: `New Chat ${spaces.length + 1}`,
                      folderId: 'mock-folder',
                      settings: {},
                    });
                
                    setSpaces(prev => [...prev, newChat]); // Add to sidebar memory
                    
                    // Also store in localStorage for dashboard to find
                    const existingChats = JSON.parse(localStorage.getItem(CHAT_LIST_KEY) || '[]');
                    localStorage.setItem(CHAT_LIST_KEY, JSON.stringify([...existingChats, { 
                      id: newChat.id, 
                      title: newChat.title 
                    }]));
                
                    // Navigate to dashboard (not chat window)
                    navigate('/');
                  } catch (err) {
                    console.error('Failed to create chat:', err);
                  }
                }}
                className="p-1 rounded-lg text-white hover:bg-gray-700"
              >
                <PlusIcon className="w-4 h-4" />
              </button>
            </div>
            {chatSpaces.map(chat => (
              <button
                key={chat.id}
                onClick={() => navigate(`/chat/${chat.id}`)}
                className={`flex items-center gap-2 px-2 py-1 text-sm rounded hover:bg-gray-700 text-white ${
                  location.pathname.includes(chat.id) ? 'bg-gray-700' : ''
                }`}
              >
                <ChatsIcon className="w-4 h-4 text-white" />
                <span className="text-white">{chat.title}</span>
              </button>
            ))}
          </div>
        )}

        {!isCollapsed && activeTab === 'Notes' && (
          <div className="mt-2 ml-2 flex flex-col gap-1">
            <div className="flex justify-between items-center mb-1">
              <h2 className="text-sm font-semibold text-white">Notes</h2>
              <button className="p-1 rounded-lg text-white hover:bg-gray-700">
                <PlusIcon className="w-4 h-4" />
              </button>
            </div>
            {noteSpaces.map(note => (
              <button
                key={note.id}
                onClick={() => navigate(`/notes/${note.id}`)}
                className="flex items-center gap-2 px-2 py-1 text-sm rounded hover:bg-gray-700 text-white"
              >
                <NotesIcon className="w-4 h-4 text-white" />
                <span className="text-white">{note.title}</span>
              </button>
            ))}
          </div>
        )}

        {/* Show study only if sidebar is expanded */}
        {!isCollapsed && activeTab === 'Study' && (
          <div className="mt-2 ml-2 flex flex-col gap-1">
            <div className="flex justify-between items-center mb-1">
              <h2 className="text-sm font-semibold text-white">Study</h2>
              <button className="p-1 rounded-lg text-white hover:bg-gray-700">
                <PlusIcon className="w-4 h-4" />
              </button>
            </div>
            {studySpaces.map(item => (
              <button
                key={item.id}
                onClick={() => navigate(`/study/${item.id}`)}
                className="flex items-center gap-2 px-2 py-1 text-sm rounded hover:bg-gray-700 text-white"
              >
                <StudyIcon className="w-4 h-4 text-white" />
                <span className="text-white">{item.title}</span>
              </button>
            ))}
          </div>
        )}
      </div>

      <div className="flex-shrink-0">
        <hr className="border-t border-border-primary -mx-2 mb-2" />
        <SidebarLink text="Settings" icon={SettingsIcon} isCollapsed={isCollapsed} hasHover={false} iconClassName="text-white" />
      </div>
    </div>
  );
};

export default Sidebar;
