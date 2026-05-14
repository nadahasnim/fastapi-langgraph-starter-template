from fastapi.testclient import TestClient

from app.main import create_app


def test_request_id_header_is_added_when_missing():
    client = TestClient(create_app())

    response = client.get("/v1/health")

    assert response.headers["x-request-id"]


def test_request_id_header_is_preserved_when_supplied():
    client = TestClient(create_app())
    response = client.get("/v1/health", headers={"x-request-id": "req_test"})
    assert response.headers["x-request-id"] == "req_test"
