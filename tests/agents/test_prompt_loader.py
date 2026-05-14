import pytest
from jinja2 import UndefinedError

from app.agents.shared.prompt_loader import PromptLoader


def test_render_renders_jinja_template_from_system_file(tmp_path) -> None:
    (tmp_path / "system.md").write_text("Hello {{ name }}")

    prompt_loader = PromptLoader(tmp_path)

    assert prompt_loader.render("system.md", {"name": "Agent"}) == "Hello Agent"


def test_render_many_composes_system_and_guardrails_with_blank_line(tmp_path) -> None:
    (tmp_path / "system.md").write_text("System prompt")
    (tmp_path / "guardrails.md").write_text("Guardrails prompt")

    prompt_loader = PromptLoader(tmp_path)

    assert prompt_loader.render_many(["system.md", "guardrails.md"], {}) == (
        "System prompt\n\nGuardrails prompt"
    )


def test_render_raises_when_required_context_is_missing(tmp_path) -> None:
    (tmp_path / "system.md").write_text("Hello {{ name }}")

    prompt_loader = PromptLoader(tmp_path)

    with pytest.raises(UndefinedError):
        prompt_loader.render("system.md", {})
