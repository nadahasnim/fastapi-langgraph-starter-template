"""Report generator for evaluation results."""

from app.evals.deterministic.checks import EvalResult


def generate_markdown_report(results: list[EvalResult]) -> str:
    """Generate markdown report from evaluation results."""
    passed = sum(1 for r in results if r.passed)
    failed = len(results) - passed

    report = ["# Eval Report", "", f"**Summary:** {passed} passed, {failed} failed", "", "## Results", ""]

    for result in results:
        status = "✅" if result.passed else "❌"
        report.append(f"- {status} **{result.name}**: {result.message}")

    return "\n".join(report)
