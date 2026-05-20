from langchain_core.embeddings import Embeddings
from langchain_core.language_models import BaseChatModel

from app.rag.embeddings import get_embeddings
from app.rag.llm import get_chat_llm


class OllamaEmbeddingProvider:
    def get_embeddings(self) -> Embeddings:
        return get_embeddings()


class OllamaLLMProvider:
    def get_llm(self, *, streaming: bool = False) -> BaseChatModel:
        return get_chat_llm(streaming=streaming)
