import pytest
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.db.base import Base
from app.rag.embeddings import MockEmbeddingProvider
from app.rag.qdrant import InMemoryVectorStore
from app.services.document_ingestion_service import DocumentIngestionService


@pytest.mark.asyncio
async def test_document_ingestion_service_ingests_markdown():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session_factory = async_sessionmaker(engine, expire_on_commit=False)
    async with session_factory() as session:
        service = DocumentIngestionService(
            session=session,
            embedding_provider=MockEmbeddingProvider(dimensions=4),
            vector_store=InMemoryVectorStore(),
        )

        result = await service.ingest_text(
            user_id="user_1",
            filename="policy.md",
            content_type="text/markdown",
            source="upload",
            text="# Policy\n\nThis is company policy.",
        )
        await session.commit()

    assert result["document_id"] is not None
    assert result["chunk_count"] > 0
