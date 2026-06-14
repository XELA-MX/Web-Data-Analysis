-- 0004_users_and_personalization (UP)
-- Cuentas de usuario y personalización (Fase 4.5). Las ofertas (`jobs`) siguen siendo
-- globales; lo de aquí es POR usuario y se aísla por user_id.
-- Ver documentación/V1/04-modelo-de-datos.md y 08-cuentas-y-personalizacion.md.

BEGIN;

CREATE TABLE users (
    id            SERIAL PRIMARY KEY,
    email         TEXT        NOT NULL UNIQUE,
    provider      TEXT        NOT NULL DEFAULT 'email' CHECK (provider IN ('email', 'github')),
    provider_id   TEXT,
    password_hash TEXT,                       -- solo si provider = 'email' (argon2id)
    display_name  TEXT,
    created_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
    last_login_at TIMESTAMPTZ
);

CREATE TABLE user_preferences (
    user_id       INT         PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
    role          TEXT,
    tech_stack    JSONB       NOT NULL DEFAULT '[]'::jsonb,
    seniority     TEXT        CHECK (seniority IN ('junior', 'mid', 'senior')),
    work_mode     TEXT        CHECK (work_mode IN ('remote', 'hybrid', 'onsite')),
    country       TEXT,
    salary_target INT,
    updated_at    TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE saved_jobs (
    id         SERIAL PRIMARY KEY,
    user_id    INT         NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    job_id     INT         NOT NULL REFERENCES jobs(id) ON DELETE CASCADE,
    status     TEXT        NOT NULL DEFAULT 'saved' CHECK (status IN ('saved', 'dismissed', 'applied')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (user_id, job_id)
);
CREATE INDEX saved_jobs_user_status_idx ON saved_jobs (user_id, status);

-- Sesiones server-side. `id` = SHA-256 hex del token de sesión (el token en claro
-- vive solo en la cookie httpOnly del cliente; la DB nunca lo guarda en claro).
CREATE TABLE sessions (
    id         TEXT        PRIMARY KEY,
    user_id    INT         NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    expires_at TIMESTAMPTZ NOT NULL
);
CREATE INDEX sessions_user_idx ON sessions (user_id);

COMMIT;
