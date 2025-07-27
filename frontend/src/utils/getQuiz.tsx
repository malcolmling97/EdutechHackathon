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
*/  

export async function getQuiz({ quizId, token, userId }: GetQuizOptions) {
  // Simulate delay
  await new Promise((resolve) => setTimeout(resolve, 500));

  // Return mock quiz data about Photosynthesis
  return {
    id: quizId,
    title: 'Photosynthesis Quiz',
    questions: [
      {
        id: 'q1',
        prompt: 'What is the main purpose of photosynthesis?',
        choices: [
          'To convert light energy into chemical energy',
          'To absorb carbon dioxide',
          'To produce nitrogen for the soil',
          'To create minerals for the plant',
        ],
        answer: 'To convert light energy into chemical energy',
        explanation: 'Photosynthesis converts light energy into glucose, a chemical energy form used by plants.',
      },
      {
        id: 'q2',
        prompt: 'Which organelle is responsible for photosynthesis?',
        choices: ['Nucleus', 'Mitochondrion', 'Chloroplast', 'Ribosome'],
        answer: 'Chloroplast',
        explanation: 'Photosynthesis takes place in chloroplasts, which contain the pigment chlorophyll.',
      },
      {
        id: 'q3',
        prompt: 'What gas is released as a byproduct of photosynthesis?',
        choices: ['Carbon dioxide', 'Oxygen', 'Nitrogen', 'Methane'],
        answer: 'Oxygen',
        explanation: 'Oxygen is released as a byproduct when water molecules are split during the light-dependent reactions.',
      },
      {
        id: 'q4',
        prompt: 'Which of the following is required for photosynthesis?',
        choices: ['Oxygen', 'Glucose', 'Sunlight', 'ATP'],
        answer: 'Sunlight',
        explanation: 'Sunlight provides the energy required to drive photosynthesis.',
      },
      {
        id: 'q5',
        prompt: 'What is the balanced chemical equation for photosynthesis?',
        choices: [
          '6 H₂O + 6 O₂ → C₆H₁₂O₆ + 6 CO₂',
          '6 CO₂ + 6 H₂O → C₆H₁₂O₆ + 6 O₂',
          '6 CO₂ + 12 H₂O → C₆H₁₂O₆ + 6 H₂O + 6 O₂',
          'C₆H₁₂O₆ + 6 O₂ → 6 CO₂ + 6 H₂O',
        ],
        answer: '6 CO₂ + 6 H₂O → C₆H₁₂O₆ + 6 O₂',
        explanation: 'This is the correct simplified equation for photosynthesis.',
      }
    ]
  };
}