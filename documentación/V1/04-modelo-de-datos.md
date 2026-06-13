# 04 · Modelo de datos

## 🗄️ Esquema general

Tres tablas centrales: `raw_jobs` (crudo), `jobs` (limpio) y `sources` (catálogo de
fuentes). Para tendencias se aprovecha el campo temporal de `jobs`.

## 📋 Tabla `sources`

Catálogo de fuentes de datos.

| Columna | Tipo | Notas |
|---------|------|-------|
| `id` | SERIAL PK | |
| `name` | TEXT | "RemoteOK", "We Work Remotely"... |
| `base_url` | TEXT | |
| `enabled` | BOOLEAN | activar/desactivar fuente |
| `rate_limit_per_min` | INT | cortesía por fuente |
| `created_at` | TIMESTAMPTZ | |

## 📥 Tabla `raw_jobs`

Datos crudos tal cual llegan del scraper (antes de procesar). Permite reprocesar sin
volver a scrapear.

| Columna | Tipo | Notas |
|---------|------|-------|
| `id` | SERIAL PK | |
| `source_id` | INT FK → sources | |
| `external_id` | TEXT | id en la fuente origen |
| `raw_payload` | JSONB | respuesta original completa |
| `url` | TEXT | enlace a la oferta |
| `scraped_at` | TIMESTAMPTZ | |
| `processed` | BOOLEAN | ¿ya pasó por el procesador? |

**Índices:** `(source_id, external_id)` único; `processed` parcial para la cola de trabajo.

## ✅ Tabla `jobs`

Ofertas limpias y enriquecidas. Es la que consume la API.

| Columna | Tipo | Notas |
|---------|------|-------|
| `id` | SERIAL PK | |
| `source_id` | INT FK → sources | |
| `external_id` | TEXT | para idempotencia |
| `fingerprint` | TEXT | hash para deduplicación cross-source |
| `title` | TEXT | |
| `company` | TEXT | |
| `location` | TEXT | texto original |
| `country` | TEXT | normalizado |
| `remote` | BOOLEAN | |
| `salary_min` | INT NULL | normalizado anual |
| `salary_max` | INT NULL | normalizado anual |
| `currency` | TEXT NULL | ISO 4217 (EUR, USD...) |
| `tech_stack` | JSONB | array de tecnologías, ej. `["go","react","postgres"]` |
| `seniority` | TEXT NULL | `junior` / `mid` / `senior` |
| `description` | TEXT | |
| `url` | TEXT | |
| `posted_at` | TIMESTAMPTZ NULL | fecha de publicación |
| `scraped_at` | TIMESTAMPTZ | cuándo lo capturamos |
| `first_seen_at` | TIMESTAMPTZ | para histórico/tendencias |

### Índices recomendados
- `UNIQUE (source_id, external_id)` → idempotencia.
- `INDEX (fingerprint)` → deduplicación.
- `INDEX (remote)`, `INDEX (seniority)`, `INDEX (country)` → filtros.
- `GIN (tech_stack)` → búsquedas por tecnología dentro del JSONB.
- `INDEX (posted_at)` / `(first_seen_at)` → series temporales.

## 🔑 Deduplicación: el `fingerprint`

Una misma oferta puede aparecer en varias fuentes. Estrategia:

1. Normalizar `title` + `company` (lowercase, sin acentos, sin extras).
2. `fingerprint = sha1(normalized_title + "|" + normalized_company)`.
3. Al insertar, si ya existe un `fingerprint` reciente → marcar como duplicado o
   fusionar (guardar qué fuentes la listan).

> Para un matching más fino se puede usar similitud difusa (Levenshtein / trigramas
> con la extensión `pg_trgm`). Empezar simple con hash exacto.

## 📈 Tablas / vistas para tendencias

Para "React subió 12% este mes" hay dos opciones:

- **A (simple):** calcular agregaciones on-the-fly desde `jobs` filtrando por
  `first_seen_at`. Suficiente para el MVP.
- **B (escalable):** tabla `tech_daily_stats (date, tech, job_count, avg_salary)`
  rellenada por un job diario. Mejor rendimiento para histórico largo.

> Empezar con A; migrar a B si las consultas se vuelven lentas.

## 👥 Tablas de usuarios y personalización

> Las ofertas (`jobs`) son **globales y compartidas**. Lo de abajo es **por usuario**.
> Detalle de la funcionalidad en [08 · Cuentas y personalización](./08-cuentas-y-personalizacion.md).

### Tabla `users`

| Columna | Tipo | Notas |
|---------|------|-------|
| `id` | SERIAL PK | |
| `email` | TEXT UNIQUE | |
| `provider` | TEXT | `github` / `email` |
| `provider_id` | TEXT NULL | id externo si es OAuth |
| `password_hash` | TEXT NULL | solo si provider = email (bcrypt/argon2) |
| `display_name` | TEXT | |
| `created_at` | TIMESTAMPTZ | |
| `last_login_at` | TIMESTAMPTZ | |

### Tabla `user_preferences`

| Columna | Tipo | Notas |
|---------|------|-------|
| `user_id` | INT PK FK → users | 1:1 con el usuario |
| `role` | TEXT NULL | frontend / backend / fullstack / data / devops... |
| `tech_stack` | JSONB | tecnologías de interés, ej. `["go","react"]` |
| `seniority` | TEXT NULL | junior / mid / senior |
| `work_mode` | TEXT NULL | remote / hybrid / onsite |
| `country` | TEXT NULL | |
| `salary_target` | INT NULL | |
| `updated_at` | TIMESTAMPTZ | |

### Tabla `saved_jobs`

| Columna | Tipo | Notas |
|---------|------|-------|
| `id` | SERIAL PK | |
| `user_id` | INT FK → users | |
| `job_id` | INT FK → jobs | |
| `status` | TEXT | `saved` / `dismissed` / `applied` |
| `created_at` | TIMESTAMPTZ | |

**Índices:** `UNIQUE (user_id, job_id)`; `INDEX (user_id, status)`.

### Tabla `alerts` (extensión)

| Columna | Tipo | Notas |
|---------|------|-------|
| `id` | SERIAL PK | |
| `user_id` | INT FK → users | |
| `criteria` | JSONB | filtros guardados (stack, remoto, salario...) |
| `channel` | TEXT | `email` / `telegram` |
| `enabled` | BOOLEAN | |
| `last_notified_at` | TIMESTAMPTZ NULL | |

### 🔒 Aislamiento por usuario
Toda query sobre `user_preferences`, `saved_jobs` y `alerts` **debe filtrar por el
`user_id` autenticado**. Validar siempre la propiedad del recurso antes de leer/escribir.

### 🎯 Scoring de afinidad (personalización)
El ranking del feed se calcula al servir, no se persiste (MVP):
- +N por cada tecnología del `user_preferences.tech_stack` presente en `jobs.tech_stack`.
- bonus si `seniority` y `work_mode` coinciden.
- (futuro) reemplazable por un modelo ML/embeddings.

## 🧬 Tipo `RawJob` (Go) → `Job` (procesado)

```go
// Lo que produce el scraper — crudo, sin interpretar.
type RawJob struct {
    Source      string
    ExternalID  string
    URL         string
    Payload     map[string]any
    ScrapedAt   time.Time
}
```

```python
# Lo que produce el procesador — limpio y enriquecido.
@dataclass
class Job:
    source: str
    external_id: str
    fingerprint: str
    title: str
    company: str
    location: str
    country: str | None
    remote: bool
    salary_min: int | None
    salary_max: int | None
    currency: str | None
    tech_stack: list[str]
    seniority: str | None
    description: str
    url: str
    posted_at: datetime | None
    scraped_at: datetime
```
