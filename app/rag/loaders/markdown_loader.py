from pathlib import Path


def load_markdown(path: Path) -> str:
    """Load markdown file."""
    return path.read_text(encoding="utf-8")
