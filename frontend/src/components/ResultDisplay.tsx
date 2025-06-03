// src/components/ResultsDisplay.tsx
import React, { useState } from 'react';
import type { CorrectionResultResponse, RichSegment } from '../types/api'; // Assuming RichSegment is also in types/api.ts
import RichSegmentDisplay from './RichSegmentDisplay'; // Assuming RichSegmentDisplay.tsx is in the same folder
import IssueTooltip from './IssueTooltip';
import type { TooltipPosition } from './IssueTooltip';

interface ResultsDisplayProps {
  results: CorrectionResultResponse | null;
  promptIdsSelectedForResultDisplay: string[];
}

const ResultsDisplay: React.FC<ResultsDisplayProps> = ({ results, promptIdsSelectedForResultDisplay }) => {
  const [activeSegmentForTooltip, setActiveSegmentForTooltip] = useState<RichSegment | null>(null);
  const [tooltipPosition, setTooltipPosition] = useState<TooltipPosition | null>(null);


  if (!results) {
    return (
      <div className="p-4 bg-gray-100 rounded text-gray-500">
        [Correction results will appear here once processed and fetched]
      </div>
    );
  }

  const handleSegmentClick = (segment: RichSegment, event: React.MouseEvent<HTMLSpanElement>) => {
    const hasIssuesSelectedForDisplay = segment.issues && segment.issues.length > 0 && segment.issues.some(issue => promptIdsSelectedForResultDisplay.includes(issue.prompt_id_ref));

    if (hasIssuesSelectedForDisplay) {
        if (segment.start_char === activeSegmentForTooltip?.start_char) {
        setActiveSegmentForTooltip(null);
        setTooltipPosition(null);
        } else {
        setActiveSegmentForTooltip(segment);
        setTooltipPosition({
            top: event.clientY,
            left: event.clientX,
        });
        console.log('Tooltip position:', tooltipPosition)
        }
   } else {
    setActiveSegmentForTooltip(null);
    setTooltipPosition(null);
   }
  };

  const handleCloseTooltip = () => {
    setActiveSegmentForTooltip(null);
    setTooltipPosition(null);
  }

  return (
    <div className="p-4 rounded-md bg-zinc-900 leading-relaxed">
        <h2 className="text-lg font-semibold text-white mb-6">Text with corrections:</h2>
        {results.rich_segments && results.rich_segments.length > 0 ? (
          <div className="p-4 rounded-md leading-relaxed whitespace-pre-line">
            {results.rich_segments.map((segment) => (
              <RichSegmentDisplay
                key={segment.start_char} // Assuming start_char is unique for keys
                segment={segment}
                onSegmentClick={handleSegmentClick}
                isActive={activeSegmentForTooltip?.start_char === segment.start_char}
                promptIdsSelectedForResultDisplay={promptIdsSelectedForResultDisplay}
              />
            ))}
          </div>
        ) : (
          <p className="text-gray-500">
            {results.rich_segments === null
              ? "[Rich segments data is null]"
              : "[No rich segments to display or segments array is empty]"
            }
          </p>
        )}
        <IssueTooltip
        segmentWithIssues={activeSegmentForTooltip}
        position={tooltipPosition}
        onClose={handleCloseTooltip}
        promptIdsSelectedForResultDisplay={promptIdsSelectedForResultDisplay}
        />
      </div>
  );
};

export default ResultsDisplay;