import type { Chat } from './types';

export function generateNewChatId(chats: Chat[]): number {
  return chats.length ? Math.max(...chats.map((c) => c.id)) + 1 : 1;
}
