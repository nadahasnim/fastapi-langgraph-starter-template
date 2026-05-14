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


def test_export_script_has_fake_llm_provider():
    import scripts.export_graphs as export_module

    assert hasattr(export_module, "FakeLlmProvider")
    provider = export_module.FakeLlmProvider()
    assert hasattr(provider, "complete")


def test_export_script_has_export_functions():
    import scripts.export_graphs as export_module

    assert hasattr(export_module, "export_orchestrator")
    assert hasattr(export_module, "export_rag_agent")
    assert hasattr(export_module, "export_tool_agent")
    assert hasattr(export_module, "OUTPUT_DIR")


def test_export_script_writes_png_files(tmp_path, monkeypatch):
    """Test that export script writes non-empty PNG files."""
    import scripts.export_graphs as export_module

    # Redirect OUTPUT_DIR to tmp_path
    monkeypatch.setattr(export_module, "OUTPUT_DIR", tmp_path)

    # Run export functions
    export_module.export_orchestrator()
    export_module.export_rag_agent()
    export_module.export_tool_agent()

    # Verify files exist and are non-empty
    orchestrator_png = tmp_path / "orchestrator.png"
    rag_agent_png = tmp_path / "rag-agent.png"
    tool_agent_png = tmp_path / "tool-agent.png"

    assert orchestrator_png.exists()
    assert rag_agent_png.exists()
    assert tool_agent_png.exists()

    assert orchestrator_png.stat().st_size > 0
    assert rag_agent_png.stat().st_size > 0
    assert tool_agent_png.stat().st_size > 0
