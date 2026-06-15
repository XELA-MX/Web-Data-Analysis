# api (FastAPI)

API REST de búsqueda/filtrado de ofertas y agregaciones sobre `jobs`. Sirve siempre
el conjunto **canónico** (`is_duplicate = FALSE`). Ver RF-12 en
`documentación/V1/01-requisitos.md`.

## Endpoints

| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/health` | Liveness + comprobación de DB |
| GET | `/jobs` | Búsqueda/filtrado. Query: `q`, `tech` (repetible, AND), `seniority`, `category`, `remote`, `source`, `salary_min`, `limit` (1-100), `offset` |
| GET | `/stats/overview` | Totales: jobs, % remoto, con salario, con tech, fuentes, último scrape |
| GET | `/stats/tech` | Top tecnologías (`limit`) |
| GET | `/stats/categories` | Ofertas por categoría (frontend, backend, data…) |
| GET | `/stats/salary` | Rangos salariales medios por `by=seniority\|tech` |
| GET | `/stats/trends` | Ofertas vistas por día (`days`, 1-365) |
| GET | `/stats/sources` | Nº de ofertas canónicas por fuente |
| POST | `/auth/register` | Alta email+password (argon2id) → crea sesión |
| POST | `/auth/login` | Login → cookie de sesión httpOnly |
| POST | `/auth/logout` | Cierra la sesión |
| GET | `/auth/me` | Usuario autenticado (401 si no) |
| DELETE | `/auth/me` | Borra la cuenta y sus datos (RGPD) |
| GET/PUT | `/me/preferences` | Lee/actualiza el perfil (rol, stack, seniority, modalidad…) |
| GET | `/me/feed` | Feed personalizado por afinidad (scoring) |
| GET | `/me/saved` | Ofertas guardadas/descartadas (filtro `status`) |
| PUT | `/me/saved` | Guarda/descarta/marca-aplicada una oferta |
| DELETE | `/me/saved/{job_id}` | Quita una oferta de guardadas |
| GET | `/admin/stats` | (admin) Métricas: usuarios, ofertas, sin procesar, fuentes |
| POST | `/admin/refresh` | (admin) Relanza scraper+procesador en background (`?full=true` = con skills Manfred) |
| GET | `/admin/refresh` | (admin) Estado del refresco (running/done/error) |

> Los endpoints `/admin/*` exigen **rol admin** (`require_admin` → 403 si no). Para hacer
> admin a un usuario: `UPDATE users SET is_admin=TRUE WHERE email='...'`. El refresco lanza
> el scraper Go (`go run`) + el procesador como subprocesos → la API necesita `go` en el PATH
> y el venv de `/processor` (`.venv`).

> Los endpoints `/me/*` requieren sesión y se **aíslan por el `user_id` de la sesión**
> (un usuario nunca ve/borra datos de otro). El **scoring** del feed: +1 por cada
> tecnología del perfil presente en la oferta, +2 si coincide el seniority, +1 si quiere
> remoto y la oferta es remota; excluye las descartadas.

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
- **CORS restringido** al origen del frontend (`allow_credentials` para la cookie).
- **Cabeceras**: `X-Content-Type-Options`, `X-Frame-Options: DENY`, `Referrer-Policy`.
- **Auth (Fase 4.5):** contraseñas con **argon2id**; sesiones server-side con cookie
  **httpOnly + SameSite** (+ `Secure` en prod vía `COOKIE_SECURE`); en la DB se guarda
  solo el **SHA-256 del token**. Errores de login **genéricos** (anti-enumeración).
  **Rate limit** por IP en registro/login. Autorización por el `user_id` de la sesión (anti-IDOR).

### Variables de entorno (auth)

- `COOKIE_SECURE` (`true`/`false`, por defecto `false` en dev; `true` en prod con HTTPS).

## Estado

- ✅ **Fase 4 (API) — hecha:** endpoints de búsqueda + agregaciones verificados con datos reales.
- ⬜ **Fase 4 (dashboard):** frontend React+TS que consume esta API.
- ⬜ Auth y feed personalizado: **Fase 4.5**.
