"""Seed Belarus (BY) into the CarTags database.

Inserts the country record, its translations, and 7 region records
(6 oblasts + Minsk city) with full translations in en/de/ru/uk.
Plate codes are single digits stored as strings.
All inserts are idempotent via INSERT OR IGNORE.

Usage::

    python data/seed_by.py
"""

import logging
import sqlite3
from pathlib import Path

logger = logging.getLogger(__name__)

DB_PATH = Path(__file__).parent.parent / "db" / "cartags.db"

COUNTRY_CODE = "BY"
COUNTRY_EMOJI = "🇧🇾"
COUNTRY_SORT_ORDER = 15

_COUNTRY_TRANSLATIONS: dict[str, str] = {
    "en": "Belarus",
    "de": "Belarus",
    "ru": "Беларусь",
    "uk": "Білорусь",
}

_BELARUS = {
    "en": "Belarus",
    "de": "Belarus",
    "ru": "Беларусь",
    "uk": "Білорусь",
}

_COORDS: dict[str, tuple[float, float]] = {
    "1": (53.9045, 27.5615),  # Minsk city
    "2": (53.9045, 27.5615),  # Minsk Oblast (uses Minsk city as centre)
    "3": (52.4227, 31.0156),  # Gomel
    "4": (53.6884, 23.8258),  # Grodno
    "5": (53.9021, 30.3294),  # Mogilev
    "6": (55.1904, 30.2049),  # Vitebsk
    "7": (52.0977, 26.0939),  # Brest
}

# (plate_code, name_en, name_de, name_ru, name_uk)
_REGION_ROWS: list[tuple[str, str, str, str, str]] = [
    ("1", "Minsk City",    "Minsk (Stadt)",   "Минск (город)",    "Мінськ (місто)"),
    ("2", "Minsk Oblast",  "Minsk (Gebiet)",  "Минская область",  "Мінська область"),
    ("3", "Gomel Oblast",  "Gomel (Gebiet)",  "Гомельская область","Гомельська область"),
    ("4", "Grodno Oblast", "Grodno (Gebiet)", "Гродненская область","Гродненська область"),
    ("5", "Mogilev Oblast","Mogiljow (Gebiet)","Могилёвская область","Могилівська область"),
    ("6", "Vitebsk Oblast","Witebsk (Gebiet)","Витебская область", "Вітебська область"),
    ("7", "Brest Oblast",  "Brest (Gebiet)",  "Брестская область", "Брестська область"),
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
    """Insert the BY country record and its translations.

    Args:
        conn: An open SQLite connection (foreign keys must be on).
    """
    country_id = _get_or_insert_country(conn)
    _insert_country_translations(conn, country_id)
    logger.info("Seeded country BY (id=%d)", country_id)


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
    """Insert one oblast and its translations."""
    lat = coords[0] if coords else None
    lon = coords[1] if coords else None
    conn.execute(
        "INSERT OR IGNORE INTO regions"
        " (country_id, plate_code, latitude, longitude) VALUES (?, ?, ?, ?)",
        (country_id, plate_code, lat, lon),
    )
    row = conn.execute(
        "SELECT id FROM regions WHERE country_id = ? AND plate_code = ?",
        (country_id, plate_code),
    ).fetchone()
    name_trans = {"en": name_en, "de": name_de, "ru": name_ru, "uk": name_uk}
    _insert_region_translations(conn, row[0], name_trans, _BELARUS)


def seed_regions(conn: sqlite3.Connection) -> None:
    """Insert all BY oblast records and their translations.

    Args:
        conn: An open SQLite connection.
    """
    row = conn.execute("SELECT id FROM countries WHERE code = ?", (COUNTRY_CODE,)).fetchone()
    country_id: int = row[0]
    for plate_code, name_en, name_de, name_ru, name_uk in _REGION_ROWS:
        coords = _COORDS.get(plate_code)
        _seed_single_region(
            conn, country_id, plate_code,
            name_en, name_de, name_ru, name_uk,
            coords,
        )
    logger.info("Seeded %d BY oblasts", len(_REGION_ROWS))


def run(conn: sqlite3.Connection) -> None:
    """Run the full Belarus seed: country + all oblasts.

    Args:
        conn: An open SQLite connection.
    """
    seed_country(conn)
    seed_regions(conn)


def main() -> None:
    """Open the production DB, seed Belarus, and close."""
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s — %(message)s")
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    try:
        run(conn)
        conn.commit()
        logger.info("Belarus seed complete")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
