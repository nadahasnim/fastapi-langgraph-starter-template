from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.core.errors import AppError
from app.middleware.error_handler import register_error_handlers


def test_app_error_returns_structured_json():
    app = FastAPI()
    register_error_handlers(app)

    @app.get("/boom")
    async def boom():
        raise AppError(message="Bad request", status_code=400, code="bad_request")

    response = TestClient(app).get("/boom")

    assert response.status_code == 400
    assert response.json()["error"]["code"] == "bad_request"
    assert response.json()["error"]["message"] == "Bad request"
