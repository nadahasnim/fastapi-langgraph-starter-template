from __future__ import annotations

from collections.abc import AsyncIterator, Sequence
from pathlib import Path

from app.agents.orchestrator.graph import OrchestratorGraph
from app.agents.rag_agent.graph import RagAgentGraph
from app.agents.shared.llm import LlmMessage, LlmProvider, LlmResponse
from app.agents.tool_agent.graph import ToolAgentGraph

OUTPUT_DIR = Path(__file__).parent.parent / "docs" / "graphs"


class FakeLlmProvider(LlmProvider):
    """Minimal LLM provider stub for graph export (does not invoke LLM)."""

    async def complete(
        self, messages: Sequence[LlmMessage], model: str | None = None
    ) -> LlmResponse:
        raise NotImplementedError("Export script does not invoke LLM")

    def stream(
        self, messages: Sequence[LlmMessage], model: str | None = None
    ) -> AsyncIterator[str]:
        raise NotImplementedError("Export script does not invoke LLM")


def export_orchestrator() -> None:
    """Export orchestrator graph to PNG."""
    provider = FakeLlmProvider()
    graph = OrchestratorGraph(llm_provider=provider, default_model="fake-model")
    png_bytes = graph.get_compiled_graph().get_graph().draw_mermaid_png()
    output_path = OUTPUT_DIR / "orchestrator.png"
    output_path.write_bytes(png_bytes)
    print(f"Exported orchestrator graph to {output_path}")


def export_rag_agent() -> None:
    """Export RAG agent graph to PNG."""
    graph = RagAgentGraph(default_model="fake-model")
    png_bytes = graph.get_compiled_graph().get_graph().draw_mermaid_png()
    output_path = OUTPUT_DIR / "rag-agent.png"
    output_path.write_bytes(png_bytes)
    print(f"Exported RAG agent graph to {output_path}")


def export_tool_agent() -> None:
    """Export tool agent graph to PNG."""
    graph = ToolAgentGraph(default_model="fake-model")
    png_bytes = graph.get_compiled_graph().get_graph().draw_mermaid_png()
    output_path = OUTPUT_DIR / "tool-agent.png"
    output_path.write_bytes(png_bytes)
    print(f"Exported tool agent graph to {output_path}")


if __name__ == "__main__":
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    export_orchestrator()
    export_rag_agent()
    export_tool_agent()
    print(f"\nAll graphs exported to {OUTPUT_DIR}")
