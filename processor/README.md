# processor (Python)

Limpia y enriquece los `RawJob` → `Job`. Es la pieza **"inteligente"** del pipeline:
lee `raw_jobs` (lo no procesado), transforma y escribe en `jobs`.

- **tech_stack**: detección por diccionario + regex (tags + título + descripción).
- **salario**: normaliza `salary_min/max` a USD anual (None si desconocido).
- **seniority**: inferida desde título + tags (`junior`/`mid`/`senior`).
- **category**: clasificación (`frontend`/`backend`/`fullstack`/`mobile`/`data`/`devops`/`qa`/`security`/`other`)
  desde el título + el stack — para que el usuario filtre fácil. Se aplica a todas las fuentes.
- **remoto**: detectado por fuente/señales (RemoteOK es 100% remoto).
- **fingerprint**: `sha1(title_norm + "|" + company_norm)` para dedup (Fase 3).
- **idempotente**: upsert por `(source_id, external_id)`; conserva `first_seen_at`.

## Estructura

```
processor/
  __main__.py          entrypoint: python -m processor
  pipeline.py          orquesta raw_jobs -> transform -> jobs (por lotes) + dedup
  adapters.py          mapeo por fuente (payload crudo -> dict normalizado común)
  extract.py           funciones puras: tech, salario, seniority, remoto, fingerprint, fechas
  tech_dictionary.py   forma canónica -> alias de cada tecnología
  db.py                acceso a Postgres (consultas parametrizadas) + recálculo de duplicados
```

Añadir una fuente nueva = añadir su adaptador en `adapters.py` (el enriquecimiento
común no cambia).

## Deduplicación

Tras procesar lo pendiente, `recompute_duplicates` recalcula `jobs.is_duplicate` con
una *window function*: por cada `fingerprint`, la oferta más antigua es la canónica y
el resto se marcan como duplicadas. La API mostrará solo `is_duplicate = FALSE`.

## Uso

```bash
cd processor
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# Requiere DATABASE_URI en el entorno (igual que el MCP / el scraper).
python -m processor                 # procesa todo lo pendiente
python -m processor --batch-size 200
```

## Estado

- ✅ **Fase 2 hecha:** ETL completo `raw_jobs` → `jobs` verificado con datos reales.
- ✅ **Fase 3 hecha:** multi-fuente (adaptadores) + deduplicación por `fingerprint`.
- ⬜ Mejoras: normalización de país, parseo de salario de Remotive (texto libre),
  reparar *mojibake* de origen, diccionario de tech más amplio.

> **Limitación conocida:** algunos títulos de RemoteOK llegan con doble codificación
> (*mojibake*, p.ej. emojis) desde el origen. No es un bug del pipeline; se abordará
> con una reparación de texto en una fase posterior.
