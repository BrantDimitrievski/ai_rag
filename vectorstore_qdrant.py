import json
import os
from typing import Iterable, List, Optional

from qdrant_client import QdrantClient
from qdrant_client.http import models as qmodels

from embeddings import embed_texts
from jsondb.database import iter_chunks_with_docs


def get_qdrant_client() -> QdrantClient:
    """
    Create a Qdrant client using env vars:
    QDRANT_URL or QDRANT_HOST/QDRANT_PORT, plus optional QDRANT_API_KEY.
    """
    url = os.getenv("QDRANT_URL")
    api_key = os.getenv("QDRANT_API_KEY")
    if url:
        return QdrantClient(url=url, api_key=api_key)

    host = os.getenv("QDRANT_HOST", "localhost")
    port = int(os.getenv("QDRANT_PORT", "6333"))
    return QdrantClient(host=host, port=port, api_key=api_key)


def ensure_collection(
    client: QdrantClient,
    collection_name: str,
    vector_size: int,
    distance: qmodels.Distance = qmodels.Distance.COSINE,
) -> None:
    """
    Create the collection if it does not exist. If it does, validate vector size/distance.
    """
    existing = {c.name for c in client.get_collections().collections}
    if collection_name in existing:
        info = client.get_collection(collection_name)
        params = info.config.params.vectors
        if isinstance(params, dict):
            raise ValueError(f"Collection '{collection_name}' uses named vectors; this helper expects a single default vector.")
        if params.size != vector_size or params.distance != distance:
            raise ValueError(
                f"Collection '{collection_name}' has size={params.size}, distance={params.distance}; "
                f"expected size={vector_size}, distance={distance}."
            )
        return

    client.create_collection(
        collection_name=collection_name,
        vectors_config=qmodels.VectorParams(size=vector_size, distance=distance),
    )


def _row_to_payload(row) -> dict:
    """
    Convert a chunk row from SQLite into a payload dict for Qdrant.
    """
    try:
        domain = json.loads(row["domain"]) if row["domain"] else []
    except Exception:
        domain = []

    try:
        chunk_metadata = json.loads(row["chunk_metadata"]) if row["chunk_metadata"] else {}
    except Exception:
        chunk_metadata = {}

    payload = {
        "doc_id": row["doc_id"],
        "chunk_idx": row["chunk_idx"],
        "text": row["text"],
        "start_pos": row["start_pos"],
        "end_pos": row["end_pos"],
        "title": row["title"],
        "file_path": row["file_path"],
        "domain": domain,
        "doc_type": row["doc_type"],
        "year": row["year"],
        "chunk_metadata": chunk_metadata,
    }
    return payload


def _rows_to_points(rows, embeddings: List[List[float]]) -> List[qmodels.PointStruct]:
    points: List[qmodels.PointStruct] = []
    for row, embedding in zip(rows, embeddings):
        point_id = f"{row['doc_id']}-{row['chunk_idx']}"
        points.append(
            qmodels.PointStruct(
                id=point_id,
                vector=embedding,
                payload=_row_to_payload(row),
            )
        )
    return points


def upsert_rows(
    client: QdrantClient,
    collection_name: str,
    rows,
) -> None:
    texts = [r["text"] for r in rows]
    embeddings = embed_texts(texts)
    points = _rows_to_points(rows, embeddings)
    if not points:
        return
    ensure_collection(client, collection_name, vector_size=len(points[0].vector))
    client.upsert(collection_name=collection_name, points=points)


def ingest_chunks_to_qdrant(
    db_path: str = "parsed_docs.db",
    collection_name: str = "doc_chunks",
    batch_size: int = 64,
) -> None:
    client = get_qdrant_client()
    for rows in iter_chunks_with_docs(db_path=db_path, batch_size=batch_size):
        upsert_rows(client, collection_name, rows)
    print(f"[OK] Ingested chunks into Qdrant collection '{collection_name}'.")


def search(
    query_text: str,
    top_k: int = 5,
    collection_name: str = "doc_chunks",
) -> List[qmodels.ScoredPoint]:
    client = get_qdrant_client()
    query_vector = embed_texts([query_text])[0]
    ensure_collection(client, collection_name, vector_size=len(query_vector))
    return client.search(
        collection_name=collection_name,
        query_vector=query_vector,
        limit=top_k,
        with_payload=True,
    )


if __name__ == "__main__":
    ingest_chunks_to_qdrant()
