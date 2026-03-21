-- LooksAI Database Schema
-- Run this against a fresh PostgreSQL 16 database.

CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- ── Users ─────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS users (
    id               SERIAL PRIMARY KEY,
    email            VARCHAR(255) UNIQUE NOT NULL,
    username         VARCHAR(100) UNIQUE NOT NULL,
    hashed_password  VARCHAR(255) NOT NULL,
    is_active        BOOLEAN DEFAULT TRUE,
    is_verified      BOOLEAN DEFAULT FALSE,
    created_at       TIMESTAMPTZ DEFAULT NOW(),
    updated_at       TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_users_email    ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);

-- ── Analysis Sessions ─────────────────────────────────────────────────────────
CREATE TYPE analysis_status AS ENUM ('pending', 'processing', 'completed', 'failed');

CREATE TABLE IF NOT EXISTS analysis_sessions (
    id               SERIAL PRIMARY KEY,
    user_id          INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    status           analysis_status DEFAULT 'pending',
    image_front      VARCHAR(500),
    image_left       VARCHAR(500),
    image_right      VARCHAR(500),
    face_shape       VARCHAR(50),
    skin_analysis    JSONB,
    facial_features  JSONB,
    landmarks_data   JSONB,
    error_message    TEXT,
    created_at       TIMESTAMPTZ DEFAULT NOW(),
    completed_at     TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_sessions_user_id    ON analysis_sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_sessions_status     ON analysis_sessions(status);
CREATE INDEX IF NOT EXISTS idx_sessions_created_at ON analysis_sessions(created_at DESC);

-- ── Recommendations ───────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS recommendations (
    id                      SERIAL PRIMARY KEY,
    session_id              INTEGER NOT NULL REFERENCES analysis_sessions(id) ON DELETE CASCADE,
    maintenance_preference  VARCHAR(10),
    length_preference       VARCHAR(10),
    filtered_haircuts       JSONB,
    narrative               TEXT,
    haircut_table_md        TEXT,
    skincare_tips           TEXT,
    lifestyle_tips          TEXT,
    created_at              TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_recs_session_id ON recommendations(session_id);

-- ── Chat Messages ─────────────────────────────────────────────────────────────
CREATE TYPE message_role AS ENUM ('user', 'assistant', 'system');

CREATE TABLE IF NOT EXISTS chat_messages (
    id          SERIAL PRIMARY KEY,
    session_id  INTEGER NOT NULL REFERENCES analysis_sessions(id) ON DELETE CASCADE,
    role        message_role NOT NULL,
    content     TEXT NOT NULL,
    meta        JSONB,
    created_at  TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_chat_session_id  ON chat_messages(session_id);
CREATE INDEX IF NOT EXISTS idx_chat_created_at  ON chat_messages(created_at ASC);

-- ── Auto-update updated_at on users ──────────────────────────────────────────
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_users_updated_at ON users;
CREATE TRIGGER trg_users_updated_at
    BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();
