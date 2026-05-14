import pytest

from app.evals.judges.judge_service import MockJudgeService


@pytest.mark.asyncio
async def test_mock_judge_service_returns_score():
    judge = MockJudgeService(score=0.9, passed=True)

    result = await judge.judge(input_text="question", output_text="answer", criteria="factuality")

    assert result.passed is True
    assert result.score == 0.9
    assert result.criteria == "factuality"
