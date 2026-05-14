# Milestone 2 API Persistence Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add the OpenAI-style `/v1/responses` API, async SQLAlchemy persistence, Alembic migrations, and SSE streaming without adding LangGraph or real LLM calls.

**Architecture:** FastAPI routes delegate to `ResponseService`; the service persists conversations/messages/responses through repository classes. The response content is deterministic in this milestone so later milestones can replace the implementation with agent runtime calls without changing the API contract.

**Tech Stack:** FastAPI, Pydantic, SQLAlchemy async, Alembic, PostgreSQL, pytest, pytest-asyncio, httpx, uv, ruff.

---

## File Structure

- Create `app/api/v1/schemas/responses.py` for request and response DTOs.
- Create `app/api/v1/routes/responses.py` for JSON and SSE response endpoints.
- Modify `app/api/v1/router.py` to include the responses router.
- Create `app/services/response_service.py` for deterministic response generation and streaming events.
- Create `app/db/base.py` and `app/db/session.py` for SQLAlchemy metadata, engine, and session dependency.
- Create `app/db/models/conversation.py`, `app/db/models/message.py`, and `app/db/models/response.py` for persistence.
- Create `app/repositories/conversation_repository.py`, `app/repositories/message_repository.py`, and `app/repositories/response_repository.py`.
- Create `alembic.ini`, `alembic/env.py`, and one migration under `alembic/versions/`.
- Modify `pyproject.toml`, `.env.example`, and `uv.lock` for SQLAlchemy/Alembic dependencies.
- Create tests in `tests/api/test_responses.py`, `tests/services/test_response_service.py`, and `tests/repositories/test_response_repository.py`.

## Task 1: Add Dependencies And Database Config

**Files:**
- Modify: `pyproject.toml`
- Modify: `.env.example`
- Modify: `app/core/config.py`
- Modify: `uv.lock`

- [ ] **Step 1: Write the failing config test**

Create `tests/core/test_config.py`:

```python
from app.core.config import get_settings


def test_settings_include_database_url(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "postgresql+asyncpg://postgres:postgres@localhost:5432/agent_db")
    get_settings.cache_clear()

    settings = get_settings()

    assert settings.database_url == "postgresql+asyncpg://postgres:postgres@localhost:5432/agent_db"
```

- [ ] **Step 2: Run the failing test**

Run: `uv run pytest tests/core/test_config.py -v`

Expected: fail because `database_url` is not defined.

- [ ] **Step 3: Add dependencies and config field**

Add dependencies to `pyproject.toml`:

```toml
dependencies = [
    "fastapi>=0.115.0",
    "uvicorn[standard]>=0.34.0",
    "pydantic-settings>=2.7.0",
    "python-dotenv>=1.0.1",
    "sqlalchemy[asyncio]>=2.0.36",
    "asyncpg>=0.30.0",
    "alembic>=1.14.0",
]
```

Add to `app/core/config.py`:

```python
database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/agent_db"
```

Ensure `.env.example` contains:

```env
DATABASE_URL=postgresql+asyncpg://postgres:postgres@postgres:5432/agent_db
```

- [ ] **Step 4: Sync and verify**

Run: `uv sync`

Expected: dependencies install and `uv.lock` updates.

Run: `uv run pytest tests/core/test_config.py -v`

Expected: pass.

- [ ] **Step 5: Commit**

```bash
git add pyproject.toml uv.lock .env.example app/core/config.py tests/core/test_config.py
git commit -m "feat: add database configuration"
```

## Task 2: Add Response DTOs

**Files:**
- Create: `app/api/v1/schemas/responses.py`
- Create: `tests/api/test_response_schemas.py`

- [ ] **Step 1: Write schema tests**

```python
import pytest
from pydantic import ValidationError

from app.api.v1.schemas.responses import ResponseCreateRequest, ResponseObject


def test_response_request_defaults_to_non_streaming():
    request = ResponseCreateRequest(input="Hello", model="test-model")

    assert request.input == "Hello"
    assert request.model == "test-model"
    assert request.stream is False
    assert request.metadata == {}


def test_response_request_rejects_empty_input():
    with pytest.raises(ValidationError):
        ResponseCreateRequest(input="", model="test-model")


def test_response_object_contains_openai_style_fields():
    response = ResponseObject.create_text_response(
        response_id="resp_test",
        model="test-model",
        text="Hello back",
        metadata={"source": "test"},
    )

    assert response.id == "resp_test"
    assert response.object == "response"
    assert response.output[0].type == "message"
    assert response.output[0].content[0].text == "Hello back"
    assert response.extensions == {}
```

- [ ] **Step 2: Run schema tests to verify failure**

Run: `uv run pytest tests/api/test_response_schemas.py -v`

Expected: fail because schema module does not exist.

- [ ] **Step 3: Implement DTOs**

Create `app/api/v1/schemas/responses.py`:

```python
from typing import Any, Literal

from pydantic import BaseModel, Field


class ResponseCreateRequest(BaseModel):
    input: str = Field(min_length=1)
    model: str | None = None
    conversation_id: str | None = None
    stream: bool = False
    metadata: dict[str, Any] = Field(default_factory=dict)


class ResponseContent(BaseModel):
    type: Literal["output_text"] = "output_text"
    text: str


class ResponseMessage(BaseModel):
    type: Literal["message"] = "message"
    role: Literal["assistant"] = "assistant"
    content: list[ResponseContent]


class ResponseUsage(BaseModel):
    input_tokens: int = 0
    output_tokens: int = 0
    total_tokens: int = 0


class ResponseObject(BaseModel):
    id: str
    object: Literal["response"] = "response"
    model: str
    output: list[ResponseMessage]
    usage: ResponseUsage = Field(default_factory=ResponseUsage)
    metadata: dict[str, Any] = Field(default_factory=dict)
    extensions: dict[str, Any] = Field(default_factory=dict)

    @classmethod
    def create_text_response(
        cls,
        response_id: str,
        model: str,
        text: str,
        metadata: dict[str, Any] | None = None,
        extensions: dict[str, Any] | None = None,
    ) -> "ResponseObject":
        return cls(
            id=response_id,
            model=model,
            output=[ResponseMessage(content=[ResponseContent(text=text)])],
            metadata=metadata or {},
            extensions=extensions or {},
        )
```

- [ ] **Step 4: Run schema tests**

Run: `uv run pytest tests/api/test_response_schemas.py -v`

Expected: pass.

- [ ] **Step 5: Commit**

```bash
git add app/api/v1/schemas/responses.py tests/api/test_response_schemas.py
git commit -m "feat: add response schemas"
```

## Task 3: Add ResponseService

**Files:**
- Create: `app/services/response_service.py`
- Create: `tests/services/test_response_service.py`

- [ ] **Step 1: Write service tests**

```python
import pytest

from app.api.v1.schemas.responses import ResponseCreateRequest
from app.services.response_service import ResponseService


@pytest.mark.asyncio
async def test_create_response_returns_deterministic_text_response():
    service = ResponseService(default_model="template-test-model")
    request = ResponseCreateRequest(input="Hello", metadata={"user_id": "user_1"})

    response = await service.create_response(request)

    assert response.object == "response"
    assert response.model == "template-test-model"
    assert response.output[0].content[0].text == "Template response: Hello"
    assert response.metadata == {"user_id": "user_1"}


@pytest.mark.asyncio
async def test_stream_response_emits_sse_event_names():
    service = ResponseService(default_model="template-test-model")
    request = ResponseCreateRequest(input="Hello", stream=True)

    events = [event async for event in service.stream_response(request)]

    assert "event: response.created" in events[0]
    assert any("event: response.output_text.delta" in event for event in events)
    assert "event: response.completed" in events[-1]
```

- [ ] **Step 2: Run service tests to verify failure**

Run: `uv run pytest tests/services/test_response_service.py -v`

Expected: fail because `ResponseService` does not exist.

- [ ] **Step 3: Implement service**

```python
import json
from collections.abc import AsyncIterator
from uuid import uuid4

from app.api.v1.schemas.responses import ResponseCreateRequest, ResponseObject


class ResponseService:
    def __init__(self, default_model: str = "template-deterministic-model") -> None:
        self.default_model = default_model

    async def create_response(self, request: ResponseCreateRequest) -> ResponseObject:
        model = request.model or self.default_model
        return ResponseObject.create_text_response(
            response_id=f"resp_{uuid4().hex}",
            model=model,
            text=f"Template response: {request.input}",
            metadata=request.metadata,
        )

    async def stream_response(self, request: ResponseCreateRequest) -> AsyncIterator[str]:
        response = await self.create_response(request)
        text = response.output[0].content[0].text
        yield self._sse("response.created", {"id": response.id, "model": response.model})
        yield self._sse("response.output_text.delta", {"delta": text})
        yield self._sse("response.output_text.done", {"text": text})
        yield self._sse("response.completed", response.model_dump())

    @staticmethod
    def _sse(event: str, data: dict) -> str:
        return f"event: {event}\ndata: {json.dumps(data)}\n\n"
```

- [ ] **Step 4: Run service tests**

Run: `uv run pytest tests/services/test_response_service.py -v`

Expected: pass.

- [ ] **Step 5: Commit**

```bash
git add app/services/response_service.py tests/services/test_response_service.py
git commit -m "feat: add deterministic response service"
```

## Task 4: Add `/v1/responses` Route

**Files:**
- Create: `app/api/v1/routes/responses.py`
- Modify: `app/api/v1/router.py`
- Create: `tests/api/test_responses.py`

- [ ] **Step 1: Write route tests**

```python
from fastapi.testclient import TestClient

from app.main import create_app


def test_create_response_returns_json_response():
    client = TestClient(create_app())

    response = client.post("/v1/responses", json={"input": "Hello", "model": "test-model"})

    assert response.status_code == 200
    data = response.json()
    assert data["object"] == "response"
    assert data["model"] == "test-model"
    assert data["output"][0]["content"][0]["text"] == "Template response: Hello"
    assert "extensions" in data


def test_create_response_stream_returns_sse():
    client = TestClient(create_app())

    with client.stream("POST", "/v1/responses", json={"input": "Hello", "stream": True}) as response:
        body = "".join(response.iter_text())

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/event-stream")
    assert "event: response.created" in body
    assert "event: response.completed" in body
```

- [ ] **Step 2: Run route tests to verify failure**

Run: `uv run pytest tests/api/test_responses.py -v`

Expected: fail with 404 for `/v1/responses`.

- [ ] **Step 3: Implement route and register router**

Create `app/api/v1/routes/responses.py`:

```python
from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from app.api.v1.schemas.responses import ResponseCreateRequest, ResponseObject
from app.services.response_service import ResponseService

router = APIRouter(prefix="/responses", tags=["responses"])


@router.post("", response_model=ResponseObject)
async def create_response(request: ResponseCreateRequest):
    service = ResponseService()
    if request.stream:
        return StreamingResponse(service.stream_response(request), media_type="text/event-stream")
    return await service.create_response(request)
```

Modify `app/api/v1/router.py`:

```python
from fastapi import APIRouter

from app.api.v1.routes import health, responses

router = APIRouter()
router.include_router(health.router)
router.include_router(responses.router)
```

- [ ] **Step 4: Run route tests**

Run: `uv run pytest tests/api/test_responses.py -v`

Expected: pass.

- [ ] **Step 5: Commit**

```bash
git add app/api/v1/routes/responses.py app/api/v1/router.py tests/api/test_responses.py
git commit -m "feat: add responses endpoint"
```

## Task 5: Add SQLAlchemy Models, Repositories, And Alembic

**Files:**
- Create: `app/db/base.py`
- Create: `app/db/session.py`
- Create: `app/db/models/conversation.py`
- Create: `app/db/models/message.py`
- Create: `app/db/models/response.py`
- Create: `app/repositories/conversation_repository.py`
- Create: `app/repositories/message_repository.py`
- Create: `app/repositories/response_repository.py`
- Create: `alembic.ini`
- Create: `alembic/env.py`
- Create: `alembic/versions/202605140001_create_conversation_message_response_tables.py`
- Create: `tests/repositories/test_response_repository.py`

- [ ] **Step 1: Write repository test**

```python
import pytest
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.db.base import Base
from app.repositories.conversation_repository import ConversationRepository
from app.repositories.message_repository import MessageRepository
from app.repositories.response_repository import ResponseRepository


@pytest.mark.asyncio
async def test_repositories_persist_response_flow():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session_factory = async_sessionmaker(engine, expire_on_commit=False)
    async with session_factory() as session:
        conversation = await ConversationRepository(session).create(user_id="user_1", title="Test")
        message = await MessageRepository(session).create(
            conversation_id=conversation.id,
            role="user",
            content="Hello",
            metadata={},
        )
        response = await ResponseRepository(session).create(
            conversation_id=conversation.id,
            message_id=message.id,
            model="test-model",
            output={"text": "Hello back"},
            metadata={},
            extensions={},
        )
        await session.commit()

    assert conversation.id is not None
    assert message.conversation_id == conversation.id
    assert response.conversation_id == conversation.id
```

- [ ] **Step 2: Run repository test to verify failure**

Run: `uv run pytest tests/repositories/test_response_repository.py -v`

Expected: fail because DB modules do not exist or `aiosqlite` is missing.

- [ ] **Step 3: Add `aiosqlite` to dev dependencies**

Add to `pyproject.toml` dev group:

```toml
"aiosqlite>=0.20.0",
```

Run: `uv sync`

Expected: lockfile updates.

- [ ] **Step 4: Implement models and repositories**

Use SQLAlchemy `DeclarativeBase`, `Mapped`, `mapped_column`, `JSON`, `DateTime`, and UUID string IDs. Repositories should accept `AsyncSession` and return model instances after `session.flush()`.

Minimal repository method signatures:

```python
async def create(self, user_id: str, title: str | None = None) -> Conversation: ...
async def create(self, conversation_id: str, role: str, content: str, metadata: dict) -> Message: ...
async def create(self, conversation_id: str, message_id: str | None, model: str, output: dict, metadata: dict, extensions: dict) -> Response: ...
```

- [ ] **Step 5: Add Alembic baseline**

`alembic/env.py` should import `Base` and model modules so metadata is available. Migration should create `conversations`, `messages`, and `responses` tables with JSON metadata/output fields and timestamp columns.

- [ ] **Step 6: Run repository test**

Run: `uv run pytest tests/repositories/test_response_repository.py -v`

Expected: pass.

- [ ] **Step 7: Commit**

```bash
git add pyproject.toml uv.lock app/db app/repositories alembic.ini alembic tests/repositories/test_response_repository.py
git commit -m "feat: add async persistence foundation"
```

## Task 6: Wire Persistence Into ResponseService

**Files:**
- Modify: `app/services/response_service.py`
- Modify: `app/api/v1/routes/responses.py`
- Modify: `tests/services/test_response_service.py`
- Modify: `tests/api/test_responses.py`

- [ ] **Step 1: Add service persistence test**

Extend `tests/services/test_response_service.py` with an async in-memory database fixture. Verify `create_response()` persists one conversation, one user message, and one response when the service is constructed with a session.

- [ ] **Step 2: Run targeted tests to verify failure**

Run: `uv run pytest tests/services/test_response_service.py -v`

Expected: fail because `ResponseService` does not accept a session.

- [ ] **Step 3: Inject database session in route**

Add `get_session()` in `app/db/session.py` and use `Depends(get_session)` in the responses route. Construct `ResponseService(session=session)`.

- [ ] **Step 4: Persist request/response in service**

When `session` is present, `ResponseService.create_response()` should create or reuse a conversation, persist the user message, persist the response object payload, commit through the route-managed session, and return the same OpenAI-style response object.

- [ ] **Step 5: Run targeted tests**

Run: `uv run pytest tests/services/test_response_service.py tests/api/test_responses.py -v`

Expected: pass.

- [ ] **Step 6: Commit**

```bash
git add app/services/response_service.py app/api/v1/routes/responses.py app/db/session.py tests/services/test_response_service.py tests/api/test_responses.py
git commit -m "feat: persist response requests"
```

## Task 7: Final Verification

**Files:**
- Review: all modified files

- [ ] **Step 1: Run full tests**

Run: `uv run pytest`

Expected: all tests pass.

- [ ] **Step 2: Run lint**

Run: `uv run ruff check .`

Expected: all checks pass.

- [ ] **Step 3: Validate compose**

Run: `docker compose config`

Expected: compose renders `api`, `postgres`, and `qdrant` services.

- [ ] **Step 4: Verify Alembic against local Postgres**

Run: `docker compose up -d postgres`

Run: `uv run alembic upgrade head`

Expected: migration completes without errors.

- [ ] **Step 5: Commit verification docs if changed**

If README or handover notes are updated, commit them with:

```bash
git add README.md HANDOVER.md
git commit -m "docs: update api persistence notes"
```
