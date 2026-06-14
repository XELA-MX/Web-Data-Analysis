"""Endpoints de búsqueda/filtrado de ofertas (RF-12)."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query

from .. import queries
from ..db import get_conn
from ..models import JobList

router = APIRouter(tags=["jobs"])


@router.get("/jobs", response_model=JobList)
def list_jobs(
    conn=Depends(get_conn),
    q: str | None = Query(None, description="texto en título o empresa"),
    tech: list[str] | None = Query(None, description="tecnologías (deben estar todas)"),
    seniority: str | None = Query(None, pattern="^(junior|mid|senior)$"),
    remote: bool | None = Query(None),
    source: str | None = Query(None),
    salary_min: int | None = Query(None, ge=0, description="salario máximo de la oferta >= este valor"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
) -> JobList:
    total, items = queries.search_jobs(
        conn,
        q=q,
        tech=tech,
        seniority=seniority,
        remote=remote,
        source=source,
        salary_min=salary_min,
        limit=limit,
        offset=offset,
    )
    return JobList(total=total, limit=limit, offset=offset, items=items)
