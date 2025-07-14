import React, { useEffect, useMemo, useRef, useState } from 'react';
import CollapsibleSection from './components/CollapsibleSection';
import MessageBubble from './components/MessageBubble';
import type { Chat, Project, Quiz } from './types';
import { generateNewChatId } from './utils';
import { Moon, Sun, UserCircle, FileText, ListChecks, Send, FilePlus, Trash2 } from 'lucide-react';

const defaultChat: Chat = {
  id: 1,
  title: 'New Chat',
  messages: [{ sender: 'ai', text: 'Hello! How can I help you today?' }],
};

export default function App() {
  const [chats, setChats] = useState<Chat[]>([defaultChat]);
  const [activeChatId, setActiveChatId] = useState<number>(1);
  const [input, setInput] = useState('');
  const [searchTerm, setSearchTerm] = useState('');
  const [theme, setTheme] = useState<'light' | 'dark'>(
    window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'
  );
  const [chatsOpen, setChatsOpen] = useState(true);
  const [projectsOpen, setProjectsOpen] = useState(false);
  const [quizzesOpen, setQuizzesOpen] = useState(false);
  const [projects, setProjects] = useState<Project[]>([]);
  const [quizzes, setQuizzes] = useState<Quiz[]>([]);
  const [selectedProject, setSelectedProject] = useState<Project | null>(null);
  const [selectedQuiz, setSelectedQuiz] = useState<Quiz | null>(null);

  const messagesEndRef = useRef<HTMLDivElement>(null);
  const activeChat = useMemo(() => chats.find((c) => c.id === activeChatId)!, [chats, activeChatId]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [activeChat.messages]);

  useEffect(() => {
    document.documentElement.classList.toggle('dark', theme === 'dark');
    localStorage.setItem('theme', theme);
  }, [theme]);

  const handleSend = () => {
    const trimmed = input.trim();
    if (!trimmed) return;
    setChats((prevChats) =>
      prevChats.map((chat) =>
        chat.id === activeChatId
          ? {
              ...chat,
              messages: [
                ...chat.messages,
                { sender: 'user', text: trimmed },
                { sender: 'ai', text: "I'm an AI. This is a static response." },
              ],
            }
          : chat
      )
    );
    setInput('');
  };

  const handleNewChat = () => {
    const newId = generateNewChatId(chats);
    const newChat: Chat = {
      id: newId,
      title: `Chat ${newId}`,
      messages: [], // start empty!
    };
    setChats([newChat, ...chats]);
    setActiveChatId(newId);
    setSelectedProject(null);
    setSelectedQuiz(null);
  };

  const handleSummarise = () => {
    const summary = activeChat.messages
      .map((m) => `${m.sender === 'ai' ? 'AI' : 'User'}: ${m.text}`)
      .join('\n');
    const title = `Project ${projects.length + 1}`;
    setProjects((prev) => [{ title, summary }, ...prev]);
    setProjectsOpen(true);
  };

  const handleCreateQuiz = () => {
    const questions = [0, 1, 2].map((i) => ({
      q: `Sample Question ${i + 1} based on chat`,
      a: `Sample Answer ${i + 1}`,
    }));
    const title = `Quiz ${quizzes.length + 1}`;
    setQuizzes((prev) => [{ title, questions }, ...prev]);
    setQuizzesOpen(true);
  };

  const isFreshChat = activeChat.messages.length === 0 || activeChat.messages.every(m => m.sender === 'ai');

  const handleDeleteChat = (id: number) => {
    setChats(chats.filter(chat => chat.id !== id));
    if (activeChatId === id) {
      // If the deleted chat was active, switch to another chat or reset
      if (chats.length > 1) {
        const nextChat = chats.find(chat => chat.id !== id);
        if (nextChat) setActiveChatId(nextChat.id);
      }
    }
  };

  const handleDeleteProject = (title: string) => {
    setProjects(projects.filter(project => project.title !== title));
    if (selectedProject && selectedProject.title === title) setSelectedProject(null);
  };

  const handleDeleteQuiz = (title: string) => {
    setQuizzes(quizzes.filter(quiz => quiz.title !== title));
    if (selectedQuiz && selectedQuiz.title === title) setSelectedQuiz(null);
  };

  return (
    <div className={`flex h-screen ${theme} bg-gray-100 dark:bg-[#23272f]`}>
      {/* Sidebar */}
      <aside className="w-64 p-4 bg-white dark:bg-gray-900 text-gray-900 dark:text-white flex flex-col border-r border-gray-200 dark:border-gray-800 overflow-y-auto">
        <button onClick={handleNewChat} className="mb-4 p-2 rounded bg-blue-500 text-white">New Chat</button>

        <CollapsibleSection title="Chats" isOpen={chatsOpen} toggle={() => setChatsOpen(!chatsOpen)}>
          <input
            type="text"
            placeholder="Search chats..."
            className="w-full px-3 py-2 text-sm rounded-md bg-gray-100 dark:bg-gray-800"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
          {chats
            .filter((chat) => chat.title.toLowerCase().includes(searchTerm.toLowerCase()))
            .map((chat) => (
              <div
                key={chat.id}
                className={`group p-2 rounded flex items-center justify-between cursor-pointer ${
                  chat.id === activeChatId ? 'bg-gray-300 dark:bg-gray-700' : 'hover:bg-gray-200'
                }`}
                onClick={() => {
                  setActiveChatId(chat.id);
                  setSelectedProject(null);
                  setSelectedQuiz(null);
                }}
              >
                <span className="truncate flex-1">{chat.title}</span>
                <button
                  className="ml-2 opacity-0 group-hover:opacity-100 transition-opacity p-1 rounded hover:bg-red-100 dark:hover:bg-red-900"
                  title="Delete Chat"
                  onClick={e => { e.stopPropagation(); handleDeleteChat(chat.id); }}
                >
                  <Trash2 className="w-4 h-4 text-red-500" />
                </button>
              </div>
            ))}
        </CollapsibleSection>

        <CollapsibleSection title="Projects" isOpen={projectsOpen} toggle={() => setProjectsOpen(!projectsOpen)}>
          {projects.length === 0 ? (
            <div className="text-xs italic">No projects yet.</div>
          ) : (
            projects.map((proj, idx) => (
              <div
                key={idx}
                className="group p-2 rounded flex items-center justify-between cursor-pointer hover:bg-gray-200"
                onClick={() => { setSelectedProject(proj); setSelectedQuiz(null); }}
              >
                <span className="truncate flex-1">{proj.title}</span>
                <button
                  className="ml-2 opacity-0 group-hover:opacity-100 transition-opacity p-1 rounded hover:bg-red-100 dark:hover:bg-red-900"
                  title="Delete Project"
                  onClick={e => { e.stopPropagation(); handleDeleteProject(proj.title); }}
                >
                  <Trash2 className="w-4 h-4 text-red-500" />
                </button>
              </div>
            ))
          )}
        </CollapsibleSection>

        <CollapsibleSection title="Quizzes" isOpen={quizzesOpen} toggle={() => setQuizzesOpen(!quizzesOpen)}>
          {quizzes.length === 0 ? (
            <div className="text-xs italic">No quizzes yet.</div>
          ) : (
            quizzes.map((quiz, idx) => (
              <div
                key={idx}
                className="group p-2 rounded flex items-center justify-between cursor-pointer hover:bg-gray-200"
                onClick={() => { setSelectedQuiz(quiz); setSelectedProject(null); }}
              >
                <span className="truncate flex-1">{quiz.title}</span>
                <button
                  className="ml-2 opacity-0 group-hover:opacity-100 transition-opacity p-1 rounded hover:bg-red-100 dark:hover:bg-red-900"
                  title="Delete Quiz"
                  onClick={e => { e.stopPropagation(); handleDeleteQuiz(quiz.title); }}
                >
                  <Trash2 className="w-4 h-4 text-red-500" />
                </button>
              </div>
            ))
          )}
        </CollapsibleSection>
      </aside>

      {/* Main Chat Area */}
      <main className="flex-1 flex flex-col">
      <header className="p-4 border-b border-gray-300 flex justify-end items-center gap-4">
        <button
          onClick={() => setTheme(theme === 'dark' ? 'light' : 'dark')}
          title="Toggle Theme"
          className="p-2 rounded hover:bg-gray-200 dark:hover:bg-gray-700 transition"
        >
          {theme === 'dark' ? <Sun className="w-5 h-5 text-yellow-400" /> : <Moon className="w-5 h-5 text-gray-600" />}
        </button>
        <button
          title="Profile"
          className="p-2 rounded-full hover:bg-gray-200 dark:hover:bg-gray-700 transition"
        >
          <UserCircle className="w-6 h-6 text-gray-600 dark:text-gray-300" />
        </button>
      </header>
        <section className="flex-1 overflow-y-auto p-4">
          {selectedProject ? (
            <main className="flex-1 flex flex-col items-center justify-center p-8">
              <div className="max-w-2xl w-full bg-gray-50 dark:bg-[#23272f] rounded-xl shadow p-8">
                <div className="flex items-center gap-3 mb-4">
                  <FileText className="w-7 h-7 text-blue-600 dark:text-blue-400" />
                  <h2 className="text-2xl font-bold text-gray-900 dark:text-white">{selectedProject.title}</h2>
                </div>
                <pre className="whitespace-pre-wrap text-gray-800 dark:text-gray-200 text-base bg-gray-100 dark:bg-[#23272f] rounded p-4">{selectedProject.summary}</pre>
              </div>
            </main>
          ) : selectedQuiz ? (
            <main className="flex-1 flex flex-col items-center justify-center p-8">
              <div className="max-w-2xl w-full bg-gray-50 dark:bg-[#23272f] rounded-xl shadow p-8">
                <div className="flex items-center gap-3 mb-4">
                  <ListChecks className="w-7 h-7 text-green-600 dark:text-green-400" />
                  <h2 className="text-2xl font-bold text-gray-900 dark:text-white">{selectedQuiz.title}</h2>
                </div>
                <div className="space-y-6">
                  {selectedQuiz.questions.map((qa, i) => (
                    <div key={i} className="bg-gray-100 dark:bg-[#23272f] rounded p-4">
                      <div className="font-semibold text-gray-800 dark:text-gray-100 mb-1">Q{i + 1}: {qa.q}</div>
                      <div className="pl-4 text-gray-700 dark:text-gray-300">A: {qa.a}</div>
                    </div>
                  ))}
                </div>
              </div>
            </main>
          ) : isFreshChat ? (
            <div className="flex flex-1 min-h-0 h-full items-center justify-center bg-white dark:bg-[#23272f]">
              <div className="flex flex-col items-center w-full max-w-2xl">
                <h1 className="text-3xl md:text-4xl font-bold text-gray-900 dark:text-white mb-8 text-center">
                  Ready when you are.
                </h1>
                <div className="w-full flex flex-col items-center">
                  <div className="w-full max-w-2xl bg-gray-100 dark:bg-[#23272f] rounded-2xl shadow-lg flex items-center px-6 py-4 mb-2 border border-gray-300 dark:border-gray-700">
                    <button
                      title="Upload PDF"
                      className="p-2 rounded-lg hover:bg-gray-200 dark:hover:bg-gray-700 transition"
                      onClick={() => document.getElementById('pdf-upload')?.click()}
                    >
                      <FilePlus className="w-5 h-5 text-gray-600 dark:text-gray-300" />
                    </button>
                    <input
                      id="pdf-upload"
                      type="file"
                      accept="application/pdf"
                      className="hidden"
                      onChange={(e) => {
                        const file = e.target.files?.[0];
                        if (file) {
                          console.log('Selected PDF:', file.name);
                          // You can send it to your backend / parse it here
                        }
                      }}
                    />
                    <input
                      className="flex-1 bg-transparent outline-none text-gray-900 dark:text-white placeholder-gray-400 text-lg"
                      type="text"
                      placeholder="Ask anything"
                      value={input}
                      onChange={(e) => setInput(e.target.value)}
                      onKeyDown={(e) => e.key === 'Enter' && handleSend()}
                    />
                    <button
                      onClick={handleSend}
                      title="Send"
                      className="p-2 rounded-full bg-blue-600 hover:bg-blue-700 text-white transition"
                    >
                      <Send className="w-4 h-4" />
                    </button>
                  </div>
                </div>
              </div>
            </div>
          ) : (
            <div className="space-y-4">
              {activeChat.messages.map((msg, idx) => (
                <MessageBubble key={idx} {...msg} />
              ))}
              <div ref={messagesEndRef} />
            </div>
          )}
        </section>

        {!isFreshChat && !selectedProject && !selectedQuiz && (
          <footer className="p-4 border-t border-gray-300 flex gap-2 items-center">
            <button
              title="Upload PDF"
              className="p-2 rounded-lg hover:bg-gray-200 dark:hover:bg-gray-700 transition"
              onClick={() => document.getElementById('pdf-upload')?.click()}
            >
              <FilePlus className="w-5 h-5 text-gray-600 dark:text-gray-300" />
            </button>
            <input
              id="pdf-upload"
              type="file"
              accept="application/pdf"
              className="hidden"
              onChange={(e) => {
                const file = e.target.files?.[0];
                if (file) {
                  console.log('Selected PDF:', file.name);
                  // You can send it to your backend / parse it here
                }
              }}
            />
            <input
              className="flex-1 p-2 rounded border"
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleSend()}
              placeholder="Type your message..."
            />
            <button
              onClick={handleSummarise}
              title="Summarize"
              className="p-2 rounded-lg hover:bg-gray-200 dark:hover:bg-gray-700 transition"
            >
              <FileText className="w-5 h-5 text-gray-600 dark:text-gray-300" />
            </button>
            <button
              onClick={handleCreateQuiz}
              title="Make a Quiz"
              className="p-2 rounded-lg hover:bg-gray-200 dark:hover:bg-gray-700 transition"
            >
              <ListChecks className="w-5 h-5 text-gray-600 dark:text-gray-300" />
            </button>
            <button
              onClick={handleSend}
              title="Send"
              className="p-2 rounded-full bg-blue-600 hover:bg-blue-700 text-white transition"
            >
              <Send className="w-4 h-4" />
            </button>
          </footer>
        )}
      </main>
    </div>
  );
}
