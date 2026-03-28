"""Seed Turkey (TR) into the CarTags database.

Inserts the country record, its translations, and 81 province records
with full translations in en/de/ru/uk.  Plate codes are stored as strings
(e.g. "01", "34").  All inserts are idempotent via INSERT OR IGNORE.

Usage::

    python data/seed_tr.py
"""

import logging
import sqlite3
from pathlib import Path

logger = logging.getLogger(__name__)

DB_PATH = Path(__file__).parent.parent / "db" / "cartags.db"

COUNTRY_CODE = "TR"
COUNTRY_EMOJI = "🇹🇷"
COUNTRY_SORT_ORDER = 17

_COUNTRY_TRANSLATIONS: dict[str, str] = {
    "en": "Turkey",
    "de": "Türkei",
    "ru": "Турция",
    "uk": "Туреччина",
}

_BOLGE: dict[str, dict[str, str]] = {
    "Marmara": {
        "en": "Marmara Region",
        "de": "Marmararegion",
        "ru": "Мраморноморский регион",
        "uk": "Мармурноморський регіон",
    },
    "Aegean": {
        "en": "Aegean Region",
        "de": "Ägäische Region",
        "ru": "Эгейский регион",
        "uk": "Егейський регіон",
    },
    "Mediterranean": {
        "en": "Mediterranean Region",
        "de": "Mittelmeerregion",
        "ru": "Средиземноморский регион",
        "uk": "Середземноморський регіон",
    },
    "Central Anatolia": {
        "en": "Central Anatolia Region",
        "de": "Zentralanatolien-Region",
        "ru": "Центральноанатолийский регион",
        "uk": "Центральноанатолійський регіон",
    },
    "Black Sea": {
        "en": "Black Sea Region",
        "de": "Schwarzmeerregion",
        "ru": "Черноморский регион",
        "uk": "Чорноморський регіон",
    },
    "Eastern Anatolia": {
        "en": "Eastern Anatolia Region",
        "de": "Ostanatolien-Region",
        "ru": "Восточноанатолийский регион",
        "uk": "Східноанатолійський регіон",
    },
    "Southeastern Anatolia": {
        "en": "Southeastern Anatolia Region",
        "de": "Südostanatolien-Region",
        "ru": "Юго-Восточная Анатолия",
        "uk": "Південно-Східна Анатолія",
    },
}

_COORDS: dict[str, tuple[float, float]] = {
    "01": (37.0000, 35.3213),  # Adana
    "02": (37.7648, 38.2786),  # Adıyaman
    "03": (38.7567, 30.5328),  # Afyonkarahisar
    "04": (39.7191, 43.0503),  # Ağrı
    "05": (40.5500, 35.1500),  # Amasya
    "06": (39.9208, 32.8541),  # Ankara
    "07": (36.8969, 30.7133),  # Antalya
    "08": (41.1872, 41.8183),  # Artvin
    "09": (37.8560, 27.8416),  # Aydın
    "10": (39.6484, 27.8826),  # Balıkesir
    "11": (40.1500, 31.6000),  # Bilecik
    "12": (38.3552, 41.1344),  # Bingöl
    "13": (38.3951, 42.1235),  # Bitlis
    "14": (40.7369, 31.6061),  # Bolu
    "15": (37.7176, 30.2986),  # Burdur
    "16": (40.1828, 29.0665),  # Bursa
    "17": (40.1553, 26.4142),  # Çanakkale
    "18": (40.6013, 33.6134),  # Çankırı
    "19": (40.5503, 34.9556),  # Çorum
    "20": (37.7726, 29.0863),  # Denizli
    "21": (37.9100, 40.2306),  # Diyarbakır
    "22": (41.6781, 26.5597),  # Edirne
    "23": (38.6748, 39.2225),  # Elazığ
    "24": (39.9207, 41.2752),  # Erzincan
    "25": (39.9000, 41.2700),  # Erzurum
    "26": (39.7767, 30.5206),  # Eskişehir
    "27": (37.0662, 37.3833),  # Gaziantep
    "28": (40.9167, 38.3833),  # Giresun
    "29": (40.4607, 38.2936),  # Gümüşhane
    "30": (37.5744, 42.7312),  # Hakkari
    "31": (36.5031, 36.1720),  # Hatay
    "32": (37.7615, 30.5553),  # Isparta
    "33": (36.8000, 34.6333),  # Mersin
    "34": (41.0082, 28.9784),  # Istanbul
    "35": (38.4189, 27.1287),  # İzmir
    "36": (42.1479, 43.0974),  # Kars
    "37": (41.2887, 36.3328),  # Kastamonu
    "38": (38.7312, 35.4787),  # Kayseri
    "39": (41.7333, 27.0833),  # Kırklareli
    "40": (39.1472, 34.1605),  # Kırşehir
    "41": (40.7626, 29.9042),  # Kocaeli
    "42": (37.8667, 32.4833),  # Konya
    "43": (43.3743, 29.0200),  # Kütahya
    "44": (38.3552, 38.3095),  # Malatya
    "45": (38.6191, 27.4289),  # Manisa
    "46": (37.5858, 36.9371),  # Kahramanmaraş
    "47": (37.3212, 40.7245),  # Mardin
    "48": (37.2153, 28.3636),  # Muğla
    "49": (38.6744, 41.5061),  # Muş
    "50": (38.6237, 34.7240),  # Nevşehir
    "51": (37.9752, 34.6789),  # Niğde
    "52": (41.0053, 36.5095),  # Ordu
    "53": (41.0208, 40.5230),  # Rize
    "54": (40.7731, 30.3947),  # Sakarya
    "55": (41.2867, 36.3300),  # Samsun
    "56": (37.9280, 41.9419),  # Siirt
    "57": (41.8628, 34.8801),  # Sinop
    "58": (39.7477, 37.0179),  # Sivas
    "59": (41.5479, 27.5239),  # Tekirdağ
    "60": (40.3167, 36.5667),  # Tokat
    "61": (40.9833, 39.7333),  # Trabzon
    "62": (39.4333, 38.2833),  # Tunceli
    "63": (37.1674, 38.7955),  # Şanlıurfa
    "64": (38.6784, 29.4082),  # Uşak
    "65": (38.4895, 43.4089),  # Van
    "66": (39.8167, 34.8000),  # Yozgat
    "67": (41.4564, 31.7987),  # Zonguldak
    "68": (38.7186, 35.6003),  # Aksaray
    "69": (40.5833, 41.5333),  # Bayburt
    "70": (37.1817, 33.2153),  # Karaman
    "71": (39.8472, 33.5154),  # Kırıkkale
    "72": (37.4324, 41.1308),  # Batman
    "73": (37.5144, 42.4429),  # Şırnak
    "74": (41.7611, 32.5628),  # Bartın
    "75": (38.9667, 42.1167),  # Ardahan
    "76": (39.7167, 44.0333),  # Iğdır
    "77": (40.6500, 30.3667),  # Yalova
    "78": (41.1333, 43.0833),  # Karabük
    "79": (36.9011, 36.0883),  # Kilis
    "80": (37.0744, 35.9936),  # Osmaniye
    "81": (41.0017, 31.1614),  # Düzce
}

# (plate_code, name_en, name_de, name_ru, name_uk, region_key)
_REGION_ROWS: list[tuple[str, str, str, str, str, str]] = [
    ("01", "Adana",           "Adana",           "Адана",           "Адана",           "Mediterranean"),
    ("02", "Adıyaman",        "Adıyaman",        "Адыяман",         "Адиямань",        "Southeastern Anatolia"),
    ("03", "Afyonkarahisar",  "Afyonkarahisar",  "Афьонкарахисар",  "Афьонкарагісар",  "Aegean"),
    ("04", "Ağrı",            "Ağrı",            "Агры",            "Агри",            "Eastern Anatolia"),
    ("05", "Amasya",          "Amasya",          "Амасья",          "Амасья",          "Black Sea"),
    ("06", "Ankara",          "Ankara",          "Анкара",          "Анкара",          "Central Anatolia"),
    ("07", "Antalya",         "Antalya",         "Анталья",         "Анталья",         "Mediterranean"),
    ("08", "Artvin",          "Artvin",          "Артвин",          "Артвін",          "Black Sea"),
    ("09", "Aydın",           "Aydın",           "Айдын",           "Айдин",           "Aegean"),
    ("10", "Balıkesir",       "Balıkesir",       "Балыкесир",       "Балікесір",       "Marmara"),
    ("11", "Bilecik",         "Bilecik",         "Биледжик",        "Біледжик",        "Marmara"),
    ("12", "Bingöl",          "Bingöl",          "Бингёль",         "Бінгель",         "Eastern Anatolia"),
    ("13", "Bitlis",          "Bitlis",          "Битлис",          "Бітліс",          "Eastern Anatolia"),
    ("14", "Bolu",            "Bolu",            "Болу",            "Болу",            "Black Sea"),
    ("15", "Burdur",          "Burdur",          "Бурдур",          "Бурдур",          "Mediterranean"),
    ("16", "Bursa",           "Bursa",           "Бурса",           "Бурса",           "Marmara"),
    ("17", "Çanakkale",       "Çanakkale",       "Чанаккале",       "Чанаккале",       "Marmara"),
    ("18", "Çankırı",         "Çankırı",         "Чанкыры",         "Чанкири",         "Black Sea"),
    ("19", "Çorum",           "Çorum",           "Чорум",           "Чорум",           "Black Sea"),
    ("20", "Denizli",         "Denizli",         "Денизли",         "Денізлі",         "Aegean"),
    ("21", "Diyarbakır",      "Diyarbakır",      "Диярбакыр",       "Діярбакир",       "Southeastern Anatolia"),
    ("22", "Edirne",          "Edirne",          "Эдирне",          "Едірне",          "Marmara"),
    ("23", "Elazığ",          "Elazığ",          "Элязыг",          "Елязиг",          "Eastern Anatolia"),
    ("24", "Erzincan",        "Erzincan",        "Эрзинджан",       "Ерзінджан",       "Eastern Anatolia"),
    ("25", "Erzurum",         "Erzurum",         "Эрзурум",         "Ерзурум",         "Eastern Anatolia"),
    ("26", "Eskişehir",       "Eskişehir",       "Эскишехир",       "Ескішегір",       "Central Anatolia"),
    ("27", "Gaziantep",       "Gaziantep",       "Газиантеп",       "Ґазіантеп",       "Southeastern Anatolia"),
    ("28", "Giresun",         "Giresun",         "Гиресун",         "Ґіресун",         "Black Sea"),
    ("29", "Gümüşhane",       "Gümüşhane",       "Гюмюшхане",       "Ґюмюшхане",       "Black Sea"),
    ("30", "Hakkari",         "Hakkari",         "Хаккяри",         "Гакарі",          "Eastern Anatolia"),
    ("31", "Hatay",           "Hatay",           "Хатай",           "Хатай",           "Mediterranean"),
    ("32", "Isparta",         "Isparta",         "Ыспарта",         "Ипарта",          "Mediterranean"),
    ("33", "Mersin",          "Mersin",          "Мерсин",          "Мерсін",          "Mediterranean"),
    ("34", "Istanbul",        "Istanbul",        "Стамбул",         "Стамбул",         "Marmara"),
    ("35", "İzmir",           "Izmir",           "Измир",           "Ізмір",           "Aegean"),
    ("36", "Kars",            "Kars",            "Карс",            "Карс",            "Eastern Anatolia"),
    ("37", "Kastamonu",       "Kastamonu",       "Кастамону",       "Кастамону",       "Black Sea"),
    ("38", "Kayseri",         "Kayseri",         "Кайсери",         "Кайсері",         "Central Anatolia"),
    ("39", "Kırklareli",      "Kırklareli",      "Кыркларели",      "Киркларелі",      "Marmara"),
    ("40", "Kırşehir",        "Kırşehir",        "Кыршехир",        "Киршегір",        "Central Anatolia"),
    ("41", "Kocaeli",         "Kocaeli",         "Коджаэли",        "Коджаелі",        "Marmara"),
    ("42", "Konya",           "Konya",           "Конья",           "Конья",           "Central Anatolia"),
    ("43", "Kütahya",         "Kütahya",         "Кютахья",         "Кютах'я",         "Aegean"),
    ("44", "Malatya",         "Malatya",         "Малатья",         "Малатья",         "Eastern Anatolia"),
    ("45", "Manisa",          "Manisa",          "Маниса",          "Маніса",          "Aegean"),
    ("46", "Kahramanmaraş",   "Kahramanmaraş",   "Кахраманмараш",   "Кахраманмараш",   "Mediterranean"),
    ("47", "Mardin",          "Mardin",          "Мардин",          "Мардін",          "Southeastern Anatolia"),
    ("48", "Muğla",           "Muğla",           "Мугла",           "Мугла",           "Aegean"),
    ("49", "Muş",             "Muş",             "Муш",             "Муш",             "Eastern Anatolia"),
    ("50", "Nevşehir",        "Nevşehir",        "Невшехир",        "Невшегір",        "Central Anatolia"),
    ("51", "Niğde",           "Niğde",           "Нигде",           "Ніде",            "Central Anatolia"),
    ("52", "Ordu",            "Ordu",            "Орду",            "Орду",            "Black Sea"),
    ("53", "Rize",            "Rize",            "Риза",            "Різе",            "Black Sea"),
    ("54", "Sakarya",         "Sakarya",         "Сакарья",         "Сакарья",         "Marmara"),
    ("55", "Samsun",          "Samsun",          "Самсун",          "Самсун",          "Black Sea"),
    ("56", "Siirt",           "Siirt",           "Сиирт",           "Сіірт",           "Southeastern Anatolia"),
    ("57", "Sinop",           "Sinop",           "Синоп",           "Сіноп",           "Black Sea"),
    ("58", "Sivas",           "Sivas",           "Сивас",           "Сівас",           "Black Sea"),
    ("59", "Tekirdağ",        "Tekirdağ",        "Текирдаг",        "Текірдаг",        "Marmara"),
    ("60", "Tokat",           "Tokat",           "Токат",           "Токат",           "Black Sea"),
    ("61", "Trabzon",         "Trabzon",         "Трабзон",         "Трабзон",         "Black Sea"),
    ("62", "Tunceli",         "Tunceli",         "Тунджели",        "Тунджелі",        "Eastern Anatolia"),
    ("63", "Şanlıurfa",       "Şanlıurfa",       "Шанлыурфа",       "Шанлиурфа",       "Southeastern Anatolia"),
    ("64", "Uşak",            "Uşak",            "Ушак",            "Ушак",            "Aegean"),
    ("65", "Van",             "Van",             "Ван",             "Ван",             "Eastern Anatolia"),
    ("66", "Yozgat",          "Yozgat",          "Йозгат",          "Йозгат",          "Central Anatolia"),
    ("67", "Zonguldak",       "Zonguldak",       "Зонгулдак",       "Зонгулдак",       "Black Sea"),
    ("68", "Aksaray",         "Aksaray",         "Аксарай",         "Аксарай",         "Central Anatolia"),
    ("69", "Bayburt",         "Bayburt",         "Байбурт",         "Байбурт",         "Black Sea"),
    ("70", "Karaman",         "Karaman",         "Караман",         "Караман",         "Central Anatolia"),
    ("71", "Kırıkkale",       "Kırıkkale",       "Кырыккале",       "Киріккале",       "Central Anatolia"),
    ("72", "Batman",          "Batman",          "Батман",          "Батман",          "Southeastern Anatolia"),
    ("73", "Şırnak",          "Şırnak",          "Ширнак",          "Шірнак",          "Southeastern Anatolia"),
    ("74", "Bartın",          "Bartın",          "Бартын",          "Бартин",          "Black Sea"),
    ("75", "Ardahan",         "Ardahan",         "Ардахан",         "Ардаган",         "Eastern Anatolia"),
    ("76", "Iğdır",           "Iğdır",           "Ыгдыр",           "Игдир",           "Eastern Anatolia"),
    ("77", "Yalova",          "Yalova",          "Ялова",           "Ялова",           "Marmara"),
    ("78", "Karabük",         "Karabük",         "Карабюк",         "Карабюк",         "Black Sea"),
    ("79", "Kilis",           "Kilis",           "Килис",           "Кіліс",           "Southeastern Anatolia"),
    ("80", "Osmaniye",        "Osmaniye",        "Османие",         "Османіє",         "Mediterranean"),
    ("81", "Düzce",           "Düzce",           "Дюздже",          "Дюздже",          "Black Sea"),
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
    """Insert the TR country record and its translations.

    Args:
        conn: An open SQLite connection (foreign keys must be on).
    """
    country_id = _get_or_insert_country(conn)
    _insert_country_translations(conn, country_id)
    logger.info("Seeded country TR (id=%d)", country_id)


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
    """Insert one province and its translations."""
    lat = coords[0] if coords else None
    lon = coords[1] if coords else None
    conn.execute(
        "INSERT OR IGNORE INTO regions"
        " (country_id, plate_code, latitude, longitude) VALUES (?, ?, ?, ?)",
        (country_id, plate_code, lat, lon),
    )
    row = conn.execute(
        "SELECT id FROM regions WHERE country_id = ? AND plate_code = ?",
        (country_id, plate_code),
    ).fetchone()
    name_trans = {"en": name_en, "de": name_de, "ru": name_ru, "uk": name_uk}
    group_trans = _BOLGE[region_key]
    _insert_region_translations(conn, row[0], name_trans, group_trans)


def seed_regions(conn: sqlite3.Connection) -> None:
    """Insert all TR province records and their translations.

    Args:
        conn: An open SQLite connection.
    """
    row = conn.execute("SELECT id FROM countries WHERE code = ?", (COUNTRY_CODE,)).fetchone()
    country_id: int = row[0]
    for plate_code, name_en, name_de, name_ru, name_uk, region_key in _REGION_ROWS:
        coords = _COORDS.get(plate_code)
        _seed_single_region(
            conn, country_id, plate_code,
            name_en, name_de, name_ru, name_uk,
            region_key, coords,
        )
    logger.info("Seeded %d TR provinces", len(_REGION_ROWS))


def run(conn: sqlite3.Connection) -> None:
    """Run the full Turkey seed: country + all provinces.

    Args:
        conn: An open SQLite connection.
    """
    seed_country(conn)
    seed_regions(conn)


def main() -> None:
    """Open the production DB, seed Turkey, and close."""
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s — %(message)s")
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    try:
        run(conn)
        conn.commit()
        logger.info("Turkey seed complete")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
