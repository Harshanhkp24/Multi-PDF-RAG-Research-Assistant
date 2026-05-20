from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.schemas.sessions import SessionListResponse, SessionMessagesResponse
from app.services.session_service import get_session_messages, list_sessions

router = APIRouter(prefix="/api/sessions", tags=["sessions"])


@router.get("", response_model=SessionListResponse)
async def get_sessions(db: AsyncSession = Depends(get_db)) -> SessionListResponse:
    return await list_sessions(db)


@router.get("/{session_id}/messages", response_model=SessionMessagesResponse)
async def get_messages(
    session_id: str,
    db: AsyncSession = Depends(get_db),
) -> SessionMessagesResponse:
    return await get_session_messages(db, session_id)
