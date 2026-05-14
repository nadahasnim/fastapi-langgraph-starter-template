from __future__ import annotations

from pathlib import Path
from typing import Any, cast

from langgraph.graph import END, START, StateGraph

from app.agents.shared.prompt_loader import PromptLoader
from app.agents.tool_agent.state import ToolAgentState


class ToolAgentGraph:
    _STUB_TEXT = "Tool execution is not implemented yet."

    def __init__(self, default_model: str) -> None:
        self._default_model = default_model
        self._prompt_loader = PromptLoader(Path(__file__).parent / "prompts")
        self._prompt_loader.render("system.md", {})
        self._graph = self._build_graph().compile()

    def _build_graph(self) -> StateGraph:
        graph = StateGraph(ToolAgentState)
        graph.add_node("answer", self._answer)
        graph.add_edge(START, "answer")
        graph.add_edge("answer", END)
        return graph

    def get_compiled_graph(self):
        """Return compiled graph for visualization."""
        return self._graph

    def _answer(self, state: ToolAgentState) -> dict[str, str]:
        return {
            "response_text": self._STUB_TEXT,
            "response_model": cast(str | None, state.get("model")) or self._default_model,
        }

    async def invoke(
        self, input_text: str, metadata: dict[str, Any], model: str | None = None
    ) -> dict[str, str]:
        return cast(
            dict[str, str],
            await self._graph.ainvoke(
                {"input_text": input_text, "metadata": metadata, "model": model}
            ),
        )
