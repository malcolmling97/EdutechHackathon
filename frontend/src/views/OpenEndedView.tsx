import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import { getOpenEndedQuestion } from '../utils/getOpenEnded';

const OpenEndedView = () => {
  const { spaceId = 'mock-space-id' } = useParams();
  const [question, setQuestion] = useState<{ prompt: string; explanation: string } | null>(null);
  const [userAnswer, setUserAnswer] = useState('');

  useEffect(() => {
    getOpenEndedQuestion(spaceId)
      .then(setQuestion)
      .catch(console.error);
  }, [spaceId]);

  return (
    <div className="flex flex-col justify-between min-h-screen bg-[#121212] text-white p-6">
      <div>
        <h2 className="text-xl font-semibold mb-6">{question?.prompt || 'Loading question...'}</h2>
        {question && (
          <div className="mt-6 text-sm text-gray-400">
            <p className="font-medium text-white">Explanation</p>
            <p>{question.explanation}</p>
          </div>
        )}
      </div>

      {/* Input */}
      <div className="mt-8">
        <textarea
          value={userAnswer}
          onChange={(e) => setUserAnswer(e.target.value)}
          rows={4}
          placeholder="Your answer..."
          className="w-full bg-gray-800 rounded-lg p-4 text-sm text-white resize-none focus:outline-none focus:ring-2 focus:ring-blue-600"
        />
      </div>
    </div>
  );
};

export default OpenEndedView;
