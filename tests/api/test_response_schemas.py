import pytest
from pydantic import ValidationError

from app.api.v1.schemas.responses import ResponseCreateRequest, ResponseObject


def test_response_request_defaults_to_non_streaming() -> None:
    request = ResponseCreateRequest(input="Hello", model="test-model")

    assert request.input == "Hello"
    assert request.model == "test-model"
    assert request.stream is False
    assert request.metadata == {}


def test_response_request_rejects_empty_input() -> None:
    with pytest.raises(ValidationError):
        ResponseCreateRequest(input="", model="test-model")


def test_response_object_contains_openai_style_fields() -> None:
    response = ResponseObject.create_text_response(
        response_id="resp_test",
        model="test-model",
        text="Hello back",
        metadata={"source": "test"},
    )

    assert response.id == "resp_test"
    assert response.object == "response"
    assert response.output[0].type == "message"
    assert response.output[0].content[0].text == "Hello back"
    assert response.extensions == {}
