Yes — put evaluator under `evals/`, not `agents/`.

Here is the markdown you can copy into a file like:

```txt
AGENT_BACKEND_SCAFFOLD_PLAN.md
```

````md
# Agent Backend Scaffold Plan

## 1. Goal

Build a reusable backend starter template for agentic AI projects.

The scaffold should provide company-wide standards for building FastAPI-based agent services using LangGraph/LangChain, OpenRouter, Qdrant, PostgreSQL, Langfuse, SQLAlchemy, Alembic, pytest, and file-based prompts.

This project is a template, not a business-specific implementation.

The first implementation should contain generic example agents such as:

- Orchestrator agent
- RAG agent
- Tool agent
- Evaluator system

Avoid client-specific agents like service card agent or journey map agent in the template.

---

## 2. Main Requirements

### Backend Server Goals

The backend should support:

1. OpenAI-compatible endpoint patterns.
2. Non-breaking custom response extensions for frontend rendering.
3. Streaming response support using SSE.
4. Structured FastAPI architecture:
   - route
   - service
   - repository
   - DTO/schema
   - dependency injection
   - middleware
5. Async SQLAlchemy.
6. Alembic migrations.
7. PostgreSQL.
8. Qdrant vector database.
9. Langfuse observability.
10. Easy testing with pytest.
11. Clean linting and formatting using ruff.
12. Dependency and project management using uv.

---

## 3. Agent Goals

The agent system should support:

1. LangGraph as the main agent runtime.
2. LangGraph subgraphs for sub-agents.
3. Generic orchestrator that can route user intent.
4. RAG flow using Qdrant.
5. Tool calling.
6. Guardrails for input and output.
7. Short-term memory using PostgreSQL conversation/message tables.
8. Long-term memory interface, with PostgreSQL implementation first.
9. File-based prompt management.
10. Jinja2 prompt rendering.
11. OpenAI-compatible LLM calls through OpenRouter.
12. OpenAI-compatible embeddings through OpenRouter.
13. Evaluation system with deterministic checks and LLM-as-judge checks.

---

## 4. Tech Stack

Use:

- Python
- uv
- FastAPI
- Pydantic
- pydantic-settings
- SQLAlchemy async
- Alembic
- PostgreSQL
- Qdrant
- LangGraph
- LangChain
- OpenAI SDK with OpenRouter base URL
- Langfuse
- Jinja2
- httpx
- pytest
- pytest-asyncio
- ruff
- Docker Compose

---

## 5. Architecture Layers

Use this architecture:

```txt
API Layer
→ Service Layer
→ Agent Runtime Layer
→ Infrastructure Layer
```
````

FastAPI routes should not call LangGraph directly.

Instead:

```txt
route
→ service
→ agent runtime / repository / external provider
```

Example:

```txt
POST /v1/responses
→ ResponseService
→ OrchestratorGraph
→ RagAgent subgraph / ToolAgent subgraph
→ ResponseFormatter
```

---

## 6. Endpoint Design

### Main endpoint

Use:

```txt
POST /v1/responses
```

Reason:

The `/responses` endpoint follows the modern OpenAI-style response pattern and gives enough flexibility for:

- text response
- streaming response
- tool calls
- metadata
- custom frontend extensions
- future multimodal output

---

## 7. Response Extension Strategy

The API should remain OpenAI-compatible as much as possible.

Custom frontend fields should be added using a non-breaking `extensions` field.

Example response:

```json
{
  "id": "resp_123",
  "object": "response",
  "model": "openrouter/anthropic/claude-sonnet",
  "output": [
    {
      "type": "message",
      "role": "assistant",
      "content": [
        {
          "type": "output_text",
          "text": "Here is the answer."
        }
      ]
    }
  ],
  "usage": {
    "input_tokens": 100,
    "output_tokens": 200,
    "total_tokens": 300
  },
  "metadata": {},
  "extensions": {
    "ui": {
      "component": "generic_card",
      "props": {}
    },
    "artifact": {
      "type": "generic_artifact",
      "data": {}
    }
  }
}
```

---

## 8. Streaming Design

Support SSE streaming.

Example events:

```txt
response.created
response.output_text.delta
response.output_text.done
response.extension.delta
response.completed
response.failed
```

The scaffold should include a streaming example from the `/v1/responses` endpoint.

---

## 9. Proposed Folder Structure

```txt
app/
  main.py

  core/
    config.py
    logging.py
    errors.py
    observability.py

  api/
    v1/
      routes/
        responses.py
        conversations.py
        documents.py
        health.py
      schemas/
        responses.py
        conversations.py
        documents.py

  middleware/
    auth_stub.py
    request_id.py
    error_handler.py

  services/
    response_service.py
    conversation_service.py
    document_ingestion_service.py

  repositories/
    conversation_repo.py
    message_repo.py
    document_repo.py
    memory_repo.py

  db/
    base.py
    session.py
    models/
      conversation.py
      message.py
      document.py
      memory.py

  agents/
    orchestrator/
      graph.py
      state.py
      prompts/
        system.md
        router.md

    rag_agent/
      graph.py
      state.py
      prompts/
        system.md
        answer.md

    tool_agent/
      graph.py
      state.py
      prompts/
        system.md

    shared/
      llm.py
      prompt_loader.py
      guardrails.py
      tools.py
      events.py
      response_formatter.py

  rag/
    embeddings.py
    qdrant.py
    retriever.py
    chunking.py
    loaders/
      markdown_loader.py
      text_loader.py
      pdf_loader.py

  evals/
    datasets/
      examples/
        basic_rag_case.yaml
        tool_call_case.yaml

    judges/
      judge_service.py
      prompts/
        factuality.md
        format_compliance.md
        safety.md

    deterministic/
      test_response_shape.py
      test_tool_routing.py

    runners/
      run_dataset.py
      generate_report.py

    reports/
      .gitkeep

tests/
  api/
  services/
  agents/
  rag/
  evals/

alembic/
  versions/

docker-compose.yml
Dockerfile
.env.example
pyproject.toml
README.md
```

---

## 10. Why Evaluator Should Not Live Inside `agents/`

The evaluator uses LLM calls, but it is not part of the user-facing runtime agent flow.

Runtime agents live here:

```txt
app/agents/
```

Evaluation tools live here:

```txt
app/evals/
```

Reason:

- Runtime agents serve user requests.
- Evaluators test agent quality.
- Evaluators may run in pytest, CI, or manual scripts.
- Evaluators generate reports.
- Evaluators should not pollute production agent orchestration.
- Langfuse should receive eval scores, but should not be the eval engine.

Recommended pattern:

```txt
test case files
→ run agent
→ collect actual output
→ deterministic checks
→ LLM judge checks
→ generate report
→ optionally log scores to Langfuse
```

---

## 11. Evaluation System

The evaluation system should support two types of evaluation.

### 11.1 Deterministic Evaluation

Used for checks like:

- response has required JSON shape
- required fields exist
- tool was called
- output contains expected keyword
- response extension is valid
- no forbidden field appears

Example:

```yaml
id: basic_rag_case
input: "What is this document about?"
expected:
  must_include:
    - "policy"
  response_shape:
    - "output"
    - "extensions"
```

### 11.2 LLM-as-Judge Evaluation

Used for softer checks like:

- factuality
- helpfulness
- safety
- format compliance
- relevance
- groundedness to retrieved context

Example output:

```json
{
  "score": 0.87,
  "verdict": "pass",
  "reasoning": "The answer is grounded and follows the requested format."
}
```

The evaluator should be implemented as a separate service:

```txt
app/evals/judges/judge_service.py
```

Not as a runtime agent inside `app/agents`.

---

## 12. Eval Dataset Format

Support YAML test cases first.

Example:

```yaml
id: rag_policy_question_001
name: Basic RAG policy question
type: rag

input:
  user_id: "test-user"
  message: "Summarize the uploaded policy document."

expected:
  must_include:
    - "policy"
    - "summary"

judge:
  enabled: true
  criteria:
    - factuality
    - groundedness
    - format_compliance

metadata:
  tags:
    - rag
    - smoke-test
```

---

## 13. Prompt Management

Use file-based prompts.

Use Jinja2 for variable injection.

Example prompt file:

```md
You are a helpful RAG assistant.

User question:
{{ user_question }}

Retrieved context:
{{ retrieved_context }}

Conversation summary:
{{ conversation_summary }}

Rules:

- Answer only using the retrieved context.
- If the context is insufficient, ask for clarification.
```

Prompt loader should support:

- loading `.md` prompt files
- rendering variables with Jinja2
- optionally composing multiple prompt parts

Example:

```txt
system.md
router.md
guardrails.md
```

---

## 14. LLM Provider

Use OpenAI SDK with OpenRouter.

Create a provider wrapper:

```txt
app/agents/shared/llm.py
```

It should support:

- chat completion
- streaming chat completion
- embeddings
- model configuration from environment variables

Example environment variables:

```env
OPENROUTER_API_KEY=
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
DEFAULT_CHAT_MODEL=
DEFAULT_EMBEDDING_MODEL=
```

---

## 15. Embeddings

Use OpenRouter-compatible embedding API by default.

Embedding flow:

```txt
document text
→ chunk text
→ convert chunks into vector embeddings
→ store vectors in Qdrant
```

Query flow:

```txt
user question
→ convert question into vector embedding
→ search similar chunks in Qdrant
→ inject retrieved chunks into RAG prompt
→ generate answer
```

Create an interface so embedding providers can be swapped later.

Example:

```txt
EmbeddingProvider
→ OpenRouterEmbeddingProvider
```

---

## 16. RAG

Use Qdrant as the vector database.

Scaffold should include:

- Qdrant client
- collection setup
- document chunking
- markdown loader
- text loader
- PDF loader
- embedding generation
- vector upsert
- vector search
- RAG agent example

Only include simple ingestion examples:

1. Markdown/TXT ingestion
2. PDF ingestion

Do not include DOCX in the first scaffold unless necessary.

---

## 17. Memory

### Short-Term Memory

Use PostgreSQL.

Tables:

```txt
conversations
messages
```

Purpose:

- current chat session
- persistent conversation history
- reload previous session

### Long-Term Memory

Use PostgreSQL first.

Table:

```txt
memories
```

Create a provider interface:

```python
class LongTermMemoryProvider:
    async def search(self, user_id: str, query: str):
        pass

    async def save(self, user_id: str, memory: str):
        pass
```

Do not add mem0 in v1.

Keep the architecture open so mem0 can be added later.

---

## 18. LangGraph Design

Use LangGraph for the agent runtime.

Main graph:

```txt
OrchestratorGraph
```

Subgraphs:

```txt
RagAgentGraph
ToolAgentGraph
```

High-level flow:

```txt
input
→ input guardrail
→ intent router
→ clarification check
→ RAG subgraph OR tool subgraph OR direct answer
→ output guardrail
→ response formatter
```

The orchestrator should be able to decide:

- answer directly
- ask clarification
- call RAG agent
- call tool agent
- reject unsafe input
- format final response

---

## 19. Guardrails

Implement simple guardrails first.

### Input guardrails

Examples:

- reject empty messages
- reject unsupported file types
- limit message length
- block obvious prompt injection patterns
- block unsupported task types

### Output guardrails

Examples:

- validate response schema
- ensure extensions follow expected shape
- ensure no internal prompt leakage
- ensure output is safe
- ensure output is not empty

Keep guardrails modular.

---

## 20. Middleware

Add middleware slots even if auth is not implemented yet.

Initial middleware:

```txt
request_id.py
error_handler.py
auth_stub.py
```

`auth_stub.py` should not enforce real authentication yet.

It should only show the pattern for future auth.

---

## 21. Database Models

Initial tables:

```txt
conversations
messages
documents
document_chunks
memories
```

Example purpose:

```txt
conversations
- id
- user_id
- title
- created_at
- updated_at

messages
- id
- conversation_id
- role
- content
- metadata
- created_at

documents
- id
- user_id
- filename
- content_type
- source
- created_at

document_chunks
- id
- document_id
- chunk_index
- content
- qdrant_point_id
- metadata
- created_at

memories
- id
- user_id
- content
- metadata
- created_at
- updated_at
```

---

## 22. Docker Compose

Local Docker Compose should include:

```txt
api
postgres
qdrant
```

Optional later:

```txt
redis
worker
```

Do not add worker/queue system in v1 unless needed.

---

## 23. Environment Variables

Example:

```env
APP_ENV=local
APP_NAME=agent-backend-template
APP_DEBUG=true

DATABASE_URL=postgresql+asyncpg://postgres:postgres@postgres:5432/agent_db

OPENROUTER_API_KEY=
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
DEFAULT_CHAT_MODEL=
DEFAULT_EMBEDDING_MODEL=

QDRANT_URL=http://qdrant:6333
QDRANT_COLLECTION=documents

LANGFUSE_PUBLIC_KEY=
LANGFUSE_SECRET_KEY=
LANGFUSE_HOST=
```

---

## 24. Testing Requirements

Add example tests for:

```txt
health endpoint
responses endpoint
response schema validation
prompt loader
RAG chunking
embedding provider mock
Qdrant retriever mock
orchestrator routing
deterministic eval checks
LLM judge service mock
```

Use mocks for LLM calls in unit tests.

Do not require real OpenRouter calls for normal test suite.

---

## 25. What Codex Should Build First

Build in this order:

1. Project setup with uv, ruff, pytest.
2. FastAPI app structure.
3. Config system.
4. Async SQLAlchemy setup.
5. Alembic setup.
6. Basic models and repositories.
7. `/health` endpoint.
8. `/v1/responses` non-streaming endpoint.
9. `/v1/responses` streaming SSE endpoint.
10. OpenRouter LLM provider wrapper.
11. Jinja2 prompt loader.
12. LangGraph orchestrator skeleton.
13. RAG agent skeleton.
14. Tool agent skeleton.
15. Qdrant client and retriever.
16. Markdown/TXT/PDF ingestion examples.
17. Langfuse observability wrapper.
18. Eval system with YAML datasets.
19. Deterministic eval examples.
20. LLM-as-judge eval examples.
21. Report generation.
22. README usage guide.

---

## 26. Done Definition

The scaffold is done when:

- The app runs locally with Docker Compose.
- PostgreSQL and Qdrant run locally.
- Alembic migrations work.
- `/health` works.
- `/v1/responses` works.
- `/v1/responses` can stream SSE.
- A generic orchestrator graph exists.
- A generic RAG graph exists.
- A generic tool agent graph exists.
- Prompt files can be loaded and rendered using Jinja2.
- Documents can be ingested from markdown/txt and PDF.
- Chunks can be embedded and stored in Qdrant.
- RAG agent can retrieve context and answer.
- Langfuse tracing is integrated.
- Tests run with pytest.
- Eval cases can be run from YAML files.
- Eval report can be generated.
- README explains how to extend the scaffold.

---

## 27. Codex Instruction Summary

Build a production-style reusable FastAPI LangGraph agent backend template.

Use:

- async FastAPI
- async SQLAlchemy
- Alembic
- PostgreSQL
- Qdrant
- LangGraph
- OpenRouter
- Langfuse
- Jinja2 prompt files
- pytest
- ruff
- uv
- Docker Compose

The template should include generic examples only:

- orchestrator agent
- RAG agent
- tool agent
- evaluator system

Do not implement client-specific business logic.

Follow this architecture:

```txt
route
→ service
→ repository / agent runtime / provider
```

Implement `/v1/responses` with both normal JSON and SSE streaming.

Support custom frontend fields through a non-breaking `extensions` object.

Keep evaluator logic outside runtime agents under `app/evals`.

The evaluator should support YAML test cases, deterministic checks, LLM-as-judge checks, and report generation.

```

```
