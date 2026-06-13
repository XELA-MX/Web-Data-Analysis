-- 0002_sources_unique_name (UP)
-- Permite identificar una fuente por su nombre (upsert idempotente desde el scraper).

BEGIN;

ALTER TABLE sources ADD CONSTRAINT sources_name_uniq UNIQUE (name);

COMMIT;
