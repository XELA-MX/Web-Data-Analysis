"""Consultas de cuentas y sesiones. Todas parametrizadas.

Toda lectura/escritura de datos personales se hace por el `user_id` de la sesión
(la capa de router nunca confía en un id que venga del cliente) → evita IDOR.
"""

from __future__ import annotations

from datetime import datetime

import psycopg
from psycopg.errors import UniqueViolation

_USER_PUBLIC = "id, email, display_name, provider, created_at, last_login_at"


def create_user(conn: psycopg.Connection, email: str, password_hash: str, display_name: str | None) -> dict | None:
    """Crea un usuario email+password. Devuelve None si el email ya existe."""
    try:
        with conn.cursor() as cur:
            cur.execute(
                f"""
                INSERT INTO users (email, provider, password_hash, display_name)
                VALUES (%s, 'email', %s, %s)
                RETURNING {_USER_PUBLIC}
                """,
                (email, password_hash, display_name),
            )
            row = cur.fetchone()
        conn.commit()
        return row
    except UniqueViolation:
        conn.rollback()
        return None


def get_auth_by_email(conn: psycopg.Connection, email: str) -> dict | None:
    """Incluye password_hash: uso interno solo para verificar login."""
    with conn.cursor() as cur:
        cur.execute("SELECT id, email, password_hash FROM users WHERE email = %s", (email,))
        return cur.fetchone()


def get_user_by_id(conn: psycopg.Connection, user_id: int) -> dict | None:
    with conn.cursor() as cur:
        cur.execute(f"SELECT {_USER_PUBLIC} FROM users WHERE id = %s", (user_id,))
        return cur.fetchone()


def touch_last_login(conn: psycopg.Connection, user_id: int) -> None:
    with conn.cursor() as cur:
        cur.execute("UPDATE users SET last_login_at = now() WHERE id = %s", (user_id,))
    conn.commit()


def delete_user(conn: psycopg.Connection, user_id: int) -> None:
    """Borra la cuenta y, en cascada, sus preferencias/guardados/sesiones (RGPD)."""
    with conn.cursor() as cur:
        cur.execute("DELETE FROM users WHERE id = %s", (user_id,))
    conn.commit()


# ───────────────────────────── sesiones ─────────────────────────────


def create_session(conn: psycopg.Connection, session_id: str, user_id: int, expires_at: datetime) -> None:
    with conn.cursor() as cur:
        cur.execute(
            "INSERT INTO sessions (id, user_id, expires_at) VALUES (%s, %s, %s)",
            (session_id, user_id, expires_at),
        )
    conn.commit()


def get_user_by_session(conn: psycopg.Connection, session_id: str) -> dict | None:
    """Devuelve el usuario de una sesión vigente (no expirada), o None."""
    with conn.cursor() as cur:
        cur.execute(
            f"""
            SELECT {", ".join("u." + c for c in _USER_PUBLIC.split(", "))}
            FROM sessions s
            JOIN users u ON u.id = s.user_id
            WHERE s.id = %s AND s.expires_at > now()
            """,
            (session_id,),
        )
        return cur.fetchone()


def delete_session(conn: psycopg.Connection, session_id: str) -> None:
    with conn.cursor() as cur:
        cur.execute("DELETE FROM sessions WHERE id = %s", (session_id,))
    conn.commit()
