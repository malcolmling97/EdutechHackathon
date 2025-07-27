import React, { useEffect, useState, useCallback, useRef } from 'react';
import debounce from 'lodash.debounce';
import { getNoteBySpaceId } from '../utils/getNotes';
import { saveNote } from '../utils/saveNotes';
import { useParams } from 'react-router-dom';
import { ChatMessage } from '../components/common/Types';
import NoteChatInput from '../components/chat/NoteChatInput';
import ChatWindow from '../components/chat/ChatWindow';
import { ChevronDoubleLeftIcon, ChevronDoubleRightIcon } from '../components/common/Icons';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

const NotesView = () => {
  const { spaceId = 'mock-space-id' } = useParams(); // mock spaceId
  const [noteId, setNoteId] = useState('');
  const [content, setContent] = useState('');
  const [loading, setLoading] = useState(true);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [collapsed, setCollapsed] = useState(false);
  const [isEditing, setIsEditing] = useState(false);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const token = localStorage.getItem('token') || '';
  const userId = localStorage.getItem('userId') || '';

  useEffect(() => {
    if (!spaceId) return;

    getNoteBySpaceId(spaceId, token, userId)
      .then((note) => {
        setNoteId(note.id);
        setContent(note.content || '# Welcome to your notes!\n\nClick anywhere to start editing!\n\n- **Bold text**\n- *Italic text*\n- `code snippets`\n\n> Blockquotes work too!\n\nType more content here...');
      })
      .catch(console.error)
      .finally(() => setLoading(false));
  }, [spaceId]);

  const debouncedSave = useCallback(
    debounce((text: string) => {
      if (noteId) saveNote(noteId, text, token, userId).catch(console.error);
    }, 1000),
    [noteId, token, userId]
  );

  const handleChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    const newText = e.target.value;
    setContent(newText);
    debouncedSave(newText);
  };

  const handlePreviewClick = () => {
    setIsEditing(true);
    setTimeout(() => {
      if (textareaRef.current) {
        textareaRef.current.focus();
        textareaRef.current.setSelectionRange(textareaRef.current.value.length, textareaRef.current.value.length);
      }
    }, 0);
  };

  const handleTextareaBlur = () => {
    // Add a small delay to allow for clicking on the preview
    setTimeout(() => {
      setIsEditing(false);
    }, 100);
  };

  const handleSend = (content: string) => {
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
    <div className="flex h-full bg-neutral-900 text-white">
      <div className="flex-1 overflow-y-auto custom-scrollbar">
        <div className="max-w-4xl mx-auto px-5 py-12 h-full">
            {loading ? (
            <p className="text-gray-400">Loading note...</p>
            ) : (
            <div className="w-full h-full">
              {isEditing ? (
                <textarea
                  ref={textareaRef}
                  className="w-full h-full p-4 border-none rounded resize-none text-base font-sans
                    bg-neutral-900 text-white focus:outline-none leading-relaxed custom-scrollbar"
                  value={content}
                  onChange={handleChange}
                  onBlur={handleTextareaBlur}
                  placeholder="Start typing markdown..."
                />
              ) : (
                <div
                  className="w-full h-full p-4 cursor-text prose prose-invert max-w-none rounded"
                  onClick={handlePreviewClick}
                >
                  <ReactMarkdown
                    remarkPlugins={[remarkGfm]}
                    components={{
                      h1: ({ children }) => <h1 className="text-3xl font-bold mb-4 mt-6 text-white">{children}</h1>,
                      h2: ({ children }) => <h2 className="text-2xl font-semibold mb-3 mt-5 text-white">{children}</h2>,
                      h3: ({ children }) => <h3 className="text-xl font-medium mb-2 mt-4 text-white">{children}</h3>,
                      p: ({ children }) => <p className="mb-4 text-gray-200 leading-relaxed">{children}</p>,
                      strong: ({ children }) => <strong className="font-semibold text-white">{children}</strong>,
                      em: ({ children }) => <em className="italic text-gray-300">{children}</em>,
                      code: ({ children }) => (
                        <code className="bg-gray-800 text-yellow-400 px-2 py-1 rounded text-sm font-mono">
                          {children}
                        </code>
                      ),
                      pre: ({ children }) => (
                        <pre className="bg-gray-800 p-4 rounded-lg overflow-x-auto my-4 border border-gray-700">
                          {children}
                        </pre>
                      ),
                      blockquote: ({ children }) => (
                        <blockquote className="border-l-4 border-blue-500 pl-4 my-4 italic text-gray-300">
                          {children}
                        </blockquote>
                      ),
                      ul: ({ children }) => <ul className="list-disc pl-6 mb-4 space-y-1">{children}</ul>,
                      ol: ({ children }) => <ol className="list-decimal pl-6 mb-4 space-y-1">{children}</ol>,
                      li: ({ children }) => <li className="text-gray-200">{children}</li>,
                      a: ({ children, href }) => (
                        <a href={href} className="text-blue-400 hover:text-blue-300 underline">
                          {children}
                        </a>
                      ),
                    }}
                  >
                    {content || 'Click here to start writing...'}
                  </ReactMarkdown>
                </div>
              )}
            </div>
            )}
        </div>
      </div>

      <div className={`transition-all duration-300 h-full flex flex-col bg-[#1e1e1e] ${collapsed ? 'w-14' : 'w-[350px]'}`}>
        {/* Toggle Button */}
        <div className="flex justify-start p-2 items-center h-[52px]">
            <button
            onClick={() => setCollapsed(prev => !prev)}
            className="text-gray-400 hover:text-white ml-2"
            title={collapsed ? 'Expand Assistant' : 'Collapse Assistant'}
            >
            {collapsed ? <ChevronDoubleLeftIcon className="w-4 h-4" /> : <ChevronDoubleRightIcon className="w-4 h-4" />}
            </button>
        </div>

        {/* Chat content */}
        {!collapsed && (
            <>
            <div className="flex-1 overflow-auto px-2 py-2 custom-scrollbar">
                <ChatWindow messages={messages} />
            </div>
            <div className="p-2 border-t border-[#2a2a2a]">
                <NoteChatInput onSend={handleSend} />
            </div>
            </>
        )}
        </div>
    </div>
  );
};

export default NotesView;
