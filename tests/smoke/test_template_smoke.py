from fastapi.testclient import TestClient

from app.main import create_app


def test_template_core_endpoints_are_available():
    client = TestClient(create_app())

    assert client.get("/v1/health").status_code == 200
    assert client.post("/v1/responses", json={"input": "Hello"}).status_code == 200


def test_streaming_response_smoke():
    client = TestClient(create_app())
    with client.stream("POST", "/v1/responses", json={"input": "Hello", "stream": True}) as response:
        body = "".join(response.iter_text())
    assert response.status_code == 200
    assert "response.completed" in body
