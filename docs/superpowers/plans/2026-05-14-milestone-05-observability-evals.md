# Milestone 5 Observability Evals Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add optional Langfuse tracing and a reusable evaluation system with YAML datasets, deterministic checks, LLM-as-judge checks, and report generation.

**Architecture:** Observability is isolated behind `app/core/observability.py` and is safe when credentials are absent. Evaluation code lives under `app/evals`, outside `app/agents`, and runs through explicit runner modules rather than production request paths.

**Tech Stack:** Langfuse, PyYAML, pytest, Pydantic, FastAPI middleware hooks, existing agent runtime, uv, ruff.

---

## File Structure

- Create `app/core/observability.py`.
- Modify `app/core/config.py` for Langfuse config.
- Modify `app/services/response_service.py` and agent runtime to use trace hooks.
- Create `app/evals/datasets/examples/basic_rag_case.yaml` and `tool_call_case.yaml`.
- Create `app/evals/deterministic/checks.py`.
- Create `app/evals/judges/judge_service.py` and judge prompts.
- Create `app/evals/runners/run_dataset.py` and `generate_report.py`.
- Create `app/evals/reports/.gitkeep`.
- Add tests under `tests/evals/` and observability tests under `tests/core/`.

## Task 1: Add Optional Langfuse Observability Wrapper

**Files:**
- Modify: `pyproject.toml`
- Modify: `uv.lock`
- Modify: `app/core/config.py`
- Create: `app/core/observability.py`
- Create: `tests/core/test_observability.py`

- [ ] **Step 1: Write observability tests**

```python
from app.core.observability import NoopTrace, Observability


def test_observability_uses_noop_when_disabled():
    observability = Observability(enabled=False)

    trace = observability.start_trace(name="test", metadata={"case": "disabled"})

    trace.update(output={"ok": True})
    trace.end()

    assert isinstance(trace, NoopTrace)


def test_observability_context_manager_is_safe_when_disabled():
    observability = Observability(enabled=False)

    with observability.trace(name="request", metadata={}) as trace:
        trace.update(input={"message": "hello"})

    assert isinstance(trace, NoopTrace)
```

- [ ] **Step 2: Run tests to verify failure**

Run: `uv run pytest tests/core/test_observability.py -v`
Expected: fail because observability module does not exist.

- [ ] **Step 3: Add dependency and config**

Add `langfuse>=2.57.0` to dependencies. Add config fields `langfuse_public_key`, `langfuse_secret_key`, and `langfuse_host`. Implement `Observability`, `NoopTrace`, and `LangfuseTrace` wrapper classes.

- [ ] **Step 4: Run tests and commit**

Run: `uv sync`
Run: `uv run pytest tests/core/test_observability.py -v`
Expected: pass.

```bash
git add pyproject.toml uv.lock app/core/config.py app/core/observability.py tests/core/test_observability.py
git commit -m "feat: add optional observability wrapper"
```

## Task 2: Trace Response And Agent Execution

**Files:**
- Modify: `app/services/response_service.py`
- Modify: `app/agents/orchestrator/graph.py`
- Create: `tests/services/test_response_tracing.py`

- [ ] **Step 1: Write tracing test**

```python
import pytest

from app.api.v1.schemas.responses import ResponseCreateRequest
from app.core.observability import Observability
from app.services.response_service import ResponseService


@pytest.mark.asyncio
async def test_response_service_accepts_observability_without_credentials():
    service = ResponseService(default_model="test-model", observability=Observability(enabled=False))

    response = await service.create_response(ResponseCreateRequest(input="Hello"))

    assert response.object == "response"
```

- [ ] **Step 2: Run test to verify failure**

Run: `uv run pytest tests/services/test_response_tracing.py -v`
Expected: fail until service accepts observability.

- [ ] **Step 3: Add trace hooks**

Wrap response creation and orchestrator execution in traces named `response.create` and `agent.orchestrator`. Include input metadata, route metadata, response ID, and errors when exceptions occur.

- [ ] **Step 4: Run tests and commit**

Run: `uv run pytest tests/services/test_response_tracing.py tests/services/test_response_service.py -v`
Expected: pass.

```bash
git add app/services/response_service.py app/agents/orchestrator/graph.py tests/services/test_response_tracing.py
git commit -m "feat: trace response execution"
```

## Task 3: Add Evaluation Dataset Schema And Deterministic Checks

**Files:**
- Modify: `pyproject.toml`
- Modify: `uv.lock`
- Create: `app/evals/datasets/examples/basic_rag_case.yaml`
- Create: `app/evals/datasets/examples/tool_call_case.yaml`
- Create: `app/evals/deterministic/checks.py`
- Create: `tests/evals/test_deterministic_checks.py`

- [ ] **Step 1: Write deterministic eval tests**

```python
from app.api.v1.schemas.responses import ResponseObject
from app.evals.deterministic.checks import check_required_response_shape, check_text_contains


def test_required_response_shape_passes_for_valid_response():
    response = ResponseObject.create_text_response("resp_1", "test-model", "hello", {})

    result = check_required_response_shape(response.model_dump())

    assert result.passed is True


def test_text_contains_fails_for_missing_text():
    result = check_text_contains("hello world", "missing")

    assert result.passed is False
    assert "missing" in result.message
```

- [ ] **Step 2: Run tests to verify failure**

Run: `uv run pytest tests/evals/test_deterministic_checks.py -v`
Expected: fail because eval checks do not exist.

- [ ] **Step 3: Add PyYAML dependency and deterministic checks**

Add `pyyaml>=6.0.2`. Implement `EvalResult(name: str, passed: bool, message: str)` plus `check_required_response_shape()` and `check_text_contains()`.

- [ ] **Step 4: Add example datasets**

`basic_rag_case.yaml` should define an input, expected required text, and deterministic checks. `tool_call_case.yaml` should define a generic tool-routing scenario without client-specific business logic.

- [ ] **Step 5: Run tests and commit**

Run: `uv sync`
Run: `uv run pytest tests/evals/test_deterministic_checks.py -v`
Expected: pass.

```bash
git add pyproject.toml uv.lock app/evals/datasets app/evals/deterministic/checks.py tests/evals/test_deterministic_checks.py
git commit -m "feat: add deterministic eval checks"
```

## Task 4: Add LLM Judge Service Abstraction

**Files:**
- Create: `app/evals/judges/judge_service.py`
- Create: `app/evals/judges/prompts/factuality.md`
- Create: `app/evals/judges/prompts/format_compliance.md`
- Create: `app/evals/judges/prompts/safety.md`
- Create: `tests/evals/test_judge_service.py`

- [ ] **Step 1: Write judge tests**

```python
import pytest

from app.evals.judges.judge_service import MockJudgeService


@pytest.mark.asyncio
async def test_mock_judge_service_returns_score():
    judge = MockJudgeService(score=0.9, passed=True)

    result = await judge.judge(input_text="question", output_text="answer", criteria="factuality")

    assert result.passed is True
    assert result.score == 0.9
    assert result.criteria == "factuality"
```

- [ ] **Step 2: Run tests to verify failure**

Run: `uv run pytest tests/evals/test_judge_service.py -v`
Expected: fail because judge service does not exist.

- [ ] **Step 3: Implement judge abstraction**

Create `JudgeResult`, `JudgeService` protocol, `MockJudgeService`, and `LlmJudgeService` that uses the existing LLM provider. The default test suite must use `MockJudgeService`.

- [ ] **Step 4: Run tests and commit**

Run: `uv run pytest tests/evals/test_judge_service.py -v`
Expected: pass.

```bash
git add app/evals/judges tests/evals/test_judge_service.py
git commit -m "feat: add llm judge abstraction"
```

## Task 5: Add Dataset Runner And Report Generator

**Files:**
- Create: `app/evals/runners/run_dataset.py`
- Create: `app/evals/runners/generate_report.py`
- Create: `app/evals/reports/.gitkeep`
- Create: `tests/evals/test_run_dataset.py`
- Create: `tests/evals/test_generate_report.py`

- [ ] **Step 1: Write runner tests**

```python
from pathlib import Path

import pytest
import yaml

from app.evals.runners.run_dataset import run_dataset


@pytest.mark.asyncio
async def test_run_dataset_returns_case_results(tmp_path: Path):
    dataset = tmp_path / "dataset.yaml"
    dataset.write_text(yaml.safe_dump({"cases": [{"name": "case", "input": "hello", "checks": [{"type": "contains", "value": "Template"}]}]}), encoding="utf-8")

    results = await run_dataset(dataset)

    assert results[0].name == "case"
```

- [ ] **Step 2: Write report test**

```python
from app.evals.deterministic.checks import EvalResult
from app.evals.runners.generate_report import generate_markdown_report


def test_generate_markdown_report_includes_pass_count():
    report = generate_markdown_report([EvalResult(name="shape", passed=True, message="ok")])

    assert "# Eval Report" in report
    assert "1 passed" in report
```

- [ ] **Step 3: Run tests to verify failure**

Run: `uv run pytest tests/evals/test_run_dataset.py tests/evals/test_generate_report.py -v`
Expected: fail because runners do not exist.

- [ ] **Step 4: Implement runner and report generator**

Runner should parse YAML, call the response service with mocked runtime defaults, run deterministic checks, optionally run mock judge checks, and return structured case results. Report generator should produce Markdown with pass/fail counts and individual result messages.

- [ ] **Step 5: Run tests and commit**

Run: `uv run pytest tests/evals/test_run_dataset.py tests/evals/test_generate_report.py -v`
Expected: pass.

```bash
git add app/evals/runners app/evals/reports/.gitkeep tests/evals/test_run_dataset.py tests/evals/test_generate_report.py
git commit -m "feat: add eval runner and reports"
```

## Task 6: Final Verification

- [ ] **Step 1: Run full tests**

Run: `uv run pytest`
Expected: all tests pass without real Langfuse or LLM credentials.

- [ ] **Step 2: Run lint**

Run: `uv run ruff check .`
Expected: all checks pass.

- [ ] **Step 3: Run example eval**

Run: `uv run python -m app.evals.runners.run_dataset app/evals/datasets/examples/basic_rag_case.yaml`
Expected: command exits successfully and prints case results.

- [ ] **Step 4: Commit docs if updated**

```bash
git add README.md HANDOVER.md
git commit -m "docs: update observability eval notes"
```
