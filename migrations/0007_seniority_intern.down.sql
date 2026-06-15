-- 0007_seniority_intern (DOWN)
-- Revierte a los 3 niveles. Antes hay que reclasificar/limpiar los 'intern' existentes
-- (si no, el ADD CONSTRAINT fallaría).

BEGIN;

UPDATE jobs SET seniority = 'junior' WHERE seniority = 'intern';
UPDATE user_preferences SET seniority = 'junior' WHERE seniority = 'intern';

ALTER TABLE jobs DROP CONSTRAINT jobs_seniority_check;
ALTER TABLE jobs ADD CONSTRAINT jobs_seniority_check
    CHECK (seniority IN ('junior', 'mid', 'senior'));

ALTER TABLE user_preferences DROP CONSTRAINT user_preferences_seniority_check;
ALTER TABLE user_preferences ADD CONSTRAINT user_preferences_seniority_check
    CHECK (seniority IN ('junior', 'mid', 'senior'));

COMMIT;
