"""Tests for utils/formatter.py — response formatting pure functions.

All functions are pure (no I/O, no DB), so no fixtures are needed.
"""

from db.database import RegionResult
from utils.formatter import format_ambiguous_response, format_region_response


def _region(
    plate_code: str = "M",
    name_local: str = "München",
    region_group: str | None = "Bavaria",
    country_code: str = "DE",
    country_name: str = "Germany",
    emoji: str = "🇩🇪",
) -> RegionResult:
    return RegionResult(
        plate_code=plate_code,
        name_local=name_local,
        region_group=region_group,
        country_code=country_code,
        country_name=country_name,
        emoji=emoji,
    )


# ---------------------------------------------------------------------------
# Tests — format_region_response
# ---------------------------------------------------------------------------

def test_format_region_response_includes_emoji_and_country() -> None:
    """Response includes the country emoji and name."""
    text = format_region_response(_region())
    assert "🇩🇪" in text
    assert "Germany" in text


def test_format_region_response_includes_plate_and_local_name() -> None:
    """Response includes the plate code and local city name."""
    text = format_region_response(_region())
    assert "M" in text
    assert "München" in text


def test_format_region_response_includes_region_group() -> None:
    """Region group is included when present."""
    text = format_region_response(_region(region_group="Bavaria"))
    assert "Bavaria" in text


def test_format_region_response_omits_region_group_when_none() -> None:
    """No region group line when region_group is None."""
    text = format_region_response(_region(region_group=None))
    assert "Bavaria" not in text


# ---------------------------------------------------------------------------
# Tests — format_ambiguous_response
# ---------------------------------------------------------------------------

def test_format_ambiguous_response_includes_all_countries() -> None:
    """Each matching country appears in the ambiguous response."""
    results = [
        _region(country_code="DE", emoji="🇩🇪"),
        _region(plate_code="M", name_local="Mistelbach", region_group="Lower Austria",
                country_code="AT", country_name="Austria", emoji="🇦🇹"),
    ]
    text = format_ambiguous_response(results, "Found in multiple countries:")
    assert "DE" in text
    assert "AT" in text


def test_format_ambiguous_response_has_header_line() -> None:
    """Response starts with the provided header."""
    header = "Found in multiple countries:"
    text = format_ambiguous_response([_region()], header)
    assert text.startswith(header)


def test_format_ambiguous_response_includes_emojis() -> None:
    """Country emojis appear in the ambiguous response."""
    results = [
        _region(country_code="DE", emoji="🇩🇪"),
        _region(plate_code="M", name_local="Mistelbach", country_code="AT", emoji="🇦🇹"),
    ]
    text = format_ambiguous_response(results, "header")
    assert "🇩🇪" in text
    assert "🇦🇹" in text
