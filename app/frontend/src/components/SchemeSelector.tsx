import React, { useState, useEffect } from 'react';
import { chatApi } from '../services/api';
import type { SchemeInfo } from '../types';

interface SchemeSelectorProps {
  onSchemeSelect: (scheme: string | null) => void;
  selectedScheme: string | null;
}

const SchemeSelector: React.FC<SchemeSelectorProps> = ({ onSchemeSelect, selectedScheme }) => {
  const [schemes, setSchemes] = useState<SchemeInfo[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isOpen, setIsOpen] = useState(false);

  useEffect(() => {
    loadSchemes();
  }, []);

  const loadSchemes = async () => {
    try {
      const response = await chatApi.getSchemes();
      setSchemes(response.schemes);
    } catch (error) {
      console.error('Failed to load schemes:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSelect = (scheme: string | null) => {
    onSchemeSelect(scheme);
    setIsOpen(false);
  };

  return (
    <div className="relative">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center gap-2 px-4 py-2 bg-surface-container border border-border rounded-lg hover:bg-surface-container-high transition-colors text-label-md text-text-primary"
      >
        <svg className="w-4 h-4 text-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
        </svg>
        <span>{selectedScheme || 'All Schemes'}</span>
      </button>

      {isOpen && (
        <div className="absolute top-full left-0 mt-2 w-64 bg-surface-container border border-border rounded-lg shadow-xl z-50 max-h-64 overflow-y-auto">
          <button
            onClick={() => handleSelect(null)}
            className={`w-full px-4 py-2 text-left text-label-md hover:bg-surface-container-high transition-colors ${
              !selectedScheme ? 'bg-primary-container/10 text-primary' : 'text-text-secondary'
            }`}
          >
            All Schemes
          </button>
          {isLoading ? (
            <div className="px-4 py-3 text-label-md text-text-secondary">Loading schemes...</div>
          ) : (
            schemes.map((scheme, idx) => (
              <button
                key={idx}
                onClick={() => handleSelect(scheme.name)}
                className={`w-full px-4 py-2 text-left text-label-md hover:bg-surface-container-high transition-colors border-t border-border ${
                  selectedScheme === scheme.name ? 'bg-primary-container/10 text-primary' : 'text-text-secondary'
                }`}
              >
                <div className="font-medium text-text-primary">{scheme.name}</div>
                <div className="text-xs text-text-secondary">{scheme.category}</div>
              </button>
            ))
          )}
        </div>
      )}
    </div>
  );
};

export default SchemeSelector;
