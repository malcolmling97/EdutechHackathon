import type { CreatedSpace } from '../components/common/Types';
import { getResources } from './getResources';
import { getNotesList } from './getNotesList';
import { getStudyList } from './getStudyList';

/*
export const getSpaces = async (token: string, userId: string): Promise<CreatedSpace[]> => {
  const res = await fetch('/api/v1/spaces', {
    headers: {
      'Authorization': `Bearer ${token}`,
      'X-User-Id': userId,
    },
  });
  if (!res.ok) {
    const err = await res.text();
    throw new Error(`Failed to fetch spaces: ${err}`);
  }
  const json = await res.json();
  return json.data;
};
*/

export const getSpaces = async (token: string, userId: string): Promise<CreatedSpace[]> => {
  try {
    const [resources, notes, study] = await Promise.all([
      getResources(), // or undefined if mocked
      getNotesList(),
      getStudyList()
    ]);

    const now = new Date().toISOString();

    const resourceSpaces = resources.map(res => ({
      id: res.id,
      folderId: 'mock-folder',
      type: 'resources' as const, // adjust this if your `res.type` maps to something more specific
      title: res.title,
      settings: {},
      createdAt: now
    }));

    const noteSpaces = notes.map(note => ({
      id: note.id,
      folderId: 'mock-folder',
      type: 'notes' as const,
      title: note.title,
      settings: {},
      createdAt: now
    }));

    const studySpaces = study.map(item => ({
      id: item.id,
      folderId: 'mock-folder',
      type: 'studyguide' as const, // or quiz, openended, flashcards depending on how you mock them
      title: item.title,
      settings: {},
      createdAt: now
    }));

    return [...resourceSpaces, ...noteSpaces, ...studySpaces];
  } catch (err) {
    console.error('Error mocking getSpaces:', err);
    return [];
  }
};
