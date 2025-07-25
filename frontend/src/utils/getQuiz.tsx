import type { GetQuizOptions } from '../components/common/Types';

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
  
  