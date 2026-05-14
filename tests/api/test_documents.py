import io

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.api.v1.routes.documents import router
from app.db.base import Base
from app.db.session import get_session


@pytest.fixture
async def test_db():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session_factory = async_sessionmaker(engine, expire_on_commit=False)
    return session_factory


@pytest.fixture
def client(test_db):
    app = FastAPI()
    app.include_router(router)

    async def override_get_session():
        async with test_db() as session:
            yield session

    app.dependency_overrides[get_session] = override_get_session
    return TestClient(app)


def test_upload_document(client: TestClient):
    file_content = b"# Test Document\n\nThis is a test."
    files = {"file": ("test.md", io.BytesIO(file_content), "text/markdown")}
    data = {"user_id": "user_1"}

    response = client.post("/documents/upload", files=files, data=data)

    assert response.status_code == 200
    body = response.json()
    assert body["object"] == "document"
    assert body["chunk_count"] > 0
