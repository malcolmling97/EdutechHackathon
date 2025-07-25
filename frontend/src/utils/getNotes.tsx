export async function getNoteBySpaceId(spaceId: string, token: string, userId: string) {
  const res = await fetch(`/api/v1/spaces/${spaceId}/notes`, {
    headers: {
      Authorization: `Bearer ${token}`,
      'Content-Type': 'application/json',
      'X-User-Id': userId,
    },
  });

  if (!res.ok) throw new Error('Failed to load notes');

  const { data } = await res.json();
  return data[0]; // assume latest/only note for now
}