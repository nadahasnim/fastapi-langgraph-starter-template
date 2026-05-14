# Architecture

## Overview

This template provides a production-ready FastAPI backend for agentic AI services with LangGraph orchestration, RAG capabilities, and observability.

## System Components

```
┌─────────────────────────────────────────────────────────────┐
│                         FastAPI API                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐       │
│  │   Responses  │  │  Documents   │  │    Health    │       │
│  └──────────────┘  └──────────────┘  └──────────────┘       │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    Middleware Layer                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐       │
│  │  Request ID  │  │ Error Handler│  │  Auth Stub   │       │
│  └──────────────┘  └──────────────┘  └──────────────┘       │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                   Response Service                          │
│                  (Observability Wrapper)                    │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                  Orchestrator Graph                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐       │
│  │  RAG Agent   │  │  Tool Agent  │  │ Direct Agent │       │
│  └──────────────┘  └──────────────┘  └──────────────┘       │
└─────────────────────────────────────────────────────────────┘
         │                    │                    │
         ▼                    ▼                    ▼
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│   Qdrant     │    │  Tool System │    │ LLM Provider │
│ (Vector DB)  │    │              │    │ (OpenRouter) │
└──────────────┘    └──────────────┘    └──────────────┘
```

## Request Flow

1. **HTTP Request** arrives at FastAPI endpoint
2. **Middleware** adds request ID, parses auth, handles errors
3. **Response Service** creates trace and invokes orchestrator
4. **Orchestrator** validates input, routes to appropriate agent, validates output
   - Input guardrail checks for blank/unsafe input
   - Router selects agent based on input content
   - Agent executes logic (RAG retrieval, tool call, or direct LLM)
   - Output guardrail validates response text
5. **Response** formatted and returned with metadata

## Data Flow

### Conversation Persistence

```
Request → ResponseService → Orchestrator → Agent
                ↓
         ConversationRepository
                ↓
         MessageRepository
                ↓
         ResponseRepository
                ↓
           PostgreSQL
```

### RAG Pipeline

```
Document Upload → Chunking → Embedding → Qdrant Storage
                                              ↓
User Query → RAG Agent → Retrieval → Context → LLM → Response
```

## Key Design Decisions

### Modular Agent Architecture

Agents are isolated graph nodes with clear responsibilities:

- **RAG Agent**: Document retrieval + generation
- **Tool Agent**: Tool execution + result formatting (currently a stub, extensible via tool registry pattern)
- **Direct Agent**: Pure LLM generation

This allows independent testing and extension without coupling.

### Observability as Optional

Langfuse tracing is wrapped in `Observability` class that safely degrades to no-op when credentials are absent. This allows development without observability infrastructure.

### Structured Error Handling

`AppError` provides consistent error responses:

```json
{
  "error": {
    "code": "bad_request",
    "message": "Invalid input"
  }
}
```

### Streaming Support

Responses support SSE streaming for real-time output:

- `response.created` - Initial metadata
- `response.output.text.delta` - Incremental text
- `response.output.text.done` - Complete text
- `response.completed` - Final response object

## Database Schema

### Conversations

- `id` (UUID)
- `user_id` (String, nullable)
- `title` (String)
- `created_at`, `updated_at`

### Messages

- `id` (UUID)
- `conversation_id` (FK)
- `role` (String: user/assistant)
- `content` (Text)
- `metadata` (JSONB)
- `created_at`

### Responses

- `id` (UUID)
- `conversation_id` (FK)
- `message_id` (FK)
- `model` (String)
- `output` (JSONB)
- `metadata` (JSONB)
- `extensions` (JSONB)
- `response_id` (String, unique)
- `created_at`

### Documents

- `id` (UUID)
- `filename` (String)
- `content_type` (String)
- `size_bytes` (Integer)
- `metadata` (JSONB)
- `created_at`

### Document Chunks

- `id` (UUID)
- `document_id` (FK)
- `chunk_index` (Integer)
- `text` (Text)
- `metadata` (JSONB)
- `vector_id` (String, unique)
- `created_at`

## Extension Points

1. **Custom Agents** - Add nodes to orchestrator graph
2. **Custom Tools** - Implement tool interface and register in tool agent (see `docs/extending-agents.md` for examples)
3. **Custom Loaders** - Add document loaders
4. **Custom Embeddings** - Swap embedding provider
5. **Custom LLM Provider** - Implement LlmProvider protocol
6. **Custom Middleware** - Add FastAPI middleware
7. **Custom Evaluations** - Add eval checks and judges

## Security Considerations

- **Auth Stub**: Replace with real authentication
- **Input Validation**: Guardrails validate input/output
- **SQL Injection**: SQLAlchemy ORM prevents injection
- **CORS**: Configure for production frontend
- **Rate Limiting**: Add rate limiting middleware
- **Secrets**: Use environment variables, never commit

## Performance Considerations

- **Connection Pooling**: SQLAlchemy manages DB connections
- **Vector Search**: Qdrant provides fast similarity search
- **Streaming**: Reduces time-to-first-token
- **Async**: FastAPI + asyncio for concurrent requests
- **Caching**: Add Redis for response caching

## Monitoring

- **Health Endpoint**: `/v1/health` for uptime checks
- **Request IDs**: Track requests across services
- **Langfuse Traces**: Observe LLM calls and agent execution
- **Structured Errors**: Consistent error format for alerting
- **Logs**: Structured logging for aggregation
