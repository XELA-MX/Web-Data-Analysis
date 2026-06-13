# 03 · Stack tecnológico

> Cada elección está justificada. En una entrevista debes poder decir **por qué**
> elegiste cada cosa.

## 🧰 Resumen

| Capa | Tecnología | Por qué |
|------|------------|---------|
| Scraper | **Go** | Concurrencia nativa (goroutines), binario único, rápido para I/O paralelo |
| Procesado | **Python** | Mejor ecosistema de datos/NLP (regex, spaCy, pandas) |
| Base de datos | **PostgreSQL** | Relacional sólido, agregaciones potentes, JSON cuando hace falta |
| API | **Go (chi/gin)** o **Python (FastAPI)** | Ver decisión abajo |
| Frontend | **React + TypeScript** | Estándar de la industria, tipado fuerte |
| Gráficas | **Recharts** o **visx** | Visualización declarativa en React |
| Contenedores | **Docker + Docker Compose** | Reproducibilidad, "un comando levanta todo" |
| CI/CD | **GitHub Actions** | Lint + test + build automáticos |
| Deploy | **Fly.io / Railway / Render** | Free tier, despliegue sencillo |

## 🔍 Decisiones clave

### ¿Por qué Go para el scraper?
- **Concurrencia de primera clase:** goroutines + channels hacen trivial scrapear
  muchas páginas/fuentes en paralelo con control fino.
- **Rate limiting limpio** con `golang.org/x/time/rate`.
- **Binario único** sin runtime → deploy y scheduling sencillos.
- Demuestra una habilidad menos común que "otro backend en Node/Python" → diferencia el CV.

### ¿Por qué Python para el procesado?
- Extracción de tecnologías y normalización de texto es **mucho más cómoda** en Python.
- Camino de evolución claro: regex → diccionarios → spaCy/embeddings si se quiere subir nivel.

### API: ¿Go o Python?
| | Go (chi/gin) | Python (FastAPI) |
|---|---|---|
| Pros | Un binario, rápido, mismo lenguaje que el scraper | Comparte código con el procesador, docs OpenAPI automáticas |
| Contras | Agregaciones complejas más verbosas | Otro runtime que desplegar |

> **Recomendación:** **FastAPI** si las agregaciones/analítica pesan; **Go** si
> quieres un stack de backend unificado y un único artefacto. Para el MVP, **FastAPI**
> acelera por las agregaciones y la documentación automática.

### ¿Por qué PostgreSQL y no NoSQL?
- Los datos son **estructurados y relacionales** (ofertas, fuentes, tecnologías).
- Las **agregaciones** (GROUP BY, ventanas temporales) son el corazón del producto →
  SQL brilla aquí.
- Soporta `JSONB` para campos flexibles (`tech_stack`) sin renunciar a lo relacional.

### ¿Cola de mensajes desde el principio?
- **No.** Empezar con inserción directa (`raw_jobs`). Introducir Redis/cola solo
  cuando el desacople aporte valor real. Evitar **complejidad prematura**.

## 📦 Librerías candidatas

### Go
- `net/http` — cliente HTTP
- `golang.org/x/time/rate` — rate limiting
- `goquery` — parsing de HTML (estilo jQuery)
- `colly` — framework de scraping (alternativa de más alto nivel)
- `chi` o `gin` — router HTTP para la API
- `robfig/cron` — scheduling
- `golang-migrate` — migrations

### Python
- `httpx` / `requests` — HTTP
- `re` (regex) — extracción inicial de tecnologías
- `spaCy` — NLP (fase avanzada, opcional)
- `psycopg` / `SQLAlchemy` — acceso a Postgres
- `FastAPI` + `uvicorn` — API
- `pandas` — análisis/agregaciones (opcional)

### Frontend
- `React` + `TypeScript` + `Vite`
- `Recharts` o `visx` — gráficas
- `TanStack Query` — fetching/caché de datos
- `Tailwind CSS` — estilos rápidos y consistentes

### Autenticación (ver [08](./08-cuentas-y-personalizacion.md))
- **OAuth GitHub** — login con un clic para devs (recomendado)
- `authlib` (FastAPI) o `goth` (Go) — flujo OAuth
- `bcrypt` / `argon2` — hashing de contraseñas (si hay email+password)
- Sesiones con cookie httpOnly (o JWT access+refresh)

## 🧪 Calidad
- **Go:** `go test` + `httptest` para mockear respuestas de fuentes.
- **Python:** `pytest`.
- **Frontend:** `vitest` + Testing Library.
- **Lint:** `golangci-lint`, `ruff`, `eslint`.
