import type { CreatedSpace } from '../components/common/Types';

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