# Milestone 6 Docs Hardening Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Harden the template for company-wide reuse with middleware, error handling, smoke tests, README expansion, and extension guides.

**Architecture:** Keep runtime behavior modular while adding production-facing polish: request IDs, structured errors, auth stub, complete documentation, and final verification commands. Documentation explains extension points without introducing client-specific agent logic.

**Tech Stack:** FastAPI middleware, pytest, Docker Compose, Markdown docs, uv, ruff.

---

## File Structure

- Create `app/middleware/request_id.py`, `error_handler.py`, and `auth_stub.py`.
- Modify `app/main.py` to register middleware.
- Modify `app/core/errors.py` for structured application errors.
- Expand `README.md`.
- Create `docs/architecture.md`, `docs/extending-agents.md`, `docs/prompts.md`, `docs/providers.md`, `docs/evals.md`, and `docs/frontend-extensions.md`.
- Create smoke tests under `tests/smoke/test_template_smoke.py` and middleware tests under `tests/middleware/`.
- Update `HANDOVER.md` with final scaffold state if needed.

## Task 1: Add Request ID Middleware

**Files:**
- Create: `app/middleware/request_id.py`
- Modify: `app/main.py`
- Create: `tests/middleware/test_request_id.py`

- [ ] **Step 1: Write request ID tests**

```python
from fastapi.testclient import TestClient

from app.main import create_app


def test_request_id_header_is_added_when_missing():
    client = TestClient(create_app())

    response = client.get("/v1/health")

    assert response.headers["x-request-id"]


def test_request_id_header_is_preserved_when_supplied():
    client = TestClient(create_app())
    response = client.get("/v1/health", headers={"x-request-id": "req_test"})
    assert response.headers["x-request-id"] == "req_test"
```

- [ ] **Step 2: Run tests to verify failure**

Run: `uv run pytest tests/middleware/test_request_id.py -v`
Expected: fail because middleware does not exist.

- [ ] **Step 3: Implement and register middleware**

Create middleware that reads incoming `x-request-id` or creates `uuid4().hex`, stores it in `request.state.request_id`, and adds it to the response header.

- [ ] **Step 4: Run tests and commit**

Run: `uv run pytest tests/middleware/test_request_id.py -v`
Expected: pass.

```bash
git add app/middleware/request_id.py app/main.py tests/middleware/test_request_id.py
git commit -m "feat: add request id middleware"
```

## Task 2: Add Error Handler Middleware

**Files:**
- Modify: `app/core/errors.py`
- Create: `app/middleware/error_handler.py`
- Modify: `app/main.py`
- Create: `tests/middleware/test_error_handler.py`

- [ ] **Step 1: Write error handler tests**

```python
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.core.errors import AppError
from app.middleware.error_handler import register_error_handlers


def test_app_error_returns_structured_json():
    app = FastAPI()
    register_error_handlers(app)

    @app.get("/boom")
    async def boom():
        raise AppError(message="Bad request", status_code=400, code="bad_request")

    response = TestClient(app).get("/boom")

    assert response.status_code == 400
    assert response.json()["error"]["code"] == "bad_request"
    assert response.json()["error"]["message"] == "Bad request"
```

- [ ] **Step 2: Run tests to verify failure**

Run: `uv run pytest tests/middleware/test_error_handler.py -v`
Expected: fail until structured error support exists.

- [ ] **Step 3: Implement error handling**

`AppError` should accept `message`, `status_code`, and `code`. `register_error_handlers(app)` should convert `AppError` to `{"error": {"code": code, "message": message}}` and return HTTP 500 for unexpected exceptions with code `internal_error`.

- [ ] **Step 4: Run tests and commit**

Run: `uv run pytest tests/middleware/test_error_handler.py -v`
Expected: pass.

```bash
git add app/core/errors.py app/middleware/error_handler.py app/main.py tests/middleware/test_error_handler.py
git commit -m "feat: add structured error handling"
```

## Task 3: Add Auth Stub Middleware

**Files:**
- Create: `app/middleware/auth_stub.py`
- Modify: `app/main.py`
- Create: `tests/middleware/test_auth_stub.py`

- [ ] **Step 1: Write auth stub tests**

```python
from fastapi.testclient import TestClient

from app.main import create_app


def test_auth_stub_does_not_block_requests():
    client = TestClient(create_app())
    response = client.get("/v1/health")
    assert response.status_code == 200


def test_auth_stub_accepts_bearer_token_pattern():
    client = TestClient(create_app())
    response = client.get("/v1/health", headers={"authorization": "Bearer test-token"})
    assert response.status_code == 200
```

- [ ] **Step 2: Run tests to verify failure**

Run: `uv run pytest tests/middleware/test_auth_stub.py -v`
Expected: fail until middleware exists or is registered.

- [ ] **Step 3: Implement auth stub**

Middleware should parse the `Authorization` header when present and set `request.state.auth_token`; it must not enforce authentication in this template milestone.

- [ ] **Step 4: Run tests and commit**

Run: `uv run pytest tests/middleware/test_auth_stub.py -v`
Expected: pass.

```bash
git add app/middleware/auth_stub.py app/main.py tests/middleware/test_auth_stub.py
git commit -m "feat: add auth stub middleware"
```

## Task 4: Expand README And Extension Guides

**Files:**
- Modify: `README.md`
- Create: `docs/architecture.md`
- Create: `docs/extending-agents.md`
- Create: `docs/prompts.md`
- Create: `docs/providers.md`
- Create: `docs/evals.md`
- Create: `docs/frontend-extensions.md`
- Create: `tests/smoke/test_docs_exist.py`

- [ ] **Step 1: Write docs smoke test**

```python
from pathlib import Path


def test_required_docs_exist():
    required = [
        "README.md",
        "docs/architecture.md",
        "docs/extending-agents.md",
        "docs/prompts.md",
        "docs/providers.md",
        "docs/evals.md",
        "docs/frontend-extensions.md",
    ]
    for path in required:
        assert Path(path).exists(), path


def test_docs_do_not_include_client_specific_agent_names():
    forbidden = ["service " + "card agent", "journey " + "map agent"]
    text = "\n".join(Path(path).read_text(encoding="utf-8").lower() for path in Path("docs").glob("*.md"))
    for phrase in forbidden:
        assert phrase not in text
```

- [ ] **Step 2: Run docs test to verify failure**

Run: `uv run pytest tests/smoke/test_docs_exist.py -v`
Expected: fail because docs do not exist yet.

- [ ] **Step 3: Write docs**

README should cover setup, env vars, Docker Compose, tests, API examples, streaming example, agent extension points, RAG ingestion, observability, evals, and production checklist. Each docs file should focus on its title and use generic examples such as `generic_card` and `generic_artifact`.

- [ ] **Step 4: Run docs test and commit**

Run: `uv run pytest tests/smoke/test_docs_exist.py -v`
Expected: pass.

```bash
git add README.md docs/architecture.md docs/extending-agents.md docs/prompts.md docs/providers.md docs/evals.md docs/frontend-extensions.md tests/smoke/test_docs_exist.py
git commit -m "docs: add template extension guides"
```

## Task 5: Add Template Smoke Tests

**Files:**
- Create: `tests/smoke/test_template_smoke.py`
- Modify: `README.md`

- [ ] **Step 1: Write smoke tests**

```python
from fastapi.testclient import TestClient

from app.main import create_app


def test_template_core_endpoints_are_available():
    client = TestClient(create_app())

    assert client.get("/v1/health").status_code == 200
    assert client.post("/v1/responses", json={"input": "Hello"}).status_code == 200


def test_streaming_response_smoke():
    client = TestClient(create_app())
    with client.stream("POST", "/v1/responses", json={"input": "Hello", "stream": True}) as response:
        body = "".join(response.iter_text())
    assert response.status_code == 200
    assert "response.completed" in body
```

- [ ] **Step 2: Run smoke tests**

Run: `uv run pytest tests/smoke/test_template_smoke.py -v`
Expected: pass if prior milestones are complete.

- [ ] **Step 3: Document smoke command**

Add `uv run pytest tests/smoke -v` to README verification section.

- [ ] **Step 4: Commit**

```bash
git add tests/smoke/test_template_smoke.py README.md
git commit -m "test: add template smoke tests"
```

## Task 6: Final Hardening Verification

**Files:**
- Review: all project files
- Modify: `HANDOVER.md` if current branch needs final status notes

- [ ] **Step 1: Run dependency sync**

Run: `uv sync`
Expected: environment is in sync with `uv.lock`.

- [ ] **Step 2: Run full tests**

Run: `uv run pytest`
Expected: all tests pass.

- [ ] **Step 3: Run lint**

Run: `uv run ruff check .`
Expected: all checks pass.

- [ ] **Step 4: Validate Docker Compose**

Run: `docker compose config`
Expected: compose renders successfully.

- [ ] **Step 5: Verify migrations**

Run: `docker compose up -d postgres qdrant`
Run: `uv run alembic upgrade head`
Expected: migrations apply and services stay running.

- [ ] **Step 6: Run eval smoke**

Run: `uv run python -m app.evals.runners.run_dataset app/evals/datasets/examples/basic_rag_case.yaml`
Expected: eval runner prints case results without real LLM credentials.

- [ ] **Step 7: Commit final notes if changed**

```bash
git add HANDOVER.md README.md docs tests
git commit -m "docs: finalize template handoff"
```
