"""Extracción y normalización: de un payload crudo a campos limpios de `jobs`.

Funciones puras y testeables (sin DB), para poder añadir pytest fácilmente en la Fase 6.
"""

from __future__ import annotations

import hashlib
import html
import re
import unicodedata
from datetime import datetime, timezone

from .tech_dictionary import TECH_ALIASES

# ─────────────────────────── texto ───────────────────────────


def strip_accents(text: str) -> str:
    nfkd = unicodedata.normalize("NFKD", text)
    return "".join(c for c in nfkd if not unicodedata.combining(c))


def normalize_text(text: str) -> str:
    """Minúsculas, sin acentos, espacios colapsados. Para fingerprint y matching."""
    text = strip_accents(text.lower())
    return re.sub(r"\s+", " ", text).strip()


def strip_html(text: str) -> str:
    """Quita etiquetas HTML y desescapa entidades (la descripción de RemoteOK es HTML)."""
    text = re.sub(r"<[^>]+>", " ", text)
    text = html.unescape(text)
    return re.sub(r"\s+", " ", text).strip()


# ─────────────────────── deduplicación ───────────────────────


def fingerprint(title: str, company: str) -> str:
    """sha1(title_normalizado + '|' + company_normalizado) para dedup cross-source."""
    key = f"{normalize_text(title)}|{normalize_text(company)}"
    return hashlib.sha1(key.encode("utf-8")).hexdigest()


# ─────────────────────── tech stack ──────────────────────────

# Pre-compilamos un patrón por canónico. Las "fronteras" admiten +, # y . para
# reconocer c++, c#, .net, node.js correctamente.
_BOUNDARY_L = r"(?<![\w+#.])"
_BOUNDARY_R = r"(?![\w+#.])"
_TECH_PATTERNS: dict[str, re.Pattern] = {
    canon: re.compile(
        _BOUNDARY_L + r"(?:" + "|".join(re.escape(a) for a in aliases) + r")" + _BOUNDARY_R,
        re.IGNORECASE,
    )
    for canon, aliases in TECH_ALIASES.items()
}


def extract_tech_stack(tags: list[str], title: str, description: str) -> list[str]:
    """Detecta tecnologías canónicas en tags + título + descripción.

    Los `tags` de RemoteOK ya son señales fuertes; título y descripción aportan extra.
    Devuelve la lista ordenada y sin duplicados.
    """
    haystack = " ".join([*(tags or []), title or "", description or ""])
    found = {canon for canon, pat in _TECH_PATTERNS.items() if pat.search(haystack)}
    return sorted(found)


# ─────────────────────── seniority ───────────────────────────

_SENIOR_RE = re.compile(r"\b(senior|sr|lead|principal|staff|architect|head of)\b", re.IGNORECASE)
_JUNIOR_RE = re.compile(r"\b(junior|jr|intern|internship|entry[- ]level|graduate|trainee)\b", re.IGNORECASE)
_MID_RE = re.compile(r"\b(mid|mid[- ]level|intermediate)\b", re.IGNORECASE)


def infer_seniority(title: str, tags: list[str]) -> str | None:
    """Devuelve 'junior' | 'mid' | 'senior' | None.

    Usa señales fiables: el título primero y, si no, los tags (RemoteOK etiqueta
    explícitamente 'junior'/'senior'). NO se escanea la descripción: genera falsos
    positivos (una mención suelta de 'senior' en el texto no define el puesto).
    """
    tagtext = " ".join(tags or [])
    for text in (title or "", tagtext):
        if _SENIOR_RE.search(text):
            return "senior"
        if _JUNIOR_RE.search(text):
            return "junior"
        if _MID_RE.search(text):
            return "mid"
    return None


# ─────────────────────── salario ─────────────────────────────


def normalize_salary(payload: dict) -> tuple[int | None, int | None, str | None]:
    """RemoteOK da salary_min/salary_max anuales en USD (0 = desconocido).

    Devuelve (min, max, currency). currency solo si hay algún importe.
    """
    smin = _as_positive_int(payload.get("salary_min"))
    smax = _as_positive_int(payload.get("salary_max"))
    if smin is None and smax is None:
        return None, None, None
    return smin, smax, "USD"


def _as_positive_int(value) -> int | None:
    try:
        n = int(value)
    except (TypeError, ValueError):
        return None
    return n if n > 0 else None


# ─────────────────────── remoto / país ───────────────────────

_REMOTE_HINTS = ("remote", "worldwide", "anywhere", "distributed")


def detect_remote(tags: list[str], location: str | None, source: str) -> bool:
    """RemoteOK es un tablón 100% remoto; aun así detectamos por señales (futuras fuentes)."""
    if source == "remoteok":
        return True
    blob = normalize_text(" ".join([*(tags or []), location or ""]))
    return any(h in blob for h in _REMOTE_HINTS)


def extract_country(location: str | None) -> str | None:
    """Best-effort: la ubicación de RemoteOK es texto libre y a menudo "Worldwide".

    Para el MVP devolvemos None cuando no es claramente un país (se mejorará luego).
    """
    if not location:
        return None
    norm = normalize_text(location)
    if any(h in norm for h in _REMOTE_HINTS):
        return None
    return None  # TODO Fase posterior: normalización geográfica real.


# ─────────────────────── fechas ──────────────────────────────


def parse_posted_at(payload: dict) -> datetime | None:
    """Fecha de publicación desde 'date' (ISO 8601) o, en su defecto, 'epoch'."""
    date_str = payload.get("date")
    if isinstance(date_str, str) and date_str:
        try:
            return datetime.fromisoformat(date_str)
        except ValueError:
            pass
    epoch = payload.get("epoch")
    try:
        return datetime.fromtimestamp(int(epoch), tz=timezone.utc)
    except (TypeError, ValueError):
        return None
