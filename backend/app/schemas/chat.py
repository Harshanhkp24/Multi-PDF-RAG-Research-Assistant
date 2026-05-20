from pydantic import BaseModel, Field


class SourceCitation(BaseModel):
    document_id: str
    filename: str
    page: int
    snippet: str
    score: float | None = None


class ChatRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=4000)
    session_id: str | None = None
    document_ids: list[str] | None = None


class ChatResponse(BaseModel):
    answer: str
    sources: list[SourceCitation]
    session_id: str
