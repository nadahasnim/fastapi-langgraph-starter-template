# Evaluations

## Overview

The evaluation framework provides deterministic checks and LLM-based judges for assessing agent performance.

## Running Evaluations

```bash
# Run eval dataset
uv run python -m app.evals.runners.run_dataset \
  app/evals/datasets/examples/basic_rag_case.yaml

# Output
✅ basic_rag_query: Text contains 'Template'
```

## Dataset Format

```yaml
# app/evals/datasets/examples/my_eval.yaml
cases:
  - name: test_case_1
    input: "What is in the knowledge base?"
    checks:
      - type: contains
        value: "Template"
      - type: judge
        criteria: factuality
```

## Deterministic Checks

### Available Checks

```python
from app.evals.deterministic.checks import (
    check_required_response_shape,
    check_text_contains
)

# Check response structure
result = check_required_response_shape(response.model_dump())
assert result.passed

# Check text content
result = check_text_contains(output_text, "expected phrase")
assert result.passed
```

### Custom Checks

```python
from app.evals.deterministic.checks import EvalResult

def check_custom_logic(response: dict) -> EvalResult:
    passed = custom_validation(response)
    return EvalResult(
        name="custom_check",
        passed=passed,
        message=f"Custom check {'passed' if passed else 'failed'}"
    )
```

## LLM Judges

### Using Judges

```python
from app.evals.judges.judge_service import LlmJudgeService, MockJudgeService

# Mock judge for testing
judge = MockJudgeService(score=0.9, passed=True)
result = await judge.judge(
    input_text="question",
    output_text="answer",
    criteria="factuality"
)

# Real LLM judge
judge = LlmJudgeService(llm_provider, model="gpt-4")
result = await judge.judge(
    input_text="What is 2+2?",
    output_text="4",
    criteria="factuality"
)
```

### Judge Criteria

- **factuality** - Is the output factually correct?
- **format_compliance** - Does output follow expected format?
- **safety** - Is output safe and appropriate?

### Custom Judge Prompts

Create `app/evals/judges/prompts/custom_criteria.md`:

```markdown
# Custom Criteria Judge

Evaluate if the output meets custom criteria.

**Input:** {input}

**Output:** {output}

**Task:** Determine if output meets criteria.

Respond with:
- PASS if criteria met
- FAIL if criteria not met

Provide brief reasoning.
```

## Report Generation

```python
from app.evals.runners.generate_report import generate_markdown_report
from app.evals.deterministic.checks import EvalResult

results = [
    EvalResult(name="test1", passed=True, message="ok"),
    EvalResult(name="test2", passed=False, message="failed")
]

report = generate_markdown_report(results)
print(report)
```

Output:

```markdown
# Eval Report

**Summary:** 1 passed, 1 failed

## Results

- ✅ **test1**: ok
- ❌ **test2**: failed
```

## Integration with CI/CD

```yaml
# .github/workflows/eval.yml
name: Evaluations

on: [push, pull_request]

jobs:
  eval:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run evals
        run: |
          uv sync
          uv run python -m app.evals.runners.run_dataset \
            app/evals/datasets/examples/basic_rag_case.yaml
```

## Best Practices

1. **Start with deterministic checks** - Fast and reliable
2. **Use LLM judges sparingly** - Expensive and slower
3. **Version datasets** - Track eval data in git
4. **Run regularly** - Catch regressions early
5. **Monitor trends** - Track eval scores over time
6. **Test edge cases** - Include failure scenarios
7. **Document expectations** - Clear pass/fail criteria

## Example: Custom Eval Dataset

```yaml
# app/evals/datasets/custom/generic_card_eval.yaml
cases:
  - name: generic_card_creation
    input: "Create a generic card for project planning"
    checks:
      - type: contains
        value: "generic card"
      - type: judge
        criteria: format_compliance
  
  - name: generic_card_validation
    input: "Validate this generic card structure"
    checks:
      - type: contains
        value: "valid"
      - type: judge
        criteria: factuality
```

Run:

```bash
uv run python -m app.evals.runners.run_dataset \
  app/evals/datasets/custom/generic_card_eval.yaml
```
