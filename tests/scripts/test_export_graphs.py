from collections.abc import AsyncIterator, Sequence

from app.agents.orchestrator.graph import OrchestratorGraph
from app.agents.rag_agent.graph import RagAgentGraph
from app.agents.shared.llm import LlmMessage, LlmProvider, LlmResponse
from app.agents.tool_agent.graph import ToolAgentGraph


class FakeLlmProvider(LlmProvider):
    async def complete(
        self, messages: Sequence[LlmMessage], model: str | None = None
    ) -> LlmResponse:
        raise NotImplementedError("Export script does not invoke LLM")

    def stream(
        self, messages: Sequence[LlmMessage], model: str | None = None
    ) -> AsyncIterator[str]:
        raise NotImplementedError("Export script does not invoke LLM")


def test_rag_agent_graph_exposes_compiled_graph():
    graph = RagAgentGraph(default_model="test-model")
    compiled = graph.get_compiled_graph()
    assert compiled is not None
    assert hasattr(compiled, "get_graph")


def test_tool_agent_graph_exposes_compiled_graph():
    graph = ToolAgentGraph(default_model="test-model")
    compiled = graph.get_compiled_graph()
    assert compiled is not None
    assert hasattr(compiled, "get_graph")


def test_orchestrator_graph_exposes_compiled_graph():
    provider = FakeLlmProvider()
    graph = OrchestratorGraph(llm_provider=provider, default_model="test-model")
    compiled = graph.get_compiled_graph()
    assert compiled is not None
    assert hasattr(compiled, "get_graph")
