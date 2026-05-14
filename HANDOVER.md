# Handover: Continue Milestone 2

## Current State

- Repository path: `/Users/nadahasni/Developer/Personal/agentic-backend-template`
- Current branch: `main`
- Milestone 1 has been merged into `main` locally.
- The completed milestone branch `milestone/01-foundation-scaffold` was deleted after merge.
- No remote/PR workflow has been set up or confirmed.
- `HANDOVER.md` is the only new handover file for the next session and may be uncommitted unless the current session commits it later.

## Recent Commits

- `46b7898 feat: add foundation scaffold`
- `157467f docs: add initial scaffold plan`

## What Is Already Done

- Initialized git on `main`.
- Added original planning docs:
  - `PLAN.md`
  - `PROBLEMS.md`
- Built Milestone 1 foundation scaffold:
  - `pyproject.toml` with `uv`, FastAPI, pydantic-settings, pytest, pytest-asyncio, httpx, ruff.
  - `uv.lock`.
  - FastAPI app factory in `app/main.py`.
  - Versioned API router under `app/api/v1/router.py`.
  - Health route at `GET /v1/health` returning `{"status": "ok"}`.
  - Core modules:
    - `app/core/config.py`
    - `app/core/logging.py`
    - `app/core/errors.py`
  - Test for health endpoint in `tests/api/test_health.py`.
  - `.env.example`.
  - `.gitignore` and `.dockerignore`.
  - `Dockerfile`.
  - `docker-compose.yml` with `api`, `postgres`, and `qdrant` services.
  - `README.md` quickstart.

## Verified So Far

Verification was run on merged `main` after Milestone 1 merge:

- `uv run pytest`: 1 passed
- `uv run ruff check .`: passed
- `docker compose config`: passed

Run these again before starting substantial Milestone 2 work if the workspace changed.

## Important Decisions

- Keep the scaffold generic. Do not implement service-card or journey-map business logic directly.
- Support custom frontend output through an OpenAI-compatible `extensions` object.
- Follow this architecture:
  - route
  - service
  - repository / agent runtime / external provider
- Keep evaluator code under `app/evals`, not under `app/agents`.
- Use TDD for new behavior.
- Prefer small, milestone-sized branches and commits.
- Planned branch naming pattern: `milestone/02-api-persistence`, `milestone/03-agent-runtime`, etc.

## Suggested Next Branch

Create a new branch from `main`:

```bash
git switch -c milestone/02-api-persistence
```

If using `rtk git` in this environment:

```bash
rtk git switch -c milestone/02-api-persistence
```

## Milestone 2 Goal

Implement API + Persistence foundation.

This milestone should add enough structure for OpenAI-style `/v1/responses` requests, persistence-backed conversations/messages/responses, and SSE streaming examples without adding LangGraph/OpenRouter runtime yet.

## Milestone 2 Scope

- Add request/response schemas under `app/api/v1/schemas/`.
- Add `/v1/responses` route under `app/api/v1/routes/responses.py`.
- Add `ResponseService` under `app/services/response_service.py`.
- Add async SQLAlchemy setup.
- Add Alembic setup.
- Add basic database models and repositories.
- Add non-streaming `POST /v1/responses` endpoint.
- Add SSE streaming support for `POST /v1/responses` when requested.
- Add tests for:
  - response schema validation
  - non-streaming responses endpoint
  - streaming SSE responses endpoint
  - repository/model basics where useful

## Suggested Milestone 2 File Layout

```txt
app/
  api/
    v1/
      routes/
        responses.py
      schemas/
        responses.py
  db/
    base.py
    session.py
  models/
    conversation.py
    message.py
    response.py
  repositories/
    conversation_repository.py
    message_repository.py
    response_repository.py
  services/
    response_service.py
alembic/
  env.py
  versions/
alembic.ini
tests/
  api/
    test_responses.py
  services/
    test_response_service.py
```

Keep this minimal. Only add files needed by Milestone 2.

## `/v1/responses` Shape To Preserve

Reference from `PLAN.md`: the response should stay OpenAI-compatible where possible and put custom frontend fields inside `extensions`.

Example response shape:

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

Do not hard-code client-specific components like service cards or journey maps. Use generic examples only.

## Streaming Events To Support

Use SSE events from `PLAN.md` as the target vocabulary:

- `response.created`
- `response.output_text.delta`
- `response.output_text.done`
- `response.extension.delta`
- `response.completed`
- `response.failed`

For Milestone 2, a deterministic placeholder response stream is acceptable. LangGraph/OpenRouter integration belongs in Milestone 3.

## Persistence Guidance

- Use async SQLAlchemy.
- Use PostgreSQL URL from existing config: `DATABASE_URL`.
- Add Alembic migrations that can run against the Compose Postgres service.
- Keep models generic and reusable, likely around:
  - conversations
  - messages
  - responses
- Do not add RAG, Qdrant document models, or LangGraph runtime in this milestone unless needed for API contracts.

## TDD Starting Point

Start with failing tests before implementation. Suggested first tests:

- `POST /v1/responses` with a simple user input returns `200` and `object == "response"`.
- Response contains `id`, `model`, `output`, `usage`, `metadata`, and `extensions`.
- `stream=true` returns `text/event-stream` and emits `response.created` and `response.completed`.
- Invalid request payload returns FastAPI validation error.

Then implement the smallest code to pass.

## Recommended Commands

```bash
uv sync
uv run pytest
uv run ruff check .
docker compose config
```

For DB work, likely commands after Alembic is added:

```bash
docker compose up -d postgres
uv run alembic upgrade head
```

## Completion Criteria For Milestone 2

- `uv run pytest` passes.
- `uv run ruff check .` passes.
- `docker compose config` passes.
- Alembic migration can be applied to local Compose Postgres.
- `POST /v1/responses` works for non-streaming JSON.
- `POST /v1/responses` works for SSE streaming.
- No real LLM/OpenRouter calls are required for tests.
- No client-specific service-card/journey-map logic is introduced.

## Notes For Next Agent

- Use the existing `create_app()` factory in `app/main.py`.
- Register new routes through `app/api/v1/router.py`.
- Existing config is in `app/core/config.py`; extend it rather than duplicating env parsing.
- Keep dependencies in `pyproject.toml` and update `uv.lock` with `uv sync` after adding packages.
- The user wants a reusable company-wide backend agent template, not a one-off application.
- Read `PLAN.md` before making Milestone 2 changes, especially sections around endpoint design, folder structure, and done definition.
