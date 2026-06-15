"""Modelos de respuesta (Pydantic). Definen el contrato público de la API."""

from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, EmailStr, Field


class Job(BaseModel):
    id: int
    source: str
    title: str
    company: str | None
    location: str | None
    country: str | None
    remote: bool
    salary_min: int | None
    salary_max: int | None
    currency: str | None
    tech_stack: list[str]
    seniority: str | None
    category: str | None
    url: str | None
    posted_at: datetime | None


class JobList(BaseModel):
    total: int
    limit: int
    offset: int
    items: list[Job]


class TechCount(BaseModel):
    tech: str
    count: int


class CategoryCount(BaseModel):
    category: str
    count: int


class SalaryByGroup(BaseModel):
    group: str
    jobs: int
    avg_min: int | None
    avg_max: int | None


class TrendPoint(BaseModel):
    day: str
    jobs: int


class SourceCount(BaseModel):
    source: str
    jobs: int


class AdminStats(BaseModel):
    users: int
    jobs: int
    pending_raw: int
    last_scraped: datetime | None
    sources: list["SourceCount"]


class RefreshState(BaseModel):
    status: str  # idle | running | done | error
    step: str | None = None
    progress: int = 0
    message: str | None = None
    log: list[str] = []
    started_at: str | None = None
    finished_at: str | None = None


class Overview(BaseModel):
    total_jobs: int
    remote_jobs: int
    remote_pct: float
    with_salary: int
    with_tech: int
    sources: int
    last_scraped: datetime | None


# ───────────────────────────── auth ─────────────────────────────


class RegisterIn(BaseModel):
    email: EmailStr
    password: str = Field(min_length=10, max_length=200)
    display_name: str | None = Field(default=None, max_length=80)


class LoginIn(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=200)


class UserOut(BaseModel):
    id: int
    email: EmailStr
    display_name: str | None
    provider: str
    created_at: datetime
    last_login_at: datetime | None
    is_admin: bool


# ──────────────────────── personalización ────────────────────────

Seniority = Literal["intern", "junior", "mid", "senior"]
WorkMode = Literal["remote", "hybrid", "onsite"]
SavedStatus = Literal["saved", "dismissed", "applied"]


class PreferencesIn(BaseModel):
    categories: list[str] = Field(default_factory=list, max_length=12)
    tech_stack: list[str] = Field(default_factory=list, max_length=50)
    seniority: Seniority | None = None
    work_mode: WorkMode | None = None
    country: str | None = Field(default=None, max_length=60)
    salary_target: int | None = Field(default=None, ge=0)


class PreferencesOut(BaseModel):
    categories: list[str]
    tech_stack: list[str]
    seniority: str | None
    work_mode: str | None
    country: str | None
    salary_target: int | None
    updated_at: datetime | None


class SavedJobIn(BaseModel):
    job_id: int
    status: SavedStatus = "saved"


class SavedJob(Job):
    saved_status: str
    saved_at: datetime


class FeedItem(Job):
    score: int
