import json
import sqlite3
from typing import Iterable, List


def init_db(db_path: str = "parsed_docs.db") -> None:
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS jsonparse (
            id       INTEGER PRIMARY KEY AUTOINCREMENT,
            file_path TEXT NOT NULL,
            title     TEXT,
            domain    TEXT,      -- JSON-encoded list of tags
            doc_type  TEXT,
            year      INTEGER,
            json_data TEXT NOT NULL
        );
        """
    )
    
    # chunk table 
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS chunks (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            doc_id     INTEGER NOT NULL,
            chunk_idx  INTEGER NOT NULL,
            text       TEXT NOT NULL,
            start_pos  INTEGER,
            end_pos    INTEGER,
            metadata   TEXT,
            FOREIGN KEY (doc_id) REFERENCES jsonparse(id)
        );
        """
    )
    conn.commit()
    conn.close()


def insert_doc(
    file_path: str,
    title: str,
    domain: list[str],
    doc_type: str,
    year: int | None,
    json_data: list[dict],
    db_path: str = "parsed_docs.db",
) -> None:
    """Insert one document's metadata + raw JSON into DB."""
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO jsonparse (file_path, title, domain, doc_type, year, json_data)
        VALUES (?, ?, ?, ?, ?, ?);
        """,
        (
            file_path,
            title,
            json.dumps(domain),
            doc_type,
            year,
            json.dumps(json_data),
        ),
    )
    conn.commit()
    conn.close()

def read_docs(db_path: str = "parsed_docs.db") -> None:
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    cur.execute("""
        SELECT id, file_path, title, domain, doc_type, year
        FROM jsonparse;
    """)

    rows = cur.fetchall()
    conn.close()

    for row in rows:
        rid, file_path, title, domain_json, doc_type, year = row
        domain = json.loads(domain_json) if domain_json else []
        print(
            f"[{rid}] {file_path}\n"
            f"     Title: {title}\n"
            f"     Domain Tags: {domain}\n"
            f"     Type: {doc_type}\n"
            f"     Year: {year}\n"
        )

    
def insert_chunk(
    doc_id: int,
    chunk_idx: int,
    text: str,
    start_pos: int | None = None,
    end_pos: int | None = None,
    metadata: dict | None = None,
    db_path: str = "parsed_docs.db",
    ) -> None:
    
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO chunks (doc_id, chunk_idx, text, start_pos, end_pos, metadata)
        VALUES (?, ?, ?, ?, ?, ?);
        """,(doc_id, chunk_idx, text, start_pos, end_pos, json.dumps(metadata or {}),),
    )
    conn.commit()
    conn.close()


def delete_chunks_for_doc(doc_id: int, db_path: str = "parsed_docs.db") -> None:
    """Delete all chunks for a given doc_id (used to keep chunking idempotent)."""
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("DELETE FROM chunks WHERE doc_id = ?;", (doc_id,))
    conn.commit()
    conn.close()


def fetch_all_docs(db_path: str = "parsed_docs.db") -> list[dict]:
    """Return all docs from jsonparse as a list of dicts."""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("SELECT id, file_path, title, domain, doc_type, year, json_data FROM jsonparse;")
    rows = cur.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def iter_chunks_with_docs(db_path: str = "parsed_docs.db", batch_size: int = 128) -> Iterable[list[sqlite3.Row]]:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    try:
        cur.execute(
            """
            SELECT
                c.id       AS chunk_id,
                c.doc_id   AS doc_id,
                c.chunk_idx,
                c.text,
                c.start_pos,
                c.end_pos,
                c.metadata AS chunk_metadata,
                j.title,
                j.file_path,
                j.domain,
                j.doc_type,
                j.year
            FROM chunks c
            JOIN jsonparse j ON c.doc_id = j.id
            ORDER BY c.id ASC;
            """
        )

        while True:
            rows = cur.fetchmany(batch_size)
            if not rows:
                break
            yield rows
    finally:
        conn.close()
