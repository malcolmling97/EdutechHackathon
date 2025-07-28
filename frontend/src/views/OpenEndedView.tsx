import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import { getOpenEndedQuestion } from '../utils/getOpenEnded';
import { useNavigate, useLocation } from 'react-router-dom';


type OpenEndedQuestion = {
  id: string;
  prompt: string;
  explanation: string;
};

const OpenEndedView = () => {
  const { spaceId = 'mock-space-id' } = useParams();
  const [questions, setQuestions] = useState<OpenEndedQuestion[]>([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [userAnswers, setUserAnswers] = useState<Record<string, string>>({});
  const [gradedQuestions, setGradedQuestions] = useState<Record<string, boolean>>({});
  const [finished, setFinished] = useState(false);
  const navigate = useNavigate();
  const location = useLocation();
  const from = location.state?.from || null;

  useEffect(() => {
    getOpenEndedQuestion(spaceId)
      .then(setQuestions)
      .catch(console.error);
  }, [spaceId]);

  const currentQuestion = questions[currentIndex];

  const handleAnswerChange = (value: string) => {
    if (currentQuestion) {
      setUserAnswers((prev) => ({
        ...prev,
        [currentQuestion.id]: value,
      }));
    }
  };

  const handleGrade = () => {
    if (currentQuestion) {
      setGradedQuestions((prev) => ({
        ...prev,
        [currentQuestion.id]: true,
      }));
    }
  };

  const handleNext = () => {
    if (currentIndex < questions.length - 1) {
      setCurrentIndex((prev) => prev + 1);
    } else {
      setFinished(true);
    }
  };

  const handlePrevious = () => {
    if (currentIndex > 0) {
      setCurrentIndex((prev) => prev - 1);
    }
  };

  if (questions.length === 0) {
    return <div className="p-6 text-gray-400">Loading questions...</div>;
  }

  if (finished) {
    return (
      <div className="min-h-screen flex flex-col justify-center items-center bg-[#121212] text-white p-6">
        <h2 className="text-2xl font-bold mb-4">🎉 You've completed the quiz!</h2>
        <p className="text-gray-400">Thank you for your answers.</p>
      </div>
    );
  }

  const isGraded = gradedQuestions[currentQuestion.id];

  return (
    <div className="min-h-screen bg-[#121212] text-white p-6 flex flex-col justify-between">
      <div>
        <div className="mb-4">
        <button
          onClick={() => from ? navigate(`/study/${from}`) : navigate(-1)}
          className="text-sm text-blue-400 hover:underline"
        >
          ← Back
        </button>
      </div>
        <h2 className="text-xl font-semibold mb-6">{currentQuestion.prompt}</h2>

        <div className="mt-6">
          <textarea
            value={userAnswers[currentQuestion.id] || ''}
            onChange={(e) => handleAnswerChange(e.target.value)}
            rows={6}
            placeholder="Your answer..."
            className="w-full bg-gray-800 rounded-lg p-4 text-sm text-white resize-none focus:outline-none focus:ring-2 focus:ring-blue-600"
          />
        </div>

        {isGraded && (
          <div className="mt-6 text-sm text-gray-400">
            <p className="font-medium text-white">Explanation</p>
            <p>{currentQuestion.explanation}</p>
          </div>
        )}
      </div>

      <div className="mt-8 flex justify-between">
        {isGraded ? (
          <>
            <button
              onClick={handlePrevious}
              disabled={currentIndex === 0}
              className={`px-6 py-2 rounded-md font-medium ${
                currentIndex === 0
                  ? 'bg-gray-600 text-white cursor-not-allowed'
                  : 'bg-gray-700 text-white hover:bg-gray-600'
              }`}
            >
              Previous
            </button>
            <button
              onClick={handleNext}
              className="px-6 py-2 rounded-md bg-blue-600 text-white hover:bg-blue-700 font-medium"
            >
              {currentIndex < questions.length - 1 ? 'Next' : 'Finish'}
            </button>
          </>
        ) : (
          <button
            onClick={handleGrade}
            disabled={!userAnswers[currentQuestion.id]?.trim()}
            className={`px-6 py-2 rounded-md font-medium w-full ${
              userAnswers[currentQuestion.id]?.trim()
                ? 'bg-green-600 text-white hover:bg-green-700'
                : 'bg-gray-600 text-white cursor-not-allowed'
            }`}
          >
            Grade Me
          </button>
        )}
      </div>
    </div>
  );
};

export default OpenEndedView;
