from app.agents.shared.response_formatter import ResponseFormatter


def test_response_formatter_wraps_text_with_response_object_shape() -> None:
    response = ResponseFormatter(default_model="test-model").format_text(
        "Hello",
        metadata={"route": "direct"},
    )

    assert response.object == "response"
    assert response.model == "test-model"
    assert response.output[0].content[0].text == "Hello"
    assert response.metadata == {"route": "direct"}
    assert response.extensions == {}


def test_response_formatter_allows_public_overrides() -> None:
    response = ResponseFormatter(default_model="test-model").format_text(
        "Hello",
        model="override-model",
        response_id="resp_custom",
        extensions={"agent": "test"},
    )

    assert response.id == "resp_custom"
    assert response.model == "override-model"
    assert response.extensions == {"agent": "test"}
