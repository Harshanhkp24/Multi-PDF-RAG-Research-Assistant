"""Stub for future OpenAI / Groq integration."""

from app.config import get_settings


class OpenAIProvider:
    """Placeholder — wire langchain-openai when OPENAI_API_KEY is set."""

    def __init__(self) -> None:
        settings = get_settings()
        if not settings.openai_api_key:
            raise ValueError("OPENAI_API_KEY not configured")

    def get_llm(self, *, streaming: bool = False):
        raise NotImplementedError("OpenAI provider not yet implemented. Set LLM_PROVIDER=ollama.")


class GroqProvider:
    """Placeholder — wire langchain-groq when GROQ_API_KEY is set."""

    def __init__(self) -> None:
        settings = get_settings()
        if not settings.groq_api_key:
            raise ValueError("GROQ_API_KEY not configured")

    def get_llm(self, *, streaming: bool = False):
        raise NotImplementedError("Groq provider not yet implemented. Set LLM_PROVIDER=ollama.")
