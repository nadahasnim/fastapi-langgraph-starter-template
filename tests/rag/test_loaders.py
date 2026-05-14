from pathlib import Path

from app.rag.chunking import chunk_text
from app.rag.loaders.markdown_loader import load_markdown
from app.rag.loaders.text_loader import load_text


def test_chunk_text_splits_with_overlap():
    chunks = chunk_text("one two three four five", chunk_size=14, overlap=4)

    assert len(chunks) >= 2
    assert chunks[0].index == 0
    assert chunks[0].content


def test_text_loader_reads_file(tmp_path: Path):
    path = tmp_path / "note.txt"
    path.write_text("hello", encoding="utf-8")

    assert load_text(path) == "hello"


def test_markdown_loader_reads_file(tmp_path: Path):
    path = tmp_path / "note.md"
    path.write_text("# hello", encoding="utf-8")

    assert load_markdown(path) == "# hello"
