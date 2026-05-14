from dataclasses import dataclass


@dataclass
class TextChunk:
    index: int
    content: str
    metadata: dict


def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 200) -> list[TextChunk]:
    """Split text into overlapping chunks."""
    if not text:
        return []

    chunks = []
    start = 0
    index = 0

    while start < len(text):
        end = start + chunk_size
        chunk_content = text[start:end]

        chunks.append(
            TextChunk(
                index=index,
                content=chunk_content,
                metadata={},
            )
        )

        index += 1
        start = end - overlap

        # Prevent infinite loop if overlap >= chunk_size
        if overlap >= chunk_size:
            start = end

    return chunks
