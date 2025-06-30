from pydantic import BaseModel
from typing import List, Optional

class Prompt(BaseModel):
    prompt_id_ref: str
    prompt_description: Optional[str] = None

class PromptList(BaseModel):
    prompts: List[Prompt]

class CorrectionCreateRequest(BaseModel):
    text_content: str
    prompt_id_refs: List[str]

class CorrectionCreateResponse(BaseModel):
    correction_id: int

class CorrectionStatusResponse(BaseModel):
    correction_id: int
    status: str
    progress: float

class RichSegmentIssue(BaseModel):
    prompt_id_ref: str
    issue: str
    revision: str

class RichSegment(BaseModel):
    text: str
    start_char: int
    end_char: int
    issues: List[RichSegmentIssue]

    def __lt__(self, other):
        return self.start_char < other.start_char

class CorrectionResultResponse(BaseModel):
    correction_id: int
    original_text: str
    status: str
    rich_segments: List[RichSegment] | None = None