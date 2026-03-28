"""Handlers for /start, /help, and /about commands."""

import logging

from telegram import Update
from telegram.ext import ContextTypes

from handlers import resolve_user_lang
from utils.locale import t

logger = logging.getLogger(__name__)


async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /start — send greeting with usage examples."""
    lang = resolve_user_lang(update)
    logger.info("start from user=%s lang=%s", update.effective_user and update.effective_user.id, lang)
    await update.message.reply_text(t("start_greeting", lang), parse_mode="HTML")


async def help_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /help — send usage instructions."""
    lang = resolve_user_lang(update)
    await update.message.reply_text(t("help_text", lang), parse_mode="HTML")


async def about_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /about — send app info."""
    lang = resolve_user_lang(update)
    await update.message.reply_text(t("about_text", lang), parse_mode="HTML")
