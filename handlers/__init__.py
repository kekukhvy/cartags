"""Shared helpers for the handlers layer."""

from telegram import Update

from db.database import get_user_lang
from utils.locale import get_lang


def resolve_user_lang(update: Update) -> str:
    """Return the effective language for the user making this request.

    Checks the DB first; falls back to Telegram language_code.

    Args:
        update: The incoming Telegram update.

    Returns:
        A supported language code string.
    """
    user = update.effective_user
    if user is None:
        return get_lang(None)
    stored = get_user_lang(user.id)
    return stored if stored else get_lang(user.language_code)
