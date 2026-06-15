"""Endpoints de agregaciones y series temporales (RF-12, RF-13..RF-17)."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query

from .. import queries
from ..db import get_conn
from ..models import CategoryCount, Overview, SalaryByGroup, SourceCount, TechCount, TrendPoint

router = APIRouter(prefix="/stats", tags=["stats"])


@router.get("/overview", response_model=Overview)
def get_overview(conn=Depends(get_conn)) -> Overview:
    return Overview(**queries.overview(conn))


@router.get("/tech", response_model=list[TechCount])
def get_top_tech(conn=Depends(get_conn), limit: int = Query(20, ge=1, le=100)) -> list[TechCount]:
    return [TechCount(**r) for r in queries.top_tech(conn, limit)]


@router.get("/categories", response_model=list[CategoryCount])
def get_categories(conn=Depends(get_conn)) -> list[CategoryCount]:
    return [CategoryCount(**r) for r in queries.categories(conn)]


@router.get("/salary", response_model=list[SalaryByGroup])
def get_salary(
    conn=Depends(get_conn),
    by: str = Query("seniority", pattern="^(seniority|tech)$"),
    limit: int = Query(20, ge=1, le=100),
) -> list[SalaryByGroup]:
    return [SalaryByGroup(**r) for r in queries.salary_by(conn, by, limit)]


@router.get("/trends", response_model=list[TrendPoint])
def get_trends(conn=Depends(get_conn), days: int = Query(30, ge=1, le=365)) -> list[TrendPoint]:
    return [TrendPoint(**r) for r in queries.trends(conn, days)]


@router.get("/sources", response_model=list[SourceCount])
def get_sources(conn=Depends(get_conn)) -> list[SourceCount]:
    return [SourceCount(**r) for r in queries.sources_with_counts(conn)]
