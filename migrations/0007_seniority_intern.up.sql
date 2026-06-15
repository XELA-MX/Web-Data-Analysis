-- 0007_seniority_intern (UP)
-- Añade el nivel 'intern' (prácticas / becario / undergraduate) a seniority,
-- en jobs y en user_preferences.

BEGIN;

ALTER TABLE jobs DROP CONSTRAINT jobs_seniority_check;
ALTER TABLE jobs ADD CONSTRAINT jobs_seniority_check
    CHECK (seniority IN ('intern', 'junior', 'mid', 'senior'));

ALTER TABLE user_preferences DROP CONSTRAINT user_preferences_seniority_check;
ALTER TABLE user_preferences ADD CONSTRAINT user_preferences_seniority_check
    CHECK (seniority IN ('intern', 'junior', 'mid', 'senior'));

COMMIT;
