from fastapi import APIRouter, File, UploadFile

from app.schemas.documents import DocumentListResponse, UploadResponse
from app.services.document_service import list_documents, save_and_ingest_files

router = APIRouter(prefix="/api/documents", tags=["documents"])


@router.post("/upload", response_model=UploadResponse)
async def upload_documents(files: list[UploadFile] = File(...)) -> UploadResponse:
    if not files:
        from fastapi import HTTPException

        raise HTTPException(status_code=400, detail="No files provided.")
    return await save_and_ingest_files(files)


@router.get("", response_model=DocumentListResponse)
async def get_documents() -> DocumentListResponse:
    return list_documents()
