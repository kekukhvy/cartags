"""Ukrainian UI strings."""

STRINGS: dict[str, str] = {
    "start_greeting": (
        "Привіт! Я CarTags — довідник автомобільних номерів.\n\n"
        "Просто напиши код з номерного знаку:\n"
        "• DE M → Мюнхен, Німеччина\n"
        "• AT W → Відень, Австрія\n"
        "• UA AA → Київ, Україна\n\n"
        "/list — всі підтримувані країни\n"
        "/help — детальна довідка"
    ),
    "help_text": (
        "Надішли код номерного знаку:\n"
        "• Тільки код: <code>M</code>\n"
        "• З кодом країни: <code>DE M</code>\n"
        "• Усі регіони: /country DE\n\n"
        "Команди:\n"
        "/plate DE M — знайти регіон за номером\n"
        "/country DE — усі регіони Німеччини\n"
        "/list — підтримувані країни\n"
        "/language — змінити мову"
    ),
    "about_text": (
        "CarTags — довідник регіонів за автономерами.\n\n"
        "Підтримуються: DE, AT, UA (скоро більше).\n"
        "Використовуй /language для зміни мови."
    ),
    "not_found": "Код <b>{plate}</b> не знайдено для {country}.\nДив. всі коди: /country {country}",
    "not_found_global": "Код <b>{plate}</b> не знайдено в жодній країні.",
    "ambiguous_header": "Знайдено в кількох країнах:",
    "ambiguous_hint": "Уточни: /plate {country} {plate}",
    "list_header": "Підтримувані країни:",
    "country_header": "{emoji} {country} — коди регіонів:",
    "country_not_found": "Країну <b>{country}</b> не знайдено.",
    "page_info": "Сторінка {page}/{total}",
    "plate_usage": "Використання: /plate &lt;країна&gt; &lt;код&gt;\nПриклад: /plate DE M",
    "country_usage": "Використання: /country &lt;код&gt;\nПриклад: /country DE",
    "language_prompt": "Оберіть мову:",
    "language_set": "Мову встановлено: Українська.",
    "unknown_input": "Не зрозумів. Спробуй: <code>DE M</code> або /help",
    "map_unavailable": "Координати для цього регіону недоступні.",
}
