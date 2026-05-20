from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: str
    ollama: bool
    ollama_models: list[str]
    chroma: bool
    message: str | None = None
