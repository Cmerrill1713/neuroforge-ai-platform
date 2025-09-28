import { useState, useCallback, useMemo } from 'react';
import { ChatMessage } from '../types';

interface UseChatReturn {
  messages: ChatMessage[];
  sendMessage: (content: string) => void;
  clearMessages: () => void;
  messageCount: number;
}

export const useChat = (): UseChatReturn => {
  const [messages, setMessages] = useState<ChatMessage[]>([]);

  const sendMessage = useCallback((content: string) => {
    const newMessage: ChatMessage = {
      id: Date.now().toString(),
      content: content.trim(),
      sender: 'user',
      timestamp: new Date(),
    };
    
    setMessages(prev => [...prev, newMessage]);
  }, []);

  const clearMessages = useCallback(() => {
    setMessages([]);
  }, []);

  const messageCount = useMemo(() => messages.length, [messages.length]);

  return {
    messages,
    sendMessage,
    clearMessages,
    messageCount,
  };
};
