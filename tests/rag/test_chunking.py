from app.rag.chunking import chunk_text


def test_chunk_text_splits_with_overlap():
    chunks = chunk_text("one two three four five", chunk_size=14, overlap=4)

    assert len(chunks) >= 2
    assert chunks[0].index == 0
    assert chunks[0].content
