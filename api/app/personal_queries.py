"""Consultas de datos personales: preferencias, ofertas guardadas y feed personalizado.

🔒 Aislamiento por usuario: TODAS filtran por el `user_id` que llega de la sesión
(la capa de router lo toma de get_current_user, nunca del cliente) → evita IDOR.
Todas parametrizadas.
"""

from __future__ import annotations

import psycopg
from psycopg.errors import ForeignKeyViolation
from psycopg.types.json import Jsonb

_PREF_COLS = "role, tech_stack, seniority, work_mode, country, salary_target, updated_at"

# Proyección de una oferta + nombre de fuente (igual que en queries.py).
_JOB_COLS = """
    j.id, s.name AS source, j.title, j.company, j.location, j.country, j.remote,
    j.salary_min, j.salary_max, j.currency, j.tech_stack, j.seniority, j.url, j.posted_at
"""


# ───────────────────────────── preferencias ─────────────────────────────


def get_preferences(conn: psycopg.Connection, user_id: int) -> dict | None:
    with conn.cursor() as cur:
        cur.execute(f"SELECT {_PREF_COLS} FROM user_preferences WHERE user_id = %s", (user_id,))
        return cur.fetchone()


def upsert_preferences(conn: psycopg.Connection, user_id: int, p: dict) -> dict:
    with conn.cursor() as cur:
        cur.execute(
            f"""
            INSERT INTO user_preferences
                (user_id, role, tech_stack, seniority, work_mode, country, salary_target, updated_at)
            VALUES
                (%(uid)s, %(role)s, %(tech)s, %(seniority)s, %(work_mode)s, %(country)s, %(salary_target)s, now())
            ON CONFLICT (user_id) DO UPDATE SET
                role = EXCLUDED.role,
                tech_stack = EXCLUDED.tech_stack,
                seniority = EXCLUDED.seniority,
                work_mode = EXCLUDED.work_mode,
                country = EXCLUDED.country,
                salary_target = EXCLUDED.salary_target,
                updated_at = now()
            RETURNING {_PREF_COLS}
            """,
            {
                "uid": user_id,
                "role": p["role"],
                "tech": Jsonb(p["tech_stack"]),
                "seniority": p["seniority"],
                "work_mode": p["work_mode"],
                "country": p["country"],
                "salary_target": p["salary_target"],
            },
        )
        row = cur.fetchone()
    conn.commit()
    return row


# ───────────────────────────── ofertas guardadas ─────────────────────────────


def save_job(conn: psycopg.Connection, user_id: int, job_id: int, status: str) -> dict | None:
    """Guarda/descarta/marca-aplicada una oferta. None si el job_id no existe."""
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO saved_jobs (user_id, job_id, status)
                VALUES (%s, %s, %s)
                ON CONFLICT (user_id, job_id) DO UPDATE SET status = EXCLUDED.status
                RETURNING id, job_id, status, created_at
                """,
                (user_id, job_id, status),
            )
            row = cur.fetchone()
        conn.commit()
        return row
    except ForeignKeyViolation:
        conn.rollback()
        return None


def list_saved(conn: psycopg.Connection, user_id: int, status: str | None) -> list[dict]:
    where = ["sj.user_id = %(uid)s"]
    params: dict = {"uid": user_id}
    if status:
        where.append("sj.status = %(status)s")
        params["status"] = status
    with conn.cursor() as cur:
        cur.execute(
            f"""
            SELECT {_JOB_COLS}, sj.status AS saved_status, sj.created_at AS saved_at
            FROM saved_jobs sj
            JOIN jobs j ON j.id = sj.job_id
            JOIN sources s ON s.id = j.source_id
            WHERE {" AND ".join(where)}
            ORDER BY sj.created_at DESC
            """,
            params,
        )
        return cur.fetchall()


def delete_saved(conn: psycopg.Connection, user_id: int, job_id: int) -> bool:
    """Borra solo si el registro es del usuario (aislamiento). True si borró algo."""
    with conn.cursor() as cur:
        cur.execute("DELETE FROM saved_jobs WHERE user_id = %s AND job_id = %s", (user_id, job_id))
        deleted = cur.rowcount
    conn.commit()
    return deleted > 0


# ───────────────────────────── feed personalizado ─────────────────────────────


def personalized_feed(
    conn: psycopg.Connection, user_id: int, prefs: dict | None, limit: int, offset: int
) -> list[dict]:
    """Feed canónico ordenado por afinidad con el perfil.

    Score = nº de tecnologías del usuario presentes en la oferta
            + 2 si coincide el seniority
            + 1 si el usuario quiere remoto y la oferta es remota.
    Se excluyen las ofertas que el usuario ha descartado (status 'dismissed').
    """
    techs = (prefs or {}).get("tech_stack") or []
    seniority = (prefs or {}).get("seniority")
    want_remote = (prefs or {}).get("work_mode") == "remote"

    with conn.cursor() as cur:
        cur.execute(
            f"""
            SELECT {_JOB_COLS},
                (
                    (SELECT count(*) FROM jsonb_array_elements_text(j.tech_stack) tt
                     WHERE tt = ANY(%(techs)s::text[]))
                    + CASE WHEN j.seniority = %(seniority)s::text THEN 2 ELSE 0 END
                    + CASE WHEN %(want_remote)s::boolean AND j.remote THEN 1 ELSE 0 END
                )::int AS score
            FROM jobs j
            JOIN sources s ON s.id = j.source_id
            WHERE NOT j.is_duplicate
              AND NOT EXISTS (
                  SELECT 1 FROM saved_jobs sj
                  WHERE sj.user_id = %(uid)s AND sj.job_id = j.id AND sj.status = 'dismissed'
              )
            ORDER BY score DESC, j.posted_at DESC NULLS LAST, j.id DESC
            LIMIT %(limit)s OFFSET %(offset)s
            """,
            {
                "techs": techs,
                "seniority": seniority,
                "want_remote": want_remote,
                "uid": user_id,
                "limit": limit,
                "offset": offset,
            },
        )
        return cur.fetchall()
