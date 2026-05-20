import uuid
from pathlib import Path

from app.rag.chunking import split_documents
from app.rag.loaders import load_pdf
from app.rag.vectorstore import add_documents, delete_by_document_id


def ingest_pdf(file_path: Path, filename: str, replace: bool = True) -> dict:
    document_id = str(uuid.uuid4())
    if replace:
        # New upload always gets new id; replace only if same file re-uploaded externally
        pass

    pages = load_pdf(file_path, document_id, filename)
    if not pages:
        return {
            "document_id": document_id,
            "filename": filename,
            "chunk_count": 0,
            "message": "No extractable text found in PDF.",
        }

    chunks = split_documents(pages)
    add_documents(chunks)

    return {
        "document_id": document_id,
        "filename": filename,
        "chunk_count": len(chunks),
        "message": f"Ingested {len(chunks)} chunks from {filename}.",
    }


def reingest_pdf(file_path: Path, document_id: str, filename: str) -> dict:
    delete_by_document_id(document_id)
    pages = load_pdf(file_path, document_id, filename)
    chunks = split_documents(pages)
    add_documents(chunks)
    return {
        "document_id": document_id,
        "filename": filename,
        "chunk_count": len(chunks),
        "message": f"Re-ingested {len(chunks)} chunks.",
    }
