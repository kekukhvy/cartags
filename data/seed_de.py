"""Seed Germany (DE) into the CarTags database.

Inserts the country record, its translations, and region records
with full translations in en/de/ru/uk.  All inserts are idempotent
via INSERT OR IGNORE.

Usage::

    python data/seed_de.py
"""

import logging
import sqlite3
from pathlib import Path

logger = logging.getLogger(__name__)

DB_PATH = Path(__file__).parent.parent / "db" / "cartags.db"

COUNTRY_CODE = "DE"
COUNTRY_EMOJI = "🇩🇪"
COUNTRY_SORT_ORDER = 1

_COUNTRY_TRANSLATIONS: dict[str, str] = {
    "en": "Germany",
    "de": "Deutschland",
    "ru": "Германия",
    "uk": "Німеччина",
}

# State name translations reused across many regions
_BAVARIA = {
    "en": "Bavaria",
    "de": "Bayern",
    "ru": "Бавария",
    "uk": "Баварія",
}
_BADEN_WUERTTEMBERG = {
    "en": "Baden-Württemberg",
    "de": "Baden-Württemberg",
    "ru": "Баден-Вюртемберг",
    "uk": "Баден-Вюртемберг",
}
_NRW = {
    "en": "North Rhine-Westphalia",
    "de": "Nordrhein-Westfalen",
    "ru": "Северный Рейн-Вестфалия",
    "uk": "Північний Рейн-Вестфалія",
}
_HESSE = {
    "en": "Hesse",
    "de": "Hessen",
    "ru": "Гессен",
    "uk": "Гессен",
}
_LOWER_SAXONY = {
    "en": "Lower Saxony",
    "de": "Niedersachsen",
    "ru": "Нижняя Саксония",
    "uk": "Нижня Саксонія",
}
_SAXONY = {
    "en": "Saxony",
    "de": "Sachsen",
    "ru": "Саксония",
    "uk": "Саксонія",
}
_THURINGIA = {
    "en": "Thuringia",
    "de": "Thüringen",
    "ru": "Тюрингия",
    "uk": "Тюрингія",
}
_BRANDENBURG = {
    "en": "Brandenburg",
    "de": "Brandenburg",
    "ru": "Бранденбург",
    "uk": "Бранденбург",
}
_SAXONY_ANHALT = {
    "en": "Saxony-Anhalt",
    "de": "Sachsen-Anhalt",
    "ru": "Саксония-Анхальт",
    "uk": "Саксонія-Ангальт",
}
_SCHLESWIG_HOLSTEIN = {
    "en": "Schleswig-Holstein",
    "de": "Schleswig-Holstein",
    "ru": "Шлезвиг-Гольштейн",
    "uk": "Шлезвіг-Гольштейн",
}
_MECKLENBURG = {
    "en": "Mecklenburg-Vorpommern",
    "de": "Mecklenburg-Vorpommern",
    "ru": "Мекленбург-Передняя Померания",
    "uk": "Мекленбург-Передня Померанія",
}
_RHINELAND_PALATINATE = {
    "en": "Rhineland-Palatinate",
    "de": "Rheinland-Pfalz",
    "ru": "Рейнланд-Пфальц",
    "uk": "Рейнланд-Пфальц",
}
_SAARLAND = {
    "en": "Saarland",
    "de": "Saarland",
    "ru": "Саар",
    "uk": "Саар",
}
_BERLIN = {
    "en": "Berlin",
    "de": "Berlin",
    "ru": "Берлин",
    "uk": "Берлін",
}
_HAMBURG = {
    "en": "Hamburg",
    "de": "Hamburg",
    "ru": "Гамбург",
    "uk": "Гамбург",
}
_BREMEN = {
    "en": "Bremen",
    "de": "Bremen",
    "ru": "Бремен",
    "uk": "Бремен",
}

# Map of plate_code → (latitude, longitude) for regions that have known coordinates.
# Only major/well-known cities are listed; the rest remain without map pins.
_COORDS: dict[str, tuple[float, float]] = {
    "B":   (52.5200, 13.4050),   # Berlin
    "HH":  (53.5511, 9.9937),    # Hamburg
    "HB":  (53.0793, 8.8017),    # Bremen
    "BRV": (53.5396, 8.5809),    # Bremerhaven
    "M":   (48.1351, 11.5820),   # Munich
    "N":   (49.4521, 11.0767),   # Nuremberg
    "A":   (48.3717, 10.8983),   # Augsburg
    "WÜ":  (49.7913, 9.9534),    # Würzburg
    "REG": (49.0000, 12.1000),   # Regensburg (approx)
    "PA":  (48.5667, 13.4333),   # Passau
    "IN":  (48.7665, 11.4258),   # Ingolstadt
    "RO":  (47.8561, 12.1289),   # Rosenheim
    "KE":  (47.7167, 10.3167),   # Kempten
    "S":   (48.7758, 9.1829),    # Stuttgart
    "KA":  (49.0069, 8.4037),    # Karlsruhe
    "MA":  (49.4875, 8.4660),    # Mannheim
    "F":   (50.1109, 8.6821),    # Frankfurt
    "K":   (50.9333, 6.9500),    # Cologne
    "D":   (51.2217, 6.7762),    # Düsseldorf
    "E":   (51.4556, 7.0116),    # Essen
    "DO":  (51.5136, 7.4653),    # Dortmund
    "DU":  (51.4350, 6.7627),    # Duisburg
    "BO":  (51.4818, 7.2162),    # Bochum
    "WUP": (51.2562, 7.1508),    # Wuppertal
    "BI":  (52.0302, 8.5325),    # Bielefeld
    "MS":  (51.9607, 7.6261),    # Münster
    "AC":  (50.7753, 6.0839),    # Aachen
    "KR":  (51.3388, 6.5853),    # Krefeld
    "BN":  (50.7374, 7.0982),    # Bonn
    "H":   (52.3759, 9.7320),    # Hanover
    "BS":  (52.2692, 10.5211),   # Braunschweig
    "OS":  (52.2799, 8.0472),    # Osnabrück
    "OL":  (53.1435, 8.2146),    # Oldenburg
    "GÖ":  (51.5413, 9.9158),    # Göttingen
    "SHG": (52.2667, 9.2000),    # Schaumburg
    "L":   (51.3397, 12.3731),   # Leipzig
    "DD":  (51.0504, 13.7373),   # Dresden
    "C":   (50.8278, 12.9214),   # Chemnitz
    "ERZ": (50.5381, 12.6981),   # Erzgebirge
    "GR":  (51.1500, 14.9833),   # Görlitz
    "HRO": (54.0924, 12.0991),   # Rostock
    "SN":  (53.6278, 11.4142),   # Schwerin
    "GS":  (51.9167, 10.4333),   # Goslar
    "KI":  (54.3233, 10.1394),   # Kiel
    "LU":  (53.8167, 10.6833),   # Lübeck
    "FL":  (54.7850, 9.4368),    # Flensburg
    "SI":  (50.8750, 8.0239),    # Siegen
    "MR":  (50.8045, 8.7732),    # Marburg
    "KS":  (51.3167, 9.4833),    # Kassel
    "DA":  (49.8728, 8.6512),    # Darmstadt
    "OF":  (50.1058, 8.7646),    # Offenbach
    "WI":  (50.0826, 8.2400),    # Wiesbaden
    "ER":  (49.5897, 11.0078),   # Erlangen
    "FÜ":  (49.4768, 10.9887),   # Fürth
    "MZ":  (49.9929, 8.2473),    # Mainz
    "KO":  (50.3569, 7.5890),    # Koblenz
    "TR":  (49.7556, 6.6389),    # Trier
    "KL":  (49.4439, 7.7689),    # Kaiserslautern
    "LDS": (51.8000, 14.1500),   # Dahme-Spreewald (approx Lübben)
    "P":   (52.3906, 13.0645),   # Potsdam
    "HNO": (52.5200, 12.1167),   # Havelland (approx)
    "MYK": (50.2667, 7.5000),    # Mayen-Koblenz (approx)
    "TBB": (49.4789, 9.7833),    # Tauberbischofsheim
    "SW":  (50.0597, 10.2347),   # Schweinfurt
    "KEH": (48.9167, 11.7833),   # Kelheim
    "ND":  (48.7167, 10.4833),   # Neuburg-Schrobenhausen (approx)
    "GZ":  (48.4556, 10.2681),   # Günzburg
    "MN":  (47.9840, 10.1812),   # Memmingen
    "OA":  (47.7167, 10.3167),   # Oberallgäu (Sonthofen approx)
    "WM":  (47.8826, 11.1194),   # Weilheim-Schongau
    "FFB": (48.1803, 11.2950),   # Fürstenfeldbruck
    "LL":  (48.1997, 11.0417),   # Landsberg am Lech
    "AIC": (48.4581, 11.1408),   # Aichach
    "EI":  (48.8928, 11.1889),   # Eichstätt
    "AN":  (49.3014, 10.5712),   # Ansbach
    "AB":  (49.9771, 9.1500),    # Aschaffenburg
    "AA":  (48.8367, 10.0933),   # Aalen
    "ABG": (51.2938, 12.9356),   # Altenburg
    "ABI": (51.8142, 12.1234),   # Köthen
    "AK":  (50.6842, 7.7108),    # Altenkirchen
    "AM":  (49.6156, 11.8622),   # Amberg
    "AW":  (50.5425, 7.1206),    # Bad Neuenahr-Ahrweiler
    "AZ":  (49.7319, 8.6456),    # Alzey
    "AÖ":  (48.6344, 12.3706),   # Altötting
    "BA":  (49.8912, 10.8767),   # Bamberg
    "BAR": (52.7614, 13.8008),   # Eberswalde
    "BB":  (48.7061, 8.9561),    # Böblingen
    "BC":  (48.0901, 9.7854),    # Biberach an der Riß
    "BGL": (47.6719, 12.9381),   # Bad Reichenhall
    "BIR": (49.6619, 7.2114),    # Birkenfeld
    "BIT": (49.9544, 6.5306),    # Bitburg
    "BL":  (48.4875, 8.5814),    # Balingen
    "BLK": (51.1889, 12.3667),   # Naumburg (Saale)
    "BM":  (51.0844, 6.9933),    # Bergheim
    "BOR": (51.8445, 6.8906),    # Borken (Westfalen)
    "BOT": (51.4333, 6.4500),    # Bottrop
    "BR":  (47.9089, 7.7236),    # Staufen
    "BT":  (49.9441, 11.5754),   # Bayreuth
    "BZ":  (51.1833, 14.4167),   # Bautzen
    "CE":  (52.6456, 10.0831),   # Celle
    "CHA": (49.2136, 12.6783),   # Cham
    "CLP": (53.0500, 8.0500),    # Cloppenburg
    "CO":  (50.2647, 10.9631),   # Coburg
    "COC": (50.1486, 7.1525),    # Cochem
    "CUX": (53.8797, 8.7300),    # Cuxhaven
    "CW":  (48.5764, 8.7719),    # Calw
    "DAH": (48.2522, 11.4689),   # Dachau
    "DAN": (53.1547, 11.5258),   # Lüchow
    "DAU": (50.1531, 6.8094),    # Daun
    "DE":  (51.8200, 12.6300),   # Dessau-Roßlau
    "DEG": (48.7289, 12.9522),   # Deggendorf
    "DEL": (53.2581, 8.6294),    # Delmenhorst
    "DGF": (48.6544, 12.5114),   # Dingolfing
    "DH":  (52.6167, 8.6333),    # Diepholz
    "DLG": (48.6256, 10.4947),   # Dillingen an der Donau
    "DN":  (50.8111, 6.2986),    # Düren
    "DON": (48.7406, 10.7636),   # Donauwörth
    "EBE": (48.0953, 11.9331),   # Ebersberg
    "EE":  (51.5567, 13.4889),   # Herzberg (Elster)
    "EF":  (50.9856, 11.0281),   # Erfurt
    "EIC": (51.3286, 10.2831),   # Heiligenstadt
    "EL":  (52.6867, 7.6200),    # Meppen
    "EM":  (48.1169, 7.8447),    # Emmendingen
    "EMD": (53.3646, 7.2071),    # Emden
    "EN":  (51.4522, 7.2042),    # Schwelm
    "ERH": (49.7094, 10.9833),   # Höchstadt an der Aisch
    "ES":  (48.7392, 9.3083),    # Esslingen am Neckar
    "EU":  (50.6622, 7.4500),    # Euskirchen
    "FB":  (50.3203, 8.7297),    # Friedberg (Hessen)
    "FD":  (50.5167, 9.6833),    # Fulda
    "FDS": (48.5903, 8.4089),    # Freudenstadt
    "FR":  (47.9990, 7.8507),    # Freiburg im Breisgau
    "FRG": (49.1264, 13.6092),   # Freyung
    "FS":  (48.4011, 11.7436),   # Freising
    "G":   (50.3597, 12.0833),   # Gera
    "GAP": (47.4922, 11.0967),   # Garmisch-Partenkirchen
    "GE":  (51.4333, 7.0667),    # Gelsenkirchen
    "GF":  (52.4833, 9.5333),    # Gifhorn
    "GI":  (50.5836, 8.6736),    # Gießen
    "GP":  (48.7022, 9.6522),    # Göppingen
    "GT":  (51.9064, 8.3819),    # Gütersloh
    "GTH": (50.9511, 10.7278),   # Gotha
    "HA":  (51.3633, 7.4564),    # Hagen
    "HAL": (51.4819, 12.0000),   # Halle (Saale)
    "HD":  (49.1428, 8.6753),    # Heidelberg
    "HEF": (50.8619, 9.5119),    # Bad Hersfeld
    "HEI": (54.3083, 9.0825),    # Heide (Holstein)
    "HER": (51.5364, 7.2225),    # Herne
    "HF":  (52.0500, 8.6667),    # Herford
    "HGW": (54.0836, 13.3833),   # Greifswald
    "HI":  (52.1500, 10.1333),   # Hildesheim
    "HK":  (52.8167, 9.5500),    # Soltau
    "HL":  (53.8667, 10.6833),   # Lübeck
    "HN":  (49.1408, 9.2225),    # Heilbronn
    "HO":  (50.3167, 11.9167),   # Hof (Saale)
    "HOL": (51.8242, 9.3778),    # Holzminden
    "HOM": (49.3186, 7.3297),    # Homburg (Saar)
    "HR":  (50.9953, 9.1111),    # Homberg (Efze)
    "HSK": (51.3689, 8.2911),    # Meschede
    "HST": (54.3092, 13.3033),   # Stralsund
    "HVL": (52.6167, 12.0667),   # Rathenow
    "HX":  (51.7833, 9.3667),    # Höxter
    "I":   (48.7642, 10.5755),   # Ingolstadt (district)
    "IK":  (50.8203, 10.9497),   # Arnstadt
    "IZ":  (54.1667, 9.3167),    # Itzehoe
    "J":   (50.9281, 11.5869),   # Jena
    "JL":  (52.2667, 11.8333),   # Burg (bei Magdeburg)
    "KF":  (47.7228, 10.6256),   # Kaufbeuren
    "KG":  (50.2000, 10.0333),   # Bad Kissingen
    "KH":  (49.8483, 7.8644),    # Bad Kreuznach
    "KLE": (51.7833, 6.1167),    # Kleve
    "KN":  (47.6667, 8.9167),    # Konstanz
    "KU":  (50.1036, 11.4689),   # Kulmbach
    "KYF": (51.3667, 10.9667),   # Sondershausen
    "KÜN": (49.2583, 9.6583),    # Künzelsau
    "LA":  (48.6314, 12.1592),   # Landshut
    "LB":  (49.0108, 8.9078),    # Ludwigsburg
    "LDK": (50.5717, 8.5033),    # Wetzlar
    "LE":  (48.7392, 9.3083),    # Esslingen am Neckar
    "LER": (53.2333, 7.4667),    # Leer (Ostfriesland)
    "LG":  (53.2500, 10.3833),   # Lüneburg
    "LIF": (50.1167, 11.2500),   # Lichtenfels
    "LIP": (51.9381, 8.8797),    # Detmold
    "LOS": (52.1403, 13.5711),   # Beeskow
    "LRO": (54.1183, 12.2000),   # Güstrow
    "LUP": (53.3000, 11.5000),   # Ludwigslust
    "MB":  (47.7894, 11.8406),   # Miesbach
    "MD":  (52.1167, 11.6500),   # Magdeburg
    "ME":  (51.2167, 7.1333),    # Mettmann
    "MEI": (51.1642, 13.4606),   # Meißen
    "MG":  (51.1614, 6.3667),    # Mönchengladbach
    "MI":  (52.2833, 8.8667),    # Minden
    "MIL": (49.7206, 9.2753),    # Miltenberg
    "MK":  (51.2583, 7.4417),    # Lüdenscheid
    "MKK": (50.1833, 9.2333),    # Gelnhausen
    "MOL": (52.4339, 13.5964),   # Strausberg
    "MOS": (47.7522, 9.1406),    # Friedrichshafen
    "MSE": (53.5719, 12.8022),   # Neubrandenburg
    "MSH": (51.6089, 11.4267),   # Sangerhausen
    "MSP": (50.0056, 9.7533),    # Karlstadt am Main
    "MTK": (50.1833, 8.4667),    # Hofheim am Taunus
    "MZG": (49.6256, 6.6031),    # Merzig
    "MÜ":  (48.2436, 12.5756),   # Mühldorf am Inn
    "NB":  (53.5719, 12.8022),   # Neubrandenburg
    "NDH": (51.5033, 10.7769),   # Nordhausen
    "NE":  (51.2281, 6.8844),    # Grevenbroich
    "NEA": (49.4128, 10.3844),   # Neustadt an der Aisch
    "NES": (50.3167, 9.9333),    # Bad Neustadt an der Saale
    "NEW": (49.6828, 12.1342),   # Neustadt an der Waldnaab
    "NF":  (54.4733, 8.8667),    # Husum
    "NK":  (49.3539, 7.2061),    # Neunkirchen (Saar)
    "NM":  (49.2956, 11.4433),   # Neumarkt in der Oberpfalz
    "NOH": (52.4381, 7.0217),    # Nordhorn
    "NOM": (51.8333, 10.2333),   # Northeim
    "NW":  (49.2297, 8.1433),    # Neustadt an der Weinstraße
    "OAL": (47.7981, 10.6236),   # Marktoberdorf
    "OB":  (51.4558, 6.8644),    # Oberhausen
    "OD":  (53.8158, 10.4522),   # Bad Oldesloe
    "OE":  (51.0244, 7.8778),    # Olpe
    "OG":  (48.4731, 7.9219),    # Offenburg
    "OH":  (54.3361, 10.6142),   # Eutin
    "OHV": (52.7533, 13.1256),   # Oranienburg
    "OPR": (52.9333, 12.4833),   # Neuruppin
    "OSL": (51.4947, 13.7306),   # Senftenberg
    "OVP": (54.0836, 13.3833),   # Greifswald
    "PAN": (48.5122, 12.3922),   # Pfarrkirchen
    "PB":  (51.7194, 8.7536),    # Paderborn
    "PE":  (52.3244, 10.2508),   # Peine
    "PF":  (48.8856, 8.6944),    # Pforzheim
    "PIN": (53.6539, 9.7956),    # Pinneberg
    "PIR": (50.9583, 14.0053),   # Pirna
    "PLÖ": (54.1833, 10.5667),   # Plön
    "PM":  (52.1278, 12.3044),   # Bad Belzig
    "PR":  (52.9833, 11.4833),   # Perleberg
    "PS":  (49.2181, 7.6117),    # Pirmasens
    "R":   (48.9708, 12.1044),   # Regensburg
    "RA":  (48.7564, 8.2014),    # Rastatt
    "RD":  (54.1944, 9.6667),    # Rendsburg
    "RE":  (51.4333, 7.2000),    # Recklinghausen
    "ROT": (49.2186, 11.0978),   # Roth (Mittelfranken)
    "ROW": (53.1167, 9.4833),    # Rotenburg (Wümme)
    "RV":  (47.7789, 9.6089),    # Ravensburg
    "RW":  (48.1472, 8.6300),    # Rottweil
    "SAD": (49.1947, 12.5517),   # Schwandorf
    "SAW": (52.6667, 11.5333),   # Salzwedel
    "SB":  (49.2414, 7.0017),    # Saarbrücken
    "SDL": (52.3667, 11.8333),   # Stendal
    "SE":  (53.9667, 10.2833),   # Bad Segeberg
    "SHA": (49.1122, 9.7536),    # Schwäbisch Hall
    "SHK": (50.7667, 11.8833),   # Eisenberg (Thüringen)
    "SIG": (48.0783, 9.2142),    # Sigmaringen
    "SIM": (50.1131, 7.6008),    # Simmern (Hunsrück)
    "SK":  (50.7728, 7.4069),    # Siegburg
    "SL":  (54.5167, 9.5667),    # Schleswig
    "SLF": (50.7167, 11.3000),   # Saalfeld
    "SLK": (51.7972, 11.9319),   # Bernburg (Saale)
    "SLS": (49.3667, 6.7833),    # Saarlouis
    "SM":  (50.5333, 10.4167),   # Meiningen
    "SO":  (51.5833, 8.1167),    # Soest
    "SOK": (50.3667, 11.5333),   # Schleiz
    "SON": (50.3500, 11.2000),   # Sonneberg
    "SPN": (51.7489, 14.2458),   # Forst (Lausitz)
    "SR":  (48.6419, 12.6178),   # Straubing
    "ST":  (52.2667, 7.8833),    # Steinfurt
    "STA": (48.0169, 11.3361),   # Starnberg
    "STD": (53.5889, 9.4833),    # Stade
    "TF":  (52.2661, 13.1919),   # Luckenwalde
    "TS":  (47.8628, 12.6539),   # Traunstein
    "TUT": (48.0367, 8.7844),    # Tuttlingen
    "TÖL": (47.7606, 11.4606),   # Bad Tölz
    "UEL": (52.9833, 10.5667),   # Uelzen
    "UH":  (51.2067, 10.4392),   # Mühlhausen (Thüringen)
    "UL":  (48.3981, 9.9875),    # Ulm
    "UM":  (53.5622, 12.7319),   # Prenzlau
    "UN":  (51.6750, 7.6750),    # Unna
    "V":   (50.7167, 12.0667),   # Plauen
    "VB":  (50.5319, 9.2500),    # Lauterbach (Hessen)
    "VER": (52.7997, 9.2394),    # Verden (Aller)
    "VIE": (51.2667, 6.3667),    # Viersen
    "VK":  (49.4294, 6.9506),    # Völklingen
    "VR":  (54.3833, 13.6667),   # Bergen auf Rügen
    "VS":  (48.0756, 8.4567),    # Villingen-Schwenningen
    "W":   (51.2557, 7.1901),    # Wuppertal
    "WAF": (51.9369, 8.0300),    # Warendorf
    "WAK": (50.5500, 10.2333),   # Bad Salzungen
    "WB":  (51.8639, 12.6300),   # Lutherstadt Wittenberg
    "WE":  (50.9856, 11.0281),   # Weimar
    "WEN": (49.0103, 12.1847),   # Weiden in der Oberpfalz
    "WES": (51.6489, 6.6089),    # Wesel
    "WHV": (53.5442, 8.1486),    # Wilhelmshaven
    "WIL": (50.0167, 7.0667),    # Wittlich
    "WL":  (53.3333, 9.8833),    # Winsen (Luhe)
    "WN":  (48.8264, 9.4500),    # Waiblingen
    "WND": (49.4667, 7.1667),    # Sankt Wendel
    "WOB": (52.4219, 10.7879),   # Wolfsburg
    "WOR": (49.6328, 8.3556),    # Worms
    "WST": (53.1833, 8.3667),    # Westerstede
    "WT":  (47.6408, 8.4431),    # Waldshut-Tiengen
    "WU":  (49.7928, 9.9328),    # Würzburg (Landkreis)
    "WUG": (48.9758, 10.7500),   # Weißenburg in Bayern
    "WUN": (50.0119, 11.9519),   # Wunsiedel im Fichtelgebirge
    "Z":   (50.7236, 12.4553),   # Zwickau
    "ZW":  (49.2633, 7.3656),    # Zweibrücken
}

# (plate_code, wikipedia_url | None, name_translations, region_group_translations)
_REGIONS: list[tuple[str, str | None, dict[str, str], dict[str, str]]] = [
    # ── Berlin ────────────────────────────────────────────────────────────────
    (
        "B",
        None,
        {"en": "Berlin", "de": "Berlin", "ru": "Берлин", "uk": "Берлін"},
        _BERLIN,
    ),
    # ── Hamburg ───────────────────────────────────────────────────────────────
    (
        "HH",
        None,
        {"en": "Hamburg", "de": "Hamburg", "ru": "Гамбург", "uk": "Гамбург"},
        _HAMBURG,
    ),
    # ── Bremen ────────────────────────────────────────────────────────────────
    (
        "HB",
        None,
        {"en": "Bremen", "de": "Bremen", "ru": "Бремен", "uk": "Бремен"},
        _BREMEN,
    ),
    (
        "BRV",
        None,
        {
            "en": "Bremerhaven",
            "de": "Bremerhaven",
            "ru": "Бремерхафен",
            "uk": "Бремерхафен",
        },
        _BREMEN,
    ),
    # ── Bavaria ───────────────────────────────────────────────────────────────
    (
        "A",
        None,
        {"en": "Augsburg", "de": "Augsburg", "ru": "Аугсбург", "uk": "Аугсбург"},
        _BAVARIA,
    ),
    (
        "AB",
        None,
        {
            "en": "Aschaffenburg",
            "de": "Aschaffenburg",
            "ru": "Ашаффенбург",
            "uk": "Ашаффенбург",
        },
        _BAVARIA,
    ),
    (
        "AIC",
        None,
        {
            "en": "Aichach-Friedberg",
            "de": "Aichach-Friedberg",
            "ru": "Айхах-Фридберг",
            "uk": "Айхах-Фрідберг",
        },
        _BAVARIA,
    ),
    (
        "AM",
        None,
        {"en": "Amberg", "de": "Amberg", "ru": "Амберг", "uk": "Амберг"},
        _BAVARIA,
    ),
    (
        "AN",
        None,
        {"en": "Ansbach", "de": "Ansbach", "ru": "Ансбах", "uk": "Ансбах"},
        _BAVARIA,
    ),
    (
        "AÖ",
        None,
        {"en": "Altötting", "de": "Altötting", "ru": "Альтёттинг", "uk": "Альтьоттінг"},
        _BAVARIA,
    ),
    (
        "BA",
        None,
        {"en": "Bamberg", "de": "Bamberg", "ru": "Бамберг", "uk": "Бамберг"},
        _BAVARIA,
    ),
    (
        "BGL",
        None,
        {
            "en": "Berchtesgadener Land",
            "de": "Berchtesgadener Land",
            "ru": "Берхтесгаден",
            "uk": "Берхтесґаден",
        },
        _BAVARIA,
    ),
    (
        "BT",
        None,
        {"en": "Bayreuth", "de": "Bayreuth", "ru": "Байройт", "uk": "Байройт"},
        _BAVARIA,
    ),
    ("CHA", None, {"en": "Cham", "de": "Cham", "ru": "Кам", "uk": "Кам"}, _BAVARIA),
    (
        "CO",
        None,
        {"en": "Coburg", "de": "Coburg", "ru": "Кобург", "uk": "Кобург"},
        _BAVARIA,
    ),
    (
        "DAH",
        None,
        {"en": "Dachau", "de": "Dachau", "ru": "Дахау", "uk": "Дахау"},
        _BAVARIA,
    ),
    (
        "DEG",
        None,
        {
            "en": "Deggendorf",
            "de": "Deggendorf",
            "ru": "Деггендорф",
            "uk": "Деггендорф",
        },
        _BAVARIA,
    ),
    (
        "DGF",
        None,
        {
            "en": "Dingolfing-Landau",
            "de": "Dingolfing-Landau",
            "ru": "Дингольфинг-Ландау",
            "uk": "Дінгольфінг-Ландау",
        },
        _BAVARIA,
    ),
    (
        "DLG",
        None,
        {
            "en": "Dillingen a.d. Donau",
            "de": "Dillingen a.d. Donau",
            "ru": "Диллинген-на-Дунае",
            "uk": "Ділінген-на-Дунаї",
        },
        _BAVARIA,
    ),
    (
        "DON",
        None,
        {"en": "Donau-Ries", "de": "Donau-Ries", "ru": "Донау-Рис", "uk": "Донау-Ріс"},
        _BAVARIA,
    ),
    (
        "EBE",
        None,
        {"en": "Ebersberg", "de": "Ebersberg", "ru": "Эберсберг", "uk": "Еберсберг"},
        _BAVARIA,
    ),
    (
        "EI",
        None,
        {"en": "Eichstätt", "de": "Eichstätt", "ru": "Айхштетт", "uk": "Айхштетт"},
        _BAVARIA,
    ),
    (
        "ER",
        None,
        {"en": "Erlangen", "de": "Erlangen", "ru": "Эрланген", "uk": "Ерланген"},
        _BAVARIA,
    ),
    (
        "ERH",
        None,
        {
            "en": "Erlangen-Höchstadt",
            "de": "Erlangen-Höchstadt",
            "ru": "Эрланген-Хёхштадт",
            "uk": "Ерланген-Гьохштадт",
        },
        _BAVARIA,
    ),
    (
        "FFB",
        None,
        {
            "en": "Fürstenfeldbruck",
            "de": "Fürstenfeldbruck",
            "ru": "Фюрстенфельдбрук",
            "uk": "Фюрстенфельдбрук",
        },
        _BAVARIA,
    ),
    (
        "FRG",
        None,
        {
            "en": "Freyung-Grafenau",
            "de": "Freyung-Grafenau",
            "ru": "Фрайунг-Графенау",
            "uk": "Фрайунг-Графенау",
        },
        _BAVARIA,
    ),
    (
        "FS",
        None,
        {"en": "Freising", "de": "Freising", "ru": "Фрайзинг", "uk": "Фрайзінг"},
        _BAVARIA,
    ),
    ("FÜ", None, {"en": "Fürth", "de": "Fürth", "ru": "Фюрт", "uk": "Фюрт"}, _BAVARIA),
    (
        "GAP",
        None,
        {
            "en": "Garmisch-Partenkirchen",
            "de": "Garmisch-Partenkirchen",
            "ru": "Гармиш-Партенкирхен",
            "uk": "Гарміш-Партенкірхен",
        },
        _BAVARIA,
    ),
    ("HO", None, {"en": "Hof", "de": "Hof", "ru": "Хоф", "uk": "Хоф"}, _BAVARIA),
    (
        "I",
        None,
        {
            "en": "Ingolstadt",
            "de": "Ingolstadt",
            "ru": "Ингольштадт",
            "uk": "Інгольштадт",
        },
        _BAVARIA,
    ),
    (
        "KEH",
        None,
        {"en": "Kelheim", "de": "Kelheim", "ru": "Кельхайм", "uk": "Кельгайм"},
        _BAVARIA,
    ),
    (
        "KF",
        None,
        {
            "en": "Kaufbeuren",
            "de": "Kaufbeuren",
            "ru": "Кауфбойрен",
            "uk": "Кауфбойрен",
        },
        _BAVARIA,
    ),
    (
        "KG",
        None,
        {
            "en": "Bad Kissingen",
            "de": "Bad Kissingen",
            "ru": "Бад-Киссинген",
            "uk": "Бад-Кіссінген",
        },
        _BAVARIA,
    ),
    (
        "KU",
        None,
        {"en": "Kulmbach", "de": "Kulmbach", "ru": "Кульмбах", "uk": "Кульмбах"},
        _BAVARIA,
    ),
    (
        "LA",
        None,
        {"en": "Landshut", "de": "Landshut", "ru": "Ландсхут", "uk": "Ландсгут"},
        _BAVARIA,
    ),
    (
        "LIF",
        None,
        {
            "en": "Lichtenfels",
            "de": "Lichtenfels",
            "ru": "Лихтенфельс",
            "uk": "Ліхтенфельс",
        },
        _BAVARIA,
    ),
    (
        "LL",
        None,
        {
            "en": "Landsberg am Lech",
            "de": "Landsberg am Lech",
            "ru": "Ландсберг-на-Лехе",
            "uk": "Ландсберг-на-Лехе",
        },
        _BAVARIA,
    ),
    (
        "M",
        None,
        {"en": "Munich", "de": "München", "ru": "Мюнхен", "uk": "Мюнхен"},
        _BAVARIA,
    ),
    (
        "MB",
        None,
        {"en": "Miesbach", "de": "Miesbach", "ru": "Мисбах", "uk": "Місбах"},
        _BAVARIA,
    ),
    (
        "MIL",
        None,
        {
            "en": "Miltenberg",
            "de": "Miltenberg",
            "ru": "Мильтенберг",
            "uk": "Мільтенберг",
        },
        _BAVARIA,
    ),
    (
        "MM",
        None,
        {"en": "Memmingen", "de": "Memmingen", "ru": "Меммингeн", "uk": "Меммінген"},
        _BAVARIA,
    ),
    (
        "MN",
        None,
        {
            "en": "Unterallgäu",
            "de": "Unterallgäu",
            "ru": "Унтерэллгой",
            "uk": "Унтерелльгой",
        },
        _BAVARIA,
    ),
    (
        "MSP",
        None,
        {
            "en": "Main-Spessart",
            "de": "Main-Spessart",
            "ru": "Майн-Шпессарт",
            "uk": "Майн-Шпессарт",
        },
        _BAVARIA,
    ),
    (
        "MÜ",
        None,
        {
            "en": "Mühldorf am Inn",
            "de": "Mühldorf am Inn",
            "ru": "Мюльдорф-на-Инне",
            "uk": "Мюльдорф-на-Інні",
        },
        _BAVARIA,
    ),
    (
        "N",
        None,
        {"en": "Nuremberg", "de": "Nürnberg", "ru": "Нюрнберг", "uk": "Нюрнберг"},
        _BAVARIA,
    ),
    (
        "ND",
        None,
        {
            "en": "Neuburg-Schrobenhausen",
            "de": "Neuburg-Schrobenhausen",
            "ru": "Нойбург-Шробенхаузен",
            "uk": "Нойбург-Шробенгаузен",
        },
        _BAVARIA,
    ),
    (
        "NEA",
        None,
        {
            "en": "Neustadt a.d. Aisch-Bad Windsheim",
            "de": "Neustadt a.d. Aisch-Bad Windsheim",
            "ru": "Нойштадт-на-Айше",
            "uk": "Нойштадт-на-Айші",
        },
        _BAVARIA,
    ),
    (
        "NES",
        None,
        {
            "en": "Rhön-Grabfeld",
            "de": "Rhön-Grabfeld",
            "ru": "Рён-Грабфельд",
            "uk": "Рен-Грабфельд",
        },
        _BAVARIA,
    ),
    (
        "NEW",
        None,
        {
            "en": "Neustadt a.d. Waldnaab",
            "de": "Neustadt a.d. Waldnaab",
            "ru": "Нойштадт-на-Вальднаабе",
            "uk": "Нойштадт-на-Вальднаабі",
        },
        _BAVARIA,
    ),
    (
        "NM",
        None,
        {
            "en": "Neumarkt i.d.OPf.",
            "de": "Neumarkt i.d.OPf.",
            "ru": "Нойнаркт-в-Верхнем-Пфальце",
            "uk": "Нойнаркт-у-Верхньому-Пфальці",
        },
        _BAVARIA,
    ),
    (
        "OA",
        None,
        {
            "en": "Oberallgäu",
            "de": "Oberallgäu",
            "ru": "Обераллгой",
            "uk": "Обераллгой",
        },
        _BAVARIA,
    ),
    (
        "OAL",
        None,
        {"en": "Ostallgäu", "de": "Ostallgäu", "ru": "Осталлгой", "uk": "Осталлгой"},
        _BAVARIA,
    ),
    (
        "PA",
        None,
        {"en": "Passau", "de": "Passau", "ru": "Пассау", "uk": "Пассау"},
        _BAVARIA,
    ),
    (
        "PAN",
        None,
        {
            "en": "Rottal-Inn",
            "de": "Rottal-Inn",
            "ru": "Ротталь-Инн",
            "uk": "Ротталь-Інн",
        },
        _BAVARIA,
    ),
    (
        "R",
        None,
        {
            "en": "Regensburg",
            "de": "Regensburg",
            "ru": "Регенсбург",
            "uk": "Регенсбург",
        },
        _BAVARIA,
    ),
    (
        "REG",
        None,
        {"en": "Regen", "de": "Regen", "ru": "Реген", "uk": "Реген"},
        _BAVARIA,
    ),
    (
        "RO",
        None,
        {"en": "Rosenheim", "de": "Rosenheim", "ru": "Розенхайм", "uk": "Розенгайм"},
        _BAVARIA,
    ),
    ("ROT", None, {"en": "Roth", "de": "Roth", "ru": "Рот", "uk": "Рот"}, _BAVARIA),
    (
        "SAD",
        None,
        {"en": "Schwandorf", "de": "Schwandorf", "ru": "Швандорф", "uk": "Швандорф"},
        _BAVARIA,
    ),
    (
        "SR",
        None,
        {"en": "Straubing", "de": "Straubing", "ru": "Штраубинг", "uk": "Штраубінг"},
        _BAVARIA,
    ),
    (
        "STA",
        None,
        {"en": "Starnberg", "de": "Starnberg", "ru": "Штарнберг", "uk": "Штарнберг"},
        _BAVARIA,
    ),
    (
        "TÖL",
        None,
        {
            "en": "Bad Tölz-Wolfratshausen",
            "de": "Bad Tölz-Wolfratshausen",
            "ru": "Бад-Тёльц-Вольфратсхаузен",
            "uk": "Бад-Тьольц-Вольфратсгаузен",
        },
        _BAVARIA,
    ),
    (
        "TS",
        None,
        {
            "en": "Traunstein",
            "de": "Traunstein",
            "ru": "Траунштайн",
            "uk": "Траунштайн",
        },
        _BAVARIA,
    ),
    (
        "WEN",
        None,
        {
            "en": "Weiden i.d.OPf.",
            "de": "Weiden i.d.OPf.",
            "ru": "Вайден-в-Верхнем-Пфальце",
            "uk": "Вайден-у-Верхньому-Пфальці",
        },
        _BAVARIA,
    ),
    (
        "WM",
        None,
        {
            "en": "Weilheim-Schongau",
            "de": "Weilheim-Schongau",
            "ru": "Вайльхайм-Шонгау",
            "uk": "Вайльгайм-Шонгау",
        },
        _BAVARIA,
    ),
    (
        "WUG",
        None,
        {
            "en": "Weißenburg-Gunzenhausen",
            "de": "Weißenburg-Gunzenhausen",
            "ru": "Вайссенбург-Гунценхаузен",
            "uk": "Вайссенбург-Гунценгаузен",
        },
        _BAVARIA,
    ),
    (
        "WUN",
        None,
        {
            "en": "Wunsiedel i.Fichtelgebirge",
            "de": "Wunsiedel i.Fichtelgebirge",
            "ru": "Вунзидель-в-Фихтельгебирге",
            "uk": "Вунзідель-у-Фіхтельгебірге",
        },
        _BAVARIA,
    ),
    (
        "WU",
        None,
        {"en": "Würzburg", "de": "Würzburg", "ru": "Вюрцбург", "uk": "Вюрцбург"},
        _BAVARIA,
    ),
    # ── Baden-Württemberg ─────────────────────────────────────────────────────
    (
        "AA",
        None,
        {
            "en": "Aalen (Ostalbkreis)",
            "de": "Aalen (Ostalbkreis)",
            "ru": "Аален",
            "uk": "Аален",
        },
        _BADEN_WUERTTEMBERG,
    ),
    (
        "BB",
        None,
        {"en": "Böblingen", "de": "Böblingen", "ru": "Бёблинген", "uk": "Бьоблінген"},
        _BADEN_WUERTTEMBERG,
    ),
    (
        "BC",
        None,
        {
            "en": "Biberach",
            "de": "Biberach an der Riß",
            "ru": "Биберах-на-Риссе",
            "uk": "Біберах-на-Ріссі",
        },
        _BADEN_WUERTTEMBERG,
    ),
    (
        "BL",
        None,
        {
            "en": "Zollernalbkreis",
            "de": "Zollernalbkreis",
            "ru": "Цоллернальбкрайс",
            "uk": "Цолерналькрайс",
        },
        _BADEN_WUERTTEMBERG,
    ),
    (
        "BR",
        None,
        {
            "en": "Breisgau-Hochschwarzwald",
            "de": "Breisgau-Hochschwarzwald",
            "ru": "Брайсгау-Высокий Шварцвальд",
            "uk": "Брайсгау-Високий Шварцвальд",
        },
        _BADEN_WUERTTEMBERG,
    ),
    (
        "CW",
        None,
        {"en": "Calw", "de": "Calw", "ru": "Кальв", "uk": "Кальв"},
        _BADEN_WUERTTEMBERG,
    ),
    (
        "EM",
        None,
        {
            "en": "Emmendingen",
            "de": "Emmendingen",
            "ru": "Эммендинген",
            "uk": "Еммендінген",
        },
        _BADEN_WUERTTEMBERG,
    ),
    (
        "ES",
        None,
        {
            "en": "Esslingen am Neckar",
            "de": "Esslingen am Neckar",
            "ru": "Эсслинген-на-Неккаре",
            "uk": "Есслінген-на-Неккарі",
        },
        _BADEN_WUERTTEMBERG,
    ),
    (
        "FDS",
        None,
        {
            "en": "Freudenstadt",
            "de": "Freudenstadt",
            "ru": "Фройденштадт",
            "uk": "Фройденштадт",
        },
        _BADEN_WUERTTEMBERG,
    ),
    (
        "FR",
        None,
        {
            "en": "Freiburg im Breisgau",
            "de": "Freiburg im Breisgau",
            "ru": "Фрайбург-им-Брайсгау",
            "uk": "Фрайбург-ім-Брайсґау",
        },
        _BADEN_WUERTTEMBERG,
    ),
    (
        "GP",
        None,
        {"en": "Göppingen", "de": "Göppingen", "ru": "Гёппинген", "uk": "Гьоппінген"},
        _BADEN_WUERTTEMBERG,
    ),
    (
        "HD",
        None,
        {
            "en": "Heidelberg",
            "de": "Heidelberg",
            "ru": "Гейдельберг",
            "uk": "Гейдельберг",
        },
        _BADEN_WUERTTEMBERG,
    ),
    (
        "HN",
        None,
        {"en": "Heilbronn", "de": "Heilbronn", "ru": "Хайльбронн", "uk": "Гайльбронн"},
        _BADEN_WUERTTEMBERG,
    ),
    (
        "KA",
        None,
        {"en": "Karlsruhe", "de": "Karlsruhe", "ru": "Карлсруэ", "uk": "Карлсруе"},
        _BADEN_WUERTTEMBERG,
    ),
    (
        "KN",
        None,
        {"en": "Konstanz", "de": "Konstanz", "ru": "Констанц", "uk": "Констанц"},
        _BADEN_WUERTTEMBERG,
    ),
    (
        "KÜN",
        None,
        {
            "en": "Hohenlohekreis",
            "de": "Hohenlohekreis",
            "ru": "Хоэнлоэкрайс",
            "uk": "Гоенлоекрайс",
        },
        _BADEN_WUERTTEMBERG,
    ),
    (
        "LB",
        None,
        {
            "en": "Ludwigsburg",
            "de": "Ludwigsburg",
            "ru": "Людвигсбург",
            "uk": "Людвігсбург",
        },
        _BADEN_WUERTTEMBERG,
    ),
    (
        "MA",
        None,
        {"en": "Mannheim", "de": "Mannheim", "ru": "Мангейм", "uk": "Мангейм"},
        _BADEN_WUERTTEMBERG,
    ),
    (
        "MOS",
        None,
        {
            "en": "Konstanz (Bodenseekreis)",
            "de": "Bodenseekreis",
            "ru": "Боденский регион",
            "uk": "Боденський регіон",
        },
        _BADEN_WUERTTEMBERG,
    ),
    (
        "OG",
        None,
        {
            "en": "Ortenaukreis",
            "de": "Ortenaukreis",
            "ru": "Ортенаукрайс",
            "uk": "Ортенаукрайс",
        },
        _BADEN_WUERTTEMBERG,
    ),
    (
        "PF",
        None,
        {"en": "Pforzheim", "de": "Pforzheim", "ru": "Пфорцхайм", "uk": "Пфорцгайм"},
        _BADEN_WUERTTEMBERG,
    ),
    (
        "RA",
        None,
        {"en": "Rastatt", "de": "Rastatt", "ru": "Раштатт", "uk": "Раштатт"},
        _BADEN_WUERTTEMBERG,
    ),
    (
        "RV",
        None,
        {
            "en": "Ravensburg",
            "de": "Ravensburg",
            "ru": "Равенсбург",
            "uk": "Равенсбург",
        },
        _BADEN_WUERTTEMBERG,
    ),
    (
        "RW",
        None,
        {"en": "Rottweil", "de": "Rottweil", "ru": "Роттвайль", "uk": "Роттвайль"},
        _BADEN_WUERTTEMBERG,
    ),
    (
        "S",
        None,
        {"en": "Stuttgart", "de": "Stuttgart", "ru": "Штутгарт", "uk": "Штутгарт"},
        _BADEN_WUERTTEMBERG,
    ),
    (
        "SHA",
        None,
        {
            "en": "Schwäbisch Hall",
            "de": "Schwäbisch Hall",
            "ru": "Швебиш-Халль",
            "uk": "Швебіш-Галль",
        },
        _BADEN_WUERTTEMBERG,
    ),
    (
        "SIG",
        None,
        {
            "en": "Sigmaringen",
            "de": "Sigmaringen",
            "ru": "Зигмаринген",
            "uk": "Зіґмарінґен",
        },
        _BADEN_WUERTTEMBERG,
    ),
    (
        "TBB",
        None,
        {
            "en": "Main-Tauber-Kreis",
            "de": "Main-Tauber-Kreis",
            "ru": "Майн-Таубер-Крайс",
            "uk": "Майн-Таубер-Крайс",
        },
        _BADEN_WUERTTEMBERG,
    ),
    (
        "TUT",
        None,
        {
            "en": "Tuttlingen",
            "de": "Tuttlingen",
            "ru": "Туттлинген",
            "uk": "Туттлінген",
        },
        _BADEN_WUERTTEMBERG,
    ),
    (
        "UL",
        None,
        {"en": "Ulm", "de": "Ulm", "ru": "Ульм", "uk": "Ульм"},
        _BADEN_WUERTTEMBERG,
    ),
    (
        "VS",
        None,
        {
            "en": "Schwarzwald-Baar-Kreis",
            "de": "Schwarzwald-Baar-Kreis",
            "ru": "Шварцвальд-Баар-Крайс",
            "uk": "Шварцвальд-Баар-Крайс",
        },
        _BADEN_WUERTTEMBERG,
    ),
    (
        "WN",
        None,
        {
            "en": "Rems-Murr-Kreis",
            "de": "Rems-Murr-Kreis",
            "ru": "Ремс-Мурр-Крайс",
            "uk": "Ремс-Мур-Крайс",
        },
        _BADEN_WUERTTEMBERG,
    ),
    (
        "WT",
        None,
        {"en": "Waldshut", "de": "Waldshut", "ru": "Вальдсхут", "uk": "Вальдсгут"},
        _BADEN_WUERTTEMBERG,
    ),
    # ── North Rhine-Westphalia ────────────────────────────────────────────────
    ("AC", None, {"en": "Aachen", "de": "Aachen", "ru": "Аахен", "uk": "Аахен"}, _NRW),
    (
        "BI",
        None,
        {"en": "Bielefeld", "de": "Bielefeld", "ru": "Билефельд", "uk": "Білефельд"},
        _NRW,
    ),
    (
        "BM",
        None,
        {
            "en": "Rhein-Erft-Kreis",
            "de": "Rhein-Erft-Kreis",
            "ru": "Рейн-Эрфт-Крайс",
            "uk": "Рейн-Ерфт-Крайс",
        },
        _NRW,
    ),
    ("BN", None, {"en": "Bonn", "de": "Bonn", "ru": "Бонн", "uk": "Бонн"}, _NRW),
    ("BO", None, {"en": "Bochum", "de": "Bochum", "ru": "Бохум", "uk": "Бохум"}, _NRW),
    (
        "BOR",
        None,
        {"en": "Borken", "de": "Borken", "ru": "Боркен", "uk": "Боркен"},
        _NRW,
    ),
    (
        "BOT",
        None,
        {"en": "Bottrop", "de": "Bottrop", "ru": "Боттроп", "uk": "Боттроп"},
        _NRW,
    ),
    (
        "D",
        None,
        {
            "en": "Düsseldorf",
            "de": "Düsseldorf",
            "ru": "Дюссельдорф",
            "uk": "Дюссельдорф",
        },
        _NRW,
    ),
    ("DN", None, {"en": "Düren", "de": "Düren", "ru": "Дюрен", "uk": "Дюрен"}, _NRW),
    (
        "DO",
        None,
        {"en": "Dortmund", "de": "Dortmund", "ru": "Дортмунд", "uk": "Дортмунд"},
        _NRW,
    ),
    (
        "DU",
        None,
        {"en": "Duisburg", "de": "Duisburg", "ru": "Дуйсбург", "uk": "Дуйсбург"},
        _NRW,
    ),
    ("E", None, {"en": "Essen", "de": "Essen", "ru": "Эссен", "uk": "Ессен"}, _NRW),
    (
        "EN",
        None,
        {
            "en": "Ennepe-Ruhr-Kreis",
            "de": "Ennepe-Ruhr-Kreis",
            "ru": "Эннепе-Рур-Крайс",
            "uk": "Еннепе-Рур-Крайс",
        },
        _NRW,
    ),
    (
        "EU",
        None,
        {"en": "Euskirchen", "de": "Euskirchen", "ru": "Ойскирхен", "uk": "Ойскірхен"},
        _NRW,
    ),
    (
        "GE",
        None,
        {
            "en": "Gelsenkirchen",
            "de": "Gelsenkirchen",
            "ru": "Гельзенкирхен",
            "uk": "Гельзенкірхен",
        },
        _NRW,
    ),
    (
        "GT",
        None,
        {"en": "Gütersloh", "de": "Gütersloh", "ru": "Гютерсло", "uk": "Гютерсло"},
        _NRW,
    ),
    ("HA", None, {"en": "Hagen", "de": "Hagen", "ru": "Хаген", "uk": "Гаген"}, _NRW),
    ("HER", None, {"en": "Herne", "de": "Herne", "ru": "Херне", "uk": "Херне"}, _NRW),
    (
        "HF",
        None,
        {"en": "Herford", "de": "Herford", "ru": "Херфорд", "uk": "Херфорд"},
        _NRW,
    ),
    (
        "HSK",
        None,
        {
            "en": "Hochsauerlandkreis",
            "de": "Hochsauerlandkreis",
            "ru": "Хохзауэрланд",
            "uk": "Гохзауерланд",
        },
        _NRW,
    ),
    (
        "HX",
        None,
        {"en": "Höxter", "de": "Höxter", "ru": "Хёкстер", "uk": "Гьокстер"},
        _NRW,
    ),
    ("K", None, {"en": "Cologne", "de": "Köln", "ru": "Кёльн", "uk": "Кельн"}, _NRW),
    ("KLE", None, {"en": "Kleve", "de": "Kleve", "ru": "Клеве", "uk": "Клеве"}, _NRW),
    (
        "KR",
        None,
        {"en": "Krefeld", "de": "Krefeld", "ru": "Крефельд", "uk": "Крефельд"},
        _NRW,
    ),
    ("LIP", None, {"en": "Lippe", "de": "Lippe", "ru": "Липпе", "uk": "Ліппе"}, _NRW),
    (
        "ME",
        None,
        {"en": "Mettmann", "de": "Mettmann", "ru": "Меттман", "uk": "Меттман"},
        _NRW,
    ),
    (
        "MG",
        None,
        {
            "en": "Mönchengladbach",
            "de": "Mönchengladbach",
            "ru": "Мёнхенгладбах",
            "uk": "Мьонхенгладбах",
        },
        _NRW,
    ),
    (
        "MI",
        None,
        {
            "en": "Minden-Lübbecke",
            "de": "Minden-Lübbecke",
            "ru": "Минден-Люббеке",
            "uk": "Мінден-Люббеке",
        },
        _NRW,
    ),
    (
        "MK",
        None,
        {
            "en": "Märkischer Kreis",
            "de": "Märkischer Kreis",
            "ru": "Меркишер-Крайс",
            "uk": "Меркішер-Крайс",
        },
        _NRW,
    ),
    (
        "MS",
        None,
        {"en": "Münster", "de": "Münster", "ru": "Мюнстер", "uk": "Мюнстер"},
        _NRW,
    ),
    (
        "NE",
        None,
        {
            "en": "Rhein-Kreis Neuss",
            "de": "Rhein-Kreis Neuss",
            "ru": "Рейн-Крайс Нойс",
            "uk": "Рейн-Крайс Нойс",
        },
        _NRW,
    ),
    (
        "OB",
        None,
        {
            "en": "Oberhausen",
            "de": "Oberhausen",
            "ru": "Оберхаузен",
            "uk": "Оберхаузен",
        },
        _NRW,
    ),
    ("OE", None, {"en": "Olpe", "de": "Olpe", "ru": "Ольпе", "uk": "Ольпе"}, _NRW),
    (
        "PB",
        None,
        {"en": "Paderborn", "de": "Paderborn", "ru": "Падерборн", "uk": "Падерборн"},
        _NRW,
    ),
    (
        "RE",
        None,
        {
            "en": "Recklinghausen",
            "de": "Recklinghausen",
            "ru": "Реклингхаузен",
            "uk": "Реклінггаузен",
        },
        _NRW,
    ),
    (
        "SI",
        None,
        {
            "en": "Siegen-Wittgenstein",
            "de": "Siegen-Wittgenstein",
            "ru": "Зиген-Виттгенштейн",
            "uk": "Зіґен-Вітґенштайн",
        },
        _NRW,
    ),
    (
        "SK",
        None,
        {
            "en": "Rhein-Sieg-Kreis",
            "de": "Rhein-Sieg-Kreis",
            "ru": "Рейн-Зиг-Крайс",
            "uk": "Рейн-Зіг-Крайс",
        },
        _NRW,
    ),
    ("SO", None, {"en": "Soest", "de": "Soest", "ru": "Зост", "uk": "Зост"}, _NRW),
    (
        "ST",
        None,
        {"en": "Steinfurt", "de": "Steinfurt", "ru": "Штайнфурт", "uk": "Штайнфурт"},
        _NRW,
    ),
    ("UN", None, {"en": "Unna", "de": "Unna", "ru": "Унна", "uk": "Унна"}, _NRW),
    (
        "VIE",
        None,
        {"en": "Viersen", "de": "Viersen", "ru": "Фирзен", "uk": "Фірзен"},
        _NRW,
    ),
    (
        "W",
        None,
        {"en": "Wuppertal", "de": "Wuppertal", "ru": "Вупперталь", "uk": "Вупперталь"},
        _NRW,
    ),
    (
        "WAF",
        None,
        {"en": "Warendorf", "de": "Warendorf", "ru": "Варендорф", "uk": "Варендорф"},
        _NRW,
    ),
    ("WES", None, {"en": "Wesel", "de": "Wesel", "ru": "Везель", "uk": "Везель"}, _NRW),
    # ── Hesse ─────────────────────────────────────────────────────────────────
    (
        "DA",
        None,
        {"en": "Darmstadt", "de": "Darmstadt", "ru": "Дармштадт", "uk": "Дармштадт"},
        _HESSE,
    ),
    (
        "F",
        None,
        {
            "en": "Frankfurt am Main",
            "de": "Frankfurt am Main",
            "ru": "Франкфурт-на-Майне",
            "uk": "Франкфурт-на-Майні",
        },
        _HESSE,
    ),
    (
        "FB",
        None,
        {
            "en": "Wetteraukreis",
            "de": "Wetteraukreis",
            "ru": "Веттерау-Крайс",
            "uk": "Веттерау-Крайс",
        },
        _HESSE,
    ),
    (
        "FD",
        None,
        {"en": "Fulda", "de": "Fulda", "ru": "Фульда", "uk": "Фульда"},
        _HESSE,
    ),
    (
        "GI",
        None,
        {"en": "Gießen", "de": "Gießen", "ru": "Гисен", "uk": "Гісен"},
        _HESSE,
    ),
    (
        "HEF",
        None,
        {
            "en": "Hersfeld-Rotenburg",
            "de": "Hersfeld-Rotenburg",
            "ru": "Херсфельд-Ротенбург",
            "uk": "Херсфельд-Ротенбург",
        },
        _HESSE,
    ),
    (
        "HR",
        None,
        {
            "en": "Schwalm-Eder-Kreis",
            "de": "Schwalm-Eder-Kreis",
            "ru": "Швальм-Эдер-Крайс",
            "uk": "Швальм-Едер-Крайс",
        },
        _HESSE,
    ),
    (
        "KS",
        None,
        {"en": "Kassel", "de": "Kassel", "ru": "Кассель", "uk": "Кассель"},
        _HESSE,
    ),
    (
        "LDK",
        None,
        {
            "en": "Lahn-Dill-Kreis",
            "de": "Lahn-Dill-Kreis",
            "ru": "Лан-Дилль-Крайс",
            "uk": "Лан-Ділль-Крайс",
        },
        _HESSE,
    ),
    (
        "MKK",
        None,
        {
            "en": "Main-Kinzig-Kreis",
            "de": "Main-Kinzig-Kreis",
            "ru": "Майн-Кинциг-Крайс",
            "uk": "Майн-Кінціг-Крайс",
        },
        _HESSE,
    ),
    (
        "MR",
        None,
        {
            "en": "Marburg-Biedenkopf",
            "de": "Marburg-Biedenkopf",
            "ru": "Марбург-Биденкопф",
            "uk": "Марбург-Біденкопф",
        },
        _HESSE,
    ),
    (
        "MTK",
        None,
        {
            "en": "Main-Taunus-Kreis",
            "de": "Main-Taunus-Kreis",
            "ru": "Майн-Таунус-Крайс",
            "uk": "Майн-Таунус-Крайс",
        },
        _HESSE,
    ),
    (
        "OF",
        None,
        {
            "en": "Offenbach am Main",
            "de": "Offenbach am Main",
            "ru": "Оффенбах",
            "uk": "Оффенбах",
        },
        _HESSE,
    ),
    (
        "VB",
        None,
        {
            "en": "Vogelsbergkreis",
            "de": "Vogelsbergkreis",
            "ru": "Фогельсберг-Крайс",
            "uk": "Фогельсберг-Крайс",
        },
        _HESSE,
    ),
    (
        "WI",
        None,
        {"en": "Wiesbaden", "de": "Wiesbaden", "ru": "Висбаден", "uk": "Вісбаден"},
        _HESSE,
    ),
    # ── Lower Saxony ──────────────────────────────────────────────────────────
    (
        "BS",
        None,
        {
            "en": "Braunschweig",
            "de": "Braunschweig",
            "ru": "Брауншвейг",
            "uk": "Брауншвейг",
        },
        _LOWER_SAXONY,
    ),
    (
        "CE",
        None,
        {"en": "Celle", "de": "Celle", "ru": "Целле", "uk": "Целле"},
        _LOWER_SAXONY,
    ),
    (
        "CLP",
        None,
        {
            "en": "Cloppenburg",
            "de": "Cloppenburg",
            "ru": "Клоппенбург",
            "uk": "Клоппенбург",
        },
        _LOWER_SAXONY,
    ),
    (
        "CUX",
        None,
        {"en": "Cuxhaven", "de": "Cuxhaven", "ru": "Куксхафен", "uk": "Куксгафен"},
        _LOWER_SAXONY,
    ),
    (
        "DAN",
        None,
        {
            "en": "Lüchow-Dannenberg",
            "de": "Lüchow-Dannenberg",
            "ru": "Люхов-Данненберг",
            "uk": "Люхов-Данненберг",
        },
        _LOWER_SAXONY,
    ),
    (
        "DEL",
        None,
        {
            "en": "Delmenhorst",
            "de": "Delmenhorst",
            "ru": "Дельменхорст",
            "uk": "Дельменгорст",
        },
        _LOWER_SAXONY,
    ),
    (
        "DH",
        None,
        {"en": "Diepholz", "de": "Diepholz", "ru": "Дипхольц", "uk": "Діпгольц"},
        _LOWER_SAXONY,
    ),
    (
        "EL",
        None,
        {"en": "Emsland", "de": "Emsland", "ru": "Эмсланд", "uk": "Емсланд"},
        _LOWER_SAXONY,
    ),
    (
        "EMD",
        None,
        {"en": "Emden", "de": "Emden", "ru": "Эмден", "uk": "Емден"},
        _LOWER_SAXONY,
    ),
    (
        "GF",
        None,
        {"en": "Gifhorn", "de": "Gifhorn", "ru": "Гифхорн", "uk": "Гіфгорн"},
        _LOWER_SAXONY,
    ),
    (
        "GS",
        None,
        {"en": "Goslar", "de": "Goslar", "ru": "Гослар", "uk": "Гослар"},
        _LOWER_SAXONY,
    ),
    (
        "H",
        None,
        {"en": "Hanover", "de": "Hannover", "ru": "Ганновер", "uk": "Ганновер"},
        _LOWER_SAXONY,
    ),
    (
        "HI",
        None,
        {
            "en": "Hildesheim",
            "de": "Hildesheim",
            "ru": "Хильдесхайм",
            "uk": "Гільдесгайм",
        },
        _LOWER_SAXONY,
    ),
    (
        "HOL",
        None,
        {
            "en": "Holzminden",
            "de": "Holzminden",
            "ru": "Хольцминден",
            "uk": "Гольцмінден",
        },
        _LOWER_SAXONY,
    ),
    (
        "HK",
        None,
        {
            "en": "Heidekreis",
            "de": "Heidekreis",
            "ru": "Хайдекрайс",
            "uk": "Гайдекрайс",
        },
        _LOWER_SAXONY,
    ),
    (
        "LER",
        None,
        {"en": "Leer", "de": "Leer", "ru": "Лер", "uk": "Лер"},
        _LOWER_SAXONY,
    ),
    (
        "LG",
        None,
        {"en": "Lüneburg", "de": "Lüneburg", "ru": "Люнебург", "uk": "Люнебург"},
        _LOWER_SAXONY,
    ),
    (
        "NOH",
        None,
        {
            "en": "Grafschaft Bentheim",
            "de": "Grafschaft Bentheim",
            "ru": "Графство Бентхайм",
            "uk": "Графство Бентгайм",
        },
        _LOWER_SAXONY,
    ),
    (
        "NOM",
        None,
        {"en": "Northeim", "de": "Northeim", "ru": "Нортхайм", "uk": "Нортгайм"},
        _LOWER_SAXONY,
    ),
    (
        "OL",
        None,
        {"en": "Oldenburg", "de": "Oldenburg", "ru": "Ольденбург", "uk": "Ольденбург"},
        _LOWER_SAXONY,
    ),
    (
        "OS",
        None,
        {"en": "Osnabrück", "de": "Osnabrück", "ru": "Оснабрюк", "uk": "Оснабрюк"},
        _LOWER_SAXONY,
    ),
    (
        "PE",
        None,
        {"en": "Peine", "de": "Peine", "ru": "Пайне", "uk": "Пайне"},
        _LOWER_SAXONY,
    ),
    (
        "ROW",
        None,
        {
            "en": "Rotenburg (Wümme)",
            "de": "Rotenburg (Wümme)",
            "ru": "Ротенбург-на-Вюмме",
            "uk": "Ротенбург-на-Вюмме",
        },
        _LOWER_SAXONY,
    ),
    (
        "SHG",
        None,
        {"en": "Schaumburg", "de": "Schaumburg", "ru": "Шаумбург", "uk": "Шаумбург"},
        _LOWER_SAXONY,
    ),
    (
        "STD",
        None,
        {"en": "Stade", "de": "Stade", "ru": "Штаде", "uk": "Штаде"},
        _LOWER_SAXONY,
    ),
    (
        "UEL",
        None,
        {"en": "Uelzen", "de": "Uelzen", "ru": "Ульцен", "uk": "Ульцен"},
        _LOWER_SAXONY,
    ),
    (
        "VER",
        None,
        {"en": "Verden", "de": "Verden", "ru": "Верден", "uk": "Верден"},
        _LOWER_SAXONY,
    ),
    (
        "WHV",
        None,
        {
            "en": "Wilhelmshaven",
            "de": "Wilhelmshaven",
            "ru": "Вильгельмсхафен",
            "uk": "Вільгельмсгафен",
        },
        _LOWER_SAXONY,
    ),
    (
        "WL",
        None,
        {
            "en": "Harburg (district)",
            "de": "Landkreis Harburg",
            "ru": "Район Харбург",
            "uk": "Район Гарбург",
        },
        _LOWER_SAXONY,
    ),
    (
        "WOB",
        None,
        {"en": "Wolfsburg", "de": "Wolfsburg", "ru": "Вольфсбург", "uk": "Вольфсбург"},
        _LOWER_SAXONY,
    ),
    (
        "WST",
        None,
        {"en": "Ammerland", "de": "Ammerland", "ru": "Аммерланд", "uk": "Аммерланд"},
        _LOWER_SAXONY,
    ),
    # ── Saxony ────────────────────────────────────────────────────────────────
    (
        "BZ",
        None,
        {"en": "Bautzen", "de": "Bautzen", "ru": "Баутцен", "uk": "Баутцен"},
        _SAXONY,
    ),
    (
        "C",
        None,
        {"en": "Chemnitz", "de": "Chemnitz", "ru": "Хемниц", "uk": "Хемніц"},
        _SAXONY,
    ),
    (
        "DD",
        None,
        {"en": "Dresden", "de": "Dresden", "ru": "Дрезден", "uk": "Дрезден"},
        _SAXONY,
    ),
    (
        "ERZ",
        None,
        {
            "en": "Erzgebirgskreis",
            "de": "Erzgebirgskreis",
            "ru": "Рудные горы (район)",
            "uk": "Рудні гори (район)",
        },
        _SAXONY,
    ),
    (
        "GR",
        None,
        {"en": "Görlitz", "de": "Görlitz", "ru": "Гёрлиц", "uk": "Герліц"},
        _SAXONY,
    ),
    (
        "L",
        None,
        {"en": "Leipzig", "de": "Leipzig", "ru": "Лейпциг", "uk": "Лейпциг"},
        _SAXONY,
    ),
    (
        "MEI",
        None,
        {"en": "Meißen", "de": "Meißen", "ru": "Мейсен", "uk": "Мейсен"},
        _SAXONY,
    ),
    (
        "PIR",
        None,
        {
            "en": "Sächsische Schweiz-Osterzgebirge",
            "de": "Sächsische Schweiz-Osterzgebirge",
            "ru": "Саксонская Швейцария",
            "uk": "Саксонська Швейцарія",
        },
        _SAXONY,
    ),
    (
        "V",
        None,
        {
            "en": "Vogtlandkreis",
            "de": "Vogtlandkreis",
            "ru": "Фогтланд",
            "uk": "Фогтланд",
        },
        _SAXONY,
    ),
    (
        "Z",
        None,
        {"en": "Zwickau", "de": "Zwickau", "ru": "Цвикау", "uk": "Цвікау"},
        _SAXONY,
    ),
    # ── Thuringia ─────────────────────────────────────────────────────────────
    (
        "ABG",
        None,
        {
            "en": "Altenburger Land",
            "de": "Altenburger Land",
            "ru": "Альтенбургер-Ланд",
            "uk": "Альтенбургер-Ланд",
        },
        _THURINGIA,
    ),
    (
        "EF",
        None,
        {"en": "Erfurt", "de": "Erfurt", "ru": "Эрфурт", "uk": "Ерфурт"},
        _THURINGIA,
    ),
    (
        "EIC",
        None,
        {"en": "Eichsfeld", "de": "Eichsfeld", "ru": "Айхсфельд", "uk": "Айхсфельд"},
        _THURINGIA,
    ),
    ("G", None, {"en": "Gera", "de": "Gera", "ru": "Гера", "uk": "Гера"}, _THURINGIA),
    (
        "GTH",
        None,
        {"en": "Gotha", "de": "Gotha", "ru": "Гота", "uk": "Гота"},
        _THURINGIA,
    ),
    (
        "IK",
        None,
        {"en": "Ilm-Kreis", "de": "Ilm-Kreis", "ru": "Ильм-Крайс", "uk": "Ільм-Крайс"},
        _THURINGIA,
    ),
    ("J", None, {"en": "Jena", "de": "Jena", "ru": "Йена", "uk": "Єна"}, _THURINGIA),
    (
        "KYF",
        None,
        {
            "en": "Kyffhäuserkreis",
            "de": "Kyffhäuserkreis",
            "ru": "Кюффхойзер-Крайс",
            "uk": "Кюффгойзер-Крайс",
        },
        _THURINGIA,
    ),
    (
        "NDH",
        None,
        {
            "en": "Nordhausen",
            "de": "Nordhausen",
            "ru": "Нордхаузен",
            "uk": "Нордгаузен",
        },
        _THURINGIA,
    ),
    (
        "SHK",
        None,
        {
            "en": "Saale-Holzland-Kreis",
            "de": "Saale-Holzland-Kreis",
            "ru": "Заале-Хольцланд-Крайс",
            "uk": "Заале-Гольцланд-Крайс",
        },
        _THURINGIA,
    ),
    (
        "SLF",
        None,
        {
            "en": "Saalfeld-Rudolstadt",
            "de": "Saalfeld-Rudolstadt",
            "ru": "Заальфельд-Рудольштадт",
            "uk": "Заальфельд-Рудольштадт",
        },
        _THURINGIA,
    ),
    (
        "SM",
        None,
        {
            "en": "Schmalkalden-Meiningen",
            "de": "Schmalkalden-Meiningen",
            "ru": "Шмалькальден-Майнинген",
            "uk": "Шмалькальден-Майнінген",
        },
        _THURINGIA,
    ),
    (
        "SOK",
        None,
        {
            "en": "Saale-Orla-Kreis",
            "de": "Saale-Orla-Kreis",
            "ru": "Заале-Орла-Крайс",
            "uk": "Заале-Орла-Крайс",
        },
        _THURINGIA,
    ),
    (
        "SON",
        None,
        {"en": "Sonneberg", "de": "Sonneberg", "ru": "Зоннеберг", "uk": "Зоннеберг"},
        _THURINGIA,
    ),
    (
        "UH",
        None,
        {
            "en": "Unstrut-Hainich-Kreis",
            "de": "Unstrut-Hainich-Kreis",
            "ru": "Унструт-Хайних-Крайс",
            "uk": "Унструт-Гайніх-Крайс",
        },
        _THURINGIA,
    ),
    (
        "WAK",
        None,
        {
            "en": "Wartburgkreis",
            "de": "Wartburgkreis",
            "ru": "Вартбургкрайс",
            "uk": "Вартбургкрайс",
        },
        _THURINGIA,
    ),
    (
        "WE",
        None,
        {"en": "Weimar", "de": "Weimar", "ru": "Веймар", "uk": "Веймар"},
        _THURINGIA,
    ),
    # ── Brandenburg ───────────────────────────────────────────────────────────
    (
        "BAR",
        None,
        {"en": "Barnim", "de": "Barnim", "ru": "Барним", "uk": "Барнім"},
        _BRANDENBURG,
    ),
    (
        "EE",
        None,
        {
            "en": "Elbe-Elster",
            "de": "Elbe-Elster",
            "ru": "Эльбе-Эльстер",
            "uk": "Ельбе-Ельстер",
        },
        _BRANDENBURG,
    ),
    (
        "HVL",
        None,
        {"en": "Havelland", "de": "Havelland", "ru": "Хавелланд", "uk": "Гавелланд"},
        _BRANDENBURG,
    ),
    (
        "LDS",
        None,
        {
            "en": "Dahme-Spreewald",
            "de": "Dahme-Spreewald",
            "ru": "Даме-Шпревальд",
            "uk": "Даме-Шпреевальд",
        },
        _BRANDENBURG,
    ),
    (
        "LOS",
        None,
        {"en": "Oder-Spree", "de": "Oder-Spree", "ru": "Одер-Шпре", "uk": "Одер-Шпре"},
        _BRANDENBURG,
    ),
    (
        "MOL",
        None,
        {
            "en": "Märkisch-Oderland",
            "de": "Märkisch-Oderland",
            "ru": "Меркиш-Одерланд",
            "uk": "Меркіш-Одерланд",
        },
        _BRANDENBURG,
    ),
    (
        "OHV",
        None,
        {
            "en": "Oberhavel",
            "de": "Oberhavel",
            "ru": "Обер-Хавель",
            "uk": "Обер-Гавель",
        },
        _BRANDENBURG,
    ),
    (
        "OPR",
        None,
        {
            "en": "Ostprignitz-Ruppin",
            "de": "Ostprignitz-Ruppin",
            "ru": "Остпригниц-Руппин",
            "uk": "Остпрігніц-Руппін",
        },
        _BRANDENBURG,
    ),
    (
        "OSL",
        None,
        {
            "en": "Oberspreewald-Lausitz",
            "de": "Oberspreewald-Lausitz",
            "ru": "Обер-Шпревальд-Лаузиц",
            "uk": "Обер-Шпреевальд-Лаузіц",
        },
        _BRANDENBURG,
    ),
    (
        "P",
        None,
        {"en": "Potsdam", "de": "Potsdam", "ru": "Потсдам", "uk": "Потсдам"},
        _BRANDENBURG,
    ),
    (
        "PM",
        None,
        {
            "en": "Potsdam-Mittelmark",
            "de": "Potsdam-Mittelmark",
            "ru": "Потсдам-Миттельмарк",
            "uk": "Потсдам-Міттельмарк",
        },
        _BRANDENBURG,
    ),
    (
        "PR",
        None,
        {"en": "Prignitz", "de": "Prignitz", "ru": "Прийниц", "uk": "Прігніц"},
        _BRANDENBURG,
    ),
    (
        "SPN",
        None,
        {
            "en": "Spree-Neiße",
            "de": "Spree-Neiße",
            "ru": "Шпре-Найсе",
            "uk": "Шпре-Найсе",
        },
        _BRANDENBURG,
    ),
    (
        "TF",
        None,
        {
            "en": "Teltow-Fläming",
            "de": "Teltow-Fläming",
            "ru": "Тельтов-Флеминг",
            "uk": "Тельтов-Флемінг",
        },
        _BRANDENBURG,
    ),
    (
        "UM",
        None,
        {"en": "Uckermark", "de": "Uckermark", "ru": "Уккермарк", "uk": "Уккермарк"},
        _BRANDENBURG,
    ),
    # ── Saxony-Anhalt ─────────────────────────────────────────────────────────
    (
        "ABI",
        None,
        {
            "en": "Anhalt-Bitterfeld",
            "de": "Anhalt-Bitterfeld",
            "ru": "Анхальт-Биттерфельд",
            "uk": "Анхальт-Біттерфельд",
        },
        _SAXONY_ANHALT,
    ),
    (
        "BLK",
        None,
        {
            "en": "Burgenlandkreis",
            "de": "Burgenlandkreis",
            "ru": "Бургенланд-Крайс",
            "uk": "Бургенланд-Крайс",
        },
        _SAXONY_ANHALT,
    ),
    (
        "DE",
        None,
        {
            "en": "Dessau-Roßlau",
            "de": "Dessau-Roßlau",
            "ru": "Дессау-Росслау",
            "uk": "Дессау-Росслау",
        },
        _SAXONY_ANHALT,
    ),
    (
        "HAL",
        None,
        {"en": "Halle (Saale)", "de": "Halle (Saale)", "ru": "Галле", "uk": "Галле"},
        _SAXONY_ANHALT,
    ),
    (
        "JL",
        None,
        {
            "en": "Jerichower Land",
            "de": "Jerichower Land",
            "ru": "Ерихов Ланд",
            "uk": "Єрихів Ланд",
        },
        _SAXONY_ANHALT,
    ),
    (
        "MD",
        None,
        {"en": "Magdeburg", "de": "Magdeburg", "ru": "Магдебург", "uk": "Магдебург"},
        _SAXONY_ANHALT,
    ),
    (
        "MSH",
        None,
        {
            "en": "Mansfeld-Südharz",
            "de": "Mansfeld-Südharz",
            "ru": "Мансфельд-Южный Гарц",
            "uk": "Мансфельд-Південний Гарц",
        },
        _SAXONY_ANHALT,
    ),
    (
        "SAW",
        None,
        {
            "en": "Altmarkkreis Salzwedel",
            "de": "Altmarkkreis Salzwedel",
            "ru": "Зальцведель",
            "uk": "Зальцведель",
        },
        _SAXONY_ANHALT,
    ),
    (
        "SDL",
        None,
        {"en": "Stendal", "de": "Stendal", "ru": "Штендаль", "uk": "Штендаль"},
        _SAXONY_ANHALT,
    ),
    (
        "SLK",
        None,
        {
            "en": "Salzlandkreis",
            "de": "Salzlandkreis",
            "ru": "Зальцланд-Крайс",
            "uk": "Зальцланд-Крайс",
        },
        _SAXONY_ANHALT,
    ),
    (
        "WB",
        None,
        {
            "en": "Wittenberg",
            "de": "Wittenberg",
            "ru": "Виттенберг",
            "uk": "Віттенберг",
        },
        _SAXONY_ANHALT,
    ),
    # ── Schleswig-Holstein ────────────────────────────────────────────────────
    (
        "FL",
        None,
        {"en": "Flensburg", "de": "Flensburg", "ru": "Фленсбург", "uk": "Фленсбург"},
        _SCHLESWIG_HOLSTEIN,
    ),
    (
        "HEI",
        None,
        {
            "en": "Dithmarschen",
            "de": "Dithmarschen",
            "ru": "Дитмаршен",
            "uk": "Дітмаршен",
        },
        _SCHLESWIG_HOLSTEIN,
    ),
    (
        "HL",
        None,
        {"en": "Lübeck", "de": "Lübeck", "ru": "Любек", "uk": "Любек"},
        _SCHLESWIG_HOLSTEIN,
    ),
    (
        "IZ",
        None,
        {"en": "Steinburg", "de": "Steinburg", "ru": "Штайнбург", "uk": "Штайнбург"},
        _SCHLESWIG_HOLSTEIN,
    ),
    (
        "KI",
        None,
        {"en": "Kiel", "de": "Kiel", "ru": "Киль", "uk": "Кіль"},
        _SCHLESWIG_HOLSTEIN,
    ),
    (
        "NF",
        None,
        {
            "en": "Nordfriesland",
            "de": "Nordfriesland",
            "ru": "Северная Фрисландия",
            "uk": "Північна Фрисландія",
        },
        _SCHLESWIG_HOLSTEIN,
    ),
    (
        "OD",
        None,
        {"en": "Stormarn", "de": "Stormarn", "ru": "Шторманн", "uk": "Шторманн"},
        _SCHLESWIG_HOLSTEIN,
    ),
    (
        "OH",
        None,
        {
            "en": "Ostholstein",
            "de": "Ostholstein",
            "ru": "Восточный Гольштейн",
            "uk": "Східний Гольштейн",
        },
        _SCHLESWIG_HOLSTEIN,
    ),
    (
        "PIN",
        None,
        {"en": "Pinneberg", "de": "Pinneberg", "ru": "Пиннеберг", "uk": "Піннеберг"},
        _SCHLESWIG_HOLSTEIN,
    ),
    (
        "PLÖ",
        None,
        {"en": "Plön", "de": "Plön", "ru": "Плён", "uk": "Плен"},
        _SCHLESWIG_HOLSTEIN,
    ),
    (
        "RD",
        None,
        {
            "en": "Rendsburg-Eckernförde",
            "de": "Rendsburg-Eckernförde",
            "ru": "Рендсбург-Эккернфёрде",
            "uk": "Рендсбург-Еккернферде",
        },
        _SCHLESWIG_HOLSTEIN,
    ),
    (
        "SE",
        None,
        {"en": "Segeberg", "de": "Segeberg", "ru": "Зегеберг", "uk": "Зегеберг"},
        _SCHLESWIG_HOLSTEIN,
    ),
    (
        "SL",
        None,
        {
            "en": "Schleswig-Flensburg",
            "de": "Schleswig-Flensburg",
            "ru": "Шлезвиг-Фленсбург",
            "uk": "Шлезвіг-Фленсбург",
        },
        _SCHLESWIG_HOLSTEIN,
    ),
    # ── Mecklenburg-Vorpommern ────────────────────────────────────────────────
    (
        "HGW",
        None,
        {
            "en": "Greifswald",
            "de": "Greifswald",
            "ru": "Грайфсвальд",
            "uk": "Грайфсвальд",
        },
        _MECKLENBURG,
    ),
    (
        "HRO",
        None,
        {"en": "Rostock", "de": "Rostock", "ru": "Росток", "uk": "Росток"},
        _MECKLENBURG,
    ),
    (
        "HST",
        None,
        {"en": "Stralsund", "de": "Stralsund", "ru": "Штральзунд", "uk": "Штральзунд"},
        _MECKLENBURG,
    ),
    (
        "LRO",
        None,
        {
            "en": "Landkreis Rostock",
            "de": "Landkreis Rostock",
            "ru": "Район Росток",
            "uk": "Район Росток",
        },
        _MECKLENBURG,
    ),
    (
        "LUP",
        None,
        {
            "en": "Ludwigslust-Parchim",
            "de": "Ludwigslust-Parchim",
            "ru": "Людвигслуст-Пархим",
            "uk": "Людвіґслуст-Пархім",
        },
        _MECKLENBURG,
    ),
    (
        "MSE",
        None,
        {
            "en": "Mecklenburgische Seenplatte",
            "de": "Mecklenburgische Seenplatte",
            "ru": "Мекленбургское озёрное плато",
            "uk": "Мекленбурзьке озерне плато",
        },
        _MECKLENBURG,
    ),
    (
        "NB",
        None,
        {
            "en": "Neubrandenburg",
            "de": "Neubrandenburg",
            "ru": "Нойбранденбург",
            "uk": "Нойбранденбург",
        },
        _MECKLENBURG,
    ),
    (
        "OVP",
        None,
        {
            "en": "Vorpommern-Greifswald",
            "de": "Vorpommern-Greifswald",
            "ru": "Передняя Померания — Грайфсвальд",
            "uk": "Передня Померанія — Грайфсвальд",
        },
        _MECKLENBURG,
    ),
    (
        "VR",
        None,
        {
            "en": "Vorpommern-Rügen",
            "de": "Vorpommern-Rügen",
            "ru": "Передняя Померания — Рюген",
            "uk": "Передня Померанія — Рюген",
        },
        _MECKLENBURG,
    ),
    # ── Rhineland-Palatinate ──────────────────────────────────────────────────
    (
        "AK",
        None,
        {
            "en": "Altenkirchen",
            "de": "Altenkirchen",
            "ru": "Альтенкирхен",
            "uk": "Альтенкірхен",
        },
        _RHINELAND_PALATINATE,
    ),
    (
        "AW",
        None,
        {"en": "Ahrweiler", "de": "Ahrweiler", "ru": "Арвайлер", "uk": "Арвайлер"},
        _RHINELAND_PALATINATE,
    ),
    (
        "AZ",
        None,
        {
            "en": "Alzey-Worms",
            "de": "Alzey-Worms",
            "ru": "Альцай-Вормс",
            "uk": "Альцай-Вормс",
        },
        _RHINELAND_PALATINATE,
    ),
    (
        "BIR",
        None,
        {
            "en": "Birkenfeld",
            "de": "Birkenfeld",
            "ru": "Биркенфельд",
            "uk": "Біркенфельд",
        },
        _RHINELAND_PALATINATE,
    ),
    (
        "BIT",
        None,
        {
            "en": "Bitburg-Prüm",
            "de": "Eifelkreis Bitburg-Prüm",
            "ru": "Битбург-Прюм",
            "uk": "Бітбург-Прюм",
        },
        _RHINELAND_PALATINATE,
    ),
    (
        "COC",
        None,
        {
            "en": "Cochem-Zell",
            "de": "Cochem-Zell",
            "ru": "Кохем-Целль",
            "uk": "Кохем-Целль",
        },
        _RHINELAND_PALATINATE,
    ),
    (
        "DAU",
        None,
        {
            "en": "Vulkaneifel",
            "de": "Vulkaneifel",
            "ru": "Вулканайфель",
            "uk": "Вулканайфель",
        },
        _RHINELAND_PALATINATE,
    ),
    (
        "KH",
        None,
        {
            "en": "Bad Kreuznach",
            "de": "Bad Kreuznach",
            "ru": "Бад-Кройцнах",
            "uk": "Бад-Кройцнах",
        },
        _RHINELAND_PALATINATE,
    ),
    (
        "KL",
        None,
        {
            "en": "Kaiserslautern",
            "de": "Kaiserslautern",
            "ru": "Кайзерслаутерн",
            "uk": "Кайзерслаутерн",
        },
        _RHINELAND_PALATINATE,
    ),
    (
        "KO",
        None,
        {"en": "Koblenz", "de": "Koblenz", "ru": "Кобленц", "uk": "Кобленц"},
        _RHINELAND_PALATINATE,
    ),
    (
        "MYK",
        None,
        {
            "en": "Mayen-Koblenz",
            "de": "Mayen-Koblenz",
            "ru": "Майен-Кобленц",
            "uk": "Майен-Кобленц",
        },
        _RHINELAND_PALATINATE,
    ),
    (
        "NW",
        None,
        {
            "en": "Neustadt a.d. Weinstraße",
            "de": "Neustadt a.d. Weinstraße",
            "ru": "Нойштадт-на-Вайнштрассе",
            "uk": "Нойштадт-на-Вайнштрасе",
        },
        _RHINELAND_PALATINATE,
    ),
    (
        "PS",
        None,
        {"en": "Pirmasens", "de": "Pirmasens", "ru": "Пирмазенс", "uk": "Пірмазенс"},
        _RHINELAND_PALATINATE,
    ),
    (
        "SIM",
        None,
        {
            "en": "Rhein-Hunsrück-Kreis",
            "de": "Rhein-Hunsrück-Kreis",
            "ru": "Рейн-Хунсрюк-Крайс",
            "uk": "Рейн-Гунсрюк-Крайс",
        },
        _RHINELAND_PALATINATE,
    ),
    (
        "TR",
        None,
        {"en": "Trier", "de": "Trier", "ru": "Трир", "uk": "Трір"},
        _RHINELAND_PALATINATE,
    ),
    (
        "WIL",
        None,
        {
            "en": "Bernkastel-Wittlich",
            "de": "Bernkastel-Wittlich",
            "ru": "Бернкастель-Виттлих",
            "uk": "Бернкастель-Вітліх",
        },
        _RHINELAND_PALATINATE,
    ),
    (
        "WOR",
        None,
        {"en": "Worms", "de": "Worms", "ru": "Вормс", "uk": "Вормс"},
        _RHINELAND_PALATINATE,
    ),
    (
        "ZW",
        None,
        {
            "en": "Zweibrücken",
            "de": "Zweibrücken",
            "ru": "Цвайбрюккен",
            "uk": "Цвайбрюккен",
        },
        _RHINELAND_PALATINATE,
    ),
    # ── Saarland ──────────────────────────────────────────────────────────────
    (
        "HOM",
        None,
        {
            "en": "Saarpfalz-Kreis",
            "de": "Saarpfalz-Kreis",
            "ru": "Сарпфальц-Крайс",
            "uk": "Сарпфальц-Крайс",
        },
        _SAARLAND,
    ),
    (
        "MZG",
        None,
        {
            "en": "Merzig-Wadern",
            "de": "Merzig-Wadern",
            "ru": "Мерциг-Вадерн",
            "uk": "Мерціґ-Вадерн",
        },
        _SAARLAND,
    ),
    (
        "NK",
        None,
        {
            "en": "Neunkirchen",
            "de": "Neunkirchen",
            "ru": "Нойнкирхен",
            "uk": "Нойнкірхен",
        },
        _SAARLAND,
    ),
    (
        "SB",
        None,
        {
            "en": "Saarbrücken",
            "de": "Saarbrücken",
            "ru": "Саарбрюккен",
            "uk": "Саарбрюккен",
        },
        _SAARLAND,
    ),
    (
        "SLS",
        None,
        {"en": "Saarlouis", "de": "Saarlouis", "ru": "Саарлуи", "uk": "Саарлуї"},
        _SAARLAND,
    ),
    (
        "VK",
        None,
        {
            "en": "Völklingen",
            "de": "Völklingen",
            "ru": "Фёлькlinген",
            "uk": "Фельклінген",
        },
        _SAARLAND,
    ),
    (
        "WND",
        None,
        {
            "en": "Sankt Wendel",
            "de": "Sankt Wendel",
            "ru": "Санкт-Вендель",
            "uk": "Санкт-Вендель",
        },
        _SAARLAND,
    ),
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
    row = conn.execute(
        "SELECT id FROM countries WHERE code = ?", (COUNTRY_CODE,)
    ).fetchone()
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
    """Insert the DE country record and its translations.

    Args:
        conn: An open SQLite connection (foreign keys must be on).
    """
    country_id = _get_or_insert_country(conn)
    _insert_country_translations(conn, country_id)
    logger.info("Seeded country DE (id=%d)", country_id)


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
    wiki_url: str | None,
    name_trans: dict[str, str],
    group_trans: dict[str, str],
    coords: tuple[float, float] | None,
) -> None:
    """Insert one region and its translations."""
    lat = coords[0] if coords else None
    lon = coords[1] if coords else None
    conn.execute(
        "INSERT OR IGNORE INTO regions"
        " (country_id, plate_code, wikipedia_url, latitude, longitude)"
        " VALUES (?, ?, ?, ?, ?)",
        (country_id, plate_code.upper(), wiki_url, lat, lon),
    )
    conn.execute(
        "UPDATE regions SET latitude = ?, longitude = ?"
        " WHERE country_id = ? AND plate_code = ? AND latitude IS NULL",
        (lat, lon, country_id, plate_code.upper()),
    )
    row = conn.execute(
        "SELECT id FROM regions WHERE country_id = ? AND plate_code = ?",
        (country_id, plate_code.upper()),
    ).fetchone()
    _insert_region_translations(conn, row[0], name_trans, group_trans)


def seed_regions(conn: sqlite3.Connection) -> None:
    """Insert all DE region records and their translations.

    Args:
        conn: An open SQLite connection.
    """
    row = conn.execute(
        "SELECT id FROM countries WHERE code = ?", (COUNTRY_CODE,)
    ).fetchone()
    country_id: int = row[0]
    for plate_code, wiki_url, name_trans, group_trans in _REGIONS:
        coords = _COORDS.get(plate_code.upper())
        _seed_single_region(
            conn, country_id, plate_code, wiki_url, name_trans, group_trans, coords
        )
    logger.info("Seeded %d DE regions", len(_REGIONS))


def run(conn: sqlite3.Connection) -> None:
    """Run the full Germany seed: country + all regions.

    Args:
        conn: An open SQLite connection.
    """
    seed_country(conn)
    seed_regions(conn)


def main() -> None:
    """Open the production DB, seed Germany, and close."""
    logging.basicConfig(
        level=logging.INFO, format="%(levelname)s %(name)s — %(message)s"
    )
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    try:
        run(conn)
        conn.commit()
        logger.info("Germany seed complete — %d regions", len(_REGIONS))
    finally:
        conn.close()


if __name__ == "__main__":
    main()
