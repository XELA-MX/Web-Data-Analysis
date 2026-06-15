"""Endpoints de administración (Fase 4.5+). Requieren rol admin (require_admin).

- GET  /admin/stats    → métricas operativas.
- POST /admin/refresh  → relanza el scraping + procesado en segundo plano.
- GET  /admin/refresh  → estado del último refresco.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query

from . import admin_jobs, queries
from .auth import require_admin
from .db import get_conn
from .models import AdminStats, RefreshState, SourceCount

router = APIRouter(prefix="/admin", tags=["admin"], dependencies=[Depends(require_admin)])


@router.get("/stats", response_model=AdminStats)
def stats(conn=Depends(get_conn)) -> AdminStats:
    base = queries.admin_stats(conn)
    sources = [SourceCount(**r) for r in queries.sources_with_counts(conn)]
    return AdminStats(**base, sources=sources)


@router.post("/refresh", response_model=RefreshState)
def refresh(full: bool = Query(False, description="incluir el detalle de Manfred (más lento)")) -> RefreshState:
    admin_jobs.start_refresh(full=full)
    return RefreshState(**admin_jobs.get_state())


@router.get("/refresh", response_model=RefreshState)
def refresh_state() -> RefreshState:
    return RefreshState(**admin_jobs.get_state())
