import pytest
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.db.base import Base
from app.repositories.document_chunk_repository import DocumentChunkRepository
from app.repositories.document_repository import DocumentRepository


@pytest.mark.asyncio
async def test_document_repositories_persist_document_and_chunks():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session_factory = async_sessionmaker(engine, expire_on_commit=False)
    async with session_factory() as session:
        document = await DocumentRepository(session).create(
            user_id="user_1",
            filename="policy.md",
            content_type="text/markdown",
            source="upload",
        )
        chunk = await DocumentChunkRepository(session).create(
            document_id=document.id,
            chunk_index=0,
            content="Policy content",
            qdrant_point_id="point_1",
            metadata={"page": 1},
        )
        await session.commit()

    assert document.id is not None
    assert chunk.document_id == document.id
