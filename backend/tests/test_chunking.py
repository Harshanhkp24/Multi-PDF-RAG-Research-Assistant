from langchain_core.documents import Document

from app.rag.chunking import split_documents


def test_split_documents_preserves_metadata():
    docs = [
        Document(
            page_content="A" * 500 + "\n\n" + "B" * 500,
            metadata={"document_id": "1", "filename": "test.pdf", "page": 1},
        )
    ]
    chunks = split_documents(docs)
    assert len(chunks) >= 1
    assert chunks[0].metadata["document_id"] == "1"
    assert chunks[0].metadata["filename"] == "test.pdf"
