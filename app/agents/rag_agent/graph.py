from __future__ import annotations

from pathlib import Path
from typing import Any, Protocol, cast

from langgraph.graph import END, START, StateGraph

from app.agents.rag_agent.state import RagAgentState
from app.agents.shared.prompt_loader import PromptLoader


class Retriever(Protocol):
    async def search(self, query: str, limit: int = 5) -> Any: ...


class RagAgentGraph:
    def __init__(self, default_model: str, retriever: Retriever | None = None) -> None:
        self._default_model = default_model
        self._retriever = retriever
        self._prompt_loader = PromptLoader(Path(__file__).parent / "prompts")
        self._answer_prompt = self._prompt_loader.render("answer.md", {})
        self._graph = self._build_graph().compile()

    def _build_graph(self) -> StateGraph:
        graph = StateGraph(RagAgentState)
        graph.add_node("answer", self._answer)
        graph.add_edge(START, "answer")
        graph.add_edge("answer", END)
        return graph

    async def _answer(self, state: RagAgentState) -> dict[str, str]:
        response_text = self._answer_prompt

        # If retriever available, retrieve context
        if self._retriever:
            input_text = cast(str, state.get("input_text", ""))
            results = await self._retriever.search(input_text, limit=5)

            # Build context from retrieved chunks
            context_parts = []
            for result in results:
                context_parts.append(f"- {result.content}")

            if context_parts:
                context = "\n".join(context_parts)
                response_text = f"Context:\n{context}\n\nAnswer: {self._answer_prompt}"

        return {
            "response_text": response_text,
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
