# Extending Agents

## Adding a Custom Agent

Agents are LangGraph nodes in the orchestrator. To add a custom agent:

### 1. Create Agent Graph

```python
# app/agents/generic_card_agent/graph.py
from app.agents.shared.llm import LlmProvider, LlmMessage

class GenericCardAgentGraph:
    def __init__(self, llm_provider: LlmProvider, default_model: str):
        self._llm_provider = llm_provider
        self._default_model = default_model
    
    async def invoke(self, input_text: str, metadata: dict, model: str | None = None):
        # Custom agent logic
        response = await self._llm_provider.complete(
            [LlmMessage(role="user", content=input_text)],
            model=model or self._default_model
        )
        return {
            "response_text": response.text,
            "response_model": response.model
        }
```

### 2. Add to Orchestrator

```python
# app/agents/orchestrator/graph.py
from app.agents.generic_card_agent.graph import GenericCardAgentGraph

class OrchestratorGraph:
    def __init__(self, ...):
        # ...
        self._generic_card_graph = GenericCardAgentGraph(...)
    
    def _build_graph(self):
        graph = StateGraph(OrchestratorRuntimeState)
        # ...
        graph.add_node("generic_card", self._generic_card_response)
        graph.add_conditional_edges("route", self._select_route, {
            # ...
            "generic_card": "generic_card"
        })
        graph.add_edge("generic_card", END)
        return graph
    
    async def _generic_card_response(self, state):
        return await self._generic_card_graph.invoke(
            state["input_text"], state["metadata"], state.get("model")
        )
```

### 3. Update Router Logic

```python
def _route_input(self, state):
    input_text = validate_input_text(state["input_text"])
    normalized = input_text.lower()
    
    if "generic card" in normalized:
        route = "generic_card"
    # ... other routes
    
    return {"input_text": input_text, "route": route}
```

### 4. Add Tests

```python
# tests/agents/test_generic_card_agent.py
@pytest.mark.asyncio
async def test_generic_card_agent_returns_response():
    agent = GenericCardAgentGraph(MockLlmProvider(), "test-model")
    
    result = await agent.invoke("Create a generic card", {}, None)
    
    assert result["response_text"]
    assert result["response_model"] == "test-model"
```

## Agent Patterns

### Stateless Agents

Simple agents that don't maintain state:

```python
async def invoke(self, input_text: str, metadata: dict, model: str | None):
    # Process input
    # Call LLM
    # Return response
    return {"response_text": text, "response_model": model}
```

### Stateful Agents

Agents that maintain conversation state:

```python
class StatefulAgent:
    def __init__(self):
        self._history = []
    
    async def invoke(self, input_text: str, metadata: dict, model: str | None):
        self._history.append({"role": "user", "content": input_text})
        # Use history in LLM call
        response = await self._llm_provider.complete(self._history, model)
        self._history.append({"role": "assistant", "content": response.text})
        return {"response_text": response.text, "response_model": response.model}
```

### Multi-Step Agents

Agents with multiple processing steps:

```python
async def invoke(self, input_text: str, metadata: dict, model: str | None):
    # Step 1: Extract entities
    entities = await self._extract_entities(input_text)
    
    # Step 2: Fetch data
    data = await self._fetch_data(entities)
    
    # Step 3: Generate response
    response = await self._generate_response(input_text, data, model)
    
    return {"response_text": response.text, "response_model": response.model}
```

## Best Practices

1. **Keep agents focused** - One responsibility per agent
2. **Use shared components** - Reuse LlmProvider, PromptLoader, etc.
3. **Test independently** - Mock dependencies for unit tests
4. **Handle errors** - Wrap in try/except and return error state
5. **Add observability** - Use trace wrappers for monitoring
6. **Document prompts** - Store prompts in `prompts/` directory
7. **Validate output** - Use guardrails for safety checks

## Example: Generic Artifact Agent

```python
# app/agents/generic_artifact_agent/graph.py
from pathlib import Path
from app.agents.shared.llm import LlmProvider, LlmMessage
from app.agents.shared.prompt_loader import PromptLoader

class GenericArtifactAgentGraph:
    def __init__(self, llm_provider: LlmProvider, default_model: str):
        self._llm_provider = llm_provider
        self._default_model = default_model
        self._prompt_loader = PromptLoader(Path(__file__).parent / "prompts")
    
    async def invoke(self, input_text: str, metadata: dict, model: str | None = None):
        system_prompt = self._prompt_loader.render("system.md", {})
        
        messages = [
            LlmMessage(role="system", content=system_prompt),
            LlmMessage(role="user", content=input_text)
        ]
        
        response = await self._llm_provider.complete(
            messages,
            model=model or self._default_model
        )
        
        return {
            "response_text": response.text,
            "response_model": response.model
        }
```

## Routing Strategies

### Keyword-Based Routing

```python
if "generic card" in normalized_text:
    route = "generic_card"
elif "generic artifact" in normalized_text:
    route = "generic_artifact"
```

### LLM-Based Routing

```python
router_prompt = f"Route this request: {input_text}\nOptions: generic_card, generic_artifact, direct"
route_response = await self._llm_provider.complete([LlmMessage(role="user", content=router_prompt)])
route = route_response.text.strip().lower()
```

### Hybrid Routing

```python
# Try keyword first
if "generic card" in normalized_text:
    return "generic_card"

# Fall back to LLM
route_response = await self._llm_router(input_text)
return route_response
```
