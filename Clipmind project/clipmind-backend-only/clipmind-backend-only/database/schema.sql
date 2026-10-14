-- schema.sql
-- Reference schema (PostgreSQL syntax). SQLAlchemy models (backend/app/models.py)
-- generate this automatically for SQLite/PostgreSQL, but this file is here
-- for documentation / team discussion as required by the project doc.

CREATE TABLE users (
    id UUID PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,          -- bcrypt hashed, never plain text
    role VARCHAR(30) NOT NULL,               -- content_creator | learner | educator | administrator
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE videos (
    id UUID PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    filename VARCHAR(255) NOT NULL,
    file_path VARCHAR(500) NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'uploaded',  -- uploaded | processing | completed | failed
    duration_seconds INTEGER,
    uploaded_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_videos_user_id ON videos(user_id);
