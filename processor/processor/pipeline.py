"""Orquestación del ETL: raw_jobs -> transformación -> jobs.

Procesa en lotes y confirma (commit) por lote: si algo falla a mitad, lo ya
confirmado queda persistido y lo demás se reintenta en la siguiente ejecución
(las crudas siguen marcadas como no procesadas).
"""

from __future__ import annotations

import logging

from . import db, extract

log = logging.getLogger("processor")


def transform(raw: dict) -> dict:
    """Convierte una fila de raw_jobs en el dict de campos de `jobs`."""
    payload: dict = raw["raw_payload"] or {}
    tags = payload.get("tags") or []
    title = payload.get("position") or ""
    company = payload.get("company") or ""
    description = extract.strip_html(payload.get("description") or "")

    salary_min, salary_max, currency = extract.normalize_salary(payload)

    return {
        "source_id": raw["source_id"],
        "external_id": raw["external_id"],
        "fingerprint": extract.fingerprint(title, company),
        "title": title,
        "company": company or None,
        "location": payload.get("location") or None,
        "country": extract.extract_country(payload.get("location")),
        "remote": extract.detect_remote(tags, payload.get("location"), "remoteok"),
        "salary_min": salary_min,
        "salary_max": salary_max,
        "currency": currency,
        "tech_stack": extract.extract_tech_stack(tags, title, description),
        "seniority": extract.infer_seniority(title, tags),
        "description": description or None,
        "url": payload.get("url") or raw["url"],
        "posted_at": extract.parse_posted_at(payload),
        "scraped_at": raw["scraped_at"],
    }


def run(batch_size: int = 500) -> int:
    """Procesa todas las crudas pendientes en lotes. Devuelve el total procesado."""
    total = 0
    with db.connect() as conn:
        while True:
            rows = db.fetch_unprocessed(conn, batch_size)
            if not rows:
                break

            for raw in rows:
                try:
                    db.upsert_job(conn, transform(raw))
                except Exception:
                    log.exception("error procesando raw_job id=%s", raw["id"])
                    raise

            db.mark_processed(conn, [r["id"] for r in rows])
            conn.commit()

            total += len(rows)
            log.info("lote procesado: %d (acumulado %d)", len(rows), total)

    log.info("procesado completado: %d ofertas", total)
    return total
