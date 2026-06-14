# api (FastAPI)

API REST de búsqueda/filtrado de ofertas y agregaciones sobre `jobs`. Sirve siempre
el conjunto **canónico** (`is_duplicate = FALSE`). Ver RF-12 en
`documentación/V1/01-requisitos.md`.

## Endpoints

| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/health` | Liveness + comprobación de DB |
| GET | `/jobs` | Búsqueda/filtrado. Query: `q`, `tech` (repetible, AND), `seniority`, `remote`, `source`, `salary_min`, `limit` (1-100), `offset` |
| GET | `/stats/overview` | Totales: jobs, % remoto, con salario, con tech, fuentes, último scrape |
| GET | `/stats/tech` | Top tecnologías (`limit`) |
| GET | `/stats/salary` | Rangos salariales medios por `by=seniority\|tech` |
| GET | `/stats/trends` | Ofertas vistas por día (`days`, 1-365) |
| GET | `/stats/sources` | Nº de ofertas canónicas por fuente |

Docs interactivos automáticos en `/docs` (Swagger) y `/redoc`.

## Estructura

```
app/
  main.py            FastAPI app, CORS, lifespan (pool), /health
  db.py              pool de conexiones (psycopg_pool); DATABASE_URI
  models.py          modelos de respuesta (Pydantic)
  queries.py         SQL parametrizado (filtros dinámicos seguros)
  routers/jobs.py    GET /jobs
  routers/stats.py   GET /stats/*
```

## Uso

```bash
cd api
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# Requiere DATABASE_URI en el entorno (igual que el procesador).
uvicorn app.main:app --reload --port 8000
```

Variables: `DATABASE_URI` (conexión), `CORS_ORIGINS` (orígenes permitidos,
coma-separados; por defecto `http://localhost:5173`).

## Seguridad

- **SQL siempre parametrizado** (nunca se concatenan valores).
- **Validación de entrada** con FastAPI/Pydantic (tipos, rangos, `pattern`) → 422 si no encaja.
- **CORS restringido** al origen del frontend.
- Solo métodos `GET` (la API es de lectura en V1).

## Estado

- ✅ **Fase 4 (API) — hecha:** endpoints de búsqueda + agregaciones verificados con datos reales.
- ⬜ **Fase 4 (dashboard):** frontend React+TS que consume esta API.
- ⬜ Auth y feed personalizado: **Fase 4.5**.
