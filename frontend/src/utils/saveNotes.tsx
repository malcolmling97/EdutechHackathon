export async function saveNote(noteId: string, content: string, token: string, userId: string) {
  const res = await fetch(`/api/v1/notes/${noteId}`, {
    method: 'PATCH',
    headers: {
      Authorization: `Bearer ${token}`,
      'Content-Type': 'application/json',
      'X-User-Id': userId,
    },
    body: JSON.stringify({ content }),
  });

  if (!res.ok) throw new Error('Failed to save note');
  const json = await res.json();
  return json.data;
}