import pytest
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.db.base import Base
from app.repositories.conversation_repository import ConversationRepository
from app.repositories.message_repository import MessageRepository
from app.repositories.response_repository import ResponseRepository


@pytest.mark.asyncio
async def test_repositories_persist_response_flow() -> None:
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
            response_id="resp_test",
        )
        await session.commit()

    assert conversation.id is not None
    assert message.conversation_id == conversation.id
    assert response.conversation_id == conversation.id

    await engine.dispose()
