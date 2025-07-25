import type { GenerateQuizOptions } from '../components/common/Types';

  export async function generateQuiz({
    spaceId,
    title = 'Auto Generated Quiz',
    fileIds = [],
    questionCount = 5,
    questionTypes = ['mcq'],
    difficulty = 'medium',
    token,
    userId
  }: GenerateQuizOptions) {
    const res = await fetch(`/api/v1/spaces/${spaceId}/quizzes`, {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${token}`,
        'Content-Type': 'application/json',
        'X-User-Id': userId,
      },
      body: JSON.stringify({
        title,
        fileIds,
        questionCount,
        questionTypes,
        difficulty,
      }),
    });
  
    if (!res.ok) {
      const error = await res.json();
      throw new Error(error?.error?.message || 'Failed to generate quiz');
    }
  
    const data = await res.json();
    return data.data; // the quiz object
  }
