import React from 'react';

interface Props {
  title: string;
  isOpen: boolean;
  toggle: () => void;
  children: React.ReactNode;
}

export default function CollapsibleSection({ title, isOpen, toggle, children }: Props) {
  return (
    <div>
      <div className="flex items-center justify-between text-xs text-gray-400 mt-6 mb-2 cursor-pointer" onClick={toggle}>
        <span>{title}</span>
        <svg className={`w-4 h-4 transition-transform ${isOpen ? 'rotate-180' : ''}`} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
          <path strokeLinecap="round" strokeLinejoin="round" d="M19 9l-7 7-7-7" />
        </svg>
      </div>
      <div className={`transition-all duration-300 overflow-hidden ${isOpen ? 'max-h-[500px] opacity-100' : 'max-h-0 opacity-0'} space-y-2`}>
        {children}
      </div>
    </div>
  );
}
