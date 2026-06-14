"""Conexión a Postgres mediante un pool. La conexión sale de DATABASE_URI.

Todas las consultas del proyecto son parametrizadas (nunca se concatena SQL).
"""

from __future__ import annotations

import os
from collections.abc import Iterator

import psycopg
from dotenv import find_dotenv, load_dotenv
from psycopg.rows import dict_row
from psycopg_pool import ConnectionPool

# Carga el .env del proyecto (buscándolo hacia arriba desde el cwd) si existe.
# No sobreescribe variables ya presentes en el entorno (el shell tiene prioridad),
# así que funciona tanto con DATABASE_URI exportada como solo con el .env.
load_dotenv(find_dotenv(usecwd=True))

_pool: ConnectionPool | None = None


def init_pool() -> ConnectionPool:
    """Crea el pool (idempotente). Se llama en el arranque de la app."""
    global _pool
    if _pool is None:
        dsn = os.environ.get("DATABASE_URI")
        if not dsn:
            raise RuntimeError("Falta la variable de entorno DATABASE_URI")
        _pool = ConnectionPool(
            dsn,
            min_size=1,
            max_size=5,
            kwargs={"row_factory": dict_row},
            open=True,
        )
    return _pool


def close_pool() -> None:
    global _pool
    if _pool is not None:
        _pool.close()
        _pool = None


def get_conn() -> Iterator[psycopg.Connection]:
    """Dependencia de FastAPI: presta una conexión del pool por request."""
    if _pool is None:
        raise RuntimeError("El pool no está inicializado")
    with _pool.connection() as conn:
        yield conn
