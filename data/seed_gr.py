"""Seed Greece (GR) into the CarTags database.

Inserts the country record, its translations, and ~50 prefecture records
with full translations in en/de/ru/uk.  All inserts are idempotent
via INSERT OR IGNORE.

Usage::

    python data/seed_gr.py
"""

import logging
import sqlite3
from pathlib import Path

logger = logging.getLogger(__name__)

DB_PATH = Path(__file__).parent.parent / "db" / "cartags.db"

COUNTRY_CODE = "GR"
COUNTRY_EMOJI = "🇬🇷"
COUNTRY_SORT_ORDER = 13

_COUNTRY_TRANSLATIONS: dict[str, str] = {
    "en": "Greece",
    "de": "Griechenland",
    "ru": "Греция",
    "uk": "Греція",
}

_PERIPHEREIA: dict[str, dict[str, str]] = {
    "Attica": {
        "en": "Attica",
        "de": "Attika",
        "ru": "Аттика",
        "uk": "Аттика",
    },
    "Central Greece": {
        "en": "Central Greece",
        "de": "Mittelgriechenland",
        "ru": "Центральная Греция",
        "uk": "Центральна Греція",
    },
    "Central Macedonia": {
        "en": "Central Macedonia",
        "de": "Zentralmakedonien",
        "ru": "Центральная Македония",
        "uk": "Центральна Македонія",
    },
    "Crete": {
        "en": "Crete",
        "de": "Kreta",
        "ru": "Крит",
        "uk": "Крит",
    },
    "Eastern Macedonia and Thrace": {
        "en": "Eastern Macedonia and Thrace",
        "de": "Ostmakedonien und Thrakien",
        "ru": "Восточная Македония и Фракия",
        "uk": "Східна Македонія та Фракія",
    },
    "Epirus": {
        "en": "Epirus",
        "de": "Epirus",
        "ru": "Эпир",
        "uk": "Епір",
    },
    "Ionian Islands": {
        "en": "Ionian Islands",
        "de": "Ionische Inseln",
        "ru": "Ионические острова",
        "uk": "Іонічні острови",
    },
    "North Aegean": {
        "en": "North Aegean",
        "de": "Nördliche Ägäis",
        "ru": "Северные Эгейские острова",
        "uk": "Північні Егейські острови",
    },
    "Peloponnese": {
        "en": "Peloponnese",
        "de": "Peloponnes",
        "ru": "Пелопоннес",
        "uk": "Пелопоннес",
    },
    "South Aegean": {
        "en": "South Aegean",
        "de": "Südliche Ägäis",
        "ru": "Южные Эгейские острова",
        "uk": "Південні Егейські острови",
    },
    "Thessaly": {
        "en": "Thessaly",
        "de": "Thessalien",
        "ru": "Фессалия",
        "uk": "Фессалія",
    },
    "Western Greece": {
        "en": "Western Greece",
        "de": "Westgriechenland",
        "ru": "Западная Греция",
        "uk": "Західна Греція",
    },
    "Western Macedonia": {
        "en": "Western Macedonia",
        "de": "Westmakedonien",
        "ru": "Западная Македония",
        "uk": "Західна Македонія",
    },
}

_COORDS: dict[str, tuple[float, float]] = {
    "AAA": (37.9838, 23.7275),  # Athens
    "AAB": (37.9838, 23.7275),
    "AAC": (37.9838, 23.7275),
    "AAD": (37.9838, 23.7275),
    "AAE": (37.9838, 23.7275),
    "AAF": (37.9838, 23.7275),
    "ABB": (40.6401, 22.9444),  # Thessaloniki
    "ABC": (40.6401, 22.9444),
    "ABD": (40.6401, 22.9444),
    "ABE": (40.6401, 22.9444),
    "ABF": (40.6401, 22.9444),
    "AEA": (35.3387, 25.1442),  # Heraklion
    "AEB": (35.3387, 25.1442),
    "AEC": (35.5136, 24.0180),  # Rethymno
    "AED": (35.5136, 24.0180),
    "AEE": (35.1914, 25.7144),  # Agios Nikolaos
    "AGA": (41.1171, 25.4019),  # Kavala
    "AGB": (41.1171, 25.4019),
    "AGC": (41.0783, 25.3736),  # Xanthi
    "AGD": (41.1203, 25.4025),  # Komotini
    "AHH": (38.2500, 21.7347),  # Patras
    "AIA": (37.5658, 22.8096),  # Corinth
    "AIB": (37.0833, 22.4167),  # Sparta
    "AIC": (37.7667, 22.7167),  # Argos
    "AKA": (39.3667, 22.9500),  # Larissa
    "AKB": (39.3667, 22.9500),
    "AKK": (39.6500, 20.8500),  # Ioannina
    "ALA": (37.9333, 23.6833),  # Piraeus
    "ALB": (37.9333, 23.6833),
    "AMA": (40.5153, 21.3344),  # Kozani
    "AMB": (40.5153, 21.3344),
    "ANA": (38.3500, 26.1333),  # Chios
    "ANB": (37.9356, 23.9456),  # Salamina
    "AOA": (37.8833, 23.7500),  # Athens East
    "AOB": (37.8833, 23.7500),
    "APA": (38.6303, 21.4178),  # Agrinio
    "ARA": (39.6222, 21.6353),  # Trikala
    "ARB": (39.6222, 21.6353),
    "ATA": (38.9028, 22.4342),  # Lamia
    "ATB": (38.9028, 22.4342),
    "AXA": (37.0417, 25.1536),  # Ermoupoli (Syros)
    "AXB": (36.4500, 28.2167),  # Rhodes
    "AXC": (36.4500, 28.2167),
    "AYA": (39.6431, 19.9153),  # Corfu
    "AZA": (39.1650, 26.5544),  # Mytilene
    "AZB": (37.7594, 26.9769),  # Samos
    "BAA": (40.9361, 24.4008),  # Serres
    "BAB": (40.9361, 24.4008),
    "BBA": (40.8769, 22.2869),  # Veria
    "BBB": (40.8769, 22.2869),
    "BCA": (40.5361, 23.3125),  # Polygyros
    "BCB": (40.5361, 23.3125),
    "BEA": (39.3478, 22.9450),  # Volos
    "BEB": (39.3478, 22.9450),
    "BGA": (40.7222, 22.7167),  # Kilkis
    "BHA": (40.7611, 21.7736),  # Florina
    "BKA": (38.8667, 22.8833),  # Livadeia
    "BNA": (40.9181, 23.4706),  # Drama
}

# (plate_code, name_en, name_de, name_ru, name_uk, region_key)
_REGION_ROWS: list[tuple[str, str, str, str, str, str]] = [
    ("AAA", "Athens A",            "Athen A",              "Афины А",             "Афіни А",             "Attica"),
    ("AAB", "Athens B",            "Athen B",              "Афины Б",             "Афіни Б",             "Attica"),
    ("AAC", "Athens C",            "Athen C",              "Афины В",             "Афіни В",             "Attica"),
    ("AAD", "Athens D",            "Athen D",              "Афины Г",             "Афіни Г",             "Attica"),
    ("AAE", "Athens E",            "Athen E",              "Афины Д",             "Афіни Д",             "Attica"),
    ("AAF", "Athens F",            "Athen F",              "Афины Е",             "Афіни Е",             "Attica"),
    ("ABB", "Thessaloniki A",      "Thessaloniki A",       "Салоники А",          "Салоніки А",          "Central Macedonia"),
    ("ABC", "Thessaloniki B",      "Thessaloniki B",       "Салоники Б",          "Салоніки Б",          "Central Macedonia"),
    ("ABD", "Thessaloniki C",      "Thessaloniki C",       "Салоники В",          "Салоніки В",          "Central Macedonia"),
    ("ABE", "Thessaloniki D",      "Thessaloniki D",       "Салоники Г",          "Салоніки Г",          "Central Macedonia"),
    ("ABF", "Thessaloniki E",      "Thessaloniki E",       "Салоники Д",          "Салоніки Д",          "Central Macedonia"),
    ("AEA", "Heraklion",           "Heraklion",            "Ираклион",            "Іракліон",            "Crete"),
    ("AEB", "Heraklion B",         "Heraklion B",          "Ираклион Б",          "Іракліон Б",          "Crete"),
    ("AEC", "Rethymno",            "Rethymno",             "Ретимно",             "Ретимно",             "Crete"),
    ("AED", "Rethymno B",          "Rethymno B",           "Ретимно Б",           "Ретимно Б",           "Crete"),
    ("AEE", "Lasithi",             "Lassithi",             "Ласити",              "Ласіті",              "Crete"),
    ("AGA", "Kavala",              "Kavala",               "Кавала",              "Кавала",              "Eastern Macedonia and Thrace"),
    ("AGB", "Kavala B",            "Kavala B",             "Кавала Б",            "Кавала Б",            "Eastern Macedonia and Thrace"),
    ("AGC", "Xanthi",              "Xanthi",               "Ксанти",              "Ксанті",              "Eastern Macedonia and Thrace"),
    ("AGD", "Rodopi (Komotini)",   "Komotini",             "Комотини",            "Комотіні",            "Eastern Macedonia and Thrace"),
    ("AHH", "Achaea (Patras)",     "Patras",               "Патры",               "Патри",               "Western Greece"),
    ("AIA", "Corinthia",           "Korinth",              "Коринфия",            "Корінтія",            "Peloponnese"),
    ("AIB", "Laconia",             "Lakonien",             "Лакония",             "Лаконія",             "Peloponnese"),
    ("AIC", "Argolis",             "Argolis",              "Арголида",            "Арголіда",            "Peloponnese"),
    ("AKA", "Larissa",             "Larissa",              "Лариса",              "Лариса",              "Thessaly"),
    ("AKB", "Larissa B",           "Larissa B",            "Лариса Б",            "Лариса Б",            "Thessaly"),
    ("AKK", "Ioannina",            "Ioannina",             "Янина",               "Яніна",               "Epirus"),
    ("ALA", "Piraeus",             "Piräus",               "Пирей",               "Пірей",               "Attica"),
    ("ALB", "Piraeus B",           "Piräus B",             "Пирей Б",             "Пірей Б",             "Attica"),
    ("AMA", "Kozani",              "Kozani",               "Козани",              "Козані",              "Western Macedonia"),
    ("AMB", "Kozani B",            "Kozani B",             "Козани Б",            "Козані Б",            "Western Macedonia"),
    ("ANA", "Chios",               "Chios",                "Хиос",                "Хіос",                "North Aegean"),
    ("ANB", "Salamis",             "Salamis",              "Саламин",             "Саламін",             "Attica"),
    ("APA", "Aetolia-Acarnania",   "Aetolien-Akarnanien",  "Этолия-Акарнания",    "Етолія-Акарнанія",    "Western Greece"),
    ("ARA", "Trikala",             "Trikala",              "Трикала",             "Трікала",             "Thessaly"),
    ("ARB", "Trikala B",           "Trikala B",            "Трикала Б",           "Трікала Б",           "Thessaly"),
    ("ATA", "Phthiotis (Lamia)",   "Lamia",                "Ламия",               "Ламія",               "Central Greece"),
    ("ATB", "Phthiotis B",         "Lamia B",              "Ламия Б",             "Ламія Б",             "Central Greece"),
    ("AXA", "Cyclades (Syros)",    "Kykladen",             "Киклады",             "Кіклади",             "South Aegean"),
    ("AXB", "Dodecanese (Rhodes)", "Rhodos",               "Родос",               "Родос",               "South Aegean"),
    ("AXC", "Dodecanese B",        "Rhodos B",             "Родос Б",             "Родос Б",             "South Aegean"),
    ("AYA", "Corfu (Kerkyra)",     "Korfu",                "Корфу",               "Корфу",               "Ionian Islands"),
    ("AZA", "Lesbos (Mytilene)",   "Lesbos",               "Лесбос",              "Лесбос",              "North Aegean"),
    ("AZB", "Samos",               "Samos",                "Самос",               "Самос",               "North Aegean"),
    ("BAA", "Serres",              "Serres",               "Серес",               "Серес",               "Central Macedonia"),
    ("BAB", "Serres B",            "Serres B",             "Серес Б",             "Серес Б",             "Central Macedonia"),
    ("BBA", "Imathia (Veria)",     "Veria",                "Верия",               "Верія",               "Central Macedonia"),
    ("BBB", "Imathia B",           "Veria B",              "Верия Б",             "Верія Б",             "Central Macedonia"),
    ("BCA", "Chalkidiki",          "Chalkidiki",           "Халкидики",           "Халкідіки",           "Central Macedonia"),
    ("BEA", "Magnesia (Volos)",    "Volos",                "Волос",               "Волос",               "Thessaly"),
    ("BGA", "Kilkis",              "Kilkis",               "Килкис",              "Кілкіс",              "Central Macedonia"),
    ("BHA", "Florina",             "Florina",              "Флорина",             "Флоріна",             "Western Macedonia"),
    ("BKA", "Boeotia (Livadeia)", "Böotien",               "Беотия",              "Беотія",              "Central Greece"),
    ("BNA", "Drama",               "Drama",                "Драма",               "Драма",               "Eastern Macedonia and Thrace"),
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
    """Insert the GR country record and its translations.

    Args:
        conn: An open SQLite connection (foreign keys must be on).
    """
    country_id = _get_or_insert_country(conn)
    _insert_country_translations(conn, country_id)
    logger.info("Seeded country GR (id=%d)", country_id)


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
    """Insert one prefecture and its translations."""
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
    group_trans = _PERIPHEREIA[region_key]
    _insert_region_translations(conn, row[0], name_trans, group_trans)


def seed_regions(conn: sqlite3.Connection) -> None:
    """Insert all GR prefecture records and their translations.

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
    logger.info("Seeded %d GR prefectures", len(_REGION_ROWS))


def run(conn: sqlite3.Connection) -> None:
    """Run the full Greece seed: country + all prefectures.

    Args:
        conn: An open SQLite connection.
    """
    seed_country(conn)
    seed_regions(conn)


def main() -> None:
    """Open the production DB, seed Greece, and close."""
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s — %(message)s")
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    try:
        run(conn)
        conn.commit()
        logger.info("Greece seed complete")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
