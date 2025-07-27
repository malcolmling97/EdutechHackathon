import type { CreateSpacePayload, CreatedSpace } from '../components/common/Types';



export const createSpace = async (
  payload: CreateSpacePayload
): Promise<CreatedSpace> => {
  // 🔁 MOCK RESPONSE – comment this out when backend is ready
  return {
    id: `space-${crypto.randomUUID()}`,
    type: 'chat',
    title: 'New Chat',
    folderId: 'real-folder-id',
    settings: payload.settings || {},
  };

  /*
  // ✅ REAL BACKEND CALL – uncomment when backend is ready
  const res = await fetch('/api/v1/spaces', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(payload),
  });

  if (!res.ok) {
    const err = await res.text();
    throw new Error(`Failed to create space: ${err}`);
  }

  const data: CreatedSpace = await res.json();
  return data;
  */
};
