"""Seed Austria (AT) into the CarTags database.

Inserts the country record, its translations, and ~70 region records
with full translations in en/de/ru/uk.  All inserts are idempotent
via INSERT OR IGNORE.

Usage::

    python data/seed_at.py
"""

import logging
import sqlite3
from pathlib import Path

logger = logging.getLogger(__name__)

DB_PATH = Path(__file__).parent.parent / "db" / "cartags.db"

COUNTRY_CODE = "AT"
COUNTRY_EMOJI = "🇦🇹"
COUNTRY_SORT_ORDER = 2

_COUNTRY_TRANSLATIONS: dict[str, str] = {
    "en": "Austria",
    "de": "Österreich",
    "ru": "Австрия",
    "uk": "Австрія",
}

# Bundesland translation lookup used by regions below.
_BUNDESLAND: dict[str, dict[str, str]] = {
    "Wien": {
        "en": "Vienna", "de": "Wien", "ru": "Вена", "uk": "Відень",
    },
    "Niederösterreich": {
        "en": "Lower Austria", "de": "Niederösterreich",
        "ru": "Нижняя Австрия", "uk": "Нижня Австрія",
    },
    "Oberösterreich": {
        "en": "Upper Austria", "de": "Oberösterreich",
        "ru": "Верхняя Австрия", "uk": "Верхня Австрія",
    },
    "Steiermark": {
        "en": "Styria", "de": "Steiermark", "ru": "Штирия", "uk": "Штирія",
    },
    "Kärnten": {
        "en": "Carinthia", "de": "Kärnten", "ru": "Каринтия", "uk": "Каринтія",
    },
    "Salzburg": {
        "en": "Salzburg", "de": "Salzburg", "ru": "Зальцбург", "uk": "Зальцбург",
    },
    "Tirol": {
        "en": "Tyrol", "de": "Tirol", "ru": "Тироль", "uk": "Тіроль",
    },
    "Vorarlberg": {
        "en": "Vorarlberg", "de": "Vorarlberg", "ru": "Форарльберг", "uk": "Форарльберг",
    },
    "Burgenland": {
        "en": "Burgenland", "de": "Burgenland", "ru": "Бургенланд", "uk": "Бургенланд",
    },
}

# (plate_code, name_en, name_de, name_ru, name_uk, bundesland_key)
_REGION_ROWS: list[tuple[str, str, str, str, str, str]] = [
    # ---- Vienna ----
    ("W",  "Vienna",                     "Wien",                      "Вена",                       "Відень",                     "Wien"),
    # ---- Lower Austria ----
    ("AM", "Amstetten",                  "Amstetten",                 "Амштеттен",                  "Амштеттен",                  "Niederösterreich"),
    ("BL", "Bruck an der Leitha",        "Bruck an der Leitha",       "Брук-на-Лейте",              "Брук-на-Лейті",              "Niederösterreich"),
    ("BN", "Baden",                      "Baden",                     "Баден",                      "Баден",                      "Niederösterreich"),
    ("GD", "Gmünd",                      "Gmünd",                     "Гмюнд",                      "Ґмюнд",                      "Niederösterreich"),
    ("GF", "Gänserndorf",                "Gänserndorf",               "Гензерндорф",                "Гензерндорф",                "Niederösterreich"),
    ("HL", "Hollabrunn",                 "Hollabrunn",                "Холлабрунн",                 "Голлабрунн",                 "Niederösterreich"),
    ("HO", "Horn",                       "Horn",                      "Хорн",                       "Горн",                       "Niederösterreich"),
    ("KG", "Klosterneuburg",             "Klosterneuburg",            "Клостернойбург",             "Клостернойбург",             "Niederösterreich"),
    ("KO", "Korneuburg",                 "Korneuburg",                "Корнойбург",                 "Корнойбург",                 "Niederösterreich"),
    ("KR", "Krems-Land",                 "Krems-Land",                "Кремс-Ланд",                 "Кремс-Ланд",                 "Niederösterreich"),
    ("KS", "Krems",                      "Krems",                     "Кремс",                      "Кремс",                      "Niederösterreich"),
    ("LF", "Lilienfeld",                 "Lilienfeld",                "Лилиенфельд",                "Ліліенфельд",                "Niederösterreich"),
    ("MD", "Mödling",                    "Mödling",                   "Мёдлинг",                    "Медлінг",                    "Niederösterreich"),
    ("ME", "Melk",                       "Melk",                      "Мельк",                      "Мельк",                      "Niederösterreich"),
    ("MI", "Mistelbach",                 "Mistelbach",                "Мистельбах",                 "Містельбах",                 "Niederösterreich"),
    ("NK", "Neunkirchen",                "Neunkirchen",               "Нойнкирхен",                 "Нойнкірхен",                 "Niederösterreich"),
    ("P",  "St. Pölten",                 "St. Pölten",                "Санкт-Пёльтен",              "Санкт-Пельтен",              "Niederösterreich"),
    ("PL", "St. Pölten-Land",            "St. Pölten-Land",           "Санкт-Пёльтен-Ланд",         "Санкт-Пельтен-Ланд",         "Niederösterreich"),
    ("SB", "Scheibbs",                   "Scheibbs",                  "Шайббс",                     "Шайббс",                     "Niederösterreich"),
    ("SW", "Schwechat",                  "Schwechat",                 "Шведат",                     "Шведат",                     "Niederösterreich"),
    ("TU", "Tulln",                      "Tulln",                     "Туллн",                      "Туллн",                      "Niederösterreich"),
    ("WB", "Wiener Neustadt-Land",       "Wiener Neustadt-Land",      "Винер-Нойштадт-Ланд",        "Вінер-Нойштадт-Ланд",        "Niederösterreich"),
    ("WN", "Wiener Neustadt",            "Wiener Neustadt",           "Винер-Нойштадт",             "Вінер-Нойштадт",             "Niederösterreich"),
    ("WT", "Waidhofen an der Thaya",     "Waidhofen an der Thaya",    "Вайдхофен-на-Тае",           "Вайдхофен-на-Таї",           "Niederösterreich"),
    ("WU", "Wien-Umgebung",              "Wien-Umgebung",             "Вена-Умгебунг",              "Відень-Умгебунг",            "Niederösterreich"),
    ("WY", "Waidhofen an der Ybbs",      "Waidhofen an der Ybbs",     "Вайдхофен-на-Иббсе",        "Вайдхофен-на-Іббсі",         "Niederösterreich"),
    ("ZT", "Zwettl",                     "Zwettl",                    "Цветтль",                    "Цветтль",                    "Niederösterreich"),
    # ---- Upper Austria ----
    ("BR", "Braunau am Inn",             "Braunau am Inn",            "Браунау-на-Инне",            "Браунау-на-Інні",            "Oberösterreich"),
    ("EF", "Eferding",                   "Eferding",                  "Эфердинг",                   "Ефердінг",                   "Oberösterreich"),
    ("FR", "Freistadt",                  "Freistadt",                 "Фрайштадт",                  "Фрайштадт",                  "Oberösterreich"),
    ("GM", "Gmunden",                    "Gmunden",                   "Гмунден",                    "Ґмунден",                    "Oberösterreich"),
    ("GR", "Grieskirchen",               "Grieskirchen",              "Грискирхен",                 "Ґрискірхен",                 "Oberösterreich"),
    ("KI", "Kirchdorf an der Krems",     "Kirchdorf an der Krems",    "Кирхдорф-на-Кремсе",         "Кірхдорф-на-Кремсі",         "Oberösterreich"),
    ("L",  "Linz",                       "Linz",                      "Линц",                       "Лінц",                       "Oberösterreich"),
    ("LL", "Linz-Land",                  "Linz-Land",                 "Линц-Ланд",                  "Лінц-Ланд",                  "Oberösterreich"),
    ("PE", "Perg",                       "Perg",                      "Перг",                       "Перґ",                       "Oberösterreich"),
    ("RI", "Ried",                       "Ried im Innkreis",          "Рид",                        "Рід",                        "Oberösterreich"),
    ("RO", "Rohrbach",                   "Rohrbach",                  "Рорбах",                     "Рорбах",                     "Oberösterreich"),
    ("SD", "Schärding",                  "Schärding",                 "Шердинг",                    "Шердінг",                    "Oberösterreich"),
    ("SE", "Steyr-Land",                 "Steyr-Land",                "Штайр-Ланд",                 "Штайр-Ланд",                 "Oberösterreich"),
    ("SR", "Steyr",                      "Steyr",                     "Штайр",                      "Штайр",                      "Oberösterreich"),
    ("UU", "Urfahr-Umgebung",            "Urfahr-Umgebung",           "Урфар-Умгебунг",             "Урфар-Умгебунг",             "Oberösterreich"),
    ("VB", "Vöcklabruck",                "Vöcklabruck",               "Фёклабрук",                  "Феклабрук",                  "Oberösterreich"),
    ("WE", "Wels",                       "Wels",                      "Вельс",                      "Вельс",                      "Oberösterreich"),
    ("WL", "Wels-Land",                  "Wels-Land",                 "Вельс-Ланд",                 "Вельс-Ланд",                 "Oberösterreich"),
    # ---- Styria ----
    ("BM", "Bruck-Mürzzuschlag",         "Bruck-Mürzzuschlag",        "Брук-Мюрццушлаг",            "Брук-Мюрццушлаґ",            "Steiermark"),
    ("DL", "Deutschlandsberg",           "Deutschlandsberg",          "Дойчландсберг",              "Дойчландсберг",              "Steiermark"),
    ("G",  "Graz",                       "Graz",                      "Грац",                       "Ґрац",                       "Steiermark"),
    ("GB", "Gröbming",                   "Gröbming",                  "Грёбминг",                   "Ґребмінг",                   "Steiermark"),
    ("GU", "Graz-Umgebung",              "Graz-Umgebung",             "Грац-Умгебунг",              "Ґрац-Умгебунг",              "Steiermark"),
    ("HB", "Hartberg",                   "Hartberg",                  "Хартберг",                   "Гартберг",                   "Steiermark"),
    ("HF", "Hartberg-Fürstenfeld",       "Hartberg-Fürstenfeld",      "Хартберг-Фюрстенфельд",      "Гартберг-Фюрстенфельд",      "Steiermark"),
    ("JU", "Judenburg",                  "Judenburg",                 "Юденбург",                   "Юденбург",                   "Steiermark"),
    ("KF", "Knittelfeld",                "Knittelfeld",               "Книттельфельд",              "Книттельфельд",              "Steiermark"),
    ("LB", "Leibnitz",                   "Leibnitz",                  "Лайбниц",                    "Лайбніц",                    "Steiermark"),
    ("LE", "Leoben",                     "Leoben",                    "Леобен",                     "Леобен",                     "Steiermark"),
    ("LI", "Liezen",                     "Liezen",                    "Лизен",                      "Лієзен",                     "Steiermark"),
    ("LN", "Leoben (countryside)",        "Leoben (Umland)",           "Леобен (округа)",            "Леобен (округа)",            "Steiermark"),
    ("MT", "Murtal",                     "Murtal",                    "Муртал",                     "Муртал",                     "Steiermark"),
    ("MU", "Murau",                      "Murau",                     "Мурау",                      "Мурау",                      "Steiermark"),
    ("MZ", "Mürzzuschlag",               "Mürzzuschlag",              "Мюрццушлаг",                 "Мюрццушлаґ",                 "Steiermark"),
    ("SO", "Südoststeiermark",           "Südoststeiermark",          "Зюдостштайермарк",           "Зюдостштайермарк",           "Steiermark"),
    ("VO", "Voitsberg",                  "Voitsberg",                 "Войтсберг",                  "Войтсберг",                  "Steiermark"),
    ("WZ", "Weiz",                       "Weiz",                      "Вайц",                       "Вайц",                       "Steiermark"),
    # ---- Carinthia ----
    ("FE", "Feldkirchen",                "Feldkirchen",               "Фельдкирхен",                "Фельдкірхен",                "Kärnten"),
    ("HE", "Hermagor",                   "Hermagor",                  "Хермагор",                   "Хермаґор",                   "Kärnten"),
    ("K",  "Klagenfurt",                 "Klagenfurt",                "Клагенфурт",                 "Клаґенфурт",                 "Kärnten"),
    ("KL", "Klagenfurt-Land",            "Klagenfurt-Land",           "Клагенфурт-Ланд",            "Клаґенфурт-Ланд",            "Kärnten"),
    ("SP", "Spittal an der Drau",        "Spittal an der Drau",       "Шпитталь-на-Драу",           "Шпітталь-на-Драу",           "Kärnten"),
    ("SV", "St. Veit an der Glan",       "St. Veit an der Glan",      "Санкт-Файт-на-Глане",        "Санкт-Файт-на-Ґлані",        "Kärnten"),
    ("VI", "Villach",                    "Villach",                   "Филлах",                     "Філлах",                     "Kärnten"),
    ("VK", "Völkermarkt",                "Völkermarkt",               "Фёлькермаркт",               "Фелькермаркт",               "Kärnten"),
    ("VL", "Villach-Land",               "Villach-Land",              "Филлах-Ланд",                "Філлах-Ланд",                "Kärnten"),
    ("WO", "Wolfsberg",                  "Wolfsberg",                 "Вольфсберг",                 "Вольфсберг",                 "Kärnten"),
    # ---- Salzburg ----
    ("HA", "Hallein",                    "Hallein",                   "Халляйн",                    "Халляйн",                    "Salzburg"),
    ("JO", "St. Johann im Pongau",       "St. Johann im Pongau",      "Санкт-Йоханн-им-Понгау",     "Санкт-Йоганн-ім-Понгау",     "Salzburg"),
    ("S",  "Salzburg",                   "Salzburg",                  "Зальцбург",                  "Зальцбург",                  "Salzburg"),
    ("SL", "Salzburg-Umgebung",          "Salzburg-Umgebung",         "Зальцбург-Умгебунг",         "Зальцбург-Умгебунг",         "Salzburg"),
    ("TA", "Tamsweg",                    "Tamsweg",                   "Тамсвег",                    "Тамсвег",                    "Salzburg"),
    ("ZE", "Zell am See",                "Zell am See",               "Целль-ам-Зее",               "Целль-ам-Зее",               "Salzburg"),
    # ---- Tyrol ----
    ("I",  "Innsbruck",                  "Innsbruck",                 "Инсбрук",                    "Інсбрук",                    "Tirol"),
    ("IL", "Innsbruck-Land",             "Innsbruck-Land",            "Инсбрук-Ланд",               "Інсбрук-Ланд",               "Tirol"),
    ("IM", "Imst",                       "Imst",                      "Имст",                       "Імст",                       "Tirol"),
    ("KB", "Kitzbühel",                  "Kitzbühel",                 "Кицбюэль",                   "Кіцбюель",                   "Tirol"),
    ("KU", "Kufstein",                   "Kufstein",                  "Куфштайн",                   "Куфштайн",                   "Tirol"),
    ("LA", "Landeck",                    "Landeck",                   "Ландек",                     "Ландек",                     "Tirol"),
    ("LZ", "Lienz",                      "Lienz",                     "Лиенц",                      "Лієнц",                      "Tirol"),
    ("RE", "Reutte",                     "Reutte",                    "Ройтте",                     "Ройтте",                     "Tirol"),
    ("SZ", "Schwaz",                     "Schwaz",                    "Шварц",                      "Шварц",                      "Tirol"),
    # ---- Vorarlberg ----
    ("B",  "Bregenz",                    "Bregenz",                   "Брегенц",                    "Брегенц",                    "Vorarlberg"),
    ("BZ", "Bludenz",                    "Bludenz",                   "Блуденц",                    "Блуденц",                    "Vorarlberg"),
    ("DO", "Dornbirn",                   "Dornbirn",                  "Дорнбирн",                   "Дорнбірн",                   "Vorarlberg"),
    ("FK", "Feldkirch",                  "Feldkirch",                 "Фельдкирх",                  "Фельдкірх",                  "Vorarlberg"),
    # ---- Burgenland ----
    ("E",  "Eisenstadt",                 "Eisenstadt",                "Айзенштадт",                 "Айзенштадт",                 "Burgenland"),
    ("EU", "Eisenstadt-Umgebung",        "Eisenstadt-Umgebung",       "Айзенштадт-Умгебунг",        "Айзенштадт-Умгебунг",        "Burgenland"),
    ("GS", "Güssing",                    "Güssing",                   "Гюссинг",                    "Ґюссінг",                    "Burgenland"),
    ("JE", "Jennersdorf",                "Jennersdorf",               "Йеннерсдорф",                "Єннерсдорф",                 "Burgenland"),
    ("MA", "Mattersburg",                "Mattersburg",               "Маттерсбург",                "Маттерсбург",                "Burgenland"),
    ("ND", "Neusiedl am See",            "Neusiedl am See",           "Нойзидль-на-Зее",            "Нойзідль-на-Зее",            "Burgenland"),
    ("OP", "Oberpullendorf",             "Oberpullendorf",            "Обerpулендорф",              "Обerpулендорф",              "Burgenland"),
    ("OW", "Oberwart",                   "Oberwart",                  "Обервард",                   "Обервард",                   "Burgenland"),
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
    """Insert the AT country record and its translations.

    Args:
        conn: An open SQLite connection (foreign keys must be on).
    """
    country_id = _get_or_insert_country(conn)
    _insert_country_translations(conn, country_id)
    logger.info("Seeded country AT (id=%d)", country_id)


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
    bundesland_key: str,
) -> None:
    """Insert one region and its 8 translations (4 name + 4 region_group)."""
    conn.execute(
        "INSERT OR IGNORE INTO regions (country_id, plate_code) VALUES (?, ?)",
        (country_id, plate_code.upper()),
    )
    row = conn.execute(
        "SELECT id FROM regions WHERE country_id = ? AND plate_code = ?",
        (country_id, plate_code.upper()),
    ).fetchone()
    name_trans = {"en": name_en, "de": name_de, "ru": name_ru, "uk": name_uk}
    group_trans = _BUNDESLAND[bundesland_key]
    _insert_region_translations(conn, row[0], name_trans, group_trans)


def seed_regions(conn: sqlite3.Connection) -> None:
    """Insert all AT region records and their translations.

    Args:
        conn: An open SQLite connection.
    """
    row = conn.execute("SELECT id FROM countries WHERE code = ?", (COUNTRY_CODE,)).fetchone()
    country_id: int = row[0]
    for plate_code, name_en, name_de, name_ru, name_uk, bundesland_key in _REGION_ROWS:
        _seed_single_region(conn, country_id, plate_code, name_en, name_de, name_ru, name_uk, bundesland_key)
    logger.info("Seeded %d AT regions", len(_REGION_ROWS))


def run(conn: sqlite3.Connection) -> None:
    """Run the full Austria seed: country + all regions.

    Args:
        conn: An open SQLite connection.
    """
    seed_country(conn)
    seed_regions(conn)


def main() -> None:
    """Open the production DB, seed Austria, and close."""
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s — %(message)s")
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    try:
        run(conn)
        conn.commit()
        logger.info("Austria seed complete")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
