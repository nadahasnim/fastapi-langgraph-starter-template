# Agent Backend Template

Reusable FastAPI backend starter for agentic AI services.

## Stack

- FastAPI
- uv
- pytest
- ruff
- PostgreSQL
- Qdrant
- Docker Compose

## Local Setup

```bash
uv sync
uv run pytest
uv run ruff check .
uv run uvicorn app.main:app --reload
```

## Health Check

```bash
curl http://localhost:8000/v1/health
```

Expected response:

```json
{"status":"ok"}
```

## Docker

```bash
docker compose up --build
```

The local Docker Compose stack starts:

- `api` on port `8000`
- `postgres` on port `5432`
- `qdrant` on ports `6333` and `6334`

## Current Milestone

Milestone 1 provides the foundation scaffold only. API persistence, LangGraph agents, RAG,
Langfuse, and eval tooling are planned for later milestone branches.
