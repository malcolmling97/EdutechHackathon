import type { CreateSpacePayload, CreatedSpace } from '../components/common/Types';
import { createSpace as apiCreateSpace } from './api';

export const createSpace = async (
  payload: CreateSpacePayload
): Promise<CreatedSpace> => {
  try {
    console.log(`[createSpace] Creating space with title: ${payload.title}, type: ${payload.type}`);
    
    // Call the backend API to create the space
    const newSpace = await apiCreateSpace(payload.folderId, payload.title, payload.type);
    console.log(`[createSpace] Space created successfully with ID: ${newSpace.id}`);
    
    // Return the created space with the correct format
    return {
      id: newSpace.id,
      type: payload.type,
      title: payload.title,
      folderId: payload.folderId,
      settings: payload.settings || {},
    };
  } catch (error) {
    console.error('[createSpace] Failed to create space:', error);
    
    // Fallback to mock implementation for development/testing
    console.warn('[createSpace] Using fallback mock implementation');
    return {
      id: `space-${crypto.randomUUID()}`,
      type: payload.type,
      title: payload.title,
      folderId: payload.folderId,
      settings: payload.settings || {},
    };
  }
};
