"""German UI strings."""

STRINGS: dict[str, str] = {
    "start_greeting": (
        "Hallo! Ich bin CarTags — ein Kfz-Kennzeichen-Verzeichnis.\n\n"
        "Gib einfach einen Kennzeichencode ein:\n"
        "• DE M → München, Deutschland\n"
        "• AT W → Wien, Österreich\n"
        "• UA AA → Kiew, Ukraine\n\n"
        "/list — alle unterstützten Länder\n"
        "/help — ausführliche Hilfe"
    ),
    "help_text": (
        "Sende einen Kennzeichencode:\n"
        "• Nur Code: <code>M</code>\n"
        "• Mit Land: <code>DE M</code>\n"
        "• Alle Kennzeichen: /country DE\n\n"
        "Befehle:\n"
        "/plate DE M — Kennzeichen nachschlagen\n"
        "/country DE — alle deutschen Kennzeichen\n"
        "/list — unterstützte Länder\n"
        "/language — Sprache ändern"
    ),
    "about_text": (
        "CarTags — Kennzeichen-Regionsnachschlagedienst.\n\n"
        "Unterstützt: DE, AT, UA (weitere folgen).\n"
        "Nutze /language zum Sprachwechsel."
    ),
    "not_found": "Code <b>{plate}</b> nicht gefunden für {country}.\nAlle Codes: /country {country}",
    "not_found_global": "Code <b>{plate}</b> in keinem Land gefunden.",
    "ambiguous_header": "In mehreren Ländern gefunden:",
    "ambiguous_hint": "Genauer: /plate {country} {plate}",
    "list_header": "Unterstützte Länder:",
    "country_header": "{emoji} {country} — Kennzeichen:",
    "country_not_found": "Land <b>{country}</b> nicht gefunden.",
    "page_info": "Seite {page}/{total}",
    "plate_usage": "Nutzung: /plate &lt;Land&gt; &lt;Code&gt;\nBeispiel: /plate DE M",
    "country_usage": "Nutzung: /country &lt;Code&gt;\nBeispiel: /country DE",
    "language_prompt": "Wähle deine Sprache:",
    "language_set": "Sprache auf Deutsch gesetzt.",
    "unknown_input": "Nicht verstanden. Versuch: <code>DE M</code> oder /help",
    "nav_list": "🌍 Länder",
    "nav_help": "❓ Hilfe",
    "nav_language": "🌐 Sprache",
    "nav_browse_country": "📋 {country} durchsuchen",
    "map_unavailable": "Kein Kartenstandort für diese Region verfügbar.",
}
