import pytest
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.api.v1.schemas.responses import ResponseCreateRequest
from app.db.base import Base
from app.db.models.conversation import Conversation
from app.db.models.message import Message
from app.db.models.response import Response
from app.services.response_service import ResponseService


@pytest.mark.asyncio
async def test_create_response_returns_deterministic_text_response() -> None:
    service = ResponseService(default_model="template-test-model")
    request = ResponseCreateRequest(input="Hello", metadata={"user_id": "user_1"})

    response = await service.create_response(request)

    assert response.object == "response"
    assert response.model == "template-test-model"
    assert response.output[0].content[0].text == "Template response: Hello"
    assert response.metadata == {"user_id": "user_1"}


@pytest.mark.asyncio
async def test_stream_response_emits_sse_event_names() -> None:
    service = ResponseService(default_model="template-test-model")
    request = ResponseCreateRequest(input="Hello", stream=True)

    events = [event async for event in service.stream_response(request)]

    assert "event: response.created" in events[0]
    assert any("event: response.output_text.delta" in event for event in events)
    assert "event: response.completed" in events[-1]


@pytest.mark.asyncio
async def test_create_response_persists_conversation_message_and_response() -> None:
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session_factory = async_sessionmaker(engine, expire_on_commit=False)
    async with session_factory() as session:
        service = ResponseService(default_model="template-test-model", session=session)
        request = ResponseCreateRequest(input="Hello", metadata={"user_id": "user_1"})

        response = await service.create_response(request)
        await session.commit()

        conversations = await session.scalar(select(func.count()).select_from(Conversation))
        messages = await session.scalar(select(func.count()).select_from(Message))
        responses = await session.scalar(select(func.count()).select_from(Response))

    assert response.output[0].content[0].text == "Template response: Hello"
    assert conversations == 1
    assert messages == 1
    assert responses == 1

    await engine.dispose()
