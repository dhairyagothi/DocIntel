CREATE TABLE IF NOT EXISTS documents (
    id TEXT PRIMARY KEY,
    filename TEXT NOT NULL,
    file_hash TEXT UNIQUE NOT NULL,
    page_count INTEGER,
    created_at TEXT
);

CREATE TABLE IF NOT EXISTS chunks (
    id TEXT PRIMARY KEY,
    document_id TEXT NOT NULL,
    page_start INTEGER,
    page_end INTEGER,
    text TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS facts (
    id TEXT PRIMARY KEY,
    subject TEXT,
    predicate TEXT,
    value TEXT,
    normalized_value TEXT,
    unit TEXT,
    currency TEXT,
    time_period TEXT,
    scope TEXT,
    confidence REAL,
    document_id TEXT,
    page INTEGER,
    chunk_id TEXT,
    evidence TEXT
);

CREATE TABLE IF NOT EXISTS relationships (
    id TEXT PRIMARY KEY,
    fact_a TEXT,
    fact_b TEXT,
    classification TEXT,
    confidence REAL,
    reason_codes TEXT,
    reasoning TEXT
);