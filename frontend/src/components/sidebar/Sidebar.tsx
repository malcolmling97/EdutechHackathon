  import React, { useEffect, useState } from 'react';
  import { useNavigate, useLocation } from 'react-router-dom';
  import SidebarLink from './SidebarLink';
  import { getSpaces } from '../../utils/getSpaces';
  import { CreatedSpace } from '../common/Types';
  import { createSpace } from '../../utils/createSpace';
  import EditableTitle from '../common/EditableTitle';
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
          if (!localStorage.getItem('token')) {
            localStorage.setItem('token', 'mock-token');
          }
          if (!localStorage.getItem('user-id')) {
            localStorage.setItem('user-id', 'mock-user');
          }
          
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

    useEffect(() => {
      const listener = (e: Event) => {
        const token = localStorage.getItem('token')!;
        const userId = localStorage.getItem('user-id')!;
        getSpaces(token, userId).then(setSpaces);
      };
    
      window.addEventListener('spaces-added', listener);
      return () => window.removeEventListener('spaces-added', listener);
    }, []);

    useEffect(() => {
      const refresh = async () => {
        const token = localStorage.getItem('token')!;
        const userId = localStorage.getItem('user-id')!;
        const data = await getSpaces(token, userId);
        setSpaces(data);
      };
    
      window.addEventListener('storage', refresh);
      return () => window.removeEventListener('storage', refresh);
    }, []);
    

    const chatSpaces = spaces.filter(s => s.type === 'chat');
    const noteSpaces = spaces.filter(s => s.type === 'notes');
    const studySpaces = spaces.filter(space =>
      ['studyguide', 'quiz', 'flashcards', 'openended'].includes(space.type)
    );
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
              {chats.map(chat => (
                <button
                  key={chat.id}
                  onClick={() => navigate(`/chat/${chat.id}`)}
                  className={`flex items-center gap-2 px-2 py-1 text-sm rounded hover:bg-gray-700 text-white ${
                    location.pathname.includes(chat.id) ? 'bg-gray-700' : ''
                  }`}
                >
                  <ChatsIcon className="w-4 h-4 text-white" />
                  <EditableTitle
                    value={chat.title}
                    onSave={(newTitle) => {
                      const updated = chats.map(c => c.id === chat.id ? { ...c, title: newTitle } : c);
                      setChats(updated);
                      localStorage.setItem(CHAT_LIST_KEY, JSON.stringify(updated));
                    }}
                  />
                </button>
              ))}
            </div>
          )}

          {!isCollapsed && activeTab === 'Notes' && (
            <div className="mt-2 ml-2 flex flex-col gap-1">
              <div className="flex justify-between items-center mb-1">
                <h2 className="text-sm font-semibold text-white">Notes</h2>
                <button
                  className="p-1 rounded-lg text-white hover:bg-gray-700"
                  onClick={async () => {
                    try {
                      const newNote = await createSpace({
                        type: 'notes',
                        title: `New Note ${noteSpaces.length + 1}`,
                        folderId: 'mock-folder',
                        settings: {},
                      });

                      console.log('Created new note space:', newNote);

                      const existingList = JSON.parse(localStorage.getItem(CHAT_LIST_KEY) || '[]');

                      const updatedList = [
                        ...existingList,
                        {
                          id: newNote.id,
                          title: newNote.title,
                          type: 'notes',
                          settings: newNote.settings || {},
                        }
                      ];

                      localStorage.setItem(CHAT_LIST_KEY, JSON.stringify(updatedList));

                      // Trigger sidebar reload
                      window.dispatchEvent(new CustomEvent('spaces-added'));

                      // Optional: directly update sidebar state too
                      setSpaces(prev => [...prev, newNote]);

                      // Navigate to new note
                      navigate(`/notes/${newNote.id}`);
                    } catch (err) {
                      console.error('Failed to create note:', err);
                    }
                  }}
                >
                  <PlusIcon className="w-4 h-4" />
                </button>
              </div>

              {noteSpaces.map(note => (
                <div
                  key={note.id}
                  onClick={() => navigate(`/notes/${note.id}`)}
                  tabIndex={0}
                  className="flex items-center gap-2 px-2 py-1 text-sm rounded hover:bg-gray-700 text-white cursor-pointer"
                >
                  <NotesIcon className="w-4 h-4 text-white" />
                  <EditableTitle
                    value={note.title}
                    onSave={(newTitle) => {
                      const updated = spaces.map(s => s.id === note.id ? { ...s, title: newTitle } : s);
                      setSpaces(updated);
                    
                      const existingList = JSON.parse(localStorage.getItem(CHAT_LIST_KEY) || '[]');
                      const updatedList = existingList.map((entry: any) =>
                        entry.id === note.id ? { ...entry, title: newTitle } : entry
                      );
                      localStorage.setItem(CHAT_LIST_KEY, JSON.stringify(updatedList));
                    }}
                  />
                </div>
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
                  <EditableTitle
                    value={item.title}
                    onSave={(newTitle) => {
                      const updated = spaces.map(s => s.id === item.id ? { ...s, title: newTitle } : s);
                      setSpaces(updated);

                      const existing = JSON.parse(localStorage.getItem(CHAT_LIST_KEY) || '[]');
                      const updatedList = existing.map((entry: any) =>
                        entry.id === item.id ? { ...entry, title: newTitle } : entry
                      );
                      localStorage.setItem(CHAT_LIST_KEY, JSON.stringify(updatedList));
                    }}
                  />
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
