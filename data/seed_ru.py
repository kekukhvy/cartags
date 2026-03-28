"""Seed Russia (RU) into the CarTags database.

Inserts the country record, its translations, and ~85 federal subject records
with full translations in en/de/ru/uk.  Plate codes are stored as strings
(e.g. "77", "78").  All inserts are idempotent via INSERT OR IGNORE.

Usage::

    python data/seed_ru.py
"""

import logging
import sqlite3
from pathlib import Path

logger = logging.getLogger(__name__)

DB_PATH = Path(__file__).parent.parent / "db" / "cartags.db"

COUNTRY_CODE = "RU"
COUNTRY_EMOJI = "🇷🇺"
COUNTRY_SORT_ORDER = 16

_COUNTRY_TRANSLATIONS: dict[str, str] = {
    "en": "Russia",
    "de": "Russland",
    "ru": "Россия",
    "uk": "Росія",
}

_FEDERAL_DISTRICT: dict[str, dict[str, str]] = {
    "Central": {
        "en": "Central Federal District",
        "de": "Zentraler Föderationskreis",
        "ru": "Центральный федеральный округ",
        "uk": "Центральний федеральний округ",
    },
    "Northwestern": {
        "en": "Northwestern Federal District",
        "de": "Nordwestlicher Föderationskreis",
        "ru": "Северо-Западный федеральный округ",
        "uk": "Північно-Західний федеральний округ",
    },
    "Southern": {
        "en": "Southern Federal District",
        "de": "Südlicher Föderationskreis",
        "ru": "Южный федеральный округ",
        "uk": "Південний федеральний округ",
    },
    "North Caucasian": {
        "en": "North Caucasian Federal District",
        "de": "Nordkaukasischer Föderationskreis",
        "ru": "Северо-Кавказский федеральный округ",
        "uk": "Північнокавказький федеральний округ",
    },
    "Volga": {
        "en": "Volga Federal District",
        "de": "Wolgaer Föderationskreis",
        "ru": "Приволжский федеральный округ",
        "uk": "Приволзький федеральний округ",
    },
    "Ural": {
        "en": "Ural Federal District",
        "de": "Uralischer Föderationskreis",
        "ru": "Уральский федеральный округ",
        "uk": "Уральський федеральний округ",
    },
    "Siberian": {
        "en": "Siberian Federal District",
        "de": "Sibirischer Föderationskreis",
        "ru": "Сибирский федеральный округ",
        "uk": "Сибірський федеральний округ",
    },
    "Far Eastern": {
        "en": "Far Eastern Federal District",
        "de": "Fernöstlicher Föderationskreis",
        "ru": "Дальневосточный федеральный округ",
        "uk": "Далекосхідний федеральний округ",
    },
}

_COORDS: dict[str, tuple[float, float]] = {
    "01": (43.1151, 47.0942),  # Republic of Adygea — Maikop
    "02": (54.7348, 55.9578),  # Republic of Bashkortostan — Ufa
    "03": (51.8272, 107.6064), # Republic of Buryatia — Ulan-Ude
    "04": (50.9793, 92.7938),  # Republic of Altai — Gorno-Altaysk
    "05": (42.9849, 47.5047),  # Republic of Dagestan — Makhachkala
    "06": (43.1717, 45.5900),  # Republic of Ingushetia — Magas
    "07": (43.6247, 43.1322),  # Kabardino-Balkaria — Nalchik
    "08": (46.3130, 44.2560),  # Republic of Kalmykia — Elista
    "09": (43.7209, 41.7266),  # Karachay-Cherkessia — Cherkessk
    "10": (61.7832, 34.3453),  # Republic of Karelia — Petrozavodsk
    "11": (61.6688, 50.8364),  # Komi Republic — Syktyvkar
    "12": (56.6344, 47.8869),  # Republic of Mari El — Yoshkar-Ola
    "13": (54.1842, 45.1839),  # Republic of Mordovia — Saransk
    "14": (62.0342, 129.7372), # Sakha (Yakutia) — Yakutsk
    "15": (43.0148, 44.6831),  # Republic of North Ossetia-Alania — Vladikavkaz
    "16": (55.7887, 49.1221),  # Republic of Tatarstan — Kazan
    "17": (51.7227, 94.4378),  # Republic of Tuva — Kyzyl
    "18": (56.8527, 53.2048),  # Udmurt Republic — Izhevsk
    "19": (53.7212, 91.4429),  # Republic of Khakassia — Abakan
    "21": (56.1439, 47.2489),  # Chuvash Republic — Cheboksary
    "22": (53.3479, 83.7798),  # Altai Krai — Barnaul
    "23": (45.0448, 38.9760),  # Krasnodar Krai — Krasnodar
    "24": (56.0095, 92.7920),  # Krasnoyarsk Krai — Krasnoyarsk
    "25": (43.1155, 131.8855), # Primorsky Krai — Vladivostok
    "26": (45.0440, 41.9693),  # Stavropol Krai — Stavropol
    "27": (48.4816, 135.0833), # Khabarovsk Krai — Khabarovsk
    "28": (50.2906, 127.5272), # Amur Oblast — Blagoveshchensk
    "29": (64.5393, 40.5169),  # Arkhangelsk Oblast — Arkhangelsk
    "30": (46.3498, 48.0408),  # Astrakhan Oblast — Astrakhan
    "31": (50.5952, 36.5873),  # Belgorod Oblast — Belgorod
    "32": (53.2434, 34.3636),  # Bryansk Oblast — Bryansk
    "33": (56.1290, 40.4066),  # Vladimir Oblast — Vladimir
    "34": (48.7194, 44.5018),  # Volgograd Oblast — Volgograd
    "35": (59.2112, 39.8725),  # Vologda Oblast — Vologda
    "36": (51.6583, 39.2004),  # Voronezh Oblast — Voronezh
    "37": (57.0005, 40.9739),  # Ivanovo Oblast — Ivanovo
    "38": (52.2978, 104.2964), # Irkutsk Oblast — Irkutsk
    "39": (54.7104, 20.4522),  # Kaliningrad Oblast — Kaliningrad
    "40": (54.5099, 36.2569),  # Kaluga Oblast — Kaluga
    "41": (53.0152, 158.6530), # Kamchatka Krai — Petropavlovsk-Kamchatsky
    "42": (55.3473, 86.0891),  # Kemerovo Oblast — Kemerovo
    "43": (58.6036, 49.6680),  # Kirov Oblast — Kirov
    "44": (58.5516, 44.2676),  # Kostroma Oblast — Kostroma
    "45": (55.4644, 65.3218),  # Kurgan Oblast — Kurgan
    "46": (51.7303, 36.1925),  # Kursk Oblast — Kursk
    "47": (59.9343, 30.3351),  # Leningrad Oblast — Saint Petersburg area
    "48": (52.5960, 39.5702),  # Lipetsk Oblast — Lipetsk
    "49": (59.5683, 150.7941), # Magadan Oblast — Magadan
    "50": (55.7558, 37.6173),  # Moscow Oblast — Moscow area
    "51": (68.9585, 33.0827),  # Murmansk Oblast — Murmansk
    "52": (56.3269, 44.0059),  # Nizhny Novgorod Oblast — Nizhny Novgorod
    "53": (58.5235, 31.2697),  # Novgorod Oblast — Veliky Novgorod
    "54": (54.9784, 82.8974),  # Novosibirsk Oblast — Novosibirsk
    "55": (54.9885, 73.3242),  # Omsk Oblast — Omsk
    "56": (51.7722, 55.0988),  # Orenburg Oblast — Orenburg
    "57": (52.9651, 36.0785),  # Oryol Oblast — Oryol
    "58": (53.1959, 45.0190),  # Penza Oblast — Penza
    "59": (57.9900, 56.2299),  # Perm Krai — Perm
    "60": (57.8136, 28.3496),  # Pskov Oblast — Pskov
    "61": (47.2224, 39.7188),  # Rostov Oblast — Rostov-on-Don
    "62": (54.6269, 39.7047),  # Ryazan Oblast — Ryazan
    "63": (53.2001, 50.1500),  # Samara Oblast — Samara
    "64": (51.5462, 46.0154),  # Saratov Oblast — Saratov
    "65": (46.9601, 142.7380), # Sakhalin Oblast — Yuzhno-Sakhalinsk
    "66": (56.8389, 60.6057),  # Sverdlovsk Oblast — Yekaterinburg
    "67": (54.7828, 32.0453),  # Smolensk Oblast — Smolensk
    "68": (52.7213, 41.4530),  # Tambov Oblast — Tambov
    "69": (56.8587, 35.9176),  # Tver Oblast — Tver
    "70": (56.4977, 84.9744),  # Tomsk Oblast — Tomsk
    "71": (54.1961, 37.6183),  # Tula Oblast — Tula
    "72": (57.1530, 68.9856),  # Tyumen Oblast — Tyumen
    "73": (54.3282, 48.3866),  # Ulyanovsk Oblast — Ulyanovsk
    "74": (55.1644, 61.4368),  # Chelyabinsk Oblast — Chelyabinsk
    "75": (51.9800, 113.5001), # Zabaykalsky Krai — Chita
    "76": (57.6226, 39.8844),  # Yaroslavl Oblast — Yaroslavl
    "77": (55.7558, 37.6173),  # Moscow City
    "78": (59.9343, 30.3351),  # Saint Petersburg City
    "79": (48.7993, 135.2374), # Jewish Autonomous Oblast — Birobidzhan
    "80": (54.5232, 53.0360),  # Bashkortostan (alt)
    "81": (44.0490, 43.0595),  # Kabardino-Balkaria (alt)
    "82": (44.9567, 34.1108),  # Republic of Crimea — Simferopol
    "83": (63.5593, 53.8220),  # Nenets Autonomous Okrug — Naryan-Mar
    "84": (66.5337, 80.5239),  # Yamalo-Nenets AO — Salekhard
    "85": (61.7232, 30.7190),  # Karelia (alt)
    "86": (61.0025, 69.0249),  # Khanty-Mansiysk AO — Khanty-Mansiysk
    "87": (64.7331, 177.5131), # Chukotka AO — Anadyr
    "88": (43.3162, 45.6889),  # Chechnya — Grozny
    "89": (67.4774, 64.0074),  # Yamalo-Nenets AO (alt)
    "90": (55.7558, 37.6173),  # Moscow (metro alt)
    "92": (44.6099, 33.5226),  # Sevastopol City
    "93": (45.0448, 38.9760),  # Krasnodar (alt)
    "94": (59.9343, 30.3351),  # Saint Petersburg (alt)
    "95": (43.3162, 45.6889),  # Chechen Republic (alt)
    "96": (56.8389, 60.6057),  # Sverdlovsk (alt)
    "97": (55.7558, 37.6173),  # Moscow (alt)
}

# (plate_code, name_en, name_de, name_ru, name_uk, district_key)
_REGION_ROWS: list[tuple[str, str, str, str, str, str]] = [
    ("01", "Republic of Adygea",           "Republik Adygeja",             "Республика Адыгея",          "Республіка Адигея",          "Southern"),
    ("02", "Republic of Bashkortostan",     "Republik Baschkortostan",      "Республика Башкортостан",    "Республіка Башкортостан",    "Volga"),
    ("03", "Republic of Buryatia",          "Republik Burjatien",           "Республика Бурятия",         "Республіка Бурятія",         "Far Eastern"),
    ("04", "Republic of Altai",             "Republik Altai",               "Республика Алтай",           "Республіка Алтай",           "Siberian"),
    ("05", "Republic of Dagestan",          "Republik Dagestan",            "Республика Дагестан",        "Республіка Дагестан",        "North Caucasian"),
    ("06", "Republic of Ingushetia",        "Republik Inguschetien",        "Республика Ингушетия",       "Республіка Інгушетія",       "North Caucasian"),
    ("07", "Kabardino-Balkarian Republic",  "Kabardino-Balkarische Republik","Кабардино-Балкарская Республика","Кабардино-Балкарська Республіка","North Caucasian"),
    ("08", "Republic of Kalmykia",          "Republik Kalmückien",          "Республика Калмыкия",        "Республіка Калмикія",        "Southern"),
    ("09", "Karachay-Cherkess Republic",    "Karatschai-Tscherkessische Republik","Карачаево-Черкесская Республика","Карачаєво-Черкеська Республіка","North Caucasian"),
    ("10", "Republic of Karelia",           "Republik Karelien",            "Республика Карелия",         "Республіка Карелія",         "Northwestern"),
    ("11", "Komi Republic",                 "Republik Komi",                "Республика Коми",            "Республіка Комі",            "Northwestern"),
    ("12", "Mari El Republic",              "Republik Mari El",             "Республика Марий Эл",        "Республіка Марій Ел",        "Volga"),
    ("13", "Republic of Mordovia",          "Republik Mordwinien",          "Республика Мордовия",        "Республіка Мордовія",        "Volga"),
    ("14", "Sakha (Yakutia) Republic",      "Republik Sacha (Jakutien)",    "Республика Саха (Якутия)",   "Республіка Саха (Якутія)",   "Far Eastern"),
    ("15", "North Ossetia-Alania",          "Nordossetien-Alanien",         "Республика Северная Осетия", "Республіка Північна Осетія", "North Caucasian"),
    ("16", "Republic of Tatarstan",         "Republik Tatarstan",           "Республика Татарстан",       "Республіка Татарстан",       "Volga"),
    ("17", "Republic of Tuva",              "Republik Tuwa",                "Республика Тыва",            "Республіка Тива",            "Siberian"),
    ("18", "Udmurt Republic",               "Republik Udmurtien",           "Удмуртская Республика",      "Удмуртська Республіка",      "Volga"),
    ("19", "Republic of Khakassia",         "Republik Chakassien",          "Республика Хакасия",         "Республіка Хакасія",         "Siberian"),
    ("21", "Chuvash Republic",              "Tschuwaschische Republik",     "Чувашская Республика",       "Чуваська Республіка",        "Volga"),
    ("22", "Altai Krai",                    "Region Altai",                 "Алтайский край",             "Алтайський край",            "Siberian"),
    ("23", "Krasnodar Krai",                "Region Krasnodar",             "Краснодарский край",         "Краснодарський край",        "Southern"),
    ("24", "Krasnoyarsk Krai",              "Region Krasnojarsk",           "Красноярский край",          "Красноярський край",         "Siberian"),
    ("25", "Primorsky Krai",                "Region Primorje",              "Приморский край",            "Приморський край",           "Far Eastern"),
    ("26", "Stavropol Krai",                "Region Stawropol",             "Ставропольский край",        "Ставропольський край",       "North Caucasian"),
    ("27", "Khabarovsk Krai",               "Region Chabarowsk",            "Хабаровский край",           "Хабаровський край",          "Far Eastern"),
    ("28", "Amur Oblast",                   "Oblast Amur",                  "Амурская область",           "Амурська область",           "Far Eastern"),
    ("29", "Arkhangelsk Oblast",            "Oblast Archangelsk",           "Архангельская область",      "Архангельська область",      "Northwestern"),
    ("30", "Astrakhan Oblast",              "Oblast Astrachan",             "Астраханская область",       "Астраханська область",       "Southern"),
    ("31", "Belgorod Oblast",               "Oblast Belgorod",              "Белгородская область",       "Білгородська область",       "Central"),
    ("32", "Bryansk Oblast",                "Oblast Brjansk",               "Брянская область",           "Брянська область",           "Central"),
    ("33", "Vladimir Oblast",               "Oblast Wladimir",              "Владимирская область",       "Владимирська область",       "Central"),
    ("34", "Volgograd Oblast",              "Oblast Wolgograd",             "Волгоградская область",      "Волгоградська область",      "Southern"),
    ("35", "Vologda Oblast",                "Oblast Wologda",               "Вологодская область",        "Вологодська область",        "Northwestern"),
    ("36", "Voronezh Oblast",               "Oblast Woronesch",             "Воронежская область",        "Воронезька область",         "Central"),
    ("37", "Ivanovo Oblast",                "Oblast Iwanowo",               "Ивановская область",         "Іванівська область",         "Central"),
    ("38", "Irkutsk Oblast",                "Oblast Irkutsk",               "Иркутская область",          "Іркутська область",          "Siberian"),
    ("39", "Kaliningrad Oblast",            "Oblast Kaliningrad",           "Калининградская область",    "Калінінградська область",    "Northwestern"),
    ("40", "Kaluga Oblast",                 "Oblast Kaluga",                "Калужская область",          "Калузька область",           "Central"),
    ("41", "Kamchatka Krai",                "Region Kamtschatka",           "Камчатский край",            "Камчатський край",           "Far Eastern"),
    ("42", "Kemerovo Oblast",               "Oblast Kemerowo",              "Кемеровская область",        "Кемеровська область",        "Siberian"),
    ("43", "Kirov Oblast",                  "Oblast Kirow",                 "Кировская область",          "Кіровська область",          "Volga"),
    ("44", "Kostroma Oblast",               "Oblast Kostroma",              "Костромская область",        "Костромська область",        "Central"),
    ("45", "Kurgan Oblast",                 "Oblast Kurgan",                "Курганская область",         "Курганська область",         "Ural"),
    ("46", "Kursk Oblast",                  "Oblast Kursk",                 "Курская область",            "Курська область",            "Central"),
    ("47", "Leningrad Oblast",              "Oblast Leningrad",             "Ленинградская область",      "Ленінградська область",      "Northwestern"),
    ("48", "Lipetsk Oblast",                "Oblast Lipezk",                "Липецкая область",           "Липецька область",           "Central"),
    ("49", "Magadan Oblast",                "Oblast Magadan",               "Магаданская область",        "Магаданська область",        "Far Eastern"),
    ("50", "Moscow Oblast",                 "Oblast Moskau",                "Московская область",         "Московська область",         "Central"),
    ("51", "Murmansk Oblast",               "Oblast Murmansk",              "Мурманская область",         "Мурманська область",         "Northwestern"),
    ("52", "Nizhny Novgorod Oblast",        "Oblast Nischni Nowgorod",      "Нижегородская область",      "Нижньогородська область",    "Volga"),
    ("53", "Novgorod Oblast",               "Oblast Nowgorod",              "Новгородская область",       "Новгородська область",       "Northwestern"),
    ("54", "Novosibirsk Oblast",            "Oblast Nowosibirsk",           "Новосибирская область",      "Новосибірська область",      "Siberian"),
    ("55", "Omsk Oblast",                   "Oblast Omsk",                  "Омская область",             "Омська область",             "Siberian"),
    ("56", "Orenburg Oblast",               "Oblast Orenburg",              "Оренбургская область",       "Оренбурзька область",        "Volga"),
    ("57", "Oryol Oblast",                  "Oblast Orjol",                 "Орловская область",          "Орловська область",          "Central"),
    ("58", "Penza Oblast",                  "Oblast Pensa",                 "Пензенская область",         "Пензенська область",         "Volga"),
    ("59", "Perm Krai",                     "Region Perm",                  "Пермский край",              "Пермський край",             "Volga"),
    ("60", "Pskov Oblast",                  "Oblast Pskow",                 "Псковская область",          "Псковська область",          "Northwestern"),
    ("61", "Rostov Oblast",                 "Oblast Rostow",                "Ростовская область",         "Ростовська область",         "Southern"),
    ("62", "Ryazan Oblast",                 "Oblast Rjasan",                "Рязанская область",          "Рязанська область",          "Central"),
    ("63", "Samara Oblast",                 "Oblast Samara",                "Самарская область",          "Самарська область",          "Volga"),
    ("64", "Saratov Oblast",                "Oblast Saratow",               "Саратовская область",        "Саратовська область",        "Volga"),
    ("65", "Sakhalin Oblast",               "Oblast Sachalin",              "Сахалинская область",        "Сахалінська область",        "Far Eastern"),
    ("66", "Sverdlovsk Oblast",             "Oblast Swerdlowsk",            "Свердловская область",       "Свердловська область",       "Ural"),
    ("67", "Smolensk Oblast",               "Oblast Smolensk",              "Смоленская область",         "Смоленська область",         "Central"),
    ("68", "Tambov Oblast",                 "Oblast Tambow",                "Тамбовская область",         "Тамбовська область",         "Central"),
    ("69", "Tver Oblast",                   "Oblast Twer",                  "Тверская область",           "Тверська область",           "Central"),
    ("70", "Tomsk Oblast",                  "Oblast Tomsk",                 "Томская область",            "Томська область",            "Siberian"),
    ("71", "Tula Oblast",                   "Oblast Tula",                  "Тульская область",           "Тульська область",           "Central"),
    ("72", "Tyumen Oblast",                 "Oblast Tjumen",                "Тюменская область",          "Тюменська область",          "Ural"),
    ("73", "Ulyanovsk Oblast",              "Oblast Uljanowsk",             "Ульяновская область",        "Ульяновська область",        "Volga"),
    ("74", "Chelyabinsk Oblast",            "Oblast Tscheljabinsk",         "Челябинская область",        "Челябінська область",        "Ural"),
    ("75", "Zabaykalsky Krai",              "Region Transbaikalien",        "Забайкальский край",         "Забайкальський край",        "Far Eastern"),
    ("76", "Yaroslavl Oblast",              "Oblast Jaroslawl",             "Ярославская область",        "Ярославська область",        "Central"),
    ("77", "Moscow City",                   "Moskau (Stadt)",               "Москва",                     "Москва",                     "Central"),
    ("78", "Saint Petersburg City",         "Sankt Petersburg (Stadt)",     "Санкт-Петербург",            "Санкт-Петербург",            "Northwestern"),
    ("79", "Jewish Autonomous Oblast",      "Jüdisches Autonomes Gebiet",   "Еврейская автономная область","Єврейська автономна область","Far Eastern"),
    ("82", "Republic of Crimea",            "Republik Krim",                "Республика Крым",            "Республіка Крим",            "Southern"),
    ("83", "Nenets Autonomous Okrug",       "Autonomes Krei der Nenzen",    "Ненецкий автономный округ",  "Ненецький автономний округ", "Northwestern"),
    ("86", "Khanty-Mansiysk AO — Yugra",   "Chanty-Mansijsk AO",          "Ханты-Мансийский АО — Югра", "Ханти-Мансійський АО — Югра","Ural"),
    ("87", "Chukotka Autonomous Okrug",     "Tschukotisches AO",            "Чукотский автономный округ", "Чукотський автономний округ","Far Eastern"),
    ("88", "Chechen Republic",              "Tschetschenische Republik",    "Чеченская Республика",       "Чеченська Республіка",       "North Caucasian"),
    ("89", "Yamalo-Nenets AO",              "Jamal-Nenzen AO",              "Ямало-Ненецкий АО",          "Ямало-Ненецький АО",         "Ural"),
    ("92", "Sevastopol City",               "Sewastopol (Stadt)",           "Севастополь",                "Севастополь",                "Southern"),
    ("95", "Chechen Republic (alt)",        "Tschetschenien (alt)",         "Чеченская Республика (доп)", "Чеченська Республіка (доп)", "North Caucasian"),
    ("96", "Sverdlovsk (alt)",              "Swerdlowsk (alt)",             "Свердловская обл. (доп)",    "Свердловська обл. (доп)",    "Ural"),
    ("97", "Moscow (federal alt)",          "Moskau (Bundesbehörden)",      "Москва (федеральные органы)","Москва (федеральні органи)", "Central"),
]


# ---------------------------------------------------------------------------
# Insertion helpers
# ---------------------------------------------------------------------------

def _get_or_insert_country(conn: sqlite3.Connection) -> int:
    """Insert country if absent and return its id."""
    conn.execute(
        "INSERT OR IGNORE INTO countries (code, emoji, sort_order) VALUES (?, ?, ?)",
        (COUNTRY_CODE, COUNTRY_EMOJI, COUNTRY_SORT_ORDER),
    )
    row = conn.execute("SELECT id FROM countries WHERE code = ?", (COUNTRY_CODE,)).fetchone()
    return row[0]


def _insert_country_translations(conn: sqlite3.Connection, country_id: int) -> None:
    """Insert all language translations for the country."""
    for lang, value in _COUNTRY_TRANSLATIONS.items():
        conn.execute(
            "INSERT OR IGNORE INTO translations "
            "(entity_type, entity_id, language_code, field, value) VALUES (?, ?, ?, ?, ?)",
            ("country", country_id, lang, "name", value),
        )


def seed_country(conn: sqlite3.Connection) -> None:
    """Insert the RU country record and its translations.

    Args:
        conn: An open SQLite connection (foreign keys must be on).
    """
    country_id = _get_or_insert_country(conn)
    _insert_country_translations(conn, country_id)
    logger.info("Seeded country RU (id=%d)", country_id)


def _insert_region_translations(
    conn: sqlite3.Connection,
    region_id: int,
    name_trans: dict[str, str],
    group_trans: dict[str, str],
) -> None:
    """Insert name and region_group translations for a single region.

    Args:
        conn:        An open SQLite connection.
        region_id:   Primary key of the region row.
        name_trans:  Mapping of language_code → name value.
        group_trans: Mapping of language_code → region_group value.
    """
    for lang, value in name_trans.items():
        conn.execute(
            "INSERT OR IGNORE INTO translations "
            "(entity_type, entity_id, language_code, field, value) VALUES (?, ?, ?, ?, ?)",
            ("region", region_id, lang, "name", value),
        )
    for lang, value in group_trans.items():
        conn.execute(
            "INSERT OR IGNORE INTO translations "
            "(entity_type, entity_id, language_code, field, value) VALUES (?, ?, ?, ?, ?)",
            ("region", region_id, lang, "region_group", value),
        )


def _seed_single_region(
    conn: sqlite3.Connection,
    country_id: int,
    plate_code: str,
    name_en: str,
    name_de: str,
    name_ru: str,
    name_uk: str,
    district_key: str,
    coords: tuple[float, float] | None,
) -> None:
    """Insert one federal subject and its translations."""
    lat = coords[0] if coords else None
    lon = coords[1] if coords else None
    conn.execute(
        "INSERT OR IGNORE INTO regions"
        " (country_id, plate_code, latitude, longitude) VALUES (?, ?, ?, ?)",
        (country_id, plate_code, lat, lon),
    )
    row = conn.execute(
        "SELECT id FROM regions WHERE country_id = ? AND plate_code = ?",
        (country_id, plate_code),
    ).fetchone()
    name_trans = {"en": name_en, "de": name_de, "ru": name_ru, "uk": name_uk}
    group_trans = _FEDERAL_DISTRICT[district_key]
    _insert_region_translations(conn, row[0], name_trans, group_trans)


def seed_regions(conn: sqlite3.Connection) -> None:
    """Insert all RU federal subject records and their translations.

    Args:
        conn: An open SQLite connection.
    """
    row = conn.execute("SELECT id FROM countries WHERE code = ?", (COUNTRY_CODE,)).fetchone()
    country_id: int = row[0]
    for plate_code, name_en, name_de, name_ru, name_uk, district_key in _REGION_ROWS:
        coords = _COORDS.get(plate_code)
        _seed_single_region(
            conn, country_id, plate_code,
            name_en, name_de, name_ru, name_uk,
            district_key, coords,
        )
    logger.info("Seeded %d RU federal subjects", len(_REGION_ROWS))


def run(conn: sqlite3.Connection) -> None:
    """Run the full Russia seed: country + all federal subjects.

    Args:
        conn: An open SQLite connection.
    """
    seed_country(conn)
    seed_regions(conn)


def main() -> None:
    """Open the production DB, seed Russia, and close."""
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s — %(message)s")
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    try:
        run(conn)
        conn.commit()
        logger.info("Russia seed complete")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
