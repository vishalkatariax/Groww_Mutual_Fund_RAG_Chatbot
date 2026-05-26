import React from 'react';

const WelcomeSection: React.FC = () => {
  const availableSchemes = [
    'HDFC Mid-Cap Fund',
    'HDFC ELSS Tax Saver Fund',
    'HDFC Large Cap Fund',
    'HDFC Equity Fund',
    'HDFC Focused Fund'
  ];

  return (
    <div className="flex-1 flex flex-col items-center justify-center px-4 py-12">
      <div className="mb-8 inline-flex items-center justify-center p-4 bg-primary-container/10 rounded-full">
        <svg className="w-12 h-12 text-primary-container" fill="currentColor" viewBox="0 0 20 20">
          <path fillRule="evenodd" d="M18 5v8a2 2 0 01-2 2h-5l-5 4v-4H4a2 2 0 01-2-2V5a2 2 0 012-2h12a2 2 0 012 2zM7 8H5v2h2V8zm2 0h2v2H9V8zm6 0h-2v2h2V8z" clipRule="evenodd" />
        </svg>
      </div>
      <h2 className="text-headline-lg text-text-primary mb-4 text-center">
        Hi! Ask me anything about HDFC Mutual Fund schemes on Groww.
      </h2>
      <p className="text-body-lg text-text-secondary max-w-lg mx-auto text-center mb-6">
        Get instant insights into NAV, holdings, risk profiles, and historical performance.
      </p>
      <div className="bg-surface-container-low/50 p-4 rounded-xl border border-border max-w-lg">
        <p className="text-label-md text-text-secondary text-center mb-3">Available schemes in database:</p>
        <div className="flex flex-wrap gap-2 justify-center">
          {availableSchemes.map((scheme, idx) => (
            <span key={idx} className="px-3 py-1 bg-primary-container/10 text-primary text-label-md rounded-full border border-primary-container/20">
              {scheme}
            </span>
          ))}
        </div>
      </div>
    </div>
  );
};

export default WelcomeSection;
