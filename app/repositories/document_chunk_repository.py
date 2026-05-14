
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.document_chunk import DocumentChunk


class DocumentChunkRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(
        self,
        document_id: str,
        chunk_index: int,
        content: str,
        qdrant_point_id: str,
        metadata: dict | None = None,
    ) -> DocumentChunk:
        chunk = DocumentChunk(
            document_id=document_id,
            chunk_index=chunk_index,
            content=content,
            qdrant_point_id=qdrant_point_id,
            chunk_metadata=metadata or {},
        )
        self.session.add(chunk)
        await self.session.flush()
        return chunk

    async def get(self, chunk_id: str) -> DocumentChunk | None:
        return await self.session.get(DocumentChunk, chunk_id)
