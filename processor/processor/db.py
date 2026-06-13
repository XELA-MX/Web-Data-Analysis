"""Acceso a Postgres para el procesador.

Lee de raw_jobs (lo no procesado), escribe en jobs (upsert idempotente) y marca
las crudas como procesadas. La conexión se toma de la variable de entorno DATABASE_URI.

Seguridad: todas las consultas son parametrizadas (nunca se concatena SQL).
"""

from __future__ import annotations

import os

import psycopg
from psycopg.rows import dict_row
from psycopg.types.json import Jsonb


def connect() -> psycopg.Connection:
    dsn = os.environ.get("DATABASE_URI")
    if not dsn:
        raise RuntimeError("Falta la variable de entorno DATABASE_URI")
    return psycopg.connect(dsn, row_factory=dict_row)


def fetch_unprocessed(conn: psycopg.Connection, limit: int) -> list[dict]:
    """Devuelve un lote de ofertas crudas sin procesar, con el nombre de su fuente."""
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT r.id, r.source_id, s.name AS source_name,
                   r.external_id, r.raw_payload, r.url, r.scraped_at
            FROM raw_jobs r
            JOIN sources s ON s.id = r.source_id
            WHERE r.processed = FALSE
            ORDER BY r.id
            LIMIT %s
            """,
            (limit,),
        )
        return cur.fetchall()


def upsert_job(conn: psycopg.Connection, job: dict) -> None:
    """Inserta/actualiza una oferta limpia. Idempotente por (source_id, external_id).

    En conflicto se actualizan los campos enriquecidos pero NO first_seen_at
    (se conserva la primera vez que vimos la oferta, para histórico/tendencias).
    """
    with conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO jobs (
                source_id, external_id, fingerprint, title, company, location,
                country, remote, salary_min, salary_max, currency, tech_stack,
                seniority, description, url, posted_at, scraped_at
            ) VALUES (
                %(source_id)s, %(external_id)s, %(fingerprint)s, %(title)s, %(company)s, %(location)s,
                %(country)s, %(remote)s, %(salary_min)s, %(salary_max)s, %(currency)s, %(tech_stack)s,
                %(seniority)s, %(description)s, %(url)s, %(posted_at)s, %(scraped_at)s
            )
            ON CONFLICT (source_id, external_id) DO UPDATE SET
                fingerprint = EXCLUDED.fingerprint,
                title       = EXCLUDED.title,
                company     = EXCLUDED.company,
                location    = EXCLUDED.location,
                country     = EXCLUDED.country,
                remote      = EXCLUDED.remote,
                salary_min  = EXCLUDED.salary_min,
                salary_max  = EXCLUDED.salary_max,
                currency    = EXCLUDED.currency,
                tech_stack  = EXCLUDED.tech_stack,
                seniority   = EXCLUDED.seniority,
                description = EXCLUDED.description,
                url         = EXCLUDED.url,
                posted_at   = EXCLUDED.posted_at,
                scraped_at  = EXCLUDED.scraped_at
            """,
            {**job, "tech_stack": Jsonb(job["tech_stack"])},
        )


def mark_processed(conn: psycopg.Connection, raw_ids: list[int]) -> None:
    if not raw_ids:
        return
    with conn.cursor() as cur:
        cur.execute(
            "UPDATE raw_jobs SET processed = TRUE WHERE id = ANY(%s)",
            (raw_ids,),
        )


def recompute_duplicates(conn: psycopg.Connection) -> int:
    """Recalcula la marca de duplicado en TODA la tabla jobs.

    Por cada `fingerprint`, la oferta más antigua (first_seen_at, id) es la canónica
    (is_duplicate = FALSE) y el resto se marcan como duplicadas. Idempotente y
    basado en conjuntos (window function). Devuelve cuántas filas cambiaron.
    """
    with conn.cursor() as cur:
        cur.execute(
            """
            WITH ranked AS (
                SELECT id,
                       row_number() OVER (
                           PARTITION BY fingerprint ORDER BY first_seen_at, id
                       ) AS rn
                FROM jobs
            )
            UPDATE jobs j
            SET is_duplicate = (r.rn > 1)
            FROM ranked r
            WHERE r.id = j.id
              AND j.is_duplicate <> (r.rn > 1)
            """
        )
        return cur.rowcount
