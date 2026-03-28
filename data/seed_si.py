"""Seed Slovenia (SI) into the CarTags database.

Inserts the country record, its translations, and 13 statistical region records
with full translations in en/de/ru/uk.  All inserts are idempotent
via INSERT OR IGNORE.

Usage::

    python data/seed_si.py
"""

import logging
import sqlite3
from pathlib import Path

logger = logging.getLogger(__name__)

DB_PATH = Path(__file__).parent.parent / "db" / "cartags.db"

COUNTRY_CODE = "SI"
COUNTRY_EMOJI = "🇸🇮"
COUNTRY_SORT_ORDER = 10

_COUNTRY_TRANSLATIONS: dict[str, str] = {
    "en": "Slovenia",
    "de": "Slowenien",
    "ru": "Словения",
    "uk": "Словенія",
}

_SLOVENIA = {
    "en": "Slovenia",
    "de": "Slowenien",
    "ru": "Словения",
    "uk": "Словенія",
}

_COORDS: dict[str, tuple[float, float]] = {
    "LJ": (46.0569, 14.5058),  # Ljubljana
    "MB": (46.5547, 15.6467),  # Maribor
    "CE": (46.2319, 15.2681),  # Celje
    "KR": (46.2397, 14.3556),  # Kranj
    "NM": (45.8011, 15.1706),  # Novo Mesto
    "KP": (45.5469, 13.7294),  # Koper
    "MS": (46.6611, 16.1625),  # Murska Sobota
    "NG": (45.9597, 13.6472),  # Nova Gorica
    "SG": (46.5086, 15.8381),  # Slovenj Gradec
    "KK": (45.8736, 15.5297),  # Krško
    "GO": (46.0886, 15.4597),  # Laško
    "PO": (46.4253, 14.8486),  # Škofja Loka
    "RV": (46.6514, 15.6339),  # Ptuj (Radvanje)
}

# (plate_code, name_en, name_de, name_ru, name_uk)
_REGION_ROWS: list[tuple[str, str, str, str, str]] = [
    ("LJ", "Central Slovenia",     "Zentralslowenien",          "Центральная Словения",      "Центральна Словенія"),
    ("MB", "Drava Statistical Region", "Draustatistische Region","Дравский статистический регион","Дравський статистичний регіон"),
    ("CE", "Savinja Statistical Region","Sanntal-Region",        "Савиньский регион",         "Савиньський регіон"),
    ("KR", "Upper Carniola Region", "Oberkrainer Region",        "Верхнекраинский регион",    "Верхньокрайнський регіон"),
    ("NM", "Southeast Slovenia",    "Südostslowenien",           "Юго-Восточная Словения",    "Південно-Східна Словенія"),
    ("KP", "Coastal–Karst Region",  "Küstenkarstregion",         "Приморско-Карстовый регион","Приморсько-Карстовий регіон"),
    ("MS", "Mura Statistical Region","Murregion",                "Мурский регион",            "Мурський регіон"),
    ("NG", "Gorizia Statistical Region","Görzer Region",         "Горицийский регион",        "Горицький регіон"),
    ("SG", "Carinthia Statistical Region","Kärntner Region",     "Каринтийский регион",       "Карінтійський регіон"),
    ("KK", "Lower Sava Region",     "Untere Save-Region",        "Нижнесавский регион",       "Нижньосавський регіон"),
    ("GO", "Central Sava Region",   "Mittlere Save-Region",      "Среднесавский регион",      "Середньосавський регіон"),
    ("PO", "Upper Carniola (Škofja Loka)","Škofja Loka",         "Шкофья-Лока",               "Шкофья Лока"),
    ("RV", "Drava (Ptuj)",          "Ptuj",                      "Птуй",                      "Птуй"),
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
    """Insert the SI country record and its translations.

    Args:
        conn: An open SQLite connection (foreign keys must be on).
    """
    country_id = _get_or_insert_country(conn)
    _insert_country_translations(conn, country_id)
    logger.info("Seeded country SI (id=%d)", country_id)


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
    """Insert one statistical region and its translations."""
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
    _insert_region_translations(conn, row[0], name_trans, _SLOVENIA)


def seed_regions(conn: sqlite3.Connection) -> None:
    """Insert all SI region records and their translations.

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
    logger.info("Seeded %d SI regions", len(_REGION_ROWS))


def run(conn: sqlite3.Connection) -> None:
    """Run the full Slovenia seed: country + all regions.

    Args:
        conn: An open SQLite connection.
    """
    seed_country(conn)
    seed_regions(conn)


def main() -> None:
    """Open the production DB, seed Slovenia, and close."""
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s — %(message)s")
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    try:
        run(conn)
        conn.commit()
        logger.info("Slovenia seed complete")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
