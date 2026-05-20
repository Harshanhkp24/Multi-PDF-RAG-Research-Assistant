# Multi-PDF RAG Research Assistant

A full-stack Retrieval-Augmented Generation (RAG) application for uploading multiple PDFs and asking contextual questions with source citations and streaming responses.

## Stack

| Layer | Technology |
|-------|------------|
| Frontend | React, TypeScript, Tailwind CSS, Vite |
| Backend | FastAPI, Python |
| AI | LangChain, Ollama (llama3 + nomic-embed-text) |
| Vector DB | ChromaDB |
| Chat history | SQLite (async) |

## Prerequisites

1. **Python 3.11+**
2. **Node.js 18+**
3. **Ollama** running locally with models:

```bash
ollama pull llama3
ollama pull nomic-embed-text
```

## Quick start

### Backend

```bash
cd backend
python -m venv .venv
# Windows
.\.venv\Scripts\activate
# macOS/Linux
# source .venv/bin/activate

pip install -r requirements.txt
copy .env.example .env   # Windows
# cp .env.example .env     # macOS/Linux

uvicorn app.main:app --reload --port 8000
```

API docs: http://127.0.0.1:8000/docs

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:5173

## API endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Ollama + Chroma status |
| POST | `/api/documents/upload` | Multi-PDF ingest |
| GET | `/api/documents` | List indexed documents |
| POST | `/api/chat` | RAG Q&A (JSON) |
| POST | `/api/chat/stream` | RAG Q&A (SSE stream) |
| GET | `/api/sessions` | List chat sessions |
| GET | `/api/sessions/{id}/messages` | Session history |

## Project structure

```
backend/app/
  api/routes/     # Thin HTTP layer
  services/       # Business logic
  rag/            # Load, chunk, embed, retrieve, generate
  providers/      # Ollama (+ OpenAI/Groq stubs)
  db/             # SQLite models
frontend/src/
  api/            # Typed API client
  components/     # Upload, chat, citations
```

## Docker (backend only)

Ollama should run on the host for local GPU access:

```bash
docker compose up --build
```

## Environment variables

See `backend/.env.example` and `frontend/.env.example`.

## Tests

```bash
cd backend
.\.venv\Scripts\python -m pytest tests/ -v
```

## RAG pipeline flow

1. **Upload** → PDF text extracted per page (pypdf)
2. **Chunk** → RecursiveCharacterTextSplitter with overlap
3. **Embed** → nomic-embed-text via Ollama
4. **Store** → ChromaDB with metadata (filename, page, document_id)
5. **Query** → Embed question → similarity search top-k
6. **Generate** → llama3 with context + chat history
7. **Respond** → Answer + source citations (streaming via SSE)

## Future: cloud providers

Set `LLM_PROVIDER=openai` or `groq` and add API keys (stubs in `backend/app/providers/`).
