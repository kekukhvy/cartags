"""Seed Ukraine (UA) into the CarTags database.

Inserts the country record, its translations, and all region codes
across the 2004, 2015, and 2021 plate series with full translations
in en/de/ru/uk.  All inserts are idempotent via INSERT OR IGNORE.

Usage::

    python data/seed_ua.py
"""

import logging
import sqlite3
from pathlib import Path

logger = logging.getLogger(__name__)

DB_PATH = Path(__file__).parent.parent / "db" / "cartags.db"

COUNTRY_CODE = "UA"
COUNTRY_EMOJI = "🇺🇦"
COUNTRY_SORT_ORDER = 3

_COUNTRY_TRANSLATIONS: dict[str, str] = {
    "en": "Ukraine",
    "de": "Ukraine",
    "ru": "Украина",
    "uk": "Україна",
}

# Map of plate_code → (latitude, longitude) for regions with known coordinates.
# Ukrainian plate codes are regional; we pin the oblast centre city for each series.
_COORDS: dict[str, tuple[float, float]] = {
    "AA": (50.4501, 30.5234),   # Kyiv
    "KA": (50.4501, 30.5234),
    "TT": (50.4501, 30.5234),
    "TA": (50.4501, 30.5234),
    "AI": (50.4501, 30.5234),   # Kyiv Oblast (Kyiv city centre)
    "KI": (50.4501, 30.5234),
    "TI": (50.4501, 30.5234),
    "ME": (50.4501, 30.5234),
    "AB": (49.2331, 28.4682),   # Vinnytsia
    "KB": (49.2331, 28.4682),
    "MM": (49.2331, 28.4682),
    "OK": (49.2331, 28.4682),
    "AC": (50.7472, 25.3254),   # Lutsk
    "KC": (50.7472, 25.3254),
    "CM": (50.7472, 25.3254),
    "TC": (50.7472, 25.3254),
    "AE": (48.4647, 35.0462),   # Dnipro
    "KE": (48.4647, 35.0462),
    "PP": (48.4647, 35.0462),
    "MI": (48.4647, 35.0462),
    "AT": (48.9226, 24.7111),   # Ivano-Frankivsk
    "KT": (48.9226, 24.7111),
    "TO": (48.9226, 24.7111),
    "XC": (48.9226, 24.7111),
    "AX": (49.9935, 36.2304),   # Kharkiv
    "KX": (49.9935, 36.2304),
    "XX": (49.9935, 36.2304),
    "EX": (49.9935, 36.2304),
    "BC": (49.8397, 24.0297),   # Lviv
    "HC": (49.8397, 24.0297),
    "CC": (49.8397, 24.0297),
    "EC": (49.8397, 24.0297),
    "BH": (46.4825, 30.7233),   # Odessa
    "HH": (46.4825, 30.7233),
    "OO": (46.4825, 30.7233),
    "EH": (46.4825, 30.7233),
    "AO": (48.6208, 22.2879),   # Uzhhorod
    "KO": (48.6208, 22.2879),
    "MT": (48.6208, 22.2879),
    "MO": (48.6208, 22.2879),
    "AP": (47.8388, 35.1396),   # Zaporizhzhia
    "KP": (47.8388, 35.1396),
    "TP": (47.8388, 35.1396),
    "MP": (47.8388, 35.1396),
    "AH": (48.0159, 37.8028),   # Donetsk
    "KH": (48.0159, 37.8028),
    "TH": (48.0159, 37.8028),
    "MH": (48.0159, 37.8028),
    "BA": (48.5132, 32.2597),   # Kropyvnytskyi
    "HA": (48.5132, 32.2597),
    "XA": (48.5132, 32.2597),
    "EA": (48.5132, 32.2597),
    "BK": (50.6199, 26.2516),   # Rivne
    "HK": (50.6199, 26.2516),
    "XK": (50.6199, 26.2516),
    "EK": (50.6199, 26.2516),
    "BI": (49.5883, 34.5514),   # Poltava
    "HI": (49.5883, 34.5514),
    "XI": (49.5883, 34.5514),
    "EI": (49.5883, 34.5514),
    "BM": (50.9077, 34.7981),   # Sumy
    "HM": (50.9077, 34.7981),
    "XM": (50.9077, 34.7981),
    "EM": (50.9077, 34.7981),
    "BO": (49.5535, 25.5948),   # Ternopil
    "HO": (49.5535, 25.5948),
    "XO": (49.5535, 25.5948),
    "EO": (49.5535, 25.5948),
    "BT": (46.6354, 32.6169),   # Kherson
    "HT": (46.6354, 32.6169),
    "XT": (46.6354, 32.6169),
    "ET": (46.6354, 32.6169),
    "BX": (49.4229, 26.9871),   # Khmelnytskyi
    "HX": (49.4229, 26.9871),
    "OX": (49.4229, 26.9871),
    "PX": (49.4229, 26.9871),
    "CA": (49.4285, 32.0619),   # Cherkasy
    "IA": (49.4285, 32.0619),
    "OA": (49.4285, 32.0619),
    "PA": (49.4285, 32.0619),
    "CB": (51.4982, 31.2893),   # Chernihiv
    "IB": (51.4982, 31.2893),
    "OB": (51.4982, 31.2893),
    "PB": (51.4982, 31.2893),
    "CE": (48.2921, 25.9358),   # Chernivtsi
    "IE": (48.2921, 25.9358),
    "OE": (48.2921, 25.9358),
    "PE": (48.2921, 25.9358),
    "BB": (48.5679, 39.3404),   # Luhansk
    "HB": (48.5679, 39.3404),
    "EE": (48.5679, 39.3404),
    "EB": (48.5679, 39.3404),
    "BE": (46.9750, 31.9946),   # Mykolaiv
    "HE": (46.9750, 31.9946),
    "XE": (46.9750, 31.9946),
    "XH": (46.9750, 31.9946),
    "AM": (50.2547, 28.6587),   # Zhytomyr
    "KM": (50.2547, 28.6587),
    "TM": (50.2547, 28.6587),
    "MB": (50.2547, 28.6587),
    "AK": (44.9521, 34.1024),   # Simferopol
    "MA": (44.9521, 34.1024),
    "TK": (44.9521, 34.1024),
    "MK": (44.9521, 34.1024),
    "CH": (44.6166, 33.5254),   # Sevastopol
    "IH": (44.6166, 33.5254),
    "OH": (44.6166, 33.5254),
    "PH": (44.6166, 33.5254),
}

# (plate_code, name_en, name_de, name_ru, name_uk,
#              group_en, group_de, group_ru, group_uk)
_REGIONS: list[tuple[str, str, str, str, str, str, str, str, str]] = [
    # --- Kyiv City ---
    ("AA", "Kyiv", "Kiew", "Киев", "Київ",
           "Kyiv City", "Stadt Kiew", "Город Киев", "Місто Київ"),
    ("KA", "Kyiv", "Kiew", "Киев", "Київ",
           "Kyiv City", "Stadt Kiew", "Город Киев", "Місто Київ"),
    ("TT", "Kyiv", "Kiew", "Киев", "Київ",
           "Kyiv City", "Stadt Kiew", "Город Киев", "Місто Київ"),
    ("TA", "Kyiv", "Kiew", "Киев", "Київ",
           "Kyiv City", "Stadt Kiew", "Город Киев", "Місто Київ"),
    # --- Kyiv Oblast ---
    ("AI", "Kyiv Oblast", "Oblast Kiew", "Киевская область", "Київська область",
           "Kyiv Oblast", "Oblast Kiew", "Киевская область", "Київська область"),
    ("KI", "Kyiv Oblast", "Oblast Kiew", "Киевская область", "Київська область",
           "Kyiv Oblast", "Oblast Kiew", "Киевская область", "Київська область"),
    ("TI", "Kyiv Oblast", "Oblast Kiew", "Киевская область", "Київська область",
           "Kyiv Oblast", "Oblast Kiew", "Киевская область", "Київська область"),
    ("ME", "Kyiv Oblast", "Oblast Kiew", "Киевская область", "Київська область",
           "Kyiv Oblast", "Oblast Kiew", "Киевская область", "Київська область"),
    # --- Vinnytsia Oblast ---
    ("AB", "Vinnytsia", "Winnyzja", "Винница", "Вінниця",
           "Vinnytsia Oblast", "Oblast Winnyzja", "Винницкая область", "Вінницька область"),
    ("KB", "Vinnytsia", "Winnyzja", "Винница", "Вінниця",
           "Vinnytsia Oblast", "Oblast Winnyzja", "Винницкая область", "Вінницька область"),
    ("MM", "Vinnytsia", "Winnyzja", "Винница", "Вінниця",
           "Vinnytsia Oblast", "Oblast Winnyzja", "Винницкая область", "Вінницька область"),
    ("OK", "Vinnytsia", "Winnyzja", "Винница", "Вінниця",
           "Vinnytsia Oblast", "Oblast Winnyzja", "Винницкая область", "Вінницька область"),
    # --- Volyn Oblast ---
    ("AC", "Lutsk", "Luzk", "Луцк", "Луцьк",
           "Volyn Oblast", "Oblast Wolyn", "Волынская область", "Волинська область"),
    ("KC", "Lutsk", "Luzk", "Луцк", "Луцьк",
           "Volyn Oblast", "Oblast Wolyn", "Волынская область", "Волинська область"),
    ("CM", "Lutsk", "Luzk", "Луцк", "Луцьк",
           "Volyn Oblast", "Oblast Wolyn", "Волынская область", "Волинська область"),
    ("TC", "Lutsk", "Luzk", "Луцк", "Луцьк",
           "Volyn Oblast", "Oblast Wolyn", "Волынская область", "Волинська область"),
    # --- Dnipropetrovsk Oblast ---
    ("AE", "Dnipro", "Dnipro", "Днепр", "Дніпро",
           "Dnipropetrovsk Oblast", "Oblast Dnipropetrowsk",
           "Днепропетровская область", "Дніпропетровська область"),
    ("KE", "Dnipro", "Dnipro", "Днепр", "Дніпро",
           "Dnipropetrovsk Oblast", "Oblast Dnipropetrowsk",
           "Днепропетровская область", "Дніпропетровська область"),
    ("PP", "Dnipro", "Dnipro", "Днепр", "Дніпро",
           "Dnipropetrovsk Oblast", "Oblast Dnipropetrowsk",
           "Днепропетровская область", "Дніпропетровська область"),
    ("MI", "Dnipro", "Dnipro", "Днепр", "Дніпро",
           "Dnipropetrovsk Oblast", "Oblast Dnipropetrowsk",
           "Днепропетровская область", "Дніпропетровська область"),
    # --- Autonomous Republic of Crimea ---
    ("AK", "Simferopol", "Simferopol", "Симферополь", "Сімферополь",
           "AR Crimea", "AR Krim", "АР Крым", "АР Крим"),
    ("MA", "Simferopol", "Simferopol", "Симферополь", "Сімферополь",
           "AR Crimea", "AR Krim", "АР Крым", "АР Крим"),
    ("TK", "Simferopol", "Simferopol", "Симферополь", "Сімферополь",
           "AR Crimea", "AR Krim", "АР Крым", "АР Крим"),
    ("MK", "Simferopol", "Simferopol", "Симферополь", "Сімферополь",
           "AR Crimea", "AR Krim", "АР Крым", "АР Крим"),
    # --- Donetsk Oblast ---
    ("AH", "Donetsk", "Donezk", "Донецк", "Донецьк",
           "Donetsk Oblast", "Oblast Donezk", "Донецкая область", "Донецька область"),
    ("KH", "Donetsk", "Donezk", "Донецк", "Донецьк",
           "Donetsk Oblast", "Oblast Donezk", "Донецкая область", "Донецька область"),
    ("TH", "Donetsk", "Donezk", "Донецк", "Донецьк",
           "Donetsk Oblast", "Oblast Donezk", "Донецкая область", "Донецька область"),
    ("MH", "Donetsk", "Donezk", "Донецк", "Донецьк",
           "Donetsk Oblast", "Oblast Donezk", "Донецкая область", "Донецька область"),
    # --- Zhytomyr Oblast ---
    ("AM", "Zhytomyr", "Schytomyr", "Житомир", "Житомир",
           "Zhytomyr Oblast", "Oblast Schytomyr", "Житомирская область", "Житомирська область"),
    ("KM", "Zhytomyr", "Schytomyr", "Житомир", "Житомир",
           "Zhytomyr Oblast", "Oblast Schytomyr", "Житомирская область", "Житомирська область"),
    ("TM", "Zhytomyr", "Schytomyr", "Житомир", "Житомир",
           "Zhytomyr Oblast", "Oblast Schytomyr", "Житомирская область", "Житомирська область"),
    ("MB", "Zhytomyr", "Schytomyr", "Житомир", "Житомир",
           "Zhytomyr Oblast", "Oblast Schytomyr", "Житомирская область", "Житомирська область"),
    # --- Zakarpattia Oblast ---
    ("AO", "Uzhhorod", "Uschhorod", "Ужгород", "Ужгород",
           "Zakarpattia Oblast", "Oblast Transkarpatien",
           "Закарпатская область", "Закарпатська область"),
    ("KO", "Uzhhorod", "Uschhorod", "Ужгород", "Ужгород",
           "Zakarpattia Oblast", "Oblast Transkarpatien",
           "Закарпатская область", "Закарпатська область"),
    ("MT", "Uzhhorod", "Uschhorod", "Ужгород", "Ужгород",
           "Zakarpattia Oblast", "Oblast Transkarpatien",
           "Закарпатская область", "Закарпатська область"),
    ("MO", "Uzhhorod", "Uschhorod", "Ужгород", "Ужгород",
           "Zakarpattia Oblast", "Oblast Transkarpatien",
           "Закарпатская область", "Закарпатська область"),
    # --- Zaporizhzhia Oblast ---
    ("AP", "Zaporizhzhia", "Saporischschja", "Запорожье", "Запоріжжя",
           "Zaporizhzhia Oblast", "Oblast Saporischschja",
           "Запорожская область", "Запорізька область"),
    ("KP", "Zaporizhzhia", "Saporischschja", "Запорожье", "Запоріжжя",
           "Zaporizhzhia Oblast", "Oblast Saporischschja",
           "Запорожская область", "Запорізька область"),
    ("TP", "Zaporizhzhia", "Saporischschja", "Запорожье", "Запоріжжя",
           "Zaporizhzhia Oblast", "Oblast Saporischschja",
           "Запорожская область", "Запорізька область"),
    ("MP", "Zaporizhzhia", "Saporischschja", "Запорожье", "Запоріжжя",
           "Zaporizhzhia Oblast", "Oblast Saporischschja",
           "Запорожская область", "Запорізька область"),
    # --- Ivano-Frankivsk Oblast ---
    ("AT", "Ivano-Frankivsk", "Iwano-Frankiwsk", "Ивано-Франковск", "Івано-Франківськ",
           "Ivano-Frankivsk Oblast", "Oblast Iwano-Frankiwsk",
           "Ивано-Франковская область", "Івано-Франківська область"),
    ("KT", "Ivano-Frankivsk", "Iwano-Frankiwsk", "Ивано-Франковск", "Івано-Франківськ",
           "Ivano-Frankivsk Oblast", "Oblast Iwano-Frankiwsk",
           "Ивано-Франковская область", "Івано-Франківська область"),
    ("TO", "Ivano-Frankivsk", "Iwano-Frankiwsk", "Ивано-Франковск", "Івано-Франківськ",
           "Ivano-Frankivsk Oblast", "Oblast Iwano-Frankiwsk",
           "Ивано-Франковская область", "Івано-Франківська область"),
    ("XC", "Ivano-Frankivsk", "Iwano-Frankiwsk", "Ивано-Франковск", "Івано-Франківськ",
           "Ivano-Frankivsk Oblast", "Oblast Iwano-Frankiwsk",
           "Ивано-Франковская область", "Івано-Франківська область"),
    # --- Kirovohrad Oblast ---
    ("BA", "Kropyvnytskyi", "Kropywnyzkyi", "Кропивницкий", "Кропивницький",
           "Kirovohrad Oblast", "Oblast Kirowohrad",
           "Кировоградская область", "Кіровоградська область"),
    ("HA", "Kropyvnytskyi", "Kropywnyzkyi", "Кропивницкий", "Кропивницький",
           "Kirovohrad Oblast", "Oblast Kirowohrad",
           "Кировоградская область", "Кіровоградська область"),
    ("XA", "Kropyvnytskyi", "Kropywnyzkyi", "Кропивницкий", "Кропивницький",
           "Kirovohrad Oblast", "Oblast Kirowohrad",
           "Кировоградская область", "Кіровоградська область"),
    ("EA", "Kropyvnytskyi", "Kropywnyzkyi", "Кропивницкий", "Кропивницький",
           "Kirovohrad Oblast", "Oblast Kirowohrad",
           "Кировоградская область", "Кіровоградська область"),
    # --- Luhansk Oblast ---
    ("BB", "Luhansk", "Luhansk", "Луганск", "Луганськ",
           "Luhansk Oblast", "Oblast Luhansk", "Луганская область", "Луганська область"),
    ("HB", "Luhansk", "Luhansk", "Луганск", "Луганськ",
           "Luhansk Oblast", "Oblast Luhansk", "Луганская область", "Луганська область"),
    ("EE", "Luhansk", "Luhansk", "Луганск", "Луганськ",
           "Luhansk Oblast", "Oblast Luhansk", "Луганская область", "Луганська область"),
    ("EB", "Luhansk", "Luhansk", "Луганск", "Луганськ",
           "Luhansk Oblast", "Oblast Luhansk", "Луганская область", "Луганська область"),
    # --- Lviv Oblast ---
    ("BC", "Lviv", "Lemberg", "Львов", "Львів",
           "Lviv Oblast", "Oblast Lemberg", "Львовская область", "Львівська область"),
    ("HC", "Lviv", "Lemberg", "Львов", "Львів",
           "Lviv Oblast", "Oblast Lemberg", "Львовская область", "Львівська область"),
    ("CC", "Lviv", "Lemberg", "Львов", "Львів",
           "Lviv Oblast", "Oblast Lemberg", "Львовская область", "Львівська область"),
    ("EC", "Lviv", "Lemberg", "Львов", "Львів",
           "Lviv Oblast", "Oblast Lemberg", "Львовская область", "Львівська область"),
    # --- Mykolaiv Oblast ---
    ("BE", "Mykolaiv", "Mykolajiw", "Николаев", "Миколаїв",
           "Mykolaiv Oblast", "Oblast Mykolajiw",
           "Николаевская область", "Миколаївська область"),
    ("HE", "Mykolaiv", "Mykolajiw", "Николаев", "Миколаїв",
           "Mykolaiv Oblast", "Oblast Mykolajiw",
           "Николаевская область", "Миколаївська область"),
    ("XE", "Mykolaiv", "Mykolajiw", "Николаев", "Миколаїв",
           "Mykolaiv Oblast", "Oblast Mykolajiw",
           "Николаевская область", "Миколаївська область"),
    ("XH", "Mykolaiv", "Mykolajiw", "Николаев", "Миколаїв",
           "Mykolaiv Oblast", "Oblast Mykolajiw",
           "Николаевская область", "Миколаївська область"),
    # --- Odessa Oblast ---
    ("BH", "Odessa", "Odessa", "Одесса", "Одеса",
           "Odessa Oblast", "Oblast Odessa", "Одесская область", "Одеська область"),
    ("HH", "Odessa", "Odessa", "Одесса", "Одеса",
           "Odessa Oblast", "Oblast Odessa", "Одесская область", "Одеська область"),
    ("OO", "Odessa", "Odessa", "Одесса", "Одеса",
           "Odessa Oblast", "Oblast Odessa", "Одесская область", "Одеська область"),
    ("EH", "Odessa", "Odessa", "Одесса", "Одеса",
           "Odessa Oblast", "Oblast Odessa", "Одесская область", "Одеська область"),
    # --- Poltava Oblast ---
    ("BI", "Poltava", "Poltawa", "Полтава", "Полтава",
           "Poltava Oblast", "Oblast Poltawa", "Полтавская область", "Полтавська область"),
    ("HI", "Poltava", "Poltawa", "Полтава", "Полтава",
           "Poltava Oblast", "Oblast Poltawa", "Полтавская область", "Полтавська область"),
    ("XI", "Poltava", "Poltawa", "Полтава", "Полтава",
           "Poltava Oblast", "Oblast Poltawa", "Полтавская область", "Полтавська область"),
    ("EI", "Poltava", "Poltawa", "Полтава", "Полтава",
           "Poltava Oblast", "Oblast Poltawa", "Полтавская область", "Полтавська область"),
    # --- Rivne Oblast ---
    ("BK", "Rivne", "Riwne", "Ровно", "Рівне",
           "Rivne Oblast", "Oblast Riwne", "Ровненская область", "Рівненська область"),
    ("HK", "Rivne", "Riwne", "Ровно", "Рівне",
           "Rivne Oblast", "Oblast Riwne", "Ровненская область", "Рівненська область"),
    ("XK", "Rivne", "Riwne", "Ровно", "Рівне",
           "Rivne Oblast", "Oblast Riwne", "Ровненская область", "Рівненська область"),
    ("EK", "Rivne", "Riwne", "Ровно", "Рівне",
           "Rivne Oblast", "Oblast Riwne", "Ровненская область", "Рівненська область"),
    # --- Sevastopol ---
    ("CH", "Sevastopol", "Sewastopol", "Севастополь", "Севастополь",
           "Sevastopol", "Sewastopol", "Севастополь", "Севастополь"),
    ("IH", "Sevastopol", "Sewastopol", "Севастополь", "Севастополь",
           "Sevastopol", "Sewastopol", "Севастополь", "Севастополь"),
    ("OH", "Sevastopol", "Sewastopol", "Севастополь", "Севастополь",
           "Sevastopol", "Sewastopol", "Севастополь", "Севастополь"),
    ("PH", "Sevastopol", "Sewastopol", "Севастополь", "Севастополь",
           "Sevastopol", "Sewastopol", "Севастополь", "Севастополь"),
    # --- Sumy Oblast ---
    ("BM", "Sumy", "Sumy", "Сумы", "Суми",
           "Sumy Oblast", "Oblast Sumy", "Сумская область", "Сумська область"),
    ("HM", "Sumy", "Sumy", "Сумы", "Суми",
           "Sumy Oblast", "Oblast Sumy", "Сумская область", "Сумська область"),
    ("XM", "Sumy", "Sumy", "Сумы", "Суми",
           "Sumy Oblast", "Oblast Sumy", "Сумская область", "Сумська область"),
    ("EM", "Sumy", "Sumy", "Сумы", "Суми",
           "Sumy Oblast", "Oblast Sumy", "Сумская область", "Сумська область"),
    # --- Ternopil Oblast ---
    ("BO", "Ternopil", "Ternopil", "Тернополь", "Тернопіль",
           "Ternopil Oblast", "Oblast Ternopil",
           "Тернопольская область", "Тернопільська область"),
    ("HO", "Ternopil", "Ternopil", "Тернополь", "Тернопіль",
           "Ternopil Oblast", "Oblast Ternopil",
           "Тернопольская область", "Тернопільська область"),
    ("XO", "Ternopil", "Ternopil", "Тернополь", "Тернопіль",
           "Ternopil Oblast", "Oblast Ternopil",
           "Тернопольская область", "Тернопільська область"),
    ("EO", "Ternopil", "Ternopil", "Тернополь", "Тернопіль",
           "Ternopil Oblast", "Oblast Ternopil",
           "Тернопольская область", "Тернопільська область"),
    # --- Kharkiv Oblast ---
    ("AX", "Kharkiv", "Charkiw", "Харьков", "Харків",
           "Kharkiv Oblast", "Oblast Charkiw", "Харьковская область", "Харківська область"),
    ("KX", "Kharkiv", "Charkiw", "Харьков", "Харків",
           "Kharkiv Oblast", "Oblast Charkiw", "Харьковская область", "Харківська область"),
    ("XX", "Kharkiv", "Charkiw", "Харьков", "Харків",
           "Kharkiv Oblast", "Oblast Charkiw", "Харьковская область", "Харківська область"),
    ("EX", "Kharkiv", "Charkiw", "Харьков", "Харків",
           "Kharkiv Oblast", "Oblast Charkiw", "Харьковская область", "Харківська область"),
    # --- Kherson Oblast ---
    ("BT", "Kherson", "Cherson", "Херсон", "Херсон",
           "Kherson Oblast", "Oblast Cherson", "Херсонская область", "Херсонська область"),
    ("HT", "Kherson", "Cherson", "Херсон", "Херсон",
           "Kherson Oblast", "Oblast Cherson", "Херсонская область", "Херсонська область"),
    ("XT", "Kherson", "Cherson", "Херсон", "Херсон",
           "Kherson Oblast", "Oblast Cherson", "Херсонская область", "Херсонська область"),
    ("ET", "Kherson", "Cherson", "Херсон", "Херсон",
           "Kherson Oblast", "Oblast Cherson", "Херсонская область", "Херсонська область"),
    # --- Khmelnytskyi Oblast ---
    ("BX", "Khmelnytskyi", "Chmelnyzkyj", "Хмельницкий", "Хмельницький",
           "Khmelnytskyi Oblast", "Oblast Chmelnyzkyj",
           "Хмельницкая область", "Хмельницька область"),
    ("HX", "Khmelnytskyi", "Chmelnyzkyj", "Хмельницкий", "Хмельницький",
           "Khmelnytskyi Oblast", "Oblast Chmelnyzkyj",
           "Хмельницкая область", "Хмельницька область"),
    ("OX", "Khmelnytskyi", "Chmelnyzkyj", "Хмельницкий", "Хмельницький",
           "Khmelnytskyi Oblast", "Oblast Chmelnyzkyj",
           "Хмельницкая область", "Хмельницька область"),
    ("PX", "Khmelnytskyi", "Chmelnyzkyj", "Хмельницкий", "Хмельницький",
           "Khmelnytskyi Oblast", "Oblast Chmelnyzkyj",
           "Хмельницкая область", "Хмельницька область"),
    # --- Cherkasy Oblast ---
    ("CA", "Cherkasy", "Tscherkassy", "Черкассы", "Черкаси",
           "Cherkasy Oblast", "Oblast Tscherkassy",
           "Черкасская область", "Черкаська область"),
    ("IA", "Cherkasy", "Tscherkassy", "Черкассы", "Черкаси",
           "Cherkasy Oblast", "Oblast Tscherkassy",
           "Черкасская область", "Черкаська область"),
    ("OA", "Cherkasy", "Tscherkassy", "Черкассы", "Черкаси",
           "Cherkasy Oblast", "Oblast Tscherkassy",
           "Черкасская область", "Черкаська область"),
    ("PA", "Cherkasy", "Tscherkassy", "Черкассы", "Черкаси",
           "Cherkasy Oblast", "Oblast Tscherkassy",
           "Черкасская область", "Черкаська область"),
    # --- Chernihiv Oblast ---
    ("CB", "Chernihiv", "Tschernihiw", "Чернигов", "Чернігів",
           "Chernihiv Oblast", "Oblast Tschernihiw",
           "Черниговская область", "Чернігівська область"),
    ("IB", "Chernihiv", "Tschernihiw", "Чернигов", "Чернігів",
           "Chernihiv Oblast", "Oblast Tschernihiw",
           "Черниговская область", "Чернігівська область"),
    ("OB", "Chernihiv", "Tschernihiw", "Чернигов", "Чернігів",
           "Chernihiv Oblast", "Oblast Tschernihiw",
           "Черниговская область", "Чернігівська область"),
    ("PB", "Chernihiv", "Tschernihiw", "Чернигов", "Чернігів",
           "Chernihiv Oblast", "Oblast Tschernihiw",
           "Черниговская область", "Чернігівська область"),
    # --- Chernivtsi Oblast ---
    ("CE", "Chernivtsi", "Czernowitz", "Черновцы", "Чернівці",
           "Chernivtsi Oblast", "Oblast Czernowitz",
           "Черновицкая область", "Чернівецька область"),
    ("IE", "Chernivtsi", "Czernowitz", "Черновцы", "Чернівці",
           "Chernivtsi Oblast", "Oblast Czernowitz",
           "Черновицкая область", "Чернівецька область"),
    ("OE", "Chernivtsi", "Czernowitz", "Черновцы", "Чернівці",
           "Chernivtsi Oblast", "Oblast Czernowitz",
           "Черновицкая область", "Чернівецька область"),
    ("PE", "Chernivtsi", "Czernowitz", "Черновцы", "Чернівці",
           "Chernivtsi Oblast", "Oblast Czernowitz",
           "Черновицкая область", "Чернівецька область"),
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
    """Insert the UA country record and its translations.

    Args:
        conn: An open SQLite connection (foreign keys must be on).
    """
    country_id = _get_or_insert_country(conn)
    _insert_country_translations(conn, country_id)
    logger.info("Seeded country UA (id=%d)", country_id)


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
    row: tuple[str, str, str, str, str, str, str, str, str],
    coords: tuple[float, float] | None,
) -> None:
    """Insert one region and its 8 translations (4 name + 4 region_group)."""
    plate_code, n_en, n_de, n_ru, n_uk, g_en, g_de, g_ru, g_uk = row
    lat = coords[0] if coords else None
    lon = coords[1] if coords else None
    conn.execute(
        "INSERT OR IGNORE INTO regions"
        " (country_id, plate_code, latitude, longitude) VALUES (?, ?, ?, ?)",
        (country_id, plate_code.upper(), lat, lon),
    )
    conn.execute(
        "UPDATE regions SET latitude = ?, longitude = ?"
        " WHERE country_id = ? AND plate_code = ? AND latitude IS NULL",
        (lat, lon, country_id, plate_code.upper()),
    )
    result = conn.execute(
        "SELECT id FROM regions WHERE country_id = ? AND plate_code = ?",
        (country_id, plate_code.upper()),
    ).fetchone()
    name_trans = {"en": n_en, "de": n_de, "ru": n_ru, "uk": n_uk}
    group_trans = {"en": g_en, "de": g_de, "ru": g_ru, "uk": g_uk}
    _insert_region_translations(conn, result[0], name_trans, group_trans)


def _delete_ua_regions(conn: sqlite3.Connection) -> None:
    """Delete all existing UA regions and their translations to allow re-seeding."""
    row = conn.execute("SELECT id FROM countries WHERE code = ?", (COUNTRY_CODE,)).fetchone()
    if row is None:
        return
    country_id: int = row[0]
    region_ids = [
        r[0] for r in conn.execute(
            "SELECT id FROM regions WHERE country_id = ?", (country_id,)
        ).fetchall()
    ]
    if region_ids:
        placeholders = ",".join("?" * len(region_ids))
        conn.execute(
            f"DELETE FROM translations WHERE entity_type = 'region' AND entity_id IN ({placeholders})",
            region_ids,
        )
        conn.execute("DELETE FROM regions WHERE country_id = ?", (country_id,))
    logger.info("Deleted %d existing UA region rows", len(region_ids))


def seed_regions(conn: sqlite3.Connection) -> None:
    """Delete existing UA regions and re-seed all region records with translations.

    Args:
        conn: An open SQLite connection.
    """
    _delete_ua_regions(conn)
    result = conn.execute("SELECT id FROM countries WHERE code = ?", (COUNTRY_CODE,)).fetchone()
    country_id: int = result[0]
    for region_row in _REGIONS:
        coords = _COORDS.get(region_row[0].upper())
        _seed_single_region(conn, country_id, region_row, coords)
    logger.info("Seeded %d UA regions", len(_REGIONS))


def run(conn: sqlite3.Connection) -> None:
    """Run the full Ukraine seed: country + all regions.

    Args:
        conn: An open SQLite connection.
    """
    seed_country(conn)
    seed_regions(conn)


def main() -> None:
    """Open the production DB, seed Ukraine, and close."""
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s — %(message)s")
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    try:
        run(conn)
        conn.commit()
        logger.info("Ukraine seed complete")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
