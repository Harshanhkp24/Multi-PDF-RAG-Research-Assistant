from pathlib import Path

from fastapi import HTTPException, UploadFile

from app.config import get_settings
from app.rag.ingestion import ingest_pdf
from app.rag.vectorstore import list_indexed_documents
from app.schemas.documents import DocumentInfo, DocumentListResponse, UploadResponse


async def save_and_ingest_files(files: list[UploadFile]) -> UploadResponse:
    settings = get_settings()
    uploads_dir = Path(settings.uploads_dir)
    uploads_dir.mkdir(parents=True, exist_ok=True)

    results: list[DocumentInfo] = []
    total_chunks = 0

    for file in files:
        if not file.filename or not file.filename.lower().endswith(".pdf"):
            raise HTTPException(status_code=400, detail=f"Invalid file: {file.filename}. Only PDF allowed.")

        content = await file.read()
        if len(content) > settings.max_upload_bytes:
            raise HTTPException(
                status_code=400,
                detail=f"File {file.filename} exceeds {settings.max_upload_size_mb}MB limit.",
            )

        safe_name = Path(file.filename).name
        dest = uploads_dir / safe_name
        dest.write_bytes(content)

        result = ingest_pdf(dest, safe_name)
        info = DocumentInfo(
            document_id=result["document_id"],
            filename=result["filename"],
            chunk_count=result["chunk_count"],
        )
        results.append(info)
        total_chunks += result["chunk_count"]

    return UploadResponse(
        documents=results,
        total_chunks=total_chunks,
        message=f"Successfully indexed {len(results)} document(s).",
    )


def list_documents() -> DocumentListResponse:
    docs = list_indexed_documents()
    return DocumentListResponse(
        documents=[
            DocumentInfo(
                document_id=d["document_id"],
                filename=d["filename"],
                chunk_count=d["chunk_count"],
            )
            for d in docs
        ]
    )
