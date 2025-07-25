import type { GetQuizOptions } from '../components/common/Types';
/*
 export async function getQuiz({ quizId, token, userId }: GetQuizOptions) {
    const res = await fetch(`/api/v1/quizzes/${quizId}`, {
      method: 'GET',
      headers: {
        Authorization: `Bearer ${token}`,
        'Content-Type': 'application/json',
        'X-User-Id': userId,
      },
    });
  
    if (!res.ok) {
      const error = await res.json();
      throw new Error(error?.error?.message || 'Failed to fetch quiz');
    }
  
    const data = await res.json();
    return data.data; // quiz object with questions[]
  }

  export interface GetQuizOptions {
    quizId: string;
    token: string;
    userId: string;
  }
  */

  export async function getQuiz() {
    await new Promise((res) => setTimeout(res, 300)); // Simulate delay
  
    return {
      id: 'mock-quiz-id',
      spaceId: 'mock-space-id',
      title: 'Pokémon Knowledge Quiz',
      createdAt: new Date().toISOString(),
      questions: [
        {
          id: 'q1',
          type: 'mcq',
          prompt: 'Which of the following Pokémon is immune to Electric-type moves?',
          choices: ['Gyarados', 'Charizard', 'Gliscor', 'Swampert'],
          answer: 'Swampert',
          explanation:
            'Swampert is a Water/Ground-type Pokémon. Ground-types are immune to Electric-type moves. Despite being part Water, Swampert takes no Electric damage due to its dual typing.',
        },
        {
          id: 'q2',
          type: 'mcq',
          prompt: 'Which Pokémon evolves into Garchomp?',
          choices: ['Gible', 'Gabite', 'Axew', 'Salamence'],
          answer: 'Gabite',
          explanation:
            'Gible evolves into Gabite, and Gabite evolves into Garchomp — a powerful Dragon/Ground pseudo-legendary Pokémon.',
        },
        {
          id: 'q3',
          type: 'mcq',
          prompt: 'What type is super effective against Ghost-type Pokémon?',
          choices: ['Dark', 'Fighting', 'Normal', 'Poison'],
          answer: 'Dark',
          explanation:
            'Dark-type moves are super effective against Ghost-types. Fighting and Normal-type moves don’t even affect them.',
        },
        {
          id: 'q4',
          type: 'mcq',
          prompt: 'Which of the following Pokémon is a Fairy/Steel type?',
          choices: ['Clefairy', 'Jirachi', 'Togekiss', 'Mawile'],
          answer: 'Mawile',
          explanation:
            'Mawile was originally just Steel-type, but it became Fairy/Steel in Gen VI. It’s the only one of the listed Pokémon with that typing.',
        },
        {
          id: 'q5',
          type: 'mcq',
          prompt: 'Which Pokémon is known as the "Aura Pokémon"?',
          choices: ['Riolu', 'Lucario', 'Mewtwo', 'Zoroark'],
          answer: 'Lucario',
          explanation:
            'Lucario is known as the Aura Pokémon, capable of sensing and manipulating aura energy. It’s also featured in Super Smash Bros.',
        },
      ],
    };
  }
  
  