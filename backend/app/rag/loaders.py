from pathlib import Path

from langchain_core.documents import Document
from pypdf import PdfReader


def load_pdf(file_path: Path, document_id: str, filename: str) -> list[Document]:
    """Extract text per page with metadata for citations."""
    reader = PdfReader(str(file_path))
    documents: list[Document] = []

    for page_num, page in enumerate(reader.pages, start=1):
        text = page.extract_text() or ""
        text = text.strip()
        if not text:
            continue
        documents.append(
            Document(
                page_content=text,
                metadata={
                    "document_id": document_id,
                    "filename": filename,
                    "page": page_num,
                    "source": filename,
                },
            )
        )

    return documents
