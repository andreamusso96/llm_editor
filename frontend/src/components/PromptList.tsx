import type { Prompt } from '../types/api';

interface PromptsListProps {
    availablePrompts: Prompt[];
    selectedPromptIds: string[];
    onSelectedPromptIdsChange: (selectedIds: string[]) => void;
    listTitle?: string;
  }

const PromptsList: React.FC<PromptsListProps> = ({ availablePrompts, selectedPromptIds, onSelectedPromptIdsChange, listTitle }) => {
  const handleCheckboxChange = (promptIdRef: string) => {
    const newSelectedPromptIds = selectedPromptIds.includes(promptIdRef)
      ? selectedPromptIds.filter(id => id !== promptIdRef)
      : [...selectedPromptIds, promptIdRef];
    onSelectedPromptIdsChange(newSelectedPromptIds);
  };

  if (!availablePrompts) {
    return <div className="text-gray-500">Loading prompts data...</div>; // Or handle as error
  }

  if (availablePrompts.length === 0) {
    return <div className="text-gray-500">No prompts available.</div>;
  }

  return (
    <div>
      {listTitle && <h3 className="text-md font-semibold mb-2 text-white">{listTitle}</h3>}
      <div className="flex flex-wrap gap-3">
        {availablePrompts.map((prompt) => (
          <label
            key={prompt.prompt_id_ref}
            className="flex items-center text-white space-x-2 p-3 hover:bg-zinc-800 rounded-lg cursor-pointer transition-colors shadow-sm"
          >
            <input
              type="checkbox"
              className="form-checkbox h-5 w-5 text-blue-100 border-gray-300 rounded focus:ring-blue-500 focus:ring-offset-0"
              checked={selectedPromptIds.includes(prompt.prompt_id_ref)}
              onChange={() => handleCheckboxChange(prompt.prompt_id_ref)}
            />
            <span className="text-white select-none">
              {prompt.prompt_description || prompt.prompt_id_ref}
            </span>
          </label>
        ))}
      </div>
    </div>
  );
};

export default PromptsList;