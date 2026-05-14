from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from typing import Any

from app.rag.embeddings import EmbeddingProvider
from app.rag.qdrant import VectorStore


@dataclass
class RetrievedChunk:
    content: str
    metadata: dict[str, Any]
    score: float


class Retriever:
    """Retrieves relevant chunks using embeddings and vector search."""

    def __init__(
        self,
        embedding_provider: EmbeddingProvider,
        vector_store: VectorStore,
    ) -> None:
        self._embedding_provider = embedding_provider
        self._vector_store = vector_store

    async def search(self, query: str, limit: int = 5) -> Sequence[RetrievedChunk]:
        """Search for relevant chunks."""
        # Embed query
        vectors = await self._embedding_provider.embed_texts([query])
        query_vector = vectors[0]

        # Search vector store
        results = await self._vector_store.search(query_vector, limit=limit)

        # Convert to RetrievedChunk
        return [
            RetrievedChunk(
                content=result.payload.get("content", ""),
                metadata=result.payload,
                score=result.score,
            )
            for result in results
        ]
