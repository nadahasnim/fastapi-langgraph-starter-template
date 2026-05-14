from __future__ import annotations

from pathlib import Path
from typing import Any, cast

from langgraph.graph import END, START, StateGraph

from app.agents.rag_agent.state import RagAgentState
from app.agents.shared.prompt_loader import PromptLoader


class RagAgentGraph:
    def __init__(self, default_model: str) -> None:
        self._default_model = default_model
        self._prompt_loader = PromptLoader(Path(__file__).parent / "prompts")
        self._answer_prompt = self._prompt_loader.render("answer.md", {})
        self._graph = self._build_graph().compile()

    def _build_graph(self) -> StateGraph:
        graph = StateGraph(RagAgentState)
        graph.add_node("answer", self._answer)
        graph.add_edge(START, "answer")
        graph.add_edge("answer", END)
        return graph

    def _answer(self, state: RagAgentState) -> dict[str, str]:
        return {
            "response_text": self._answer_prompt,
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
