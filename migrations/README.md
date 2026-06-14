# Migrations

Las migrations `.sql` versionadas son la **fuente de verdad** del esquema de la base
de datos. Convención de nombres estilo [`golang-migrate`](https://github.com/golang-migrate/migrate):

```
NNNN_nombre.up.sql    → aplica el cambio
NNNN_nombre.down.sql  → lo revierte
```

## Cómo se aplican

En esta máquina **`psql` no está instalado**, así que durante el desarrollo los
cambios de esquema se aplican **a través del MCP de Postgres** (tiene escritura),
pero **siempre dejando la migration `.sql` versionada** aquí como fuente de verdad.
No crear tablas ad-hoc sin su migration correspondiente.

Cuando el scraper en Go esté en marcha (Fase 1+), se puede automatizar con
`golang-migrate`:

```bash
migrate -path ./migrations -database "$DATABASE_URI" up
migrate -path ./migrations -database "$DATABASE_URI" down 1
```

## Historial

| Versión | Descripción |
|---------|-------------|
| `0001`  | Esquema inicial: `sources`, `raw_jobs`, `jobs` (núcleo del pipeline). |
| `0002`  | `UNIQUE (name)` en `sources` (upsert idempotente de la fuente desde el scraper). |
| `0003`  | `jobs.is_duplicate` + índice parcial canónico (deduplicación cross-source). |
| `0004`  | Cuentas: `users`, `user_preferences`, `saved_jobs`, `sessions` (Fase 4.5). |

> Las tablas de usuarios/personalización llegaron en `0004` (Fase 4.5). `alerts` queda
> como extensión futura.
