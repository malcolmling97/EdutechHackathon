import React, { useState, type FC } from 'react';
import {
    UserSpaceIcon,
    ResourcesIcon,
    ChatsIcon,
    NotesIcon,
    StudyIcon,
    SettingsIcon,
    MainDropIcon,
    VoiceIcon,
    ChatAttachIcon,
    SidebarToggleIcon,
} from '../components/common/Icons';


const SidebarLink: FC<{ text: string, icon: React.ComponentType<{className?: string}>, isCollapsed: boolean, isButton?: boolean, hasHover?: boolean }> = ({ text, icon: Icon, isCollapsed, isButton = true, hasHover = true }) => {
    const interactiveClasses = isButton ? `${hasHover ? 'hover:bg-gray-700 hover:text-white' : ''} cursor-pointer` : 'cursor-default';
    return (
        <a className={`flex items-center gap-3 px-3 py-2.5 rounded-lg text-content-secondary transition-colors ${interactiveClasses} ${isCollapsed ? 'justify-center' : ''}`}>
            <Icon className="w-5 h-5 flex-shrink-0" />
            {!isCollapsed && <span className="truncate">{text}</span>}
        </a>
    )
}

const Sidebar: FC<{isCollapsed: boolean, onToggle: () => void}> = ({ isCollapsed, onToggle }) => {
  return (
    <div className={`flex flex-col h-screen bg-secondary border-r border-border-primary text-white p-2 transition-all duration-300 ${isCollapsed ? 'w-20' : 'w-64'}`}>
      <div className="flex-grow">
        <div className={`flex items-center mb-2 h-[42px] ${isCollapsed ? 'justify-center' : 'justify-between'}`}>
            {!isCollapsed && <SidebarLink text="Malcolm's Space" icon={UserSpaceIcon} isCollapsed={isCollapsed} isButton={false} hasHover={false} />}
            <button onClick={onToggle} className="p-1 rounded-lg text-content-secondary mr-1 cursor-pointer">
                <SidebarToggleIcon className="w-4 h-4" />
            </button>
        </div>
        <hr className="border-t border-border-primary -mx-2" />
        <nav className="flex flex-col gap-2 mt-2">
          <SidebarLink text="Resources" icon={ResourcesIcon} isCollapsed={isCollapsed} />
          <SidebarLink text="Chats" icon={ChatsIcon} isCollapsed={isCollapsed} />
          <SidebarLink text="Notes" icon={NotesIcon} isCollapsed={isCollapsed} />
          <SidebarLink text="Study" icon={StudyIcon} isCollapsed={isCollapsed} />
        </nav>
        <hr className="border-t border-border-primary -mx-2 mt-2" />
      </div>
      <div className='flex-shrink-0'>
        <hr className="border-t border-border-primary -mx-2 mb-2" />
        <SidebarLink text="Settings" icon={SettingsIcon} isCollapsed={isCollapsed} hasHover={false}/>
      </div>
    </div>
  );
};

const ChatInput = () => {
    return (
        <div className="w-full bg-brand-dark-2 rounded-2xl p-4 flex flex-col gap-2">
            <textarea
                rows={1}
                placeholder="Ask anything"
                className="flex-grow bg-transparent text-gray-300 placeholder-gray-500 focus:outline-none resize-none p-2 max-h-24 overflow-y-auto custom-scrollbar"
                onInput={(e) => {
                    const target = e.target as HTMLTextAreaElement;
                    target.style.height = 'auto';
                    target.style.height = `${target.scrollHeight}px`;
                }}
            />
            <div className="flex justify-between items-center">
                <button className="p-2">
                    <ChatAttachIcon className="w-4 h-5 text-content-secondary" />
                </button>
                <button className="p-2">
                    <VoiceIcon className="w-4 h-5 text-content-secondary" />
                </button>
            </div>
        </div>
    )
}

const DashboardView = () => {
  const [isSidebarCollapsed, setSidebarCollapsed] = useState(false);

  const toggleSidebar = () => {
    setSidebarCollapsed(!isSidebarCollapsed);
  };

  return (
    <div className="flex h-screen bg-primary text-white">
      <Sidebar isCollapsed={isSidebarCollapsed} onToggle={toggleSidebar} />
      <main className="flex-1 flex flex-col items-center px-8 pt-8 pb-10">
        <div className="flex-grow" />
        <div className="text-center">
            <MainDropIcon className="h-28 w-24 mx-auto mb-6 text-gray-500"/>
            <h1 className="text-3xl font-medium text-white mb-8">
                Drag and drop your material, or start a chat!
            </h1>
        </div>
        <div className="flex-grow-[1]" />
        <div className="w-full max-w-3xl">
            <ChatInput />
        </div>
      </main>
    </div>
  );
};

export default DashboardView; 