"""Language resolution and i18n string lookup for CarTags.

Pure utility — no I/O, no Telegram API, no DB calls.
"""

import logging

from constants import FALLBACK_LANG, SUPPORTED_LANGS, resolve_lang

logger = logging.getLogger(__name__)

# Lazy-loaded per-language string dicts
_CACHE: dict[str, dict[str, str]] = {}


def _load_strings(lang: str) -> dict[str, str]:
    """Import and return the STRINGS dict for the given language module.

    Args:
        lang: A supported language key (e.g. "en", "de").

    Returns:
        The STRINGS mapping for that language.
    """
    if lang not in _CACHE:
        module = __import__(f"i18n.{lang}", fromlist=["STRINGS"])
        _CACHE[lang] = module.STRINGS
    return _CACHE[lang]


def get_lang(language_code: str | None) -> str:
    """Resolve a Telegram language_code to a supported lang key.

    Args:
        language_code: Raw Telegram language_code (may be None or e.g. "de-AT").

    Returns:
        A supported language key string.
    """
    return resolve_lang(language_code)


def t(key: str, lang: str, **kwargs: str) -> str:
    """Return the translated string for key in lang, with optional substitutions.

    Falls back to FALLBACK_LANG if key is missing in the requested language.

    Args:
        key:    The i18n string key (e.g. "not_found").
        lang:   The target language code.
        **kwargs: Named substitution values for str.format().

    Returns:
        The translated and formatted string.
    """
    if lang not in SUPPORTED_LANGS:
        lang = FALLBACK_LANG
    strings = _load_strings(lang)
    template = strings.get(key)
    if template is None:
        logger.warning("Missing i18n key '%s' for lang '%s', falling back to en", key, lang)
        template = _load_strings(FALLBACK_LANG).get(key, key)
    return template.format(**kwargs) if kwargs else template
