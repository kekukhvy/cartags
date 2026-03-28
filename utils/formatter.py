"""Pure formatting functions for CarTags bot responses.

No I/O, no DB, no Telegram API — only text transformations.
"""

from db.database import CountryResult, RegionResult


def format_region_response(result: RegionResult, lang: str = "en") -> str:
    """Format a single region lookup result as a Telegram HTML message.

    Args:
        result: The region data to format.
        lang:   The UI language (affects label text via caller — kept for signature parity).

    Returns:
        An HTML-formatted string ready to send via reply_text(parse_mode="HTML").
    """
    group_part = f"\n{result.region_group}" if result.region_group else ""
    return (
        f"{result.emoji} <b>{result.country_name}</b>\n"
        f"<code>{result.plate_code}</code> — {result.name_local}"
        f"{group_part}"
    )


def format_ambiguous_response(results: list[RegionResult], header: str) -> str:
    """Format multiple country matches into a disambiguation message.

    Args:
        results: List of RegionResult objects matching the plate code.
        header:  Translated header line (e.g. "Found in multiple countries:").

    Returns:
        A plain-text message listing each match.
    """
    lines = [header]
    for r in results:
        lines.append(f"{r.emoji} {r.country_code} — {r.name_local}")
    return "\n".join(lines)


def format_country_list(countries: list[CountryResult], header: str) -> str:
    """Format the list of supported countries.

    Args:
        countries: All CountryResult rows.
        header:    Translated header line.

    Returns:
        A plain-text list of countries.
    """
    lines = [header]
    for c in countries:
        lines.append(f"{c.emoji} <b>{c.code}</b> — {c.name}")
    return "\n".join(lines)


def format_region_list_page(
    results: list[RegionResult],
    header: str,
    page: int,
    total_pages: int,
    page_label: str,
) -> str:
    """Format one page of a country's region list, grouping all plate codes per region.

    Args:
        results:     Grouped regions for this page (one RegionResult per region).
        header:      Translated country header line.
        page:        Current 1-based page number.
        total_pages: Total number of pages.
        page_label:  Translated "Page X/Y" string.

    Returns:
        An HTML-formatted message string.
    """
    lines = [header]
    for r in results:
        codes = r.all_plate_codes if r.all_plate_codes else (r.plate_code,)
        codes_str = ", ".join(f"<code>{c}</code>" for c in codes)
        group_part = f" ({r.region_group})" if r.region_group else ""
        lines.append(f"{codes_str} — {r.name_local}{group_part}")
    if total_pages > 1:
        lines.append(f"\n{page_label}")
    return "\n".join(lines)
