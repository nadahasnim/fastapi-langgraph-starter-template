from collections.abc import AsyncIterator

from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.db.base import Base
from app.db.session import get_session
from app.main import create_app


async def _session_override() -> AsyncIterator[AsyncSession]:
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session_factory = async_sessionmaker(engine, expire_on_commit=False)
    async with session_factory() as session:
        yield session

    await engine.dispose()


def test_create_response_returns_json_response() -> None:
    app = create_app()
    app.dependency_overrides[get_session] = _session_override
    client = TestClient(app)

    response = client.post("/v1/responses", json={"input": "Hello", "model": "test-model"})

    assert response.status_code == 200
    data = response.json()
    assert data["object"] == "response"
    assert data["model"] == "test-model"
    assert data["output"][0]["content"][0]["text"] == "Template response: Hello"
    assert "extensions" in data


def test_create_response_stream_returns_sse() -> None:
    app = create_app()
    app.dependency_overrides[get_session] = _session_override
    client = TestClient(app)

    with client.stream(
        "POST",
        "/v1/responses",
        json={"input": "Hello", "stream": True},
    ) as response:
        body = "".join(response.iter_text())

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/event-stream")
    assert "event: response.created" in body
    assert "event: response.completed" in body
