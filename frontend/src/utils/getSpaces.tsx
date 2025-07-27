import type { CreatedSpace } from '../components/common/Types';
import { getResources } from './getResources';
import { getNotesList } from './getNotesList';
import { getStudyList } from './getStudyList';

const CHAT_LIST_KEY = 'chat-list';

export const getSpaces = async (token: string, userId: string): Promise<CreatedSpace[]> => {
  try {
    const [resources, notes, study] = await Promise.all([
      getResources(),
      getNotesList(),
      getStudyList()
    ]);

    const now = new Date().toISOString();

    const resourceSpaces: CreatedSpace[] = resources.map(res => ({
      id: res.id,
      folderId: 'mock-folder',
      type: 'resources',
      title: res.title,
      settings: {},
      createdAt: now,
    }));

    const noteSpaces: CreatedSpace[] = notes.map(note => ({
      id: note.id,
      folderId: 'mock-folder',
      type: 'notes',
      title: note.title,
      settings: {},
      createdAt: now,
    }));

    const studySpaces: CreatedSpace[] = study.map(item => ({
      id: item.id,
      folderId: 'mock-folder',
      type: 'studyguide',
      title: item.title,
      settings: {},
      createdAt: now,
    }));

    // 👇 Get generated items from localStorage
    const localList = JSON.parse(localStorage.getItem(CHAT_LIST_KEY) || '[]');

    const localSpaces: CreatedSpace[] = localList.map((item: any): CreatedSpace => ({
      id: item.id,
      type: item.type || 'chat', // fallback if old entries
      title: item.title,
      folderId: 'mock-folder',
      settings: item.settings || {},
    }));

    return [...resourceSpaces, ...noteSpaces, ...studySpaces, ...localSpaces];
  } catch (err) {
    console.error('Error merging mocked + local spaces:', err);
    return [];
  }
};
