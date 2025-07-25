import React, { useEffect, useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import SidebarLink from './SidebarLink';
import { getSpaces } from '../../utils/getSpaces'
import {
  UserSpaceIcon, ResourcesIcon, ChatsIcon, NotesIcon, StudyIcon, SettingsIcon, SidebarToggleIcon,
} from '../common/Icons';

const generateId = () => `${Date.now()}-${Math.floor(Math.random() * 100000)}`;
const CHAT_LIST_KEY = 'chat-list';

const Sidebar = ({ isCollapsed, onToggle }: { isCollapsed: boolean, onToggle: () => void }) => {
  const [chats, setChats] = useState<{ id: string; title: string }[]>([]);
  const navigate = useNavigate();
  const location = useLocation();

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

  fetchChats();
}, []);
*/

  // Load chats from localStorage on mount or fetch from backend
  useEffect(() => {
    const stored = localStorage.getItem(CHAT_LIST_KEY);
    if (stored) {
      setChats(JSON.parse(stored));
    }
  }, []);

  // Save chats to localStorage whenever they change and/or sync with backend
  useEffect(() => {
    // TODO: Optionally, send a POST/PUT request to your backend to update the user's chat list
    // Example:
    // fetch('/api/chats', {
    //   method: 'PUT',
    //   headers: { 'Content-Type': 'application/json' },
    //   body: JSON.stringify(chats),
    // });
    localStorage.setItem(CHAT_LIST_KEY, JSON.stringify(chats));
  }, [chats]);

  // Listen for global event to add new chat
  useEffect(() => {
    const listener = (e: Event) => {
      const detail = (e as CustomEvent).detail;
      // TODO: Optionally, send a POST request to your backend to create a new chat session
      // Example:
      // fetch('/api/chats', {
      //   method: 'POST',
      //   headers: { 'Content-Type': 'application/json' },
      //   body: JSON.stringify({ id: detail.id, title: detail.title }),
      // });
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
            <SidebarLink text="Malcolm's Space" icon={UserSpaceIcon} isCollapsed={isCollapsed} isButton={false} hasHover={false} />
          )}
          <button onClick={onToggle} className="p-1 rounded-lg text-content-secondary mr-1 cursor-pointer">
            <SidebarToggleIcon isCollapsed={isCollapsed} className="w-4 h-4" />
          </button>
        </div>
        <hr className="border-t border-border-primary -mx-2" />
        <nav className="flex flex-col gap-2 mt-2">
          {/*<SidebarLink text="Resources" icon={ResourcesIcon} isCollapsed={isCollapsed} />*/}
          <SidebarLink text="Chats" icon={ChatsIcon} isCollapsed={isCollapsed} to="/" />
          <SidebarLink text="Notes" icon={NotesIcon} isCollapsed={isCollapsed} />
          <SidebarLink text="Study" icon={StudyIcon} isCollapsed={isCollapsed} to="/study"/>
        </nav>
        <hr className="border-t border-border-primary -mx-2 mt-2" />

        {/* Show chats only if sidebar is expanded */}
        {!isCollapsed && (
          <div className="mt-2 ml-2 flex flex-col gap-1">
            {chats.map(chat => (
              <button
                key={chat.id}
                onClick={() => navigate(`/chat/${chat.id}`)}
                className={`flex items-center gap-2 px-2 py-1 text-sm rounded hover:bg-gray-700 ${
                  location.pathname.includes(chat.id) ? 'bg-gray-700' : ''
                }`}
              >
                💬 {chat.title}
              </button>
            ))}
          </div>
        )}
      </div>

      <div className="flex-shrink-0">
        <hr className="border-t border-border-primary -mx-2 mb-2" />
        <SidebarLink text="Settings" icon={SettingsIcon} isCollapsed={isCollapsed} hasHover={false} />
      </div>
    </div>
  );
};

export default Sidebar;
