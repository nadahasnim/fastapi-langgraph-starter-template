import pytest

from app.agents.rag_agent.graph import RagAgentGraph
from app.rag.retriever import RetrievedChunk


class FakeRetriever:
    async def search(self, query: str, limit: int = 5):
        return [RetrievedChunk(content="retrieved context", metadata={"source": "test"}, score=1.0)]


@pytest.mark.asyncio
async def test_rag_agent_includes_retrieved_context():
    graph = RagAgentGraph(default_model="test-model", retriever=FakeRetriever())

    result = await graph.invoke("What does the document say?", {})

    assert "retrieved context" in result["response_text"]
