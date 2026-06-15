#!/usr/bin/env bash
# Pipeline completo de datos: scrape -> procesado (+ snapshot diario de tendencias).
# Pensado para ejecutarse por cron / scheduler del PaaS (Fase 5 · Automatización).
#
# Uso manual:   scripts/refresh.sh
# Cron (cada 6h, con log):
#   0 */6 * * * /ruta/al/repo/scripts/refresh.sh >> /tmp/jobmarket-refresh.log 2>&1
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# go y el venv pueden no estar en el PATH mínimo de cron.
export PATH="/snap/bin:/usr/local/go/bin:${HOME}/go/bin:${PATH}"

# Carga DATABASE_URI (y demás) del .env para que el scraper Go la tenga en cron.
set -a
[ -f "$ROOT/.env" ] && . "$ROOT/.env"
set +a

echo "[$(date -Is)] === scrape ==="
( cd "$ROOT/scraper" && go run ./cmd/scraper -sink=postgres -manfred-details="${MANFRED_DETAILS:-true}" )

echo "[$(date -Is)] === procesado + snapshot ==="
( cd "$ROOT/processor" && ./.venv/bin/python -m processor )

echo "[$(date -Is)] === hecho ==="
