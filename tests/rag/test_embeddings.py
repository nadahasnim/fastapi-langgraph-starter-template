import pytest

from app.rag.embeddings import MockEmbeddingProvider


@pytest.mark.asyncio
async def test_mock_embedding_provider_returns_vector_per_text():
    provider = MockEmbeddingProvider(dimensions=4)

    vectors = await provider.embed_texts(["hello", "world"])

    assert len(vectors) == 2
    assert all(len(vector) == 4 for vector in vectors)
