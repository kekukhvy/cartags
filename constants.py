"""Shared constants and enumerations for CarTags bot.

All magic values live here — no literals in handlers or utils.
"""

from enum import Enum, auto


# ---------------------------------------------------------------------------
# Supported languages
# ---------------------------------------------------------------------------

class Lang(str, Enum):
    """Supported UI language codes."""

    EN = "en"
    DE = "de"
    RU = "ru"
    UK = "uk"


SUPPORTED_LANGS: tuple[str, ...] = tuple(lang.value for lang in Lang)
FALLBACK_LANG: str = Lang.EN.value

# Telegram language_code prefixes that map to each supported lang
_LANG_PREFIXES: dict[str, str] = {
    "de": Lang.DE.value,
    "uk": Lang.UK.value,
    "ru": Lang.RU.value,
    "be": Lang.RU.value,
    "kk": Lang.RU.value,
}


def resolve_lang(telegram_lang: str | None) -> str:
    """Resolve a Telegram language_code string to a supported lang key.

    Args:
        telegram_lang: The language_code from Telegram (e.g. "de", "de-AT", "uk").

    Returns:
        A supported language key string, or FALLBACK_LANG if not matched.
    """
    if not telegram_lang:
        return FALLBACK_LANG
    prefix = telegram_lang.split("-")[0].lower()
    return _LANG_PREFIXES.get(prefix, FALLBACK_LANG)


# ---------------------------------------------------------------------------
# Pagination
# ---------------------------------------------------------------------------

MAX_REGIONS_PER_PAGE: int = 20
MAX_AMBIGUOUS_RESULTS: int = 5

# ---------------------------------------------------------------------------
# Callback data prefixes for inline keyboards
# ---------------------------------------------------------------------------

class CallbackPrefix(str, Enum):
    """Prefixes used to identify inline keyboard button callbacks."""

    COUNTRY_PAGE = "cp"      # country page: "cp:<country_code>:<page>"
    SET_LANG = "sl"          # set language: "sl:<lang>"
    SELECT_COUNTRY = "sc"    # select country from list: "sc:<country_code>"
    NAV = "nav"              # navigation shortcut: "nav:<action>"
    MAP_REGION = "mr"        # show region on map: "mr:<country_code>:<plate_code>"


class NavAction(str, Enum):
    """Navigation actions for nav callback buttons."""

    LIST = "list"
    HELP = "help"
    LANGUAGE = "language"
    COUNTRY = "country"      # nav:country:<code> — browse a specific country


# ---------------------------------------------------------------------------
# Bot commands
# ---------------------------------------------------------------------------

class BotCommand(str, Enum):
    """Telegram bot command names (without leading slash)."""

    START = "start"
    HELP = "help"
    ABOUT = "about"
    PLATE = "plate"
    COUNTRY = "country"
    LIST = "list"
    LANGUAGE = "language"
