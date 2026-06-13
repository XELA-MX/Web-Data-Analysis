-- 0003_jobs_dedup (UP)
-- Marca de deduplicación cross-source. Una misma oferta puede aparecer en varias
-- fuentes con el mismo `fingerprint`; marcamos como duplicadas todas menos la
-- canónica (la primera vista). La API mostrará solo `is_duplicate = FALSE`.

BEGIN;

ALTER TABLE jobs ADD COLUMN is_duplicate BOOLEAN NOT NULL DEFAULT FALSE;

-- Índice parcial para servir rápido el conjunto canónico (no duplicados).
CREATE INDEX jobs_canonical_idx ON jobs (id) WHERE is_duplicate = FALSE;

COMMIT;
