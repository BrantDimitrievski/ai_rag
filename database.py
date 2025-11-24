import sqlite3

def init_db():
    conn = sqlite3
    cur = conn.cursor()
    cur.execute("""
            CREATE TABLE IF NOT EXISTS jsonparse
                id
                """)