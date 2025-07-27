import React from 'react';
import { VoiceIcon } from '../common/Icons';

interface NoteChatInputProps {
  onSend: (content: string) => void;
}

const NoteChatInput: React.FC<NoteChatInputProps> = ({ onSend }) => {
  const [input, setInput] = React.useState('');

  const sendMessage = () => {
    const trimmed = input.trim();
    if (!trimmed) return;

    onSend(trimmed);
    setInput('');
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  return (
    <div className="bg-brand-dark-2 rounded-2xl p-4 flex flex-col gap-2">
      <textarea
        value={input}
        onChange={e => setInput(e.target.value)}
        onKeyDown={handleKeyDown}
        placeholder="Ask anything"
        className="bg-transparent text-gray-300 resize-none p-2 text-sm"
      />

      <div className="flex justify-between items-center">
        <div className="flex gap-2">
          {/* Voice Icon */}
          <button className="p-2 hover:bg-gray-700 rounded transition">
            <VoiceIcon className="w-5 h-5 text-content-secondary" />
          </button>
        </div>

        {/* Send Button */}
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

export default NoteChatInput; 