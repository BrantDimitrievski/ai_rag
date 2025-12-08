import os
from typing import List

import SentenceTransformer


def _get_model() -> SentenceTransformer:
    global _model
    if _model is None:
        model_name = os.getenv(
            "EMBEDDING_MODEL_NAME",
            "sentence-transformers/all-MiniLM-L6-v2",
        )
        print(f"[INFO] Loading embedding model: {model_name}")
        _model = SentenceTransformer(model_name)
    return _model


def embed_texts(texts: List[str]) -> List[list[float]]:
    """
    Embed a list of texts into vectors.

    Returns list of vectors (each vector is a list[float]).
    """
    if not texts:
        return []

    model = _get_model()

    embeddings = model.encode(
        texts,
        show_progress_bar=False,
        convert_to_numpy=False,
    )
    return [e.tolist() for e in embeddings]
