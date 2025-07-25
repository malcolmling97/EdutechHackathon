import React, { useEffect, useRef } from 'react';
import type { ChatMessage } from '../common/Types';

const ChatWindow = ({ messages }: { messages: ChatMessage[] }) => {
  const bottomRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  return (
    <div className="flex-1 w-full overflow-y-auto px-2 space-y-4 custom-scrollbar">
      {messages.map((msg, idx) => (
        <div key={idx} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
          <div
            className={`
              max-w-[75%] px-4 py-3 text-sm whitespace-pre-line
              ${msg.role === 'user'
                ? 'bg-[#2e2e2e] text-white rounded-full self-end'
                : 'bg-brand-dark-1 text-gray-100 rounded-xl self-start'}
            `}
          >
            {msg.content}
          </div>
        </div>
      ))}
      <div ref={bottomRef} />
    </div>
  );
};

export default ChatWindow;
