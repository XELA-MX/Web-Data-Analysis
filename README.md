# Tech Job Market Analyzer

> Agregador del mercado laboral tech. Scrapea ofertas de empleo de fuentes públicas,
> extrae **stack tecnológico + salario + ubicación + seniority**, y lo muestra en un
> **dashboard de tendencias**.
>
> Responde: **"¿Qué tecnologías se piden más, dónde y cuánto pagan?"**

Producto público y multiusuario: los usuarios se registran y obtienen un feed
**personalizado** según su perfil (rol, stack, seniority, modalidad).

## 🏗️ Arquitectura

Pipeline de datos con componentes desacoplados — el scraper **recoge**, el procesador
**enriquece**, la API **sirve**, el dashboard **muestra**:

```
Scraper (Go) ─▶ raw_jobs ─▶ Procesador (Python) ─▶ jobs (Postgres) ─▶ API ─▶ Dashboard (React+TS)
```

Detalle en [`documentación/V1/02-arquitectura.md`](./documentación/V1/02-arquitectura.md).

## 🧰 Stack

| Capa | Tecnología |
|------|------------|
| Scraper | Go (goroutines + worker pool + rate limiting) |
| Procesado | Python (extracción de tech, normalización, dedup) |
| Base de datos | PostgreSQL 16 |
| API | FastAPI (Python) — alternativa: Go (chi/gin) |
| Frontend | React + TypeScript + Vite, gráficas con Recharts/visx |
| Infra | Docker Compose, GitHub Actions (CI), deploy en Fly.io/Railway/Render |

El **porqué** de cada decisión: [`documentación/V1/03-stack-tecnologico.md`](./documentación/V1/03-stack-tecnologico.md).

## 📁 Estructura

```
/scraper      → Go        (recoge ofertas crudas)
/processor    → Python    (limpia y enriquece)
/api          → FastAPI   (REST: búsqueda + agregaciones)
/web          → React+TS  (dashboard)
/migrations   → SQL versionado (fuente de verdad del esquema)
docker-compose.yml
documentación/V1/   → diseño completo del MVP
```

## 🚀 Puesta en marcha (desarrollo)

```bash
# 1. Configurar entorno
cp .env.example .env        # y rellenar los valores reales

# 2. Levantar Postgres local
docker compose up -d

# 3. Aplicar el esquema (cuando golang-migrate esté disponible)
migrate -path ./migrations -database "$DATABASE_URI" up
```

> El esquema vive en [`/migrations`](./migrations) como migrations `.sql` versionadas
> (fuente de verdad). Ver [`migrations/README.md`](./migrations/README.md).

## 🗺️ Roadmap

Plan por fases (0 → 6) en [`documentación/V1/05-roadmap.md`](./documentación/V1/05-roadmap.md).
**Fase actual: 0 — Cimientos.**

## 🔒 Seguridad

Producto con cuentas de usuario → la seguridad es prioridad en cada línea. Checklist
en [`documentación/V1/09-seguridad.md`](./documentación/V1/09-seguridad.md).

## 📚 Documentación

Todo el diseño del MVP está en [`documentación/V1/`](./documentación/V1/).
