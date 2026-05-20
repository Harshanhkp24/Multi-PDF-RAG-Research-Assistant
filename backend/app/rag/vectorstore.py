from pathlib import Path

from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_core.vectorstores import VectorStore

from app.config import get_settings
from app.rag.embeddings import get_embeddings

_vectorstore: Chroma | None = None


def get_vectorstore() -> Chroma:
    global _vectorstore
    if _vectorstore is None:
        settings = get_settings()
        persist_dir = Path(settings.chroma_persist_dir)
        persist_dir.mkdir(parents=True, exist_ok=True)
        _vectorstore = Chroma(
            collection_name=settings.chroma_collection_name,
            embedding_function=get_embeddings(),
            persist_directory=str(persist_dir),
        )
    return _vectorstore


def add_documents(chunks: list[Document]) -> None:
    store = get_vectorstore()
    store.add_documents(chunks)


def delete_by_document_id(document_id: str) -> None:
    store = get_vectorstore()
    # Chroma filter delete
    try:
        store._collection.delete(where={"document_id": document_id})
    except Exception:
        pass


def get_retriever(
    document_ids: list[str] | None = None,
) -> VectorStore:
    settings = get_settings()
    store = get_vectorstore()
    search_kwargs: dict = {"k": settings.retrieval_top_k}
    if document_ids:
        search_kwargs["filter"] = {"document_id": {"$in": document_ids}}
    return store.as_retriever(search_type="similarity", search_kwargs=search_kwargs)


def list_indexed_documents() -> list[dict]:
    """Return unique documents from Chroma metadata."""
    store = get_vectorstore()
    try:
        result = store._collection.get(include=["metadatas"])
    except Exception:
        return []

    seen: dict[str, dict] = {}
    metadatas = result.get("metadatas") or []
    for meta in metadatas:
        if not meta:
            continue
        doc_id = meta.get("document_id")
        if not doc_id or doc_id in seen:
            if doc_id in seen:
                seen[doc_id]["chunk_count"] += 1
            continue
        seen[doc_id] = {
            "document_id": doc_id,
            "filename": meta.get("filename", "unknown"),
            "chunk_count": 1,
        }
    # Recount chunks properly
    chunk_counts: dict[str, int] = {}
    filenames: dict[str, str] = {}
    for meta in metadatas:
        if not meta:
            continue
        doc_id = meta.get("document_id")
        if doc_id:
            chunk_counts[doc_id] = chunk_counts.get(doc_id, 0) + 1
            filenames[doc_id] = meta.get("filename", filenames.get(doc_id, "unknown"))

    return [
        {
            "document_id": doc_id,
            "filename": filenames.get(doc_id, "unknown"),
            "chunk_count": count,
        }
        for doc_id, count in chunk_counts.items()
    ]
