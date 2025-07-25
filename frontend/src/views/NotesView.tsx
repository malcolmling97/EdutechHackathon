import React, { useEffect, useState } from 'react';
import debounce from 'lodash.debounce';
import { getNoteBySpaceId } from '../utils/getNotes';
import { saveNote } from '../utils/saveNotes';
import { useParams } from 'react-router-dom';
import { ChatMessage } from '../components/common/Types';
import ChatInput from '../components/chat/ChatInput';
import ChatWindow from '../components/chat/ChatWindow';
import { SidebarToggleIcon } from '../components/common/Icons';

const NotesView = () => {
  const { spaceId = 'mock-space-id' } = useParams(); // mock spaceId
  const [noteId, setNoteId] = useState('');
  const [content, setContent] = useState('');
  const [loading, setLoading] = useState(true);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [collapsed, setCollapsed] = useState(false);

  useEffect(() => {
    if (!spaceId) return;

    getNoteBySpaceId(spaceId)
      .then((note) => {
        setNoteId(note.id);
        setContent(note.content);
      })
      .catch(console.error)
      .finally(() => setLoading(false));
  }, [spaceId]);

  const debouncedSave = debounce((text: string) => {
    if (noteId) saveNote(noteId, text).catch(console.error);
  }, 1000);

  const handleChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    const newText = e.target.value;
    setContent(newText);
    debouncedSave(newText);
  };

  const handleSend = (content: string, file?: File | null) => {
    const newMsg: ChatMessage = {
      id: `${Date.now()}`,
      spaceId,
      role: 'user',
      content,
      createdAt: new Date().toISOString(),
    };
    setMessages((prev) => [...prev, newMsg]);

    const mockResponse: ChatMessage = {
      id: `${Date.now()}-ai`,
      spaceId,
      role: 'assistant',
      content: `Got it! Here's a mock reply to: "${content}"`,
      createdAt: new Date().toISOString(),
    };

    setTimeout(() => {
      setMessages((prev) => [...prev, mockResponse]);
    }, 1000);
  };

  return (
    <div className="flex h-full">
      <div className="flex-1 p-4 overflow-auto">
        <h2 className="text-xl font-semibold mb-4">AI-Generated Notes</h2>
        {loading ? (
          <p className="text-gray-400">Loading note...</p>
        ) : (
          <textarea
            className="w-full h-[80vh] p-4 border rounded resize-none text-sm font-mono
              bg-white text-black dark:bg-neutral-900 dark:text-white dark:border-neutral-700"
            value={content}
            onChange={handleChange}
          />
        )}
        <p className="text-xs text-gray-500 mt-2">Auto-saving...</p>
      </div>

      <div className={`transition-all duration-300 h-full flex flex-col bg-[#1e1e1e] ${collapsed ? 'w-14' : 'w-[350px]'}`}>
        {/* Toggle Button */}
        <div className="flex justify-start p-2">
            <button
            onClick={() => setCollapsed(prev => !prev)}
            className="text-gray-400 hover:text-white"
            title={collapsed ? 'Expand Assistant' : 'Collapse Assistant'}
            >
            <SidebarToggleIcon isCollapsed={!collapsed} className="w-4 h-4" />
            </button>
        </div>

        {/* Chat content */}
        {!collapsed && (
            <>
            <div className="flex-1 overflow-auto px-2 py-2">
                <ChatWindow messages={messages} />
            </div>
            <div className="p-2 border-t border-[#2a2a2a]">
                <ChatInput onSend={handleSend} />
            </div>
            </>
        )}
        </div>

    </div>
  );
};

export default NotesView;
