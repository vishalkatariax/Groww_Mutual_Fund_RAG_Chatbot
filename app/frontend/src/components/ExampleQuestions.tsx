import React from 'react';
import type { ExampleQuestion } from '../types';

interface ExampleQuestionsProps {
  onQuestionClick: (query: string) => void;
  disabled: boolean;
}

const EXAMPLE_QUESTIONS: ExampleQuestion[] = [
  {
    text: 'What is the NAV of HDFC Mid-Cap Fund?',
    query: 'What is the NAV of HDFC Mid-Cap Fund?',
    icon: (
      <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
      </svg>
    ),
  },
  {
    text: 'What is the exit load for HDFC ELSS Tax Saver Fund?',
    query: 'What is the exit load for HDFC ELSS Tax Saver Fund?',
    icon: (
      <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
      </svg>
    ),
  },
  {
    text: 'What are the top holdings of HDFC Large Cap Fund?',
    query: 'What are the top holdings of HDFC Large Cap Fund?',
    icon: (
      <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 3.055A9.001 9.001 0 1020.945 13H11V3.055z" />
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20.488 9H15V3.512A9.025 9.025 0 0120.488 9z" />
      </svg>
    ),
  },
];

const ExampleQuestions: React.FC<ExampleQuestionsProps> = ({ onQuestionClick, disabled }) => {
  return (
    <div className="px-4 pb-8">
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 w-full max-w-3xl mx-auto">
        {EXAMPLE_QUESTIONS.map((q, idx) => (
          <button
            key={idx}
            onClick={() => onQuestionClick(q.query)}
            disabled={disabled}
            className="bg-surface-card/70 backdrop-blur-sm border border-border rounded-xl p-6 text-left hover:bg-surface-container-high transition-all duration-300 group active:scale-95 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <div className="text-primary mb-3">
              {q.icon}
            </div>
            <p className="text-label-lg text-text-primary group-hover:text-primary transition-colors">
              {q.text}
            </p>
          </button>
        ))}
      </div>
    </div>
  );
};

export default ExampleQuestions;
