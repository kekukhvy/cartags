"""Single idempotent script: initialise schema + seed all countries.

Safe to run multiple times — schema uses CREATE TABLE IF NOT EXISTS and
all seed inserts use INSERT OR IGNORE, so re-running never duplicates data.

Usage::

    python db/setup.py              # init schema + seed all countries
    python db/setup.py --only DE,AT # seed only specific countries
    python db/setup.py --skip RU,BY # skip specific countries
    python db/setup.py --schema-only # apply schema without seeding
"""

import argparse
import logging
import sqlite3
import sys
from pathlib import Path

# Ensure the project root is on sys.path so `data` package is importable
# regardless of which directory the script is invoked from.
sys.path.insert(0, str(Path(__file__).parent.parent))

from data import (
    seed_de, seed_at, seed_pl, seed_ch, seed_cz, seed_ro,
    seed_bg, seed_hr, seed_rs, seed_si, seed_me, seed_mk,
    seed_gr, seed_ua, seed_by, seed_ru, seed_tr, seed_xk,
    seed_no, seed_ie,
)

logger = logging.getLogger(__name__)

DB_PATH = Path(__file__).parent / "cartags.db"
SCHEMA_PATH = Path(__file__).parent / "schema.sql"

SEED_AGENTS: list[tuple[str, object]] = [
    ("DE", seed_de), ("AT", seed_at), ("PL", seed_pl),
    ("CH", seed_ch), ("CZ", seed_cz), ("RO", seed_ro),
    ("BG", seed_bg), ("HR", seed_hr), ("RS", seed_rs),
    ("SI", seed_si), ("ME", seed_me), ("MK", seed_mk),
    ("GR", seed_gr), ("UA", seed_ua), ("BY", seed_by),
    ("RU", seed_ru), ("TR", seed_tr), ("XK", seed_xk),
    ("NO", seed_no), ("IE", seed_ie),
]


def _parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Initialise CarTags DB schema and seed country data.",
    )
    parser.add_argument(
        "--schema-only",
        action="store_true",
        help="Apply schema without seeding any countries.",
    )
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "--only",
        metavar="CC,...",
        help="Seed only these comma-separated country codes (e.g. DE,AT).",
    )
    group.add_argument(
        "--skip",
        metavar="CC,...",
        help="Seed all countries except these comma-separated codes.",
    )
    return parser.parse_args()


def _apply_schema(conn: sqlite3.Connection) -> None:
    """Read schema.sql and execute it against the connection.

    Args:
        conn: An open SQLite connection.
    """
    sql = SCHEMA_PATH.read_text(encoding="utf-8")
    conn.executescript(sql)
    logger.info("Schema applied")


def _select_agents(
    only: str | None,
    skip: str | None,
) -> list[tuple[str, object]]:
    """Return filtered (code, module) pairs based on CLI flags.

    Args:
        only: Comma-separated codes to include exclusively, or None.
        skip: Comma-separated codes to exclude, or None.
    """
    if only:
        codes = {c.strip().upper() for c in only.split(",")}
        return [(code, mod) for code, mod in SEED_AGENTS if code in codes]
    if skip:
        codes = {c.strip().upper() for c in skip.split(",")}
        return [(code, mod) for code, mod in SEED_AGENTS if code not in codes]
    return list(SEED_AGENTS)


def _seed_countries(
    conn: sqlite3.Connection,
    agents: list[tuple[str, object]],
) -> None:
    """Run each seed module's run() inside the open connection.

    Args:
        conn:   An open SQLite connection with foreign keys enabled.
        agents: List of (country_code, seed_module) pairs.
    """
    for code, module in agents:
        logger.info("Seeding %s …", code)
        module.run(conn)  # type: ignore[attr-defined]


def _print_summary(conn: sqlite3.Connection) -> None:
    """Print post-seed row counts.

    Args:
        conn: An open SQLite connection.
    """
    countries = conn.execute("SELECT COUNT(*) FROM countries").fetchone()[0]
    regions = conn.execute("SELECT COUNT(*) FROM regions").fetchone()[0]
    translations = conn.execute("SELECT COUNT(*) FROM translations").fetchone()[0]
    logger.info("DB summary — countries: %d, regions: %d, translations: %d",
                countries, regions, translations)


def setup(
    db_path: Path = DB_PATH,
    only: str | None = None,
    skip: str | None = None,
    schema_only: bool = False,
) -> None:
    """Initialise schema and optionally seed countries.

    Args:
        db_path:     Path to the SQLite database file.
        only:        Comma-separated codes to seed exclusively.
        skip:        Comma-separated codes to skip.
        schema_only: If True, skip seeding entirely.
    """
    logger.info("Opening database at %s", db_path)
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys = ON")
    try:
        _apply_schema(conn)
        if not schema_only:
            agents = _select_agents(only, skip)
            if agents:
                _seed_countries(conn, agents)
            else:
                logger.warning("No seed agents selected — schema applied, no data seeded.")
        conn.commit()
        _print_summary(conn)
        logger.info("Setup complete.")
    finally:
        conn.close()


def main() -> None:
    """Entry point: parse args and run setup."""
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s — %(message)s")
    args = _parse_args()
    setup(
        only=args.only,
        skip=args.skip,
        schema_only=args.schema_only,
    )


if __name__ == "__main__":
    main()
