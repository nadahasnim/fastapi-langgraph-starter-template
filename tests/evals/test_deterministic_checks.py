from app.api.v1.schemas.responses import ResponseObject
from app.evals.deterministic.checks import check_required_response_shape, check_text_contains


def test_required_response_shape_passes_for_valid_response():
    response = ResponseObject.create_text_response("resp_1", "test-model", "hello", {})

    result = check_required_response_shape(response.model_dump())

    assert result.passed is True


def test_text_contains_fails_for_missing_text():
    result = check_text_contains("hello world", "missing")

    assert result.passed is False
    assert "missing" in result.message
