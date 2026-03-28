"""Seed Croatia (HR) into the CarTags database.

Inserts the country record, its translations, and 21 county records
with full translations in en/de/ru/uk.  All inserts are idempotent
via INSERT OR IGNORE.

Usage::

    python data/seed_hr.py
"""

import logging
import sqlite3
from pathlib import Path

logger = logging.getLogger(__name__)

DB_PATH = Path(__file__).parent.parent / "db" / "cartags.db"

COUNTRY_CODE = "HR"
COUNTRY_EMOJI = "🇭🇷"
COUNTRY_SORT_ORDER = 8

_COUNTRY_TRANSLATIONS: dict[str, str] = {
    "en": "Croatia",
    "de": "Kroatien",
    "ru": "Хорватия",
    "uk": "Хорватія",
}

_CROATIA = {
    "en": "Croatia",
    "de": "Kroatien",
    "ru": "Хорватия",
    "uk": "Хорватія",
}

_COORDS: dict[str, tuple[float, float]] = {
    "ZG": (45.8150, 15.9819),  # Zagreb
    "ZGZ": (45.8150, 15.9819),
    "ST": (43.5081, 16.4402),  # Split
    "RI": (45.3271, 14.4422),  # Rijeka
    "OS": (45.5550, 18.6950),  # Osijek
    "VK": (46.3067, 16.3356),  # Varaždin
    "SB": (45.6564, 17.0093),  # Slavonski Brod
    "KA": (45.4839, 14.5508),  # Karlovac
    "KK": (45.9958, 16.1347),  # Koprivnica
    "BJ": (45.9000, 17.1500),  # Bjelovar
    "VU": (45.3511, 17.3972),  # Vukovar
    "PU": (44.8683, 13.8481),  # Pula
    "SK": (46.0044, 15.5697),  # Krapina
    "ZD": (44.1194, 15.2314),  # Zadar
    "SI": (44.5611, 16.3783),  # Šibenik
    "GS": (45.5553, 15.3736),  # Sisak
    "MK": (45.8283, 18.4078),  # Vinkovci
    "DA": (46.5053, 16.3822),  # Čakovec
    "NE": (44.0406, 15.5428),  # Gospić
    "PZ": (45.1956, 14.6706),  # Pazin
    "KR": (45.8000, 15.5833),  # Križevci
}

# (plate_code, name_en, name_de, name_ru, name_uk)
_REGION_ROWS: list[tuple[str, str, str, str, str]] = [
    ("ZG",  "Zagreb City",                 "Zagreb (Stadt)",              "Загреб (город)",              "Загреб (місто)"),
    ("ZGZ", "Zagreb County",               "Zagreb (Gespanschaft)",       "Загребская жупания",          "Загребська жупанія"),
    ("ST",  "Split-Dalmatia County",       "Gespanschaft Split-Dalmatien","Сплитско-Далматинская жупания","Спліт-Далматинська жупанія"),
    ("RI",  "Primorje-Gorski Kotar",       "Gespanschaft Primorje-Gorski Kotar","Приморско-Горанская жупания","Приморсько-Горанська жупанія"),
    ("OS",  "Osijek-Baranja County",       "Gespanschaft Osijek-Baranja", "Осиечко-Бараньская жупания",  "Осієцько-Бараньська жупанія"),
    ("VK",  "Varaždin County",             "Gespanschaft Varaždin",       "Вараждинская жупания",        "Вараждинська жупанія"),
    ("SB",  "Brod-Posavina County",        "Gespanschaft Brod-Posavina",  "Бродско-Посавская жупания",   "Бродсько-Посавська жупанія"),
    ("KA",  "Karlovac County",             "Gespanschaft Karlstadt",      "Карловацкая жупания",         "Карловацька жупанія"),
    ("KK",  "Koprivnica-Križevci County",  "Gespanschaft Koprivnica-Križevci","Копривничко-Крижевачская жупания","Копривничко-Крижевачська жупанія"),
    ("BJ",  "Bjelovar-Bilogora County",    "Gespanschaft Bjelovar-Bilogora","Бьеловарско-Билогорская жупания","Бьєловарсько-Білогорська жупанія"),
    ("VU",  "Vukovar-Srijem County",       "Gespanschaft Vukovar-Syrmien","Вуковарско-Сримская жупания", "Вуковарсько-Сримська жупанія"),
    ("PU",  "Istria County",               "Gespanschaft Istrien",        "Истрийская жупания",          "Істрійська жупанія"),
    ("SK",  "Krapina-Zagorje County",      "Gespanschaft Krapina-Zagorje","Крапинско-Загорская жупания", "Крапінсько-Загорська жупанія"),
    ("ZD",  "Zadar County",                "Gespanschaft Zadar",          "Задарская жупания",           "Задарська жупанія"),
    ("SI",  "Šibenik-Knin County",         "Gespanschaft Šibenik-Knin",   "Шибеничко-Книнская жупания",  "Шибеницько-Книнська жупанія"),
    ("GS",  "Sisak-Moslavina County",      "Gespanschaft Sisak-Moslavina","Сисачко-Мославинская жупания","Сисачко-Мославинська жупанія"),
    ("MK",  "Vukovar-Srijem (Vinkovci)",   "Vinkovci",                    "Винковцы",                    "Винківці"),
    ("DA",  "Međimurje County",            "Gespanschaft Međimurje",      "Меджимурская жупания",        "Меджімурська жупанія"),
    ("NE",  "Lika-Senj County",            "Gespanschaft Lika-Senj",      "Личко-Сеньская жупания",      "Лицько-Сеньська жупанія"),
    ("PZ",  "Pazin (Istria)",              "Pazin (Istrien)",             "Пазин",                       "Пазін"),
    ("KR",  "Koprivnica-Križevci (alt)",   "Koprivnica-Križevci",         "Крижевцы",                    "Крижевці"),
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
    """Insert the HR country record and its translations.

    Args:
        conn: An open SQLite connection (foreign keys must be on).
    """
    country_id = _get_or_insert_country(conn)
    _insert_country_translations(conn, country_id)
    logger.info("Seeded country HR (id=%d)", country_id)


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
    _insert_region_translations(conn, row[0], name_trans, _CROATIA)


def seed_regions(conn: sqlite3.Connection) -> None:
    """Insert all HR county records and their translations.

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
    logger.info("Seeded %d HR counties", len(_REGION_ROWS))


def run(conn: sqlite3.Connection) -> None:
    """Run the full Croatia seed: country + all counties.

    Args:
        conn: An open SQLite connection.
    """
    seed_country(conn)
    seed_regions(conn)


def main() -> None:
    """Open the production DB, seed Croatia, and close."""
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s — %(message)s")
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    try:
        run(conn)
        conn.commit()
        logger.info("Croatia seed complete")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
