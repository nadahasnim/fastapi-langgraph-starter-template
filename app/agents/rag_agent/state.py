from __future__ import annotations

from typing import Any, TypedDict


class RagAgentState(TypedDict):
    input_text: str
    metadata: dict[str, Any]
    model: str | None
    response_text: str
    response_model: str
