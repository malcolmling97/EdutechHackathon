import React from 'react';
import { FaUserAlt, FaBookOpen, FaComments, FaCog, FaStickyNote, FaBrain, FaChevronLeft, FaChevronRight, FaUpload, FaMicrophone, FaPaperclip, FaFilePdf, FaRegListAlt, FaRegClone, FaQuestionCircle, FaRegEdit, FaBars, FaAngleDoubleLeft, FaPlus } from 'react-icons/fa';

export const UserSpaceIcon = ({ className = "w-5 h-5" }) => <FaUserAlt className={className} />;
export const ResourcesIcon = ({ className = "w-5 h-5" }) => <FaBookOpen className={className} />;
export const ChatsIcon = ({ className = "w-5 h-5" }) => <FaComments className={className} />;
export const SettingsIcon = ({ className = "w-5 h-5" }) => <FaCog className={className} />;
export const NotesIcon = ({ className = "w-5 h-5" }) => <FaStickyNote className={className} />;
export const StudyIcon = ({ className = "w-5 h-5" }) => <FaBrain className={className} />;
export const MainDropIcon = ({ className = "w-5 h-5" }) => <FaUpload className={className} />;
export const VoiceIcon = ({ className = "w-5 h-5" }) => <FaMicrophone className={className} />;
export const ChatAttachIcon = ({ className = "w-5 h-5" }) => <FaPaperclip className={className} />;
export const PDFIcon = ({ className = "w-5 h-5" }) => <FaFilePdf className={className} />;
export const QuizIcon   = ({ className = "w-5 h-5" }) => <FaQuestionCircle className={className} />;
export const FlashcardIcon  = ({ className = "w-5 h-5" }) => <FaRegClone className={className} />;
export const OpenEndedIcon  = ({ className = "w-5 h-5" }) => <FaRegEdit className={className} />;
export const StudiesIcon   = ({ className = "w-5 h-5" }) => <FaRegListAlt className={className} />;
export const ChevronRight   = ({ className = "w-5 h-5" }) => <FaChevronRight className={className} />;
export const ChevronLeft   = ({ className = "w-5 h-5" }) => <FaChevronLeft className={className} />;
export const PlusIcon = ({ className = "w-5 h-5" }) => <FaPlus className={className} />;

export const SidebarToggleIcon = ({ isCollapsed, className = "w-4 h-4" }: { isCollapsed: boolean; className?: string }) => {
  const Icon = isCollapsed ? FaBars : FaAngleDoubleLeft;
  return <Icon className={className} />;
};