/*
export async function saveNote(noteId: string, content: string) {
    const res = await fetch(`/api/v1/notes/${noteId}`, {
      method: 'PATCH',
      headers: {
        Authorization: `Bearer <your-token>`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ content }),
    });
  
    if (!res.ok) throw new Error('Failed to save note');
  }
  */

  export async function saveNote(noteId: string, content: string) {
    console.log('Mock saving note:', noteId);
    console.log('New content:', content);
  
    // simulate delay
    await new Promise((resolve) => setTimeout(resolve, 300));
  }