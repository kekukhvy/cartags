"""Seed Serbia (RS) into the CarTags database.

Inserts the country record, its translations, and ~30 region records
with full translations in en/de/ru/uk.  All inserts are idempotent
via INSERT OR IGNORE.

Usage::

    python data/seed_rs.py
"""

import logging
import sqlite3
from pathlib import Path

logger = logging.getLogger(__name__)

DB_PATH = Path(__file__).parent.parent / "db" / "cartags.db"

COUNTRY_CODE = "RS"
COUNTRY_EMOJI = "🇷🇸"
COUNTRY_SORT_ORDER = 9

_COUNTRY_TRANSLATIONS: dict[str, str] = {
    "en": "Serbia",
    "de": "Serbien",
    "ru": "Сербия",
    "uk": "Сербія",
}

_OKRUG: dict[str, dict[str, str]] = {
    "Vojvodina": {
        "en": "Vojvodina",
        "de": "Vojvodina",
        "ru": "Воеводина",
        "uk": "Воєводина",
    },
    "Belgrade": {
        "en": "Belgrade District",
        "de": "Belgrader Bezirk",
        "ru": "Белградский округ",
        "uk": "Белградський округ",
    },
    "Sumadija": {
        "en": "Šumadija and Western Serbia",
        "de": "Šumadija und Westserbien",
        "ru": "Шумадия и Западная Сербия",
        "uk": "Шумадія та Західна Сербія",
    },
    "South": {
        "en": "Southern and Eastern Serbia",
        "de": "Süd- und Ostserbien",
        "ru": "Южная и Восточная Сербия",
        "uk": "Південна та Східна Сербія",
    },
    "Kosovo": {
        "en": "Kosovo and Metohija",
        "de": "Kosovo und Metochien",
        "ru": "Косово и Метохия",
        "uk": "Косово та Метохія",
    },
}

_COORDS: dict[str, tuple[float, float]] = {
    "BG": (44.8176, 20.4569),  # Belgrade
    "NS": (45.2671, 19.8335),  # Novi Sad
    "NI": (43.3209, 21.8954),  # Niš
    "KG": (43.9933, 20.9253),  # Kragujevac
    "KR": (43.7230, 20.6878),  # Kraljevo
    "SU": (45.7928, 19.1714),  # Subotica
    "ZA": (44.0167, 19.7000),  # Užice (Zlatibor)
    "SO": (44.1000, 22.0833),  # Bor
    "PO": (44.3667, 21.1833),  # Požarevac
    "SM": (44.9667, 19.6167),  # Sremska Mitrovica
    "PA": (45.2433, 20.7108),  # Pančevo
    "VR": (45.1000, 21.3000),  # Vršac
    "ZR": (43.8886, 21.4644),  # Zaječar
    "PR": (42.2167, 20.7333),  # Prizren
    "PE": (42.6608, 20.2886),  # Peć
    "UR": (43.8667, 20.7167),  # Užice
    "KV": (43.7000, 21.3833),  # Kruševac
    "PI": (43.1500, 22.3500),  # Pirot
    "LN": (43.5000, 21.9667),  # Leskovac
    "LK": (43.0000, 21.9500),  # Leskovac (south)
    "LA": (43.3000, 21.9167),  # Leskovac (north)
    "JA": (42.4667, 21.7500),  # Vranje
    "VJ": (42.5500, 21.9000),  # Vranje south
    "TO": (45.1333, 19.7500),  # Titel
    "IN": (45.8000, 19.6333),  # Inđija
    "SK": (44.9667, 20.1167),  # Stara Pazova
    "RU": (44.1000, 22.1000),  # Majdanpek
    "AB": (43.7000, 20.2500),  # Arilje
    "SV": (43.4000, 21.5000),  # Svrljig
    "BO": (44.3000, 22.1167),  # Boljevac
}

# (plate_code, name_en, name_de, name_ru, name_uk, okrug_key)
_REGION_ROWS: list[tuple[str, str, str, str, str, str]] = [
    ("BG", "Belgrade",              "Belgrad",               "Белград",                "Белград",                "Belgrade"),
    ("NS", "Novi Sad",              "Neusatz",               "Нови-Сад",               "Новий Сад",              "Vojvodina"),
    ("NI", "Niš",                   "Nisch",                 "Ниш",                    "Ніш",                    "South"),
    ("KG", "Kragujevac",            "Kragujevac",            "Крагуевац",              "Крагуєваць",             "Sumadija"),
    ("KR", "Kraljevo",              "Kraljevo",              "Кральево",               "Кральєво",               "Sumadija"),
    ("SU", "Subotica",              "Subotica",              "Суботица",               "Суботиця",               "Vojvodina"),
    ("ZA", "Zlatibor District",     "Zlatibor-Bezirk",       "Злачиборский округ",     "Златиборський округ",    "Sumadija"),
    ("SO", "Bor District",          "Bor-Bezirk",            "Борский округ",          "Борський округ",         "South"),
    ("PO", "Braničevo District",    "Braničevo-Bezirk",      "Браничевский округ",     "Браничевський округ",    "Sumadija"),
    ("SM", "Srem District",         "Syrmien-Bezirk",        "Сремский округ",         "Сремський округ",        "Vojvodina"),
    ("PA", "South Banat District",  "Südbanat-Bezirk",       "Южно-Банатский округ",   "Південно-Банатський округ", "Vojvodina"),
    ("VR", "South Banat (Vršac)",   "Vršac",                 "Вршац",                  "Вршаць",                 "Vojvodina"),
    ("ZR", "Zaječar District",      "Zaječar-Bezirk",        "Зайчарский округ",       "Зайчарський округ",      "South"),
    ("PR", "Prizren",               "Prizren",               "Призрен",                "Призрен",                "Kosovo"),
    ("PE", "Peć",                   "Peja",                  "Печ",                    "Печ",                    "Kosovo"),
    ("UR", "Zlatibor (Užice)",      "Užice",                 "Ужице",                  "Ужіце",                  "Sumadija"),
    ("KV", "Rasina District",       "Rasina-Bezirk",         "Расинский округ",        "Расинський округ",       "Sumadija"),
    ("PI", "Pirot District",        "Pirot-Bezirk",          "Пиротский округ",        "Піротський округ",       "South"),
    ("LN", "Jablanica District",    "Jablanica-Bezirk",      "Яблоничский округ",      "Яблоничський округ",     "South"),
    ("JA", "Pčinja District",       "Pčinja-Bezirk",         "Пчиньский округ",        "Пчинський округ",        "South"),
    ("IN", "Srem (Inđija)",         "Indjija",               "Индийя",                 "Інджія",                 "Vojvodina"),
    ("SK", "Srem (Stara Pazova)",   "Stara Pazova",          "Стара-Пазова",           "Стара Пазова",           "Vojvodina"),
    ("TO", "South Bačka (Titel)",   "Titel",                 "Титель",                 "Титель",                 "Vojvodina"),
    ("AB", "Moravica District",     "Moravica-Bezirk",       "Моравичкий округ",       "Моравицький округ",      "Sumadija"),
    ("RU", "Bor (Majdanpek)",       "Majdanpek",             "Майданпек",              "Майданпек",              "South"),
    ("BO", "Bor (Boljevac)",        "Boljevac",              "Бoljevac",               "Больєваць",              "South"),
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
    """Insert the RS country record and its translations.

    Args:
        conn: An open SQLite connection (foreign keys must be on).
    """
    country_id = _get_or_insert_country(conn)
    _insert_country_translations(conn, country_id)
    logger.info("Seeded country RS (id=%d)", country_id)


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
    okrug_key: str,
    coords: tuple[float, float] | None,
) -> None:
    """Insert one municipality/district and its translations."""
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
    group_trans = _OKRUG[okrug_key]
    _insert_region_translations(conn, row[0], name_trans, group_trans)


def seed_regions(conn: sqlite3.Connection) -> None:
    """Insert all RS district records and their translations.

    Args:
        conn: An open SQLite connection.
    """
    row = conn.execute("SELECT id FROM countries WHERE code = ?", (COUNTRY_CODE,)).fetchone()
    country_id: int = row[0]
    for plate_code, name_en, name_de, name_ru, name_uk, okrug_key in _REGION_ROWS:
        coords = _COORDS.get(plate_code.upper())
        _seed_single_region(
            conn, country_id, plate_code,
            name_en, name_de, name_ru, name_uk,
            okrug_key, coords,
        )
    logger.info("Seeded %d RS districts", len(_REGION_ROWS))


def run(conn: sqlite3.Connection) -> None:
    """Run the full Serbia seed: country + all districts.

    Args:
        conn: An open SQLite connection.
    """
    seed_country(conn)
    seed_regions(conn)


def main() -> None:
    """Open the production DB, seed Serbia, and close."""
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s — %(message)s")
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    try:
        run(conn)
        conn.commit()
        logger.info("Serbia seed complete")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
