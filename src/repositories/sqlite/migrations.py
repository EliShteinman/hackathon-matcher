import logging

import aiosqlite

logger = logging.getLogger(__name__)

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS users (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    id_number       TEXT    NOT NULL UNIQUE,
    email           TEXT    NOT NULL,
    full_name       TEXT    NOT NULL,
    branch          TEXT    NOT NULL,
    class_name      TEXT,
    status          TEXT    NOT NULL DEFAULT 'available'
                            CHECK(status IN ('available', 'pending', 'matched')),
    created_at      TEXT    NOT NULL DEFAULT (datetime('now')),
    updated_at      TEXT    NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_users_status ON users(status);

CREATE TABLE IF NOT EXISTS match_requests (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    initiator_id    INTEGER NOT NULL REFERENCES users(id),
    target_id       INTEGER NOT NULL REFERENCES users(id),
    status          TEXT    NOT NULL DEFAULT 'pending'
                            CHECK(status IN ('pending', 'approved', 'rejected', 'cancelled')),
    created_at      TEXT    NOT NULL DEFAULT (datetime('now')),
    resolved_at     TEXT,
    CHECK(initiator_id != target_id)
);

CREATE INDEX IF NOT EXISTS idx_match_requests_status ON match_requests(status);
CREATE INDEX IF NOT EXISTS idx_match_requests_initiator ON match_requests(initiator_id);
CREATE INDEX IF NOT EXISTS idx_match_requests_target ON match_requests(target_id);

CREATE TABLE IF NOT EXISTS email_tokens (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    uuid                TEXT    NOT NULL UNIQUE,
    match_request_id    INTEGER NOT NULL REFERENCES match_requests(id),
    is_used             INTEGER NOT NULL DEFAULT 0,
    expires_at          TEXT    NOT NULL,
    created_at          TEXT    NOT NULL DEFAULT (datetime('now'))
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_email_tokens_uuid ON email_tokens(uuid);

CREATE TABLE IF NOT EXISTS system_settings (
    id                      INTEGER PRIMARY KEY CHECK(id = 1),
    is_globally_locked      INTEGER NOT NULL DEFAULT 0,
    deadline                TEXT,
    last_excel_upload_at    TEXT,
    updated_at              TEXT    NOT NULL DEFAULT (datetime('now'))
);
"""

SEED_SQL = "INSERT OR IGNORE INTO system_settings (id) VALUES (1);"


async def run_migrations(db: aiosqlite.Connection) -> None:
    await db.executescript(SCHEMA_SQL)
    await db.execute(SEED_SQL)
    await db.commit()
    logger.info("Database migrations completed")
