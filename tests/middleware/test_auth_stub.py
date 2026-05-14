from fastapi.testclient import TestClient

from app.main import create_app


def test_auth_stub_does_not_block_requests():
    client = TestClient(create_app())
    response = client.get("/v1/health")
    assert response.status_code == 200


def test_auth_stub_accepts_bearer_token_pattern():
    client = TestClient(create_app())
    response = client.get("/v1/health", headers={"authorization": "Bearer test-token"})
    assert response.status_code == 200
