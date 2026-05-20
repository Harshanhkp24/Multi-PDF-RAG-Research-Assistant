import httpx
from fastapi import APIRouter

from app.config import get_settings
from app.schemas.health import HealthResponse

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    settings = get_settings()
    ollama_ok = False
    models: list[str] = []
    chroma_ok = False
    message = None

    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get(f"{settings.ollama_base_url}/api/tags")
            if resp.status_code == 200:
                ollama_ok = True
                data = resp.json()
                models = [m.get("name", "").split(":")[0] for m in data.get("models", [])]
    except Exception as e:
        message = f"Ollama unreachable: {e}"

    try:
        from pathlib import Path

        chroma_path = Path(settings.chroma_persist_dir)
        chroma_path.mkdir(parents=True, exist_ok=True)
        from app.rag.vectorstore import get_vectorstore

        get_vectorstore()
        chroma_ok = True
    except Exception as e:
        message = (message or "") + f" Chroma error: {e}"

    required = {settings.ollama_chat_model, settings.ollama_embed_model}
    model_base_names = {m.split(":")[0] for m in models}
    missing = required - model_base_names
    if ollama_ok and missing:
        message = (message or "") + f" Missing models: {', '.join(missing)}. Run: ollama pull <model>"

    status = "healthy" if ollama_ok and chroma_ok and not missing else "degraded"
    return HealthResponse(
        status=status,
        ollama=ollama_ok,
        ollama_models=models,
        chroma=chroma_ok,
        message=message,
    )
