"""Initialise the CarTags SQLite database.

Reads schema.sql from the same directory and executes it against
db/cartags.db (path resolved relative to this file).  Idempotent —
schema uses CREATE TABLE IF NOT EXISTS so it is safe to run repeatedly.

Usage::

    python db/init_db.py
"""

import logging
import sqlite3
from pathlib import Path

logger = logging.getLogger(__name__)

DB_PATH = Path(__file__).parent / "cartags.db"
SCHEMA_PATH = Path(__file__).parent / "schema.sql"


def _read_schema() -> str:
    """Read and return the SQL schema as a string."""
    logger.info("Reading schema from %s", SCHEMA_PATH)
    return SCHEMA_PATH.read_text(encoding="utf-8")


def _apply_schema(conn: sqlite3.Connection) -> None:
    """Execute the full schema SQL against the connection."""
    sql = _read_schema()
    conn.executescript(sql)
    logger.info("Schema applied successfully")


def _enable_foreign_keys(conn: sqlite3.Connection) -> None:
    """Enable foreign key enforcement for the session."""
    conn.execute("PRAGMA foreign_keys = ON")
    logger.info("Foreign keys enabled")


def init_database(db_path: Path = DB_PATH) -> None:
    """Create the database file and apply the schema.

    Args:
        db_path: Path to the SQLite database file to create or update.
    """
    logger.info("Initialising database at %s", db_path)
    conn = sqlite3.connect(db_path)
    try:
        _enable_foreign_keys(conn)
        _apply_schema(conn)
        conn.commit()
        logger.info("Database initialised successfully")
    finally:
        conn.close()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s — %(message)s")
    init_database()
