import React from 'react';
import { useChat } from './hooks/useChat';
import DisclaimerBanner from './components/DisclaimerBanner';
import WelcomeSection from './components/WelcomeSection';
import ExampleQuestions from './components/ExampleQuestions';
import ChatWindow from './components/ChatWindow';
import InputBar from './components/InputBar';
import SchemeSelector from './components/SchemeSelector';

const App: React.FC = () => {
  const { messages, isProcessing, error, sendMessage, clearChat, selectedScheme, setSelectedScheme } = useChat();
  const hasMessages = messages.length > 0;

  return (
    <div className="flex flex-col h-screen bg-background">
      {/* Header with Glass Effect */}
      <header className="sticky top-0 z-50 bg-background/80 backdrop-blur-md border-b border-border px-margin-mobile md:px-margin-desktop h-16 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <svg className="w-6 h-6 text-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
          </svg>
          <h1 className="text-headline-md font-extrabold text-text-primary">Groww MF FAQ Assistant</h1>
        </div>
        
        <div className="flex items-center gap-4">
          <SchemeSelector 
            selectedScheme={selectedScheme} 
            onSchemeSelect={setSelectedScheme} 
          />
          
          {hasMessages && (
            <button
              onClick={clearChat}
              className="px-3 py-1.5 text-label-md text-text-secondary hover:text-text-primary hover:bg-surface-container-high rounded-lg transition-colors"
            >
              New Chat
            </button>
          )}
          <span className="text-label-md text-text-secondary hidden md:block">
            Last updated: May 26, 2026
          </span>
        </div>
      </header>

      {/* Disclaimer Banner - Moved above input */}
      {!hasMessages && (
        <DisclaimerBanner />
      )}
      
      {/* Main Content */}
      <div className="flex-1 flex flex-col max-w-chat mx-auto w-full">
        {/* Error Message */}
        {error && (
          <div className="bg-functional-error/10 border-b border-functional-error px-6 py-3">
            <p className="text-sm text-functional-error">{error}</p>
          </div>
        )}

        {/* Welcome Section (shown when no messages) */}
        {!hasMessages && <WelcomeSection />}

        {/* Example Questions (shown when no messages) */}
        {!hasMessages && (
          <ExampleQuestions
            onQuestionClick={sendMessage}
            disabled={isProcessing}
          />
        )}

        {/* Chat Window */}
        {hasMessages && <ChatWindow messages={messages} />}

        {/* Disclaimer above input */}
        {hasMessages && (
          <div className="w-full px-4 py-2 border-t border-border bg-surface-container-low/50">
            <div className="max-w-chat mx-auto flex items-center justify-center gap-2">
              <svg className="w-4 h-4 text-functional-warning" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
              </svg>
              <span className="text-label-md text-text-secondary">
                All data is fetched in real-time. Investments are subject to market risks. Read all scheme documents carefully.
              </span>
            </div>
          </div>
        )}

        {/* Input Bar */}
        <InputBar
          onSend={sendMessage}
          disabled={isProcessing}
        />

        {/* Quick Action Chips */}
        {hasMessages && (
          <div className="w-full px-4 py-3 border-t border-border bg-surface-container-low">
            <div className="max-w-chat mx-auto flex justify-center gap-2 overflow-x-auto">
              <button
                onClick={() => sendMessage("Compare with Peer Funds")}
                className="whitespace-nowrap px-4 py-1.5 rounded-full bg-surface border border-border text-label-md text-text-primary hover:bg-surface-container transition-colors"
              >
                Compare with Peer Funds
              </button>
              <button
                onClick={() => sendMessage("Show Top 5 Holdings")}
                className="whitespace-nowrap px-4 py-1.5 rounded-full bg-surface border border-border text-label-md text-text-primary hover:bg-surface-container transition-colors"
              >
                Top 5 Holdings
              </button>
              <button
                onClick={() => sendMessage("Show Risk Analysis")}
                className="whitespace-nowrap px-4 py-1.5 rounded-full bg-surface border border-border text-label-md text-text-primary hover:bg-surface-container transition-colors"
              >
                Risk Analysis
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default App;
