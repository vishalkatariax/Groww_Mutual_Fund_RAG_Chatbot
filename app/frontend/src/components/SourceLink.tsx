import React from 'react';

interface SourceLinkProps {
  url: string;
}

const SourceLink: React.FC<SourceLinkProps> = ({ url }) => {
  const displayUrl = url.replace(/^https?:\/\//, '').replace(/\/$/, '');
  
  return (
    <div className="mt-2 flex items-start gap-1.5 text-label-md">
      <svg className="w-3.5 h-3.5 text-functional-success flex-shrink-0 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
        <path fillRule="evenodd" d="M12.586 4.586a2 2 0 112.828 2.828l-3 3a2 2 0 01-2.828 0 1 1 0 00-1.414 1.414 4 4 0 005.656 0l3-3a4 4 0 00-5.656-5.656l-1.5 1.5a1 1 0 101.414 1.414l1.5-1.5zm-5 5a2 2 0 012.828 0 1 1 0 101.414-1.414 4 4 0 00-5.656 0l-3 3a4 4 0 105.656 5.656l1.5-1.5a1 1 0 10-1.414-1.414l-1.5 1.5a2 2 0 11-2.828-2.828l3-3z" clipRule="evenodd" />
      </svg>
      <a
        href={url}
        target="_blank"
        rel="noopener noreferrer"
        className="text-functional-success hover:text-tertiary hover:underline break-all"
      >
        Source: {displayUrl}
      </a>
    </div>
  );
};

export default SourceLink;
