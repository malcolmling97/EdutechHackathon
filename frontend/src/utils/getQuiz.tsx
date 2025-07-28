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
    title: 'Cloud Computing Quiz',
    questions: [
      {
        id: 'q1',
        prompt: 'What is cloud computing?',
        choices: [
          'A local storage solution',
          'A way to run applications without any hardware',
          'The delivery of computing services over the internet',
          'A method to clean computer hardware',
        ],
        answer: 'The delivery of computing services over the internet',
        explanation: 'Cloud computing delivers servers, storage, databases, networking, and software over the internet.',
      },
      {
        id: 'q2',
        prompt: 'Which of the following is a key benefit of cloud computing?',
        choices: ['Fixed resource capacity', 'High upfront costs', 'Scalability', 'Manual server management'],
        answer: 'Scalability',
        explanation: 'Cloud resources can be scaled up or down based on demand, making scalability a key benefit.',
      },
      {
        id: 'q3',
        prompt: 'Which service model offers virtual machines and storage?',
        choices: ['SaaS', 'PaaS', 'IaaS', 'DaaS'],
        answer: 'IaaS',
        explanation: 'Infrastructure as a Service (IaaS) provides basic computing infrastructure like virtual machines and networks.',
      },
      {
        id: 'q4',
        prompt: 'What does SaaS stand for?',
        choices: [
          'Software and Application as a Service',
          'System as a Software',
          'Software as a Service',
          'Storage and Access Service',
        ],
        answer: 'Software as a Service',
        explanation: 'SaaS delivers software applications over the internet (e.g., Google Docs, Dropbox).',
      },
      {
        id: 'q5',
        prompt: 'Which of the following best describes virtualization in cloud computing?',
        choices: [
          'Buying new physical servers',
          'Running software directly on hardware',
          'Creating virtual versions of physical resources',
          'Installing software updates manually',
        ],
        answer: 'Creating virtual versions of physical resources',
        explanation: 'Virtualization abstracts physical resources into virtual environments, enabling efficient resource use.',
      }
    ]
  };
}