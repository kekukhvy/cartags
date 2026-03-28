"""Seed Czech Republic (CZ) into the CarTags database.

Inserts the country record, its translations, and ~77 district records
with full translations in en/de/ru/uk.  All inserts are idempotent
via INSERT OR IGNORE.

Usage::

    python data/seed_cz.py
"""

import logging
import sqlite3
from pathlib import Path

logger = logging.getLogger(__name__)

DB_PATH = Path(__file__).parent.parent / "db" / "cartags.db"

COUNTRY_CODE = "CZ"
COUNTRY_EMOJI = "🇨🇿"
COUNTRY_SORT_ORDER = 5

_COUNTRY_TRANSLATIONS: dict[str, str] = {
    "en": "Czech Republic",
    "de": "Tschechische Republik",
    "ru": "Чехия",
    "uk": "Чехія",
}

_KRAJ: dict[str, dict[str, str]] = {
    "Praha": {
        "en": "Prague",
        "de": "Prag",
        "ru": "Прага",
        "uk": "Прага",
    },
    "Středočeský": {
        "en": "Central Bohemian Region",
        "de": "Mittelböhmische Region",
        "ru": "Среднечешский край",
        "uk": "Середньочеський край",
    },
    "Jihočeský": {
        "en": "South Bohemian Region",
        "de": "Südböhmische Region",
        "ru": "Южночешский край",
        "uk": "Південночеський край",
    },
    "Plzeňský": {
        "en": "Plzeň Region",
        "de": "Region Pilsen",
        "ru": "Пльзеньский край",
        "uk": "Пльзенський край",
    },
    "Karlovarský": {
        "en": "Karlovy Vary Region",
        "de": "Region Karlsbad",
        "ru": "Карловарский край",
        "uk": "Карловарський край",
    },
    "Ústecký": {
        "en": "Ústí nad Labem Region",
        "de": "Region Aussig",
        "ru": "Устецкий край",
        "uk": "Устецький край",
    },
    "Liberecký": {
        "en": "Liberec Region",
        "de": "Region Reichenberg",
        "ru": "Либерецкий край",
        "uk": "Ліберецький край",
    },
    "Královéhradecký": {
        "en": "Hradec Králové Region",
        "de": "Region Königgrätz",
        "ru": "Краловеградецкий край",
        "uk": "Краловеградецький край",
    },
    "Pardubický": {
        "en": "Pardubice Region",
        "de": "Region Pardubitz",
        "ru": "Пардубицкий край",
        "uk": "Пардубицький край",
    },
    "Vysočina": {
        "en": "Vysočina Region",
        "de": "Region Vysočina",
        "ru": "Высочина",
        "uk": "Височина",
    },
    "Jihomoravský": {
        "en": "South Moravian Region",
        "de": "Südmährische Region",
        "ru": "Южноморавский край",
        "uk": "Південноморавський край",
    },
    "Olomoucký": {
        "en": "Olomouc Region",
        "de": "Region Olmütz",
        "ru": "Оломоуцкий край",
        "uk": "Оломоуцький край",
    },
    "Zlínský": {
        "en": "Zlín Region",
        "de": "Region Zlín",
        "ru": "Злинский край",
        "uk": "Злінський край",
    },
    "Moravskoslezský": {
        "en": "Moravian-Silesian Region",
        "de": "Mährisch-Schlesische Region",
        "ru": "Моравскосилезский край",
        "uk": "Моравськосілезький край",
    },
}

_COORDS: dict[str, tuple[float, float]] = {
    "1A": (50.0755, 14.4378),  # Prague
    "1B": (50.0755, 14.4378),
    "1C": (50.0755, 14.4378),
    "1D": (50.0755, 14.4378),
    "1E": (50.0755, 14.4378),
    "1F": (50.0755, 14.4378),
    "1G": (50.0755, 14.4378),
    "1H": (50.0755, 14.4378),
    "1I": (50.0755, 14.4378),
    "1J": (50.0755, 14.4378),
    "1K": (50.0755, 14.4378),
    "1L": (50.0755, 14.4378),
    "1M": (50.0755, 14.4378),
    "1N": (50.0755, 14.4378),
    "1O": (50.0755, 14.4378),
    "1P": (50.0755, 14.4378),
    "2A": (50.0521, 14.4074),  # Central Bohemia
    "2B": (50.0521, 14.4074),
    "2C": (50.0521, 14.4074),
    "2D": (50.0521, 14.4074),
    "2E": (50.0521, 14.4074),
    "3A": (48.9745, 14.4742),  # České Budějovice
    "3B": (48.9745, 14.4742),
    "3C": (48.9745, 14.4742),
    "3D": (48.9745, 14.4742),
    "3E": (48.9745, 14.4742),
    "3F": (48.9745, 14.4742),
    "3G": (48.9745, 14.4742),
    "4A": (49.7384, 13.3736),  # Plzeň
    "4B": (49.7384, 13.3736),
    "4C": (49.7384, 13.3736),
    "4D": (49.7384, 13.3736),
    "4E": (49.7384, 13.3736),
    "4F": (49.7384, 13.3736),
    "4G": (49.7384, 13.3736),
    "5A": (50.2311, 12.8716),  # Karlovy Vary
    "5B": (50.2311, 12.8716),
    "5C": (50.2311, 12.8716),
    "6A": (50.6611, 14.0531),  # Ústí nad Labem
    "6B": (50.6611, 14.0531),
    "6C": (50.6611, 14.0531),
    "6D": (50.6611, 14.0531),
    "6E": (50.6611, 14.0531),
    "6F": (50.6611, 14.0531),
    "6G": (50.6611, 14.0531),
    "7A": (50.7663, 15.0543),  # Liberec
    "7B": (50.7663, 15.0543),
    "7C": (50.7663, 15.0543),
    "7D": (50.7663, 15.0543),
    "7E": (50.2104, 15.8336),  # Hradec Králové
    "7F": (50.2104, 15.8336),
    "7G": (50.2104, 15.8336),
    "7H": (50.2104, 15.8336),
    "7I": (50.0343, 15.7812),  # Pardubice
    "7J": (50.0343, 15.7812),
    "7K": (50.0343, 15.7812),
    "7L": (50.0343, 15.7812),
    "7M": (49.3961, 15.5913),  # Jihlava
    "7N": (49.3961, 15.5913),
    "7O": (49.3961, 15.5913),
    "7P": (49.3961, 15.5913),
    "8A": (49.1951, 16.6068),  # Brno
    "8B": (49.1951, 16.6068),
    "8C": (49.1951, 16.6068),
    "8D": (49.1951, 16.6068),
    "8E": (49.1951, 16.6068),
    "8F": (49.5938, 17.2509),  # Olomouc
    "8G": (49.5938, 17.2509),
    "8H": (49.2255, 17.6671),  # Zlín
    "8I": (49.2255, 17.6671),
    "8J": (49.8209, 18.2625),  # Ostrava
    "8K": (49.8209, 18.2625),
    "8L": (49.8209, 18.2625),
    "8M": (49.8209, 18.2625),
}

# (plate_code, name_en, name_de, name_ru, name_uk, kraj_key)
_REGION_ROWS: list[tuple[str, str, str, str, str, str]] = [
    # Prague
    ("1A", "Prague 1", "Prag 1", "Прага 1", "Прага 1", "Praha"),
    ("1B", "Prague 2", "Prag 2", "Прага 2", "Прага 2", "Praha"),
    ("1C", "Prague 3", "Prag 3", "Прага 3", "Прага 3", "Praha"),
    ("1D", "Prague 4", "Prag 4", "Прага 4", "Прага 4", "Praha"),
    ("1E", "Prague 5", "Prag 5", "Прага 5", "Прага 5", "Praha"),
    ("1F", "Prague 6", "Prag 6", "Прага 6", "Прага 6", "Praha"),
    ("1G", "Prague 7", "Prag 7", "Прага 7", "Прага 7", "Praha"),
    ("1H", "Prague 8", "Prag 8", "Прага 8", "Прага 8", "Praha"),
    ("1I", "Prague 9", "Prag 9", "Прага 9", "Прага 9", "Praha"),
    ("1J", "Prague 10", "Prag 10", "Прага 10", "Прага 10", "Praha"),
    ("1K", "Prague-East", "Prag-Ost", "Прага-Восток", "Прага-Схід", "Praha"),
    ("1L", "Prague-West", "Prag-West", "Прага-Запад", "Прага-Захід", "Praha"),
    ("1M", "Kladno", "Kladno", "Кладно", "Кладно", "Středočeský"),
    ("1N", "Beroun", "Beroun", "Бероун", "Бероун", "Středočeský"),
    ("1O", "Kolín", "Kolin", "Колин", "Колін", "Středočeský"),
    ("1P", "Kutná Hora", "Kuttenberg", "Кутна-Гора", "Кутна Гора", "Středočeský"),
    # Central Bohemia
    ("2A", "Mělník", "Melnik", "Мелник", "Мелник", "Středočeský"),
    ("2B", "Mladá Boleslav", "Jungbunzlau", "Млада-Болеслав", "Млада Болеслав", "Středočeský"),
    ("2C", "Nymburk", "Nimburg", "Нимбурк", "Німбурк", "Středočeský"),
    ("2D", "Příbram", "Přibram", "Пршибрам", "Пршибрам", "Středočeský"),
    ("2E", "Rakovník", "Rakonitz", "Раковник", "Раковник", "Středočeský"),
    # South Bohemia
    ("3A", "České Budějovice", "Budweis", "Чешске-Будеёвице", "Чеські Будейовіце", "Jihočeský"),
    ("3B", "Český Krumlov", "Böhmisch Krumau", "Чешски-Крумлов", "Чеський Крумлов", "Jihočeský"),
    ("3C", "Jindřichův Hradec", "Neuhaus", "Индржихув-Градец", "Їндржихів Градець", "Jihočeský"),
    ("3D", "Písek", "Pisek", "Писек", "Písek", "Jihočeský"),
    ("3E", "Prachatice", "Prachatitz", "Прахатице", "Прахатіце", "Jihočeský"),
    ("3F", "Strakonice", "Strakonitz", "Стракониче", "Страконіце", "Jihočeský"),
    ("3G", "Tábor", "Tabor", "Табор", "Табор", "Jihočeský"),
    # Plzeň
    ("4A", "Plzeň-City", "Pilsen-Stadt", "Пльзень", "Пльзень", "Plzeňský"),
    ("4B", "Domažlice", "Taus", "Домажлице", "Домажліце", "Plzeňský"),
    ("4C", "Klatovy", "Klattau", "Клатовы", "Клатові", "Plzeňský"),
    ("4D", "Plzeň-North", "Pilsen-Nord", "Пльзень-Север", "Пльзень-Північ", "Plzeňský"),
    ("4E", "Plzeň-South", "Pilsen-Süd", "Пльзень-Юг", "Пльзень-Південь", "Plzeňský"),
    ("4F", "Rokycany", "Rokycany", "Рокицаны", "Рокіцани", "Plzeňský"),
    ("4G", "Tachov", "Tachau", "Тахов", "Тахов", "Plzeňský"),
    # Karlovy Vary
    ("5A", "Cheb", "Eger", "Хеб", "Хеб", "Karlovarský"),
    ("5B", "Karlovy Vary", "Karlsbad", "Карловы-Вары", "Карлові Вари", "Karlovarský"),
    ("5C", "Sokolov", "Falkenau", "Соколов", "Соколов", "Karlovarský"),
    # Ústí nad Labem
    ("6A", "Děčín", "Tetschen", "Дечин", "Дечін", "Ústecký"),
    ("6B", "Chomutov", "Komotau", "Хомутов", "Хомутов", "Ústecký"),
    ("6C", "Litoměřice", "Leitmeritz", "Литомержице", "Літомержіце", "Ústecký"),
    ("6D", "Louny", "Laun", "Лоуны", "Лоуни", "Ústecký"),
    ("6E", "Most", "Brüx", "Мост", "Мост", "Ústecký"),
    ("6F", "Teplice", "Teplitz", "Теплице", "Тепліце", "Ústecký"),
    ("6G", "Ústí nad Labem", "Aussig", "Усти-над-Лабем", "Усті-над-Лабем", "Ústecký"),
    # Liberec / Hradec Králové
    ("7A", "Česká Lípa", "Böhmisch Leipa", "Чешска-Липа", "Чеська Ліпа", "Liberecký"),
    ("7B", "Jablonec nad Nisou", "Gablonz", "Яблонец-над-Нисоу", "Яблонець-над-Нисоу", "Liberecký"),
    ("7C", "Liberec", "Reichenberg", "Либерец", "Ліберець", "Liberecký"),
    ("7D", "Semily", "Semil", "Семилы", "Семілі", "Liberecký"),
    ("7E", "Hradec Králové", "Königgrätz", "Градец-Кралове", "Градець Кралове", "Královéhradecký"),
    ("7F", "Jičín", "Jitschin", "Ичин", "Їчін", "Královéhradecký"),
    ("7G", "Náchod", "Nachod", "Наход", "Нахід", "Královéhradecký"),
    ("7H", "Trutnov", "Trautenau", "Трутнов", "Трутнов", "Královéhradecký"),
    # Pardubice / Vysočina
    ("7I", "Chrudim", "Chrudim", "Хрудим", "Хрудим", "Pardubický"),
    ("7J", "Pardubice", "Pardubitz", "Пардубице", "Пардубіце", "Pardubický"),
    ("7K", "Svitavy", "Zwittau", "Свитавы", "Світавіце", "Pardubický"),
    ("7L", "Ústí nad Orlicí", "Wildenschwert", "Усти-над-Орлици", "Усті-над-Орліці", "Pardubický"),
    ("7M", "Havlíčkův Brod", "Deutsch Brod", "Гавличкув-Брод", "Гавлічків Брод", "Vysočina"),
    ("7N", "Jihlava", "Iglau", "Йиглава", "Їглава", "Vysočina"),
    ("7O", "Pelhřimov", "Pilgram", "Пелгржимов", "Пелгржімов", "Vysočina"),
    ("7P", "Třebíč", "Trebitsch", "Тржебич", "Тршебіч", "Vysočina"),
    # South Moravia / Olomouc / Zlín / Moravia-Silesia
    ("8A", "Blansko", "Blansko", "Бланско", "Бланско", "Jihomoravský"),
    ("8B", "Brno-City", "Brünn-Stadt", "Брно-город", "Брно-місто", "Jihomoravský"),
    ("8C", "Brno-Country", "Brünn-Land", "Брно-район", "Брно-район", "Jihomoravský"),
    ("8D", "Břeclav", "Lundenburg", "Бржецлав", "Бржецлав", "Jihomoravský"),
    ("8E", "Hodonín", "Göding", "Годонин", "Годонін", "Jihomoravský"),
    ("8F", "Olomouc", "Olmütz", "Оломоуц", "Оломоуць", "Olomoucký"),
    ("8G", "Šumperk", "Schönberg", "Шумперк", "Шумперк", "Olomoucký"),
    ("8H", "Zlín", "Zlín", "Злин", "Злін", "Zlínský"),
    ("8I", "Uherské Hradiště", "Ungarisch Hradisch", "Угерске-Градиште", "Угерське Градіште", "Zlínský"),
    ("8J", "Frýdek-Místek", "Friedeck-Mistek", "Фридек-Мистек", "Фрідек-Містек", "Moravskoslezský"),
    ("8K", "Karviná", "Karwin", "Карвина", "Карвіна", "Moravskoslezský"),
    ("8L", "Nový Jičín", "Neu Titschein", "Нови-Йичин", "Новий Їчин", "Moravskoslezský"),
    ("8M", "Ostrava-City", "Ostrau-Stadt", "Острава-город", "Острава-місто", "Moravskoslezský"),
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
    """Insert the CZ country record and its translations.

    Args:
        conn: An open SQLite connection (foreign keys must be on).
    """
    country_id = _get_or_insert_country(conn)
    _insert_country_translations(conn, country_id)
    logger.info("Seeded country CZ (id=%d)", country_id)


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
    kraj_key: str,
    coords: tuple[float, float] | None,
) -> None:
    """Insert one district and its translations."""
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
    group_trans = _KRAJ[kraj_key]
    _insert_region_translations(conn, row[0], name_trans, group_trans)


def seed_regions(conn: sqlite3.Connection) -> None:
    """Insert all CZ district records and their translations.

    Args:
        conn: An open SQLite connection.
    """
    row = conn.execute("SELECT id FROM countries WHERE code = ?", (COUNTRY_CODE,)).fetchone()
    country_id: int = row[0]
    for plate_code, name_en, name_de, name_ru, name_uk, kraj_key in _REGION_ROWS:
        coords = _COORDS.get(plate_code.upper())
        _seed_single_region(
            conn, country_id, plate_code,
            name_en, name_de, name_ru, name_uk,
            kraj_key, coords,
        )
    logger.info("Seeded %d CZ districts", len(_REGION_ROWS))


def run(conn: sqlite3.Connection) -> None:
    """Run the full Czech Republic seed: country + all districts.

    Args:
        conn: An open SQLite connection.
    """
    seed_country(conn)
    seed_regions(conn)


def main() -> None:
    """Open the production DB, seed Czech Republic, and close."""
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s — %(message)s")
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    try:
        run(conn)
        conn.commit()
        logger.info("Czech Republic seed complete")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
