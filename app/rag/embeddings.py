from __future__ import annotations

import random
from collections.abc import Sequence
from typing import Any, Protocol

from openai import AsyncOpenAI

from app.core.config import Settings, get_settings


class EmbeddingProvider(Protocol):
    async def embed_texts(self, texts: Sequence[str]) -> list[list[float]]: ...


class MockEmbeddingProvider:
    def __init__(self, dimensions: int = 1536) -> None:
        self._dimensions = dimensions

    async def embed_texts(self, texts: Sequence[str]) -> list[list[float]]:
        """Return deterministic fake embeddings."""
        return [[random.random() for _ in range(self._dimensions)] for _ in texts]


class OpenRouterEmbeddingProvider:
    def __init__(
        self,
        settings: Settings | None = None,
        client: Any = None,
        model: str | None = None,
    ) -> None:
        self._settings = settings or get_settings()
        self._client = client or AsyncOpenAI(
            base_url=self._settings.openrouter_base_url,
            api_key=self._settings.openrouter_api_key,
        )
        self._model = model or "text-embedding-3-small"

    async def embed_texts(self, texts: Sequence[str]) -> list[list[float]]:
        """Generate embeddings using OpenRouter."""
        response = await self._client.embeddings.create(
            model=self._model,
            input=list(texts),
        )
        return [item.embedding for item in response.data]
