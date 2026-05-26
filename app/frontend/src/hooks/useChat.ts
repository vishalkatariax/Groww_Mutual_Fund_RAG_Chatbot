import { useState, useCallback } from 'react';
import type { Message } from '../types';
import { chatApi } from '../services/api';

const generateId = () => `msg_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;

export function useChat() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isProcessing, setIsProcessing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [selectedScheme, setSelectedScheme] = useState<string | null>(null);

  const sendMessage = useCallback(async (query: string) => {
    if (!query.trim() || isProcessing) return;

    // Clear previous errors
    setError(null);

    // Add user message
    const userMessage: Message = {
      id: generateId(),
      type: 'user',
      content: query.trim(),
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);

    // Add loading message
    const loadingMessage: Message = {
      id: generateId(),
      type: 'bot',
      content: 'Thinking...',
      timestamp: new Date(),
      isLoading: true,
    };

    setMessages((prev) => [...prev, loadingMessage]);
    setIsProcessing(true);

    try {
      // Call API
      const response = await chatApi.sendMessage(query.trim());

      // Replace loading message with actual response
      const botMessage: Message = {
        id: loadingMessage.id,
        type: 'bot',
        content: response.answer,
        source_url: response.source_url,
        last_updated: response.last_updated,
        is_refusal: response.is_refusal,
        query_type: response.query_type,
        timestamp: new Date(),
      };

      setMessages((prev) =>
        prev.map((msg) => (msg.id === loadingMessage.id ? botMessage : msg))
      );
    } catch (err: any) {
      // Replace loading message with error
      const errorMessage: Message = {
        id: loadingMessage.id,
        type: 'bot',
        content: 'Sorry, I encountered an error. Please try again.',
        timestamp: new Date(),
        is_refusal: true,
      };

      setMessages((prev) =>
        prev.map((msg) => (msg.id === loadingMessage.id ? errorMessage : msg))
      );

      setError(err.message || 'Failed to send message');
      console.error('[useChat] Error:', err);
    } finally {
      setIsProcessing(false);
    }
  }, [isProcessing]);

  const clearChat = useCallback(() => {
    setMessages([]);
    setError(null);
  }, []);

  return {
    messages,
    isProcessing,
    error,
    sendMessage,
    clearChat,
    selectedScheme,
    setSelectedScheme,
  };
}
