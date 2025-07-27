import React, { useState } from 'react';

type Props = {
  value: string;
  onSave: (newValue: string) => void;
  className?: string;
};

const EditableTitle: React.FC<Props> = ({ value, onSave, className }) => {
  const [isEditing, setIsEditing] = useState(false);
  const [title, setTitle] = useState(value);

  return isEditing ? (
    <input
      autoFocus
      value={title}
      onChange={(e) => setTitle(e.target.value)}
      onBlur={() => {
        onSave(title);
        setIsEditing(false);
      }}
      onKeyDown={(e) => {
        if (e.key === 'Enter') (e.target as HTMLInputElement).blur();
      }}
      className={className || 'bg-gray-700 text-white px-1 py-0.5 rounded w-full'}
    />
  ) : (
    <span className="cursor-text text-white" onClick={(e) => { e.stopPropagation(); setIsEditing(true); }}>
      {value}
    </span>
  );
};

export default EditableTitle;
