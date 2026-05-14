import pytest

from app.api.v1.schemas.responses import ResponseCreateRequest, ResponseObject
from app.core.observability import Observability
from app.services.response_service import ResponseService


class MockOrchestrator:
    async def invoke(self, input_text: str, metadata: dict, model: str | None = None):
        return ResponseObject.create_text_response("resp_test", model or "test-model", "Hello", {})


@pytest.mark.asyncio
async def test_response_service_accepts_observability_without_credentials():
    service = ResponseService(
        default_model="test-model",
        observability=Observability(enabled=False),
        orchestrator=MockOrchestrator(),
    )

    response = await service.create_response(ResponseCreateRequest(input="Hello"))

    assert response.object == "response"
