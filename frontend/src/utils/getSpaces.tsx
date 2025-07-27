import type { CreatedSpace } from '../components/common/Types';
import { loadMockSpaces } from './loadMockSpaces';
import { getNotesList } from './getNotesList';
import { getStudyList } from './getStudyList';
import { getResources } from './getResources'

const CHAT_LIST_KEY = 'chat-list';

export const getSpaces = async (token: string, userId: string): Promise<CreatedSpace[]> => {
  try {
    //const [resources, notes, study] = await Promise.all([
      // Uncomment when using real data:
      // loadMockResources(token, userId),
      // getNotesList(token, userId),
      // getStudyList(token, userId)
    //]);

    const now = new Date().toISOString();

    /*
    const resourceSpaces: CreatedSpace[] = (resources || []).map(res => ({
      id: res.id,
      folderId: 'mock-folder',
      type: 'resources',
      title: res.title,
      settings: {},
      createdAt: now,
    }));

    const noteSpaces: CreatedSpace[] = (notes || []).map(note => ({
      id: note.id,
      folderId: 'mock-folder',
      type: 'notes',
      title: note.title,
      settings: {},
      createdAt: now,
    }));

    const studySpaces: CreatedSpace[] = (study || []).map(item => ({
      id: item.id,
      folderId: 'mock-folder',
      type: 'studyguide',
      title: item.title,
      settings: {},
      createdAt: now,
    }));
    */

    // 👇 Load from /public/mock_spaces_with_generatedTypes.json
    const mockRes = await fetch('/mock_spaces.json');
    const mockList = await mockRes.json();

    const localSpaces: CreatedSpace[] = mockList.map((item: any): CreatedSpace => ({
      id: item.id,
      type: item.type || 'chat',
      title: item.title,
      folderId: 'mock-folder',
      settings: item.settings || {},
    }));

    return [ ...localSpaces,];
  } catch (err) {
    console.error('Error merging mocked + local spaces:', err);
    return [];
  }
};
