from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

BACKEND_ROOT = Path(__file__).resolve().parent.parent
PROJECT_ROOT = BACKEND_ROOT.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(BACKEND_ROOT / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "Multi-PDF RAG Research Assistant"
    debug: bool = True

    ollama_base_url: str = "http://localhost:11434"
    ollama_chat_model: str = "llama3"
    ollama_embed_model: str = "nomic-embed-text"
    llm_provider: str = "ollama"

    openai_api_key: str | None = None
    groq_api_key: str | None = None

    chroma_persist_dir: str = str(PROJECT_ROOT / "data" / "chroma")
    chroma_collection_name: str = "research_docs"

    chunk_size: int = 1000
    chunk_overlap: int = 200
    retrieval_top_k: int = 4

    max_upload_size_mb: int = 50
    uploads_dir: str = str(PROJECT_ROOT / "data" / "uploads")

    database_url: str = f"sqlite+aiosqlite:///{PROJECT_ROOT / 'data' / 'chat.db'}"

    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173"

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    @property
    def max_upload_bytes(self) -> int:
        return self.max_upload_size_mb * 1024 * 1024


@lru_cache
def get_settings() -> Settings:
    return Settings()
