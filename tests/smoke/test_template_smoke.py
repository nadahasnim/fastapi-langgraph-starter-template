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


def test_template_core_endpoints_are_available():
    app = create_app()
    app.dependency_overrides[get_session] = _session_override
    client = TestClient(app)

    assert client.get("/v1/health").status_code == 200
    assert client.post("/v1/responses", json={"input": "Hello"}).status_code == 200


def test_streaming_response_smoke():
    app = create_app()
    app.dependency_overrides[get_session] = _session_override
    client = TestClient(app)
    with client.stream(
        "POST", "/v1/responses", json={"input": "Hello", "stream": True}
    ) as response:
        body = "".join(response.iter_text())
    assert response.status_code == 200
    assert "response.completed" in body
