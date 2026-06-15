-- 0006_users_is_admin (DOWN)

BEGIN;

ALTER TABLE users DROP COLUMN IF EXISTS is_admin;

COMMIT;
