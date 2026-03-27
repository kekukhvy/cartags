"""Tests for db/database.py query functions.

All tests run against the in-memory DB fixture from conftest.py.
Functions under test accept an explicit `conn` parameter so the
production module can default to DB_PATH while tests inject in-memory.
"""

import sqlite3

import pytest

from tests.conftest import seed_test_data, init_schema


# ---------------------------------------------------------------------------
# Helpers — inline query implementations mirroring db/database.py signatures.
# These will be replaced by imports once db/database.py is wired end-to-end.
# ---------------------------------------------------------------------------

_REGION_JOIN_SQL = """
SELECT r.plate_code, c.code AS country_code, c.emoji,
       rname.value  AS name_local,
       rgroup.value AS region_group,
       cname.value  AS country_name
FROM regions r
JOIN countries c ON c.id = r.country_id
LEFT JOIN translations rname
       ON rname.entity_type = 'region'
      AND rname.entity_id   = r.id
      AND rname.language_code = 'en'
      AND rname.field       = 'name'
LEFT JOIN translations rgroup
       ON rgroup.entity_type = 'region'
      AND rgroup.entity_id   = r.id
      AND rgroup.language_code = 'en'
      AND rgroup.field      = 'region_group'
LEFT JOIN translations cname
       ON cname.entity_type = 'country'
      AND cname.entity_id   = c.id
      AND cname.language_code = 'en'
      AND cname.field       = 'name'
"""


def find_by_code(
    country_code: str,
    plate_code: str,
    conn: sqlite3.Connection,
) -> sqlite3.Row | None:
    """Return region row for a given country + plate, or None."""
    return conn.execute(
        _REGION_JOIN_SQL + """
        WHERE UPPER(c.code) = UPPER(?)
          AND UPPER(r.plate_code) = UPPER(?)
        """,
        (country_code, plate_code),
    ).fetchone()


def find_by_plate_only(
    plate_code: str,
    conn: sqlite3.Connection,
) -> list[sqlite3.Row]:
    """Return all regions matching a plate code across all countries."""
    return conn.execute(
        _REGION_JOIN_SQL + "WHERE UPPER(r.plate_code) = UPPER(?)",
        (plate_code,),
    ).fetchall()


def get_country_regions(
    country_code: str,
    conn: sqlite3.Connection,
    offset: int = 0,
    limit: int = 20,
) -> list[sqlite3.Row]:
    """Return paginated regions for a country ordered by plate_code."""
    return conn.execute(
        _REGION_JOIN_SQL + """
        WHERE UPPER(c.code) = UPPER(?)
        ORDER BY r.plate_code
        LIMIT ? OFFSET ?
        """,
        (country_code, limit, offset),
    ).fetchall()


# ---------------------------------------------------------------------------
# find_by_code
# ---------------------------------------------------------------------------

def test_find_by_code_returns_region_for_valid_input(db: sqlite3.Connection) -> None:
    """find_by_code returns the correct row when country and plate match."""
    result = find_by_code("DE", "M", conn=db)
    assert result is not None
    assert result["name_local"] == "Munich"
    assert result["emoji"] == "🇩🇪"


def test_find_by_code_is_case_insensitive(db: sqlite3.Connection) -> None:
    """find_by_code matches regardless of input casing."""
    lower = find_by_code("de", "m", conn=db)
    upper = find_by_code("DE", "M", conn=db)
    assert lower is not None
    assert upper is not None
    assert lower["name_local"] == upper["name_local"]


def test_find_by_code_returns_none_for_unknown_plate(db: sqlite3.Connection) -> None:
    """find_by_code returns None when plate code does not exist for country."""
    result = find_by_code("DE", "XYZ", conn=db)
    assert result is None


def test_find_by_code_returns_none_for_unknown_country(db: sqlite3.Connection) -> None:
    """find_by_code returns None when country code does not exist."""
    result = find_by_code("XX", "M", conn=db)
    assert result is None


def test_find_by_code_returns_correct_country_for_shared_plate(db: sqlite3.Connection) -> None:
    """find_by_code returns the right country when same plate exists in multiple countries."""
    de_result = find_by_code("DE", "M", conn=db)
    at_result = find_by_code("AT", "M", conn=db)
    assert de_result is not None
    assert at_result is not None
    assert de_result["name_local"] == "Munich"
    assert at_result["name_local"] == "Mistelbach"


# ---------------------------------------------------------------------------
# find_by_plate_only
# ---------------------------------------------------------------------------

def test_find_by_plate_only_returns_all_matches(db: sqlite3.Connection) -> None:
    """find_by_plate_only returns rows from every country that has the plate code."""
    results = find_by_plate_only("M", conn=db)
    country_codes = {row["country_code"] for row in results}
    assert "DE" in country_codes
    assert "AT" in country_codes


def test_find_by_plate_only_returns_empty_for_unknown_plate(db: sqlite3.Connection) -> None:
    """find_by_plate_only returns an empty list when no match exists."""
    results = find_by_plate_only("ZZZ", conn=db)
    assert results == []


def test_find_by_plate_only_is_case_insensitive(db: sqlite3.Connection) -> None:
    """find_by_plate_only matches lowercase input."""
    results = find_by_plate_only("hh", conn=db)
    assert len(results) == 1
    assert results[0]["name_local"] == "Hamburg"


def test_find_by_plate_only_unique_plate_returns_single_row(db: sqlite3.Connection) -> None:
    """find_by_plate_only returns exactly one row for a plate unique to one country."""
    results = find_by_plate_only("AA", conn=db)
    assert len(results) == 1
    assert results[0]["country_code"] == "UA"


# ---------------------------------------------------------------------------
# get_country_regions
# ---------------------------------------------------------------------------

def test_get_country_regions_returns_regions_for_valid_country(db: sqlite3.Connection) -> None:
    """get_country_regions returns all seeded regions for DE."""
    results = get_country_regions("DE", conn=db)
    assert len(results) == 4


def test_get_country_regions_returns_empty_for_unknown_country(db: sqlite3.Connection) -> None:
    """get_country_regions returns empty list for a country not in DB."""
    results = get_country_regions("XX", conn=db)
    assert results == []


def test_get_country_regions_is_ordered_by_plate_code(db: sqlite3.Connection) -> None:
    """get_country_regions returns rows sorted alphabetically by plate_code."""
    results = get_country_regions("DE", conn=db)
    codes = [row["plate_code"] for row in results]
    assert codes == sorted(codes)


def test_get_country_regions_pagination_offset(db: sqlite3.Connection) -> None:
    """get_country_regions offset skips the correct number of rows."""
    all_results = get_country_regions("DE", conn=db, limit=100)
    page2 = get_country_regions("DE", conn=db, offset=2, limit=100)
    assert len(page2) == len(all_results) - 2
    assert page2[0]["plate_code"] == all_results[2]["plate_code"]


def test_get_country_regions_pagination_limit(db: sqlite3.Connection) -> None:
    """get_country_regions limit caps the number of returned rows."""
    results = get_country_regions("DE", conn=db, limit=2)
    assert len(results) == 2


def test_get_country_regions_is_case_insensitive(db: sqlite3.Connection) -> None:
    """get_country_regions matches lowercase country code."""
    results = get_country_regions("de", conn=db)
    assert len(results) == 4
