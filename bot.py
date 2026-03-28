"""CarTags bot entry point.

Wires all handlers and starts long-polling. Zero business logic here.
"""

import logging
import os
from pathlib import Path

from dotenv import load_dotenv
from telegram import BotCommand as TgBotCommand
from telegram.ext import Application, ApplicationBuilder, CallbackQueryHandler, CommandHandler, MessageHandler, filters

from constants import BotCommand, CallbackPrefix
from handlers.country import country_handler, country_page_callback, list_handler, select_country_callback
from handlers.language import language_handler, set_language_callback
from handlers.search import plate_handler, search_handler
from handlers.start import about_handler, help_handler, start_handler

load_dotenv(Path(__file__).parent / ".env")

logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s %(levelname)s %(name)s — %(message)s",
)
logger = logging.getLogger(__name__)


async def _post_init(app: Application) -> None:
    """Register bot commands for each supported language after startup."""
    commands: dict[str, list[TgBotCommand]] = {
        "en": [
            TgBotCommand("plate", "Look up a plate code (e.g. DE M)"),
            TgBotCommand("country", "Browse all codes for a country"),
            TgBotCommand("list", "Show all supported countries"),
            TgBotCommand("help", "How to use CarTags"),
            TgBotCommand("about", "About the app and iOS version"),
        ],
        "de": [
            TgBotCommand("plate", "Kennzeichen nachschlagen (z.B. DE M)"),
            TgBotCommand("country", "Alle Kürzel eines Landes anzeigen"),
            TgBotCommand("list", "Alle unterstützten Länder anzeigen"),
            TgBotCommand("help", "So benutzt du CarTags"),
            TgBotCommand("about", "Über die App und iOS-Version"),
        ],
        "ru": [
            TgBotCommand("plate", "Найти код номера (например DE M)"),
            TgBotCommand("country", "Все коды страны (например DE)"),
            TgBotCommand("list", "Список поддерживаемых стран"),
            TgBotCommand("help", "Как пользоваться CarTags"),
            TgBotCommand("about", "О приложении и версии для iOS"),
        ],
        "uk": [
            TgBotCommand("plate", "Знайти код номера (наприклад DE M)"),
            TgBotCommand("country", "Усі коди країни (наприклад DE)"),
            TgBotCommand("list", "Список підтримуваних країн"),
            TgBotCommand("help", "Як користуватися CarTags"),
            TgBotCommand("about", "Про застосунок та версію для iOS"),
        ],
    }
    for lang, cmds in commands.items():
        await app.bot.set_my_commands(cmds, language_code=lang)


def _build_application():
    """Build and configure the Telegram Application with all handlers.

    Returns:
        A fully configured Application instance.
    """
    token = os.getenv("BOT_TOKEN")
    if not token:
        raise RuntimeError("BOT_TOKEN environment variable is not set")
    app = ApplicationBuilder().token(token).post_init(_post_init).build()

    app.add_handler(CommandHandler(BotCommand.START, start_handler))
    app.add_handler(CommandHandler(BotCommand.HELP, help_handler))
    app.add_handler(CommandHandler(BotCommand.ABOUT, about_handler))
    app.add_handler(CommandHandler(BotCommand.PLATE, plate_handler))
    app.add_handler(CommandHandler(BotCommand.COUNTRY, country_handler))
    app.add_handler(CommandHandler(BotCommand.LIST, list_handler))
    app.add_handler(CommandHandler(BotCommand.LANGUAGE, language_handler))

    app.add_handler(CallbackQueryHandler(
        country_page_callback,
        pattern=f"^{CallbackPrefix.COUNTRY_PAGE}:",
    ))
    app.add_handler(CallbackQueryHandler(
        select_country_callback,
        pattern=f"^{CallbackPrefix.SELECT_COUNTRY}:",
    ))
    app.add_handler(CallbackQueryHandler(
        set_language_callback,
        pattern=f"^{CallbackPrefix.SET_LANG}:",
    ))

    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, search_handler))

    return app


def main() -> None:
    """Start the bot with long-polling."""
    logger.info("Starting CarTags bot")
    app = _build_application()
    app.run_polling()


if __name__ == "__main__":
    main()
