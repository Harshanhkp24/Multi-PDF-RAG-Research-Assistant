from datetime import datetime

from pydantic import BaseModel

from app.schemas.chat import SourceCitation


class MessageInfo(BaseModel):
    id: str
    role: str
    content: str
    sources: list[SourceCitation] = []
    created_at: datetime


class SessionInfo(BaseModel):
    id: str
    title: str | None
    created_at: datetime
    updated_at: datetime


class SessionListResponse(BaseModel):
    sessions: list[SessionInfo]


class SessionMessagesResponse(BaseModel):
    session_id: str
    messages: list[MessageInfo]
