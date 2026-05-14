# Agent Backend Template

Reusable FastAPI + LangGraph backend template for agentic AI services with RAG-oriented scaffolding, observability, and evaluation tooling.

## Features

- **FastAPI** REST API with streaming support
- **LangGraph** orchestrator with RAG, tool, and direct response agents
- **PostgreSQL** persistence for conversations, messages, and responses
- **Qdrant** vector store for document retrieval
- **Langfuse** optional observability and tracing
- **Evaluation** framework with deterministic checks and LLM judges
- **Middleware** for request IDs, structured errors, and auth stubs
- **Docker Compose** for local development

## Quick Start

```bash
# Install dependencies
uv sync

# Run tests
uv run pytest

# Lint
uv run ruff check .

# Start services
docker compose up -d postgres qdrant

# Run migrations
uv run alembic upgrade head

# Start API
uv run uvicorn app.main:app --reload
```

## Environment Variables

Create `.env` file:

```env
# App
APP_ENV=local
APP_NAME=agent-backend-template
APP_DEBUG=true

# Database
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/agent_db

# LLM Provider
OPENROUTER_API_KEY=your-key-here
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
DEFAULT_CHAT_MODEL=anthropic/claude-3.5-sonnet
DEFAULT_TEMPERATURE=0.2
DEFAULT_EMBEDDING_MODEL=openai/text-embedding-3-small

# Vector Store
QDRANT_URL=http://localhost:6333
QDRANT_COLLECTION=documents

# Observability (optional)
LANGFUSE_PUBLIC_KEY=
LANGFUSE_SECRET_KEY=
LANGFUSE_HOST=https://cloud.langfuse.com
```

## API Examples

### Health Check

```bash
curl http://localhost:8000/v1/health
```

Response:
```json
{"status":"ok"}
```

### Create Response

```bash
curl -X POST http://localhost:8000/v1/responses \
  -H "Content-Type: application/json" \
  -d '{"input": "What is in the knowledge base?"}'
```

Response:
```json
{
  "id": "resp_abc123",
  "object": "response",
  "model": "anthropic/claude-3.5-sonnet",
  "output": [
    {
      "type": "message",
      "role": "assistant",
      "content": [{"type": "output_text", "text": "..."}]
    }
  ],
  "metadata": {"route": "rag"},
  "extensions": {}
}
```

### Streaming Response

```bash
curl -X POST http://localhost:8000/v1/responses \
  -H "Content-Type: application/json" \
  -d '{"input": "Hello", "stream": true}'
```

Response (SSE):
```
event: response.created
data: {"id":"resp_abc123","model":"..."}

event: response.output_text.delta
data: {"delta":"Hello"}

event: response.output_text.done
data: {"text":"Hello there!"}

event: response.completed
data: {...}
```

## Agent Extension Points

The orchestrator routes requests to specialized agents:

- **RAG Agent** - RAG response stub with retriever integration points
- **Tool Agent** - Executes tools and returns results (currently a stub, see tool integration examples in docs)
- **Direct Agent** - Generates responses without tools or retrieval

See [docs/extending-agents.md](docs/extending-agents.md) for adding custom agents and tool integrations.

## RAG Document Ingestion

```bash
  curl -X POST http://localhost:8000/v1/documents/upload \
  -F "file=@document.pdf" \
  -F "user_id=user_123"
```

Documents are chunked and embedded during ingestion. The current upload route uses an in-memory vector store for the scaffold path; wire `QdrantVectorStore` into the route for persistent retrieval.

## Current Scaffold Status

- Implemented: OpenAI-style `POST /v1/responses`, SSE streaming from the same endpoint, LangGraph orchestrator skeleton, prompt loading, guardrails, persistence, document ingestion pipeline, observability wrapper, eval runners.
- Partial: RAG retrieval plumbing exists, but the default upload route is not yet wired to persistent Qdrant storage and the shipped RAG agent response remains a scaffold stub.
- Extension point: tool/function calling is not implemented yet; see `docs/extending-agents.md` for a registry-based example and future function-calling notes.

## Observability

When Langfuse credentials are configured, traces are automatically captured for:

- Response creation
- Agent orchestration
- LLM calls
- Tool executions

See [docs/evals.md](docs/evals.md) for evaluation framework.

## Graph Visualization

Generate static images of agent graphs:

```bash
uv run python scripts/export_graphs.py
```

Output: `docs/graphs/*.png`

Images show the structure of:
- Orchestrator routing logic
- RAG agent retrieval flow
- Tool agent execution flow

## Running Evaluations

```bash
# Run eval dataset
uv run python -m app.evals.runners.run_dataset \
  app/evals/datasets/examples/basic_rag_case.yaml

# Output
✅ basic_rag_query: Text contains 'Template'
```

## Testing

```bash
# All tests
uv run pytest

# Specific test file
uv run pytest tests/agents/test_orchestrator_graph.py -v

# Smoke tests
uv run pytest tests/smoke -v

# With coverage
uv run pytest --cov=app --cov-report=html
```

## Docker Compose

```bash
# Start all services
docker compose up --build

# Start specific services
docker compose up -d postgres qdrant

# View logs
docker compose logs -f api

# Stop services
docker compose down
```

Services:
- **api** - FastAPI application (port 8000)
- **postgres** - PostgreSQL database (port 5432)
- **qdrant** - Vector store (ports 6333, 6334)

## Production Checklist

- [ ] Set `APP_DEBUG=false`
- [ ] Use production database URL
- [ ] Configure Langfuse for observability
- [ ] Set up proper authentication (replace auth stub)
- [ ] Configure CORS for frontend
- [ ] Set up rate limiting
- [ ] Configure logging aggregation
- [ ] Set up health check monitoring
- [ ] Run migrations in deployment pipeline
- [ ] Configure backup strategy for PostgreSQL
- [ ] Set up Qdrant persistence volume

## Documentation

- [Architecture](docs/architecture.md) - System design and components
- [Extending Agents](docs/extending-agents.md) - Adding custom agents
- [Prompts](docs/prompts.md) - Prompt engineering guide
- [Providers](docs/providers.md) - LLM provider configuration
- [Evaluations](docs/evals.md) - Evaluation framework
- [Frontend Extensions](docs/frontend-extensions.md) - Frontend integration

## License

MIT
