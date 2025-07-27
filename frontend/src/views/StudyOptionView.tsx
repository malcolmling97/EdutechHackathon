import React from 'react';
import { useEffect, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { getSpaces } from '../utils/getSpaces';
import {
  StudyIcon,
  FlashcardIcon,
  OpenEndedIcon,
  QuizIcon,
} from '../components/common/Icons';
import { CreatedSpace } from '../components/common/Types';

const StudyOptionsView = () => {
  const { spaceId } = useParams();
  const navigate = useNavigate();
  const [availableTools, setAvailableTools] = useState<string[]>([]);

  useEffect(() => {

    if (!localStorage.getItem('token')) {
        localStorage.setItem('token', 'mock-token');
      }
      if (!localStorage.getItem('user-id')) {
        localStorage.setItem('user-id', 'mock-user');
      }

    const token = localStorage.getItem('token') || '';
    const userId = localStorage.getItem('user-id') || '';
  
    getSpaces(token, userId).then(spaces => {
      const space = spaces.find(s => s.id === spaceId);
      const tools = space?.settings?.generatedTypes || [];
      setAvailableTools(tools);
    });
  }, [spaceId]);

  const iconMap: Record<string, JSX.Element> = {
    studyguide: <StudyIcon className="w-6 h-6 text-white" />,
    flashcards: <FlashcardIcon className="w-6 h-6 text-white" />,
    openended: <OpenEndedIcon className="w-6 h-6 text-white" />,
    quiz: <QuizIcon className="w-6 h-6 text-white" />,
  };

  const labelMap: Record<string, string> = {
    studyguide: 'Study Guide',
    flashcards: 'Flashcards',
    openended: 'Comprehension',
    quiz: 'Quiz',
  };

  const subtitleMap: Record<string, string> = {
    studyguide: 'Structured outline for review',
    flashcards: 'Quick memory cards',
    openended: 'Open-ended understanding checks',
    quiz: 'Multiple choice and short questions',
  };

  return (
    <div className="min-h-screen p-8 text-white bg-primary">
      <h1 className="text-3xl font-semibold mb-8">What would you like to cover today?</h1>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
        {availableTools.map((type) => (
          <button
            key={type}
            onClick={() => navigate(`/study/${spaceId}/${type}`)}
            className="flex flex-col gap-3 items-start bg-secondary p-6 rounded-xl hover:bg-gray-700 transition-colors shadow"
          >
            <div className="flex items-center gap-4">
              {iconMap[type]}
              <span className="text-lg font-medium">{labelMap[type]}</span>
            </div>
            <p className="text-sm text-gray-400">{subtitleMap[type]}</p>
          </button>
        ))}
      </div>
    </div>
  );
};

export default StudyOptionsView;
