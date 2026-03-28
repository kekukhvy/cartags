"""Handler for /language command and language selection callback."""

import logging

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from constants import CallbackPrefix, Lang
from db.database import set_user_lang
from handlers import resolve_user_lang
from utils.locale import t

logger = logging.getLogger(__name__)

_LANG_LABELS: dict[str, str] = {
    Lang.EN: "🇬🇧 English",
    Lang.DE: "🇩🇪 Deutsch",
    Lang.UK: "🇺🇦 Українська",
    Lang.RU: "🇷🇺 Русский",
}


def _build_language_keyboard() -> InlineKeyboardMarkup:
    """Build inline keyboard with one button per supported language.

    Returns:
        InlineKeyboardMarkup with language selection buttons.
    """
    prefix = CallbackPrefix.SET_LANG
    buttons = [
        [InlineKeyboardButton(label, callback_data=f"{prefix}:{lang}")]
        for lang, label in _LANG_LABELS.items()
    ]
    return InlineKeyboardMarkup(buttons)


async def language_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /language — show language selection keyboard."""
    lang = resolve_user_lang(update)
    text = t("language_prompt", lang)
    await update.message.reply_text(text, reply_markup=_build_language_keyboard())


async def set_language_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle language selection callback — persist and confirm."""
    query = update.callback_query
    await query.answer()
    parts = query.data.split(":")
    if len(parts) != 2:
        return
    _, chosen_lang = parts
    user = update.effective_user
    if user is None:
        return
    set_user_lang(user.id, chosen_lang)
    logger.info("user=%d set lang=%s", user.id, chosen_lang)
    confirmation = t("language_set", chosen_lang)
    await query.edit_message_text(confirmation)
