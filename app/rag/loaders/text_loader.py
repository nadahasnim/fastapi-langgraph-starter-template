from pathlib import Path


def load_text(path: Path) -> str:
    """Load plain text file."""
    return path.read_text(encoding="utf-8")
