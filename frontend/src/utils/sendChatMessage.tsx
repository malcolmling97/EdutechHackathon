import type { FileMetadata, MessageSource, SendChatOptions, ChatMessage } from '../components/common/Types';

export const sendChatMessage = async ({
  spaceId,
  content,
  file,
  folderId,
  role = 'user',
}: SendChatOptions): Promise<ChatMessage> => {
  let sources: MessageSource[] = [];

  if (file) {
    if (!folderId) {
      throw new Error('folderId is required when uploading a file.');
    }

    const formData = new FormData();
    formData.append('files', file);
    formData.append('folderId', folderId);

    const fileRes = await fetch('/files/upload', {
      method: 'POST',
      body: formData,
    });

    if (!fileRes.ok) {
      const errorText = await fileRes.text();
      throw new Error(`Upload failed: ${errorText}`);
    }

    const uploadedFile: FileMetadata = await fileRes.json();
    sources.push({ fileId: uploadedFile.id, page: 1 }); // assuming page 1 for now
  }

  const messagePayload: Omit<ChatMessage, 'id'> = {
    spaceId,
    role,
    content,
    sources: sources.length > 0 ? sources : undefined,
    createdAt: new Date().toISOString(),
  };

  const msgRes = await fetch(`/spaces/${spaceId}/messages`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(messagePayload),
  });

  if (!msgRes.ok) {
    const errorText = await msgRes.text();
    throw new Error(`Message send failed: ${errorText}`);
  }

  const createdMessage: ChatMessage = await msgRes.json();
  return createdMessage;
};
