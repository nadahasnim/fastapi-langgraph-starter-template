"""Dataset runner for evaluations."""

from pathlib import Path

import yaml

from app.api.v1.schemas.responses import ResponseCreateRequest, ResponseObject
from app.evals.deterministic.checks import EvalResult, check_text_contains
from app.services.response_service import ResponseService


class MockOrchestrator:
    """Mock orchestrator for testing."""

    async def invoke(self, input_text: str, metadata: dict, model: str | None = None):
        return ResponseObject.create_text_response("resp_eval", model or "test-model", "Template response", {})


async def run_dataset(dataset_path: Path, service: ResponseService | None = None) -> list[EvalResult]:
    """Run evaluation dataset and return results."""
    with open(dataset_path, encoding="utf-8") as f:
        dataset = yaml.safe_load(f)

    if service is None:
        service = ResponseService(default_model="test-model", orchestrator=MockOrchestrator())

    results: list[EvalResult] = []

    for case in dataset.get("cases", []):
        case_name = case["name"]
        input_text = case["input"]

        # Run response service
        response = await service.create_response(ResponseCreateRequest(input=input_text))
        output_text = response.output[0].content[0].text

        # Run checks
        for check in case.get("checks", []):
            if check["type"] == "contains":
                result = check_text_contains(output_text, check["value"])
                results.append(
                    EvalResult(
                        name=case_name,
                        passed=result.passed,
                        message=f"{case_name}: {result.message}",
                    )
                )

    return results
