from app.config import get_settings
from app.providers.ollama_provider import OllamaEmbeddingProvider, OllamaLLMProvider


def get_llm_provider():
    settings = get_settings()
    if settings.llm_provider == "ollama":
        return OllamaLLMProvider()
    if settings.llm_provider == "openai":
        from app.providers.openai_provider import OpenAIProvider

        return OpenAIProvider()
    if settings.llm_provider == "groq":
        from app.providers.openai_provider import GroqProvider

        return GroqProvider()
    raise ValueError(f"Unknown LLM_PROVIDER: {settings.llm_provider}")


def get_embedding_provider():
    settings = get_settings()
    if settings.llm_provider == "ollama":
        return OllamaEmbeddingProvider()
    raise NotImplementedError("Only Ollama embeddings are configured. Set LLM_PROVIDER=ollama.")
