"""Seed Bulgaria (BG) into the CarTags database.

Inserts the country record, its translations, and 28 oblast records
with full translations in en/de/ru/uk.  All inserts are idempotent
via INSERT OR IGNORE.

Usage::

    python data/seed_bg.py
"""

import logging
import sqlite3
from pathlib import Path

logger = logging.getLogger(__name__)

DB_PATH = Path(__file__).parent.parent / "db" / "cartags.db"

COUNTRY_CODE = "BG"
COUNTRY_EMOJI = "🇧🇬"
COUNTRY_SORT_ORDER = 7

_COUNTRY_TRANSLATIONS: dict[str, str] = {
    "en": "Bulgaria",
    "de": "Bulgarien",
    "ru": "Болгария",
    "uk": "Болгарія",
}

_BULGARIA = {
    "en": "Bulgaria",
    "de": "Bulgarien",
    "ru": "Болгария",
    "uk": "Болгарія",
}

_COORDS: dict[str, tuple[float, float]] = {
    "A":  (42.6977, 23.3219),  # Sofia
    "B":  (43.2141, 27.9147),  # Varna
    "BH": (42.4958, 27.4723),  # Burgas
    "BL": (43.4081, 23.2247),  # Montana
    "C":  (43.8556, 25.9678),  # Ruse
    "CB": (42.5000, 25.3333),  # Stara Zagora
    "CH": (43.3708, 22.8686),  # Vidin
    "CO": (42.1354, 24.7453),  # Plovdiv
    "CT": (42.4667, 27.4667),  # Burgas (city)
    "E":  (41.6818, 26.5565),  # Haskovo
    "EB": (42.8767, 25.3228),  # Gabrovo
    "EH": (42.6167, 26.5833),  # Yambol
    "EN": (43.6667, 25.3500),  # Lovech
    "ET": (43.0833, 25.6667),  # Targovishte
    "H":  (43.6167, 25.3500),  # Lovech
    "HK": (41.9167, 25.5500),  # Kardzhali
    "K":  (43.8333, 24.0167),  # Pleven
    "KN": (43.9833, 22.8667),  # Vratsa
    "KY": (42.0833, 25.3667),  # Smolyan
    "M":  (41.9967, 21.4325),  # Blagoevgrad
    "OB": (43.5667, 27.9667),  # Dobrich
    "P":  (42.1500, 24.7500),  # Plovdiv
    "PA": (42.7500, 24.3333),  # Pazardzhik
    "PB": (42.5500, 24.3333),  # Plovdiv (south)
    "PK": (41.6667, 23.4833),  # Kyustendil
    "PP": (42.1167, 24.1500),  # Pernik
    "RR": (42.0333, 23.5500),  # Kyustendil
    "SD": (42.6977, 23.3219),  # Sofia (city)
    "SL": (42.6833, 23.3167),  # Sofia
    "SS": (42.6833, 23.3167),  # Sofia oblast
    "T":  (43.8889, 25.3658),  # Targovishte
    "TX": (41.9167, 25.5500),  # Kardzhali
    "VB": (43.2050, 26.6919),  # Shumen
    "VH": (43.9667, 25.6167),  # Vidin
    "VN": (43.2050, 26.6919),  # Shumen (Novi Pazar)
    "VR": (43.2000, 23.5500),  # Vratsa
    "VT": (43.0767, 25.6511),  # Veliko Tarnovo
    "X":  (41.5500, 26.3333),  # Haskovo
    "Y":  (42.4833, 27.4667),  # Burgas
}

# (plate_code, name_en, name_de, name_ru, name_uk)
_REGION_ROWS: list[tuple[str, str, str, str, str]] = [
    ("A",  "Sofia (city)",          "Sofia (Stadt)",         "София (город)",          "Софія (місто)"),
    ("B",  "Varna",                  "Warna",                  "Варна",                  "Варна"),
    ("BH", "Burgas",                 "Burgas",                 "Бургас",                 "Бургас"),
    ("BL", "Montana",                "Montana",                "Монтана",                "Монтана"),
    ("C",  "Ruse",                   "Russe",                  "Русе",                   "Русе"),
    ("CB", "Stara Zagora",           "Stara Sagora",           "Стара-Загора",           "Стара Загора"),
    ("CH", "Vidin",                  "Widin",                  "Видин",                  "Відін"),
    ("CO", "Plovdiv",                "Plowdiw",                "Пловдив",                "Пловдів"),
    ("E",  "Haskovo",                "Haskovo",                "Хасково",                "Хасково"),
    ("EB", "Gabrovo",                "Gabrowo",                "Габрово",                "Габрово"),
    ("EH", "Yambol",                 "Jambol",                 "Ямбол",                  "Ямбол"),
    ("EN", "Lovech",                 "Lowetsch",               "Ловеч",                  "Ловеч"),
    ("ET", "Targovishte",            "Targowitsche",           "Търговище",              "Търговіще"),
    ("H",  "Pleven",                 "Plewen",                 "Плевен",                 "Плевен"),
    ("HK", "Kardzhali",              "Kardschali",             "Кырджали",               "Кирджалі"),
    ("K",  "Pleven (city)",          "Plewen (Stadt)",         "Плевен (город)",         "Плевен (місто)"),
    ("KN", "Vratsa",                 "Wraza",                  "Враца",                  "Враца"),
    ("KY", "Smolyan",                "Smoljan",                "Смолян",                 "Смолян"),
    ("M",  "Blagoevgrad",            "Blagojewgrad",           "Благоевград",            "Благоєвград"),
    ("OB", "Dobrich",                "Dobritsch",              "Добрич",                 "Добрич"),
    ("P",  "Plovdiv (city)",         "Plowdiw (Stadt)",        "Пловдив (город)",        "Пловдів (місто)"),
    ("PA", "Pazardzhik",             "Pasardschik",            "Пазарджик",              "Пазарджик"),
    ("PB", "Pernik",                 "Pernik",                 "Перник",                 "Перник"),
    ("PK", "Kyustendil",             "Kjustendil",             "Кюстендил",              "Кюстенділ"),
    ("PP", "Sliven",                 "Sliwno",                 "Сливен",                 "Сливен"),
    ("SD", "Sofia (district)",       "Sofia (Bezirk)",         "Софийская область",      "Софійська область"),
    ("T",  "Targovishte (city)",     "Targowitsche (Stadt)",   "Търговище (город)",      "Търговіще (місто)"),
    ("VT", "Veliko Tarnovo",         "Tarnowo",                "Велико-Тырново",         "Велико Тирново"),
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
    """Insert the BG country record and its translations.

    Args:
        conn: An open SQLite connection (foreign keys must be on).
    """
    country_id = _get_or_insert_country(conn)
    _insert_country_translations(conn, country_id)
    logger.info("Seeded country BG (id=%d)", country_id)


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
        (country_id, plate_code.upper(), lat, lon),
    )
    row = conn.execute(
        "SELECT id FROM regions WHERE country_id = ? AND plate_code = ?",
        (country_id, plate_code.upper()),
    ).fetchone()
    name_trans = {"en": name_en, "de": name_de, "ru": name_ru, "uk": name_uk}
    _insert_region_translations(conn, row[0], name_trans, _BULGARIA)


def seed_regions(conn: sqlite3.Connection) -> None:
    """Insert all BG oblast records and their translations.

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
    logger.info("Seeded %d BG oblasts", len(_REGION_ROWS))


def run(conn: sqlite3.Connection) -> None:
    """Run the full Bulgaria seed: country + all oblasts.

    Args:
        conn: An open SQLite connection.
    """
    seed_country(conn)
    seed_regions(conn)


def main() -> None:
    """Open the production DB, seed Bulgaria, and close."""
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s — %(message)s")
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    try:
        run(conn)
        conn.commit()
        logger.info("Bulgaria seed complete")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
