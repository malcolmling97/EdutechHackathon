import React, { useEffect, useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import SidebarLink from './SidebarLink';
import { getSpaces } from '../../utils/getSpaces';
import { getResources } from '../../utils/getResources';
import { getNotesList } from '../../utils/getNotesList';
import { getStudyList } from '../../utils/getStudyList';
import {
  UserSpaceIcon, ResourcesIcon, ChatsIcon, NotesIcon, StudyIcon, SettingsIcon, SidebarToggleIcon, PlusIcon, PDFIcon, ChatAttachIcon,
} from '../common/Icons';

const generateId = () => `${Date.now()}-${Math.floor(Math.random() * 100000)}`;
const CHAT_LIST_KEY = 'chat-list';

type ActiveTab = 'Resources' | 'Chats' | 'Notes' | 'Study';

const Sidebar = ({ isCollapsed, onToggle }: { isCollapsed: boolean, onToggle: () => void }) => {
  const [chats, setChats] = useState<{ id: string; title: string }[]>([]);
  const [resources, setResources] = useState<{ id: string; title: string; type: string }[]>([]);
  const [notes, setNotes] = useState<{ id: string; title: string }[]>([]);
  const [study, setStudy] = useState<{ id: string; title: string }[]>([]);
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

  //when backend is set up 
  /*
  useEffect(() => {
  const fetchChats = async () => {
    try {
      const data = await getSpaces();
      const chatList = data.map(space => ({
        id: space.id,
        title: space.title,
      }));
      setChats(chatList);
    } catch (err) {
      console.error('Error fetching spaces:', err);
    }
  };

  const fetchResources = async () => {
    try {
      // Assuming you have a current space ID, otherwise this needs to be dynamic
      const data = await getResources('some-space-id');
      setResources(data);
    } catch (err) {
      console.error('Error fetching resources:', err);
    }
  }

  fetchChats();
  fetchResources();
}, []);
*/
  useEffect(() => {
    const fetchResources = async () => {
      try {
        // Assuming you have a current space ID, otherwise this needs to be dynamic
        const data = await getResources('some-space-id');
        setResources(data);
      } catch (err) {
        console.error('Error fetching resources:', err);
      }
    }
    const fetchNotes = async () => {
      try {
        const data = await getNotesList();
        setNotes(data);
      } catch (err) {
        console.error('Error fetching notes:', err);
      }
    }
    const fetchStudy = async () => {
      try {
        const data = await getStudyList();
        setStudy(data);
      } catch (err) {
        console.error('Error fetching study:', err);
      }
    }
    fetchResources();
    fetchNotes();
    fetchStudy();
  }, [])

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
          <SidebarLink text="Resources" icon={ResourcesIcon} isCollapsed={isCollapsed} iconClassName="text-white" onClick={() => setActiveTab('Resources')} />
          <SidebarLink text="Chats" icon={ChatsIcon} isCollapsed={isCollapsed} iconClassName="text-white" onClick={() => setActiveTab('Chats')} />
          <SidebarLink text="Notes" icon={NotesIcon} isCollapsed={isCollapsed} iconClassName="text-white" onClick={() => setActiveTab('Notes')} />
          <SidebarLink text="Study" icon={StudyIcon} isCollapsed={isCollapsed} iconClassName="text-white" onClick={() => setActiveTab('Study')} />
        </nav>
        <hr className="border-t border-border-primary -mx-2 mt-2" />

        {/* Show chats only if sidebar is expanded */}
        {!isCollapsed && activeTab === 'Chats' && (
          <div className="mt-2 ml-2 flex flex-col gap-1">
            <div className='flex justify-between items-center mb-1'>
              <h2 className="text-sm font-semibold text-white">Chats</h2>
              <button className="p-1 rounded-lg text-white hover:bg-gray-700">
                <PlusIcon className="w-4 h-4" />
              </button>
            </div>
            {chats.map(chat => (
              <button
                key={chat.id}
                onClick={() => navigate(`/chat/${chat.id}`)}
                className={`flex items-center gap-2 px-2 py-1 text-sm rounded hover:bg-gray-700 text-white ${location.pathname.includes(chat.id) ? 'bg-gray-700' : ''
                  }`}
              >
                <ChatsIcon className="w-4 h-4 text-white" />
                <span className="text-white">{chat.title}</span>
              </button>
            ))}
          </div>
        )}

        {/* Show resources only if sidebar is expanded */}
        {!isCollapsed && activeTab === 'Resources' && (
          <div className="mt-2 ml-2 flex flex-col gap-1">
            <div className='flex justify-between items-center mb-1'>
              <h2 className="text-sm font-semibold text-white">Resources</h2>
              <button className="p-1 rounded-lg text-white hover:bg-gray-700">
                <PlusIcon className="w-4 h-4" />
              </button>
            </div>
            {resources.map(resource => (
              <button
                key={resource.id}
                // onClick={() => navigate(`/resource/${resource.id}`)}
                className={`flex items-center gap-2 px-2 py-1 text-sm rounded hover:bg-gray-700 text-white`}
              >
                {getResourceIcon(resource.type)}
                <span className="text-white">{resource.title}</span>
              </button>
            ))}
          </div>
        )}

        {/* Show notes only if sidebar is expanded */}
        {!isCollapsed && activeTab === 'Notes' && (
          <div className="mt-2 ml-2 flex flex-col gap-1">
            <div className='flex justify-between items-center mb-1'>
              <h2 className="text-sm font-semibold text-white">Notes</h2>
              <button className="p-1 rounded-lg text-white hover:bg-gray-700">
                <PlusIcon className="w-4 h-4" />
              </button>
            </div>
            {notes.map(note => (
              <button
                key={note.id}
                onClick={() => navigate(`/notes/${note.id}`)}
                className={`flex items-center gap-2 px-2 py-1 text-sm rounded hover:bg-gray-700 text-white`}
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
            <div className='flex justify-between items-center mb-1'>
              <h2 className="text-sm font-semibold text-white">Study</h2>
              <button className="p-1 rounded-lg text-white hover:bg-gray-700">
                <PlusIcon className="w-4 h-4" />
              </button>
            </div>
            {study.map(item => (
              <button
                key={item.id}
                onClick={() => navigate(`/study/${item.id}`)}
                className={`flex items-center gap-2 px-2 py-1 text-sm rounded hover:bg-gray-700 text-white`}
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
