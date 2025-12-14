from typing import List, Tuple


def chunk_text(text: str, max_chars: int = 1000, overlap: int = 200) -> List[Tuple[str, int, int]]:
    """
    Split text into overlapping character chunks.

    Returns list of tuples: (chunk_text, start_index, end_index).
    """
    if max_chars <= 0:
        raise ValueError("max_chars must be positive")
    if overlap < 0:
        raise ValueError("overlap cannot be negative")
    if overlap >= max_chars:
        # prevent infinite loops; cap overlap to one less than max_chars
        overlap = max_chars - 1

    chunks: List[Tuple[str, int, int]] = []
    n = len(text)
    if n == 0:
        return chunks

    start = 0
    while start < n:
        end = min(start + max_chars, n)
        chunk = text[start:end]
        chunks.append((chunk, start, end))
        if end == n:
            break
        start = end - overlap

    return chunks
