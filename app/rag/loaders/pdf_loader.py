from pathlib import Path

from pypdf import PdfReader


def load_pdf(path: Path) -> str:
    """Load PDF file and extract text from all pages."""
    reader = PdfReader(path)
    text_parts = []

    for page in reader.pages:
        text_parts.append(page.extract_text())

    return "\n".join(text_parts)
