# CarTags — Telegram Bot Specification

**Version:** 1.0
**Platform:** Telegram
**Language:** Python 3.14
**Library:** python-telegram-bot 20.x  
**Database:** SQLite  
**Deploy:** Synology NAS (Docker)

---

## 1. Обзор

CarTags — бот-справочник номерных знаков. Пользователь вводит код региона с номерного знака и получает название города/региона и страны. Бот полностью бесплатный, без ограничений.

**Целевая аудитория:** путешественники, автолюбители, люди живущие в Европе и интересующиеся откуда приехала та или иная машина.

**Приоритетные страны:** Европа (DE, AT, PL, CZ, HU, SK, CH, IT, FR и др.) + СНГ (UA, RU, KZ, BY, GE и др.)

---

## 2. Команды бота

| Команда | Описание |
|---|---|
| `/start` | Приветствие + краткая инструкция |
| `/help` | Справка по использованию |
| `/country <код>` | Поиск по коду страны (список регионов) |
| `/plate <код_страны> <код_региона>` | Найти регион по коду номера |
| `/list` | Список поддерживаемых стран |
| `/about` | О приложении, ссылка на iOS |

---

## 3. Пользовательские сценарии

### 3.1 Быстрый поиск (основной)

Пользователь просто пишет код без команды — бот пытается его распознать.

```
Пользователь: M
Бот: Нашел несколько совпадений:
     🇩🇪 DE — Мюнхен (München), Бавария
     🇦🇹 AT — Mistelbach, Нижняя Австрия
     Уточни страну: /plate DE M или /plate AT M
```

```
Пользователь: DE M
Бот: 🇩🇪 Германия
     M — Мюнхен (München)
     Регион: Бавария (Bayern)
```

### 3.2 Поиск через команду

```
Пользователь: /plate DE B
Бот: 🇩🇪 Германия
     B — Берлин (Berlin)
     Регион: Берлин
```

```
Пользователь: /plate AT W
Бот: 🇦🇹 Австрия
     W — Вена (Wien)
     Регион: Вена
```

### 3.3 Просмотр всех регионов страны

```
Пользователь: /country DE
Бот: 🇩🇪 Германия — коды регионов:
     A — Augsburg (Бавария)
     B — Berlin
     BA — Bamberg (Бавария)
     ... [показывает первые 20, далее кнопки пагинации]
```

### 3.4 Неизвестный код

```
Пользователь: DE XYZ
Бот: Код XYZ не найден для Германии.
     Возможно, это новый или редкий код.
     Посмотри все коды Германии: /country DE
```

### 3.5 Команда /start

```
Бот: Привет! Я CarTags — справочник автомобильных номеров.

     Просто напиши код с номерного знака:
     • DE M → Мюнхен, Германия
     • AT W → Вена, Австрия
     • UA AA → Киев, Украина

     /list — все поддерживаемые страны
     /help — подробная справка
```

---

## 4. Структура базы данных

```sql
-- Страны
CREATE TABLE countries (
    id      INTEGER PRIMARY KEY AUTOINCREMENT,
    code    TEXT NOT NULL UNIQUE,   -- ISO: DE, AT, UA
    name_en TEXT NOT NULL,          -- Germany
    name_de TEXT,                   -- Deutschland
    name_uk TEXT,                   -- Німеччина
    name_ru TEXT NOT NULL,          -- Германия
    emoji   TEXT NOT NULL           -- 🇩🇪
);

-- Регионы
CREATE TABLE regions (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    country_id  INTEGER NOT NULL REFERENCES countries(id),
    plate_code  TEXT NOT NULL,      -- M, B, WU и т.д.
    name_local  TEXT NOT NULL,      -- München
    name_ru     TEXT,               -- Мюнхен (опционально)
    name_uk     TEXT,               -- Мюнхен (опционально)
    region_name TEXT,               -- Bayern
    UNIQUE(country_id, plate_code)
);

-- Переводы UI-строк
CREATE TABLE i18n (
    key     TEXT NOT NULL,          -- message key, e.g. "not_found"
    lang    TEXT NOT NULL,          -- en, de, uk, ru
    value   TEXT NOT NULL,          -- translated string
    PRIMARY KEY (key, lang)
);

CREATE INDEX idx_regions_plate_code ON regions(plate_code);
CREATE INDEX idx_regions_country_id ON regions(country_id);
```

---

## 5. Архитектура кода

```
cartags-bot/
├── bot.py               # Точка входа, запуск
├── handlers/
│   ├── start.py         # /start, /help, /about
│   ├── search.py        # /plate, свободный ввод
│   └── country.py       # /country, /list
├── db/
│   ├── database.py      # Подключение, базовые запросы
│   └── cartags.db       # SQLite файл
├── data/
│   ├── seed_de.py       # Данные Германии
│   ├── seed_at.py       # Данные Австрии
│   └── seed_ua.py       # Данные Украины
├── i18n/
│   ├── en.py            # English strings
│   ├── de.py            # German strings
│   ├── uk.py            # Ukrainian strings
│   └── ru.py            # Russian strings
├── utils/
│   ├── formatter.py     # Форматирование ответов
│   └── locale.py        # Определение языка пользователя, получение строк
├── .env                 # BOT_TOKEN (не в git)
├── .env.example         # Шаблон для .env
├── requirements.txt
├── Dockerfile
└── docker-compose.yml
```

---

## 6. Технические требования

### 6.1 Зависимости (requirements.txt)

```
python-telegram-bot==20.7
python-dotenv==1.0.0
```

### 6.2 Переменные окружения (.env)

```
BOT_TOKEN=7123456789:AAFxxxxxxxxxxxxxxxxxxxxxxx
LOG_LEVEL=INFO
DEFAULT_LANG=en
```

### 6.3 Поведение поиска

- Поиск регистронезависимый (`m` = `M`)
- При вводе без команды — пытаемся определить формат: `DE M`, `M`, `/plate DE M`
- Если код найден в одной стране — сразу отвечаем
- Если в нескольких — просим уточнить через inline-кнопки
- Частичный поиск: `MU` найдёт `MÜ` если включить LIKE-поиск (фаза 2)

### 6.4 Пагинация

Если у страны более 20 регионов (Германия — 400+), используем inline-кнопки:

```
[← Назад] [1/21] [Вперёд →]
```

---

## 7. Мультиязычность

Бот поддерживает 4 языка: **English (en)**, **Deutsch (de)**, **Українська (uk)**, **Русский (ru)**.

### 7.1 Определение языка

Язык определяется автоматически по `update.effective_user.language_code` из Telegram. Если язык не поддерживается — используется English как fallback.

```
Telegram language_code → наш язык
de, de-*               → de
uk                     → uk
ru, be, kk, ...        → ru
всё остальное          → en (fallback)
```

### 7.2 Структура i18n

Все UI-строки вынесены в `i18n/<lang>.py` в виде словаря. Функция `t(key, lang, **kwargs)` в `utils/locale.py` возвращает нужную строку с подстановкой параметров.

```python
# i18n/en.py
STRINGS: dict[str, str] = {
    "start_greeting": "Hi! I'm CarTags — a license plate directory.\n\nJust type a plate code:\n• DE M → Munich, Germany\n• AT W → Vienna, Austria",
    "not_found": "Code {plate} not found for {country}.\nSee all codes: /country {country}",
    "ambiguous": "Found in multiple countries:",
    "help_text": "Send a plate code to look it up:\n• Single code: M\n• With country: DE M\n• All regions: /country DE",
    "list_header": "Supported countries:",
    "country_header": "{emoji} {country} — plate codes:",
    "page_info": "Page {page}/{total}",
}
```

```python
# utils/locale.py
SUPPORTED_LANGS = ("en", "de", "uk", "ru")
FALLBACK_LANG = "en"

def get_lang(language_code: str | None) -> str:
    """Resolve Telegram language_code to a supported lang key."""
    ...

def t(key: str, lang: str, **kwargs: str) -> str:
    """Return translated string for key in lang, with optional format args."""
    ...
```

### 7.3 Команда /language

Пользователь может явно сменить язык командой `/language`:

```
/language → бот отвечает inline-кнопками: 🇬🇧 English | 🇩🇪 Deutsch | 🇺🇦 Українська | 🇷🇺 Русский
```

Выбранный язык сохраняется в таблице `user_settings` в SQLite и имеет приоритет над автоопределением.

```sql
CREATE TABLE user_settings (
    user_id  INTEGER PRIMARY KEY,
    lang     TEXT NOT NULL DEFAULT 'en'
);
```

### 7.4 Данные регионов

Названия регионов отображаются в зависимости от языка:

| Поле в `regions` | Используется для |
|---|---|
| `name_local` | Всегда отображается (оригинальное название) |
| `name_ru` | Дополнительно для `ru` и `uk` |
| `name_uk` | Дополнительно для `uk` |

Названия стран берутся из соответствующего поля в `countries` (`name_en`, `name_de`, `name_uk`, `name_ru`).

---

## 8. Деплой на Synology NAS

### Dockerfile

```dockerfile
FROM python:3.14-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["python", "bot.py"]
```

### docker-compose.yml

```yaml
version: "3.8"
services:
  cartags-bot:
    build: .
    restart: unless-stopped
    env_file: .env
    volumes:
      - ./db:/app/db
```

### Запуск

```bash
docker-compose up -d
docker-compose logs -f  # смотреть логи
```

---

## 9. Первоначальные данные (MVP)

Минимальный набор стран для запуска:

| Страна | Кол-во кодов | Приоритет |
|---|---|---|
| Германия (DE) | ~430 | P1 — самая популярная в Европе |
| Австрия (AT) | ~120 | P1 — ты живёшь в Вене |
| Украина (UA) | ~30 | P1 — СНГ аудитория |
| Польша (PL) | ~380 | P2 |
| Чехия (CZ) | ~80 | P2 |
| Швейцария (CH) | ~50 | P2 |
| Венгрия (HU) | ~25 | P2 |

---

## 10. Фазы разработки

### Фаза 1 — MVP (1–2 недели)
- [ ] Создать SQLite-схему (включая `i18n`, `user_settings`)
- [ ] Заполнить данные DE, AT, UA
- [ ] Команды `/start`, `/plate`, `/country`, `/list`
- [ ] Свободный ввод (без команды)
- [ ] Мультиязычность: EN, DE, UK, RU — автоопределение + `/language`
- [ ] Деплой на NAS

### Фаза 2 — Расширение (2–4 недели)
- [ ] Добавить PL, CZ, CH, HU, SK
- [ ] Пагинация для длинных списков
- [ ] Inline-кнопки для выбора страны при неоднозначности
- [ ] Поддержка RU, KZ, BY, GE

### Фаза 3 — Полировка
- [ ] Статистика использования (простой счётчик в SQLite)
- [ ] Команда `/feedback` — отправка сообщения разработчику

---

## 11. Примеры кода

### bot.py

```python
import logging
import os
from dotenv import load_dotenv
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters

from handlers.start import start_handler, help_handler, about_handler
from handlers.search import search_handler, plate_handler
from handlers.country import country_handler, list_handler

load_dotenv()
logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))

def main():
    app = ApplicationBuilder().token(os.getenv("BOT_TOKEN")).build()

    app.add_handler(CommandHandler("start", start_handler))
    app.add_handler(CommandHandler("help", help_handler))
    app.add_handler(CommandHandler("about", about_handler))
    app.add_handler(CommandHandler("plate", plate_handler))
    app.add_handler(CommandHandler("country", country_handler))
    app.add_handler(CommandHandler("list", list_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, search_handler))

    app.run_polling()

if __name__ == "__main__":
    main()
```

### db/database.py

```python
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "cartags.db"

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def find_by_code(country_code: str, plate_code: str):
    with get_connection() as conn:
        return conn.execute("""
            SELECT r.plate_code, r.name_local, r.name_ru, r.region_name,
                   c.name_ru as country_ru, c.emoji
            FROM regions r
            JOIN countries c ON c.id = r.country_id
            WHERE UPPER(c.code) = UPPER(?)
              AND UPPER(r.plate_code) = UPPER(?)
        """, (country_code, plate_code)).fetchone()

def find_by_plate_only(plate_code: str):
    with get_connection() as conn:
        return conn.execute("""
            SELECT r.plate_code, r.name_local, r.name_ru, r.region_name,
                   c.code as country_code, c.name_ru as country_ru, c.emoji
            FROM regions r
            JOIN countries c ON c.id = r.country_id
            WHERE UPPER(r.plate_code) = UPPER(?)
        """, (plate_code,)).fetchall()

def get_country_regions(country_code: str, offset: int = 0, limit: int = 20):
    with get_connection() as conn:
        return conn.execute("""
            SELECT r.plate_code, r.name_local, r.region_name
            FROM regions r
            JOIN countries c ON c.id = r.country_id
            WHERE UPPER(c.code) = UPPER(?)
            ORDER BY r.plate_code
            LIMIT ? OFFSET ?
        """, (country_code, limit, offset)).fetchall()
```

---

*Документ обновляется по мере разработки.*
