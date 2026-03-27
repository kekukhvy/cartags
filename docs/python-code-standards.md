# Python Coding Standards for AI

These rules apply to every file you write or modify in this project.
When in doubt — keep it simple and readable. I must be able to understand what's happening.

---

## 1. Python Version & Runtime

- Use **Python 3.14** — never suggest downgrade-compatible syntax
- Use modern built-in generics for type hints: `list[str]`, `dict[str, int]`, `tuple[int, ...]`
- Do **not** import `List`, `Dict`, `Tuple`, `Optional` from `typing` — use built-ins and `X | None` instead

```python
# WRONG
from typing import List, Optional
def find(codes: List[str]) -> Optional[str]: ...

# CORRECT
def find(codes: list[str]) -> str | None: ...
```

---

## 2. No Magic Literals

Never use raw strings, numbers, or repeated values inline. Extract everything into named constants or enums.

```python
# WRONG
if country_code == "DE":
    return "🇩🇪"

if limit > 20:
    ...

# CORRECT
DEFAULT_PAGE_SIZE = 20
UNKNOWN_COUNTRY = "Unknown country code"

class CountryCode(str, Enum):
    GERMANY = "DE"
    AUSTRIA = "AT"
    UKRAINE = "UA"
```

---

## 3. Enums Over Raw Strings

Whenever a variable has a fixed set of possible values — use an `Enum`. This applies to country codes, bot states, error types, search modes, anything categorical.

```python
from enum import Enum, auto

class SearchMode(Enum):
    BY_PLATE_AND_COUNTRY = auto()
    BY_PLATE_ONLY = auto()

class BotCommand(str, Enum):
    START = "start"
    HELP = "help"
    PLATE = "plate"
    COUNTRY = "country"
    LIST = "list"
    ABOUT = "about"
```

Use `str, Enum` when the value needs to be a string (e.g. command names, country codes).
Use `Enum` + `auto()` for internal states that are never serialized.

---

## 4. Single Responsibility Principle

Each module, class, and function does exactly one thing.

- `bot.py` — wires handlers, starts polling. Zero business logic.
- `handlers/` — reads Telegram input, calls services, sends response. Zero SQL.
- `db/` — all database access. Zero Telegram API.
- `utils/` — pure functions, no side effects, no I/O.
- `services/` — business logic if needed. No Telegram, no raw SQL.

```python
# WRONG — handler doing SQL directly
async def plate_handler(update, context):
    code = context.args[0]
    conn = sqlite3.connect("cartags.db")
    row = conn.execute("SELECT * FROM regions WHERE plate_code = ?", (code,)).fetchone()
    await update.message.reply_text(row["name_local"])

# CORRECT — handler delegates to db layer
async def plate_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    code = context.args[0]
    result = find_region_by_plate(code)
    await update.message.reply_text(format_region_response(result))
```

---

## 5. Short Functions

- **Maximum 20 lines per function** — if it grows longer, split it
- One function = one job
- The function name must describe exactly what it does

```python
# WRONG — one big function doing everything
async def handle_message(update, context):
    text = update.message.text.strip().upper()
    parts = text.split()
    if len(parts) == 2:
        # search by country + code
        ...
    elif len(parts) == 1:
        # search by code only
        ...
    else:
        # error
        ...
    # format response
    # send message
    ...

# CORRECT — each concern is a named function
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = parse_search_query(update.message.text)
    result = execute_search(query)
    response = format_search_response(result)
    await update.message.reply_text(response)
```

---

## 6. Type Hints Everywhere

Every function must have type hints on all parameters and the return type. No exceptions.

```python
# WRONG
def find_region(country_code, plate_code):
    ...

# CORRECT
def find_region(country_code: str, plate_code: str) -> dict | None:
    ...
```

For Telegram handlers, always annotate with proper types:

```python
from telegram import Update
from telegram.ext import ContextTypes

async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    ...
```

---

## 7. Dataclasses Over Raw Dicts

Never pass raw `dict` or `sqlite3.Row` objects between layers. Wrap data in `dataclass`.

```python
# WRONG
def find_region(country_code: str, plate_code: str) -> dict | None:
    ...
result["name_local"]  # fragile, no autocomplete, no validation

# CORRECT
from dataclasses import dataclass

@dataclass(frozen=True)
class RegionResult:
    plate_code: str
    name_local: str
    name_ru: str | None
    region_name: str | None
    country_code: str
    country_name: str
    emoji: str

def find_region(country_code: str, plate_code: str) -> RegionResult | None:
    ...
result.name_local  # clear, safe, IDE-friendly
```

Use `frozen=True` for data that should not be mutated after creation.

---

## 8. Constants File

All shared constants live in `constants.py` at the project root.

```python
# constants.py

MAX_REGIONS_PER_PAGE = 20
MAX_AMBIGUOUS_RESULTS = 5
BOT_USERNAME = "cartags_bot"

MESSAGES = {
    "not_found": "Code {code} not found.",
    "ambiguous": "Found in multiple countries. Please specify:",
    "empty_country": "No regions found for country {code}.",
}
```

Never duplicate the same string in two places.

---

## 9. Error Handling

- Never use bare `except:` — always catch specific exceptions
- Never silently swallow exceptions — always log them
- User-facing errors must be friendly messages, not raw exceptions

```python
# WRONG
try:
    result = find_region(country, plate)
except:
    pass

# CORRECT
import logging
logger = logging.getLogger(__name__)

try:
    result = find_region(country, plate)
except sqlite3.DatabaseError as e:
    logger.error("Database error while searching region: %s", e)
    await update.message.reply_text("Something went wrong. Please try again.")
    return
```

---

## 10. Logging

- Use `logging` module — never `print()` in production code
- Create a logger per module: `logger = logging.getLogger(__name__)`
- Use appropriate levels: `DEBUG` for details, `INFO` for flow, `WARNING` for unexpected but handled, `ERROR` for failures

```python
# WRONG
print(f"Searching for {plate_code}")

# CORRECT
logger.info("Searching for plate code: %s in country: %s", plate_code, country_code)
```

---

## 11. Design Patterns — When to Use

Apply patterns only when they genuinely simplify the code. Do not over-engineer.

| Pattern | When to use in this project |
|---|---|
| **Repository** | `db/` layer — isolate all SQL behind functions, never write SQL in handlers |
| **Factory** | Building Telegram `InlineKeyboardMarkup` objects with varying button sets |
| **Strategy** | If search behavior varies significantly by country (future) |
| **Formatter / Builder** | `utils/formatter.py` — constructing response text from data objects |

Do **not** use patterns just to use them. If simple procedural code is clearer — use that.

---

## 12. Async Rules

This project uses `python-telegram-bot` v20 which is fully async.

- All handler functions must be `async def`
- Use `await` for all Telegram API calls
- Do **not** mix sync and async database calls in the same function
- SQLite is synchronous — keep DB calls fast and simple, no need for async DB library at this scale

```python
# CORRECT async handler pattern
async def plate_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not context.args:
        await update.message.reply_text("Usage: /plate DE M")
        return

    country_code, plate_code = parse_plate_args(context.args)
    result = find_region(country_code, plate_code)  # sync SQLite — fine

    if result is None:
        await update.message.reply_text(f"Code {plate_code} not found for {country_code}.")
        return

    await update.message.reply_text(format_region_response(result))
```

---

## 13. No Clever Code

Write code for readability, not cleverness. If you need a comment to explain what a line does — rewrite the line.

```python
# WRONG — clever but unreadable
result = next((r for r in rows if r.plate_code.upper() == code.upper()), None)

# CORRECT — clear intent
def find_matching_region(rows: list[RegionResult], code: str) -> RegionResult | None:
    normalized = code.upper()
    for region in rows:
        if region.plate_code.upper() == normalized:
            return region
    return None
```

---

## 14. Docstrings

Write docstrings for all public functions. One-line for simple functions, multi-line for complex ones.

```python
def find_region(country_code: str, plate_code: str) -> RegionResult | None:
    """Return region info for a given country and plate code, or None if not found."""
    ...

def parse_search_query(text: str) -> SearchQuery:
    """
    Parse raw user input into a structured SearchQuery.

    Handles formats:
      - "DE M"      → SearchQuery(country="DE", plate="M")
      - "M"         → SearchQuery(country=None, plate="M")
      - "DE"        → SearchQuery(country="DE", plate=None)
    """
    ...
```

Write docstrings in **English** only.

---

## 15. File & Naming Conventions

| Thing | Convention | Example |
|---|---|---|
| Files | `snake_case` | `plate_handler.py` |
| Functions | `snake_case` | `find_region_by_code()` |
| Classes | `PascalCase` | `RegionResult` |
| Constants | `UPPER_SNAKE_CASE` | `MAX_PAGE_SIZE` |
| Enums | `PascalCase` + `UPPER` values | `CountryCode.GERMANY` |
| Type aliases | `PascalCase` | `PlateCode = str` |

---

## 16. What to Avoid

- **No `global` variables** — pass dependencies explicitly
- **No mutable default arguments** — `def f(items=[])` is a Python trap
- **No `import *`** — always explicit imports
- **No hardcoded file paths** — use `pathlib.Path` relative to `__file__`
- **No commented-out code** — delete it, git has history
- **No TODOs left in committed code** — either do it or open a ticket

```python
# WRONG
DB_PATH = "/home/vlad/cartags/db/cartags.db"

# CORRECT
from pathlib import Path
DB_PATH = Path(__file__).parent / "cartags.db"
```

---

## 17. Testing

All tests live in `tests/`. Use `pytest`. No mocking the database — tests run against an in-memory SQLite instance seeded with fixture data.

```bash
pytest                  # run all tests
pytest tests/test_db.py # run a single file
```

**Structure:**

```
tests/
  conftest.py           # shared fixtures: in-memory DB, seeded countries/regions
  test_db.py            # db layer: find_by_code, find_by_plate_only, get_country_regions
  test_formatter.py     # utils/formatter pure functions
  test_search_parser.py # parse_search_query input variations
```

**Rules:**
- Tests must use the in-memory DB fixture — never touch `cartags.db`
- Each test function tests exactly one behavior
- Test names describe the scenario: `test_find_by_code_returns_none_for_unknown_plate`
- Fixtures in `conftest.py` only — no setup/teardown inside test functions
- All test functions have type hints and return `None`

```python
# conftest.py pattern
import pytest
import sqlite3
from db.database import init_schema, seed_test_data

@pytest.fixture
def db() -> sqlite3.Connection:
    """In-memory SQLite DB seeded with test countries and regions."""
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    init_schema(conn)
    seed_test_data(conn)
    return conn
```

```python
# test example
def test_find_by_code_returns_region_for_valid_input(db: sqlite3.Connection) -> None:
    """find_by_code returns correct region when country and plate match."""
    result = find_by_code("DE", "M", conn=db)
    assert result is not None
    assert result.name_local == "München"
```

- [ ] Tests added/updated for new checklist
- [ ] No fixture duplication — reuse `conftest.py`

---

## Quick Checklist Before Submitting Code

- [ ] All functions have type hints and return types
- [ ] No magic strings or numbers — everything is a constant or enum
- [ ] No function longer than 20 lines
- [ ] Each function does exactly one thing
- [ ] No SQL in handlers, no Telegram calls in db layer
- [ ] Specific exceptions caught and logged
- [ ] No `print()` statements
- [ ] All new public functions have docstrings in English
- [ ] Tests added or updated in `tests/`
