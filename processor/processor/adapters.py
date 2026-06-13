"""Adaptadores por fuente: del payload crudo (cada API tiene su forma) a un
diccionario normalizado común. Aquí vive todo lo específico de cada fuente; el
enriquecimiento posterior (tech, seniority, fingerprint) es uniforme.

Añadir una fuente = añadir un adaptador y registrarlo en _ADAPTERS.
"""

from __future__ import annotations

from . import extract

# Claves del diccionario normalizado que produce cada adaptador:
#   title, company, location, tags, description, remote,
#   salary_min, salary_max, currency, url, posted_at


def adapt(source_name: str, payload: dict) -> dict:
    fn = _ADAPTERS.get(source_name)
    if fn is None:
        raise ValueError(f"sin adaptador para la fuente {source_name!r}")
    return fn(payload or {})


def _remoteok(p: dict) -> dict:
    smin, smax, currency = extract.normalize_salary(p)
    return {
        "title": p.get("position") or "",
        "company": p.get("company") or "",
        "location": p.get("location"),
        "tags": p.get("tags") or [],
        "description": p.get("description") or "",
        "remote": True,  # RemoteOK es 100% remoto.
        "salary_min": smin,
        "salary_max": smax,
        "currency": currency,
        "url": p.get("url"),
        "posted_at": extract.parse_datetime(p.get("date") or p.get("epoch")),
    }


def _remotive(p: dict) -> dict:
    return {
        "title": p.get("title") or "",
        "company": p.get("company_name") or "",
        "location": p.get("candidate_required_location"),
        "tags": p.get("tags") or [],
        "description": p.get("description") or "",
        "remote": True,  # Remotive es tablón remoto.
        # salary de Remotive es texto libre ("$31,2k- $52k") → parseo en fase futura.
        "salary_min": None,
        "salary_max": None,
        "currency": None,
        "url": p.get("url"),
        "posted_at": extract.parse_datetime(p.get("publication_date")),
    }


def _arbeitnow(p: dict) -> dict:
    tags = list(p.get("tags") or []) + list(p.get("job_types") or [])
    return {
        "title": p.get("title") or "",
        "company": p.get("company_name") or "",
        "location": p.get("location"),
        "tags": tags,
        "description": p.get("description") or "",
        "remote": bool(p.get("remote")),  # Arbeitnow trae remote booleano real.
        "salary_min": None,
        "salary_max": None,
        "currency": None,
        "url": p.get("url"),
        "posted_at": extract.parse_datetime(p.get("created_at")),
    }


_ADAPTERS = {
    "remoteok": _remoteok,
    "remotive": _remotive,
    "arbeitnow": _arbeitnow,
}
