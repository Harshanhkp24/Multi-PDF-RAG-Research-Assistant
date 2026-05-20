from typing import Protocol

from langchain_core.embeddings import Embeddings
from langchain_core.language_models import BaseChatModel


class EmbeddingProvider(Protocol):
    def get_embeddings(self) -> Embeddings: ...


class LLMProvider(Protocol):
    def get_llm(self, *, streaming: bool = False) -> BaseChatModel: ...
