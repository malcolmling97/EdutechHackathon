import React, { type FC } from 'react';

// --- Icon Asset URLs from Figma ---
// Note: In a production app, these would ideally be local SVG files
// rather than URLs pointing to the MCP server.

const ICON_URLS = {
  USER_SPACE: "http://localhost:3845/assets/c46b80190744100cd2172aaa1f178d3a10c88b7f.svg",
  RESOURCES: "http://localhost:3845/assets/610d3add3f6c7414ed9bb069db53fa2a963a34d0.svg",
  CHATS: "http://localhost:3845/assets/2a21a476570fbc39526a54d745b6f1faa285036d.svg",
  SETTINGS: "http://localhost:3845/assets/fa49767301306a0ff1fcb81653dbc9db641452b2.svg",
  NOTES: "http://localhost:3845/assets/6a66fa78ac4f151b9c1494be2cd13eb3787198e4.svg",
  STUDY: "http://localhost:3845/assets/42151ed73fb2769eb094efaf0bad74db201a4fb0.svg",
  SIDEBAR_TOGGLE: "http://localhost:3845/assets/9921c1efe94f0339398260540860951f35bfd07e.svg",
  MAIN_DROP_ICON: "http://localhost:3845/assets/5215cb0f0acfabe7caf3842907bca68878fcea7b.svg",
  VOICE_ICON: "http://localhost:3845/assets/b470bfcca83170816d69895f1b0ea006f6bca430.svg",
  CHAT_ATTACH: "http://localhost:3845/assets/5f69ca7237270a6c0750e5e855d83502bc0d3c14.svg",
};

// --- Reusable Icon Components ---

const BaseIcon: FC<{ src: string, alt: string, className?: string }> = ({ src, alt, className = "w-5 h-5" }) => (
    <img src={src} alt={alt} className={className} />
);

export const UserSpaceIcon: FC<{className?: string}> = ({className}) => <BaseIcon src={ICON_URLS.USER_SPACE} alt="User Space" className={className}/>;
export const ResourcesIcon: FC<{className?: string}> = ({className}) => <BaseIcon src={ICON_URLS.RESOURCES} alt="Resources" className={className}/>;
export const ChatsIcon: FC<{className?: string}> = ({className}) => <BaseIcon src={ICON_URLS.CHATS} alt="Chats" className={className}/>;
export const SettingsIcon: FC<{className?: string}> = ({className}) => <BaseIcon src={ICON_URLS.SETTINGS} alt="Settings" className={className}/>;
export const NotesIcon: FC<{className?: string}> = ({className}) => <BaseIcon src={ICON_URLS.NOTES} alt="Notes" className={className}/>;
export const StudyIcon: FC<{className?: string}> = ({className}) => <BaseIcon src={ICON_URLS.STUDY} alt="Study" className={className}/>;
export const SidebarToggleIcon: FC<{className?: string}> = ({className}) => <BaseIcon src={ICON_URLS.SIDEBAR_TOGGLE} alt="Toggle Sidebar" className={className}/>;
export const MainDropIcon: FC<{className?: string}> = ({className}) => <BaseIcon src={ICON_URLS.MAIN_DROP_ICON} alt="Upload material" className={className} />;
export const VoiceIcon: FC<{className?: string}> = ({className}) => <BaseIcon src={ICON_URLS.VOICE_ICON} alt="Voice Input" className={className} />;
export const ChatAttachIcon: FC<{className?: string}> = ({className}) => <BaseIcon src={ICON_URLS.CHAT_ATTACH} alt="Attach" className={className} />; 