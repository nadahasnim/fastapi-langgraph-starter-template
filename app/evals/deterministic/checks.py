"""Deterministic evaluation checks."""

from dataclasses import dataclass
from typing import Any


@dataclass
class EvalResult:
    """Result of an evaluation check."""

    name: str
    passed: bool
    message: str


def check_required_response_shape(response: dict[str, Any]) -> EvalResult:
    """Check if response has required shape."""
    required_fields = ["id", "object", "model", "output"]
    missing = [field for field in required_fields if field not in response]

    if missing:
        return EvalResult(
            name="required_response_shape",
            passed=False,
            message=f"Missing required fields: {', '.join(missing)}",
        )

    return EvalResult(
        name="required_response_shape",
        passed=True,
        message="Response has all required fields",
    )


def check_text_contains(text: str, expected: str) -> EvalResult:
    """Check if text contains expected substring."""
    passed = expected in text

    return EvalResult(
        name="text_contains",
        passed=passed,
        message=f"Text {'contains' if passed else 'does not contain'} '{expected}'",
    )
