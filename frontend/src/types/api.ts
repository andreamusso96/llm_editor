// src/types/api.ts
export interface Prompt {
    prompt_id_ref: string;
    prompt_description?: string;
  }
  
  export interface PromptList {
    prompts: Prompt[];
  }
  
  export interface CorrectionCreateRequest {
    text_content: string;
    prompt_id_refs: string[];
  }
  
  export interface CorrectionCreateResponse {
    correction_id: number;
  }
  
  export interface CorrectionStatusResponse {
    correction_id: number;
    status: string;
    progress: number; // Assuming float is 0.0 to 1.0
  }
  
  export interface RichSegmentIssue {
    prompt_id_ref: string;
    issue: string;
    revision: string;
  }
  
  export interface RichSegment {
    text: string;
    start_char: number;
    end_char: number;
    issues: RichSegmentIssue[];
  }
  
  export interface CorrectionResultResponse {
    correction_id: number;
    original_text: string;
    status: string;
    rich_segments?: RichSegment[];
  }