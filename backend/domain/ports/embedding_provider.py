from typing import Protocol


class EmbeddingProvider(Protocol):
    """Embedding boundary used by document ingestion and retrieval."""

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        """Return one vector for each input text in the same order."""
        ...
