"""Seed Kosovo (XK) into the CarTags database.

Inserts the country record, its translations, and 7 region records
with full translations in en/de/ru/uk.  All inserts are idempotent
via INSERT OR IGNORE.

Usage::

    python data/seed_xk.py
"""

import logging
import sqlite3
from pathlib import Path

logger = logging.getLogger(__name__)

DB_PATH = Path(__file__).parent.parent / "db" / "cartags.db"

COUNTRY_CODE = "XK"
COUNTRY_EMOJI = "🇽🇰"
COUNTRY_SORT_ORDER = 18

_COUNTRY_TRANSLATIONS: dict[str, str] = {
    "en": "Kosovo",
    "de": "Kosovo",
    "ru": "Косово",
    "uk": "Косово",
}

_KOSOVO = {
    "en": "Kosovo",
    "de": "Kosovo",
    "ru": "Косово",
    "uk": "Косово",
}

_COORDS: dict[str, tuple[float, float]] = {
    "PR": (42.2167, 20.7333),  # Prizren
    "PE": (42.6608, 20.2886),  # Peć / Peja
    "PZ": (42.6614, 21.1655),  # Pristina
    "GJ": (42.4581, 20.4317),  # Gjakova
    "UR": (42.3719, 21.1483),  # Uroševac / Ferizaj
    "FE": (42.3694, 21.1458),  # Ferizaj (alt)
    "MF": (43.1086, 20.8297),  # Mitrovica
}

# (plate_code, name_en, name_de, name_ru, name_uk)
_REGION_ROWS: list[tuple[str, str, str, str, str]] = [
    ("PR", "Prizren",           "Prizren",           "Призрен",          "Призрен"),
    ("PE", "Peć / Peja",        "Peć",               "Печ",              "Печ"),
    ("PZ", "Pristina",          "Pristina",          "Приштина",         "Приштина"),
    ("GJ", "Gjakova",           "Gjakova",           "Джакова",          "Джакова"),
    ("UR", "Uroševac / Ferizaj","Uroševac",          "Урошевац",         "Урошеваць"),
    ("FE", "Ferizaj",           "Ferizaj",           "Феризай",          "Феризай"),
    ("MF", "Mitrovica",         "Mitrovica",         "Митровица",        "Митровиця"),
]


# ---------------------------------------------------------------------------
# Insertion helpers
# ---------------------------------------------------------------------------

def _get_or_insert_country(conn: sqlite3.Connection) -> int:
    """Insert country if absent and return its id."""
    conn.execute(
        "INSERT OR IGNORE INTO countries (code, emoji, sort_order) VALUES (?, ?, ?)",
        (COUNTRY_CODE, COUNTRY_EMOJI, COUNTRY_SORT_ORDER),
    )
    row = conn.execute("SELECT id FROM countries WHERE code = ?", (COUNTRY_CODE,)).fetchone()
    return row[0]


def _insert_country_translations(conn: sqlite3.Connection, country_id: int) -> None:
    """Insert all language translations for the country."""
    for lang, value in _COUNTRY_TRANSLATIONS.items():
        conn.execute(
            "INSERT OR IGNORE INTO translations "
            "(entity_type, entity_id, language_code, field, value) VALUES (?, ?, ?, ?, ?)",
            ("country", country_id, lang, "name", value),
        )


def seed_country(conn: sqlite3.Connection) -> None:
    """Insert the XK country record and its translations.

    Args:
        conn: An open SQLite connection (foreign keys must be on).
    """
    country_id = _get_or_insert_country(conn)
    _insert_country_translations(conn, country_id)
    logger.info("Seeded country XK (id=%d)", country_id)


def _insert_region_translations(
    conn: sqlite3.Connection,
    region_id: int,
    name_trans: dict[str, str],
    group_trans: dict[str, str],
) -> None:
    """Insert name and region_group translations for a single region.

    Args:
        conn:        An open SQLite connection.
        region_id:   Primary key of the region row.
        name_trans:  Mapping of language_code → name value.
        group_trans: Mapping of language_code → region_group value.
    """
    for lang, value in name_trans.items():
        conn.execute(
            "INSERT OR IGNORE INTO translations "
            "(entity_type, entity_id, language_code, field, value) VALUES (?, ?, ?, ?, ?)",
            ("region", region_id, lang, "name", value),
        )
    for lang, value in group_trans.items():
        conn.execute(
            "INSERT OR IGNORE INTO translations "
            "(entity_type, entity_id, language_code, field, value) VALUES (?, ?, ?, ?, ?)",
            ("region", region_id, lang, "region_group", value),
        )


def _seed_single_region(
    conn: sqlite3.Connection,
    country_id: int,
    plate_code: str,
    name_en: str,
    name_de: str,
    name_ru: str,
    name_uk: str,
    coords: tuple[float, float] | None,
) -> None:
    """Insert one region and its translations."""
    lat = coords[0] if coords else None
    lon = coords[1] if coords else None
    conn.execute(
        "INSERT OR IGNORE INTO regions"
        " (country_id, plate_code, latitude, longitude) VALUES (?, ?, ?, ?)",
        (country_id, plate_code.upper(), lat, lon),
    )
    row = conn.execute(
        "SELECT id FROM regions WHERE country_id = ? AND plate_code = ?",
        (country_id, plate_code.upper()),
    ).fetchone()
    name_trans = {"en": name_en, "de": name_de, "ru": name_ru, "uk": name_uk}
    _insert_region_translations(conn, row[0], name_trans, _KOSOVO)


def seed_regions(conn: sqlite3.Connection) -> None:
    """Insert all XK region records and their translations.

    Args:
        conn: An open SQLite connection.
    """
    row = conn.execute("SELECT id FROM countries WHERE code = ?", (COUNTRY_CODE,)).fetchone()
    country_id: int = row[0]
    for plate_code, name_en, name_de, name_ru, name_uk in _REGION_ROWS:
        coords = _COORDS.get(plate_code.upper())
        _seed_single_region(
            conn, country_id, plate_code,
            name_en, name_de, name_ru, name_uk,
            coords,
        )
    logger.info("Seeded %d XK regions", len(_REGION_ROWS))


def run(conn: sqlite3.Connection) -> None:
    """Run the full Kosovo seed: country + all regions.

    Args:
        conn: An open SQLite connection.
    """
    seed_country(conn)
    seed_regions(conn)


def main() -> None:
    """Open the production DB, seed Kosovo, and close."""
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s — %(message)s")
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    try:
        run(conn)
        conn.commit()
        logger.info("Kosovo seed complete")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
