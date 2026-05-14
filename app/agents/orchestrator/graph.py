from __future__ import annotations

from pathlib import Path
from typing import Any, cast

from langgraph.graph import END, START, StateGraph

from app.agents.orchestrator.state import OrchestratorRuntimeState, RouteName
from app.agents.rag_agent.graph import RagAgentGraph
from app.agents.shared.guardrails import (
    GuardrailViolation,
    validate_input_text,
    validate_output_text,
)
from app.agents.shared.llm import LlmMessage, LlmProvider
from app.agents.shared.prompt_loader import PromptLoader
from app.agents.shared.response_formatter import ResponseFormatter
from app.agents.tool_agent.graph import ToolAgentGraph
from app.api.v1.schemas.responses import ResponseObject
from app.core.observability import Observability


class OrchestratorGraph:
    _GUARDRAIL_TEXT = "Please send a non-empty, safe request so I can help."

    def __init__(
        self,
        llm_provider: LlmProvider,
        default_model: str,
        observability: Observability | None = None,
    ) -> None:
        self._llm_provider = llm_provider
        self._default_model = default_model
        self._observability = observability or Observability(enabled=False)
        self._response_formatter = ResponseFormatter(default_model=default_model)
        self._prompt_loader = PromptLoader(Path(__file__).parent / "prompts")
        self._system_prompt = self._prompt_loader.render("system.md", {})
        router_prompt = self._prompt_loader.render("router.md", {}).lower()
        self._rag_terms = tuple(
            term for term in ("knowledge", "document") if term in router_prompt
        ) or ("knowledge", "document")
        self._tool_terms = tuple(term for term in ("tool",) if term in router_prompt) or ("tool",)
        self._rag_graph = RagAgentGraph(default_model=default_model)
        self._tool_graph = ToolAgentGraph(default_model=default_model)
        self._graph = self._build_graph().compile()

    def _build_graph(self) -> StateGraph:
        graph = StateGraph(OrchestratorRuntimeState)
        graph.add_node("input_guardrail", self._input_guardrail)
        graph.add_node("route", self._route_input)
        graph.add_node("blocked_response", self._blocked_response)
        graph.add_node("clarify", self._clarification_response)
        graph.add_node("rag", self._rag_response)
        graph.add_node("tool", self._tool_response)
        graph.add_node("direct", self._direct_response)
        graph.add_node("output_guardrail", self._output_guardrail)
        
        graph.add_edge(START, "input_guardrail")
        graph.add_conditional_edges(
            "input_guardrail",
            self._select_after_input_guardrail,
            {
                "blocked": "blocked_response",
                "route": "route",
            },
        )
        graph.add_conditional_edges(
            "route",
            self._select_route,
            {
                "clarify": "clarify",
                "rag": "rag",
                "tool": "tool",
                "direct": "direct",
            },
        )
        graph.add_edge("blocked_response", "output_guardrail")
        graph.add_edge("clarify", "output_guardrail")
        graph.add_edge("rag", "output_guardrail")
        graph.add_edge("tool", "output_guardrail")
        graph.add_edge("direct", "output_guardrail")
        graph.add_edge("output_guardrail", END)
        return graph

    def get_compiled_graph(self):
        """Return compiled graph for visualization."""
        return self._graph

    def _input_guardrail(self, state: OrchestratorRuntimeState) -> dict[str, object]:
        """Validate input text and mark if blocked."""
        try:
            input_text = validate_input_text(state["input_text"])
            return {"input_text": input_text, "input_blocked": False}
        except GuardrailViolation:
            return {"input_blocked": True, "route": "guardrail"}

    def _select_after_input_guardrail(self, state: OrchestratorRuntimeState) -> str:
        """Route to blocked_response or route based on input_blocked."""
        return "blocked" if state.get("input_blocked") else "route"

    def _route_input(self, state: OrchestratorRuntimeState) -> dict[str, object]:
        """Select route based on input text."""
        input_text = state["input_text"]
        normalized_text = input_text.lower()
        
        if len(input_text.strip()) < 3:
            route: RouteName = "clarify"
        elif any(term in normalized_text for term in self._rag_terms):
            route = "rag"
        elif any(term in normalized_text for term in self._tool_terms):
            route = "tool"
        else:
            route = "direct"

        return {"route": route}

    def _select_route(self, state: OrchestratorRuntimeState) -> RouteName:
        return cast(RouteName, state.get("route", "direct"))

    def _blocked_response(self, state: OrchestratorRuntimeState) -> dict[str, object]:
        """Return blocked response for unsafe/invalid input."""
        return {
            "response_text": self._GUARDRAIL_TEXT,
            "response_model": cast(str | None, state.get("model")) or self._default_model,
            "route": "guardrail",
        }

    def _output_guardrail(self, state: OrchestratorRuntimeState) -> dict[str, object]:
        """Validate output text before returning."""
        response_text = cast(str, state.get("response_text", ""))
        route = cast(RouteName, state.get("route", "guardrail"))
        
        try:
            validated_text = validate_output_text(response_text)
            return {"response_text": validated_text, "route": route}
        except GuardrailViolation:
            return {
                "response_text": self._GUARDRAIL_TEXT,
                "route": "guardrail",
            }

    def _clarification_response(self, state: OrchestratorRuntimeState) -> dict[str, object]:
        return {
            "response_text": "Could you provide more detail so I can answer accurately?",
            "response_model": cast(str | None, state.get("model")) or self._default_model,
        }

    async def _rag_response(self, state: OrchestratorRuntimeState) -> dict[str, object]:
        return cast(
            dict[str, object],
            await self._rag_graph.invoke(
                state["input_text"], state["metadata"], cast(str | None, state.get("model"))
            ),
        )

    async def _tool_response(self, state: OrchestratorRuntimeState) -> dict[str, object]:
        return cast(
            dict[str, object],
            await self._tool_graph.invoke(
                state["input_text"], state["metadata"], cast(str | None, state.get("model"))
            ),
        )

    async def _direct_response(self, state: OrchestratorRuntimeState) -> dict[str, object]:
        response = await self._llm_provider.complete(
            [
                LlmMessage(role="system", content=self._system_prompt),
                LlmMessage(role="user", content=state["input_text"]),
            ],
            model=cast(str | None, state.get("model")) or self._default_model,
        )
        return {
            "response_text": response.text,
            "response_model": response.model,
            "route": "direct",
        }

    async def invoke(
        self, input_text: str, metadata: dict[str, Any], model: str | None = None
    ) -> ResponseObject:
        with self._observability.trace(
            name="agent.orchestrator",
            metadata={"input": input_text, "model": model or self._default_model},
        ) as trace:
            try:
                final_state = cast(
                    OrchestratorRuntimeState,
                    await self._graph.ainvoke(
                        {"input_text": input_text, "metadata": metadata, "model": model}
                    ),
                )
                response_text = cast(str, final_state.get("response_text", ""))
                route = cast(RouteName, final_state.get("route", "guardrail"))

                response = self._response_formatter.format_text(
                    response_text,
                    metadata={**metadata, "route": route},
                    model=model
                    or cast(str, final_state.get("response_model", self._default_model)),
                )
                trace.update(output={"route": route, "response_id": response.id})
                return response
            except Exception as e:
                trace.update(level="ERROR", status_message=str(e))
                raise
