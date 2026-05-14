"""LLM judge service abstraction for evaluation."""

from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

from app.agents.shared.llm import LlmMessage, LlmProvider


@dataclass
class JudgeResult:
    """Result of an LLM judge evaluation."""

    criteria: str
    passed: bool
    score: float
    reasoning: str = ""


class JudgeService(Protocol):
    """Protocol for judge services."""

    async def judge(self, input_text: str, output_text: str, criteria: str) -> JudgeResult:
        """Judge output against criteria."""
        ...


class MockJudgeService:
    """Mock judge service for testing."""

    def __init__(self, score: float = 1.0, passed: bool = True) -> None:
        self.score = score
        self.passed = passed

    async def judge(self, input_text: str, output_text: str, criteria: str) -> JudgeResult:
        """Return mock judge result."""
        return JudgeResult(
            criteria=criteria,
            passed=self.passed,
            score=self.score,
            reasoning="Mock judge result",
        )


class LlmJudgeService:
    """LLM-based judge service."""

    def __init__(self, llm_provider: LlmProvider, model: str) -> None:
        self._llm_provider = llm_provider
        self._model = model
        self._prompts_dir = Path(__file__).parent / "prompts"

    async def judge(self, input_text: str, output_text: str, criteria: str) -> JudgeResult:
        """Judge output using LLM."""
        prompt_file = self._prompts_dir / f"{criteria}.md"
        if not prompt_file.exists():
            prompt_file = self._prompts_dir / "factuality.md"

        prompt_template = prompt_file.read_text()
        prompt = prompt_template.format(input=input_text, output=output_text)

        response = await self._llm_provider.complete(
            [LlmMessage(role="user", content=prompt)],
            model=self._model,
        )

        # Parse response for score (simple heuristic: look for "PASS" or "FAIL")
        response_text = response.text.lower()
        passed = "pass" in response_text and "fail" not in response_text
        score = 1.0 if passed else 0.0

        return JudgeResult(
            criteria=criteria,
            passed=passed,
            score=score,
            reasoning=response.text,
        )
