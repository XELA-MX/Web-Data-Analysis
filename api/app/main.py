"""Punto de entrada de la API FastAPI.

Arranque/cierre del pool de DB vía lifespan; CORS restringido al origen del
frontend (configurable con CORS_ORIGINS).
"""

from __future__ import annotations

import os
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from . import auth, db
from .routers import jobs, stats

# Orígenes permitidos para CORS (coma-separados). Por defecto, el dev server de Vite.
CORS_ORIGINS = os.environ.get("CORS_ORIGINS", "http://localhost:5173").split(",")


@asynccontextmanager
async def lifespan(app: FastAPI):
    db.init_pool()
    yield
    db.close_pool()


app = FastAPI(
    title="Tech Job Market Analyzer API",
    version="0.1.0",
    description="Búsqueda y agregaciones del mercado laboral tech.",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in CORS_ORIGINS if o.strip()],
    allow_credentials=True,  # necesario para enviar/recibir la cookie de sesión
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)


@app.middleware("http")
async def security_headers(request: Request, call_next):
    """Cabeceras de seguridad básicas (ver documentación/V1/09-seguridad.md)."""
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    return response


app.include_router(auth.router)
app.include_router(jobs.router)
app.include_router(stats.router)


@app.get("/health", tags=["meta"])
def health(conn=Depends(db.get_conn)) -> dict:
    """Comprueba que la API responde y que la DB es alcanzable."""
    with conn.cursor() as cur:
        cur.execute("SELECT 1 AS ok")
        cur.fetchone()
    return {"status": "ok", "db": "ok"}
