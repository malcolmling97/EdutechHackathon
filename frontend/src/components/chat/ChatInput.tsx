import React from 'react';
import { ChatAttachIcon, VoiceIcon, PDFIcon } from '../common/Icons';

interface ChatInputProps {
  onSend: (content: string, file?: File | null) => void;
  dispatchChatEvent?: boolean;
  spaceId?: string;
  selectedFile?: File | null;
  setSelectedFile?: (file: File | null) => void;
  clearSelectedFile?: () => void;
}

const ChatInput: React.FC<ChatInputProps> = ({
  onSend,
  dispatchChatEvent = false,
  spaceId,
  selectedFile,
  setSelectedFile,
  clearSelectedFile,
}) => {
  const [input, setInput] = React.useState('');
  const fileInputRef = React.useRef<HTMLInputElement>(null);

  const sendMessage = () => {
    const trimmed = input.trim();
    if (!trimmed && !selectedFile) return;

    onSend(trimmed, selectedFile);
    setInput('');
    clearSelectedFile?.();

    if (dispatchChatEvent && spaceId) {
      const event = new CustomEvent('add-chat', {
        detail: {
          id: spaceId,
          title: (trimmed || selectedFile?.name)?.slice(0, 30) || 'New Chat',
        },
      });
      window.dispatchEvent(event);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file && file.type === 'application/pdf') {
      setSelectedFile?.(file);
      e.target.value = '';
    }
  };

  return (
    <div className="bg-brand-dark-2 rounded-2xl p-4 flex flex-col gap-2">
      {selectedFile && (
        <div className="flex items-center gap-2 p-2 bg-gray-800 text-sm rounded text-white">
          <PDFIcon className="w-4 h-4 text-red-500" />
          {selectedFile.name}
          <button
            onClick={clearSelectedFile}
            className="ml-auto text-red-400 hover:text-red-600"
          >
            ✕
          </button>
        </div>
      )}

      <textarea
        value={input}
        onChange={e => setInput(e.target.value)}
        onKeyDown={handleKeyDown}
        placeholder="Ask anything"
        className="bg-transparent text-gray-300 resize-none p-2"
      />

      <div className="flex justify-between items-center">
        <div className="flex gap-2">
          <label className="cursor-pointer p-2 hover:bg-gray-700 rounded transition">
            <PDFIcon className="w-5 h-5 text-content-secondary" />
            <input
              type="file"
              accept="application/pdf"
              className="hidden"
              ref={fileInputRef}
              onChange={handleFileChange}
            />
          </label>

          <button className="p-2 hover:bg-gray-700 rounded transition">
            <ChatAttachIcon className="w-5 h-5 text-content-secondary" />
          </button>

          <button className="p-2 hover:bg-gray-700 rounded transition">
            <VoiceIcon className="w-5 h-5 text-content-secondary" />
          </button>
        </div>

        <button
          onClick={sendMessage}
          className="p-2 text-sm text-white bg-blue-600 rounded px-4 hover:bg-blue-700"
        >
          Send
        </button>
      </div>
    </div>
  );
};

export default ChatInput;
