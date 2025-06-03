// src/components/ProgressBar.tsx
import React from 'react';

interface ProgressBarProps {
  progress: number; // A value between 0 and 1
  statusText?: string; // Optional text to display, e.g., current status
}

const ProgressBar: React.FC<ProgressBarProps> = ({ progress, statusText }) => {
  const percentage = Math.max(0, Math.min(100, Math.round(progress * 100)));

  return (
    <div>
      {statusText && (
        <p className="text-sm text-gray-600 mb-1 text-center">
          {statusText}
        </p>
      )}
      <div className="w-full bg-gray-200 rounded-full h-4 dark:bg-gray-700 overflow-hidden">
        <div
          className="bg-blue-600 h-4 rounded-full text-xs font-medium text-blue-100 text-center p-0.5 leading-none transition-all duration-300 ease-out"
          style={{ width: `${percentage}%` }}
          role="progressbar"
          aria-valuenow={percentage}
          aria-valuemin={0}
          aria-valuemax={100}
        >
          {percentage}%
        </div>
      </div>
    </div>
  );
};

export default ProgressBar;