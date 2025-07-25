import type { CreatedSpace } from '../components/common/Types';

export const getSpaces = async (): Promise<CreatedSpace[]> => {
  const res = await fetch('/api/v1/spaces');
  if (!res.ok) {
    const err = await res.text();
    throw new Error(`Failed to fetch spaces: ${err}`);
  }
  return res.json();
};