"""Orquestación del ETL: raw_jobs -> transformación -> jobs.

Procesa en lotes y confirma (commit) por lote: si algo falla a mitad, lo ya
confirmado queda persistido y lo demás se reintenta en la siguiente ejecución
(las crudas siguen marcadas como no procesadas).
"""

from __future__ import annotations

import logging

from . import adapters, db, extract

log = logging.getLogger("processor")


def transform(raw: dict) -> dict:
    """Convierte una fila de raw_jobs en el dict de campos de `jobs`.

    El mapeo específico de cada fuente lo hace su adaptador; aquí solo se aplica el
    enriquecimiento común (limpiar descripción, tech_stack, seniority, fingerprint).
    """
    norm = adapters.adapt(raw["source_name"], raw["raw_payload"])

    title = norm["title"]
    company = norm["company"]
    tags = norm["tags"]
    description = extract.strip_html(norm["description"])
    tech_stack = extract.extract_tech_stack(tags, title, description)

    return {
        "source_id": raw["source_id"],
        "external_id": raw["external_id"],
        "fingerprint": extract.fingerprint(title, company),
        "title": title,
        "company": company or None,
        "location": norm["location"] or None,
        "country": extract.extract_country(norm["location"]),
        "remote": norm["remote"],
        "salary_min": norm["salary_min"],
        "salary_max": norm["salary_max"],
        "currency": norm["currency"],
        "tech_stack": tech_stack,
        "seniority": extract.infer_seniority(title, tags),
        "category": extract.categorize(title, tech_stack),
        "description": description or None,
        "url": norm["url"] or raw["url"],
        "posted_at": norm["posted_at"],
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

        # Deduplicación cross-source una vez procesado todo lo pendiente.
        changed = db.recompute_duplicates(conn)
        conn.commit()
        log.info("deduplicación: %d filas actualizadas", changed)

    log.info("procesado completado: %d ofertas", total)
    return total
