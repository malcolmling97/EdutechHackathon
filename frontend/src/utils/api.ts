const API_BASE_URL = 'http://localhost:4000/api/v1';

// Helper function to extract UUID from space ID
function extractUUID(id: string): string {
  // If the ID starts with 'space-', extract the UUID part
  if (id.startsWith('space-')) {
    return id.substring(6); // Remove 'space-' prefix
  }
  return id; // Return as is if it doesn't have the prefix
}

export async function fetchFolders() {
  try {
    const response = await fetch(`${API_BASE_URL}/folders`, {
      headers: {
        'X-User-Id': '00000000-0000-0000-0000-000000000001'
      }
    });
    const data = await response.json();
    return data.data;
  } catch (error) {
    console.error('Error fetching folders:', error);
    return [];
  }
}

export async function fetchSpaces(folderId: string) {
  try {
    const response = await fetch(`${API_BASE_URL}/folders/${folderId}/spaces`, {
      headers: {
        'X-User-Id': '00000000-0000-0000-0000-000000000001'
      }
    });
    const data = await response.json();
    return data.data;
  } catch (error) {
    console.error('Error fetching spaces:', error);
    return [];
  }
}

export async function fetchChatHistory(spaceId: string) {
  try {
    const uuid = extractUUID(spaceId);
    console.log(`[API] Fetching chat history for spaceId: ${spaceId}, extracted UUID: ${uuid}`);
    
    const response = await fetch(`${API_BASE_URL}/spaces/${uuid}/messages`, {
      headers: {
        'X-User-Id': '00000000-0000-0000-0000-000000000001'
      }
    });
    
    if (!response.ok) {
      console.error(`[API] Error fetching chat history: ${response.status} ${response.statusText}`);
      const errorText = await response.text();
      console.error(`[API] Error response body:`, errorText);
      throw new Error(`API error: ${response.status} ${response.statusText}`);
    }
    
    const data = await response.json();
    console.log(`[API] Chat history fetch successful, received:`, data);
    return data.data?.messages || [];
  } catch (error) {
    console.error(`[API] Error fetching chat history for spaceId: ${spaceId}:`, error);
    throw error; // Re-throw to allow component to handle error
  }
}

export async function sendChatMessage(spaceId: string, content: string) {
  try {
    const uuid = extractUUID(spaceId);
    console.log(`[API] Sending chat message to spaceId: ${spaceId}, extracted UUID: ${uuid}`);
    console.log(`[API] Message content length: ${content.length}`);
    
    const response = await fetch(`${API_BASE_URL}/spaces/${uuid}/messages`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-User-Id': '00000000-0000-0000-0000-000000000001'
      },
      body: JSON.stringify({ content })
    });
    
    if (!response.ok) {
      console.error(`[API] Error sending message: ${response.status} ${response.statusText}`);
      const errorText = await response.text();
      console.error(`[API] Error response body:`, errorText);
      throw new Error(`API error: ${response.status} ${response.statusText}`);
    }
    
    const data = await response.json();
    console.log(`[API] Message sent successfully, received response:`, data);
    return data.data;
  } catch (error) {
    console.error(`[API] Error sending message to spaceId: ${spaceId}:`, error);
    throw error;
  }
}

export async function createSpace(folderId: string, title: string, type: string = 'chat') {
  try {
    console.log(`[API] Creating space in folder: ${folderId}, type: ${type}, title: ${title}`);
    
    const response = await fetch(`${API_BASE_URL}/folders/${folderId}/spaces`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-User-Id': '00000000-0000-0000-0000-000000000001'
      },
      body: JSON.stringify({ title, type })
    });
    
    if (!response.ok) {
      console.error(`[API] Error creating space: ${response.status} ${response.statusText}`);
      const errorText = await response.text();
      console.error(`[API] Error response body:`, errorText);
      throw new Error(`API error: ${response.status} ${response.statusText}`);
    }
    
    const data = await response.json();
    console.log(`[API] Space created successfully:`, data);
    return data.data;
  } catch (error) {
    console.error(`[API] Error creating space in folder ${folderId}:`, error);
    throw error;
  }
}
