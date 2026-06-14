"""Endpoints personales (Fase 4.5): preferencias, ofertas guardadas y feed
personalizado. Todos requieren sesión (get_current_user) y se aíslan por user_id.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, status

from . import personal_queries as pq
from .auth import get_current_user
from .db import get_conn
from .models import FeedItem, PreferencesIn, PreferencesOut, SavedJob, SavedJobIn, SavedStatus

router = APIRouter(prefix="/me", tags=["me"])

_EMPTY_PREFS = {
    "role": None,
    "tech_stack": [],
    "seniority": None,
    "work_mode": None,
    "country": None,
    "salary_target": None,
    "updated_at": None,
}


@router.get("/preferences", response_model=PreferencesOut)
def get_preferences(user=Depends(get_current_user), conn=Depends(get_conn)) -> dict:
    prefs = pq.get_preferences(conn, user["id"])
    return prefs or _EMPTY_PREFS


@router.put("/preferences", response_model=PreferencesOut)
def put_preferences(body: PreferencesIn, user=Depends(get_current_user), conn=Depends(get_conn)) -> dict:
    data = body.model_dump()
    # Normaliza el stack: minúsculas, sin vacíos, sin duplicados (preservando orden).
    data["tech_stack"] = list(dict.fromkeys(t.strip().lower() for t in data["tech_stack"] if t.strip()))
    return pq.upsert_preferences(conn, user["id"], data)


@router.get("/saved", response_model=list[SavedJob])
def list_saved(
    user=Depends(get_current_user),
    conn=Depends(get_conn),
    status_filter: SavedStatus | None = Query(default=None, alias="status"),
) -> list[dict]:
    return pq.list_saved(conn, user["id"], status_filter)


@router.put("/saved", response_model=SavedJob, status_code=status.HTTP_200_OK)
def save_job(body: SavedJobIn, user=Depends(get_current_user), conn=Depends(get_conn)) -> dict:
    row = pq.save_job(conn, user["id"], body.job_id, body.status)
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="La oferta no existe")
    # Devolvemos la oferta completa con su estado guardado.
    saved = pq.list_saved(conn, user["id"], None)
    match = next((s for s in saved if s["id"] == body.job_id), None)
    assert match is not None
    return match


@router.delete("/saved/{job_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_saved(job_id: int, user=Depends(get_current_user), conn=Depends(get_conn)) -> None:
    if not pq.delete_saved(conn, user["id"], job_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No estaba guardada")


@router.get("/feed", response_model=list[FeedItem])
def feed(
    user=Depends(get_current_user),
    conn=Depends(get_conn),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
) -> list[dict]:
    prefs = pq.get_preferences(conn, user["id"])
    return pq.personalized_feed(conn, user["id"], prefs, limit, offset)
