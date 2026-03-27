# Claude Code Prompt — CarTags Database Setup

---

## Context

You are working on **CarTags** — a Telegram bot and iOS app that helps users identify
the origin (country and region) of a vehicle by its license plate code.

Read `python-code-standards.md` before writing any code. Follow all rules there strictly.

---

## Task

Create the SQLite database schema and seed data scripts for the CarTags bot.

---

## Requirements

### Multilingual support

The bot supports **4 languages**:
- English (`en`)
- German (`de`)
- Russian (`ru`)
- Ukrainian (`uk`)

Every user-facing name — country names, region names, region group names — must be
available in all 4 languages. Store translations in a dedicated translations table,
not as separate columns.

### Schema rules

- Use `INTEGER PRIMARY KEY AUTOINCREMENT` for all IDs
- All `code` fields are stored in `UPPER CASE`
- Add appropriate indexes for all fields used in WHERE clauses
- Use `UNIQUE` constraints wherever logically required
- Add `created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP` to every table
- Foreign keys must be enforced: run `PRAGMA foreign_keys = ON` at connection time

### Translation table pattern

Use a single `translations` table to store all multilingual strings:

```
translations(id, entity_type, entity_id, language_code, field, value)
```

Where:
- `entity_type` — e.g. `"country"`, `"region"`
- `entity_id`   — FK to the corresponding table
- `language_code` — `"en"`, `"de"`, `"ru"`, `"uk"`
- `field`       — `"name"` or `"region_group"` (administrative region name)
- `value`       — the translated string

---

## Files to Create

### 1. `db/schema.sql`

Pure SQL file. Must include:

- `countries` table — ISO code, flag emoji, sort order
- `regions` table — plate code, country FK, optional Wikipedia URL for reference
- `translations` table — all multilingual names as described above
- All indexes
- All constraints

### 2. `db/init_db.py`

Python script that:
- Creates the database file at `db/cartags.db`
- Runs `schema.sql` to create all tables
- Is idempotent — safe to run multiple times (`CREATE TABLE IF NOT EXISTS`)
- Logs each step clearly

### 3. `data/seed_de.py`

Seed script for **Germany** — the largest dataset (~430 plate codes).

Each record must include translations in all 4 languages for:
- The region name (e.g. "München" / "Munich" / "Мюнхен" / "Мюнхен")
- The administrative group name (e.g. "Bayern" / "Bavaria" / "Бавария" / "Баварія")

Include at minimum these 30 well-known German plate codes as a starting dataset
(add more if you know them with confidence):

`B, M, HH, K, F, S, D, L, HB, MUC, BN, DD, LE, N, DO, E, HO, BA, WU, FR,
KA, MA, HD, BI, GE, MS, OB, BO, MG, SB`

### 4. `data/seed_at.py`

Seed script for **Austria** (~120 plate codes).

Each Austrian plate code encodes the district. Include translations for:
- District name in all 4 languages
- State (Bundesland) name in all 4 languages

Include at minimum:
`W, GD, KR, LF, PL, SB, TU, WB, WN, WR, BL, EF, ER, GF, GM, GR, HB, HO,
KO, LA, LI, LL, ME, MK, MO, MT, NK, PE, PL, PO, RE, RK, SL, SR, ST, SV,
TK, TU, UU, VB, VL, VK, WK, ZE, AM, BA, BM, BR, DL, EF, EU, FF, FK, FR,
FU, GB, GD, GF, GM, GR, GS, GU, HA, HB, HE, HF, HO, IK, IM, JE, JO, JU,
KF, KI, KL, KO, KU, LA, LB, LE, LF, LI, LL, LN, LZ, MA, MD, ME, MK, MO,
MT, MU, MZ, NA, NE, NK, OW, PE, PK, PL, PO, PT, PU, RE, RO, RO, VB, VK,
VL, VO, VK, WB, WE, WK, WL, WN, WR, WS, WT, ZE, ZT`

### 5. `data/seed_ua.py`

Seed script for **Ukraine** (~27 plate codes, one per oblast + Kyiv city).

Include translations for:
- Oblast name in all 4 languages
- Note: Ukrainian plates use a two-letter regional prefix (AA, AB, AC, etc.)

All 27 codes:
`AA, AB, AC, AE, AH, AI, AK, AM, AO, AP, AT, AX, BA, BB, BC, BE, BH, BI,
BK, BM, BO, BP, BT, CA, CB, CC, CE`

Map each code to the correct oblast with all 4 language translations.

---

## Helper Script

### 6. `db/verify_db.py`

A script to verify the database after seeding:
- Print total counts: countries, regions, translations
- Print a sample lookup: find "DE" + "M" and show all 4 language translations
- Print a sample lookup: find "AT" + "W" and show all 4 language translations
- Print a sample lookup: find "UA" + "AA" and show all 4 language translations
- Report any regions missing translations for any of the 4 languages

---

## Query Helper

### 7. `db/database.py`

Python module with typed query functions. Follow `python-code-standards.md`.

Must include:

```python
def find_region(country_code: str, plate_code: str, lang: str = "en") -> RegionResult | None:
    """Return region info for a country + plate code in the requested language."""

def find_by_plate_only(plate_code: str, lang: str = "en") -> list[RegionResult]:
    """Search across all countries by plate code only. Returns all matches."""

def get_country_regions(country_code: str, lang: str = "en",
                        offset: int = 0, limit: int = 20) -> list[RegionResult]:
    """Return paginated list of all regions for a country."""

def get_all_countries(lang: str = "en") -> list[CountryResult]:
    """Return all supported countries sorted by sort_order."""
```

Use `dataclasses` for `RegionResult` and `CountryResult` as defined in `python-code-standards.md`.

---

## Expected File Structure After Completion

```
cartags-bot/
├── db/
│   ├── schema.sql
│   ├── init_db.py
│   ├── database.py
│   ├── verify_db.py
│   └── cartags.db          ← generated, not committed to git
├── data/
│   ├── seed_de.py
│   ├── seed_at.py
│   └── seed_ua.py
```

---

## How to Run

After all files are created, the setup sequence must work as follows:

```bash
python db/init_db.py      # creates tables
python data/seed_de.py    # seeds Germany
python data/seed_at.py    # seeds Austria
python data/seed_ua.py    # seeds Ukraine
python db/verify_db.py    # verify everything looks correct
```

---

## Constraints

- Do not use any ORM (no SQLAlchemy, no Peewee) — raw `sqlite3` only
- All seed data must be hardcoded in the scripts — no external CSV or JSON files
- If a translation is the same across languages (e.g. city name "Wien" in EN and DE),
  still store it explicitly for all 4 languages — do not skip any row
- All scripts must be runnable independently and be idempotent
- Use `INSERT OR IGNORE` or `INSERT OR REPLACE` to allow re-running seed scripts safely
