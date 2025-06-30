from pydantic import BaseModel, Field
from typing import List as PyList


class SnippetIssueRevision(BaseModel):
    snippet: str = Field(description="The snippet of TEXT that contains the issue")
    sentence_context: str = Field(description="The full sentence in the TEXT that contains the issue")
    issue: str = Field(description="The issue that is present in the snippet")
    revision: str = Field(description="The revision that corrects the issue")

class SnippetIssuesRevisionList(BaseModel):
    issues: PyList[SnippetIssueRevision] = Field(description="A list of issues")