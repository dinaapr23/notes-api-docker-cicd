import os
import sqlite3
from contextlib import contextmanager

# Database file location. Uses in-memory DB by default (handy for tests);
# in Docker Compose this is overridden to point at a file on a mounted
# volume so data survives container restarts.
DB_PATH = os.environ.get("DB_PATH", ":memory:")

_shared_memory_conn = None  # keeps :memory: DB alive across connections


def get_connection():
    global _shared_memory_conn
    if DB_PATH == ":memory:":
        if _shared_memory_conn is None:
            _shared_memory_conn = sqlite3.connect(":memory:", check_same_thread=False)
            _shared_memory_conn.row_factory = sqlite3.Row
        return _shared_memory_conn

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            created_at TEXT NOT NULL DEFAULT (datetime('now'))
        )
        """
    )
    conn.commit()
    if DB_PATH != ":memory:":
        conn.close()


def reset_db():
    """Used by tests to guarantee a clean slate between test cases."""
    conn = get_connection()
    conn.execute("DROP TABLE IF EXISTS notes")
    conn.commit()
    if DB_PATH != ":memory:":
        conn.close()
    init_db()


@contextmanager
def db_cursor():
    conn = get_connection()
    try:
        cur = conn.cursor()
        yield cur
        conn.commit()
    finally:
        if DB_PATH != ":memory:":
            conn.close()
