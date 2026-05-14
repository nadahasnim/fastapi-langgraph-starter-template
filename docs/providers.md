# LLM Providers

## Current Provider: OpenRouter

The template uses OpenRouter for LLM access, providing access to multiple models through a single API.

## Configuration

```env
OPENROUTER_API_KEY=your-key-here
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
DEFAULT_CHAT_MODEL=anthropic/claude-3.5-sonnet
DEFAULT_TEMPERATURE=0.2
DEFAULT_EMBEDDING_MODEL=openai/text-embedding-3-small
```

`DEFAULT_TEMPERATURE` is backend configuration. It is not exposed through the public responses endpoint.

## Provider Interface

```python
from app.agents.shared.llm import LlmProvider, LlmMessage, LlmResponse

class CustomLlmProvider(LlmProvider):
    async def complete(
        self,
        messages: list[LlmMessage],
        model: str | None = None,
    ) -> LlmResponse:
        # Implement LLM call
        return LlmResponse(text="...", model=model or "custom-model")
```

## Current Runtime Contract

- `LlmProvider.complete()` currently accepts `messages` plus optional `model`.
- Temperature is configured by the backend provider implementation via environment/config.
- Per-request `temperature`, `max_tokens`, and `tools` are not part of the public scaffold contract yet.

## Switching Providers

### 1. Implement Provider

```python
# app/agents/shared/llm.py
class AnthropicLlmProvider(LlmProvider):
    def __init__(self, api_key: str, default_temperature: float | None = None):
        self._client = anthropic.AsyncAnthropic(api_key=api_key)
        self._default_temperature = default_temperature
    
    async def complete(self, messages, model=None):
        create_kwargs = {
            model=model,
            messages=[{"role": m.role, "content": m.content} for m in messages],
        }
        if self._default_temperature is not None:
            create_kwargs["temperature"] = self._default_temperature
        response = await self._client.messages.create(**create_kwargs)
        return LlmResponse(
            text=response.content[0].text,
            model=model or "anthropic-default"
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
    default_temperature: float | None = None
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

## Future Extensions

Examples that mention `max_tokens`, per-request `temperature`, or `tools=` require extending the provider protocol and response types first. Keep them as internal implementation enhancements rather than frontend-exposed API parameters.

## Testing with Mock Provider

```python
class MockLlmProvider(LlmProvider):
    async def complete(self, messages, model=None):
        return LlmResponse(text="Mock response", model=model or "mock-model")

# Use in tests
provider = MockLlmProvider()
response = await provider.complete([], model="test")
```
