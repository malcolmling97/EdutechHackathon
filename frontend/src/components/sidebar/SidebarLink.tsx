import React from 'react';
import { Link } from 'react-router-dom';

interface SidebarLinkProps {
  text: string;
  icon: React.ComponentType<{ className?: string }>;
  isCollapsed: boolean;
  to?: string;                     // Optional route path
  isButton?: boolean;
  hasHover?: boolean;
  textClassName?: string;
  iconClassName?: string;
}

const SidebarLink: React.FC<SidebarLinkProps> = ({
  text,
  icon: Icon,
  isCollapsed,
  to,
  isButton = true,
  hasHover = true,
  textClassName = '',
  iconClassName = '',
}) => {
  const classes = `flex items-center gap-3 px-3 py-2.5 rounded-lg text-content-secondary transition-colors 
    ${isButton ? (hasHover ? 'hover:bg-gray-700 hover:text-white' : '') : 'cursor-default'} 
    ${isCollapsed ? 'justify-center' : ''}`;

  const content = (
    <>
      <Icon className={`w-5 h-5 flex-shrink-0 ${iconClassName}`} />
      {!isCollapsed && <span className={`truncate ${textClassName}`}>{text}</span>}
    </>
  );

  return to ? (
    <Link to={to} className={classes}>
      {content}
    </Link>
  ) : (
    <div className={`${classes} cursor-pointer`}>
      {content}
    </div>
  );
};

export default SidebarLink;