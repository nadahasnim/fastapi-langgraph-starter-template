from __future__ import annotations

from pathlib import Path
from typing import Any
from uuid import uuid4

from sqlalchemy.ext.asyncio import AsyncSession

from app.rag.chunking import chunk_text
from app.rag.embeddings import EmbeddingProvider
from app.rag.loaders.markdown_loader import load_markdown
from app.rag.loaders.pdf_loader import load_pdf
from app.rag.loaders.text_loader import load_text
from app.rag.qdrant import VectorStore
from app.repositories.document_chunk_repository import DocumentChunkRepository
from app.repositories.document_repository import DocumentRepository


class DocumentIngestionService:
    """Service for ingesting documents into the RAG system."""

    def __init__(
        self,
        session: AsyncSession,
        embedding_provider: EmbeddingProvider,
        vector_store: VectorStore,
        chunk_size: int = 1000,
        overlap: int = 200,
    ) -> None:
        self._session = session
        self._embedding_provider = embedding_provider
        self._vector_store = vector_store
        self._chunk_size = chunk_size
        self._overlap = overlap

    async def ingest_text(
        self,
        user_id: str,
        filename: str,
        content_type: str,
        source: str,
        text: str,
    ) -> dict[str, Any]:
        """Ingest text content."""
        # Create document record
        document_repo = DocumentRepository(self._session)
        document = await document_repo.create(
            user_id=user_id,
            filename=filename,
            content_type=content_type,
            source=source,
        )

        # Chunk text
        chunks = chunk_text(text, chunk_size=self._chunk_size, overlap=self._overlap)

        # Embed chunks
        chunk_texts = [chunk.content for chunk in chunks]
        vectors = await self._embedding_provider.embed_texts(chunk_texts)

        # Store chunks and vectors
        chunk_repo = DocumentChunkRepository(self._session)
        for chunk, vector in zip(chunks, vectors, strict=False):
            point_id = str(uuid4())

            # Store in database
            await chunk_repo.create(
                document_id=document.id,
                chunk_index=chunk.index,
                content=chunk.content,
                qdrant_point_id=point_id,
                metadata=chunk.metadata,
            )

            # Store in vector database
            await self._vector_store.upsert(
                point_id=point_id,
                vector=vector,
                payload={
                    "content": chunk.content,
                    "document_id": document.id,
                    "chunk_index": chunk.index,
                    **chunk.metadata,
                },
            )

        return {
            "document_id": document.id,
            "chunk_count": len(chunks),
        }

    async def ingest_upload(
        self,
        user_id: str,
        filename: str,
        content_type: str,
        file_path: Path,
    ) -> dict[str, Any]:
        """Ingest uploaded file."""
        # Load file based on type
        if filename.endswith(".md"):
            text = load_markdown(file_path)
        elif filename.endswith(".txt"):
            text = load_text(file_path)
        elif filename.endswith(".pdf"):
            text = load_pdf(file_path)
        else:
            raise ValueError(f"Unsupported file type: {filename}")

        return await self.ingest_text(
            user_id=user_id,
            filename=filename,
            content_type=content_type,
            source="upload",
            text=text,
        )
