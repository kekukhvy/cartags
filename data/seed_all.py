"""Run all country seed scripts in priority order.

Usage::

    python data/seed_all.py              # seed everything
    python data/seed_all.py --only DE,AT # seed specific countries
    python data/seed_all.py --skip RU,BY # skip specific countries
"""

import argparse
import logging
import sqlite3
from pathlib import Path

from data import (
    seed_de, seed_at, seed_pl, seed_ch, seed_cz, seed_ro,
    seed_bg, seed_hr, seed_rs, seed_si, seed_me, seed_mk,
    seed_gr, seed_ua, seed_by, seed_ru, seed_tr, seed_xk,
    seed_no, seed_ie,
)

logger = logging.getLogger(__name__)

DB_PATH = Path(__file__).parent.parent / "db" / "cartags.db"

# Ordered list of (country_code, module) pairs — priority order
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
    parser = argparse.ArgumentParser(description="Seed all countries into CarTags DB.")
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "--only",
        metavar="CC,...",
        help="Comma-separated list of country codes to seed (e.g. DE,AT)",
    )
    group.add_argument(
        "--skip",
        metavar="CC,...",
        help="Comma-separated list of country codes to skip (e.g. RU,BY)",
    )
    return parser.parse_args()


def _select_agents(
    only: str | None,
    skip: str | None,
) -> list[tuple[str, object]]:
    """Return the filtered list of (code, module) pairs to run.

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


def run_all(conn: sqlite3.Connection, agents: list[tuple[str, object]]) -> None:
    """Run each agent's run() inside a single transaction.

    Args:
        conn:   An open SQLite connection with foreign keys enabled.
        agents: List of (country_code, seed_module) pairs to execute.
    """
    for code, module in agents:
        logger.info("Seeding %s …", code)
        module.run(conn)  # type: ignore[attr-defined]
    logger.info("All %d agents complete.", len(agents))


def main() -> None:
    """Entry point: parse args, open DB, run selected agents, commit."""
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s — %(message)s")
    args = _parse_args()
    agents = _select_agents(args.only, args.skip)
    if not agents:
        logger.warning("No seed agents selected — nothing to do.")
        return
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    try:
        run_all(conn, agents)
        conn.commit()
        logger.info("Seed complete.")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
