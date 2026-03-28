"""Seed Ukraine (UA) into the CarTags database.

Inserts the country record, its translations, and all 53 region codes
with full translations in en/de/ru/uk.  All inserts are idempotent
via INSERT OR IGNORE.

Usage::

    python data/seed_ua.py
"""

import logging
import sqlite3
from pathlib import Path

logger = logging.getLogger(__name__)

DB_PATH = Path(__file__).parent.parent / "db" / "cartags.db"

COUNTRY_CODE = "UA"
COUNTRY_EMOJI = "🇺🇦"
COUNTRY_SORT_ORDER = 3

_COUNTRY_TRANSLATIONS: dict[str, str] = {
    "en": "Ukraine",
    "de": "Ukraine",
    "ru": "Украина",
    "uk": "Україна",
}

# (plate_code, name_en, name_de, name_ru, name_uk,
#              group_en, group_de, group_ru, group_uk)
_REGIONS: list[tuple[str, str, str, str, str, str, str, str, str]] = [
    # --- A-series ---
    ("AA", "Kyiv",             "Kiew",            "Киев",             "Київ",
           "Kyiv City",        "Stadt Kiew",       "Город Киев",       "Місто Київ"),
    ("AB", "Vinnytsia",        "Winnyzja",         "Винница",          "Вінниця",
           "Vinnytsia Oblast", "Oblast Winnyzja",  "Винницкая область","Вінницька область"),
    ("AC", "Lutsk",            "Luzk",             "Луцк",             "Луцьк",
           "Volyn Oblast",     "Oblast Wolyn",     "Волынская область","Волинська область"),
    ("AE", "Dnipro",           "Dnipro",           "Днепр",            "Дніпро",
           "Dnipropetrovsk Oblast", "Oblast Dnipropetrowsk",
           "Днепропетровская область", "Дніпропетровська область"),
    ("AH", "Donetsk",          "Donezk",           "Донецк",           "Донецьк",
           "Donetsk Oblast",   "Oblast Donezk",    "Донецкая область", "Донецька область"),
    ("AI", "Zhytomyr",         "Schytomyr",        "Житомир",          "Житомир",
           "Zhytomyr Oblast",  "Oblast Schytomyr", "Житомирская область","Житомирська область"),
    ("AK", "Uzhhorod",         "Uschhorod",        "Ужгород",          "Ужгород",
           "Zakarpattia Oblast","Oblast Transkarpatien",
           "Закарпатская область","Закарпатська область"),
    ("AM", "Zaporizhzhia",     "Saporischschja",   "Запорожье",        "Запоріжжя",
           "Zaporizhzhia Oblast","Oblast Saporischschja",
           "Запорожская область","Запорізька область"),
    ("AO", "Ivano-Frankivsk",  "Iwano-Frankiwsk",  "Ивано-Франковск",  "Івано-Франківськ",
           "Ivano-Frankivsk Oblast","Oblast Iwano-Frankiwsk",
           "Ивано-Франковская область","Івано-Франківська область"),
    ("AP", "Boryspil",         "Borispil",         "Борисполь",        "Бориспіль",
           "Kyiv Oblast",      "Oblast Kiew",      "Киевская область", "Київська область"),
    ("AT", "Kropyvnytskyi",    "Kropywnyzkyi",     "Кропивницкий",     "Кропивницький",
           "Kirovohrad Oblast","Oblast Kirowohrad","Кировоградская область","Кіровоградська область"),
    ("AX", "Kharkiv",          "Charkiw",          "Харьков",          "Харків",
           "Kharkiv Oblast",   "Oblast Charkiw",   "Харьковская область","Харківська область"),
    ("BA", "Luhansk",          "Luhansk",          "Луганск",          "Луганськ",
           "Luhansk Oblast",   "Oblast Luhansk",   "Луганская область","Луганська область"),
    ("BB", "Lviv",             "Lemberg",          "Львов",            "Львів",
           "Lviv Oblast",      "Oblast Lemberg",   "Львовская область","Львівська область"),
    ("BC", "Mykolaiv",         "Mykolajiw",        "Николаев",         "Миколаїв",
           "Mykolaiv Oblast",  "Oblast Mykolajiw", "Николаевская область","Миколаївська область"),
    ("BE", "Odessa",           "Odessa",           "Одесса",           "Одеса",
           "Odessa Oblast",    "Oblast Odessa",    "Одесская область", "Одеська область"),
    ("BH", "Poltava",          "Poltawa",          "Полтава",          "Полтава",
           "Poltava Oblast",   "Oblast Poltawa",   "Полтавская область","Полтавська область"),
    ("BI", "Rivne",            "Riwne",            "Ровно",            "Рівне",
           "Rivne Oblast",     "Oblast Riwne",     "Ровненская область","Рівненська область"),
    ("BK", "Sumy",             "Sumy",             "Сумы",             "Суми",
           "Sumy Oblast",      "Oblast Sumy",      "Сумская область",  "Сумська область"),
    ("BM", "Ternopil",         "Ternopil",         "Тернополь",        "Тернопіль",
           "Ternopil Oblast",  "Oblast Ternopil",  "Тернопольская область","Тернопільська область"),
    ("BO", "Kherson",          "Cherson",          "Херсон",           "Херсон",
           "Kherson Oblast",   "Oblast Cherson",   "Херсонская область","Херсонська область"),
    ("BP", "Khmelnytskyi",     "Chmelnyzkyj",      "Хмельницкий",      "Хмельницький",
           "Khmelnytskyi Oblast","Oblast Chmelnyzkyj",
           "Хмельницкая область","Хмельницька область"),
    ("BT", "Cherkasy",         "Tscherkassy",      "Черкассы",         "Черкаси",
           "Cherkasy Oblast",  "Oblast Tscherkassy","Черкасская область","Черкаська область"),
    ("CA", "Chernivtsi",       "Czernowitz",       "Черновцы",         "Чернівці",
           "Chernivtsi Oblast","Oblast Czernowitz","Черновицкая область","Чернівецька область"),
    ("CB", "Chernihiv",        "Tschernihiw",      "Чернигов",         "Чернігів",
           "Chernihiv Oblast", "Oblast Tschernihiw","Черниговская область","Чернігівська область"),
    ("CC", "Simferopol",       "Simferopol",       "Симферополь",      "Сімферополь",
           "Crimea",           "Krim",             "Крым",             "Крим"),
    ("CE", "Sevastopol",       "Sewastopol",       "Севастополь",      "Севастополь",
           "Sevastopol",       "Sewastopol",       "Севастополь",      "Севастополь"),
    # --- K-series (second series, same regions as A-series) ---
    ("KA", "Kyiv",             "Kiew",            "Киев",             "Київ",
           "Kyiv City",        "Stadt Kiew",       "Город Киев",       "Місто Київ"),
    ("KB", "Vinnytsia",        "Winnyzja",         "Винница",          "Вінниця",
           "Vinnytsia Oblast", "Oblast Winnyzja",  "Винницкая область","Вінницька область"),
    ("KC", "Lutsk",            "Luzk",             "Луцк",             "Луцьк",
           "Volyn Oblast",     "Oblast Wolyn",     "Волынская область","Волинська область"),
    ("KE", "Dnipro",           "Dnipro",           "Днепр",            "Дніпро",
           "Dnipropetrovsk Oblast", "Oblast Dnipropetrowsk",
           "Днепропетровская область", "Дніпропетровська область"),
    ("KH", "Donetsk",          "Donezk",           "Донецк",           "Донецьк",
           "Donetsk Oblast",   "Oblast Donezk",    "Донецкая область", "Донецька область"),
    ("KI", "Boryspil",         "Borispil",         "Борисполь",        "Бориспіль",
           "Kyiv Oblast",      "Oblast Kiew",      "Киевская область", "Київська область"),
    ("KM", "Zhytomyr",         "Schytomyr",        "Житомир",          "Житомир",
           "Zhytomyr Oblast",  "Oblast Schytomyr", "Житомирская область","Житомирська область"),
    ("KO", "Uzhhorod",         "Uschhorod",        "Ужгород",          "Ужгород",
           "Zakarpattia Oblast","Oblast Transkarpatien",
           "Закарпатская область","Закарпатська область"),
    ("KR", "Zaporizhzhia",     "Saporischschja",   "Запорожье",        "Запоріжжя",
           "Zaporizhzhia Oblast","Oblast Saporischschja",
           "Запорожская область","Запорізька область"),
    ("KT", "Ivano-Frankivsk",  "Iwano-Frankiwsk",  "Ивано-Франковск",  "Івано-Франківськ",
           "Ivano-Frankivsk Oblast","Oblast Iwano-Frankiwsk",
           "Ивано-Франковская область","Івано-Франківська область"),
    ("KX", "Kharkiv",          "Charkiw",          "Харьков",          "Харків",
           "Kharkiv Oblast",   "Oblast Charkiw",   "Харьковская область","Харківська область"),
    ("NA", "Luhansk",          "Luhansk",          "Луганск",          "Луганськ",
           "Luhansk Oblast",   "Oblast Luhansk",   "Луганская область","Луганська область"),
    ("NV", "Lviv",             "Lemberg",          "Львов",            "Львів",
           "Lviv Oblast",      "Oblast Lemberg",   "Львовская область","Львівська область"),
    ("NE", "Mykolaiv",         "Mykolajiw",        "Николаев",         "Миколаїв",
           "Mykolaiv Oblast",  "Oblast Mykolajiw", "Николаевская область","Миколаївська область"),
    ("NN", "Odessa",           "Odessa",           "Одесса",           "Одеса",
           "Odessa Oblast",    "Oblast Odessa",    "Одесская область", "Одеська область"),
    ("NK", "Rivne",            "Riwne",            "Ровно",            "Рівне",
           "Rivne Oblast",     "Oblast Riwne",     "Ровненская область","Рівненська область"),
    ("NM", "Sumy",             "Sumy",             "Сумы",             "Суми",
           "Sumy Oblast",      "Oblast Sumy",      "Сумская область",  "Сумська область"),
    ("NO", "Ternopil",         "Ternopil",         "Тернополь",        "Тернопіль",
           "Ternopil Oblast",  "Oblast Ternopil",  "Тернопольская область","Тернопільська область"),
    ("NR", "Kherson",          "Cherson",          "Херсон",           "Херсон",
           "Kherson Oblast",   "Oblast Cherson",   "Херсонская область","Херсонська область"),
    ("NT", "Khmelnytskyi",     "Chmelnyzkyj",      "Хмельницкий",      "Хмельницький",
           "Khmelnytskyi Oblast","Oblast Chmelnyzkyj",
           "Хмельницкая область","Хмельницька область"),
    ("NH", "Cherkasy",         "Tscherkassy",      "Черкассы",         "Черкаси",
           "Cherkasy Oblast",  "Oblast Tscherkassy","Черкасская область","Черкаська область"),
    ("NU", "Chernivtsi",       "Czernowitz",       "Черновцы",         "Чернівці",
           "Chernivtsi Oblast","Oblast Czernowitz","Черновицкая область","Чернівецька область"),
    ("NX", "Chernihiv",        "Tschernihiw",      "Чернигов",         "Чернігів",
           "Chernihiv Oblast", "Oblast Tschernihiw","Черниговская область","Чернігівська область"),
    ("UK", "Simferopol",       "Simferopol",       "Симферополь",      "Сімферополь",
           "Crimea",           "Krim",             "Крым",             "Крим"),
    ("SN", "Sevastopol",       "Sewastopol",       "Севастополь",      "Севастополь",
           "Sevastopol",       "Sewastopol",       "Севастополь",      "Севастополь"),
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
    """Insert the UA country record and its translations.

    Args:
        conn: An open SQLite connection (foreign keys must be on).
    """
    country_id = _get_or_insert_country(conn)
    _insert_country_translations(conn, country_id)
    logger.info("Seeded country UA (id=%d)", country_id)


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
    row: tuple[str, str, str, str, str, str, str, str, str],
) -> None:
    """Insert one region and its 8 translations (4 name + 4 region_group)."""
    plate_code, n_en, n_de, n_ru, n_uk, g_en, g_de, g_ru, g_uk = row
    conn.execute(
        "INSERT OR IGNORE INTO regions (country_id, plate_code) VALUES (?, ?)",
        (country_id, plate_code.upper()),
    )
    result = conn.execute(
        "SELECT id FROM regions WHERE country_id = ? AND plate_code = ?",
        (country_id, plate_code.upper()),
    ).fetchone()
    name_trans = {"en": n_en, "de": n_de, "ru": n_ru, "uk": n_uk}
    group_trans = {"en": g_en, "de": g_de, "ru": g_ru, "uk": g_uk}
    _insert_region_translations(conn, result[0], name_trans, group_trans)


def seed_regions(conn: sqlite3.Connection) -> None:
    """Insert all UA region records and their translations.

    Args:
        conn: An open SQLite connection.
    """
    result = conn.execute("SELECT id FROM countries WHERE code = ?", (COUNTRY_CODE,)).fetchone()
    country_id: int = result[0]
    for region_row in _REGIONS:
        _seed_single_region(conn, country_id, region_row)
    logger.info("Seeded %d UA regions", len(_REGIONS))


def run(conn: sqlite3.Connection) -> None:
    """Run the full Ukraine seed: country + all regions.

    Args:
        conn: An open SQLite connection.
    """
    seed_country(conn)
    seed_regions(conn)


def main() -> None:
    """Open the production DB, seed Ukraine, and close."""
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s — %(message)s")
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    try:
        run(conn)
        conn.commit()
        logger.info("Ukraine seed complete")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
