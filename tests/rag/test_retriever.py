import pytest

from app.rag.embeddings import MockEmbeddingProvider
from app.rag.qdrant import InMemoryVectorStore
from app.rag.retriever import Retriever


@pytest.mark.asyncio
async def test_retriever_returns_matching_chunks():
    store = InMemoryVectorStore()
    await store.upsert("point_1", [0.1, 0.2, 0.3, 0.4], {"content": "company policy"})
    retriever = Retriever(embedding_provider=MockEmbeddingProvider(dimensions=4), vector_store=store)

    results = await retriever.search("policy", limit=1)

    assert results[0].content == "company policy"
