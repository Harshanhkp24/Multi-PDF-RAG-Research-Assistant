from pydantic import BaseModel


class DocumentInfo(BaseModel):
    document_id: str
    filename: str
    chunk_count: int


class UploadResponse(BaseModel):
    documents: list[DocumentInfo]
    total_chunks: int
    message: str


class DocumentListResponse(BaseModel):
    documents: list[DocumentInfo]
