"""Seed Germany (DE) into the CarTags database.

Inserts the country record, its translations, and ~30 region records
with full translations in en/de/ru/uk.  All inserts are idempotent
via INSERT OR IGNORE.

Usage::

    python data/seed_de.py
"""

import logging
import sqlite3
from pathlib import Path

logger = logging.getLogger(__name__)

DB_PATH = Path(__file__).parent.parent / "db" / "cartags.db"

COUNTRY_CODE = "DE"
COUNTRY_EMOJI = "🇩🇪"
COUNTRY_SORT_ORDER = 1

_COUNTRY_TRANSLATIONS: dict[str, str] = {
    "en": "Germany",
    "de": "Deutschland",
    "ru": "Германия",
    "uk": "Німеччина",
}

# (plate_code, wikipedia_url | None, name_translations, region_group_translations)
_REGIONS: list[tuple[str, str | None, dict[str, str], dict[str, str]]] = [
    (
        "B", None,
        {"en": "Berlin", "de": "Berlin", "ru": "Берлин", "uk": "Берлін"},
        {"en": "Berlin", "de": "Berlin", "ru": "Берлин", "uk": "Берлін"},
    ),
    (
        "M", None,
        {"en": "Munich", "de": "München", "ru": "Мюнхен", "uk": "Мюнхен"},
        {"en": "Bavaria", "de": "Bayern", "ru": "Бавария", "uk": "Баварія"},
    ),
    (
        "HH", None,
        {"en": "Hamburg", "de": "Hamburg", "ru": "Гамбург", "uk": "Гамбург"},
        {"en": "Hamburg", "de": "Hamburg", "ru": "Гамбург", "uk": "Гамбург"},
    ),
    (
        "K", None,
        {"en": "Cologne", "de": "Köln", "ru": "Кёльн", "uk": "Кельн"},
        {
            "en": "North Rhine-Westphalia",
            "de": "Nordrhein-Westfalen",
            "ru": "Северный Рейн-Вестфалия",
            "uk": "Північний Рейн-Вестфалія",
        },
    ),
    (
        "F", None,
        {"en": "Frankfurt am Main", "de": "Frankfurt am Main", "ru": "Франкфурт-на-Майне", "uk": "Франкфурт-на-Майні"},
        {"en": "Hesse", "de": "Hessen", "ru": "Гессен", "uk": "Гессен"},
    ),
    (
        "S", None,
        {"en": "Stuttgart", "de": "Stuttgart", "ru": "Штутгарт", "uk": "Штутгарт"},
        {"en": "Baden-Württemberg", "de": "Baden-Württemberg", "ru": "Баден-Вюртемберг", "uk": "Баден-Вюртемберг"},
    ),
    (
        "D", None,
        {"en": "Düsseldorf", "de": "Düsseldorf", "ru": "Дюссельдорф", "uk": "Дюссельдорф"},
        {
            "en": "North Rhine-Westphalia",
            "de": "Nordrhein-Westfalen",
            "ru": "Северный Рейн-Вестфалия",
            "uk": "Північний Рейн-Вестфалія",
        },
    ),
    (
        "L", None,
        {"en": "Leipzig", "de": "Leipzig", "ru": "Лейпциг", "uk": "Лейпциг"},
        {"en": "Saxony", "de": "Sachsen", "ru": "Саксония", "uk": "Саксонія"},
    ),
    (
        "HB", None,
        {"en": "Bremen", "de": "Bremen", "ru": "Бремен", "uk": "Бремен"},
        {"en": "Bremen", "de": "Bremen", "ru": "Бремен", "uk": "Бремен"},
    ),
    (
        "MÜ", None,
        {"en": "Mühldorf am Inn", "de": "Mühldorf am Inn", "ru": "Мюльдорф-на-Инне", "uk": "Мюльдорф-на-Інні"},
        {"en": "Bavaria", "de": "Bayern", "ru": "Бавария", "uk": "Баварія"},
    ),
    (
        "BN", None,
        {"en": "Bonn", "de": "Bonn", "ru": "Бонн", "uk": "Бонн"},
        {
            "en": "North Rhine-Westphalia",
            "de": "Nordrhein-Westfalen",
            "ru": "Северный Рейн-Вестфалия",
            "uk": "Північний Рейн-Вестфалія",
        },
    ),
    (
        "DD", None,
        {"en": "Dresden", "de": "Dresden", "ru": "Дрезден", "uk": "Дрезден"},
        {"en": "Saxony", "de": "Sachsen", "ru": "Саксония", "uk": "Саксонія"},
    ),
    (
        "LE", None,
        {"en": "Esslingen am Neckar", "de": "Esslingen am Neckar", "ru": "Эсслинген-на-Неккаре", "uk": "Есслінген-на-Неккарі"},
        {"en": "Baden-Württemberg", "de": "Baden-Württemberg", "ru": "Баден-Вюртемберг", "uk": "Баден-Вюртемберг"},
    ),
    (
        "N", None,
        {"en": "Nuremberg", "de": "Nürnberg", "ru": "Нюрнберг", "uk": "Нюрнберг"},
        {"en": "Bavaria", "de": "Bayern", "ru": "Бавария", "uk": "Баварія"},
    ),
    (
        "DO", None,
        {"en": "Dortmund", "de": "Dortmund", "ru": "Дортмунд", "uk": "Дортмунд"},
        {
            "en": "North Rhine-Westphalia",
            "de": "Nordrhein-Westfalen",
            "ru": "Северный Рейн-Вестфалия",
            "uk": "Північний Рейн-Вестфалія",
        },
    ),
    (
        "E", None,
        {"en": "Essen", "de": "Essen", "ru": "Эссен", "uk": "Ессен"},
        {
            "en": "North Rhine-Westphalia",
            "de": "Nordrhein-Westfalen",
            "ru": "Северный Рейн-Вестфалия",
            "uk": "Північний Рейн-Вестфалія",
        },
    ),
    (
        "HO", None,
        {"en": "Hof", "de": "Hof", "ru": "Хоф", "uk": "Хоф"},
        {"en": "Bavaria", "de": "Bayern", "ru": "Бавария", "uk": "Баварія"},
    ),
    (
        "BA", None,
        {"en": "Bamberg", "de": "Bamberg", "ru": "Бамберг", "uk": "Бамберг"},
        {"en": "Bavaria", "de": "Bayern", "ru": "Бавария", "uk": "Баварія"},
    ),
    (
        "WU", None,
        {"en": "Würzburg", "de": "Würzburg", "ru": "Вюрцбург", "uk": "Вюрцбург"},
        {"en": "Bavaria", "de": "Bayern", "ru": "Бавария", "uk": "Баварія"},
    ),
    (
        "FR", None,
        {"en": "Freiburg im Breisgau", "de": "Freiburg im Breisgau", "ru": "Фрайбург-им-Брайсгау", "uk": "Фрайбург-ім-Брайсґау"},
        {"en": "Baden-Württemberg", "de": "Baden-Württemberg", "ru": "Баден-Вюртемберг", "uk": "Баден-Вюртемберг"},
    ),
    (
        "KA", None,
        {"en": "Karlsruhe", "de": "Karlsruhe", "ru": "Карлсруэ", "uk": "Карлсруе"},
        {"en": "Baden-Württemberg", "de": "Baden-Württemberg", "ru": "Баден-Вюртемберг", "uk": "Баден-Вюртемберг"},
    ),
    (
        "MA", None,
        {"en": "Mannheim", "de": "Mannheim", "ru": "Мангейм", "uk": "Мангейм"},
        {"en": "Baden-Württemberg", "de": "Baden-Württemberg", "ru": "Баден-Вюртемберг", "uk": "Баден-Вюртемберг"},
    ),
    (
        "HD", None,
        {"en": "Heidelberg", "de": "Heidelberg", "ru": "Гейдельберг", "uk": "Гейдельберг"},
        {"en": "Baden-Württemberg", "de": "Baden-Württemberg", "ru": "Баден-Вюртемберг", "uk": "Баден-Вюртемберг"},
    ),
    (
        "BI", None,
        {"en": "Bielefeld", "de": "Bielefeld", "ru": "Билефельд", "uk": "Білефельд"},
        {
            "en": "North Rhine-Westphalia",
            "de": "Nordrhein-Westfalen",
            "ru": "Северный Рейн-Вестфалия",
            "uk": "Північний Рейн-Вестфалія",
        },
    ),
    (
        "GE", None,
        {"en": "Gelsenkirchen", "de": "Gelsenkirchen", "ru": "Гельзенкирхен", "uk": "Гельзенкірхен"},
        {
            "en": "North Rhine-Westphalia",
            "de": "Nordrhein-Westfalen",
            "ru": "Северный Рейн-Вестфалия",
            "uk": "Північний Рейн-Вестфалія",
        },
    ),
    (
        "MS", None,
        {"en": "Münster", "de": "Münster", "ru": "Мюнстер", "uk": "Мюнстер"},
        {
            "en": "North Rhine-Westphalia",
            "de": "Nordrhein-Westfalen",
            "ru": "Северный Рейн-Вестфалия",
            "uk": "Північний Рейн-Вестфалія",
        },
    ),
    (
        "OB", None,
        {"en": "Oberhausen", "de": "Oberhausen", "ru": "Оберхаузен", "uk": "Оберхаузен"},
        {
            "en": "North Rhine-Westphalia",
            "de": "Nordrhein-Westfalen",
            "ru": "Северный Рейн-Вестфалия",
            "uk": "Північний Рейн-Вестфалія",
        },
    ),
    (
        "BO", None,
        {"en": "Bochum", "de": "Bochum", "ru": "Бохум", "uk": "Бохум"},
        {
            "en": "North Rhine-Westphalia",
            "de": "Nordrhein-Westfalen",
            "ru": "Северный Рейн-Вестфалия",
            "uk": "Північний Рейн-Вестфалія",
        },
    ),
    (
        "MG", None,
        {"en": "Mönchengladbach", "de": "Mönchengladbach", "ru": "Мёнхенгладбах", "uk": "Мьонхенгладбах"},
        {
            "en": "North Rhine-Westphalia",
            "de": "Nordrhein-Westfalen",
            "ru": "Северный Рейн-Вестфалия",
            "uk": "Північний Рейн-Вестфалія",
        },
    ),
    (
        "SB", None,
        {"en": "Saarbrücken", "de": "Saarbrücken", "ru": "Саарбрюккен", "uk": "Саарбрюккен"},
        {"en": "Saarland", "de": "Saarland", "ru": "Саар", "uk": "Саар"},
    ),
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
    """Insert the DE country record and its translations.

    Args:
        conn: An open SQLite connection (foreign keys must be on).
    """
    country_id = _get_or_insert_country(conn)
    _insert_country_translations(conn, country_id)
    logger.info("Seeded country DE (id=%d)", country_id)


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
    wiki_url: str | None,
    name_trans: dict[str, str],
    group_trans: dict[str, str],
) -> None:
    """Insert one region and its translations."""
    conn.execute(
        "INSERT OR IGNORE INTO regions (country_id, plate_code, wikipedia_url) VALUES (?, ?, ?)",
        (country_id, plate_code.upper(), wiki_url),
    )
    row = conn.execute(
        "SELECT id FROM regions WHERE country_id = ? AND plate_code = ?",
        (country_id, plate_code.upper()),
    ).fetchone()
    _insert_region_translations(conn, row[0], name_trans, group_trans)


def seed_regions(conn: sqlite3.Connection) -> None:
    """Insert all DE region records and their translations.

    Args:
        conn: An open SQLite connection.
    """
    row = conn.execute("SELECT id FROM countries WHERE code = ?", (COUNTRY_CODE,)).fetchone()
    country_id: int = row[0]
    for plate_code, wiki_url, name_trans, group_trans in _REGIONS:
        _seed_single_region(conn, country_id, plate_code, wiki_url, name_trans, group_trans)
    logger.info("Seeded %d DE regions", len(_REGIONS))


def run(conn: sqlite3.Connection) -> None:
    """Run the full Germany seed: country + all regions.

    Args:
        conn: An open SQLite connection.
    """
    seed_country(conn)
    seed_regions(conn)


def main() -> None:
    """Open the production DB, seed Germany, and close."""
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s — %(message)s")
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    try:
        run(conn)
        conn.commit()
        logger.info("Germany seed complete")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
