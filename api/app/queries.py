"""Consultas SQL. Todas parametrizadas; los filtros dinámicos se construyen
añadiendo condiciones con placeholders, nunca interpolando valores.

Se sirve siempre el conjunto canónico: `NOT is_duplicate`.
"""

from __future__ import annotations

import psycopg
from psycopg.types.json import Jsonb

# Proyección común de una fila de `jobs` + nombre de la fuente.
_JOB_COLS = """
    j.id, s.name AS source, j.title, j.company, j.location, j.country,
    j.remote, j.salary_min, j.salary_max, j.currency, j.tech_stack,
    j.seniority, j.url, j.posted_at
"""


def search_jobs(
    conn: psycopg.Connection,
    *,
    q: str | None,
    tech: list[str] | None,
    seniority: str | None,
    remote: bool | None,
    source: str | None,
    salary_min: int | None,
    limit: int,
    offset: int,
) -> tuple[int, list[dict]]:
    """Búsqueda/filtrado de ofertas. Devuelve (total, página de items)."""
    where = ["NOT j.is_duplicate"]
    params: dict = {}

    if q:
        where.append("(j.title ILIKE %(q)s OR j.company ILIKE %(q)s)")
        params["q"] = f"%{q}%"
    if tech:
        # tech_stack contiene TODAS las tecnologías pedidas (operador @>).
        where.append("j.tech_stack @> %(tech)s")
        params["tech"] = Jsonb([t.lower() for t in tech])
    if seniority:
        where.append("j.seniority = %(seniority)s")
        params["seniority"] = seniority
    if remote is not None:
        where.append("j.remote = %(remote)s")
        params["remote"] = remote
    if source:
        where.append("s.name = %(source)s")
        params["source"] = source
    if salary_min is not None:
        where.append("j.salary_max >= %(salary_min)s")
        params["salary_min"] = salary_min

    where_sql = " AND ".join(where)

    with conn.cursor() as cur:
        cur.execute(
            f"SELECT count(*) AS total FROM jobs j JOIN sources s ON s.id = j.source_id WHERE {where_sql}",
            params,
        )
        total = cur.fetchone()["total"]

        cur.execute(
            f"""
            SELECT {_JOB_COLS}
            FROM jobs j JOIN sources s ON s.id = j.source_id
            WHERE {where_sql}
            ORDER BY j.posted_at DESC NULLS LAST, j.id DESC
            LIMIT %(limit)s OFFSET %(offset)s
            """,
            {**params, "limit": limit, "offset": offset},
        )
        items = cur.fetchall()

    return total, items


def overview(conn: psycopg.Connection) -> dict:
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT
                count(*) FILTER (WHERE NOT is_duplicate) AS total_jobs,
                count(*) FILTER (WHERE NOT is_duplicate AND remote) AS remote_jobs,
                count(*) FILTER (WHERE NOT is_duplicate
                    AND (salary_min IS NOT NULL OR salary_max IS NOT NULL)) AS with_salary,
                count(*) FILTER (WHERE NOT is_duplicate AND tech_stack <> '[]'::jsonb) AS with_tech,
                max(scraped_at) AS last_scraped
            FROM jobs
            """
        )
        row = cur.fetchone()
        cur.execute("SELECT count(*) AS n FROM sources")
        row["sources"] = cur.fetchone()["n"]
    total = row["total_jobs"] or 0
    row["remote_pct"] = round(100 * (row["remote_jobs"] or 0) / total, 1) if total else 0.0
    return row


def top_tech(conn: psycopg.Connection, limit: int) -> list[dict]:
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT tech, count(*) AS count
            FROM jobs, jsonb_array_elements_text(tech_stack) AS tech
            WHERE NOT is_duplicate
            GROUP BY tech
            ORDER BY count DESC, tech
            LIMIT %(limit)s
            """,
            {"limit": limit},
        )
        return cur.fetchall()


def salary_by(conn: psycopg.Connection, by: str, limit: int) -> list[dict]:
    """Rangos salariales medios agrupados por 'seniority' o por 'tech'."""
    if by == "tech":
        sql = """
            SELECT tech AS "group", count(*) AS jobs,
                   round(avg(salary_min))::int AS avg_min,
                   round(avg(salary_max))::int AS avg_max
            FROM jobs, jsonb_array_elements_text(tech_stack) AS tech
            WHERE NOT is_duplicate AND (salary_min IS NOT NULL OR salary_max IS NOT NULL)
            GROUP BY tech
            ORDER BY jobs DESC, tech
            LIMIT %(limit)s
        """
    else:  # seniority
        sql = """
            SELECT coalesce(seniority, 'desconocido') AS "group", count(*) AS jobs,
                   round(avg(salary_min))::int AS avg_min,
                   round(avg(salary_max))::int AS avg_max
            FROM jobs
            WHERE NOT is_duplicate AND (salary_min IS NOT NULL OR salary_max IS NOT NULL)
            GROUP BY coalesce(seniority, 'desconocido')
            ORDER BY jobs DESC
            LIMIT %(limit)s
        """
    with conn.cursor() as cur:
        cur.execute(sql, {"limit": limit})
        return cur.fetchall()


def trends(conn: psycopg.Connection, days: int) -> list[dict]:
    """Series temporales: ofertas vistas por día (demanda en el tiempo)."""
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT to_char(date_trunc('day', first_seen_at), 'YYYY-MM-DD') AS day,
                   count(*) AS jobs
            FROM jobs
            WHERE NOT is_duplicate
              AND first_seen_at >= now() - make_interval(days => %(days)s)
            GROUP BY day
            ORDER BY day
            """,
            {"days": days},
        )
        return cur.fetchall()


def sources_with_counts(conn: psycopg.Connection) -> list[dict]:
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT s.name AS source,
                   count(j.id) FILTER (WHERE NOT j.is_duplicate) AS jobs
            FROM sources s
            LEFT JOIN jobs j ON j.source_id = s.id
            GROUP BY s.name
            ORDER BY jobs DESC, s.name
            """
        )
        return cur.fetchall()
