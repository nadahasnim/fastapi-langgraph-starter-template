from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol

from qdrant_client import AsyncQdrantClient
from qdrant_client.models import Distance, PointStruct, VectorParams


@dataclass
class VectorSearchResult:
    point_id: str
    score: float
    payload: dict[str, Any]


class VectorStore(Protocol):
    async def upsert(
        self, point_id: str, vector: list[float], payload: dict[str, Any]
    ) -> None: ...

    async def search(
        self, vector: list[float], limit: int = 5
    ) -> list[VectorSearchResult]: ...


class InMemoryVectorStore:
    """In-memory vector store for testing."""

    def __init__(self) -> None:
        self._points: dict[str, tuple[list[float], dict[str, Any]]] = {}

    async def upsert(
        self, point_id: str, vector: list[float], payload: dict[str, Any]
    ) -> None:
        self._points[point_id] = (vector, payload)

    async def search(
        self, vector: list[float], limit: int = 5
    ) -> list[VectorSearchResult]:
        """Simple cosine similarity search."""
        results = []

        for point_id, (stored_vector, payload) in self._points.items():
            # Cosine similarity
            dot_product = sum(a * b for a, b in zip(vector, stored_vector))
            magnitude_a = sum(a * a for a in vector) ** 0.5
            magnitude_b = sum(b * b for b in stored_vector) ** 0.5
            score = dot_product / (magnitude_a * magnitude_b) if magnitude_a and magnitude_b else 0.0

            results.append(VectorSearchResult(point_id=point_id, score=score, payload=payload))

        results.sort(key=lambda r: r.score, reverse=True)
        return results[:limit]


class QdrantVectorStore:
    """Qdrant vector store for production."""

    def __init__(
        self,
        client: AsyncQdrantClient,
        collection_name: str,
        vector_size: int = 1536,
    ) -> None:
        self._client = client
        self._collection_name = collection_name
        self._vector_size = vector_size

    async def ensure_collection(self) -> None:
        """Create collection if it doesn't exist."""
        collections = await self._client.get_collections()
        if self._collection_name not in [c.name for c in collections.collections]:
            await self._client.create_collection(
                collection_name=self._collection_name,
                vectors_config=VectorParams(size=self._vector_size, distance=Distance.COSINE),
            )

    async def upsert(
        self, point_id: str, vector: list[float], payload: dict[str, Any]
    ) -> None:
        await self._client.upsert(
            collection_name=self._collection_name,
            points=[PointStruct(id=point_id, vector=vector, payload=payload)],
        )

    async def search(
        self, vector: list[float], limit: int = 5
    ) -> list[VectorSearchResult]:
        results = await self._client.search(
            collection_name=self._collection_name,
            query_vector=vector,
            limit=limit,
        )

        return [
            VectorSearchResult(
                point_id=str(result.id),
                score=result.score,
                payload=result.payload or {},
            )
            for result in results
        ]
