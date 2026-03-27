import sqlite3

import pytest


def init_schema(conn: sqlite3.Connection) -> None:
    """Create countries, regions, and translations tables with indexes."""
    conn.executescript("""
        CREATE TABLE countries (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            code       TEXT NOT NULL UNIQUE,
            emoji      TEXT NOT NULL,
            sort_order INTEGER NOT NULL DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE regions (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            country_id    INTEGER NOT NULL REFERENCES countries(id),
            plate_code    TEXT NOT NULL,
            wikipedia_url TEXT,
            created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(country_id, plate_code)
        );

        CREATE TABLE translations (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            entity_type   TEXT NOT NULL,
            entity_id     INTEGER NOT NULL,
            language_code TEXT NOT NULL,
            field         TEXT NOT NULL,
            value         TEXT NOT NULL,
            created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(entity_type, entity_id, language_code, field)
        );

        CREATE INDEX idx_regions_plate_code ON regions(plate_code);
        CREATE INDEX idx_regions_country_id ON regions(country_id);
        CREATE INDEX idx_translations_entity ON translations(entity_type, entity_id);
        CREATE INDEX idx_translations_lookup
            ON translations(entity_type, entity_id, language_code, field);
    """)


def _insert_country(
    conn: sqlite3.Connection,
    code: str,
    emoji: str,
    sort_order: int,
    translations: dict[str, str],
) -> int:
    """Insert a country with translations and return its id."""
    conn.execute(
        "INSERT INTO countries (code, emoji, sort_order) VALUES (?, ?, ?)",
        (code, emoji, sort_order),
    )
    country_id: int = conn.execute(
        "SELECT id FROM countries WHERE code = ?", (code,)
    ).fetchone()[0]
    for lang, name in translations.items():
        conn.execute(
            "INSERT INTO translations (entity_type, entity_id, language_code, field, value) "
            "VALUES ('country', ?, ?, 'name', ?)",
            (country_id, lang, name),
        )
    return country_id


def _insert_region(
    conn: sqlite3.Connection,
    country_id: int,
    plate_code: str,
    name_trans: dict[str, str],
    group_trans: dict[str, str],
) -> None:
    """Insert a region with name and region_group translations."""
    conn.execute(
        "INSERT INTO regions (country_id, plate_code) VALUES (?, ?)",
        (country_id, plate_code),
    )
    region_id: int = conn.execute(
        "SELECT id FROM regions WHERE country_id = ? AND plate_code = ?",
        (country_id, plate_code),
    ).fetchone()[0]
    for lang, value in name_trans.items():
        conn.execute(
            "INSERT INTO translations "
            "(entity_type, entity_id, language_code, field, value) "
            "VALUES ('region', ?, ?, 'name', ?)",
            (region_id, lang, value),
        )
    for lang, value in group_trans.items():
        conn.execute(
            "INSERT INTO translations "
            "(entity_type, entity_id, language_code, field, value) "
            "VALUES ('region', ?, ?, 'region_group', ?)",
            (region_id, lang, value),
        )


def seed_test_data(conn: sqlite3.Connection) -> None:
    """Insert minimal fixture data: DE, AT, UA with a few regions each."""
    de_id = _insert_country(
        conn, "DE", "🇩🇪", 1,
        {"en": "Germany", "de": "Deutschland", "ru": "Германия", "uk": "Німеччина"},
    )
    at_id = _insert_country(
        conn, "AT", "🇦🇹", 2,
        {"en": "Austria", "de": "Österreich", "ru": "Австрия", "uk": "Австрія"},
    )
    ua_id = _insert_country(
        conn, "UA", "🇺🇦", 3,
        {"en": "Ukraine", "de": "Ukraine", "ru": "Украина", "uk": "Україна"},
    )

    _insert_region(
        conn, de_id, "M",
        {"en": "Munich", "de": "München", "ru": "Мюнхен", "uk": "Мюнхен"},
        {"en": "Bavaria", "de": "Bayern", "ru": "Бавария", "uk": "Баварія"},
    )
    _insert_region(
        conn, de_id, "B",
        {"en": "Berlin", "de": "Berlin", "ru": "Берлин", "uk": "Берлін"},
        {"en": "Berlin", "de": "Berlin", "ru": "Берлин", "uk": "Берлін"},
    )
    _insert_region(
        conn, de_id, "BA",
        {"en": "Bamberg", "de": "Bamberg", "ru": "Бамберг", "uk": "Бамберг"},
        {"en": "Bavaria", "de": "Bayern", "ru": "Бавария", "uk": "Баварія"},
    )
    _insert_region(
        conn, de_id, "HH",
        {"en": "Hamburg", "de": "Hamburg", "ru": "Гамбург", "uk": "Гамбург"},
        {"en": "Hamburg", "de": "Hamburg", "ru": "Гамбург", "uk": "Гамбург"},
    )
    _insert_region(
        conn, at_id, "W",
        {"en": "Vienna", "de": "Wien", "ru": "Вена", "uk": "Відень"},
        {"en": "Vienna", "de": "Wien", "ru": "Вена", "uk": "Відень"},
    )
    _insert_region(
        conn, at_id, "M",
        {"en": "Mistelbach", "de": "Mistelbach", "ru": "Мистельбах", "uk": "Містельбах"},
        {"en": "Lower Austria", "de": "Niederösterreich",
         "ru": "Нижняя Австрия", "uk": "Нижня Австрія"},
    )
    _insert_region(
        conn, ua_id, "AA",
        {"en": "Kyiv", "de": "Kiew", "ru": "Киев", "uk": "Київ"},
        {"en": "Kyiv City", "de": "Stadt Kiew", "ru": "Город Киев", "uk": "Місто Київ"},
    )
    conn.commit()


@pytest.fixture
def db() -> sqlite3.Connection:
    """In-memory SQLite DB seeded with test countries and regions."""
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    init_schema(conn)
    seed_test_data(conn)
    return conn
