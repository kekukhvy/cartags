# Claude Code Prompt — Multi-Country Seed Agents

## Context

You are working on **CarTags** — a Telegram bot and iOS app for license plate region
lookup. 

Read `python-code-standards.md` before writing any code. Follow all rules strictly.

The database schema and Germany seed (`data/seed_de.py`) already exist as reference.
Use `data/seed_de.py` as the canonical template for every new seed file.

---

## Overview

Create one seed agent per country, then wire all of them into the application.

**Countries to implement** (in priority order):

| Priority | Code | Country          | Regional logic                        |
|----------|------|------------------|---------------------------------------|
|                  |
| P1       | PL   | Poland           | 2–3 letters = Powiat                  |
| P1       | CH   | Switzerland      | 2 letters = Canton                    |
| P2       | CZ   | Czech Republic   | 1 letter + digit = District           |
| P2       | RO   | Romania          | 2 letters = Județ                     |
| P2       | BG   | Bulgaria         | 1–2 letters = Oblast                  |
| P2       | HR   | Croatia          | 2 letters = City / County             |
| P2       | RS   | Serbia           | 2 letters = City / Municipality       |
| P2       | SI   | Slovenia         | 2 letters = Municipality              |
| P3       | ME   | Montenegro       | 2 letters = Municipality              |
| P3       | MK   | North Macedonia  | 2 letters = City                      |
| P3       | GR   | Greece           | 3 letters = Prefecture                |                  |
| P3       | BY   | Belarus          | 1 digit = Region                      |
| P3       | RU   | Russia           | 2–3 digits = Region                   |
| P3       | TR   | Turkey           | 2–3 digits = Province                 |
| P3       | XK   | Kosovo           | 2 letters = Region                    |
| P3       | NO   | Norway           | 2 letters = Fylke (pre-2018 system)   |
| P3       | IE   | Ireland          | 2 letters = County                    |

---

## Task 1 — Create one seed file per country

For **every country in the table above**, create `data/seed_<lower_code>.py`.

### Rules for each seed file

- Follow the exact structure of `data/seed_de.py`
- Every region entry must have translations in all 4 languages: `en`, `de`, `ru`, `uk`
- Use `INSERT OR IGNORE` — all scripts must be idempotent
- Set `COUNTRY_SORT_ORDER` incrementally (AT=2, PL=3, CH=4, CZ=5 … IE=19)
- Include **all** currently active plate codes for the country — do not omit any
- For countries with numeric codes (BY, RU, TR) store them as strings: `"77"`, `"34"`
- Include `lat` and `lon` (geographic center of each region's main city/district seat)
- Use the reusable state/group name dicts pattern from `seed_de.py` to avoid
  repeating the same region group translations on every entry

### Country-specific notes

**PL — Poland** (~380 codes)
- Format: `WA`, `KR`, `GD`, `WR` etc. (2–3 letters)
- Group = Województwo (16 voivodeships)
- First letter often indicates voivodeship: W=Mazowieckie, K=Małopolskie etc.

**CH — Switzerland** (26 codes, one per canton)
- Format: `ZH`, `BE`, `LU`, `UR`, `SZ`, `OW`, `NW`, `GL`, `ZG`, `FR`, `SO`,
  `BS`, `BL`, `SH`, `AR`, `AI`, `SG`, `GR`, `AG`, `TG`, `TI`, `VD`, `VS`,
  `NE`, `GE`, `JU`
- Group = Switzerland (single level, no sub-grouping needed)
- Each canton name needs all 4 languages (e.g. Bern/Berne/Берн/Берн)

**CZ — Czech Republic** (~77 codes)
- Format: `1A`–`8Z` (digit + letter prefix indicates region)
- Group = Kraj (14 regions)

**RO — Romania** (42 codes)
- Format: `B` (Bucharest), `AB`, `AR`, `AG` etc.
- Group = Regiune de dezvoltare (8 development regions)

**BG — Bulgaria** (28 codes)
- Format: `A`, `B`, `BH`, `BL` etc.
- Group = Oblast (28 oblasts, same as the code coverage)

**HR — Croatia** (21 codes)
- Format: `ZG`, `ST`, `RI`, `OS` etc.
- Group = Županija (21 counties)

**RS — Serbia** (30 codes)
- Format: `BG`, `NS`, `NI`, `KG` etc.
- Group = Okrug / Region

**SI — Slovenia** (13 codes)
- Format: `LJ`, `MB`, `CE`, `KR` etc.
- Group = Statistična regija (12 statistical regions)

**ME — Montenegro** (21 codes)
- Format: `PG`, `BD`, `TG` etc.
- Group = Montenegro (single level)

**MK — North Macedonia** (34 codes)
- Format: `SK`, `BT`, `OH` etc.
- Group = Region

**GR — Greece** (~50 codes)
- Format: `AAA`, `ABB` etc. (3 letters)
- Group = Περιφέρεια (13 regions)


**BY — Belarus** (7 codes)
- Format: `1`–`7` (single digit)
- Group = Oblast + Minsk city

**RU — Russia** (~85 codes)
- Format: `77`, `78`, `50` etc.
- Group = Federal subject / Oblast / Krai / Republic

**TR — Turkey** (81 codes)
- Format: `1`–`81`
- Group = İl (province)

**XK — Kosovo** (7 codes)
- Format: `PR`, `PE`, `PZ`, `GJ`, `UR`, `FE`, `MF`
- Group = Kosovo

**NO — Norway** (15 codes, pre-2018 system still readable on older plates)
- Format: `M` (Oslo), `N`, `SF` etc.
- Group = Fylke

**IE — Ireland** (26 codes)
- Format: `D` (Dublin), `C` (Cork), `G` (Galway) etc.
- Group = Province (Leinster, Munster, Connacht, Ulster)

---

## Task 2 — Create a master seed runner

Create `data/seed_all.py`:

```python
"""Run all country seed scripts in priority order.

Usage::

    python data/seed_all.py              # seed everything
    python data/seed_all.py --only DE,AT # seed specific countries
    python data/seed_all.py --skip RU,BY # skip specific countries
"""

import argparse
import logging
import sqlite3
from pathlib import Path

from data import (
    seed_de, seed_at, seed_pl, seed_ch, seed_cz, seed_ro,
    seed_bg, seed_hr, seed_rs, seed_si, seed_me, seed_mk,
    seed_gr, seed_ua, seed_by, seed_ru, seed_tr, seed_xk,
    seed_no, seed_ie,
)

# Ordered list of (country_code, module) pairs
SEED_AGENTS: list[tuple[str, object]] = [
    ("DE", seed_de), ("AT", seed_at), ("PL", seed_pl),
    ("CH", seed_ch), ("CZ", seed_cz), ("RO", seed_ro),
    ("BG", seed_bg), ("HR", seed_hr), ("RS", seed_rs),
    ("SI", seed_si), ("ME", seed_me), ("MK", seed_mk),
    ("GR", seed_gr), ("UA", seed_ua), ("BY", seed_by),
    ("RU", seed_ru), ("TR", seed_tr), ("XK", seed_xk),
    ("NO", seed_no), ("IE", seed_ie),
]
```

Each agent module must expose a `run(conn: sqlite3.Connection) -> None` function
(same as `seed_de.py`). The runner calls `agent.run(conn)` for each selected agent
inside a single transaction.

---

## Task 3 — Update `db/database.py`

### 3a — Update `get_all_countries`

The existing function must now return all seeded countries sorted by `sort_order`.
No change needed to the signature — just verify the SQL returns all rows.

### 3b — Add language fallback

If a translation for the requested language is missing, fall back to `"en"`.
Implement this in a private helper:

```python
def _get_translation(
    conn: sqlite3.Connection,
    entity_type: str,
    entity_id: int,
    language_code: str,
    field: str,
) -> str | None:
    """Return translation for the given language, falling back to 'en'."""
    row = conn.execute(
        "SELECT value FROM translations "
        "WHERE entity_type=? AND entity_id=? AND language_code=? AND field=?",
        (entity_type, entity_id, language_code, field),
    ).fetchone()
    if row:
        return row[0]
    # fallback to English
    row = conn.execute(
        "SELECT value FROM translations "
        "WHERE entity_type=? AND entity_id=? AND language_code='en' AND field=?",
        (entity_type, entity_id, field),
    ).fetchone()
    return row[0] if row else None
```

Replace all inline translation lookups in the existing query functions with
calls to `_get_translation`.

---

## Task 4 — Update handlers

### 4a — `handlers/search.py`

The free-text search handler must now search across **all countries**, not just DE.

When a user sends `M` (without country code), the bot searches all countries and:
- If exactly one match → reply directly
- If multiple matches → show inline buttons, one per match:
  `[🇩🇪 Munich, Germany]  [🇲🇰 Makedonska Kamenica, MK]`

### 4b — `handlers/country.py`

`/list` must now show all seeded countries grouped by priority tier,
with a flag emoji and name in the user's language.

```
🌍 Supported countries

⭐ Europe
🇩🇪 Germany  🇦🇹 Austria  🇵🇱 Poland  🇨🇭 Switzerland
🇨🇿 Czechia  🇷🇴 Romania  🇧🇬 Bulgaria  🇭🇷 Croatia
🇷🇸 Serbia   🇸🇮 Slovenia  🇲🇪 Montenegro  🇲🇰 North Macedonia
🇬🇷 Greece   🇮🇪 Ireland  🇳🇴 Norway

🌏 Eastern Europe & Caucasus
🇺🇦 Ukraine  🇧🇾 Belarus  🇷🇺 Russia

🌏 Asia / Middle East
🇹🇷 Turkey

🏛 Other
🇽🇰 Kosovo
```

---

## Task 5 — Update `db/verify_db.py`

Extend the verification script to check every seeded country:

```python
def verify_country(conn: sqlite3.Connection, country_code: str) -> None:
    """Print region count and flag any missing translations for a country."""
```

For each country print:
- Total region count
- Count of regions missing any of the 4 language translations
- One sample lookup (first region alphabetically) with all 4 translations

---

## Run order after implementation

```bash
python db/init_db.py        # ensure schema is up to date
python data/seed_all.py     # seed all countries
python db/verify_db.py      # verify no missing translations
python bot.py               # start the bot
```

---

## Constraints

- Never break the existing DE seed — `seed_de.py` must still run independently
- Every seed file must be runnable standalone: `python data/seed_at.py`
- All plate codes stored as `UPPER CASE` strings — including numeric ones: `"77"`, `"34"`
- `lat`/`lon` required for every region — use geographic center of the main city
- Follow all rules in `python-code-standards.md`
- Do not add any new pip dependencies
