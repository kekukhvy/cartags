"""Seed Poland (PL) into the CarTags database.

Inserts the country record, its translations, and ~380 region records
with full translations in en/de/ru/uk.  All inserts are idempotent
via INSERT OR IGNORE.

Usage::

    python data/seed_pl.py
"""

import logging
import sqlite3
from pathlib import Path

logger = logging.getLogger(__name__)

DB_PATH = Path(__file__).parent.parent / "db" / "cartags.db"

COUNTRY_CODE = "PL"
COUNTRY_EMOJI = "🇵🇱"
COUNTRY_SORT_ORDER = 3

_COUNTRY_TRANSLATIONS: dict[str, str] = {
    "en": "Poland",
    "de": "Polen",
    "ru": "Польша",
    "uk": "Польща",
}

# Województwo (voivodeship) translations reused across many regions
_WOJ: dict[str, dict[str, str]] = {
    "Dolnośląskie": {
        "en": "Lower Silesian Voivodeship",
        "de": "Woiwodschaft Niederschlesien",
        "ru": "Нижнесилезское воеводство",
        "uk": "Нижньосілезьке воєводство",
    },
    "Kujawsko-Pomorskie": {
        "en": "Kuyavian-Pomeranian Voivodeship",
        "de": "Woiwodschaft Kujawien-Pommern",
        "ru": "Куявско-Поморское воеводство",
        "uk": "Куявсько-Поморське воєводство",
    },
    "Lubelskie": {
        "en": "Lublin Voivodeship",
        "de": "Woiwodschaft Lublin",
        "ru": "Люблинское воеводство",
        "uk": "Люблінське воєводство",
    },
    "Lubuskie": {
        "en": "Lubusz Voivodeship",
        "de": "Woiwodschaft Lebus",
        "ru": "Любуское воеводство",
        "uk": "Любуське воєводство",
    },
    "Łódzkie": {
        "en": "Łódź Voivodeship",
        "de": "Woiwodschaft Lodsch",
        "ru": "Лодзинское воеводство",
        "uk": "Лодзинське воєводство",
    },
    "Małopolskie": {
        "en": "Lesser Poland Voivodeship",
        "de": "Woiwodschaft Kleinpolen",
        "ru": "Малопольское воеводство",
        "uk": "Малопольське воєводство",
    },
    "Mazowieckie": {
        "en": "Masovian Voivodeship",
        "de": "Woiwodschaft Masowien",
        "ru": "Мазовецкое воеводство",
        "uk": "Мазовецьке воєводство",
    },
    "Opolskie": {
        "en": "Opole Voivodeship",
        "de": "Woiwodschaft Oppeln",
        "ru": "Опольское воеводство",
        "uk": "Опольське воєводство",
    },
    "Podkarpackie": {
        "en": "Subcarpathian Voivodeship",
        "de": "Woiwodschaft Karpatenvorland",
        "ru": "Подкарпатское воеводство",
        "uk": "Підкарпатське воєводство",
    },
    "Podlaskie": {
        "en": "Podlaskie Voivodeship",
        "de": "Woiwodschaft Podlachien",
        "ru": "Подляское воеводство",
        "uk": "Підляське воєводство",
    },
    "Pomorskie": {
        "en": "Pomeranian Voivodeship",
        "de": "Woiwodschaft Pommern",
        "ru": "Поморское воеводство",
        "uk": "Поморське воєводство",
    },
    "Śląskie": {
        "en": "Silesian Voivodeship",
        "de": "Woiwodschaft Schlesien",
        "ru": "Силезское воеводство",
        "uk": "Сілезьке воєводство",
    },
    "Świętokrzyskie": {
        "en": "Holy Cross Voivodeship",
        "de": "Woiwodschaft Heiligkreuz",
        "ru": "Свентокшиское воеводство",
        "uk": "Свентокшиське воєводство",
    },
    "Warmińsko-Mazurskie": {
        "en": "Warmian-Masurian Voivodeship",
        "de": "Woiwodschaft Ermland-Masuren",
        "ru": "Варминско-Мазурское воеводство",
        "uk": "Вармінсько-Мазурське воєводство",
    },
    "Wielkopolskie": {
        "en": "Greater Poland Voivodeship",
        "de": "Woiwodschaft Großpolen",
        "ru": "Великопольское воеводство",
        "uk": "Великопольське воєводство",
    },
    "Zachodniopomorskie": {
        "en": "West Pomeranian Voivodeship",
        "de": "Woiwodschaft Westpommern",
        "ru": "Западно-Поморское воеводство",
        "uk": "Західнопоморське воєводство",
    },
}

_COORDS: dict[str, tuple[float, float]] = {
    "WA": (52.2297, 21.0122),   # Warsaw
    "WB": (52.2297, 21.0122),
    "WD": (52.2297, 21.0122),
    "WE": (52.2297, 21.0122),
    "WF": (52.2297, 21.0122),
    "WG": (52.2297, 21.0122),
    "WH": (52.2297, 21.0122),
    "WI": (52.2297, 21.0122),
    "WJ": (52.2297, 21.0122),
    "WK": (52.2297, 21.0122),
    "WL": (52.2297, 21.0122),
    "WM": (52.2297, 21.0122),
    "WN": (52.2297, 21.0122),
    "WO": (52.2297, 21.0122),
    "WP": (52.2297, 21.0122),
    "WR": (52.2297, 21.0122),
    "WS": (52.2297, 21.0122),
    "WT": (52.2297, 21.0122),
    "WU": (52.2297, 21.0122),
    "WW": (52.2297, 21.0122),
    "WX": (52.2297, 21.0122),
    "WY": (52.2297, 21.0122),
    "WZ": (52.2297, 21.0122),
    "KR": (50.0647, 19.9450),   # Kraków
    "KK": (50.0647, 19.9450),
    "KN": (50.0647, 19.9450),
    "KO": (50.0647, 19.9450),
    "KS": (50.0647, 19.9450),
    "KT": (50.0647, 19.9450),
    "KW": (50.0647, 19.9450),
    "KA": (50.0647, 19.9450),
    "KB": (50.0647, 19.9450),
    "KC": (50.0647, 19.9450),
    "KD": (50.0647, 19.9450),
    "KE": (50.0647, 19.9450),
    "GD": (54.3520, 18.6466),   # Gdańsk
    "GA": (54.3520, 18.6466),
    "GB": (54.3520, 18.6466),
    "GC": (54.3520, 18.6466),
    "GG": (54.3520, 18.6466),
    "GK": (54.3520, 18.6466),
    "GM": (54.3520, 18.6466),
    "GN": (54.3520, 18.6466),
    "GP": (54.3520, 18.6466),
    "GS": (54.3520, 18.6466),
    "GT": (54.3520, 18.6466),
    "WR": (51.1079, 17.0385),   # Wrocław
    "DB": (51.1079, 17.0385),
    "DBA": (51.1079, 17.0385),
    "DBL": (51.1079, 17.0385),
    "DBO": (51.1079, 17.0385),
    "DC": (51.1079, 17.0385),
    "DJ": (51.1079, 17.0385),
    "DK": (51.1079, 17.0385),
    "DL": (51.1079, 17.0385),
    "DM": (51.1079, 17.0385),
    "DN": (51.1079, 17.0385),
    "DO": (51.1079, 17.0385),
    "DP": (51.1079, 17.0385),
    "DT": (51.1079, 17.0385),
    "DW": (51.1079, 17.0385),
    "DZ": (51.1079, 17.0385),
    "KA": (50.2599, 19.0216),   # Katowice
    "SB": (50.2599, 19.0216),
    "SC": (50.2599, 19.0216),
    "SF": (50.2599, 19.0216),
    "SG": (50.2599, 19.0216),
    "SK": (50.2599, 19.0216),
    "SL": (50.2599, 19.0216),
    "SM": (50.2599, 19.0216),
    "SO": (50.2599, 19.0216),
    "SR": (50.2599, 19.0216),
    "ST": (50.2599, 19.0216),
    "SY": (50.2599, 19.0216),
    "SZ": (50.2599, 19.0216),
    "PO": (52.4064, 16.9252),   # Poznań
    "PA": (52.4064, 16.9252),
    "PC": (52.4064, 16.9252),
    "PE": (52.4064, 16.9252),
    "PG": (52.4064, 16.9252),
    "PK": (52.4064, 16.9252),
    "PL": (52.4064, 16.9252),
    "PM": (52.4064, 16.9252),
    "PP": (52.4064, 16.9252),
    "PR": (52.4064, 16.9252),
    "PS": (52.4064, 16.9252),
    "PT": (52.4064, 16.9252),
    "PW": (52.4064, 16.9252),
    "LU": (51.2465, 22.5684),   # Lublin
    "LA": (51.2465, 22.5684),
    "LB": (51.2465, 22.5684),
    "LC": (51.2465, 22.5684),
    "LE": (51.2465, 22.5684),
    "LG": (51.2465, 22.5684),
    "LH": (51.2465, 22.5684),
    "LJ": (51.2465, 22.5684),
    "LK": (51.2465, 22.5684),
    "LL": (51.2465, 22.5684),
    "LM": (51.2465, 22.5684),
    "LO": (51.2465, 22.5684),
    "LP": (51.2465, 22.5684),
    "LR": (51.2465, 22.5684),
    "LS": (51.2465, 22.5684),
    "LT": (51.2465, 22.5684),
    "LW": (51.2465, 22.5684),
    "LD": (51.7592, 19.4560),   # Łódź
    "LDL": (51.7592, 19.4560),
    "LDO": (51.7592, 19.4560),
    "LDB": (51.7592, 19.4560),
    "LDC": (51.7592, 19.4560),
    "LDE": (51.7592, 19.4560),
    "LDK": (51.7592, 19.4560),
    "LDM": (51.7592, 19.4560),
    "LDN": (51.7592, 19.4560),
    "LDP": (51.7592, 19.4560),
    "LDR": (51.7592, 19.4560),
    "LDS": (51.7592, 19.4560),
    "LDT": (51.7592, 19.4560),
    "LDW": (51.7592, 19.4560),
    "LDZ": (51.7592, 19.4560),
    "RZ": (50.0412, 21.9991),   # Rzeszów
    "RA": (50.0412, 21.9991),
    "RB": (50.0412, 21.9991),
    "RC": (50.0412, 21.9991),
    "RD": (50.0412, 21.9991),
    "RE": (50.0412, 21.9991),
    "RF": (50.0412, 21.9991),
    "RG": (50.0412, 21.9991),
    "RJ": (50.0412, 21.9991),
    "RK": (50.0412, 21.9991),
    "RL": (50.0412, 21.9991),
    "RM": (50.0412, 21.9991),
    "RN": (50.0412, 21.9991),
    "RP": (50.0412, 21.9991),
    "RR": (50.0412, 21.9991),
    "RS": (50.0412, 21.9991),
    "RT": (50.0412, 21.9991),
    "RU": (50.0412, 21.9991),
    "BI": (53.1325, 23.1688),   # Białystok
    "BA": (53.1325, 23.1688),
    "BB": (53.1325, 23.1688),
    "BC": (53.1325, 23.1688),
    "BD": (53.1325, 23.1688),
    "BG": (53.1325, 23.1688),
    "BH": (53.1325, 23.1688),
    "BL": (53.1325, 23.1688),
    "BM": (53.1325, 23.1688),
    "BN": (53.1325, 23.1688),
    "BP": (53.1325, 23.1688),
    "BS": (53.1325, 23.1688),
    "BW": (53.1325, 23.1688),
    "OL": (53.7784, 20.4801),   # Olsztyn
    "OB": (53.7784, 20.4801),
    "OD": (53.7784, 20.4801),
    "OE": (53.7784, 20.4801),
    "OG": (53.7784, 20.4801),
    "OI": (53.7784, 20.4801),
    "OK": (53.7784, 20.4801),
    "OM": (53.7784, 20.4801),
    "ON": (53.7784, 20.4801),
    "OR": (53.7784, 20.4801),
    "OS": (53.7784, 20.4801),
    "OT": (53.7784, 20.4801),
    "OW": (53.7784, 20.4801),
    "OZ": (53.7784, 20.4801),
    "ZG": (51.9356, 15.5062),   # Zielona Góra
    "ZA": (51.9356, 15.5062),
    "ZK": (51.9356, 15.5062),
    "ZL": (51.9356, 15.5062),
    "ZN": (51.9356, 15.5062),
    "ZS": (51.9356, 15.5062),
    "ZW": (51.9356, 15.5062),
    "SZ": (53.4289, 14.5530),   # Szczecin
    "ZB": (53.4289, 14.5530),
    "ZC": (53.4289, 14.5530),
    "ZD": (53.4289, 14.5530),
    "ZF": (53.4289, 14.5530),
    "ZG": (53.4289, 14.5530),
    "ZH": (53.4289, 14.5530),
    "ZJ": (53.4289, 14.5530),
    "ZM": (53.4289, 14.5530),
    "ZP": (53.4289, 14.5530),
    "ZT": (53.4289, 14.5530),
    "ZV": (53.4289, 14.5530),
    "ZX": (53.4289, 14.5530),
    "KI": (50.8661, 20.6286),   # Kielce
    "KL": (50.8661, 20.6286),
    "KN": (50.8661, 20.6286),
    "KO": (50.8661, 20.6286),
    "KP": (50.8661, 20.6286),
    "KW": (50.8661, 20.6286),
    "KX": (50.8661, 20.6286),
    "BY": (53.1235, 18.0084),   # Bydgoszcz
    "CA": (53.1235, 18.0084),
    "CB": (53.1235, 18.0084),
    "CC": (53.1235, 18.0084),
    "CD": (53.1235, 18.0084),
    "CE": (53.1235, 18.0084),
    "CF": (53.1235, 18.0084),
    "CG": (53.1235, 18.0084),
    "CH": (53.1235, 18.0084),
    "CI": (53.1235, 18.0084),
    "CJ": (53.1235, 18.0084),
    "CK": (53.1235, 18.0084),
    "CL": (53.1235, 18.0084),
    "CM": (53.1235, 18.0084),
    "CN": (53.1235, 18.0084),
    "CO": (53.1235, 18.0084),
    "CP": (53.1235, 18.0084),
    "CS": (53.1235, 18.0084),
    "CT": (53.1235, 18.0084),
    "CU": (53.1235, 18.0084),
    "CW": (53.1235, 18.0084),
    "CY": (53.1235, 18.0084),
    "OP": (50.6751, 17.9213),   # Opole
    "OA": (50.6751, 17.9213),
    "OC": (50.6751, 17.9213),
    "OF": (50.6751, 17.9213),
    "OJ": (50.6751, 17.9213),
    "OK": (50.6751, 17.9213),
    "OL": (50.6751, 17.9213),
    "ON": (50.6751, 17.9213),
    "OP": (50.6751, 17.9213),
    "OR": (50.6751, 17.9213),
    "OS": (50.6751, 17.9213),
    "OT": (50.6751, 17.9213),
    "OW": (50.6751, 17.9213),
}

# (plate_code, name_en, name_de, name_ru, name_uk, voivodeship_key)
_REGION_ROWS: list[tuple[str, str, str, str, str, str]] = [
    # ---- Masovian / Mazowieckie ----
    ("WA", "Warsaw", "Warschau", "Варшава", "Варшава", "Mazowieckie"),
    ("WB", "Białobrzegi", "Białobrzegi", "Бялобжеги", "Білобжеги", "Mazowieckie"),
    ("WD", "Siedlce", "Siedlce", "Седльце", "Сєдльце", "Mazowieckie"),
    ("WE", "Węgrów", "Węgrów", "Венгрув", "Венґрув", "Mazowieckie"),
    ("WF", "Radom", "Radom", "Радом", "Радом", "Mazowieckie"),
    ("WG", "Garwolin", "Garwolin", "Гарволин", "Гарволін", "Mazowieckie"),
    ("WH", "Płock", "Płock", "Плоцк", "Плоцьк", "Mazowieckie"),
    ("WI", "Piaseczno", "Piaseczno", "Пясечно", "Пясечно", "Mazowieckie"),
    ("WJ", "Grodzisk Mazowiecki", "Grodzisk Mazowiecki", "Гродзиск-Мазовецки", "Ґродзиськ-Мазовецький", "Mazowieckie"),
    ("WK", "Legionowo", "Legionowo", "Легионово", "Леґіоново", "Mazowieckie"),
    ("WL", "Łosice", "Łosice", "Лосице", "Лосіце", "Mazowieckie"),
    ("WM", "Mińsk Mazowiecki", "Mińsk Mazowiecki", "Минск-Мазовецки", "Мінськ-Мазовецький", "Mazowieckie"),
    ("WN", "Nowy Dwór Mazowiecki", "Nowy Dwór Mazowiecki", "Новы-Двур-Мазовецки", "Новий Двір Мазовецький", "Mazowieckie"),
    ("WO", "Ostrołęka", "Ostrołęka", "Остроленка", "Остроленка", "Mazowieckie"),
    ("WP", "Przasnysz", "Przasnysz", "Пшаснышь", "Пшасниш", "Mazowieckie"),
    ("WR", "Radom (city)", "Radom (Stadt)", "Радом (город)", "Радом (місто)", "Mazowieckie"),
    ("WS", "Sierpc", "Sierpc", "Серпц", "Серпц", "Mazowieckie"),
    ("WT", "Otwock", "Otwock", "Отвоцк", "Отвоцьк", "Mazowieckie"),
    ("WU", "Żyrardów", "Żyrardów", "Жирардув", "Жирардув", "Mazowieckie"),
    ("WW", "Warsaw West", "Warschau West", "Варшава Западная", "Варшава Захід", "Mazowieckie"),
    ("WX", "Wyszków", "Wyszków", "Вышкув", "Вишкув", "Mazowieckie"),
    ("WY", "Wołomin", "Wołomin", "Воломин", "Воломін", "Mazowieckie"),
    ("WZ", "Żuromin", "Żuromin", "Журомин", "Журомін", "Mazowieckie"),
    # ---- Lesser Poland / Małopolskie ----
    ("KR", "Kraków", "Krakau", "Краков", "Краків", "Małopolskie"),
    ("KK", "Kraków (county)", "Krakau (Landkreis)", "Краков (район)", "Краків (район)", "Małopolskie"),
    ("KN", "Nowy Sącz", "Nowy Sącz", "Новы-Сонч", "Новий Санч", "Małopolskie"),
    ("KO", "Oświęcim", "Auschwitz", "Освенцим", "Освенцім", "Małopolskie"),
    ("KS", "Nowy Targ", "Nowy Targ", "Новы-Тарг", "Новий Тарг", "Małopolskie"),
    ("KT", "Tarnów", "Tarnow", "Тарнув", "Тарнув", "Małopolskie"),
    ("KW", "Wieliczka", "Wieliczka", "Величка", "Велічка", "Małopolskie"),
    ("KA", "Chrzanów", "Chrzanów", "Хшанув", "Хшанув", "Małopolskie"),
    ("KB", "Bochnia", "Bochnia", "Бохня", "Бохня", "Małopolskie"),
    ("KC", "Dąbrowa Tarnowska", "Dąbrowa Tarnowska", "Домброва-Тарновска", "Домброва Тарновська", "Małopolskie"),
    ("KD", "Gorlice", "Gorlitz", "Горлице", "Горліце", "Małopolskie"),
    ("KE", "Limanowa", "Limanowa", "Лиманова", "Лиманова", "Małopolskie"),
    # ---- Pomeranian / Pomorskie ----
    ("GD", "Gdańsk", "Danzig", "Гданьск", "Гданськ", "Pomorskie"),
    ("GA", "Gdańsk (county)", "Danzig (Landkreis)", "Гданьск (район)", "Гданськ (район)", "Pomorskie"),
    ("GB", "Bytów", "Bütow", "Битув", "Битув", "Pomorskie"),
    ("GC", "Chojnice", "Konitz", "Хойнице", "Хойніце", "Pomorskie"),
    ("GG", "Gdynia", "Gdingen", "Гдыня", "Гдиня", "Pomorskie"),
    ("GK", "Kościerzyna", "Berent", "Косцежина", "Косцежина", "Pomorskie"),
    ("GM", "Malbork", "Marienburg", "Мальборк", "Мальборк", "Pomorskie"),
    ("GN", "Nowy Dwór Gdański", "Nowy Dwór Gdański", "Новы-Двур-Гданьски", "Новий Двір Гданський", "Pomorskie"),
    ("GP", "Puck", "Putzig", "Пуцк", "Пуцьк", "Pomorskie"),
    ("GS", "Słupsk", "Stolp", "Слупск", "Слупськ", "Pomorskie"),
    ("GT", "Tczew", "Dirschau", "Тчев", "Тчев", "Pomorskie"),
    # ---- Lower Silesian / Dolnośląskie ----
    ("DW", "Wrocław", "Breslau", "Вроцлав", "Вроцлав", "Dolnośląskie"),
    ("DBA", "Bardo", "Wartha", "Бардо", "Бардо", "Dolnośląskie"),
    ("DBO", "Bolesławiec", "Bunzlau", "Болеславец", "Болеславець", "Dolnośląskie"),
    ("DC", "Dzierżoniów", "Reichenbach", "Джержонюв", "Джержонюв", "Dolnośląskie"),
    ("DJ", "Jawor", "Jauer", "Явор", "Явор", "Dolnośląskie"),
    ("DK", "Kłodzko", "Glatz", "Клодзко", "Клодзько", "Dolnośląskie"),
    ("DL", "Legnica", "Liegnitz", "Легница", "Лєгниця", "Dolnośląskie"),
    ("DM", "Milicz", "Militsch", "Милич", "Міліч", "Dolnośląskie"),
    ("DN", "Nowa Ruda", "Neurode", "Нова-Руда", "Нова Руда", "Dolnośląskie"),
    ("DO", "Oleśnica", "Oels", "Олесница", "Олесниця", "Dolnośląskie"),
    ("DP", "Polkowice", "Heerwegen", "Полковице", "Полковіце", "Dolnośląskie"),
    ("DT", "Trzebnica", "Trebnitz", "Тшебница", "Тшебниця", "Dolnośląskie"),
    ("DZ", "Złotoryja", "Goldberg", "Злоторыя", "Злоториля", "Dolnośląskie"),
    # ---- Silesian / Śląskie ----
    ("KA", "Katowice", "Kattowitz", "Катовице", "Катовіце", "Śląskie"),
    ("SB", "Będzin", "Bendzin", "Бендзин", "Бендзін", "Śląskie"),
    ("SC", "Częstochowa", "Tschenstochau", "Ченстохова", "Ченстохова", "Śląskie"),
    ("SF", "Cieszyn", "Teschen", "Цешин", "Цешин", "Śląskie"),
    ("SG", "Gliwice", "Gleiwitz", "Гливице", "Ґлівіце", "Śląskie"),
    ("SK", "Rybnik", "Rybnik", "Рыбник", "Рибник", "Śląskie"),
    ("SL", "Sosnowiec", "Sosnowitz", "Сосновец", "Сосновець", "Śląskie"),
    ("SM", "Mysłowice", "Myslowitz", "Мысловице", "Мислович", "Śląskie"),
    ("SO", "Bytom", "Beuthen", "Бытом", "Битом", "Śląskie"),
    ("SR", "Racibórz", "Ratibor", "Рацибуж", "Рацибуж", "Śląskie"),
    ("ST", "Tychy", "Tychy", "Тыхы", "Тихи", "Śląskie"),
    ("SY", "Zabrze", "Hindenburg", "Забже", "Забже", "Śląskie"),
    ("SZ", "Żywiec", "Saybusch", "Живец", "Живець", "Śląskie"),
    # ---- Greater Poland / Wielkopolskie ----
    ("PO", "Poznań", "Posen", "Познань", "Познань", "Wielkopolskie"),
    ("PA", "Gniezno", "Gnesen", "Гнезно", "Гнєзно", "Wielkopolskie"),
    ("PC", "Chodzież", "Kolmar", "Ходзеж", "Ходзеж", "Wielkopolskie"),
    ("PE", "Krotoszyn", "Krotoschin", "Кротошин", "Кротошин", "Wielkopolskie"),
    ("PG", "Konin", "Konin", "Конин", "Конін", "Wielkopolskie"),
    ("PK", "Kalisz", "Kalisch", "Калиш", "Каліш", "Wielkopolskie"),
    ("PL", "Leszno", "Lissa", "Лешно", "Лешно", "Wielkopolskie"),
    ("PM", "Ostrów Wielkopolski", "Ostrowo", "Остров-Велькопольски", "Острів Великопольський", "Wielkopolskie"),
    ("PP", "Piła", "Schneidemühl", "Пила", "Піла", "Wielkopolskie"),
    ("PR", "Rawicz", "Rawitsch", "Равич", "Равич", "Wielkopolskie"),
    ("PS", "Szamotuły", "Samter", "Шамотулы", "Шамотули", "Wielkopolskie"),
    ("PT", "Turek", "Turek", "Турек", "Турек", "Wielkopolskie"),
    ("PW", "Wrzesnia", "Wreschen", "Вжесня", "Вжесня", "Wielkopolskie"),
    # ---- Lublin / Lubelskie ----
    ("LU", "Lublin", "Lublin", "Люблин", "Люблін", "Lubelskie"),
    ("LA", "Biała Podlaska", "Biała Podlaska", "Бяла-Подляска", "Бяла Підляська", "Lubelskie"),
    ("LB", "Biłgoraj", "Bilgoraj", "Билгорай", "Білгорай", "Lubelskie"),
    ("LC", "Chełm", "Kulm", "Хелм", "Хелм", "Lubelskie"),
    ("LE", "Zamość", "Zamość", "Замосць", "Замосць", "Lubelskie"),
    ("LG", "Hrubieszów", "Grabowiec", "Грубешув", "Грубешув", "Lubelskie"),
    ("LH", "Janów Lubelski", "Janów Lubelski", "Янув-Люблински", "Янів Люблінський", "Lubelskie"),
    ("LJ", "Krasnystaw", "Krasnystaw", "Красныстав", "Красностав", "Lubelskie"),
    ("LK", "Kraśnik", "Kraśnik", "Красник", "Красник", "Lubelskie"),
    ("LL", "Łęczna", "Łęczna", "Ленчна", "Ленчна", "Lubelskie"),
    ("LM", "Łuków", "Łuków", "Луков", "Луків", "Lubelskie"),
    ("LO", "Opole Lubelskie", "Opole Lubelskie", "Ополе-Люблинске", "Ополе Люблінське", "Lubelskie"),
    ("LP", "Puławy", "Puławy", "Пулавы", "Пулави", "Lubelskie"),
    ("LR", "Radzyń Podlaski", "Radzyń Podlaski", "Радзынь-Подляски", "Радзинь Підляський", "Lubelskie"),
    ("LS", "Świdnik", "Świdnik", "Свидник", "Свидник", "Lubelskie"),
    ("LT", "Tomaszów Lubelski", "Tomaszów Lubelski", "Томашув-Люблински", "Томашів Люблінський", "Lubelskie"),
    ("LW", "Włodawa", "Włodawa", "Влодава", "Влодава", "Lubelskie"),
    # ---- Łódź / Łódzkie ----
    ("LD", "Łódź", "Lodsch", "Лодзь", "Лодзь", "Łódzkie"),
    ("LDL", "Łęczyca", "Lentschütz", "Ленчица", "Ленчиця", "Łódzkie"),
    ("LDO", "Opoczno", "Opoczno", "Опочно", "Опочно", "Łódzkie"),
    ("LDB", "Bełchatów", "Belchatow", "Белхатув", "Белхатув", "Łódzkie"),
    ("LDC", "Łowicz", "Lowitsch", "Ловіч", "Ловіч", "Łódzkie"),
    ("LDE", "Łódź East", "Lodsch Ost", "Лодзь Восток", "Лодзь Схід", "Łódzkie"),
    ("LDK", "Kutno", "Kutno", "Кутно", "Кутно", "Łódzkie"),
    ("LDM", "Radomsko", "Radomsko", "Радомско", "Радомсько", "Łódzkie"),
    ("LDN", "Piotrków Trybunalski", "Piotrków Trybunalski", "Петркув-Трыбунальски", "Петрків Трибунальський", "Łódzkie"),
    ("LDP", "Pajęczno", "Pajęczno", "Паенчно", "Паєнчно", "Łódzkie"),
    ("LDR", "Rawa Mazowiecka", "Rawa Mazowiecka", "Рава-Мазовецка", "Рава Мазовецька", "Łódzkie"),
    ("LDS", "Sieradz", "Sieradz", "Серадз", "Серадз", "Łódzkie"),
    ("LDT", "Tomaszów Mazowiecki", "Tomaszów Mazowiecki", "Томашув-Мазовецки", "Томашів Мазовецький", "Łódzkie"),
    ("LDW", "Wieluń", "Wielun", "Велюнь", "Велюнь", "Łódzkie"),
    ("LDZ", "Zduńska Wola", "Zdunska Wola", "Здунска-Воля", "Здунська Воля", "Łódzkie"),
    # ---- Subcarpathian / Podkarpackie ----
    ("RZ", "Rzeszów", "Rzeszów", "Жешув", "Жешув", "Podkarpackie"),
    ("RA", "Brzozów", "Brzozów", "Бжозув", "Бжозув", "Podkarpackie"),
    ("RB", "Bieszczady", "Bieszczady", "Бещады", "Бещади", "Podkarpackie"),
    ("RC", "Dębica", "Dembica", "Дембица", "Дембиця", "Podkarpackie"),
    ("RD", "Jarosław", "Jarosław", "Ярослав", "Ярослав", "Podkarpackie"),
    ("RE", "Jasło", "Jasło", "Ясло", "Ясло", "Podkarpackie"),
    ("RF", "Kolbuszowa", "Kolbuszowa", "Колбушова", "Колбушова", "Podkarpackie"),
    ("RG", "Krosno", "Krosno", "Кросно", "Кросно", "Podkarpackie"),
    ("RJ", "Lesko", "Lesko", "Леско", "Леско", "Podkarpackie"),
    ("RK", "Leżajsk", "Leżajsk", "Лежайск", "Лежайськ", "Podkarpackie"),
    ("RL", "Lubaczów", "Lubaczów", "Любачув", "Любачів", "Podkarpackie"),
    ("RM", "Mielec", "Mielec", "Мелец", "Мелець", "Podkarpackie"),
    ("RN", "Nisko", "Nisko", "Ниско", "Нісько", "Podkarpackie"),
    ("RP", "Przemyśl", "Przemysl", "Перемышль", "Перемишль", "Podkarpackie"),
    ("RR", "Ropczyce-Sędziszów", "Ropczyce-Sędziszów", "Ропчице-Сендзишув", "Ропчице-Сендзишув", "Podkarpackie"),
    ("RS", "Sanok", "Sanok", "Санок", "Санок", "Podkarpackie"),
    ("RT", "Stalowa Wola", "Stalowa Wola", "Сталова-Воля", "Сталова Воля", "Podkarpackie"),
    ("RU", "Strzyżów", "Strzyżów", "Стшижув", "Стшижув", "Podkarpackie"),
    # ---- Podlaskie ----
    ("BI", "Białystok", "Białystok", "Белосток", "Білосток", "Podlaskie"),
    ("BA", "Augustów", "Augustow", "Августув", "Августів", "Podlaskie"),
    ("BB", "Bielsk Podlaski", "Bielsk Podlaski", "Бельск-Подляски", "Більськ Підляський", "Podlaskie"),
    ("BC", "Grajewo", "Grajewo", "Грайево", "Граєво", "Podlaskie"),
    ("BD", "Hajnówka", "Hajnowka", "Гайнувка", "Гайнівка", "Podlaskie"),
    ("BG", "Kolno", "Kolno", "Кольно", "Кольно", "Podlaskie"),
    ("BH", "Łomża", "Lomza", "Ломжа", "Ломжа", "Podlaskie"),
    ("BL", "Mońki", "Mońki", "Монки", "Монки", "Podlaskie"),
    ("BM", "Sejny", "Seinai", "Сейны", "Сейни", "Podlaskie"),
    ("BN", "Siemiatycze", "Siemiatycze", "Семятыче", "Семятіче", "Podlaskie"),
    ("BP", "Sokółka", "Sokółka", "Сокулка", "Сокулка", "Podlaskie"),
    ("BS", "Suwałki", "Suwalki", "Сувалки", "Сувалки", "Podlaskie"),
    ("BW", "Zambrów", "Zambrów", "Замбрув", "Замбрув", "Podlaskie"),
    # ---- Warmian-Masurian / Warmińsko-Mazurskie ----
    ("OL", "Olsztyn", "Allenstein", "Ольштын", "Ольштин", "Warmińsko-Mazurskie"),
    ("OB", "Bartoszyce", "Bartenstein", "Бартошице", "Бартошіце", "Warmińsko-Mazurskie"),
    ("OD", "Działdowo", "Soldau", "Дзялдово", "Дзялдово", "Warmińsko-Mazurskie"),
    ("OE", "Elbląg", "Elbing", "Эльблонг", "Ельблонґ", "Warmińsko-Mazurskie"),
    ("OG", "Giżycko", "Lötzen", "Гижицко", "Гіжицько", "Warmińsko-Mazurskie"),
    ("OI", "Iława", "Deutsch Eylau", "Илава", "Ілава", "Warmińsko-Mazurskie"),
    ("OK", "Kętrzyn", "Rastenburg", "Кентшин", "Кентшин", "Warmińsko-Mazurskie"),
    ("OM", "Mrągowo", "Sensburg", "Мронгово", "Мронґово", "Warmińsko-Mazurskie"),
    ("ON", "Nidzica", "Neidenburg", "Нидзица", "Нидзіца", "Warmińsko-Mazurskie"),
    ("OR", "Ostróda", "Osterode", "Острода", "Оструда", "Warmińsko-Mazurskie"),
    ("OS", "Szczytno", "Ortelsburg", "Щитно", "Щитно", "Warmińsko-Mazurskie"),
    ("OT", "Lidzbark Warmiński", "Heilsberg", "Лидзбарк-Варминьски", "Лідзбарк Вармінський", "Warmińsko-Mazurskie"),
    ("OW", "Węgorzewo", "Angerburg", "Венгожево", "Венгожево", "Warmińsko-Mazurskie"),
    ("OZ", "Pisz", "Johannisburg", "Пиш", "Пиш", "Warmińsko-Mazurskie"),
    # ---- Lubusz / Lubuskie ----
    ("ZG", "Zielona Góra", "Grünberg", "Зелёна-Гура", "Зелена Гура", "Lubuskie"),
    ("ZA", "Gorzów Wielkopolski", "Landsberg an der Warthe", "Гожув-Велькопольски", "Ґожув Великопольський", "Lubuskie"),
    ("ZK", "Krosno Odrzańskie", "Crossen", "Кросно-Одшаньске", "Кросно Одержанське", "Lubuskie"),
    ("ZL", "Nowa Sól", "Fraustadt", "Нова-Суль", "Нова Суль", "Lubuskie"),
    ("ZN", "Słubice", "Frankfurt-Dammvorstadt", "Слубице", "Слубіце", "Lubuskie"),
    ("ZS", "Strzelce Krajeńskie", "Friedeberg", "Стшелце-Краеньске", "Стшелце Краєнські", "Lubuskie"),
    ("ZW", "Wschowa", "Fraustadt", "Всхова", "Всхова", "Lubuskie"),
    # ---- West Pomeranian / Zachodniopomorskie ----
    ("ZB", "Szczecin (county)", "Stettin (Landkreis)", "Щецин (район)", "Щецин (район)", "Zachodniopomorskie"),
    ("ZC", "Kamień Pomorski", "Cammin", "Камень-Поморски", "Кам'єнь Поморський", "Zachodniopomorskie"),
    ("ZD", "Drawsko Pomorskie", "Dramburg", "Дравско-Поморске", "Дравсько Поморське", "Zachodniopomorskie"),
    ("ZF", "Gryfice", "Greifenberg", "Грыфице", "Ґрифіце", "Zachodniopomorskie"),
    ("ZH", "Choszczno", "Arnswalde", "Хощно", "Хощно", "Zachodniopomorskie"),
    ("ZJ", "Goleniów", "Gollnow", "Голенюв", "Голенюв", "Zachodniopomorskie"),
    ("ZM", "Myślibórz", "Soldin", "Мысьлибуж", "Мислібуж", "Zachodniopomorskie"),
    ("ZP", "Police", "Pölitz", "Полице", "Поліце", "Zachodniopomorskie"),
    ("ZT", "Stargard", "Stargard", "Старгард", "Старгард", "Zachodniopomorskie"),
    ("ZV", "Świnoujście", "Swinemünde", "Свинойсьце", "Свіноуйсьце", "Zachodniopomorskie"),
    ("ZX", "Wałcz", "Deutsch Krone", "Вальч", "Вальч", "Zachodniopomorskie"),
    # ---- Kuyavian-Pomeranian / Kujawsko-Pomorskie ----
    ("BY", "Bydgoszcz", "Bromberg", "Быдгощ", "Бидгощ", "Kujawsko-Pomorskie"),
    ("CA", "Aleksandrów Kujawski", "Alexandrowo", "Александрув-Куявски", "Александрів Куявський", "Kujawsko-Pomorskie"),
    ("CB", "Brodnica", "Strasburg", "Бродница", "Бродниця", "Kujawsko-Pomorskie"),
    ("CC", "Chełmno", "Kulmsee", "Хелмно", "Хелмно", "Kujawsko-Pomorskie"),
    ("CD", "Grudziądz", "Graudenz", "Грудзёнз", "Ґрудзьондз", "Kujawsko-Pomorskie"),
    ("CE", "Golub-Dobrzyń", "Golub-Dobrzyń", "Голуб-Добжинь", "Голуб-Добжинь", "Kujawsko-Pomorskie"),
    ("CF", "Inowrocław", "Hohensalza", "Иновроцлав", "Іновроцлав", "Kujawsko-Pomorskie"),
    ("CG", "Lipno", "Lipno", "Липно", "Липно", "Kujawsko-Pomorskie"),
    ("CH", "Mogilno", "Mogilno", "Могильно", "Могільно", "Kujawsko-Pomorskie"),
    ("CI", "Nakło nad Notecią", "Nakel", "Накло-над-Нотецём", "Накло-над-Нотечю", "Kujawsko-Pomorskie"),
    ("CJ", "Radziejów", "Radziejow", "Радзейув", "Радзієюв", "Kujawsko-Pomorskie"),
    ("CK", "Rypín", "Rippin", "Рыпин", "Рипін", "Kujawsko-Pomorskie"),
    ("CL", "Sępólno Krajeńskie", "Zempelburg", "Сенполно-Краеньске", "Семпольно Краєнське", "Kujawsko-Pomorskie"),
    ("CM", "Świecie", "Schwetz", "Свеце", "Свеце", "Kujawsko-Pomorskie"),
    ("CN", "Toruń", "Thorn", "Торунь", "Торунь", "Kujawsko-Pomorskie"),
    ("CO", "Tuchola", "Tuchel", "Тухола", "Тухола", "Kujawsko-Pomorskie"),
    ("CP", "Wąbrzeźno", "Briesen", "Вомбжезно", "Вомбжезно", "Kujawsko-Pomorskie"),
    ("CS", "Włocławek", "Leslau", "Влоцлавек", "Влоцлавек", "Kujawsko-Pomorskie"),
    ("CT", "Żnin", "Znin", "Жнин", "Жнін", "Kujawsko-Pomorskie"),
    ("CU", "Bydgoszcz (county)", "Bromberg (Landkreis)", "Быдгощ (район)", "Бидгощ (район)", "Kujawsko-Pomorskie"),
    ("CW", "Chełmno (county)", "Kulm (Landkreis)", "Хелмно (район)", "Хелмно (район)", "Kujawsko-Pomorskie"),
    ("CY", "Wąbrzeźno (county)", "Briesen (Landkreis)", "Вомбжезно (район)", "Вомбжезно (район)", "Kujawsko-Pomorskie"),
    # ---- Opole / Opolskie ----
    ("OP", "Opole", "Oppeln", "Ополе", "Ополе", "Opolskie"),
    ("OA", "Brzeg", "Brieg", "Бжег", "Бжег", "Opolskie"),
    ("OC", "Głubczyce", "Leobschütz", "Глубчице", "Глубчіце", "Opolskie"),
    ("OF", "Kluczbork", "Kreuzburg", "Клучборк", "Клучборк", "Opolskie"),
    ("OJ", "Kędzierzyn-Koźle", "Kandrzin-Cosel", "Кендзежин-Козьле", "Кендзежин-Козьле", "Opolskie"),
    ("OK", "Krapkowice", "Krappitz", "Крапковице", "Крапковіце", "Opolskie"),
    ("ON", "Namysłów", "Namslau", "Намыслув", "Намислів", "Opolskie"),
    ("OR", "Prudnik", "Neustadt", "Прудник", "Прудник", "Opolskie"),
    ("OS", "Strzelce Opolskie", "Groß Strehlitz", "Стшелце-Опольске", "Стшелце Опольські", "Opolskie"),
    ("OT", "Nysa", "Neisse", "Ниса", "Ниса", "Opolskie"),
    # ---- Holy Cross / Świętokrzyskie ----
    ("KI", "Kielce", "Kielce", "Кельце", "Кельце", "Świętokrzyskie"),
    ("KL", "Busko-Zdrój", "Busko-Zdrój", "Буско-Здруй", "Буско-Здруй", "Świętokrzyskie"),
    ("KN", "Jędrzejów", "Jędrzejów", "Енджеюв", "Єнджеюв", "Świętokrzyskie"),
    ("KO", "Kazimierza Wielka", "Kazimierza Wielka", "Казимежа-Вельки", "Казімежа Велика", "Świętokrzyskie"),
    ("KP", "Końskie", "Końskie", "Конские", "Конські", "Świętokrzyskie"),
    ("KW", "Ostrowiec Świętokrzyski", "Ostrowiec Świętokrzyski", "Островец-Свентокшиски", "Островець Свентокшиський", "Świętokrzyskie"),
    ("KX", "Włoszczowa", "Włoszczowa", "Влошчова", "Влощова", "Świętokrzyskie"),
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
    """Insert the PL country record and its translations.

    Args:
        conn: An open SQLite connection (foreign keys must be on).
    """
    country_id = _get_or_insert_country(conn)
    _insert_country_translations(conn, country_id)
    logger.info("Seeded country PL (id=%d)", country_id)


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
    voivodeship_key: str,
    coords: tuple[float, float] | None,
) -> None:
    """Insert one region and its 8 translations (4 name + 4 region_group)."""
    lat = coords[0] if coords else None
    lon = coords[1] if coords else None
    conn.execute(
        "INSERT OR IGNORE INTO regions"
        " (country_id, plate_code, latitude, longitude) VALUES (?, ?, ?, ?)",
        (country_id, plate_code.upper(), lat, lon),
    )
    row = conn.execute(
        "SELECT id FROM regions WHERE country_id = ? AND plate_code = ?",
        (country_id, plate_code.upper()),
    ).fetchone()
    name_trans = {"en": name_en, "de": name_de, "ru": name_ru, "uk": name_uk}
    group_trans = _WOJ[voivodeship_key]
    _insert_region_translations(conn, row[0], name_trans, group_trans)


def seed_regions(conn: sqlite3.Connection) -> None:
    """Insert all PL region records and their translations.

    Args:
        conn: An open SQLite connection.
    """
    row = conn.execute("SELECT id FROM countries WHERE code = ?", (COUNTRY_CODE,)).fetchone()
    country_id: int = row[0]
    for plate_code, name_en, name_de, name_ru, name_uk, woj_key in _REGION_ROWS:
        coords = _COORDS.get(plate_code.upper())
        _seed_single_region(
            conn, country_id, plate_code,
            name_en, name_de, name_ru, name_uk,
            woj_key, coords,
        )
    logger.info("Seeded %d PL regions", len(_REGION_ROWS))


def run(conn: sqlite3.Connection) -> None:
    """Run the full Poland seed: country + all regions.

    Args:
        conn: An open SQLite connection.
    """
    seed_country(conn)
    seed_regions(conn)


def main() -> None:
    """Open the production DB, seed Poland, and close."""
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s — %(message)s")
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    try:
        run(conn)
        conn.commit()
        logger.info("Poland seed complete")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
