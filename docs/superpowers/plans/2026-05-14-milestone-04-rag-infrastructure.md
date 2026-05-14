# Milestone 4 RAG Infrastructure Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add generic document ingestion, chunking, embeddings, Qdrant storage, retrieval, and RAG-agent integration.

**Architecture:** Document routes call `DocumentIngestionService`; the service loads files, chunks text, persists document metadata, embeds chunks, and upserts vectors to Qdrant. The RAG agent depends on a retriever interface so tests can use fake embeddings and fake vector results without real OpenRouter or Qdrant calls.

**Tech Stack:** FastAPI, SQLAlchemy async, Alembic, Qdrant client, OpenAI-compatible embeddings, pypdf, pytest, uv, ruff.

---

## File Structure

- Create `app/api/v1/routes/documents.py` and `app/api/v1/schemas/documents.py`.
- Create `app/services/document_ingestion_service.py`.
- Create `app/rag/chunking.py`, `embeddings.py`, `qdrant.py`, `retriever.py`, and loaders under `app/rag/loaders/`.
- Create `app/db/models/document.py` and `app/db/models/document_chunk.py`.
- Create `app/repositories/document_repository.py` and `app/repositories/document_chunk_repository.py`.
- Modify `app/agents/rag_agent/graph.py` to use a retriever.
- Add Alembic migration for `documents` and `document_chunks`.
- Add tests under `tests/rag/`, `tests/services/`, `tests/api/`, and `tests/agents/`.

## Task 1: Add Document Models And Repositories

**Files:**
- Create: `app/db/models/document.py`
- Create: `app/db/models/document_chunk.py`
- Create: `app/repositories/document_repository.py`
- Create: `app/repositories/document_chunk_repository.py`
- Create: `alembic/versions/202605140002_create_document_tables.py`
- Create: `tests/repositories/test_document_repository.py`

- [ ] **Step 1: Write repository test**

```python
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
```

- [ ] **Step 2: Run test to verify failure**

Run: `uv run pytest tests/repositories/test_document_repository.py -v`
Expected: fail because document repository does not exist.

- [ ] **Step 3: Implement models and repositories**

Models should match `PLAN.md`: `documents` has user ID, filename, content type, source, timestamps; `document_chunks` has document ID, chunk index, content, Qdrant point ID, metadata, timestamp.

- [ ] **Step 4: Add migration**

Migration should create `documents` and `document_chunks` with a foreign key from chunks to documents.

- [ ] **Step 5: Run test and commit**

Run: `uv run pytest tests/repositories/test_document_repository.py -v`
Expected: pass.

```bash
git add app/db/models/document.py app/db/models/document_chunk.py app/repositories/document_repository.py app/repositories/document_chunk_repository.py alembic/versions/202605140002_create_document_tables.py tests/repositories/test_document_repository.py
git commit -m "feat: add document persistence"
```

## Task 2: Add Loaders And Chunking

**Files:**
- Modify: `pyproject.toml`
- Modify: `uv.lock`
- Create: `app/rag/chunking.py`
- Create: `app/rag/loaders/markdown_loader.py`
- Create: `app/rag/loaders/text_loader.py`
- Create: `app/rag/loaders/pdf_loader.py`
- Create: `tests/rag/test_chunking.py`
- Create: `tests/rag/test_loaders.py`

- [ ] **Step 1: Write chunking and loader tests**

```python
from pathlib import Path

from app.rag.chunking import chunk_text
from app.rag.loaders.markdown_loader import load_markdown
from app.rag.loaders.text_loader import load_text


def test_chunk_text_splits_with_overlap():
    chunks = chunk_text("one two three four five", chunk_size=14, overlap=4)

    assert len(chunks) >= 2
    assert chunks[0].index == 0
    assert chunks[0].content


def test_text_loader_reads_file(tmp_path: Path):
    path = tmp_path / "note.txt"
    path.write_text("hello", encoding="utf-8")

    assert load_text(path) == "hello"


def test_markdown_loader_reads_file(tmp_path: Path):
    path = tmp_path / "note.md"
    path.write_text("# hello", encoding="utf-8")

    assert load_markdown(path) == "# hello"
```

- [ ] **Step 2: Run tests to verify failure**

Run: `uv run pytest tests/rag/test_chunking.py tests/rag/test_loaders.py -v`
Expected: fail because modules do not exist.

- [ ] **Step 3: Add dependency and implement**

Add `pypdf>=5.1.0` to dependencies. Implement `TextChunk(index: int, content: str, metadata: dict)` and deterministic `chunk_text()` with character limits and overlap. Loaders should read UTF-8 markdown/text and extract PDF page text with `pypdf.PdfReader`.

- [ ] **Step 4: Run tests and commit**

Run: `uv sync`
Run: `uv run pytest tests/rag/test_chunking.py tests/rag/test_loaders.py -v`
Expected: pass.

```bash
git add pyproject.toml uv.lock app/rag/chunking.py app/rag/loaders tests/rag/test_chunking.py tests/rag/test_loaders.py
git commit -m "feat: add document loaders and chunking"
```

## Task 3: Add Embedding Provider

**Files:**
- Create: `app/rag/embeddings.py`
- Create: `tests/rag/test_embeddings.py`

- [ ] **Step 1: Write embedding tests**

```python
import pytest

from app.rag.embeddings import MockEmbeddingProvider


@pytest.mark.asyncio
async def test_mock_embedding_provider_returns_vector_per_text():
    provider = MockEmbeddingProvider(dimensions=4)

    vectors = await provider.embed_texts(["hello", "world"])

    assert len(vectors) == 2
    assert all(len(vector) == 4 for vector in vectors)
```

- [ ] **Step 2: Run test to verify failure**

Run: `uv run pytest tests/rag/test_embeddings.py -v`
Expected: fail because embedding provider does not exist.

- [ ] **Step 3: Implement embedding abstraction**

Create `EmbeddingProvider` protocol, `MockEmbeddingProvider`, and `OpenRouterEmbeddingProvider`. The OpenRouter implementation should use the existing OpenAI client pattern but tests should only use the mock provider.

- [ ] **Step 4: Run tests and commit**

Run: `uv run pytest tests/rag/test_embeddings.py -v`
Expected: pass.

```bash
git add app/rag/embeddings.py tests/rag/test_embeddings.py
git commit -m "feat: add embedding provider abstraction"
```

## Task 4: Add Qdrant Wrapper And Retriever

**Files:**
- Modify: `pyproject.toml`
- Modify: `uv.lock`
- Create: `app/rag/qdrant.py`
- Create: `app/rag/retriever.py`
- Create: `tests/rag/test_retriever.py`

- [ ] **Step 1: Write retriever test**

```python
import pytest

from app.rag.embeddings import MockEmbeddingProvider
from app.rag.retriever import InMemoryVectorStore, Retriever


@pytest.mark.asyncio
async def test_retriever_returns_matching_chunks():
    store = InMemoryVectorStore()
    await store.upsert("point_1", [0.1, 0.2, 0.3, 0.4], {"content": "company policy"})
    retriever = Retriever(embedding_provider=MockEmbeddingProvider(dimensions=4), vector_store=store)

    results = await retriever.search("policy", limit=1)

    assert results[0].content == "company policy"
```

- [ ] **Step 2: Run test to verify failure**

Run: `uv run pytest tests/rag/test_retriever.py -v`
Expected: fail because retriever does not exist.

- [ ] **Step 3: Add Qdrant dependency and implement interfaces**

Add `qdrant-client>=1.12.1`. Implement `VectorStore` protocol, `InMemoryVectorStore` for tests, `QdrantVectorStore` for runtime, `RetrievedChunk`, and `Retriever`.

- [ ] **Step 4: Run tests and commit**

Run: `uv sync`
Run: `uv run pytest tests/rag/test_retriever.py -v`
Expected: pass.

```bash
git add pyproject.toml uv.lock app/rag/qdrant.py app/rag/retriever.py tests/rag/test_retriever.py
git commit -m "feat: add qdrant retriever abstraction"
```

## Task 5: Add Document Ingestion Service And API

**Files:**
- Create: `app/api/v1/schemas/documents.py`
- Create: `app/api/v1/routes/documents.py`
- Modify: `app/api/v1/router.py`
- Create: `app/services/document_ingestion_service.py`
- Create: `tests/services/test_document_ingestion_service.py`
- Create: `tests/api/test_documents.py`

- [ ] **Step 1: Write service and API tests**

Service test should pass markdown text through chunking, mock embeddings, in-memory vector store, document repositories, and return a document ID plus chunk count. API test should upload a small `.md` file and receive JSON with `object == "document"` and `chunk_count > 0`.

- [ ] **Step 2: Run tests to verify failure**

Run: `uv run pytest tests/services/test_document_ingestion_service.py tests/api/test_documents.py -v`
Expected: fail because service and route do not exist.

- [ ] **Step 3: Implement service and route**

Route should accept `UploadFile`, reject unsupported suffixes outside `.md`, `.txt`, `.pdf`, and call `DocumentIngestionService.ingest_upload()`. Service should persist metadata, create chunks, embed, upsert vectors, and store Qdrant point IDs.

- [ ] **Step 4: Run tests and commit**

Run: `uv run pytest tests/services/test_document_ingestion_service.py tests/api/test_documents.py -v`
Expected: pass.

```bash
git add app/api/v1/schemas/documents.py app/api/v1/routes/documents.py app/api/v1/router.py app/services/document_ingestion_service.py tests/services/test_document_ingestion_service.py tests/api/test_documents.py
git commit -m "feat: add document ingestion api"
```

## Task 6: Wire RAG Agent To Retriever

**Files:**
- Modify: `app/agents/rag_agent/graph.py`
- Modify: `app/agents/orchestrator/graph.py`
- Create: `tests/agents/test_rag_agent.py`

- [ ] **Step 1: Write RAG agent test**

```python
import pytest

from app.agents.rag_agent.graph import RagAgentGraph
from app.rag.retriever import RetrievedChunk


class FakeRetriever:
    async def search(self, query: str, limit: int = 5):
        return [RetrievedChunk(content="retrieved context", metadata={"source": "test"}, score=1.0)]


@pytest.mark.asyncio
async def test_rag_agent_includes_retrieved_context():
    graph = RagAgentGraph(retriever=FakeRetriever())

    result = await graph.invoke("What does the document say?")

    assert "retrieved context" in result.answer
```

- [ ] **Step 2: Run test to verify failure**

Run: `uv run pytest tests/agents/test_rag_agent.py -v`
Expected: fail until RAG agent accepts a retriever.

- [ ] **Step 3: Implement RAG wiring**

`RagAgentGraph.invoke()` should retrieve chunks, build a context block, and return a generic answer. Orchestrator should route document/knowledge inputs to this graph.

- [ ] **Step 4: Run tests and commit**

Run: `uv run pytest tests/agents/test_rag_agent.py tests/agents/test_orchestrator_graph.py -v`
Expected: pass.

```bash
git add app/agents/rag_agent/graph.py app/agents/orchestrator/graph.py tests/agents/test_rag_agent.py
git commit -m "feat: connect rag agent to retriever"
```

## Task 7: Final Verification

- [ ] **Step 1: Run full tests**

Run: `uv run pytest`
Expected: all tests pass.

- [ ] **Step 2: Run lint**

Run: `uv run ruff check .`
Expected: all checks pass.

- [ ] **Step 3: Validate compose and migrations**

Run: `docker compose config`
Expected: compose renders successfully.

Run: `docker compose up -d postgres qdrant`
Run: `uv run alembic upgrade head`
Expected: migrations apply and Qdrant service starts.
