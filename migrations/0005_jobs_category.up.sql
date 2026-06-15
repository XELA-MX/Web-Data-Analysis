-- 0005_jobs_category (UP)
-- Categoría derivada de la oferta (frontend, backend, fullstack, mobile, data,
-- devops, qa, other...) para que el usuario filtre con comodidad. La calcula el
-- procesador a partir del tech_stack + título; se aplica a TODAS las fuentes por igual.

BEGIN;

ALTER TABLE jobs ADD COLUMN category TEXT;
CREATE INDEX jobs_category_idx ON jobs (category);

COMMIT;
