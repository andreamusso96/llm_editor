import React, { useMemo } from "react";
import type { RichSegment } from "../types/api";

interface RichSegmentDisplayProps {
    segment: RichSegment;
    onSegmentClick: (segment: RichSegment, event: React.MouseEvent<HTMLSpanElement>) => void;
    promptIdsSelectedForResultDisplay: string[];
    isActive: boolean;
}


// Inside RichSegmentDisplay.jsx (simplified)
const RichSegmentDisplay = ({ segment, onSegmentClick, isActive , promptIdsSelectedForResultDisplay}: RichSegmentDisplayProps) => {
    const hasVisibleIssues = useMemo(() => {
        if (!segment.issues || segment.issues.length === 0) {
          return false;
        }
        if (promptIdsSelectedForResultDisplay.length === 0 && segment.issues.length > 0) {
            return false;
        }
        return segment.issues.some(issue => promptIdsSelectedForResultDisplay.includes(issue.prompt_id_ref));
      }, [segment.issues, promptIdsSelectedForResultDisplay]);
  
    const handleClick = (event: React.MouseEvent<HTMLSpanElement>) => {
        if (hasVisibleIssues) {
          onSegmentClick(segment, event);
        }
    };

  
    return (
        <span
        onClick={handleClick}
        // Apply cursor-pointer only if there are visible issues to interact with
        className={`rounded transition-colors duration-150 ${
          hasVisibleIssues ? 'underline decoration-red-500 decoration-wavy cursor-pointer' : ''
        } ${
          isActive
            ? 'bg-sky-100 dark:bg-sky-700'
            : hasVisibleIssues
            ? 'hover:bg-red-100 dark:hover:bg-red-800' // Hover for segments with visible issues
            : 'hover:bg-gray-100 dark:hover:bg-slate-700' // Default hover
        }`}
      >
        {segment.text}
      </span>
    );
  };

export default RichSegmentDisplay;