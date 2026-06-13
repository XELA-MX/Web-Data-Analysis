# 02 · Arquitectura

## 🏗️ Vista general

El sistema sigue un patrón **pipeline de datos** con componentes desacoplados.
La idea central: **el scraper es "tonto" (solo recoge), el procesador es "inteligente"
(limpia y enriquece)**. Esto mantiene cada pieza simple y testeable.

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐     ┌──────────────┐
│  Scraper    │────▶│  Cola/Buffer │────▶│  Procesador │────▶│  PostgreSQL  │
│  (Go)       │     │  (channels   │     │  (Python:   │     │  (datos      │
│ concurrente │     │   o Redis)   │     │  NLP/regex) │     │  limpios)    │
└─────────────┘     └──────────────┘     └─────────────┘     └──────┬───────┘
       ▲                                                            │
       │ scheduler (cron)                                           ▼
       │ respeta robots.txt + rate limit                    ┌──────────────┐
       │                                                    │     API      │
       └────────────────────────────────────────────────── │  (REST)      │
                                                            └──────┬───────┘
                                                                   │
                                                                   ▼
                                                            ┌──────────────┐
                                                            │ Dashboard    │
                                                            │ React + TS   │
                                                            └──────────────┘
```

## 🧱 Componentes

### 1. Scraper (Go)
- **Responsabilidad:** obtener datos crudos de cada fuente. Nada más.
- **Patrón:** una interfaz `Scraper` por fuente.
  ```go
  type Scraper interface {
      Name() string
      Fetch(ctx context.Context) ([]RawJob, error)
  }
  ```
- **Concurrencia:** worker pool con goroutines + canal de trabajos. Límite de
  workers configurable.
- **Cortesía:** `golang.org/x/time/rate` para rate limiting por dominio; `User-Agent`
  honesto; chequeo de `robots.txt`.
- **Resiliencia:** reintentos con backoff exponencial; `context` para cancelación/timeout.
- **Salida:** `RawJob` (datos sin procesar) → cola/buffer.

### 2. Cola / Buffer (opcional al inicio)
- **MVP:** inserción directa en una tabla `raw_jobs`. Simple.
- **Evolución:** Redis o channels para desacoplar scraper y procesador.
- _Decisión: empezar simple, introducir cola solo cuando aporte valor._

### 3. Procesador (Python)
- **Responsabilidad:** limpiar y enriquecer.
  - Extraer `tech_stack` (diccionario de tecnologías + regex; luego spaCy si interesa).
  - Normalizar salario a `(min, max, currency)`.
  - Inferir seniority.
  - Detectar remoto.
  - Deduplicar.
- **Por qué Python:** ecosistema de NLP/datos más cómodo que Go para esta parte.
- **Salida:** `Job` limpio → PostgreSQL.

### 4. PostgreSQL
- Almacena ofertas limpias + histórico para tendencias.
- Migrations versionadas (`golang-migrate` o `alembic`).
- Ver [04 · Modelo de datos](./04-modelo-de-datos.md).

### 5. API REST
- Endpoints de búsqueda, agregaciones y series temporales.
- **Opción A:** Go (`chi`/`gin`) → un solo lenguaje de backend.
- **Opción B:** Python (FastAPI) → comparte código con el procesador.
- _Recomendación: FastAPI si las agregaciones son complejas; Go si priorizas un único binario._

### 6. Dashboard (React + TypeScript)
- Visualizaciones con Recharts/visx.
- Buscador con filtros.
- Vista de tendencias temporales.
- **Feed personalizado** según las preferencias del usuario autenticado.
- Onboarding (al registrarse) y pantalla de ajustes de preferencias.

### 6.5. Autenticación y personalización
- **Auth:** GitHub OAuth y/o email+contraseña. Sesiones con cookie httpOnly (o JWT).
- **Datos por usuario:** preferencias, ofertas guardadas/descartadas, alertas — ligados
  a `user_id`, aislados entre cuentas.
- **Personalización:** la API filtra y ordena las ofertas (globales) según el perfil del
  usuario. El scoring de afinidad se calcula al servir (no se persiste en el MVP).
- Detalle en [08 · Cuentas y personalización](./08-cuentas-y-personalizacion.md).

### 7. Scheduler
- Dispara el scraping cada X horas (`robfig/cron` en Go, o cron del sistema/PaaS).

## 🔄 Flujo de datos (end-to-end)

1. El **scheduler** dispara el **scraper**.
2. El scraper consulta cada fuente (en paralelo, con rate limit) → `RawJob`.
3. Los `RawJob` se guardan crudos (tabla `raw_jobs` o cola).
4. El **procesador** lee los crudos → limpia, enriquece, deduplica → `Job`.
5. Los `Job` se persisten en Postgres (con timestamp para histórico).
6. La **API** sirve consultas y agregaciones.
7. El **dashboard** consume la API y muestra las visualizaciones.

## 🧭 Principios de diseño

- **Separación de responsabilidades:** recoger ≠ procesar ≠ servir.
- **Empezar simple:** sin cola, sin microservicios prematuros. Introducir complejidad
  solo cuando se justifique.
- **Tolerancia a fallos:** una fuente caída no tumba el pipeline.
- **Idempotencia:** re-scrapear no debe duplicar datos (clave en la deduplicación).
- **Observabilidad:** logs estructurados desde el día 1.

## 🗺️ Diagrama de despliegue (objetivo)

```
┌────────────────── PaaS (Fly.io / Railway / Render) ──────────────────┐
│                                                                       │
│  [Scheduler+Scraper Go]   [Procesador Python]   [API]   [Postgres]    │
│                                                          (managed)    │
└───────────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
                        [Dashboard estático]
                        (Vercel / Netlify / mismo PaaS)
```
