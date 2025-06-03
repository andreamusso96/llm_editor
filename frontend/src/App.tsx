import { useEffect, useState } from 'react'
import PromptsList from './components/PromptList'
import { getCorrectionStatus, submitCorrection, getCorrectionResult, fetchPrompts} from './services/correctionService'
import type { CorrectionCreateResponse, CorrectionStatusResponse, CorrectionResultResponse, Prompt } from './types/api'
import ProgressBar from './components/ProgressBar';
import ResultsDisplay from './components/ResultDisplay';


const fetchTextFileContent = async (): Promise<string> => {
  const response = await fetch('/text.txt'); 
  if (!response.ok) {
    throw new Error(`Failed to fetch text.txt: ${response.statusText}`);
  }
  const textContent = await response.text();
  return textContent;
};

const POLLING_TERMINAL_STATUSES = ['completed', 'failed', 'error'];
const SUCCESS_TERMINAL_STATUSES = ['completed'];

function App() {
  const [availablePrompts, setAvailablePrompts] = useState<Prompt[]>([]);


  const [promptIdsSelectedForCorrection, setPromptIdsSelectedForCorrection] = useState<string[]>([]);
  const [promptIdsSelectedForResultDisplay, setPromptIdsSelectedForResultDisplay] = useState<string[]>([]);
  
  const [correctionId, setCorrectionId] = useState<number | null>(null);
  const [isHandlingRunCorrection, setIsHandlingRunCorrection] = useState<boolean>(false); 
  const [currentCorrectionStatus, setCurrentCorrectionStatus] = useState<string | null>(null);
  const [currentCorrectionProgress, setCurrentCorrectionProgress] = useState<number>(0);
  const [correctionResults, setCorrectionResults] = useState<CorrectionResultResponse | null>(null);
  const [isLoadingCorrectionResults, setIsLoadingCorrectionResults] = useState<boolean>(false);


  //
  useEffect(() => {
    const loadPrompts = async () => {
      try {
        const promptData = await fetchPrompts();
        setAvailablePrompts(promptData.prompts);
      } catch (err) {
        console.error(err);
      }
    };
    loadPrompts();
  }, []);



  const handlePromptIdsSelectedForCorrectionChange = (newSelectedPromptIds: string[]) => {
    setPromptIdsSelectedForCorrection(newSelectedPromptIds);
    setCorrectionId(null);
    setCurrentCorrectionStatus(null);
    setCurrentCorrectionProgress(0);
  };

  const handlePromptIdsSelectedForResultDisplayChange = (newSelectedPromptIds: string[]) => {
    setPromptIdsSelectedForResultDisplay(newSelectedPromptIds);
  };

  const handleRunCorrection = async () => {
    if (promptIdsSelectedForCorrection.length === 0) {
      alert("Please select at least one prompt.");
      return;
    }

    setIsHandlingRunCorrection(true);
    setCorrectionId(null);
    setCurrentCorrectionStatus("submitting");
    setCurrentCorrectionProgress(0);
    setCorrectionResults(null);

    try {
      const currentTextContent = await fetchTextFileContent();
      console.log("Running correction with freshly fetched text:");
      console.log("Text from text.txt:", currentTextContent);
      console.log("Selected Prompt IDs:", promptIdsSelectedForCorrection);

      const correction: CorrectionCreateResponse = await submitCorrection(currentTextContent, promptIdsSelectedForCorrection);

      setCorrectionId(correction.correction_id);
      setCurrentCorrectionStatus("submitted");
      console.log("Text submitted for correction. Correction ID:", correction.correction_id);

    } catch (error) {
      console.error("Error fetching text file content:", error);
      alert("Failed to fetch text file content. Please try again.");
      setCorrectionId(null);
      setCurrentCorrectionStatus(null);
      setCurrentCorrectionProgress(0);
    } finally {
      setIsHandlingRunCorrection(false);
    }
  };

  useEffect(() => {
    if (correctionId === null || currentCorrectionStatus === null) {
      return; 
    }
    if (SUCCESS_TERMINAL_STATUSES.includes(currentCorrectionStatus) && !correctionResults && !isLoadingCorrectionResults) {
      
      const fetchResults = async () => {
        console.log(`Fetching results for correction ID: ${correctionId}`);
        setIsLoadingCorrectionResults(true);
        try {
          const results: CorrectionResultResponse = await getCorrectionResult(correctionId);
          setCorrectionResults(results);
          setPromptIdsSelectedForResultDisplay(promptIdsSelectedForCorrection);
          console.log(`Results fetched for correction ID: ${correctionId}`);
        } catch (error) {
          console.error(`Error fetching results for correction ID ${correctionId}:`, error);
        } finally {
          setIsLoadingCorrectionResults(false);
        }
      };

      fetchResults();
    }
  
    if (!POLLING_TERMINAL_STATUSES.includes(currentCorrectionStatus)) {
      const intervalId = setInterval(async () => {
        console.log(`Polling for status of correction ID: ${correctionId}, current status: ${currentCorrectionProgress}`);
        try {
          const statusResponse: CorrectionStatusResponse = await getCorrectionStatus(correctionId);
          setCurrentCorrectionStatus(statusResponse.status);
          setCurrentCorrectionProgress(statusResponse.progress);

          if (POLLING_TERMINAL_STATUSES.includes(statusResponse.status.toLowerCase())) {
            console.log(`Reached terminal status: ${statusResponse.status}. Stopping polling.`);
            clearInterval(intervalId); 
            // Optionally: trigger fetching results here if status is 'completed' or 'succeeded'
          }
        } catch (error) {
          console.error(`Error polling for status (ID: ${correctionId}):`, error);
          setCurrentCorrectionStatus('polling_error');
          clearInterval(intervalId); 
        }
      }, 3000); // Poll every 3 seconds

      return () => clearInterval(intervalId);
    }

  }, [correctionId, currentCorrectionStatus, correctionResults, isLoadingCorrectionResults]);

  return (
    <>
      <div className="min-h-screen bg-zinc-900 flex flex-col items-center justify-center p-4 text-white">
      <header className="mb-8">
        <h1 className="text-4xl font-bold text-center text-blue-600">Writing Editor</h1>
      </header>
      <div className="max-w-4xl mx-auto">
      {/* Prompts section */}
      <section id="prompts-section" className="mb-6 p-4 border rounded-lg shadow-sm">
        <PromptsList 
          availablePrompts={availablePrompts}
          selectedPromptIds={promptIdsSelectedForCorrection} 
          onSelectedPromptIdsChange={handlePromptIdsSelectedForCorrectionChange} 
          listTitle="Select correction prompts"
        />
      </section>

      {/* Run Button Section */}
      <section id="run-section" className="mb-6 text-center">
        <button
          onClick={handleRunCorrection}
          className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-6 rounded-lg text-lg shadow active:bg-blue-800 transition duration-150 ease-in-out disabled:bg-zinc-800 disabled:cursor-not-allowed"
          disabled={promptIdsSelectedForCorrection.length === 0 || isHandlingRunCorrection}
        >
          {isHandlingRunCorrection ? "Running..." : "Run Correction"}
        </button>
      </section>

     {/* Progress Section - Updated to use ProgressBar component */}
     <section id="progress-section" className="mb-6 p-4 border rounded-lg shadow-sm">
        {correctionId !== null ? (
          <div>
            <p className="text-sm text-gray-700 mb-2 text-center">
              Job ID: <span className="font-medium">{correctionId}</span>
            </p>
            <ProgressBar progress={currentCorrectionProgress} statusText={currentCorrectionStatus || undefined} />
            {isLoadingCorrectionResults && <p className="text-sm text-blue-500 text-center mt-2">Loading results...</p>}
          </div>
        ) : (
          <div className="p-4 bg-gray-100 rounded text-gray-500">
            [Submit a job to see progress]
          </div>
        )}
      </section>

    {/* Results Section */}
    <section id="results-section" className="p-4 border rounded-lg shadow-sm">
        <ResultsDisplay results={correctionResults} promptIdsSelectedForResultDisplay={promptIdsSelectedForResultDisplay} />
      </section>

      {/* +++ New section for the filter PromptList +++ */}
      <section id="filter-prompts-section" className="mt-8 p-4 border rounded-lg shadow-sm">
        {availablePrompts.length > 0 && (
          <PromptsList
            availablePrompts={availablePrompts}
            selectedPromptIds={promptIdsSelectedForResultDisplay}
            onSelectedPromptIdsChange={handlePromptIdsSelectedForResultDisplayChange}
            listTitle="Show corrections from"
          />
        )}
      </section>
      </div>
      </div>
    </>
  )
}

export default App
