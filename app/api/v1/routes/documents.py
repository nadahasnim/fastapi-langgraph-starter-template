import tempfile
from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.schemas.documents import DocumentObject
from app.db.session import get_session
from app.rag.embeddings import MockEmbeddingProvider
from app.rag.qdrant import InMemoryVectorStore
from app.services.document_ingestion_service import DocumentIngestionService

router = APIRouter(prefix="/documents", tags=["documents"])


@router.post("/upload", response_model=DocumentObject)
async def upload_document(
    file: Annotated[UploadFile, File()],
    user_id: Annotated[str, Form()],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> DocumentObject:
    """Upload and ingest a document."""
    # Validate file type
    if not file.filename:
        raise HTTPException(status_code=400, detail="Filename is required")

    if not any(file.filename.endswith(ext) for ext in [".md", ".txt", ".pdf"]):
        raise HTTPException(
            status_code=400,
            detail="Unsupported file type. Supported: .md, .txt, .pdf",
        )

    # Save uploaded file temporarily
    with tempfile.NamedTemporaryFile(delete=False, suffix=Path(file.filename).suffix) as tmp:
        content = await file.read()
        tmp.write(content)
        tmp_path = Path(tmp.name)

    try:
        # Ingest document
        service = DocumentIngestionService(
            session=session,
            embedding_provider=MockEmbeddingProvider(dimensions=1536),
            vector_store=InMemoryVectorStore(),
        )

        result = await service.ingest_upload(
            user_id=user_id,
            filename=file.filename,
            content_type=file.content_type or "application/octet-stream",
            file_path=tmp_path,
        )

        await session.commit()

        # Fetch document to get created_at
        from app.repositories.document_repository import DocumentRepository

        document = await DocumentRepository(session).get(result["document_id"])
        if not document:
            raise HTTPException(status_code=500, detail="Document not found after creation")

        return DocumentObject(
            id=document.id,
            user_id=document.user_id,
            filename=document.filename,
            content_type=document.content_type,
            source=document.source,
            chunk_count=result["chunk_count"],
            created_at=document.created_at.isoformat(),
        )
    finally:
        # Clean up temp file
        tmp_path.unlink(missing_ok=True)
