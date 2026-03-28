"""Handlers for /country, /list commands and country pagination callbacks."""

import logging
import math

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from constants import MAX_REGIONS_PER_PAGE, CallbackPrefix
from db.database import CountryResult, count_country_regions, get_all_countries, get_country_regions
from handlers import resolve_user_lang
from utils.formatter import format_region_list_page
from utils.locale import t

logger = logging.getLogger(__name__)


def _build_pagination_keyboard(
    country_code: str,
    page: int,
    total_pages: int,
) -> InlineKeyboardMarkup | None:
    """Build prev/next inline keyboard for paginated region lists.

    Args:
        country_code: ISO country code for callback data.
        page:         Current 1-based page number.
        total_pages:  Total number of pages.

    Returns:
        InlineKeyboardMarkup or None if only one page.
    """
    if total_pages <= 1:
        return None
    buttons: list[InlineKeyboardButton] = []
    prefix = CallbackPrefix.COUNTRY_PAGE
    if page > 1:
        buttons.append(InlineKeyboardButton(
            "← Prev",
            callback_data=f"{prefix}:{country_code}:{page - 1}",
        ))
    buttons.append(InlineKeyboardButton(
        f"{page}/{total_pages}",
        callback_data=f"{prefix}:{country_code}:{page}",
    ))
    if page < total_pages:
        buttons.append(InlineKeyboardButton(
            "Next →",
            callback_data=f"{prefix}:{country_code}:{page + 1}",
        ))
    return InlineKeyboardMarkup([buttons])


async def _send_country_page(
    update: Update,
    country_code: str,
    page: int,
    lang: str,
    edit: bool = False,
) -> None:
    """Fetch and send (or edit) one page of regions for a country.

    Args:
        update:       Incoming Telegram update.
        country_code: ISO country code.
        page:         1-based page number to display.
        lang:         UI language code.
        edit:         If True, edit the existing message instead of sending new.
    """
    total = count_country_regions(country_code)
    if total == 0:
        msg = t("country_not_found", lang, country=country_code)
        await update.effective_message.reply_text(msg, parse_mode="HTML")
        return
    total_pages = math.ceil(total / MAX_REGIONS_PER_PAGE)
    page = max(1, min(page, total_pages))
    offset = (page - 1) * MAX_REGIONS_PER_PAGE
    results = get_country_regions(country_code, lang=lang, offset=offset, limit=MAX_REGIONS_PER_PAGE)
    country_name = results[0].country_name if results else country_code
    emoji = results[0].emoji if results else ""
    header = t("country_header", lang, emoji=emoji, country=country_name)
    page_label = t("page_info", lang, page=str(page), total=str(total_pages))
    text = format_region_list_page(results, header, page, total_pages, page_label)
    keyboard = _build_pagination_keyboard(country_code, page, total_pages)
    if edit and update.callback_query:
        await update.callback_query.edit_message_text(text, reply_markup=keyboard, parse_mode="HTML")
    else:
        await update.effective_message.reply_text(text, reply_markup=keyboard, parse_mode="HTML")


async def country_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /country <code> — list regions for a country with pagination."""
    lang = resolve_user_lang(update)
    if not context.args:
        countries = get_all_countries(lang=lang)
        keyboard = _build_country_list_keyboard(countries)
        await update.message.reply_text(t("list_header", lang), reply_markup=keyboard, parse_mode="HTML")
        return
    country_code = context.args[0].upper()
    logger.info("/country code=%s user=%s", country_code,
                update.effective_user and update.effective_user.id)
    await _send_country_page(update, country_code, page=1, lang=lang)


_COUNTRY_BUTTONS_PER_ROW: int = 3


def _build_country_list_keyboard(countries: list[CountryResult]) -> InlineKeyboardMarkup:
    """Build inline keyboard with three buttons per row for country selection.

    Args:
        countries: List of CountryResult to render as buttons.

    Returns:
        InlineKeyboardMarkup with three buttons per row.
    """
    all_buttons = [
        InlineKeyboardButton(
            text=f"{c.emoji} {c.name}",
            callback_data=f"{CallbackPrefix.SELECT_COUNTRY}:{c.code}",
        )
        for c in countries
    ]
    rows = [
        all_buttons[i:i + _COUNTRY_BUTTONS_PER_ROW]
        for i in range(0, len(all_buttons), _COUNTRY_BUTTONS_PER_ROW)
    ]
    return InlineKeyboardMarkup(rows)


async def list_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /list — show inline buttons for all supported countries."""
    lang = resolve_user_lang(update)
    countries = get_all_countries(lang=lang)
    header = t("list_header", lang)
    keyboard = _build_country_list_keyboard(countries)
    await update.message.reply_text(header, reply_markup=keyboard, parse_mode="HTML")


async def select_country_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle country selection from /list inline keyboard."""
    query = update.callback_query
    await query.answer()
    parts = query.data.split(":")
    if len(parts) != 2:
        return
    _, country_code = parts
    lang = resolve_user_lang(update)
    logger.info("select country=%s user=%s", country_code,
                update.effective_user and update.effective_user.id)
    await _send_country_page(update, country_code, page=1, lang=lang, edit=False)


async def country_page_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle inline keyboard pagination callback for /country."""
    query = update.callback_query
    await query.answer()
    parts = query.data.split(":")
    if len(parts) != 3:
        return
    _, country_code, page_str = parts
    lang = resolve_user_lang(update)
    try:
        page = int(page_str)
    except ValueError:
        return
    logger.info("pagination country=%s page=%d user=%s", country_code, page,
                update.effective_user and update.effective_user.id)
    await _send_country_page(update, country_code, page=page, lang=lang, edit=True)
