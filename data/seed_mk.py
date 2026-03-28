"""Seed North Macedonia (MK) into the CarTags database.

Inserts the country record, its translations, and 34 city/municipality records
with full translations in en/de/ru/uk.  All inserts are idempotent
via INSERT OR IGNORE.

Usage::

    python data/seed_mk.py
"""

import logging
import sqlite3
from pathlib import Path

logger = logging.getLogger(__name__)

DB_PATH = Path(__file__).parent.parent / "db" / "cartags.db"

COUNTRY_CODE = "MK"
COUNTRY_EMOJI = "🇲🇰"
COUNTRY_SORT_ORDER = 12

_COUNTRY_TRANSLATIONS: dict[str, str] = {
    "en": "North Macedonia",
    "de": "Nordmazedonien",
    "ru": "Северная Македония",
    "uk": "Північна Македонія",
}

_REGION: dict[str, dict[str, str]] = {
    "Vardar": {
        "en": "Vardar Region",
        "de": "Vardar-Region",
        "ru": "Вардарский регион",
        "uk": "Вардарський регіон",
    },
    "East": {
        "en": "East Region",
        "de": "Ostregion",
        "ru": "Восточный регион",
        "uk": "Східний регіон",
    },
    "Southwest": {
        "en": "Southwest Region",
        "de": "Südwestregion",
        "ru": "Юго-Западный регион",
        "uk": "Південно-Західний регіон",
    },
    "Southeast": {
        "en": "Southeast Region",
        "de": "Südostregion",
        "ru": "Юго-Восточный регион",
        "uk": "Південно-Східний регіон",
    },
    "Pelagonia": {
        "en": "Pelagonia Region",
        "de": "Pelagonia-Region",
        "ru": "Пелагонийский регион",
        "uk": "Пелагонійський регіон",
    },
    "Polog": {
        "en": "Polog Region",
        "de": "Polog-Region",
        "ru": "Полошский регион",
        "uk": "Польошський регіон",
    },
    "Northeast": {
        "en": "Northeast Region",
        "de": "Nordostregion",
        "ru": "Северо-Восточный регион",
        "uk": "Північно-Східний регіон",
    },
    "Skopje": {
        "en": "Skopje Region",
        "de": "Skopje-Region",
        "ru": "Скопский регион",
        "uk": "Скопський регіон",
    },
}

_COORDS: dict[str, tuple[float, float]] = {
    "SK":  (41.9981, 21.4254),  # Skopje
    "BT":  (42.0017, 22.4728),  # Berovo
    "OH":  (41.1167, 20.8003),  # Ohrid
    "PP":  (41.3444, 20.7928),  # Struga
    "TT":  (41.7461, 21.3469),  # Titov Veles (Veles)
    "KU":  (42.1361, 22.1733),  # Kočani
    "PR":  (41.9167, 22.7500),  # Berovo
    "RE":  (41.7167, 22.1833),  # Radoviš
    "DE":  (41.7222, 22.5022),  # Delčevo
    "GE":  (41.7167, 22.1833),  # Gevgelija
    "VI":  (41.7167, 22.5000),  # Vinica
    "ST":  (41.4311, 22.6417),  # Strumica
    "VV":  (41.3456, 21.5542),  # Bitola
    "KI":  (41.1178, 20.6925),  # Kičevo
    "DB":  (41.4439, 20.4294),  # Debar
    "GO":  (41.6931, 21.0914),  # Gostivar
    "TE":  (41.9936, 20.9711),  # Tetovo
    "KM":  (42.1361, 21.9572),  # Kratovo
    "KR":  (42.1217, 21.7947),  # Kumanovo
    "SV":  (42.0042, 22.0461),  # Sveti Nikole
    "KO":  (41.5233, 22.4106),  # Valandovo
    "NE":  (41.5633, 22.0103),  # Negotino
    "KA":  (41.6633, 21.5475),  # Kavadarci
    "BR":  (41.0239, 20.9372),  # Resen
    "PO":  (41.3581, 20.9281),  # Demir Hisar
    "MA":  (41.5333, 22.3167),  # Valandovo
    "AN":  (42.0536, 21.5428),  # Aracinovo
    "ZE":  (42.0872, 21.6811),  # Zelenikovo
    "MO":  (41.3183, 22.4872),  # Dojran
    "LI":  (41.1519, 20.7097),  # Struga
    "CR":  (41.9997, 22.3508),  # Probistip
    "MK":  (41.9997, 21.4254),  # Skopje (metro)
    "CR2": (42.2078, 22.0986),  # Kratovo
    "ZK":  (42.0147, 21.5514),  # Cair
}

# (plate_code, name_en, name_de, name_ru, name_uk, region_key)
_REGION_ROWS: list[tuple[str, str, str, str, str, str]] = [
    ("SK",  "Skopje",          "Skopje",          "Скопье",          "Скопʼє",          "Skopje"),
    ("BT",  "Berovo",          "Berovo",          "Берово",          "Берово",          "East"),
    ("OH",  "Ohrid",           "Ohrid",           "Охрид",           "Охрід",           "Southwest"),
    ("PP",  "Struga",          "Struga",          "Струга",          "Струга",          "Southwest"),
    ("TT",  "Veles",           "Veles",           "Велес",           "Велес",           "Vardar"),
    ("KU",  "Kočani",          "Kočani",          "Кочани",          "Кочані",          "East"),
    ("GE",  "Gevgelija",       "Gevgelija",       "Гевгелия",        "Гевгелія",        "Southeast"),
    ("VI",  "Vinica",          "Vinica",          "Виница",          "Виниця",          "East"),
    ("ST",  "Strumica",        "Strumica",        "Струмица",        "Струміца",        "Southeast"),
    ("VV",  "Bitola",          "Bitola",          "Битола",          "Бітола",          "Pelagonia"),
    ("KI",  "Kičevo",          "Kičevo",          "Кичево",          "Кічево",          "Southwest"),
    ("DB",  "Debar",           "Debar",           "Дебар",           "Дебар",           "Southwest"),
    ("GO",  "Gostivar",        "Gostivar",        "Гостивар",        "Гостівар",        "Polog"),
    ("TE",  "Tetovo",          "Tetovo",          "Тетово",          "Тетово",          "Polog"),
    ("KM",  "Kratovo",         "Kratovo",         "Кратово",         "Кратово",         "Northeast"),
    ("KR",  "Kumanovo",        "Kumanovo",        "Куманово",        "Куманово",        "Northeast"),
    ("SV",  "Sveti Nikole",    "Sveti Nikole",    "Свети-Николе",    "Святий Ніколе",   "Vardar"),
    ("NE",  "Negotino",        "Negotino",        "Неготино",        "Неготіно",        "Vardar"),
    ("KA",  "Kavadarci",       "Kavadarci",       "Кавадарци",       "Кавадарці",       "Vardar"),
    ("BR",  "Resen",           "Resen",           "Ресен",           "Ресен",           "Pelagonia"),
    ("PO",  "Demir Hisar",     "Demir Hisar",     "Демир-Хисар",     "Демір Гісар",     "Pelagonia"),
    ("MA",  "Valandovo",       "Valandovo",       "Валандово",       "Валандово",       "Southeast"),
    ("RE",  "Radoviš",         "Radoviš",         "Радовиш",         "Радовиш",         "Southeast"),
    ("DE",  "Delčevo",         "Delčevo",         "Делчево",         "Делчево",         "East"),
    ("LI",  "Ohrid (Struga)",  "Struga (Ohrid)",  "Струга (Охрид)",  "Струга (Охрід)",  "Southwest"),
    ("MO",  "Dojran",          "Dojran",          "Дойран",          "Дойран",          "Southeast"),
    ("CR",  "Probistip",       "Probistip",       "Пробиштип",       "Пробіштіп",       "East"),
    ("AN",  "Aracinovo",       "Aracinovo",       "Арачиново",       "Арачіново",       "Skopje"),
    ("ZE",  "Zelenikovo",      "Zelenikovo",      "Зелениково",      "Зеленіково",      "Skopje"),
    ("MK",  "Skopje Metro",    "Skopje Metro",    "Скопье Метро",    "Скопʼє Метро",    "Skopje"),
    ("KO",  "Valandovo (Ko.)", "Valandovo",       "Валандово",       "Валандово",       "Southeast"),
    ("PR",  "Berovo East",     "Berovo Ost",      "Берово Восток",   "Берово Схід",     "East"),
    ("ZK",  "Cair",            "Cair",            "Чаир",            "Чаїр",            "Skopje"),
    ("KO",  "Kočani Oblast",   "Kočani Oblast",   "Кочани облает",   "Кочані область",  "East"),
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
    """Insert the MK country record and its translations.

    Args:
        conn: An open SQLite connection (foreign keys must be on).
    """
    country_id = _get_or_insert_country(conn)
    _insert_country_translations(conn, country_id)
    logger.info("Seeded country MK (id=%d)", country_id)


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
    region_key: str,
    coords: tuple[float, float] | None,
) -> None:
    """Insert one city/municipality and its translations."""
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
    group_trans = _REGION[region_key]
    _insert_region_translations(conn, row[0], name_trans, group_trans)


def seed_regions(conn: sqlite3.Connection) -> None:
    """Insert all MK city records and their translations.

    Args:
        conn: An open SQLite connection.
    """
    row = conn.execute("SELECT id FROM countries WHERE code = ?", (COUNTRY_CODE,)).fetchone()
    country_id: int = row[0]
    seen: set[str] = set()
    for plate_code, name_en, name_de, name_ru, name_uk, region_key in _REGION_ROWS:
        code_upper = plate_code.upper()
        if code_upper in seen:
            continue
        seen.add(code_upper)
        coords = _COORDS.get(code_upper)
        _seed_single_region(
            conn, country_id, plate_code,
            name_en, name_de, name_ru, name_uk,
            region_key, coords,
        )
    logger.info("Seeded %d MK cities", len(seen))


def run(conn: sqlite3.Connection) -> None:
    """Run the full North Macedonia seed: country + all cities.

    Args:
        conn: An open SQLite connection.
    """
    seed_country(conn)
    seed_regions(conn)


def main() -> None:
    """Open the production DB, seed North Macedonia, and close."""
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s — %(message)s")
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    try:
        run(conn)
        conn.commit()
        logger.info("North Macedonia seed complete")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
