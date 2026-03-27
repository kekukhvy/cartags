"""Database query layer for CarTags.

All SQL lives here.  Handlers call these typed functions; no SQL
escapes into other layers.  Each public function accepts an optional
``conn`` parameter so tests can inject an in-memory connection.
"""

import logging
import sqlite3
from dataclasses import dataclass
from enum import Enum
from pathlib import Path

logger = logging.getLogger(__name__)

DB_PATH = Path(__file__).parent / "cartags.db"


# ---------------------------------------------------------------------------
# Enumerations
# ---------------------------------------------------------------------------

class LanguageCode(str, Enum):
    """Supported translation language codes."""

    EN = "en"
    DE = "de"
    RU = "ru"
    UK = "uk"


class TranslationField(str, Enum):
    """Fields stored in the translations table."""

    NAME = "name"
    REGION_GROUP = "region_group"


class EntityType(str, Enum):
    """Entity types referenced in the translations table."""

    COUNTRY = "country"
    REGION = "region"


# ---------------------------------------------------------------------------
# Result dataclasses
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class RegionResult:
    """Typed result returned by region query functions."""

    plate_code: str
    name_local: str         # name in the requested language
    region_group: str | None  # administrative group in the requested language
    country_code: str
    country_name: str       # country name in the requested language
    emoji: str


@dataclass(frozen=True)
class CountryResult:
    """Typed result returned by country query functions."""

    code: str
    name: str               # name in the requested language
    emoji: str
    sort_order: int


# ---------------------------------------------------------------------------
# Connection helpers
# ---------------------------------------------------------------------------

def get_connection(db_path: Path = DB_PATH) -> sqlite3.Connection:
    """Open a connection with row_factory and foreign keys enabled.

    Args:
        db_path: Path to the SQLite database file.

    Returns:
        A configured sqlite3.Connection.
    """
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

_FIND_REGION_SQL = """
SELECT r.id, r.plate_code, c.code AS country_code, c.emoji,
       rname.value  AS name_local,
       rgroup.value AS region_group,
       cname.value  AS country_name
FROM regions r
JOIN countries c ON c.id = r.country_id
LEFT JOIN translations rname
       ON rname.entity_type = 'region'
      AND rname.entity_id   = r.id
      AND rname.language_code = ?
      AND rname.field       = 'name'
LEFT JOIN translations rgroup
       ON rgroup.entity_type = 'region'
      AND rgroup.entity_id   = r.id
      AND rgroup.language_code = ?
      AND rgroup.field      = 'region_group'
LEFT JOIN translations cname
       ON cname.entity_type = 'country'
      AND cname.entity_id   = c.id
      AND cname.language_code = ?
      AND cname.field       = 'name'
WHERE UPPER(c.code) = UPPER(?) AND UPPER(r.plate_code) = UPPER(?)
"""

_FIND_BY_PLATE_SQL = """
SELECT r.id, r.plate_code, c.code AS country_code, c.emoji,
       rname.value  AS name_local,
       rgroup.value AS region_group,
       cname.value  AS country_name
FROM regions r
JOIN countries c ON c.id = r.country_id
LEFT JOIN translations rname
       ON rname.entity_type = 'region'
      AND rname.entity_id   = r.id
      AND rname.language_code = ?
      AND rname.field       = 'name'
LEFT JOIN translations rgroup
       ON rgroup.entity_type = 'region'
      AND rgroup.entity_id   = r.id
      AND rgroup.language_code = ?
      AND rgroup.field      = 'region_group'
LEFT JOIN translations cname
       ON cname.entity_type = 'country'
      AND cname.entity_id   = c.id
      AND cname.language_code = ?
      AND cname.field       = 'name'
WHERE UPPER(r.plate_code) = UPPER(?)
"""

_GET_COUNTRY_REGIONS_SQL = """
SELECT r.id, r.plate_code, c.code AS country_code, c.emoji,
       rname.value  AS name_local,
       rgroup.value AS region_group,
       cname.value  AS country_name
FROM regions r
JOIN countries c ON c.id = r.country_id
LEFT JOIN translations rname
       ON rname.entity_type = 'region'
      AND rname.entity_id   = r.id
      AND rname.language_code = ?
      AND rname.field       = 'name'
LEFT JOIN translations rgroup
       ON rgroup.entity_type = 'region'
      AND rgroup.entity_id   = r.id
      AND rgroup.language_code = ?
      AND rgroup.field      = 'region_group'
LEFT JOIN translations cname
       ON cname.entity_type = 'country'
      AND cname.entity_id   = c.id
      AND cname.language_code = ?
      AND cname.field       = 'name'
WHERE UPPER(c.code) = UPPER(?)
ORDER BY r.plate_code
LIMIT ? OFFSET ?
"""

_GET_ALL_COUNTRIES_SQL = """
SELECT c.code, c.emoji, c.sort_order,
       t.value AS name
FROM countries c
LEFT JOIN translations t
       ON t.entity_type   = 'country'
      AND t.entity_id     = c.id
      AND t.language_code = ?
      AND t.field         = 'name'
ORDER BY c.sort_order
"""


def _row_to_region_result(row: sqlite3.Row) -> RegionResult:
    """Map a sqlite3.Row from a region query to a RegionResult.

    Args:
        row: A row from a region SELECT with translations joined.

    Returns:
        A frozen RegionResult dataclass.
    """
    return RegionResult(
        plate_code=row["plate_code"],
        name_local=row["name_local"] or "",
        region_group=row["region_group"],
        country_code=row["country_code"],
        country_name=row["country_name"] or "",
        emoji=row["emoji"],
    )


def _resolve_conn(conn: sqlite3.Connection | None) -> sqlite3.Connection:
    """Return conn if provided, otherwise open a new connection."""
    return conn if conn is not None else get_connection()


# ---------------------------------------------------------------------------
# Public query functions
# ---------------------------------------------------------------------------

def find_region(
    country_code: str,
    plate_code: str,
    lang: str = "en",
    conn: sqlite3.Connection | None = None,
) -> RegionResult | None:
    """Return region info for a country + plate code in the requested language.

    Args:
        country_code: ISO 3166-1 alpha-2 country code (e.g. "DE").
        plate_code:   Vehicle registration plate prefix (e.g. "M").
        lang:         BCP-47 language code; falls back to "en" if not found.
        conn:         Optional connection for testing (in-memory DB).

    Returns:
        A RegionResult or None if no match is found.
    """
    connection = _resolve_conn(conn)
    row = connection.execute(
        _FIND_REGION_SQL, (lang, lang, lang, country_code, plate_code)
    ).fetchone()
    if row is None:
        return None
    result = _row_to_region_result(row)
    if result.name_local:
        return result
    return _find_region_fallback(country_code, plate_code, connection)


def _find_region_fallback(
    country_code: str,
    plate_code: str,
    conn: sqlite3.Connection,
) -> RegionResult | None:
    """Re-query with 'en' fallback when the requested language has no translation."""
    row = conn.execute(
        _FIND_REGION_SQL, ("en", "en", "en", country_code, plate_code)
    ).fetchone()
    return _row_to_region_result(row) if row else None


def find_by_plate_only(
    plate_code: str,
    lang: str = "en",
    conn: sqlite3.Connection | None = None,
) -> list[RegionResult]:
    """Search across all countries by plate code only. Returns all matches.

    Args:
        plate_code: Vehicle registration plate prefix (e.g. "M").
        lang:       BCP-47 language code.
        conn:       Optional connection for testing.

    Returns:
        A list of RegionResult (may be empty).
    """
    connection = _resolve_conn(conn)
    rows = connection.execute(
        _FIND_BY_PLATE_SQL, (lang, lang, lang, plate_code)
    ).fetchall()
    return [_row_to_region_result(r) for r in rows]


def get_country_regions(
    country_code: str,
    lang: str = "en",
    offset: int = 0,
    limit: int = 20,
    conn: sqlite3.Connection | None = None,
) -> list[RegionResult]:
    """Return paginated list of all regions for a country.

    Args:
        country_code: ISO 3166-1 alpha-2 country code.
        lang:         BCP-47 language code.
        offset:       Number of rows to skip (for pagination).
        limit:        Maximum number of rows to return.
        conn:         Optional connection for testing.

    Returns:
        A list of RegionResult ordered by plate_code.
    """
    connection = _resolve_conn(conn)
    rows = connection.execute(
        _GET_COUNTRY_REGIONS_SQL, (lang, lang, lang, country_code, limit, offset)
    ).fetchall()
    return [_row_to_region_result(r) for r in rows]


def get_all_countries(
    lang: str = "en",
    conn: sqlite3.Connection | None = None,
) -> list[CountryResult]:
    """Return all supported countries sorted by sort_order.

    Args:
        lang: BCP-47 language code.
        conn: Optional connection for testing.

    Returns:
        A list of CountryResult ordered by sort_order.
    """
    connection = _resolve_conn(conn)
    rows = connection.execute(_GET_ALL_COUNTRIES_SQL, (lang,)).fetchall()
    return [
        CountryResult(
            code=row["code"],
            name=row["name"] or row["code"],
            emoji=row["emoji"],
            sort_order=row["sort_order"],
        )
        for row in rows
    ]
