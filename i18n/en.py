"""English UI strings."""

STRINGS: dict[str, str] = {
    "start_greeting": (
        "Hi! I'm CarTags — a license plate directory.\n\n"
        "Just type a plate code:\n"
        "• DE M → Munich, Germany\n"
        "• AT W → Vienna, Austria\n"
        "• UA AA → Kyiv, Ukraine\n\n"
        "/list — all supported countries\n"
        "/help — detailed help"
    ),
    "help_text": (
        "Send a plate code to look it up:\n"
        "• Single code: <code>M</code>\n"
        "• With country: <code>DE M</code>\n"
        "• All regions: /country DE\n\n"
        "Commands:\n"
        "/plate DE M — look up a specific plate\n"
        "/country DE — list all German regions\n"
        "/list — supported countries\n"
        "/language — change language"
    ),
    "about_text": (
        "CarTags — license plate region lookup.\n\n"
        "Supported: DE, AT, UA (more coming).\n"
        "Use /language to switch UI language."
    ),
    "not_found": "Code <b>{plate}</b> not found for {country}.\nSee all codes: /country {country}",
    "not_found_global": "Code <b>{plate}</b> not found in any country.",
    "ambiguous_header": "Found in multiple countries:",
    "ambiguous_hint": "Specify: /plate {country} {plate}",
    "list_header": "Supported countries:",
    "country_header": "{emoji} {country} — plate codes:",
    "country_not_found": "Country <b>{country}</b> not found.",
    "page_info": "Page {page}/{total}",
    "plate_usage": "Usage: /plate &lt;country&gt; &lt;code&gt;\nExample: /plate DE M",
    "country_usage": "Usage: /country &lt;code&gt;\nExample: /country DE",
    "language_prompt": "Choose your language:",
    "language_set": "Language set to English.",
    "unknown_input": "I didn't understand that. Try: <code>DE M</code> or /help",
    "nav_list": "🌍 Countries",
    "nav_help": "❓ Help",
    "nav_language": "🌐 Language",
    "nav_browse_country": "📋 Browse {country}",
    "map_unavailable": "No map location available for this region.",
}
