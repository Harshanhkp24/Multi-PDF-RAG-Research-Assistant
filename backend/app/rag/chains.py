from langchain_core.documents import Document
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

from app.rag.llm import get_chat_llm
from app.rag.vectorstore import get_retriever
from app.schemas.chat import SourceCitation

RAG_SYSTEM_PROMPT = """You are a research assistant that answers questions based ONLY on the provided context from uploaded PDF documents.

Rules:
- Answer using only the context below. If the context does not contain enough information, say "I don't have enough information in the uploaded documents to answer that."
- Be concise and accurate.
- When referencing facts, mention which source (filename and page) they come from when possible.
- Do not make up information not present in the context.

Context:
{context}
"""


def _format_docs(docs: list[Document]) -> str:
    parts = []
    for doc in docs:
        meta = doc.metadata
        filename = meta.get("filename", "unknown")
        page = meta.get("page", "?")
        parts.append(f"[{filename}, page {page}]\n{doc.page_content}")
    return "\n\n---\n\n".join(parts)


def docs_to_sources(docs: list[Document]) -> list[SourceCitation]:
    sources = []
    for doc in docs:
        meta = doc.metadata
        snippet = doc.page_content[:300] + ("..." if len(doc.page_content) > 300 else "")
        sources.append(
            SourceCitation(
                document_id=meta.get("document_id", ""),
                filename=meta.get("filename", "unknown"),
                page=int(meta.get("page", 0)),
                snippet=snippet,
            )
        )
    return sources


def build_rag_chain(document_ids: list[str] | None = None):
    retriever = get_retriever(document_ids)
    llm = get_chat_llm(streaming=False)

    def retrieve_and_format(question: str) -> dict:
        docs = retriever.invoke(question)
        return {
            "context": _format_docs(docs),
            "source_docs": docs,
            "question": question,
        }

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", RAG_SYSTEM_PROMPT),
            MessagesPlaceholder("history"),
            ("human", "{question}"),
        ]
    )

    def run_with_history(inputs: dict) -> dict:
        retrieved = retrieve_and_format(inputs["question"])
        history = inputs.get("history", [])
        messages = prompt.format_messages(
            context=retrieved["context"],
            history=history,
            question=inputs["question"],
        )
        response = llm.invoke(messages)
        answer = response.content if isinstance(response, AIMessage) else str(response)
        return {
            "answer": answer,
            "sources": docs_to_sources(retrieved["source_docs"]),
        }

    return run_with_history


def build_streaming_rag(document_ids: list[str] | None = None):
    """Returns retriever docs + llm for streaming path."""
    retriever = get_retriever(document_ids)
    llm = get_chat_llm(streaming=True)
    return retriever, llm, RAG_SYSTEM_PROMPT
