# LLM Editor

A web-based text correction tool that uses LLM prompts to identify and fix issues in text documents. 

## Installation

1. Install docker desktop https://www.docker.com/
2. Clone the repository
```
git clone https://github.com/andreamusso96/llm_editor.git
```
3. Enter the repository
```
cd llm_editor
```
4. Copy the .env.example file into a .env file
```
cp .env.example .env
```
5. Get a gemini api key https://aistudio.google.com/api-keys and paste in the `.env` file where it says `GOOGLE_API_KEY=YOUR_API_KEY` 

6. Start up the containers using docker compose
```
docker compose up --build
```
7. Paste this URL into your browser http://localhost:5173. You should see a frotend with "Writing Editor" as a title

## Usage

1. **Prepare Your Text**: Place your text file in `frontend/public/text.txt`
2. **Select Prompts**: Choose which correction prompts you want to run from the available options
3. **Run Corrections**: Click the "Run" button and wait for the processing to complete
4. **Review Results**: View the identified issues and suggested corrections

## Adding Custom Prompts

You can add you custom prompts. 
To add new prompts, create YAML files in the `backend/database_setup/prompts/` directory following this structure:

```yaml
- prompt_id_ref: your_prompt_name
  description: "Brief description of what this prompt does"
  input_granularity: paragraph  # or whole_text
  prompt: |
    Your prompt text here...
    Use {{ input_text }} to reference the input text
```

### Prompt Structure

- **prompt_id_ref**: A unique string identifier for your prompt
- **description**: A short description explaining what the prompt does
- **input_granularity**: 
  - `paragraph`: Runs the prompt on each paragraph separately
  - `whole_text`: Runs the prompt on the entire text at once
- **prompt**: Your actual prompt text. Use `{{ input_text }}` to reference the input text

### Expected Output Format

Your prompt must return a JSON response in this format:

```json
{
  "issues": [
    {
      "snippet": "The exact text with the issue",
      "sentence_context": "The full sentence containing the issue",
      "issue": "Description of the problem",
      "revision": "The corrected version"
    }
  ]
}
```

### Example Prompt

Here's an example of a grammar correction prompt:

```yaml
  - prompt_id_ref: copy_editor_corrections
    description: "Check punctuation, grammar, and spelling errors."
    input_granularity: paragraph
    prompt: |
        ## ROLE:
        You are an expert copy editor for scientific writing, tasked with reviewing a PhD thesis in cryptography.

        ## TASK:
        Analyze the provided TEXT to identify and correct all objective errors. Your goal is to ensure the text is grammatically perfect and free of spelling and punctuation mistakes.

        ## INSTRUCTIONS:
        1.  Carefully read the provided TEXT.
        2.  Identify any sections, sentences, or phrases that exhibit the following issues:
            * Grammar errors (e.g., subject-verb agreement, tense, word order).
            * Spelling errors.
            * Punctuation errors.
        3.  For each identified issue, create a JSON object. The final output should be a single JSON object containing a list named "issues".
        4.  Each object in the list must contain the following keys:
            * `snippet`: The exact part of the TEXT with the issue. Keep it as short as possible.
            * `sentence_context`: The full sentence containing the snippet.
            * `issue`: A concise explanation of the error (e.g., "Spelling error", "Incorrect comma usage").
            * `revision`: The corrected version of the snippet.

        ## TEXT:
        {{ input_text }}
```

## Project Structure

```
llm_editor/
├── backend/
│   ├── database_setup/prompts/  # Custom prompts go here
│   ├── src/
│   │   ├── api.py              # FastAPI endpoints
│   │   ├── services/           # Business logic
│   │   └── schemas/            # Pydantic models
│   └── requirements.txt
├── frontend/
│   ├── public/text.txt         # Your text file goes here
│   ├── src/
│   │   ├── components/         # React components
│   │   └── services/           # API calls
│   └── package.json
└── README.md
```