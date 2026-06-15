-- 0008_preferences_categories (UP)
-- Permite múltiples áreas de interés por usuario: sustituye `role` (único) por
-- `categories` (lista). El feed prioriza ofertas de cualquiera de esas categorías.

BEGIN;

ALTER TABLE user_preferences ADD COLUMN categories JSONB NOT NULL DEFAULT '[]'::jsonb;
ALTER TABLE user_preferences DROP COLUMN role;

COMMIT;
