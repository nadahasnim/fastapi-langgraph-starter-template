from app.evals.deterministic.checks import EvalResult
from app.evals.runners.generate_report import generate_markdown_report


def test_generate_markdown_report_includes_pass_count():
    report = generate_markdown_report([EvalResult(name="shape", passed=True, message="ok")])

    assert "# Eval Report" in report
    assert "1 passed" in report
