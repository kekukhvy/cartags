"""Seed Ireland (IE) into the CarTags database.

Inserts the country record, its translations, and 26 county records
with full translations in en/de/ru/uk.  All inserts are idempotent
via INSERT OR IGNORE.

Usage::

    python data/seed_ie.py
"""

import logging
import sqlite3
from pathlib import Path

logger = logging.getLogger(__name__)

DB_PATH = Path(__file__).parent.parent / "db" / "cartags.db"

COUNTRY_CODE = "IE"
COUNTRY_EMOJI = "🇮🇪"
COUNTRY_SORT_ORDER = 20

_COUNTRY_TRANSLATIONS: dict[str, str] = {
    "en": "Ireland",
    "de": "Irland",
    "ru": "Ирландия",
    "uk": "Ірландія",
}

_PROVINCE: dict[str, dict[str, str]] = {
    "Leinster": {
        "en": "Leinster",
        "de": "Leinster",
        "ru": "Ленстер",
        "uk": "Ленстер",
    },
    "Munster": {
        "en": "Munster",
        "de": "Munster",
        "ru": "Манстер",
        "uk": "Манстер",
    },
    "Connacht": {
        "en": "Connacht",
        "de": "Connacht",
        "ru": "Коннахт",
        "uk": "Коннахт",
    },
    "Ulster": {
        "en": "Ulster",
        "de": "Ulster",
        "ru": "Ольстер",
        "uk": "Ольстер",
    },
}

_COORDS: dict[str, tuple[float, float]] = {
    "D":  (53.3498, -6.2603),  # Dublin
    "C":  (51.8985, -8.4756),  # Cork
    "G":  (53.2707, -9.0568),  # Galway
    "L":  (52.6638, -8.6267),  # Limerick
    "W":  (52.2597, -6.9993),  # Waterford
    "KE": (53.2161, -6.9097),  # Kildare
    "MH": (53.5161, -6.6578),  # Meath
    "WH": (53.5333, -7.4667),  # Westmeath
    "WW": (52.9797, -6.0442),  # Wicklow
    "WX": (52.3348, -6.4564),  # Wexford
    "LS": (52.9922, -7.3300),  # Laois
    "OY": (53.1391, -7.4858),  # Offaly
    "KK": (52.6477, -7.2561),  # Kilkenny
    "CW": (52.8408, -6.9239),  # Carlow
    "LH": (53.9908, -6.4003),  # Louth
    "MN": (53.7311, -7.7933),  # Monaghan
    "CN": (53.9881, -7.5622),  # Cavan
    "LM": (53.7230, -7.9528),  # Longford
    "RN": (53.7950, -8.2944),  # Roscommon
    "MO": (53.8483, -9.3022),  # Mayo
    "SO": (54.2700, -8.4694),  # Sligo
    "LK": (53.9783, -8.4944),  # Leitrim
    "CE": (52.8408, -8.9822),  # Clare
    "TN": (52.4736, -8.1614),  # Tipperary (N)
    "TS": (52.2700, -7.7700),  # Tipperary (S)
    "KY": (52.0593, -9.5044),  # Kerry
    "DL": (54.9544, -7.7284),  # Donegal
}

# (plate_code, name_en, name_de, name_ru, name_uk, province_key)
_REGION_ROWS: list[tuple[str, str, str, str, str, str]] = [
    ("D",  "Dublin",             "Dublin",            "Дублин",           "Дублін",           "Leinster"),
    ("C",  "Cork",               "Cork",              "Корк",             "Корк",             "Munster"),
    ("G",  "Galway",             "Galway",            "Голуэй",           "Голуей",           "Connacht"),
    ("L",  "Limerick",           "Limerick",          "Лимерик",          "Лімерік",          "Munster"),
    ("W",  "Waterford",          "Waterford",         "Уотерфорд",        "Вотерфорд",        "Munster"),
    ("KE", "Kildare",            "Kildare",           "Килдэр",           "Килдер",           "Leinster"),
    ("MH", "Meath",              "Meath",             "Мит",              "Міт",              "Leinster"),
    ("WH", "Westmeath",          "Westmeath",         "Уэстмит",          "Вестміт",          "Leinster"),
    ("WW", "Wicklow",            "Wicklow",           "Уиклоу",           "Віклоу",           "Leinster"),
    ("WX", "Wexford",            "Wexford",           "Уэксфорд",         "Векфорд",          "Leinster"),
    ("LS", "Laois",              "Laois",             "Лиш",              "Ліш",              "Leinster"),
    ("OY", "Offaly",             "Offaly",            "Оффали",           "Оффалі",           "Leinster"),
    ("KK", "Kilkenny",           "Kilkenny",          "Килкенни",         "Кілкенні",         "Leinster"),
    ("CW", "Carlow",             "Carlow",            "Карлоу",           "Карлоу",           "Leinster"),
    ("LH", "Louth",              "Louth",             "Лаут",             "Лаут",             "Leinster"),
    ("MN", "Monaghan",           "Monaghan",          "Монаган",          "Монаган",          "Ulster"),
    ("CN", "Cavan",              "Cavan",             "Каван",            "Каван",            "Ulster"),
    ("LM", "Longford",           "Longford",          "Лонгфорд",         "Лонгфорд",         "Leinster"),
    ("RN", "Roscommon",          "Roscommon",         "Роскоммон",        "Роскоммон",        "Connacht"),
    ("MO", "Mayo",               "Mayo",              "Мейо",             "Мейо",             "Connacht"),
    ("SO", "Sligo",              "Sligo",             "Слайго",           "Слайго",           "Connacht"),
    ("LK", "Leitrim",            "Leitrim",           "Литрим",           "Лейтрим",          "Connacht"),
    ("CE", "Clare",              "Clare",             "Клэр",             "Клер",             "Munster"),
    ("TN", "Tipperary",          "Tipperary",         "Типперэри",        "Тіппераррі",       "Munster"),
    ("KY", "Kerry",              "Kerry",             "Керри",            "Керрі",            "Munster"),
    ("DL", "Donegal",            "Donegal",           "Донегол",          "Донеґал",          "Ulster"),
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
    """Insert the IE country record and its translations.

    Args:
        conn: An open SQLite connection (foreign keys must be on).
    """
    country_id = _get_or_insert_country(conn)
    _insert_country_translations(conn, country_id)
    logger.info("Seeded country IE (id=%d)", country_id)


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
    province_key: str,
    coords: tuple[float, float] | None,
) -> None:
    """Insert one county and its translations."""
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
    group_trans = _PROVINCE[province_key]
    _insert_region_translations(conn, row[0], name_trans, group_trans)


def seed_regions(conn: sqlite3.Connection) -> None:
    """Insert all IE county records and their translations.

    Args:
        conn: An open SQLite connection.
    """
    row = conn.execute("SELECT id FROM countries WHERE code = ?", (COUNTRY_CODE,)).fetchone()
    country_id: int = row[0]
    for plate_code, name_en, name_de, name_ru, name_uk, province_key in _REGION_ROWS:
        coords = _COORDS.get(plate_code.upper())
        _seed_single_region(
            conn, country_id, plate_code,
            name_en, name_de, name_ru, name_uk,
            province_key, coords,
        )
    logger.info("Seeded %d IE counties", len(_REGION_ROWS))


def run(conn: sqlite3.Connection) -> None:
    """Run the full Ireland seed: country + all counties.

    Args:
        conn: An open SQLite connection.
    """
    seed_country(conn)
    seed_regions(conn)


def main() -> None:
    """Open the production DB, seed Ireland, and close."""
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s — %(message)s")
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    try:
        run(conn)
        conn.commit()
        logger.info("Ireland seed complete")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
