import json
import sqlite3


def init_db():
    conn = sqlite3.connect("parsed_docs.db")
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS jsonparse (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            file_path TEXT NOT NULL,
            title TEXT,
            domain TEXT,
            doc_type TEXT,
            year INTEGER,
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
    year: int, # make this optional
    json_data: list[dict],
):
    """Insert one document's metadata + raw JSON into DB."""
    conn = sqlite3.connect("parsed_docs.db")
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
    conn.commit()
    conn.close()