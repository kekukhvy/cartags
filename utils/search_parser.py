"""Parse free-form user text into structured search queries.

Pure utility — no I/O, no DB, no Telegram API.
"""

from dataclasses import dataclass
from enum import Enum, auto


class SearchMode(Enum):
    """Possible search modes derived from user input."""

    BY_PLATE_AND_COUNTRY = auto()
    BY_PLATE_ONLY = auto()
    UNKNOWN = auto()


@dataclass(frozen=True)
class SearchQuery:
    """Structured result of parsing a user's plate search input."""

    mode: SearchMode
    country: str | None
    plate: str | None


def parse_search_query(text: str) -> SearchQuery:
    """Parse raw user input into a structured SearchQuery.

    Handles formats:
      - "DE M"   → SearchQuery(BY_PLATE_AND_COUNTRY, country="DE", plate="M")
      - "M"      → SearchQuery(BY_PLATE_ONLY, country=None, plate="M")
      - ""       → SearchQuery(UNKNOWN, country=None, plate=None)
      - 3+ parts → SearchQuery(UNKNOWN, country=None, plate=None)

    Args:
        text: Raw input string from the user.

    Returns:
        A SearchQuery describing what to look up.
    """
    parts = text.strip().upper().split()
    if len(parts) == 2:
        return SearchQuery(
            mode=SearchMode.BY_PLATE_AND_COUNTRY,
            country=parts[0],
            plate=parts[1],
        )
    if len(parts) == 1:
        return SearchQuery(
            mode=SearchMode.BY_PLATE_ONLY,
            country=None,
            plate=parts[0],
        )
    return SearchQuery(mode=SearchMode.UNKNOWN, country=None, plate=None)
