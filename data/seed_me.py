"""Seed Montenegro (ME) into the CarTags database.

Inserts the country record, its translations, and 21 municipality records
with full translations in en/de/ru/uk.  All inserts are idempotent
via INSERT OR IGNORE.

Usage::

    python data/seed_me.py
"""

import logging
import sqlite3
from pathlib import Path

logger = logging.getLogger(__name__)

DB_PATH = Path(__file__).parent.parent / "db" / "cartags.db"

COUNTRY_CODE = "ME"
COUNTRY_EMOJI = "🇲🇪"
COUNTRY_SORT_ORDER = 11

_COUNTRY_TRANSLATIONS: dict[str, str] = {
    "en": "Montenegro",
    "de": "Montenegro",
    "ru": "Черногория",
    "uk": "Чорногорія",
}

_MONTENEGRO = {
    "en": "Montenegro",
    "de": "Montenegro",
    "ru": "Черногория",
    "uk": "Чорногорія",
}

_COORDS: dict[str, tuple[float, float]] = {
    "PG": (42.4411, 19.2636),  # Podgorica
    "BD": (42.0994, 19.1044),  # Bar
    "TG": (42.3997, 18.9128),  # Budva
    "KO": (42.5775, 18.9736),  # Kotor
    "HN": (43.5364, 18.5508),  # Pljevlja
    "NI": (43.1181, 19.5458),  # Bijelo Polje
    "BR": (43.3447, 19.8681),  # Berane
    "RO": (42.8336, 19.5189),  # Mojkovac
    "PV": (43.1497, 19.1253),  # Kolašin
    "AN": (42.2697, 19.7853),  # Plav
    "PL": (42.6361, 19.9447),  # Andrijevica
    "UL": (41.9222, 19.2181),  # Ulcinj
    "HE": (43.5364, 18.5508),  # Herceg Novi
    "CE": (42.3894, 18.6214),  # Cetinje
    "DG": (42.8667, 19.2167),  # Danilovgrad
    "NK": (42.7583, 18.9461),  # Nikšić
    "CT": (42.3894, 18.6214),  # Cetinje (alt)
    "ZB": (43.1497, 19.1253),  # Žabljak
    "SA": (43.2600, 19.8700),  # Šavnik
    "PT": (42.5833, 19.9167),  # Petnjica
    "GU": (43.3167, 19.8667),  # Gusinje
}

# (plate_code, name_en, name_de, name_ru, name_uk)
_REGION_ROWS: list[tuple[str, str, str, str, str]] = [
    ("PG", "Podgorica",   "Podgorica",   "Подгорица",   "Подгориця"),
    ("BD", "Bar",         "Bar",         "Бар",         "Бар"),
    ("TG", "Budva",       "Budva",       "Будва",       "Будва"),
    ("KO", "Kotor",       "Kotor",       "Котор",       "Котор"),
    ("HN", "Pljevlja",    "Pljevlja",    "Плевля",      "Плевля"),
    ("NI", "Bijelo Polje","Bijelo Polje","Биело-Поле",  "Бієло Поле"),
    ("BR", "Berane",      "Berane",      "Бераны",      "Берани"),
    ("RO", "Mojkovac",    "Mojkovac",    "Мойковац",    "Мойковаць"),
    ("PV", "Kolašin",     "Kolašin",     "Колашин",     "Колашин"),
    ("AN", "Plav",        "Plav",        "Плав",        "Плав"),
    ("PL", "Andrijevica", "Andrijevica", "Андриевица",  "Андрієвиця"),
    ("UL", "Ulcinj",      "Ulcinj",      "Ульцинь",     "Ульцинь"),
    ("HE", "Herceg Novi", "Herceg Novi", "Герцег-Нови", "Герцег-Нові"),
    ("CE", "Cetinje",     "Cetinje",     "Цетине",      "Цетіне"),
    ("DG", "Danilovgrad", "Danilovgrad", "Даниловград", "Даниловград"),
    ("NK", "Nikšić",      "Nikšić",      "Никшич",      "Нікшич"),
    ("ZB", "Žabljak",     "Žabljak",     "Жабляк",      "Жабляк"),
    ("SA", "Šavnik",      "Šavnik",      "Шавник",      "Шавник"),
    ("PT", "Petnjica",    "Petnjica",    "Петница",     "Петниця"),
    ("GU", "Gusinje",     "Gusinje",     "Гусинье",     "Гусіньє"),
    ("CT", "Cetinje (historic)", "Cetinje (hist.)", "Цетине (ист.)", "Цетіне (іст.)"),
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
    """Insert the ME country record and its translations.

    Args:
        conn: An open SQLite connection (foreign keys must be on).
    """
    country_id = _get_or_insert_country(conn)
    _insert_country_translations(conn, country_id)
    logger.info("Seeded country ME (id=%d)", country_id)


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
    """Insert one municipality and its translations."""
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
    _insert_region_translations(conn, row[0], name_trans, _MONTENEGRO)


def seed_regions(conn: sqlite3.Connection) -> None:
    """Insert all ME municipality records and their translations.

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
    logger.info("Seeded %d ME municipalities", len(_REGION_ROWS))


def run(conn: sqlite3.Connection) -> None:
    """Run the full Montenegro seed: country + all municipalities.

    Args:
        conn: An open SQLite connection.
    """
    seed_country(conn)
    seed_regions(conn)


def main() -> None:
    """Open the production DB, seed Montenegro, and close."""
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s — %(message)s")
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    try:
        run(conn)
        conn.commit()
        logger.info("Montenegro seed complete")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
