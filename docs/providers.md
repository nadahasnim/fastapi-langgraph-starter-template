# LLM Providers

## Current Provider: OpenRouter

The template uses OpenRouter for LLM access, providing access to multiple models through a single API.

## Configuration

```env
OPENROUTER_API_KEY=your-key-here
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
DEFAULT_CHAT_MODEL=anthropic/claude-3.5-sonnet
DEFAULT_EMBEDDING_MODEL=openai/text-embedding-3-small
```

## Provider Interface

```python
from app.agents.shared.llm import LlmProvider, LlmMessage, LlmResponse

class CustomLlmProvider(LlmProvider):
    async def complete(
        self,
        messages: list[LlmMessage],
        model: str,
        temperature: float = 0.7,
        max_tokens: int | None = None
    ) -> LlmResponse:
        # Implement LLM call
        return LlmResponse(text="...", model=model)
```

## Switching Providers

### 1. Implement Provider

```python
# app/agents/shared/llm.py
class AnthropicLlmProvider(LlmProvider):
    def __init__(self, api_key: str):
        self._client = anthropic.AsyncAnthropic(api_key=api_key)
    
    async def complete(self, messages, model, temperature=0.7, max_tokens=None):
        response = await self._client.messages.create(
            model=model,
            messages=[{"role": m.role, "content": m.content} for m in messages],
            temperature=temperature,
            max_tokens=max_tokens or 4096
        )
        return LlmResponse(
            text=response.content[0].text,
            model=model
        )
```

### 2. Update Service

```python
# app/services/response_service.py
def _build_default_orchestrator(self):
    settings = get_settings()
    return OrchestratorGraph(
        llm_provider=AnthropicLlmProvider(api_key=settings.anthropic_api_key),
        default_model=self.default_model or settings.default_chat_model,
        observability=self.observability,
    )
```

### 3. Update Config

```python
# app/core/config.py
class Settings(BaseSettings):
    anthropic_api_key: str = ""
    # ...
```

## Supported Models

### OpenRouter Models

- `anthropic/claude-3.5-sonnet` - Best for complex reasoning
- `anthropic/claude-3-haiku` - Fast and cost-effective
- `openai/gpt-4-turbo` - Strong general performance
- `openai/gpt-3.5-turbo` - Fast and affordable
- `meta-llama/llama-3.1-70b-instruct` - Open source option

### Embedding Models

- `openai/text-embedding-3-small` - Fast, good quality
- `openai/text-embedding-3-large` - Higher quality
- `voyage-ai/voyage-2` - Specialized for retrieval

## Model Selection Strategy

```python
# Per-request model override
response = await service.create_response(
    ResponseCreateRequest(
        input="Hello",
        model="anthropic/claude-3-haiku"  # Override default
    )
)
```

## Cost Optimization

1. **Use cheaper models for simple tasks** - Haiku for routing, Sonnet for generation
2. **Cache embeddings** - Store vectors, don't re-embed
3. **Limit max_tokens** - Set reasonable limits
4. **Batch requests** - Process multiple inputs together
5. **Monitor usage** - Track costs with Langfuse

## Testing with Mock Provider

```python
class MockLlmProvider(LlmProvider):
    async def complete(self, messages, model, temperature=0.7, max_tokens=None):
        return LlmResponse(text="Mock response", model=model)

# Use in tests
agent = RagAgentGraph(llm_provider=MockLlmProvider(), default_model="test")
```
