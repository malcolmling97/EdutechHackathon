import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { generateQuiz } from '../utils/generateQuiz';
import {
  StudyIcon, FlashcardIcon, OpenEndedIcon, QuizIcon,
} from '../components/common/Icons'; // Replace as needed

const StudyView = () => {
  const navigate = useNavigate();
  const [showModal, setShowModal] = useState(false);

  const [formData, setFormData] = useState({
    spaceId: '',
    title: 'Auto Generated Quiz',
    fileIds: '',
    questionCount: 5,
    questionTypes: ['mcq'],
    difficulty: 'medium',
  });

  const token = localStorage.getItem('token') || '';
  const userId = localStorage.getItem('userId') || '';

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: name === 'questionCount' ? Number(value) : value,
    }));
  };

  const handleTypeToggle = (type: string) => {
    setFormData(prev => {
      const updated = prev.questionTypes.includes(type)
        ? prev.questionTypes.filter(t => t !== type)
        : [...prev.questionTypes, type];
      return { ...prev, questionTypes: updated };
    });
  };

  const handleSubmit = async () => {
    try {
      const quiz = await generateQuiz({
        ...formData,
        fileIds: formData.fileIds.split(',').map(s => s.trim()),
        questionTypes: formData.questionTypes as Array<'mcq' | 'tf' | 'short'>,
        difficulty: formData.difficulty as 'easy' | 'medium' | 'hard' | undefined,
        token,
        userId,
      });
      //navigate(`/quiz/${quiz.spaceId}/attempt`); Backend not functional
      navigate(`/quiz`);

    } catch (err: any) {
      alert(err.message);
    }
  };

  const cards = [
    {
      title: 'Study Guide',
      subtitle: 'Memorise key terms and concepts',
      icon: <StudyIcon className="w-6 h-6 text-white" />,
      to: '/study-guide/content',
    },
    {
      title: 'Flashcards',
      subtitle: 'Memorise key terms and concepts',
      icon: <FlashcardIcon className="w-6 h-6 text-white" />,
      to: '/flashcards',
    },
    {
      title: 'Open Ended',
      subtitle: 'Test your understanding',
      icon: <OpenEndedIcon className="w-6 h-6 text-white" />,
      to: '/open-ended',
    },
    {
      title: 'Practise Quiz',
      subtitle: 'Generate questions and test yourself',
      icon: <QuizIcon className="w-6 h-6 text-white" />,
      onClick: () => setShowModal(true),
    },
  ];

  return (
    <div className="flex h-screen bg-primary text-white items-center justify-center px-4">
      <div className="w-full max-w-4xl text-center">
        <h1 className="text-3xl font-semibold mb-12">
          What would you like to cover today?
        </h1>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
          {cards.map((card, idx) => (
            <button
              key={idx}
              onClick={() => card.to ? navigate(card.to) : card.onClick?.()}
              className="bg-secondary p-6 rounded-xl hover:bg-gray-700 transition-colors shadow text-left flex flex-col gap-3 items-start"
            >
              <div className="flex items-center gap-4">
                {card.icon}
                <span className="text-lg font-medium">{card.title}</span>
              </div>
              <p className="text-sm text-gray-400">{card.subtitle}</p>
            </button>
          ))}
        </div>
      </div>

      {/* Modal */}
      {showModal && (
        <div className="fixed inset-0 bg-black bg-opacity-60 flex items-center justify-center z-50">
          <div className="bg-secondary text-white p-6 rounded-xl w-full max-w-lg">
            <h2 className="text-xl font-semibold mb-4">Generate Quiz</h2>

            <div className="space-y-3 text-left">
              <input type="text" name="spaceId" placeholder="Space ID" value={formData.spaceId} onChange={handleChange} className="w-full p-2 rounded bg-gray-800" />
              <input type="text" name="title" placeholder="Quiz Title" value={formData.title} onChange={handleChange} className="w-full p-2 rounded bg-gray-800" />
              <input type="text" name="fileIds" placeholder="Comma-separated File IDs" value={formData.fileIds} onChange={handleChange} className="w-full p-2 rounded bg-gray-800" />
              <input type="number" name="questionCount" placeholder="Number of Questions" value={formData.questionCount} onChange={handleChange} className="w-full p-2 rounded bg-gray-800" />

              <div>
                <label className="block mb-1">Question Types</label>
                {['mcq'].map(type => (
                  <label key={type} className="mr-3">
                    <input
                      type="checkbox"
                      checked={formData.questionTypes.includes(type)}
                      onChange={() => handleTypeToggle(type)}
                      className="mr-1"
                    />
                    {type.toUpperCase()}
                  </label>
                ))}
              </div>

              <select name="difficulty" value={formData.difficulty} onChange={handleChange} className="w-full p-2 rounded bg-gray-800">
                <option value="easy">Easy</option>
                <option value="medium">Medium</option>
                <option value="hard">Hard</option>
              </select>
            </div>

            <div className="mt-6 flex justify-end gap-3">
              <button onClick={() => setShowModal(false)} className="px-4 py-2 bg-gray-600 rounded hover:bg-gray-500">Cancel</button>
              <button onClick={handleSubmit} className="px-4 py-2 bg-blue-600 rounded hover:bg-blue-500">Generate</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default StudyView;
