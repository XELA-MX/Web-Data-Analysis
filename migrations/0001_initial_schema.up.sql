-- 0001_initial_schema (UP)
-- Esquema inicial V1 (MVP): núcleo del pipeline de datos.
-- Las tablas de usuarios/personalización (users, user_preferences, saved_jobs,
-- alerts) llegan en una migration posterior, en la Fase 4.5.
-- Referencia: documentación/V1/04-modelo-de-datos.md

BEGIN;

-- Catálogo de fuentes de datos.
CREATE TABLE sources (
    id                 SERIAL PRIMARY KEY,
    name               TEXT        NOT NULL,
    base_url           TEXT        NOT NULL,
    enabled            BOOLEAN     NOT NULL DEFAULT TRUE,
    rate_limit_per_min INT         NOT NULL DEFAULT 60,
    created_at         TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Datos crudos tal cual llegan del scraper (permite reprocesar sin re-scrapear).
CREATE TABLE raw_jobs (
    id          SERIAL PRIMARY KEY,
    source_id   INT         NOT NULL REFERENCES sources(id) ON DELETE CASCADE,
    external_id TEXT        NOT NULL,
    raw_payload JSONB       NOT NULL,
    url         TEXT,
    scraped_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
    processed   BOOLEAN     NOT NULL DEFAULT FALSE
);

-- Idempotencia: una oferta de una fuente solo una vez.
CREATE UNIQUE INDEX raw_jobs_source_external_uniq ON raw_jobs (source_id, external_id);
-- Índice parcial: "cola de trabajo" del procesador (solo lo no procesado).
CREATE INDEX raw_jobs_unprocessed_idx ON raw_jobs (id) WHERE processed = FALSE;

-- Ofertas limpias y enriquecidas. Es la que consume la API.
CREATE TABLE jobs (
    id            SERIAL PRIMARY KEY,
    source_id     INT         NOT NULL REFERENCES sources(id) ON DELETE CASCADE,
    external_id   TEXT        NOT NULL,
    fingerprint   TEXT        NOT NULL,
    title         TEXT        NOT NULL,
    company       TEXT,
    location      TEXT,
    country       TEXT,
    remote        BOOLEAN     NOT NULL DEFAULT FALSE,
    salary_min    INT,
    salary_max    INT,
    currency      TEXT,
    tech_stack    JSONB       NOT NULL DEFAULT '[]'::jsonb,
    seniority     TEXT        CHECK (seniority IN ('junior', 'mid', 'senior')),
    description   TEXT,
    url           TEXT,
    posted_at     TIMESTAMPTZ,
    scraped_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
    first_seen_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE UNIQUE INDEX jobs_source_external_uniq ON jobs (source_id, external_id);
CREATE INDEX jobs_fingerprint_idx   ON jobs (fingerprint);
CREATE INDEX jobs_remote_idx        ON jobs (remote);
CREATE INDEX jobs_seniority_idx     ON jobs (seniority);
CREATE INDEX jobs_country_idx       ON jobs (country);
CREATE INDEX jobs_tech_stack_gin    ON jobs USING GIN (tech_stack);
CREATE INDEX jobs_posted_at_idx     ON jobs (posted_at);
CREATE INDEX jobs_first_seen_at_idx ON jobs (first_seen_at);

COMMIT;
