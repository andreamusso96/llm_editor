import React, { useState, useEffect, useMemo } from 'react';
import type { RichSegment } from '../types/api';
import { HiChevronLeft, HiChevronRight, HiX } from 'react-icons/hi';

// TooltipPosition type can remain as is or be moved to types/ui.ts if you prefer
export type TooltipPosition = {
  top: number;
  left: number;
};

interface IssueTooltipProps {
  segmentWithIssues: RichSegment | null;
  position: TooltipPosition | null;
  onClose: () => void;
  promptIdsSelectedForResultDisplay: string[];
}

// Renamed from ErrorDisplayTooltip to IssueTooltip
function IssueTooltip({ segmentWithIssues, position, onClose, promptIdsSelectedForResultDisplay }: IssueTooltipProps): React.ReactElement | null {
  const [currentIssueIndex, setCurrentIssueIndex] = useState(0);

  useEffect(() => {
    // Reset to the first issue when the segment changes
    setCurrentIssueIndex(0);
  }, [segmentWithIssues, promptIdsSelectedForResultDisplay]);

  const issuesToDisplay = useMemo(() => {
    if (!segmentWithIssues || !segmentWithIssues.issues) {
      return [];
    }
    return segmentWithIssues.issues.filter(issue => promptIdsSelectedForResultDisplay.includes(issue.prompt_id_ref));
  }, [segmentWithIssues, promptIdsSelectedForResultDisplay]);

  // Return if tooltip should not be displayed
  // Check segmentWithIssues and segmentWithIssues.issues
  if (!segmentWithIssues || !segmentWithIssues.issues || segmentWithIssues.issues.length === 0 || !position) {
    return null;
  }

  // Use RichSegmentIssue[] and segment.issues
  const totalIssues = issuesToDisplay.length;
  const currentIssue = issuesToDisplay[currentIssueIndex];

  const handleNextIssue = () => {
    setCurrentIssueIndex((prevIndex) => (prevIndex + 1) % totalIssues);
  };

  const handlePrevIssue = () => {
    setCurrentIssueIndex((prevIndex) => (prevIndex - 1 + totalIssues) % totalIssues);
  };

  return (
    <div
      className="fixed bg-zinc-700 text-white p-4 rounded-lg shadow-xl z-50 w-80 max-w-md"
      style={{ top: `${position.top + 15}px`, left: `${position.left + 15}px` }}
      role="tooltip"
      aria-live="polite"
    >
      {/* Header Section: Title, Navigation, and Close Button */}
      <div className="flex justify-between items-center mb-3">
        <h3 className="text-lg text-blue-400">
          {/* Updated title from "Mistake" to "Issue/Suggestion" */}
          {totalIssues} Suggestion{totalIssues > 1 ? 's' : ''}
          {totalIssues > 1 && ` (${currentIssueIndex + 1}/${totalIssues})`}
        </h3>
        <div className="flex items-center space-x-2">
          {totalIssues > 1 && (
            <>
              <button
                onClick={handlePrevIssue}
                className="p-1 rounded-full hover:bg-slate-700 focus:outline-none focus:ring-2 focus:ring-sky-500"
              >
                <HiChevronLeft size={20} />
              </button>
              <button
                onClick={handleNextIssue}
                className="p-1 rounded-full hover:bg-slate-700 focus:outline-none focus:ring-2 focus:ring-sky-500"
              >
                <HiChevronRight size={20} />
              </button>
            </>
          )}
          <button
            onClick={onClose}
            className="p-1 rounded-full hover:bg-slate-700 focus:outline-none focus:ring-2 focus:ring-sky-500"
          >
            <HiX size={20} />
          </button>
        </div>
      </div>

      {/* Issue Details - Mapped from RichSegmentIssue fields */}
      <div className="space-y-3 text-sm">
        {/* Display prompt_id_ref if you want */}
        {currentIssue.prompt_id_ref && (
          <div>
            <span className="font-semibold text-gray-400">Source Prompt:</span>
            <p className="mt-0.5 text-gray-300">{currentIssue.prompt_id_ref}</p>
          </div>
        )}
        <div>
          <span className="font-semibold text-blue-400">Issue:</span>
          {/* Using currentIssue.issue for explanation */}
          <p className="mt-0.5">{currentIssue.issue}</p>
        </div>
        <div>
          <span className="font-semibold text-blue-400">Suggested Revision:</span>
          {/* Using currentIssue.revision for corrected snippet */}
          <p className="mt-0.5">
            {currentIssue.revision}
          </p>
        </div>
      </div>
    </div>
  );
}

export default IssueTooltip;
// export type { TooltipPosition }; // TooltipPosition is already exported above