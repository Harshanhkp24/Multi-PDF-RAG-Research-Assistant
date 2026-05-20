import json
from collections.abc import AsyncGenerator

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from sqlalchemy.ext.asyncio import AsyncSession

from app.rag.chains import build_rag_chain, build_streaming_rag, docs_to_sources, _format_docs
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.session_service import get_history_messages, get_or_create_session, save_message


async def chat(request: ChatRequest, db: AsyncSession) -> ChatResponse:
    session_id = await get_or_create_session(db, request.session_id)
    history = await get_history_messages(db, session_id)

    await save_message(db, session_id, "user", request.question)

    chain = build_rag_chain(request.document_ids)
    result = chain({"question": request.question, "history": history})

    await save_message(db, session_id, "assistant", result["answer"], result["sources"])

    return ChatResponse(
        answer=result["answer"],
        sources=result["sources"],
        session_id=session_id,
    )


async def chat_stream(request: ChatRequest, db: AsyncSession) -> AsyncGenerator[str, None]:
    session_id = await get_or_create_session(db, request.session_id)
    history = await get_history_messages(db, session_id)

    await save_message(db, session_id, "user", request.question)

    retriever, llm, system_template = build_streaming_rag(request.document_ids)
    docs = retriever.invoke(request.question)
    sources = docs_to_sources(docs)
    context = _format_docs(docs)

    # Send sources first as SSE event
    yield f"event: sources\ndata: {json.dumps([s.model_dump() for s in sources])}\n\n"

    messages = [
        SystemMessage(content=system_template.format(context=context)),
        *history,
        HumanMessage(content=request.question),
    ]

    full_answer = ""
    async for chunk in llm.astream(messages):
        token = chunk.content if hasattr(chunk, "content") else str(chunk)
        if token:
            full_answer += token
            yield f"event: token\ndata: {json.dumps(token)}\n\n"

    await save_message(db, session_id, "assistant", full_answer, sources)
    yield f"event: done\ndata: {json.dumps({'session_id': session_id})}\n\n"
