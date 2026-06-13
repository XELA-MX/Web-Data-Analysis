# scraper (Go)

Recoge ofertas crudas de fuentes públicas y las deja como `RawJob`. El scraper es
**"tonto"**: solo recoge, no interpreta (eso lo hace `/processor`).

- **Concurrencia:** worker pool con goroutines que corre las fuentes en paralelo y
  **aísla fallos** (una fuente caída no tumba al resto).
- **Cortesía:** rate limiting (`golang.org/x/time/rate`), `User-Agent` honesto, timeouts.
- **Resiliencia:** reintentos con backoff exponencial; `context` para timeout/cancelación.
- **Observabilidad:** logs estructurados con `log/slog`.

Interfaz central (una implementación por fuente):

```go
type Scraper interface {
    Name() string
    Fetch(ctx context.Context) ([]rawjob.RawJob, error)
}
```

## Estructura

```
cmd/scraper/main.go              entrypoint: orquesta y escribe jobs.json
internal/rawjob/                 struct RawJob (ver documentación/V1/04-modelo-de-datos.md)
internal/httpx/                  cliente HTTP: UA + rate limit + retry/backoff + timeout
internal/source/                 interface Scraper + Runner (worker pool)
internal/source/remoteok/        fuente RemoteOK
internal/store/                  escribe []RawJob → jobs.json (escritura atómica)
```

## Uso

```bash
cd scraper
go run ./cmd/scraper                       # escribe jobs.json
go run ./cmd/scraper -out=/tmp/jobs.json   # otra ruta
go run ./cmd/scraper -rps=1 -workers=4 -timeout=60s
go build -o bin/scraper ./cmd/scraper      # binario
```

Flags: `-out` (salida), `-workers` (fuentes en paralelo), `-rps` (peticiones/seg de
cortesía), `-timeout` (límite global).

## Fuentes

Cada fuente vive en `internal/source/<nombre>/` e implementa `Scraper`. Cada una usa
su propio cliente HTTP → **rate limiting independiente por dominio**.

| Fuente | Endpoint | Notas |
|--------|----------|-------|
| **RemoteOK** | `https://remoteok.com/api` | JSON sin auth; array (1er elemento = metadata legal, se descarta). ⚠️ **Atribución** obligatoria. |
| **Remotive** | `https://remotive.com/api/remote-jobs` | JSON sin auth; ofertas bajo `jobs`. ⚠️ **Atribución** (ver `0-legal-notice`). |
| **Arbeitnow** | `https://www.arbeitnow.com/api/job-board-api` | JSON sin auth; ofertas bajo `data`. Foco europeo; campo `remote` real. |

> Fuentes a evitar (ToS/anti-bot): LinkedIn, Indeed, Glassdoor. Ver
> `documentación/V1/06-fuentes-de-datos.md` y `07-etica-y-legalidad.md`.

## Estado

- ✅ **Fase 1 hecha:** scraper de RemoteOK → `jobs.json`.
- ✅ **Fase 2 hecha:** sink a Postgres (`raw_jobs`, idempotente) vía pgx.
- ✅ **Fase 3 hecha:** 3 fuentes en paralelo + aislamiento de fallos (una fuente caída
  no tumba al resto, ni al scrapear ni al persistir). Dedup por `fingerprint` la hace
  el procesador.

> El módulo es `github.com/x3no/tech-job-market-analyzer/scraper`. Si tu repo/usuario
> de GitHub es otro, cámbialo en `go.mod` (y en los imports) — es la única dependencia
> del nombre.
