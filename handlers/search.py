"""Handlers for /plate command and free-form text input."""

import logging

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from constants import MAX_AMBIGUOUS_RESULTS, CallbackPrefix
from db.database import RegionResult, find_by_plate_only, find_region
from handlers import resolve_user_lang
from utils.formatter import format_ambiguous_response, format_region_response
from utils.locale import t
from utils.search_parser import SearchMode, parse_search_query

logger = logging.getLogger(__name__)


def _map_button(result: RegionResult) -> InlineKeyboardMarkup | None:
    """Return a 'Show on map' inline keyboard if coordinates are available.

    Args:
        result: Region result that may contain latitude/longitude.

    Returns:
        InlineKeyboardMarkup with the map button, or None if no coords.
    """
    if result.latitude is None or result.longitude is None:
        return None
    callback = f"{CallbackPrefix.MAP_REGION}:{result.country_code}:{result.plate_code}"
    button = InlineKeyboardButton(text="📍 Show on map", callback_data=callback)
    return InlineKeyboardMarkup([[button]])


async def _reply_single_result(update: Update, country: str, plate: str, lang: str) -> None:
    """Look up and send a single country+plate result.

    Args:
        update:  Incoming Telegram update.
        country: ISO country code.
        plate:   Plate code to look up.
        lang:    UI language code.
    """
    result = find_region(country, plate, lang=lang)
    if result is None:
        msg = t("not_found", lang, plate=plate, country=country)
        await update.message.reply_text(msg, parse_mode="HTML")
        return
    markup = _map_button(result)
    await update.message.reply_text(
        format_region_response(result),
        parse_mode="HTML",
        reply_markup=markup,
    )


async def map_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle 'Show on map' button — send a Telegram venue for the region.

    Args:
        update:  Incoming Telegram update with callback query.
        context: Handler context (unused).
    """
    query = update.callback_query
    _, country_code, plate_code = query.data.split(":", 2)
    lang = resolve_user_lang(update)
    result = find_region(country_code, plate_code, lang=lang)
    if result is None or result.latitude is None or result.longitude is None:
        await query.answer(t("map_unavailable", lang), show_alert=True)
        return
    await query.answer()
    title = result.name_local
    address = f"{result.country_name} · {result.plate_code}"
    await query.message.reply_venue(
        latitude=result.latitude,
        longitude=result.longitude,
        title=title,
        address=address,
    )


async def _reply_ambiguous(update: Update, plate: str, lang: str) -> None:
    """Search all countries for plate and reply with disambiguation.

    Args:
        update: Incoming Telegram update.
        plate:  Plate code to search.
        lang:   UI language code.
    """
    results = find_by_plate_only(plate, lang=lang)
    if not results:
        msg = t("not_found_global", lang, plate=plate)
        await update.message.reply_text(msg, parse_mode="HTML")
        return
    if len(results) == 1:
        markup = _map_button(results[0])
        await update.message.reply_text(
            format_region_response(results[0]),
            parse_mode="HTML",
            reply_markup=markup,
        )
        return
    trimmed = results[:MAX_AMBIGUOUS_RESULTS]
    header = t("ambiguous_header", lang)
    text = format_ambiguous_response(trimmed, header)
    buttons = _build_ambiguous_buttons(trimmed, plate)
    await update.message.reply_text(text, reply_markup=buttons)


def _build_ambiguous_buttons(
    results: list[RegionResult],
    plate: str,
) -> InlineKeyboardMarkup:
    """Build inline keyboard for disambiguation — one button per country.

    Args:
        results: RegionResult list (already trimmed).
        plate:   The searched plate code.

    Returns:
        InlineKeyboardMarkup with one button per country.
    """
    buttons = [
        [InlineKeyboardButton(
            text=f"📍 {r.emoji} {r.country_code} — Show on map",
            callback_data=f"{CallbackPrefix.MAP_REGION}:{r.country_code}:{r.plate_code}",
        )]
        for r in results
    ]
    return InlineKeyboardMarkup(buttons)


async def plate_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /plate <country> <code> command."""
    lang = resolve_user_lang(update)
    if not context.args or len(context.args) < 2:
        await update.message.reply_text(t("plate_usage", lang), parse_mode="HTML")
        return
    country = context.args[0].upper()
    plate = context.args[1].upper()
    logger.info("/plate country=%s plate=%s user=%s", country, plate,
                update.effective_user and update.effective_user.id)
    await _reply_single_result(update, country, plate, lang)


async def search_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle free-form text input — auto-detect format and route."""
    text = update.message.text or ""
    lang = resolve_user_lang(update)
    query = parse_search_query(text)
    logger.info("free text='%s' mode=%s user=%s", text, query.mode,
                update.effective_user and update.effective_user.id)
    if query.mode == SearchMode.BY_PLATE_AND_COUNTRY:
        await _reply_single_result(update, query.country, query.plate, lang)
    elif query.mode == SearchMode.BY_PLATE_ONLY:
        await _reply_ambiguous(update, query.plate, lang)
    else:
        await update.message.reply_text(t("unknown_input", lang), parse_mode="HTML")
