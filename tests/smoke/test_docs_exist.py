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
    text = "\n".join(
        Path(path).read_text(encoding="utf-8").lower() for path in Path("docs").glob("*.md")
    )
    for phrase in forbidden:
        assert phrase not in text
