import json
import uuid
from datetime import datetime, timezone

from langchain_core.messages import AIMessage, HumanMessage
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import ChatMessage, ChatSession
from app.schemas.chat import SourceCitation
from app.schemas.sessions import MessageInfo, SessionInfo, SessionListResponse, SessionMessagesResponse


async def get_or_create_session(db: AsyncSession, session_id: str | None) -> str:
    if session_id:
        result = await db.execute(select(ChatSession).where(ChatSession.id == session_id))
        if result.scalar_one_or_none():
            return session_id

    new_session = ChatSession(id=str(uuid.uuid4()), title=None)
    db.add(new_session)
    await db.commit()
    return new_session.id


async def save_message(
    db: AsyncSession,
    session_id: str,
    role: str,
    content: str,
    sources: list[SourceCitation] | None = None,
) -> None:
    sources_json = json.dumps([s.model_dump() for s in sources]) if sources else None
    msg = ChatMessage(
        session_id=session_id,
        role=role,
        content=content,
        sources_json=sources_json,
    )
    db.add(msg)
    session = await db.get(ChatSession, session_id)
    if session:
        session.updated_at = datetime.now(timezone.utc)
        if not session.title and role == "user":
            session.title = content[:80]
    await db.commit()


async def get_history_messages(db: AsyncSession, session_id: str) -> list:
    result = await db.execute(
        select(ChatMessage).where(ChatMessage.session_id == session_id).order_by(ChatMessage.created_at)
    )
    messages = result.scalars().all()
    history = []
    for msg in messages:
        if msg.role == "user":
            history.append(HumanMessage(content=msg.content))
        elif msg.role == "assistant":
            history.append(AIMessage(content=msg.content))
    return history


async def list_sessions(db: AsyncSession) -> SessionListResponse:
    result = await db.execute(select(ChatSession).order_by(ChatSession.updated_at.desc()))
    sessions = result.scalars().all()
    return SessionListResponse(
        sessions=[
            SessionInfo(
                id=s.id,
                title=s.title,
                created_at=s.created_at,
                updated_at=s.updated_at,
            )
            for s in sessions
        ]
    )


async def get_session_messages(db: AsyncSession, session_id: str) -> SessionMessagesResponse:
    result = await db.execute(
        select(ChatMessage).where(ChatMessage.session_id == session_id).order_by(ChatMessage.created_at)
    )
    messages = result.scalars().all()
    items = []
    for m in messages:
        sources = []
        if m.sources_json:
            sources = [SourceCitation(**s) for s in json.loads(m.sources_json)]
        items.append(
            MessageInfo(
                id=m.id,
                role=m.role,
                content=m.content,
                sources=sources,
                created_at=m.created_at,
            )
        )
    return SessionMessagesResponse(session_id=session_id, messages=items)
