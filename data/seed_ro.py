"""Seed Romania (RO) into the CarTags database.

Inserts the country record, its translations, and 42 județ records
with full translations in en/de/ru/uk.  All inserts are idempotent
via INSERT OR IGNORE.

Usage::

    python data/seed_ro.py
"""

import logging
import sqlite3
from pathlib import Path

logger = logging.getLogger(__name__)

DB_PATH = Path(__file__).parent.parent / "db" / "cartags.db"

COUNTRY_CODE = "RO"
COUNTRY_EMOJI = "🇷🇴"
COUNTRY_SORT_ORDER = 6

_COUNTRY_TRANSLATIONS: dict[str, str] = {
    "en": "Romania",
    "de": "Rumänien",
    "ru": "Румыния",
    "uk": "Румунія",
}

_REGION: dict[str, dict[str, str]] = {
    "Nord-Vest": {
        "en": "North-West Region",
        "de": "Nordwestregion",
        "ru": "Северо-Западный регион",
        "uk": "Північно-Західний регіон",
    },
    "Centru": {
        "en": "Centre Region",
        "de": "Zentralregion",
        "ru": "Центральный регион",
        "uk": "Центральний регіон",
    },
    "Nord-Est": {
        "en": "North-East Region",
        "de": "Nordostregion",
        "ru": "Северо-Восточный регион",
        "uk": "Північно-Східний регіон",
    },
    "Sud-Est": {
        "en": "South-East Region",
        "de": "Südostregion",
        "ru": "Юго-Восточный регион",
        "uk": "Південно-Східний регіон",
    },
    "Sud": {
        "en": "South Region",
        "de": "Südregion",
        "ru": "Южный регион",
        "uk": "Південний регіон",
    },
    "Bucuresti-Ilfov": {
        "en": "Bucharest–Ilfov Region",
        "de": "Bukarest-Ilfov-Region",
        "ru": "Бухарест-Илфов",
        "uk": "Бухарест-Ілфов",
    },
    "Sud-Vest": {
        "en": "South-West Oltenia Region",
        "de": "Südwest-Oltenien-Region",
        "ru": "Юго-Западная Олтения",
        "uk": "Південно-Західна Олтенія",
    },
    "Vest": {
        "en": "West Region",
        "de": "Westregion",
        "ru": "Западный регион",
        "uk": "Західний регіон",
    },
}

_COORDS: dict[str, tuple[float, float]] = {
    "B":  (44.4268, 26.1025),  # Bucharest
    "AB": (46.0769, 23.5800),  # Alba Iulia
    "AR": (46.1766, 21.3226),  # Arad
    "AG": (44.8565, 24.8697),  # Pitești
    "BC": (46.5670, 26.9146),  # Bacău
    "BH": (47.0722, 21.9217),  # Oradea
    "BN": (47.1327, 24.4960),  # Bistrița
    "BT": (47.7500, 26.6667),  # Botoșani
    "BV": (45.6427, 25.5887),  # Brașov
    "BR": (45.2692, 27.9574),  # Brăila
    "BZ": (45.1500, 26.8167),  # Buzău
    "CS": (45.2985, 21.8996),  # Reșița
    "CL": (44.2000, 27.3333),  # Călărași
    "CJ": (46.7712, 23.6236),  # Cluj-Napoca
    "CT": (44.1598, 28.6348),  # Constanța
    "CV": (45.8716, 25.7869),  # Sfântu Gheorghe
    "DB": (44.9345, 25.4575),  # Târgoviște
    "DJ": (44.3302, 23.7949),  # Craiova
    "GL": (45.4353, 28.0498),  # Galați
    "GR": (43.9017, 25.9669),  # Giurgiu
    "GJ": (44.9199, 23.3342),  # Târgu Jiu
    "HR": (46.3528, 25.8019),  # Miercurea Ciuc
    "HD": (45.8667, 22.9167),  # Deva
    "IL": (44.3617, 27.6472),  # Slobozia
    "IS": (47.1585, 27.6014),  # Iași
    "IF": (44.4268, 26.1025),  # Ilfov (near Bucharest)
    "MM": (47.6591, 23.5700),  # Baia Mare
    "MH": (44.6167, 22.6667),  # Drobeta-Turnu Severin
    "MS": (46.5412, 24.5578),  # Târgu Mureș
    "NT": (46.9752, 26.3835),  # Piatra Neamț
    "OT": (44.1167, 24.3667),  # Slatina
    "PH": (44.9364, 26.0228),  # Ploiești
    "SM": (47.7970, 22.8852),  # Satu Mare
    "SJ": (47.1833, 23.0667),  # Zalău
    "SB": (45.7983, 24.1256),  # Sibiu
    "SV": (47.6514, 26.2556),  # Suceava
    "TR": (43.8967, 25.3097),  # Alexandria
    "TM": (45.7489, 21.2087),  # Timișoara
    "TL": (45.1781, 28.8025),  # Tulcea
    "VS": (46.6403, 27.7284),  # Vaslui
    "VL": (45.1000, 24.3667),  # Râmnicu Vâlcea
    "VN": (45.7000, 27.0667),  # Focșani
}

# (plate_code, name_en, name_de, name_ru, name_uk, region_key)
_REGION_ROWS: list[tuple[str, str, str, str, str, str]] = [
    ("B",  "Bucharest",            "Bukarest",              "Бухарест",               "Бухарест",               "Bucuresti-Ilfov"),
    ("AB", "Alba",                  "Alba",                   "Алба",                   "Алба",                   "Centru"),
    ("AR", "Arad",                  "Arad",                   "Арад",                   "Арад",                   "Vest"),
    ("AG", "Argeș",                 "Argeș",                  "Арджеш",                 "Арджеш",                 "Sud"),
    ("BC", "Bacău",                 "Bacău",                  "Бакэу",                  "Бакеу",                  "Nord-Est"),
    ("BH", "Bihor",                 "Bihor",                  "Бихор",                  "Бігор",                  "Nord-Vest"),
    ("BN", "Bistrița-Năsăud",       "Bistritz-Nassod",        "Бистрица-Нэсэуд",        "Бистриця-Несеуд",        "Nord-Vest"),
    ("BT", "Botoșani",              "Botoschani",             "Ботошань",               "Ботошань",               "Nord-Est"),
    ("BV", "Brașov",                "Kronstadt",              "Брашов",                 "Брашов",                 "Centru"),
    ("BR", "Brăila",                "Brăila",                 "Брэила",                 "Брэіла",                 "Sud-Est"),
    ("BZ", "Buzău",                 "Buzau",                  "Бузэу",                  "Бузеу",                  "Sud-Est"),
    ("CS", "Caraș-Severin",         "Karasch-Severin",        "Кэраш-Северин",          "Кераш-Северин",          "Vest"),
    ("CL", "Călărași",              "Călărași",               "Кэлэраши",               "Келерашь",               "Sud"),
    ("CJ", "Cluj",                  "Klausenburg",            "Клуж",                   "Клуж",                   "Nord-Vest"),
    ("CT", "Constanța",             "Konstanza",              "Констанца",              "Констанца",              "Sud-Est"),
    ("CV", "Covasna",               "Covasna",                "Ковасна",                "Ковасна",                "Centru"),
    ("DB", "Dâmbovița",             "Dâmbovița",              "Дымбовица",              "Димбовіца",              "Sud"),
    ("DJ", "Dolj",                  "Dolj",                   "Долж",                   "Долж",                   "Sud-Vest"),
    ("GL", "Galați",                "Galatz",                 "Галац",                  "Галац",                  "Sud-Est"),
    ("GR", "Giurgiu",               "Giurgiu",                "Джурджу",                "Джурджу",                "Sud"),
    ("GJ", "Gorj",                  "Gorj",                   "Горж",                   "Горж",                   "Sud-Vest"),
    ("HR", "Harghita",              "Harghita",               "Харгита",                "Гаргіта",                "Centru"),
    ("HD", "Hunedoara",             "Eisenmarkt",             "Хунедоара",              "Гунедоара",              "Vest"),
    ("IL", "Ialomița",              "Ialomița",               "Яломица",                "Яломіца",                "Sud-Est"),
    ("IS", "Iași",                  "Jassy",                  "Яссы",                   "Ясси",                   "Nord-Est"),
    ("IF", "Ilfov",                 "Ilfov",                  "Илфов",                  "Ілфов",                  "Bucuresti-Ilfov"),
    ("MM", "Maramureș",             "Maramuresch",            "Марамуреш",              "Марамуреш",              "Nord-Vest"),
    ("MH", "Mehedinți",             "Mehedinți",              "Мехединц",               "Мехединц",               "Sud-Vest"),
    ("MS", "Mureș",                 "Mieresch",               "Муреш",                  "Муреш",                  "Centru"),
    ("NT", "Neamț",                 "Neamț",                  "Нямц",                   "Нямц",                   "Nord-Est"),
    ("OT", "Olt",                   "Olt",                    "Олт",                    "Олт",                    "Sud-Vest"),
    ("PH", "Prahova",               "Prahova",                "Прахова",                "Прахова",                "Sud"),
    ("SM", "Satu Mare",             "Sathmar",                "Сату-Маре",              "Сату-Маре",              "Nord-Vest"),
    ("SJ", "Sălaj",                 "Sälaj",                  "Сэлаж",                  "Сележ",                  "Nord-Vest"),
    ("SB", "Sibiu",                 "Hermannstadt",           "Сибиу",                  "Сібіу",                  "Centru"),
    ("SV", "Suceava",               "Suczawa",                "Сучава",                 "Сучава",                 "Nord-Est"),
    ("TR", "Teleorman",             "Teleorman",              "Телеорман",              "Телеорман",              "Sud"),
    ("TM", "Timiș",                 "Temesch",                "Тимиш",                  "Тіміш",                  "Vest"),
    ("TL", "Tulcea",                "Tultscha",               "Тулча",                  "Тулча",                  "Sud-Est"),
    ("VS", "Vaslui",                "Waslui",                 "Васлуй",                 "Васлуй",                 "Nord-Est"),
    ("VL", "Vâlcea",                "Walzei",                 "Вылча",                  "Валча",                  "Sud-Vest"),
    ("VN", "Vrancea",               "Wrantscha",              "Вранча",                 "Вранча",                 "Sud-Est"),
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
    """Insert the RO country record and its translations.

    Args:
        conn: An open SQLite connection (foreign keys must be on).
    """
    country_id = _get_or_insert_country(conn)
    _insert_country_translations(conn, country_id)
    logger.info("Seeded country RO (id=%d)", country_id)


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
    """Insert one județ and its translations."""
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
    """Insert all RO județ records and their translations.

    Args:
        conn: An open SQLite connection.
    """
    row = conn.execute("SELECT id FROM countries WHERE code = ?", (COUNTRY_CODE,)).fetchone()
    country_id: int = row[0]
    for plate_code, name_en, name_de, name_ru, name_uk, region_key in _REGION_ROWS:
        coords = _COORDS.get(plate_code.upper())
        _seed_single_region(
            conn, country_id, plate_code,
            name_en, name_de, name_ru, name_uk,
            region_key, coords,
        )
    logger.info("Seeded %d RO județe", len(_REGION_ROWS))


def run(conn: sqlite3.Connection) -> None:
    """Run the full Romania seed: country + all județe.

    Args:
        conn: An open SQLite connection.
    """
    seed_country(conn)
    seed_regions(conn)


def main() -> None:
    """Open the production DB, seed Romania, and close."""
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s — %(message)s")
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    try:
        run(conn)
        conn.commit()
        logger.info("Romania seed complete")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
