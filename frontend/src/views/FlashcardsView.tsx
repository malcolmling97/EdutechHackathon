import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import { getFlashcards } from '../utils/getFlashcards';
import { Flashcard } from '../components/common/Types';
import { ChevronLeft, ChevronRight } from '../components/common/Icons';

const FlashcardsView = () => {
  const { spaceId = 'mock-space-id' } = useParams();
  const [flashcards, setFlashcards] = useState<Flashcard[]>([]);
  const [current, setCurrent] = useState(0);
  const [flipped, setFlipped] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getFlashcards(spaceId)
      .then(setFlashcards)
      .catch(console.error)
      .finally(() => setLoading(false));
  }, [spaceId]);

  const nextCard = () => {
    setFlipped(false);
    setCurrent((prev) => (prev + 1) % flashcards.length);
  };

  const prevCard = () => {
    setFlipped(false);
    setCurrent((prev) => (prev - 1 + flashcards.length) % flashcards.length);
  };

  const shuffleCards = () => {
    const shuffled = [...flashcards].sort(() => Math.random() - 0.5);
    setFlashcards(shuffled);
    setCurrent(0);
    setFlipped(false);
  };

  if (loading) return <p className="text-center text-gray-400">Loading flashcards...</p>;
  if (flashcards.length === 0) return <p className="text-center text-gray-500">No flashcards available.</p>;

  const currentCard = flashcards[current];

  return (
    <div className="flex flex-col items-center justify-center h-screen text-white bg-[#121212] px-4 relative">
      {/* Top Bar */}
      <div className="absolute top-6 flex gap-4 items-center text-sm text-gray-400">
        <button className="px-3 py-1 bg-gray-700 rounded hover:bg-gray-600">Edit</button>
        <span className="text-gray-300">|</span>
        <span className="text-gray-300">Card {current + 1} of {flashcards.length}</span>
        <span className="text-gray-300">|</span>
        <button onClick={shuffleCards} className="px-3 py-1 bg-gray-700 rounded hover:bg-gray-600">Shuffle</button>
      </div>

      {/* Left Arrow */}
      <button onClick={prevCard} className="absolute left-6 text-gray-400 hover:text-white">
        <ChevronLeft />
      </button>

      {/* Card */}
      <div
        onClick={() => setFlipped((f) => !f)}
        className="bg-[#2c2c2c] rounded-2xl shadow-xl p-12 w-full max-w-xl text-center cursor-pointer transition duration-300"
      >
        <p className="text-xl font-semibold">{flipped ? currentCard.back : currentCard.front}</p>
        <p className="text-xs text-gray-400 mt-2">{flipped ? 'Back' : 'Front'} - Click to flip</p>
      </div>

      {/* Right Arrow */}
      <button onClick={nextCard} className="absolute right-6 text-gray-400 hover:text-white">
        <ChevronRight />
      </button>
    </div>
  );
};

export default FlashcardsView;
