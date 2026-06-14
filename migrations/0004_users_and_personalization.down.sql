-- 0004_users_and_personalization (DOWN)

BEGIN;

DROP TABLE IF EXISTS sessions;
DROP TABLE IF EXISTS saved_jobs;
DROP TABLE IF EXISTS user_preferences;
DROP TABLE IF EXISTS users;

COMMIT;
