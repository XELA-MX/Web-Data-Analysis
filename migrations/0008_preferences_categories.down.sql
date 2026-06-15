-- 0008_preferences_categories (DOWN)

BEGIN;

ALTER TABLE user_preferences ADD COLUMN role TEXT;
ALTER TABLE user_preferences DROP COLUMN categories;

COMMIT;
