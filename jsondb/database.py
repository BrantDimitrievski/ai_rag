import json
import sqlite3



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