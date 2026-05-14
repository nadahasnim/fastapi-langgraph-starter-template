from dataclasses import dataclass, field
from typing import Any

RESPONSE_CREATED = "response.created"
RESPONSE_OUTPUT_TEXT_DELTA = "response.output_text.delta"
RESPONSE_OUTPUT_TEXT_DONE = "response.output_text.done"
RESPONSE_COMPLETED = "response.completed"


@dataclass
class AgentEvent:
    type: str
    data: dict[str, Any] = field(default_factory=dict)
