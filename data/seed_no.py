"""Seed Norway (NO) into the CarTags database.

Inserts the country record, its translations, and 15 county (Fylke) records
using the pre-2018 plate code system.  Full translations in en/de/ru/uk.
All inserts are idempotent via INSERT OR IGNORE.

Usage::

    python data/seed_no.py
"""

import logging
import sqlite3
from pathlib import Path

logger = logging.getLogger(__name__)

DB_PATH = Path(__file__).parent.parent / "db" / "cartags.db"

COUNTRY_CODE = "NO"
COUNTRY_EMOJI = "🇳🇴"
COUNTRY_SORT_ORDER = 19

_COUNTRY_TRANSLATIONS: dict[str, str] = {
    "en": "Norway",
    "de": "Norwegen",
    "ru": "Норвегия",
    "uk": "Норвегія",
}

_NORWAY = {
    "en": "Norway",
    "de": "Norwegen",
    "ru": "Норвегия",
    "uk": "Норвегія",
}

_COORDS: dict[str, tuple[float, float]] = {
    "M":  (59.9139, 10.7522),  # Oslo
    "A":  (59.9139, 10.7522),  # Akershus
    "B":  (59.2839, 10.4076),  # Østfold (Fredrikstad)
    "C":  (60.7945, 11.0676),  # Hedmark (Hamar)
    "D":  (60.7965, 10.6915),  # Oppland (Lillehammer)
    "E":  (59.7447, 10.2046),  # Buskerud (Drammen)
    "F":  (59.2167, 10.3833),  # Vestfold (Tønsberg)
    "G":  (59.1330, 9.7341),   # Telemark (Skien)
    "H":  (58.4630, 8.7726),   # Aust-Agder (Arendal)
    "I":  (58.1464, 7.9960),   # Vest-Agder (Kristiansand)
    "K":  (58.9700, 5.7331),   # Rogaland (Stavanger)
    "L":  (60.3913, 5.3221),   # Hordaland (Bergen)
    "N":  (61.6333, 5.8500),   # Sogn og Fjordane (Leikanger)
    "R":  (62.7372, 7.1681),   # Møre og Romsdal (Molde)
    "S":  (63.4305, 10.3951),  # Sør-Trøndelag (Trondheim)
    "T":  (64.4680, 11.4938),  # Nord-Trøndelag (Steinkjer)
    "U":  (67.2803, 14.4049),  # Nordland (Bodø)
    "V":  (69.6492, 18.9560),  # Troms (Tromsø)
    "X":  (69.9739, 23.2717),  # Finnmark (Alta)
}

# (plate_code, name_en, name_de, name_ru, name_uk)
_REGION_ROWS: list[tuple[str, str, str, str, str]] = [
    ("M", "Oslo",              "Oslo",              "Осло",              "Осло"),
    ("A", "Akershus",          "Akershus",          "Акерсхус",          "Акерсгус"),
    ("B", "Østfold",           "Østfold",           "Эстфолл",           "Естфолл"),
    ("C", "Hedmark",           "Hedmark",           "Хедмарк",           "Гедмарк"),
    ("D", "Oppland",           "Oppland",           "Оппланн",           "Опплан"),
    ("E", "Buskerud",          "Buskerud",          "Бускеруд",          "Бускеруд"),
    ("F", "Vestfold",          "Vestfold",          "Вестфолл",          "Вестфолл"),
    ("G", "Telemark",          "Telemark",          "Телемарк",          "Телемарк"),
    ("H", "Aust-Agder",        "Aust-Agder",        "Ауст-Агдер",        "Ауст-Аґдер"),
    ("I", "Vest-Agder",        "Vest-Agder",        "Вест-Агдер",        "Вест-Аґдер"),
    ("K", "Rogaland",          "Rogaland",          "Ругаланн",          "Роґаланн"),
    ("L", "Hordaland",         "Hordaland",         "Хордаланн",         "Горданн"),
    ("N", "Sogn og Fjordane",  "Sogn og Fjordane",  "Согн-ог-Фьюране",   "Согн-ог-Фьордане"),
    ("R", "Møre og Romsdal",   "Møre og Romsdal",   "Мёре-ог-Ромсдал",   "Мере-ог-Ромсдал"),
    ("S", "Sør-Trøndelag",     "Sør-Trøndelag",     "Сёр-Трённелаг",     "Сер-Тренделаг"),
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
    """Insert the NO country record and its translations.

    Args:
        conn: An open SQLite connection (foreign keys must be on).
    """
    country_id = _get_or_insert_country(conn)
    _insert_country_translations(conn, country_id)
    logger.info("Seeded country NO (id=%d)", country_id)


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
    """Insert one fylke and its translations."""
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
    _insert_region_translations(conn, row[0], name_trans, _NORWAY)


def seed_regions(conn: sqlite3.Connection) -> None:
    """Insert all NO fylke records and their translations.

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
    logger.info("Seeded %d NO fylker", len(_REGION_ROWS))


def run(conn: sqlite3.Connection) -> None:
    """Run the full Norway seed: country + all fylker.

    Args:
        conn: An open SQLite connection.
    """
    seed_country(conn)
    seed_regions(conn)


def main() -> None:
    """Open the production DB, seed Norway, and close."""
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s — %(message)s")
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    try:
        run(conn)
        conn.commit()
        logger.info("Norway seed complete")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
