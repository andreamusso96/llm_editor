# LLM Editor

A web-based text correction tool that uses LLM prompts to identify and fix issues in text documents. The application consists of a React frontend and a FastAPI backend that processes text through configurable prompts.

## Features

- **Text Correction**: Upload text and run various correction prompts
- **Configurable Prompts**: Add custom prompts for different types of text analysis
- **Real-time Processing**: See corrections as they're processed
- **Multiple Granularities**: Process text by paragraph or as a whole document

## Prerequisites

- Python 3.8+
- Node.js 18+
- npm or yarn

## Installation

### Backend Setup

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Create a virtual environment (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Frontend Setup

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install Node.js dependencies:
   ```bash
   npm install
   ```

## Running the Application

### Start the Backend

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Activate your virtual environment (if using one):
   ```bash
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Start the FastAPI server:
   ```bash
   uvicorn main:app --reload
   ```

The backend will be available at `http://localhost:8000`

### Start the Frontend

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Start the development server:
   ```bash
   npm run dev
   ```

The frontend will be available at `http://localhost:5173`

## Usage

1. **Prepare Your Text**: Place your text file in `frontend/public/text.txt`
2. **Select Prompts**: Choose which correction prompts you want to run from the available options
3. **Run Corrections**: Click the "Run" button and wait for the processing to complete
4. **Review Results**: View the identified issues and suggested corrections

## Adding Custom Prompts

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
- prompt_id_ref: grammar_check
  description: "Check for grammar and punctuation errors"
  input_granularity: paragraph
  prompt: |
    ## ROLE:
    You are an expert copy editor.

    ## TASK:
    Identify and correct grammar, spelling, and punctuation errors in the provided text.

    ## INSTRUCTIONS:
    1. Read the provided TEXT carefully
    2. Identify any grammar, spelling, or punctuation errors
    3. Return a JSON object with an "issues" list
    4. Each issue should contain: snippet, sentence_context, issue, and revision

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

## API Endpoints

- `POST /api/correct`: Process text with selected prompts
- `GET /api/prompts`: Get available prompts

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

[Add your license information here]
