-- 0009_tech_daily_stats (UP)
-- Histórico diario de demanda por tecnología, para tendencias en el tiempo
-- ("React +12% este mes"). Lo rellena el procesador en cada pasada (idempotente
-- por día). Ver documentación/V1/04-modelo-de-datos.md (opción B).

BEGIN;

CREATE TABLE tech_daily_stats (
    snapshot_date  DATE NOT NULL,
    tech           TEXT NOT NULL,
    job_count      INT  NOT NULL,
    avg_salary_min INT,
    avg_salary_max INT,
    PRIMARY KEY (snapshot_date, tech)
);

CREATE INDEX tech_daily_stats_tech_idx ON tech_daily_stats (tech, snapshot_date);

COMMIT;
