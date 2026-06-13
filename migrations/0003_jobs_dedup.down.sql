-- 0003_jobs_dedup (DOWN)

BEGIN;

DROP INDEX IF EXISTS jobs_canonical_idx;
ALTER TABLE jobs DROP COLUMN IF EXISTS is_duplicate;

COMMIT;
