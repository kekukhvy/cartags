"""Tests for utils/search_parser.py — parse_search_query().

Covers all input formats the bot must handle from free-form user text.
"""

from utils.search_parser import SearchMode, SearchQuery, parse_search_query


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_parse_country_and_plate() -> None:
    """'DE M' parses to BY_PLATE_AND_COUNTRY with correct fields."""
    result = parse_search_query("DE M")
    assert result.mode == SearchMode.BY_PLATE_AND_COUNTRY
    assert result.country == "DE"
    assert result.plate == "M"


def test_parse_plate_only() -> None:
    """Single token parses to BY_PLATE_ONLY with no country."""
    result = parse_search_query("M")
    assert result.mode == SearchMode.BY_PLATE_ONLY
    assert result.country is None
    assert result.plate == "M"


def test_parse_empty_string_returns_unknown() -> None:
    """Empty input returns UNKNOWN mode."""
    result = parse_search_query("")
    assert result.mode == SearchMode.UNKNOWN
    assert result.country is None
    assert result.plate is None


def test_parse_normalizes_to_uppercase() -> None:
    """Lowercase input is normalized to uppercase."""
    result = parse_search_query("de m")
    assert result.country == "DE"
    assert result.plate == "M"


def test_parse_strips_leading_trailing_whitespace() -> None:
    """Leading/trailing whitespace is stripped before parsing."""
    result = parse_search_query("  DE M  ")
    assert result.mode == SearchMode.BY_PLATE_AND_COUNTRY
    assert result.country == "DE"
    assert result.plate == "M"


def test_parse_three_tokens_returns_unknown() -> None:
    """Input with three or more tokens returns UNKNOWN — ambiguous format."""
    result = parse_search_query("DE M extra")
    assert result.mode == SearchMode.UNKNOWN


def test_parse_at_w() -> None:
    """'AT W' parses correctly — Austria Wien example from spec."""
    result = parse_search_query("AT W")
    assert result.mode == SearchMode.BY_PLATE_AND_COUNTRY
    assert result.country == "AT"
    assert result.plate == "W"


def test_parse_ua_aa() -> None:
    """'UA AA' parses correctly — Ukraine Kyiv example from spec."""
    result = parse_search_query("UA AA")
    assert result.country == "UA"
    assert result.plate == "AA"
