from abc import ABC, abstractmethod
from typing import List

from app.config import settings


class EmbeddingProvider(ABC):
    """Abstract base class for embedding providers."""

    @abstractmethod
    def embed_text(self, text: str) -> List[float]:
        """Generate embedding for a single text."""
        pass

    @abstractmethod
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts (batch)."""
        pass

    @property
    @abstractmethod
    def dimension(self) -> int:
        """Return the embedding vector dimension."""
        pass


class OllamaEmbeddingProvider(EmbeddingProvider):
    """Ollama embedding provider using nomic-embed-text or similar models."""

    def __init__(self, base_url: str | None = None, model: str | None = None):
        self.base_url = base_url or settings.ollama_base_url
        self.model = model or settings.embedding_model
        self._dimension = settings.embedding_dimension
        self._client = None

    @property
    def dimension(self) -> int:
        return self._dimension

    def _get_client(self):
        if self._client is None:
            import ollama
            self._client = ollama.Client(host=self.base_url)
        return self._client

    def embed_text(self, text: str) -> List[float]:
        """Generate embedding for a single text."""
        client = self._get_client()
        response = client.embeddings(model=self.model, prompt=text)
        return response["embedding"]

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts."""
        if not texts:
            return []

        client = self._get_client()
        embeddings = []
        for text in texts:
            response = client.embeddings(model=self.model, prompt=text)
            embeddings.append(response["embedding"])
        return embeddings


def get_embedding_provider() -> EmbeddingProvider:
    """Factory function to get the configured embedding provider."""
    provider_name = settings.embedding_provider.lower()

    if provider_name == "ollama":
        return OllamaEmbeddingProvider()
    else:
        raise ValueError(f"Unknown embedding provider: {provider_name}")