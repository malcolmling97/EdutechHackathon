import type { FileMetadata, MessageSource, SendChatOptions, ChatMessage } from '../components/common/Types';

export const sendChatMessage = async ({
  spaceId,
  content,
  file,
  folderId,
  role = 'user',
  token,
  userId,
}: SendChatOptions & { token: string; userId: string }): Promise<ChatMessage> => {
  let sources: MessageSource[] = [];

  if (file) {
    if (!folderId) {
      throw new Error('folderId is required when uploading a file.');
    }

    const formData = new FormData();
    formData.append('files', file);
    formData.append('folderId', folderId);

    const fileRes = await fetch('/api/v1/files/upload', {
      method: 'POST',
      headers: { 'Authorization': `Bearer ${token}`, 'X-User-Id': userId },
      body: formData,
    });

    if (!fileRes.ok) {
      const errorText = await fileRes.text();
      throw new Error(`Upload failed: ${errorText}`);
    }

    const fileJson = await fileRes.json();
    const uploadedFile: FileMetadata = fileJson.data ? fileJson.data[0] : fileJson; // API returns { data: [...] }
    sources.push({ fileId: uploadedFile.id, page: 1 });
  }

  const messagePayload: Omit<ChatMessage, 'id'> = {
    spaceId,
    role,
    content,
    sources: sources.length > 0 ? sources : undefined,
    createdAt: new Date().toISOString(),
  };

  const msgRes = await fetch(`/api/v1/spaces/${spaceId}/messages`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`,
      'X-User-Id': userId,
    },
    body: JSON.stringify(messagePayload),
  });

  if (!msgRes.ok) {
    const errorText = await msgRes.text();
    throw new Error(`Message send failed: ${errorText}`);
  }

  const msgJson = await msgRes.json();
  return msgJson.data;
};
