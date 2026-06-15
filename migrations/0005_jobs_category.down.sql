-- 0005_jobs_category (DOWN)

BEGIN;

DROP INDEX IF EXISTS jobs_category_idx;
ALTER TABLE jobs DROP COLUMN IF EXISTS category;

COMMIT;
