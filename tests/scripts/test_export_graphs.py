from app.agents.rag_agent.graph import RagAgentGraph
from app.agents.tool_agent.graph import ToolAgentGraph


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
