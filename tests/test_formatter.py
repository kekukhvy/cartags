"""Tests for utils/formatter.py — response formatting pure functions.

All functions are pure (no I/O, no DB), so no fixtures are needed.
"""

from dataclasses import dataclass


# ---------------------------------------------------------------------------
# Inline dataclass — mirrors db/database.py until it is created.
# Replace with: from db.database import RegionResult
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class RegionResult:
    plate_code: str
    name_local: str
    name_ru: str | None
    region_name: str | None
    country_code: str
    country_name: str
    emoji: str


# ---------------------------------------------------------------------------
# Inline formatter — mirrors utils/formatter.py until it is created.
# Replace with: from utils.formatter import format_region_response, format_ambiguous_response
# ---------------------------------------------------------------------------

def format_region_response(result: RegionResult) -> str:
    """Format a single region lookup result as a Telegram message."""
    ru_part = f" ({result.name_ru})" if result.name_ru else ""
    region_part = f"\nРегион: {result.region_name}" if result.region_name else ""
    return (
        f"{result.emoji} {result.country_name}\n"
        f"{result.plate_code} — {result.name_local}{ru_part}"
        f"{region_part}"
    )


def format_ambiguous_response(results: list[RegionResult]) -> str:
    """Format multiple matches for the same plate code into a disambiguation message."""
    lines = ["Нашел несколько совпадений:"]
    for r in results:
        ru_part = f" ({r.name_ru})" if r.name_ru else ""
        lines.append(f"{r.emoji} {r.country_code} — {r.name_local}{ru_part}")
    return "\n".join(lines)


def format_not_found_response(plate_code: str, country_code: str) -> str:
    """Format a not-found message for a specific country + plate search."""
    return (
        f"Код {plate_code} не найден для {country_code}.\n"
        f"Посмотри все коды: /country {country_code}"
    )


# ---------------------------------------------------------------------------
# Tests — format_region_response
# ---------------------------------------------------------------------------

def test_format_region_response_includes_emoji_and_country() -> None:
    """Response includes the country emoji and name."""
    result = RegionResult("M", "München", "Мюнхен", "Bayern", "DE", "Германия", "🇩🇪")
    text = format_region_response(result)
    assert "🇩🇪" in text
    assert "Германия" in text


def test_format_region_response_includes_plate_and_local_name() -> None:
    """Response includes the plate code and local city name."""
    result = RegionResult("M", "München", "Мюнхен", "Bayern", "DE", "Германия", "🇩🇪")
    text = format_region_response(result)
    assert "M" in text
    assert "München" in text


def test_format_region_response_includes_russian_name_when_present() -> None:
    """Russian name is included in parentheses when provided."""
    result = RegionResult("M", "München", "Мюнхен", "Bayern", "DE", "Германия", "🇩🇪")
    text = format_region_response(result)
    assert "Мюнхен" in text


def test_format_region_response_omits_russian_name_when_none() -> None:
    """No parenthetical when name_ru is None."""
    result = RegionResult("M", "Mistelbach", None, "Niederösterreich", "AT", "Австрия", "🇦🇹")
    text = format_region_response(result)
    assert "(" not in text


def test_format_region_response_includes_region_name() -> None:
    """Region name (state/oblast) is included when present."""
    result = RegionResult("M", "München", "Мюнхен", "Bayern", "DE", "Германия", "🇩🇪")
    text = format_region_response(result)
    assert "Bayern" in text


def test_format_region_response_omits_region_line_when_none() -> None:
    """No region line when region_name is None."""
    result = RegionResult("AA", "Kyiv", "Київ", None, "UA", "Украина", "🇺🇦")
    text = format_region_response(result)
    assert "Регион" not in text


# ---------------------------------------------------------------------------
# Tests — format_ambiguous_response
# ---------------------------------------------------------------------------

def test_format_ambiguous_response_includes_all_countries() -> None:
    """Each matching country appears in the ambiguous response."""
    results = [
        RegionResult("M", "München", "Мюнхен", "Bayern", "DE", "Германия", "🇩🇪"),
        RegionResult("M", "Mistelbach", None, "Niederösterreich", "AT", "Австрия", "🇦🇹"),
    ]
    text = format_ambiguous_response(results)
    assert "DE" in text
    assert "AT" in text


def test_format_ambiguous_response_has_header_line() -> None:
    """Response starts with a disambiguation header."""
    results = [
        RegionResult("M", "München", "Мюнхен", "Bayern", "DE", "Германия", "🇩🇪"),
    ]
    text = format_ambiguous_response(results)
    assert text.startswith("Нашел несколько совпадений")


def test_format_ambiguous_response_includes_emojis() -> None:
    """Country emojis appear in the ambiguous response."""
    results = [
        RegionResult("M", "München", "Мюнхен", "Bayern", "DE", "Германия", "🇩🇪"),
        RegionResult("M", "Mistelbach", None, "Niederösterreich", "AT", "Австрия", "🇦🇹"),
    ]
    text = format_ambiguous_response(results)
    assert "🇩🇪" in text
    assert "🇦🇹" in text


# ---------------------------------------------------------------------------
# Tests — format_not_found_response
# ---------------------------------------------------------------------------

def test_format_not_found_response_includes_plate_and_country() -> None:
    """Not-found message mentions the searched plate and country."""
    text = format_not_found_response("XYZ", "DE")
    assert "XYZ" in text
    assert "DE" in text


def test_format_not_found_response_includes_country_command_hint() -> None:
    """Not-found message includes a /country hint for the user."""
    text = format_not_found_response("XYZ", "DE")
    assert "/country DE" in text
