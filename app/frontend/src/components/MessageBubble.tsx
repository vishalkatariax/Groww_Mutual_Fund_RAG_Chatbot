import React from 'react';
import type { Message } from '../types';
import SourceLink from './SourceLink';

interface MessageBubbleProps {
  message: Message;
}

const MessageBubble: React.FC<MessageBubbleProps> = ({ message }) => {
  const isUser = message.type === 'user';
  
  if (isUser) {
    return (
      <div className="flex justify-end w-full mb-4">
        <div className="max-w-[85%] md:max-w-[70%] bg-primary-container text-text-primary rounded-2xl rounded-tr-lg px-5 py-4 shadow-lg">
          <p className="text-body-lg whitespace-pre-wrap">{message.content}</p>
        </div>
      </div>
    );
  }
  
  // Bot message
  const isRefusal = message.is_refusal;
  const isLoading = message.isLoading;
  
  return (
    <div className="flex justify-start w-full mb-4">
      <div className={`max-w-[85%] md:max-w-[80%] p-5 rounded-2xl rounded-tl-lg ${
        isRefusal 
          ? 'bg-surface-card border-l-4 border-error-refusal border-y border-r border-border shadow-lg' 
          : 'bg-surface-card border border-border shadow-lg'
      }`}>
        {/* Bot Header */}
        {!isLoading && (
          <div className="flex items-center gap-2 mb-3">
            <svg className="w-5 h-5 text-primary" fill="currentColor" viewBox="0 0 20 20">
              <path d="M2 5a2 2 0 012-2h7a2 2 0 012 2v4a2 2 0 01-2 2H9l-3 3v-3H4a2 2 0 01-2-2V5z" />
              <path d="M15 7v2a4 4 0 01-4 4H9.828l-1.766 1.767c.28.149.599.233.938.233h2l3 3v-3h2a2 2 0 002-2V9a2 2 0 00-2-2h-1z" />
            </svg>
            <span className="text-label-lg font-semibold text-primary">Groww Assistant</span>
          </div>
        )}

        {isLoading ? (
          <div className="flex items-center gap-2">
            <div className="flex gap-1">
              <div className="w-2 h-2 bg-text-secondary rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
              <div className="w-2 h-2 bg-text-secondary rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
              <div className="w-2 h-2 bg-text-secondary rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
            </div>
            <span className="text-body-md text-text-secondary">Thinking...</span>
          </div>
        ) : (
          <>
            {isRefusal ? (
              // Refusal styling with enhanced visual treatment
              <div className="space-y-3">
                <div className="flex items-start gap-3 bg-error-refusal/10 -ml-3 -mr-3 -mt-3 p-3 rounded-t-2xl border-b border-error-refusal/20">
                  <svg className="w-5 h-5 text-error-refusal flex-shrink-0 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                  </svg>
                  <div>
                    <h4 className="text-label-lg font-semibold text-error-refusal">Compliance Notice</h4>
                  </div>
                </div>
                <p className="text-body-lg leading-relaxed text-text-primary">
                  {message.content}
                </p>
                <p className="text-body-md text-text-secondary italic border-l-2 border-error-refusal/30 pl-3">
                  Please consult a SEBI-registered financial advisor to assess your risk profile and goal alignment.
                </p>
              </div>
            ) : (
              // Normal response
              <div className="space-y-3">
                <p className="text-body-lg leading-relaxed text-text-primary">
                  {message.content}
                </p>
                
                {message.source_url && (
                  <SourceLink url={message.source_url} />
                )}
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
};

export default MessageBubble;
