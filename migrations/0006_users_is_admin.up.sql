-- 0006_users_is_admin (UP)
-- Rol de administrador. Marcar qué usuarios son admin es dato específico del entorno
-- (no va en la migration): se hace con un UPDATE manual sobre el email correspondiente.

BEGIN;

ALTER TABLE users ADD COLUMN is_admin BOOLEAN NOT NULL DEFAULT FALSE;

COMMIT;
