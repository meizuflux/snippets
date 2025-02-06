CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    email TEXT UNIQUE,
    password TEXT, -- hashed with argon2
    session_duration BIGINT NOT NULL DEFAULT 86400,
    joined TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT (NOW() AT TIME ZONE 'UTC')
);

CREATE TABLE IF NOT EXISTS sessions (
    token UUID NOT NULL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users (id) ON DELETE CASCADE,
    created TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT (NOW() AT TIME ZONE 'UTC'),
    expires TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT ((NOW() AT TIME ZONE 'UTC') + interval '1 day'),
    ip INET,
    browser TEXT DEFAULT 'Unknown',
    os TEXT DEFAULT 'Unknown'
);

CREATE TABLE IF NOT EXISTS api_keys (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users (id) ON DELETE CASCADE,
    created TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT (NOW() AT TIME ZONE 'UTC'),
    key TEXT NOT NULL, -- hashed so as not to be stored
    title TEXT NOT NULL
);

CREATE OR REPLACE FUNCTION delete_old_sessions() RETURNS TRIGGER AS $$
BEGIN
    DELETE FROM sessions WHERE expires < NOW() AT TIME ZONE 'UTC';
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS old_sessions_expiry ON public.sessions;
CREATE TRIGGER old_sessions_expiry
    AFTER INSERT OR UPDATE
    ON sessions
    FOR STATEMENT
    EXECUTE PROCEDURE delete_old_sessions();