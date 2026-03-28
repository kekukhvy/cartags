"""Seed Switzerland (CH) into the CarTags database.

Inserts the country record, its translations, and 26 canton records
with full translations in en/de/ru/uk.  All inserts are idempotent
via INSERT OR IGNORE.

Usage::

    python data/seed_ch.py
"""

import logging
import sqlite3
from pathlib import Path

logger = logging.getLogger(__name__)

DB_PATH = Path(__file__).parent.parent / "db" / "cartags.db"

COUNTRY_CODE = "CH"
COUNTRY_EMOJI = "🇨🇭"
COUNTRY_SORT_ORDER = 4

_COUNTRY_TRANSLATIONS: dict[str, str] = {
    "en": "Switzerland",
    "de": "Schweiz",
    "ru": "Швейцария",
    "uk": "Швейцарія",
}

_SWITZERLAND = {
    "en": "Switzerland",
    "de": "Schweiz",
    "ru": "Швейцария",
    "uk": "Швейцарія",
}

_COORDS: dict[str, tuple[float, float]] = {
    "ZH": (47.3769, 8.5417),    # Zürich
    "BE": (46.9481, 7.4474),    # Bern
    "LU": (47.0502, 8.3093),    # Lucerne
    "UR": (46.8850, 8.6359),    # Altdorf
    "SZ": (47.0219, 8.6528),    # Schwyz
    "OW": (46.8961, 8.2406),    # Sarnen
    "NW": (46.9575, 8.3639),    # Stans
    "GL": (47.0403, 9.0678),    # Glarus
    "ZG": (47.1660, 8.5150),    # Zug
    "FR": (46.8065, 7.1615),    # Fribourg
    "SO": (47.2088, 7.5323),    # Solothurn
    "BS": (47.5596, 7.5886),    # Basel
    "BL": (47.4817, 7.7289),    # Liestal
    "SH": (47.6967, 8.6342),    # Schaffhausen
    "AR": (47.3849, 9.2803),    # Herisau
    "AI": (47.3333, 9.4167),    # Appenzell
    "SG": (47.4245, 9.3767),    # St. Gallen
    "GR": (46.8500, 9.5333),    # Chur
    "AG": (47.3925, 8.0444),    # Aarau
    "TG": (47.5584, 9.0919),    # Frauenfeld
    "TI": (46.3317, 8.8008),    # Bellinzona
    "VD": (46.5197, 6.6323),    # Lausanne
    "VS": (46.2270, 7.3606),    # Sion
    "NE": (46.9900, 6.9293),    # Neuchâtel
    "GE": (46.2044, 6.1432),    # Geneva
    "JU": (47.3667, 7.3500),    # Delémont
}

# (plate_code, name_en, name_de, name_ru, name_uk)
_REGION_ROWS: list[tuple[str, str, str, str, str]] = [
    ("ZH", "Zurich", "Zürich", "Цюрих", "Цюрих"),
    ("BE", "Bern", "Bern", "Берн", "Берн"),
    ("LU", "Lucerne", "Luzern", "Люцерн", "Люцерн"),
    ("UR", "Uri", "Uri", "Ури", "Урі"),
    ("SZ", "Schwyz", "Schwyz", "Швиц", "Швіц"),
    ("OW", "Obwalden", "Obwalden", "Обвальден", "Обвальден"),
    ("NW", "Nidwalden", "Nidwalden", "Нидвальден", "Нідвальден"),
    ("GL", "Glarus", "Glarus", "Гларус", "Ґларус"),
    ("ZG", "Zug", "Zug", "Цуг", "Цуґ"),
    ("FR", "Fribourg", "Freiburg", "Фрибур", "Фрибур"),
    ("SO", "Solothurn", "Solothurn", "Золотурн", "Золотурн"),
    ("BS", "Basel-City", "Basel-Stadt", "Базель-Штадт", "Базель-Штадт"),
    ("BL", "Basel-Landschaft", "Basel-Landschaft", "Базель-Ланд", "Базель-Ланд"),
    ("SH", "Schaffhausen", "Schaffhausen", "Шаффхаузен", "Шаффгаузен"),
    ("AR", "Appenzell Ausserrhoden", "Appenzell Ausserrhoden", "Аппенцелль-Ауссерроден", "Аппенцелль-Ауссерроден"),
    ("AI", "Appenzell Innerrhoden", "Appenzell Innerrhoden", "Аппенцелль-Иннерроден", "Аппенцелль-Іннерроден"),
    ("SG", "St. Gallen", "St. Gallen", "Санкт-Галлен", "Санкт-Галлен"),
    ("GR", "Graubünden", "Graubünden", "Граубюнден", "Граубюнден"),
    ("AG", "Aargau", "Aargau", "Аргау", "Аргау"),
    ("TG", "Thurgau", "Thurgau", "Тургау", "Тургау"),
    ("TI", "Ticino", "Tessin", "Тичино", "Тічіно"),
    ("VD", "Vaud", "Waadt", "Во", "Во"),
    ("VS", "Valais", "Wallis", "Валлис", "Вале"),
    ("NE", "Neuchâtel", "Neuenburg", "Невшатель", "Невшатель"),
    ("GE", "Geneva", "Genf", "Женева", "Женева"),
    ("JU", "Jura", "Jura", "Юра", "Юра"),
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
    """Insert the CH country record and its translations.

    Args:
        conn: An open SQLite connection (foreign keys must be on).
    """
    country_id = _get_or_insert_country(conn)
    _insert_country_translations(conn, country_id)
    logger.info("Seeded country CH (id=%d)", country_id)


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
    """Insert one canton and its translations."""
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
    _insert_region_translations(conn, row[0], name_trans, _SWITZERLAND)


def seed_regions(conn: sqlite3.Connection) -> None:
    """Insert all CH canton records and their translations.

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
    logger.info("Seeded %d CH cantons", len(_REGION_ROWS))


def run(conn: sqlite3.Connection) -> None:
    """Run the full Switzerland seed: country + all cantons.

    Args:
        conn: An open SQLite connection.
    """
    seed_country(conn)
    seed_regions(conn)


def main() -> None:
    """Open the production DB, seed Switzerland, and close."""
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s — %(message)s")
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    try:
        run(conn)
        conn.commit()
        logger.info("Switzerland seed complete")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
