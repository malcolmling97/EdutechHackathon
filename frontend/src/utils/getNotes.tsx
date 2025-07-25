/*
export async function getNoteBySpaceId(spaceId: string) {
    const res = await fetch(`/api/v1/spaces/${spaceId}/notes`, {
      headers: {
        Authorization: `Bearer <your-token>`,
        'Content-Type': 'application/json',
      },
    });
  
    if (!res.ok) throw new Error('Failed to load notes');
  
    const { data } = await res.json();
    return data[0]; // assume latest/only note for now
  }
  */

  export async function getNoteBySpaceId(spaceId: string) {
    console.log('Mock fetching note for space:', spaceId);
  
    // simulate delay
    await new Promise((resolve) => setTimeout(resolve, 500));
  
    return {
      id: 'mock-note-123',
      spaceId,
      content: `# Welcome to Your AI Notes\n\nThis is a mock note for space \`${spaceId}\`.\n\n- Editable\n- Auto-saving\n- No backend yet 😉`,
    };
  }