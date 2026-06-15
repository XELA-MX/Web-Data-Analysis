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
_INTERN_RE = re.compile(
    r"\b(intern|internship|becari[oa]|pr[aá]cticas|trainee|undergraduate|working student|werkstudent)\b",
    re.IGNORECASE,
)
_JUNIOR_RE = re.compile(r"\b(junior|jr|entry[- ]level|graduate)\b", re.IGNORECASE)
_MID_RE = re.compile(r"\b(mid|mid[- ]level|intermediate)\b", re.IGNORECASE)


def infer_seniority(title: str, tags: list[str]) -> str | None:
    """Devuelve 'intern' | 'junior' | 'mid' | 'senior' | None.

    Usa señales fiables: el título primero y, si no, los tags. NO se escanea la
    descripción (falsos positivos). 'intern' (prácticas/becario/undergraduate) se
    comprueba antes que 'junior'.
    """
    tagtext = " ".join(tags or [])
    for text in (title or "", tagtext):
        if _SENIOR_RE.search(text):
            return "senior"
        if _INTERN_RE.search(text):
            return "intern"
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


# ─────────────────────── categoría ───────────────────────────

# Por título (señal fuerte). Orden: de más específico a menos.
_CATEGORY_TITLE = [
    ("fullstack", re.compile(r"\bfull[\s-]?stack\b", re.IGNORECASE)),
    ("mobile", re.compile(r"\b(ios|android|mobile|react native|flutter)\b", re.IGNORECASE)),
    ("devops", re.compile(r"\b(devops|sre|site reliability|platform|infra|infrastructure|cloud engineer)\b", re.IGNORECASE)),
    ("data", re.compile(r"\b(data|machine learning|\bml\b|analytics|analyst|scientist|big data)\b", re.IGNORECASE)),
    ("qa", re.compile(r"\b(qa|quality assurance|tester|testing|sdet)\b", re.IGNORECASE)),
    ("security", re.compile(r"\b(security|seguridad|cyber|infosec)\b", re.IGNORECASE)),
    ("frontend", re.compile(r"\b(frontend|front[\s-]end|ui engineer)\b", re.IGNORECASE)),
    ("backend", re.compile(r"\b(backend|back[\s-]end)\b", re.IGNORECASE)),
]

# Por stack (si el título no lo dice). Conjuntos razonablemente distintos.
_CATEGORY_TECH: dict[str, set[str]] = {
    "frontend": {"react", "vue", "angular", "svelte", "nextjs", "tailwind", "html", "css"},
    "backend": {"go", "python", "java", "php", "ruby", "rails", "django", "flask", "spring",
                "nodejs", "dotnet", "express", "laravel", "c#", "c++", "graphql"},
    "data": {"pandas", "spark", "tensorflow", "pytorch", "machine learning", "kafka", "elasticsearch"},
    "devops": {"docker", "kubernetes", "terraform", "ansible", "aws", "gcp", "azure", "ci/cd"},
    "mobile": {"swift", "kotlin"},
}


def categorize(title: str, tech_stack: list[str]) -> str:
    """Clasifica la oferta en una categoría para filtrar. El título manda; si no,
    se infiere del stack. Si hay señales de frontend Y backend → fullstack."""
    for cat, rx in _CATEGORY_TITLE:
        if rx.search(title or ""):
            return cat

    techs = set(tech_stack)
    counts = {cat: len(techs & s) for cat, s in _CATEGORY_TECH.items()}
    if counts["frontend"] and counts["backend"]:
        return "fullstack"
    if any(counts.values()):
        return max(counts, key=lambda c: counts[c])
    return "other"


def parse_datetime(value) -> datetime | None:
    """Convierte un valor a datetime con zona horaria (UTC si viene sin tz).

    Acepta una cadena ISO 8601 (ej. RemoteOK/Remotive) o un epoch en segundos
    (ej. RemoteOK 'epoch' / Arbeitnow 'created_at').
    """
    if value is None:
        return None
    if isinstance(value, str):
        if not value:
            return None
        try:
            dt = datetime.fromisoformat(value)
        except ValueError:
            return None
        return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)
    try:
        return datetime.fromtimestamp(int(value), tz=timezone.utc)
    except (TypeError, ValueError):
        return None
