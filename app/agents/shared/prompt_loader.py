from pathlib import Path
from typing import Any

from jinja2 import Environment, FileSystemLoader, StrictUndefined


class PromptLoader:
    def __init__(self, base_path: Path) -> None:
        self._environment = Environment(
            loader=FileSystemLoader(base_path),
            undefined=StrictUndefined,
            autoescape=False,
        )

    def render(self, name: str, context: dict[str, Any]) -> str:
        return self._environment.get_template(name).render(**context)

    def render_many(self, names: list[str], context: dict[str, Any]) -> str:
        return "\n\n".join(self.render(name, context) for name in names)
