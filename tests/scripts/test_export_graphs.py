from app.agents.rag_agent.graph import RagAgentGraph


def test_rag_agent_graph_exposes_compiled_graph():
    graph = RagAgentGraph(default_model="test-model")
    compiled = graph.get_compiled_graph()
    assert compiled is not None
    assert hasattr(compiled, "get_graph")
