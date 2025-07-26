import React, { useState } from 'react';
import { NotesIcon, StudiesIcon, FlashcardIcon, QuizIcon, OpenEndedIcon } from './Icons';
import { FaCheckCircle, FaRegCircle, FaTimes } from 'react-icons/fa';

interface GenerationModalProps {
  onGenerate: (selectedOptions: string[]) => void;
  onClose: () => void;
}

const GenerationModal: React.FC<GenerationModalProps> = ({ onGenerate, onClose }) => {
  const [selected, setSelected] = useState<string[]>([]);

  // Split options: Notes is standalone, rest are Study
  const notesOption = { name: 'Notes', icon: <NotesIcon />, description: "Summarize key points from your materials." };
  const studyOptions = [
    { name: 'Study Guide', icon: <StudiesIcon />, description: "Structured study outline" },
    { name: 'Flashcards', icon: <FlashcardIcon />, description: "Quick review cards" },
    { name: 'Quiz', icon: <QuizIcon />, description: "Short answer questions" },
    { name: 'Comprehenshion', icon: <OpenEndedIcon />, description: "Open-ended questions" },
  ];

  const toggleOption = (name: string) => {
    setSelected(prev =>
      prev.includes(name) ? prev.filter(item => item !== name) : [...prev, name]
    );
  };

  const handleGenerate = () => {
    if (selected.length > 0) {
      onGenerate(selected);
    }
  };

  return (
    <div className="fixed inset-0 flex items-center justify-center z-50 pointer-events-none">
      <div
        className="bg-secondary border border-border-primary rounded-3xl shadow-2xl p-8 max-w-5xl w-full flex flex-col relative pointer-events-auto"
        style={{ minWidth: 320, maxWidth: 900, height: 700 }}
      >
        {/* Close button */}
        <button
          onClick={onClose}
          className="absolute top-4 right-4 text-content-secondary hover:text-white text-2xl focus:outline-none"
          aria-label="Close"
        >
          <FaTimes />
        </button>
        {/* Notes (standalone) */}
        <div className="mb-6">
          <div className="text-content-secondary font-semibold mb-2 ml-1">Notes</div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
            <button
              key={notesOption.name}
              onClick={() => toggleOption(notesOption.name)}
              className={`relative flex flex-row items-center bg-brand-dark-2 hover:bg-brand-dark-3 border-2 transition-all duration-200 rounded-2xl px-5 py-6 w-full h-full text-left ${selected.includes(notesOption.name) ? 'border-blue-500' : 'border-border-primary'}`}
            >
              <div className="flex flex-row items-center flex-1 min-w-0">
                <div className="flex items-start w-8 h-8 mr-1 text-blue-500 flex-shrink-0 ml-0 pl-0">{notesOption.icon}</div>
                <div className="flex flex-col items-start justify-center min-w-0">
                  <span className="block text-base font-semibold text-white mb-0 truncate">Summarise Notes</span>
                  <span className="block text-xs text-content-secondary leading-snug truncate">Key points summary</span>
                </div>
              </div>
              <div className="flex items-center justify-center h-full ml-2">
                {selected.includes(notesOption.name) ? (
                  <FaCheckCircle className="text-blue-500 text-xl" />
                ) : (
                  <FaRegCircle className="text-content-secondary text-xl" />
                )}
              </div>
            </button>
          </div>
        </div>
        {/* Study group */}
        <div>
          <div className="text-content-secondary font-semibold mb-2 ml-1">Study</div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
            {studyOptions.map((option) => (
              <button
                key={option.name}
                onClick={() => toggleOption(option.name)}
                className={`relative flex flex-row items-center bg-brand-dark-2 hover:bg-brand-dark-3 border-2 transition-all duration-200 rounded-2xl px-5 py-6 w-full h-full text-left ${selected.includes(option.name) ? 'border-blue-500' : 'border-border-primary'}`}
              >
                <div className="flex flex-row items-center flex-1 min-w-0">
                  <div className="flex items-start w-8 h-8 mr-1 text-blue-500 flex-shrink-0 ml-0 pl-0">{option.icon}</div>
                  <div className="flex flex-col items-start justify-center min-w-0">
                    <span className="block text-base font-semibold text-white mb-0 truncate">{option.name}</span>
                    <span className="block text-xs text-content-secondary leading-snug truncate">{option.description}</span>
                  </div>
                </div>
                <div className="flex items-center justify-center h-full ml-2">
                  {selected.includes(option.name) ? (
                    <FaCheckCircle className="text-blue-500 text-xl" />
                  ) : (
                    <FaRegCircle className="text-content-secondary text-xl" />
                  )}
                </div>
              </button>
            ))}
          </div>
        </div>
        <button
          onClick={handleGenerate}
          disabled={selected.length === 0}
          className="mt-8 w-full bg-blue-600 text-white font-bold text-lg py-4 px-4 rounded-xl transition-colors disabled:bg-gray-700 disabled:text-gray-400 disabled:cursor-not-allowed"
        >
          Enter
        </button>
      </div>
    </div>
  );
};

export default GenerationModal; 