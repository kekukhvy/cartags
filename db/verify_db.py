"""Verification script for the CarTags database after seeding.

Prints summary counts, sample lookups in all languages, and a report
of any regions missing translations.

Usage::

    python db/verify_db.py
"""

import logging
import sqlite3
from pathlib import Path

logger = logging.getLogger(__name__)

DB_PATH = Path(__file__).parent / "cartags.db"

_LANGUAGES = ("en", "de", "ru", "uk")


def print_counts(conn: sqlite3.Connection) -> None:
    """Print total counts of countries, regions, and translations.

    Args:
        conn: An open SQLite connection.
    """
    country_count = conn.execute("SELECT COUNT(*) FROM countries").fetchone()[0]
    region_count = conn.execute("SELECT COUNT(*) FROM regions").fetchone()[0]
    trans_count = conn.execute("SELECT COUNT(*) FROM translations").fetchone()[0]
    print(f"Countries:    {country_count}")
    print(f"Regions:      {region_count}")
    print(f"Translations: {trans_count}")


def _fetch_region_name(
    conn: sqlite3.Connection,
    country_code: str,
    plate_code: str,
    lang: str,
) -> str | None:
    """Return the region name translation for a given language."""
    row = conn.execute(
        """
        SELECT t.value
        FROM translations t
        JOIN regions r ON r.id = t.entity_id AND t.entity_type = 'region'
        JOIN countries c ON c.id = r.country_id
        WHERE UPPER(c.code) = UPPER(?)
          AND UPPER(r.plate_code) = UPPER(?)
          AND t.language_code = ?
          AND t.field = 'name'
        """,
        (country_code, plate_code, lang),
    ).fetchone()
    return row[0] if row else None


def lookup_sample(
    conn: sqlite3.Connection,
    country_code: str,
    plate_code: str,
) -> None:
    """Print region name in all 4 languages for a given country + plate.

    Args:
        conn:         An open SQLite connection.
        country_code: ISO 3166-1 alpha-2 country code.
        plate_code:   Vehicle registration plate prefix.
    """
    print(f"\nLookup: {country_code} {plate_code}")
    for lang in _LANGUAGES:
        name = _fetch_region_name(conn, country_code, plate_code, lang)
        print(f"  [{lang}] {name or '(missing)'}")


def _regions_missing_lang(
    conn: sqlite3.Connection,
    lang: str,
) -> list[tuple[str, str]]:
    """Return (country_code, plate_code) pairs missing a 'name' translation for lang."""
    rows = conn.execute(
        """
        SELECT c.code, r.plate_code
        FROM regions r
        JOIN countries c ON c.id = r.country_id
        WHERE NOT EXISTS (
            SELECT 1 FROM translations t
            WHERE t.entity_type = 'region'
              AND t.entity_id = r.id
              AND t.language_code = ?
              AND t.field = 'name'
        )
        ORDER BY c.code, r.plate_code
        """,
        (lang,),
    ).fetchall()
    return [(row[0], row[1]) for row in rows]


def check_missing_translations(conn: sqlite3.Connection) -> None:
    """Find and print regions that are missing any of the 4 language translations.

    Args:
        conn: An open SQLite connection.
    """
    print("\nMissing 'name' translations:")
    any_missing = False
    for lang in _LANGUAGES:
        missing = _regions_missing_lang(conn, lang)
        if missing:
            any_missing = True
            for country_code, plate_code in missing:
                print(f"  [{lang}] {country_code} {plate_code}")
    if not any_missing:
        print("  None — all regions have translations in all 4 languages.")


def main() -> None:
    """Open the database, run all verification checks, and close.

    Prints counts, sample lookups, and missing-translation report.
    """
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s — %(message)s")
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    try:
        print("=== CarTags DB Verification ===\n")
        print_counts(conn)
        lookup_sample(conn, "DE", "M")
        lookup_sample(conn, "AT", "W")
        lookup_sample(conn, "UA", "AA")
        check_missing_translations(conn)
    finally:
        conn.close()


if __name__ == "__main__":
    main()
