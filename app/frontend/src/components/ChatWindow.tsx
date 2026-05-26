import React, { useEffect, useRef } from 'react';
import type { Message } from '../types';
import MessageBubble from './MessageBubble';

interface ChatWindowProps {
  messages: Message[];
}

const ChatWindow: React.FC<ChatWindowProps> = ({ messages }) => {
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  return (
    <div className="flex-1 overflow-y-auto custom-scrollbar px-4 md:px-0 flex flex-col items-center bg-background">
      <div className="w-full max-w-chat py-8 space-y-gutter">
        {/* Timestamp Badge */}
        {messages.length > 0 && (
          <div className="flex justify-center">
            <span className="px-3 py-1 bg-surface-container text-text-secondary text-label-md rounded-full border border-border">
              Today, {new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
            </span>
          </div>
        )}

        {messages.length === 0 ? (
          <div className="flex items-center justify-center h-full">
            <p className="text-text-secondary text-body-md">No messages yet. Ask a question to get started!</p>
          </div>
        ) : (
          messages.map((message) => (
            <MessageBubble key={message.id} message={message} />
          ))
        )}
      </div>
      <div ref={messagesEndRef} />
    </div>
  );
};

export default ChatWindow;
