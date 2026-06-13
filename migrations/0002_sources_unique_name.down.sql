-- 0002_sources_unique_name (DOWN)

BEGIN;

ALTER TABLE sources DROP CONSTRAINT IF EXISTS sources_name_uniq;

COMMIT;
