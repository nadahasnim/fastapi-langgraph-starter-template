from __future__ import annotations

import pytest
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.api.v1.schemas.responses import ResponseCreateRequest, ResponseObject
from app.db.base import Base
from app.db.models.conversation import Conversation
from app.db.models.message import Message
from app.db.models.response import Response
from app.services.response_service import ResponseService


class StubOrchestrator:
    def __init__(self, response_text: str = "Graph response") -> None:
        self.response_text = response_text
        self.calls: list[tuple[str, dict[str, object], str | None]] = []

    async def invoke(
        self, input_text: str, metadata: dict[str, object], model: str | None = None
    ) -> ResponseObject:
        self.calls.append((input_text, metadata, model))
        return ResponseObject.model_validate(
            {
                "id": "resp_from_graph",
                "object": "response",
                "model": model or "graph-test-model",
                "output": [
                    {
                        "type": "message",
                        "role": "assistant",
                        "content": [{"type": "output_text", "text": self.response_text}],
                    }
                ],
                "usage": {"input_tokens": 3, "output_tokens": 2, "total_tokens": 5},
                "metadata": {"user_id": metadata.get("user_id"), "route": "direct"},
                "extensions": {"source": "stub-orchestrator"},
            }
        )


@pytest.mark.asyncio
async def test_create_response_returns_orchestrator_output() -> None:
    orchestrator = StubOrchestrator(response_text="Graph says hello")
    service = ResponseService(default_model="template-test-model", orchestrator=orchestrator)
    request = ResponseCreateRequest(input="Hello", metadata={"user_id": "user_1"})

    response = await service.create_response(request)

    assert response.object == "response"
    assert response.id == "resp_from_graph"
    assert response.model == "graph-test-model"
    assert response.output[0].content[0].text == "Graph says hello"
    assert response.metadata == {"user_id": "user_1", "route": "direct"}
    assert response.extensions == {"source": "stub-orchestrator"}
    assert response.usage.total_tokens == 5
    assert orchestrator.calls == [("Hello", {"user_id": "user_1"}, None)]


@pytest.mark.asyncio
async def test_create_response_preserves_request_model_override() -> None:
    orchestrator = StubOrchestrator(response_text="Graph says hello")
    service = ResponseService(default_model="template-test-model", orchestrator=orchestrator)

    response = await service.create_response(
        ResponseCreateRequest(input="Hello", model="override-model", metadata={"user_id": "user_1"})
    )

    assert response.model == "override-model"
    assert orchestrator.calls == [("Hello", {"user_id": "user_1"}, "override-model")]


@pytest.mark.asyncio
async def test_stream_response_emits_sse_event_names() -> None:
    orchestrator = StubOrchestrator(response_text="Graph stream")
    service = ResponseService(default_model="template-test-model", orchestrator=orchestrator)
    request = ResponseCreateRequest(input="Hello", stream=True)

    events = [event async for event in service.stream_response(request)]

    assert "event: response.created" in events[0]
    assert any("event: response.output_text.delta" in event for event in events)
    assert any("Graph stream" in event for event in events)
    assert "event: response.completed" in events[-1]


@pytest.mark.asyncio
async def test_create_response_persists_conversation_message_and_response() -> None:
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session_factory = async_sessionmaker(engine, expire_on_commit=False)
    async with session_factory() as session:
        orchestrator = StubOrchestrator(response_text="Persisted graph output")
        service = ResponseService(
            default_model="template-test-model",
            session=session,
            orchestrator=orchestrator,
        )
        request = ResponseCreateRequest(input="Hello", metadata={"user_id": "user_1"})

        response = await service.create_response(request)
        await session.commit()

        conversations = await session.scalar(select(func.count()).select_from(Conversation))
        messages = await session.scalar(select(func.count()).select_from(Message))
        responses = await session.scalar(select(func.count()).select_from(Response))
        persisted_response = await session.scalar(select(Response))

    assert response.output[0].content[0].text == "Persisted graph output"
    assert response.metadata == {"user_id": "user_1", "route": "direct"}
    assert conversations == 1
    assert messages == 1
    assert responses == 1
    assert persisted_response is not None
    assert persisted_response.id == "resp_from_graph"
    assert persisted_response.model == "graph-test-model"
    assert persisted_response.metadata_json == {"user_id": "user_1", "route": "direct"}
    assert persisted_response.extensions == {"source": "stub-orchestrator"}

    await engine.dispose()
