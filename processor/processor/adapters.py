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


_CURRENCY_BY_SYMBOL = {"€": "EUR", "$": "USD", "£": "GBP"}


def _pos_int(value) -> int | None:
    try:
        n = int(value)
    except (TypeError, ValueError):
        return None
    return n if n > 0 else None


def _manfred(p: dict) -> dict:
    company = p.get("company") or {}
    locations = p.get("locations") or []
    salary_min = _pos_int(p.get("salaryFrom"))
    salary_max = _pos_int(p.get("salaryTo"))
    currency = _CURRENCY_BY_SYMBOL.get(p.get("currency"), p.get("currency"))
    remote_pct = p.get("remotePercentage") or 0
    return {
        "title": p.get("position") or "",
        "company": company.get("name") or "",
        "location": locations[0] if locations else None,
        # techNames lo añade el scraper desde el detalle de la oferta (skills reales).
        "tags": p.get("techNames") or [],
        "description": "",
        "remote": isinstance(remote_pct, (int, float)) and remote_pct >= 80,
        "salary_min": salary_min,
        "salary_max": salary_max,
        "currency": currency if (salary_min or salary_max) else None,
        "url": None,  # la construye el scraper y va en raw_jobs.url
        "posted_at": extract.parse_datetime(p.get("updatedAt")),
    }


def _jobicy(p: dict) -> dict:
    smin = _pos_int(p.get("annualSalaryMin"))
    smax = _pos_int(p.get("annualSalaryMax"))
    return {
        "title": p.get("jobTitle") or "",
        "company": p.get("companyName") or "",
        "location": p.get("jobGeo"),
        "tags": [],  # Jobicy no da tags tech → se extrae del título/descripción
        "description": p.get("jobDescription") or "",
        "remote": True,
        "salary_min": smin,
        "salary_max": smax,
        "currency": "USD" if (smin or smax) else None,
        "url": p.get("url"),
        "posted_at": extract.parse_datetime(p.get("pubDate")),
    }


def _greenhouse(p: dict) -> dict:
    loc_obj = p.get("location")
    location = loc_obj.get("name") if isinstance(loc_obj, dict) else None
    return {
        "title": p.get("title") or "",
        "company": p.get("company_name") or p.get("_board") or "",
        "location": location,
        "tags": [],  # el listado no trae skills → tech del título
        "description": "",
        "remote": bool(location and "remote" in location.lower()),
        "salary_min": None,
        "salary_max": None,
        "currency": None,
        "url": p.get("absolute_url"),
        "posted_at": extract.parse_datetime(p.get("updated_at")),
    }


_ADAPTERS = {
    "remoteok": _remoteok,
    "remotive": _remotive,
    "arbeitnow": _arbeitnow,
    "manfred": _manfred,
    "jobicy": _jobicy,
    "greenhouse": _greenhouse,
}
