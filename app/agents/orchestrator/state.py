from __future__ import annotations

from typing import Any, Literal, TypedDict

RouteName = Literal["guardrail", "clarify", "rag", "tool", "direct"]


class OrchestratorState(TypedDict):
    input_text: str
    metadata: dict[str, Any]
    model: str | None


class OrchestratorRuntimeState(OrchestratorState, total=False):
    route: RouteName
    response_text: str
    response_model: str
