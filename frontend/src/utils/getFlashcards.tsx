import { Flashcard } from "../components/common/Types";

export async function getFlashcards(spaceId: string): Promise<Flashcard[]> {
    console.log('Mock fetching flashcards for:', spaceId);
  
    // Simulate delay
    await new Promise((r) => setTimeout(r, 500));
  
    return [
      {
        id: '1',
        front: 'What is photosynthesis?',
        back: 'A process used by plants to convert light energy into chemical energy.',
      },
      {
        id: '2',
        front: 'Where does photosynthesis occur?',
        back: 'In the chloroplasts of plant cells.',
      },
      {
        id: '3',
        front: 'What is the main product of photosynthesis?',
        back: 'Glucose (C6H12O6).',
      },
    ];
  }