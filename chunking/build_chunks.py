import json
from pathlib import Path
import parsing.helper as helper
import jsondb.database as db
from chunking import chunk_text


def build_chunks(db_path: str = "parsed_docs.db") -> None:

    db.init_db(db_path)

    docs = db.fetch_all_docs(db_path=db_path)
    if not docs:
        print("[WARN] No documents found in jsonparse. Did you run Step 1?")
        return

    total_chunks = 0

    for doc in docs:
        doc_id = doc["id"]
        file_path = doc["file_path"]

        try:
            elements = json.loads(doc["json_data"])
        except Exception as e:
            print(f"[ERROR] Could not decode json_data for doc_id={doc_id}: {e}")
            continue

        full_text = helper.get_full_text(elements)
        if not full_text.strip():
            print(f"[WARN] Empty full_text for doc_id={doc_id}, file={file_path}")
            continue

        # Clear existing chunks for idempotent reruns
        db.delete_chunks_for_doc(doc_id=doc_id, db_path=db_path)

        chunks = chunk_text(full_text, max_chars=1000, overlap=200)
        if not chunks:
            print(f"[WARN] No chunks generated for doc_id={doc_id}, file={file_path}")
            continue

        for idx, (chunk_text_str, start_pos, end_pos) in enumerate(chunks):
            metadata = {
                "source_file": file_path,
                "note": "auto-chunked from full_text",
            }
            db.insert_chunk(
                doc_id=doc_id,
                chunk_idx=idx,
                text=chunk_text_str,
                start_pos=start_pos,
                end_pos=end_pos,
                metadata=metadata,
                db_path=db_path,
            )
            total_chunks += 1

        print(f"[OK] Doc id={doc_id}, file={file_path} -> {len(chunks)} chunks")

    print(f"Chunking complete. Total chunks inserted: {total_chunks}")


if __name__ == "__main__":
    build_chunks("parsed_docs.db")
