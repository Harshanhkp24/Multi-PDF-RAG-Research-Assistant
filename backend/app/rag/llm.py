from langchain_ollama import ChatOllama

from app.config import get_settings


def get_chat_llm(*, streaming: bool = False) -> ChatOllama:
    settings = get_settings()
    return ChatOllama(
        model=settings.ollama_chat_model,
        base_url=settings.ollama_base_url,
        temperature=0.2,
        streaming=streaming,
    )
