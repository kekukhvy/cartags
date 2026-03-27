# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

CarTags is a Telegram bot for looking up vehicle license plate region origins. Users input plate codes (e.g., `DE M`, `AT W`) and receive region/city/country information.

**Docs:**
- [`docs/cartags-bot-spec.md`](docs/cartags-bot-spec.md) — full bot specification: commands, user flows, DB schema, deployment
- [`docs/python-code-standards.md`](docs/python-code-standards.md) — mandatory coding standards for every file written or modified

**Stack:** Python 3.14, python-telegram-bot 20.x, SQLite, Docker (Synology NAS deployment)

## Running the Bot

```bash
# Local development (once implemented)
python bot.py

# Docker deployment
docker-compose up -d
docker-compose logs -f
```

**Required env vars** (in `.env`):
```
BOT_TOKEN=<telegram_bot_token>
LOG_LEVEL=INFO
```

## Project Structure

```
bot.py               # Entry point — wires handlers, starts polling. Zero business logic.
handlers/
  start.py           # /start, /help, /about
  search.py          # /plate command and free-form text input
  country.py         # /country, /list
db/
  database.py        # All SQL queries — repository layer
  cartags.db         # SQLite file
data/
  seed_de.py         # Germany (~430 codes)
  seed_at.py         # Austria (~120 codes)
  seed_ua.py         # Ukraine (~30 codes)
utils/
  formatter.py       # Pure formatting functions, no I/O
constants.py         # ALL shared constants and message templates
```

## Architecture & Layer Rules

Strict layer separation — violations are bugs, not style issues:

| Layer | Responsibility | Must NOT contain |
|---|---|---|
| `bot.py` | Handler registration, polling | Business logic, SQL |
| `handlers/` | Parse Telegram input, call db/utils, send response | SQL, direct Telegram SDK outside handlers |
| `db/` | All SQLite queries | Telegram API calls |
| `utils/` | Pure formatting functions | Side effects, I/O |
| `constants.py` | All magic values, message strings | Logic |

## Database Schema

```sql
CREATE TABLE countries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    code TEXT NOT NULL UNIQUE,   -- ISO: DE, AT, UA
    name_en TEXT NOT NULL,
    name_ru TEXT NOT NULL,
    emoji TEXT NOT NULL
);

CREATE TABLE regions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    country_id INTEGER NOT NULL REFERENCES countries(id),
    plate_code TEXT NOT NULL,
    name_local TEXT NOT NULL,
    name_ru TEXT,
    region_name TEXT,
    UNIQUE(country_id, plate_code)
);
-- Indexes: idx_regions_plate_code, idx_regions_country_id
```

Search is case-insensitive via `UPPER()`. Pagination at 20 regions per page (Germany has 400+).

## Coding Standards (from [`docs/python-code-standards.md`](docs/python-code-standards.md))

**Python 3.14 syntax only:**
```python
# CORRECT
def find(codes: list[str]) -> str | None: ...

# WRONG — do not use
from typing import List, Optional
def find(codes: List[str]) -> Optional[str]: ...
```

**No magic literals** — all constants in `constants.py`, all fixed-value variables as `Enum`:
```python
class CountryCode(str, Enum):
    GERMANY = "DE"

class SearchMode(Enum):
    BY_PLATE_AND_COUNTRY = auto()
    BY_PLATE_ONLY = auto()
```

**Dataclasses over dicts** between layers — use `frozen=True`:
```python
@dataclass(frozen=True)
class RegionResult:
    plate_code: str
    name_local: str
    country_code: str
    emoji: str
    ...
```

**Async handlers** — all handlers are `async def`; SQLite stays synchronous (no async DB library needed):
```python
async def plate_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    result = find_region(country_code, plate_code)  # sync SQLite — fine
    await update.message.reply_text(format_region_response(result))
```

**Other rules:**
- Max 20 lines per function — split if longer
- All public functions need docstrings in English
- `logger = logging.getLogger(__name__)` per module — never `print()`
- Use `pathlib.Path` relative to `__file__` for file paths — no hardcoded paths
- Specific exceptions only — no bare `except:`
- No `global` variables, no `import *`, no mutable default arguments, no commented-out code

## Testing

```bash
pytest                   # run all tests
pytest tests/test_db.py  # run a single file
```

Tests use an in-memory SQLite DB (never `cartags.db`). Structure:

```
tests/
  conftest.py           # shared fixtures: in-memory DB seeded with test data
  test_db.py            # db layer queries
  test_formatter.py     # utils/formatter pure functions
  test_search_parser.py # parse_search_query input variations
```

See [`docs/python-code-standards.md`](docs/python-code-standards.md) §17 for full testing rules and fixture patterns.
