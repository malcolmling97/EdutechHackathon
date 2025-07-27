import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import { getQuiz } from '../utils/getQuiz';
import { FaCheckCircle, FaTimesCircle } from 'react-icons/fa';

const QuizView = () => {
  const { quizId } = useParams();
  const [quiz, setQuiz] = useState<any>(null);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [selected, setSelected] = useState<string | null>(null);
  const [showExplanation, setShowExplanation] = useState(false);
  const [score, setScore] = useState(0);
  const [finished, setFinished] = useState(false);
  

  const token = localStorage.getItem('token') || '';
  const userId = localStorage.getItem('userId') || '';

  /*
  useEffect(() => {
    const load = async () => {
      try {
        const data = await getQuiz({ quizId: quizId!, token, userId });
        setQuiz(data);
      } catch (e) {
        console.error('Failed to load quiz');
      }
    };
    if (quizId) load();
  }, [quizId]);
*/

    useEffect(() => {
        const load = async () => {
        try {
          const data = await getQuiz({
            quizId: 'mock-quiz-id',
            token: 'mock-token',
            userId: 'mock-user-id',
          });
          console.log(data)
            setQuiz(data);
        } catch (e) {
            console.error('Failed to load quiz');
        }
        };
        load();
    }, []);
    
  if (!quiz) return <div className="text-white text-center mt-10">Loading quiz...</div>;

  const currentQuestion = quiz.questions[currentIndex];

  const handleSelect = (choice: string) => {
    if (selected) return; // prevent double select

    setSelected(choice);
    setShowExplanation(true);

    if (choice === currentQuestion.answer) {
      setScore(prev => prev + 1);
    }
  };

  const handleNext = () => {
    if (currentIndex < quiz.questions.length - 1) {
      setCurrentIndex(i => i + 1);
      setSelected(null);
      setShowExplanation(false);
    } else {
      setFinished(true);
    }
  };

  const getOptionClass = (choice: string) => {
    if (!selected) return 'bg-gray-700 hover:bg-gray-600';
    if (choice === currentQuestion.answer) return 'bg-green-700 text-white';
    if (choice === selected) return 'bg-red-700 text-white';
    return 'bg-gray-700 text-white';
  };

  return (
    <div className="max-w-3xl mx-auto text-white px-4 py-12">
      <h1 className="text-3xl font-bold mb-10">{quiz.title}</h1>

      {!finished ? (
        <>
          <div className="mb-8">
            <h2 className="text-2xl font-semibold mb-6">
              {currentIndex + 1}. {currentQuestion.prompt}
            </h2>

            <div className="space-y-3">
              {currentQuestion.choices.map((choice: string, idx: number) => (
                <button
                  key={idx}
                  onClick={() => handleSelect(choice)}
                  disabled={!!selected}
                  className={`w-full flex items-center justify-between px-5 py-3 rounded-lg text-left transition ${getOptionClass(choice)}`}
                >
                  <span>
                    <strong>{String.fromCharCode(65 + idx)}.</strong> {choice}
                  </span>
                  {selected && choice === currentQuestion.answer && (
                    <FaCheckCircle className="text-xl text-white" />
                  )}
                  {selected && choice === selected && choice !== currentQuestion.answer && (
                    <FaTimesCircle className="text-xl text-white" />
                  )}
                </button>
              ))}
            </div>
          </div>

          {showExplanation && currentQuestion.explanation && (
            <div className="bg-gray-800 p-4 rounded mb-6">
              <h4 className="text-white font-bold mb-1">Explanation</h4>
              <p className="text-gray-300 text-sm">{currentQuestion.explanation}</p>
            </div>
          )}

          {showExplanation && (
            <div className="text-right">
              <button
                onClick={handleNext}
                className="px-6 py-2 bg-blue-600 rounded hover:bg-blue-700"
              >
                {currentIndex === quiz.questions.length - 1 ? 'Finish Quiz' : 'Next Question'}
              </button>
            </div>
          )}
        </>
      ) : (
        <div className="text-center mt-10">
          <h2 className="text-3xl font-bold mb-2">Quiz Completed!</h2>
          <p className="text-lg text-gray-300">
            You scored {score} out of {quiz.questions.length} ({Math.round((score / quiz.questions.length) * 100)}%)
          </p>
        </div>
      )}
    </div>
  );
};

export default QuizView;
