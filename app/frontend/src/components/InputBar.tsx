import React, { useState } from 'react';

interface InputBarProps {
  onSend: (message: string) => void;
  disabled: boolean;
}

const InputBar: React.FC<InputBarProps> = ({ onSend, disabled }) => {
  const [input, setInput] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (input.trim() && !disabled) {
      onSend(input.trim());
      setInput('');
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  return (
    <div className="w-full flex flex-col items-center border-t border-border bg-surface-container-low px-4 py-4 space-y-3">
      <form onSubmit={handleSubmit} className="w-full max-w-chat relative">
        <div className="flex-1 bg-surface-container-highest border border-border rounded-xl flex items-center px-4 py-3 focus-within:border-primary-container transition-all shadow-sm">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Ask about fund details, returns, or risks..."
            disabled={disabled}
            className="flex-1 bg-transparent border-none focus:ring-0 text-body-lg placeholder:text-text-secondary outline-none text-text-primary disabled:opacity-50 disabled:cursor-not-allowed"
            maxLength={500}
          />
          <button
            type="submit"
            disabled={disabled || !input.trim()}
            className="bg-primary-container text-on-primary-container p-2 rounded-lg hover:opacity-90 active:scale-95 transition-all flex items-center justify-center disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14 5l7 7m0 0l-7 7m7-7H3" />
            </svg>
          </button>
        </div>
      </form>
      {input.length > 0 && (
        <p className="text-label-md text-text-secondary text-center">
          {input.length}/500 characters • Press Enter to send
        </p>
      )}
    </div>
  );
};

export default InputBar;
