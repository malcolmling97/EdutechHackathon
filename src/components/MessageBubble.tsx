import React from 'react';
import type { Message } from '../types';

export default function MessageBubble({ sender, text }: Message) {
  const isUser = sender === 'user';
  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'} w-full`}>
      <div
        className={`px-4 py-3 text-sm max-w-[80%] ${
          isUser
            ? 'bg-blue-600 dark:bg-blue-500 text-white rounded-xl'
            : 'text-gray-900 dark:text-white'
        }`}
      >
        {text}
      </div>
    </div>
  );
}
