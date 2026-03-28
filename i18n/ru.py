"""Russian UI strings."""

STRINGS: dict[str, str] = {
    "start_greeting": (
        "Привет! Я CarTags — справочник автомобильных номеров.\n\n"
        "Просто напиши код с номерного знака:\n"
        "• DE M → Мюнхен, Германия\n"
        "• AT W → Вена, Австрия\n"
        "• UA AA → Киев, Украина\n\n"
        "/list — все поддерживаемые страны\n"
        "/help — подробная справка"
    ),
    "help_text": (
        "Отправь код номерного знака:\n"
        "• Только код: <code>M</code>\n"
        "• С кодом страны: <code>DE M</code>\n"
        "• Все регионы: /country DE\n\n"
        "Команды:\n"
        "/plate DE M — найти регион по номеру\n"
        "/country DE — все регионы Германии\n"
        "/list — поддерживаемые страны\n"
        "/language — сменить язык"
    ),
    "about_text": (
        "CarTags — справочник регионов по автономерам.\n\n"
        "Поддерживаются: DE, AT, UA (скоро больше).\n"
        "Используй /language для смены языка."
    ),
    "not_found": "Код <b>{plate}</b> не найден для {country}.\nСмотри все коды: /country {country}",
    "not_found_global": "Код <b>{plate}</b> не найден ни в одной стране.",
    "ambiguous_header": "Нашёл в нескольких странах:",
    "ambiguous_hint": "Уточни: /plate {country} {plate}",
    "list_header": "Поддерживаемые страны:",
    "country_header": "{emoji} {country} — коды регионов:",
    "country_not_found": "Страна <b>{country}</b> не найдена.",
    "page_info": "Страница {page}/{total}",
    "plate_usage": "Использование: /plate &lt;страна&gt; &lt;код&gt;\nПример: /plate DE M",
    "country_usage": "Использование: /country &lt;код&gt;\nПример: /country DE",
    "language_prompt": "Выбери язык:",
    "language_set": "Язык установлен: Русский.",
    "unknown_input": "Не понял. Попробуй: <code>DE M</code> или /help",
    "nav_list": "🌍 Страны",
    "nav_help": "❓ Помощь",
    "nav_language": "🌐 Язык",
    "nav_browse_country": "📋 Все коды {country}",
}
