import React, { useEffect, useState } from 'react';
import ReactDOM from 'react-dom';

interface DropZoneWrapperProps {
  onFileDrop: (file: File) => void;
  children: React.ReactNode;
}

const DropZoneWrapper: React.FC<DropZoneWrapperProps> = ({ onFileDrop, children }) => {
  const [isDragging, setIsDragging] = useState(false);

  useEffect(() => {
    const handleDragOver = (e: DragEvent) => {
      e.preventDefault();
      if (e.dataTransfer?.types.includes('Files')) {
        setIsDragging(true);
      }
    };

    const handleDrop = (e: DragEvent) => {
      e.preventDefault();
      setIsDragging(false);

      const file = e.dataTransfer?.files?.[0];
      if (file && file.type === 'application/pdf') {
        onFileDrop(file);
      }
    };

    const handleDragLeave = () => {
      setIsDragging(false);
    };

    document.addEventListener('dragover', handleDragOver);
    document.addEventListener('drop', handleDrop);
    document.addEventListener('dragleave', handleDragLeave);

    return () => {
      document.removeEventListener('dragover', handleDragOver);
      document.removeEventListener('drop', handleDrop);
      document.removeEventListener('dragleave', handleDragLeave);
    };
  }, [onFileDrop]);

  return (
    <>
      {children}

      {isDragging &&
        ReactDOM.createPortal(
          <div className="fixed inset-0 bg-black bg-opacity-40 z-50 flex items-center justify-center pointer-events-none">
            <div className="bg-white text-black px-4 py-2 rounded shadow-lg text-lg font-medium">
              Drop your PDF here
            </div>
          </div>,
          document.body
        )}
    </>
  );
};

export default DropZoneWrapper;
