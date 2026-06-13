-- 0001_initial_schema (DOWN)
-- Revierte el esquema inicial. Orden inverso por las FK.

BEGIN;

DROP TABLE IF EXISTS jobs;
DROP TABLE IF EXISTS raw_jobs;
DROP TABLE IF EXISTS sources;

COMMIT;
