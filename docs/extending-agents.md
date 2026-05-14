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

## Adding Tool Integrations

The tool agent is currently a stub that returns `"Tool execution is not implemented yet."` This section shows how to add concrete tool integrations using a simple registry pattern.

### Tool Interface

Define a protocol for tools:

```python
# app/agents/tool_agent/tools/base.py
from typing import Protocol, Any

class Tool(Protocol):
    """Protocol for tool implementations."""
    
    @property
    def name(self) -> str:
        """Unique tool identifier."""
        ...
    
    @property
    def description(self) -> str:
        """Human-readable description of what the tool does."""
        ...
    
    async def invoke(self, **kwargs: Any) -> dict[str, Any]:
        """Execute the tool with given arguments.
        
        Returns:
            dict with 'result' key on success, 'error' key on failure
        """
        ...
```

### Example: Math Tools

Simple arithmetic tools for demonstration:

```python
# app/agents/tool_agent/tools/math.py
from typing import Any

class AddTool:
    """Add two numbers."""
    
    @property
    def name(self) -> str:
        return "add"
    
    @property
    def description(self) -> str:
        return "Add two numbers together"
    
    async def invoke(self, a: float, b: float, **kwargs: Any) -> dict[str, Any]:
        try:
            return {"result": a + b}
        except (TypeError, ValueError) as e:
            return {"error": f"Invalid arguments: {e}"}


class SubtractTool:
    """Subtract two numbers."""
    
    @property
    def name(self) -> str:
        return "subtract"
    
    @property
    def description(self) -> str:
        return "Subtract b from a"
    
    async def invoke(self, a: float, b: float, **kwargs: Any) -> dict[str, Any]:
        try:
            return {"result": a - b}
        except (TypeError, ValueError) as e:
            return {"error": f"Invalid arguments: {e}"}


class MultiplyTool:
    """Multiply two numbers."""
    
    @property
    def name(self) -> str:
        return "multiply"
    
    @property
    def description(self) -> str:
        return "Multiply two numbers"
    
    async def invoke(self, a: float, b: float, **kwargs: Any) -> dict[str, Any]:
        try:
            return {"result": a * b}
        except (TypeError, ValueError) as e:
            return {"error": f"Invalid arguments: {e}"}


class DivideTool:
    """Divide two numbers."""
    
    @property
    def name(self) -> str:
        return "divide"
    
    @property
    def description(self) -> str:
        return "Divide a by b"
    
    async def invoke(self, a: float, b: float, **kwargs: Any) -> dict[str, Any]:
        try:
            if b == 0:
                return {"error": "Division by zero"}
            return {"result": a / b}
        except (TypeError, ValueError) as e:
            return {"error": f"Invalid arguments: {e}"}
```

### Tool Registry

Register tools for lookup:

```python
# app/agents/tool_agent/tools/registry.py
from app.agents.tool_agent.tools.math import AddTool, SubtractTool, MultiplyTool, DivideTool

class ToolRegistry:
    """Central registry for available tools."""
    
    def __init__(self):
        self._tools = {
            "add": AddTool(),
            "subtract": SubtractTool(),
            "multiply": MultiplyTool(),
            "divide": DivideTool(),
        }
    
    def get(self, name: str):
        """Get tool by name."""
        return self._tools.get(name)
    
    def list_tools(self) -> list[dict[str, str]]:
        """List all available tools with descriptions."""
        return [
            {"name": tool.name, "description": tool.description}
            for tool in self._tools.values()
        ]
```

### Tool Agent Integration

Wire the registry into the tool agent:

```python
# app/agents/tool_agent/graph.py (modified)
from app.agents.tool_agent.tools.registry import ToolRegistry

class ToolAgentGraph:
    def __init__(self, default_model: str):
        self._default_model = default_model
        self._registry = ToolRegistry()
        # ... rest of init
    
    async def _answer(self, state: ToolAgentState) -> dict[str, str]:
        input_text = state["input_text"]
        
        # Simple parsing: "add 5 and 3" -> tool="add", args={"a": 5, "b": 3}
        # In production, use LLM function calling or structured parsing
        parsed = self._parse_tool_request(input_text)
        
        if not parsed:
            return {
                "response_text": "Could not parse tool request",
                "response_model": self._default_model
            }
        
        tool = self._registry.get(parsed["tool"])
        if not tool:
            return {
                "response_text": f"Unknown tool: {parsed['tool']}",
                "response_model": self._default_model
            }
        
        result = await tool.invoke(**parsed["args"])
        
        if "error" in result:
            response_text = f"Tool error: {result['error']}"
        else:
            response_text = f"Result: {result['result']}"
        
        return {
            "response_text": response_text,
            "response_model": self._default_model
        }
    
    def _parse_tool_request(self, text: str) -> dict | None:
        """Simple keyword-based parsing.
        
        Production systems should use:
        - LLM function calling (OpenAI, Anthropic tool use)
        - Structured output parsing
        - Intent classification + slot filling
        """
        text_lower = text.lower()
        
        # Example: "add 5 and 3"
        if "add" in text_lower:
            parts = text_lower.split()
            try:
                a = float(parts[1])
                b = float(parts[3])
                return {"tool": "add", "args": {"a": a, "b": b}}
            except (IndexError, ValueError):
                return None
        
        # Similar patterns for subtract, multiply, divide
        # ...
        
        return None
```

### Error Handling

Handle common tool execution errors:

```python
async def _answer(self, state: ToolAgentState) -> dict[str, str]:
    try:
        # Parse and execute tool
        parsed = self._parse_tool_request(state["input_text"])
        
        if not parsed:
            return {
                "response_text": "Could not understand tool request. Try: 'add 5 and 3'",
                "response_model": self._default_model
            }
        
        tool = self._registry.get(parsed["tool"])
        if not tool:
            available = ", ".join(t["name"] for t in self._registry.list_tools())
            return {
                "response_text": f"Unknown tool. Available: {available}",
                "response_model": self._default_model
            }
        
        result = await tool.invoke(**parsed["args"])
        
        if "error" in result:
            return {
                "response_text": f"Tool execution failed: {result['error']}",
                "response_model": self._default_model
            }
        
        return {
            "response_text": f"Result: {result['result']}",
            "response_model": self._default_model
        }
    
    except Exception as e:
        return {
            "response_text": f"Unexpected error: {str(e)}",
            "response_model": self._default_model
        }
```

### Testing Tools

Test tools independently:

```python
# tests/agents/tool_agent/test_math_tools.py
import pytest
from app.agents.tool_agent.tools.math import AddTool, DivideTool

@pytest.mark.asyncio
async def test_add_tool_returns_sum():
    tool = AddTool()
    result = await tool.invoke(a=5, b=3)
    assert result == {"result": 8}

@pytest.mark.asyncio
async def test_divide_tool_handles_zero():
    tool = DivideTool()
    result = await tool.invoke(a=10, b=0)
    assert "error" in result
    assert "zero" in result["error"].lower()

@pytest.mark.asyncio
async def test_add_tool_handles_invalid_types():
    tool = AddTool()
    result = await tool.invoke(a="not a number", b=3)
    assert "error" in result
```

### Production Considerations

The examples above use simple keyword parsing. Production systems should use:

1. **LLM Function Calling** - OpenAI, Anthropic, or other providers with native tool support
2. **Structured Output** - JSON schema validation for tool arguments
3. **Intent Classification** - Separate model to classify tool intent before execution
4. **Argument Validation** - Pydantic models for type-safe tool arguments
5. **Async Tool Execution** - Background tasks for long-running tools
6. **Tool Composition** - Chain multiple tools together
7. **Observability** - Trace tool calls with Langfuse or similar

Example with LLM function calling:

```python
# Using OpenAI-style function calling
tools_schema = [
    {
        "type": "function",
        "function": {
            "name": "add",
            "description": "Add two numbers",
            "parameters": {
                "type": "object",
                "properties": {
                    "a": {"type": "number"},
                    "b": {"type": "number"}
                },
                "required": ["a", "b"]
            }
        }
    }
]

response = await llm_provider.complete(
    messages=[{"role": "user", "content": input_text}],
    tools=tools_schema
)

if response.tool_calls:
    tool_call = response.tool_calls[0]
    tool = registry.get(tool_call.function.name)
    result = await tool.invoke(**tool_call.function.arguments)
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
