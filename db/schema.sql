-- CarTags database schema
-- All text codes stored UPPERCASE.

CREATE TABLE IF NOT EXISTS countries (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    code       TEXT NOT NULL UNIQUE,  -- ISO 3166-1 alpha-2, stored UPPERCASE
    emoji      TEXT NOT NULL,
    sort_order INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS regions (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    country_id  INTEGER NOT NULL REFERENCES countries(id),
    plate_code  TEXT NOT NULL,  -- stored UPPERCASE
    wikipedia_url TEXT,
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(country_id, plate_code)
);

CREATE TABLE IF NOT EXISTS translations (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    entity_type   TEXT NOT NULL,  -- "country" or "region"
    entity_id     INTEGER NOT NULL,
    language_code TEXT NOT NULL,  -- en, de, ru, uk
    field         TEXT NOT NULL,  -- "name" or "region_group"
    value         TEXT NOT NULL,
    created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(entity_type, entity_id, language_code, field)
);

CREATE INDEX IF NOT EXISTS idx_regions_plate_code
    ON regions(plate_code);

CREATE INDEX IF NOT EXISTS idx_regions_country_id
    ON regions(country_id);

CREATE INDEX IF NOT EXISTS idx_translations_entity
    ON translations(entity_type, entity_id);

CREATE INDEX IF NOT EXISTS idx_translations_lookup
    ON translations(entity_type, entity_id, language_code, field);

CREATE TABLE IF NOT EXISTS user_settings (
    user_id  INTEGER PRIMARY KEY,
    lang     TEXT NOT NULL DEFAULT 'en'
);
