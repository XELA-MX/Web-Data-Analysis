// Package pgstore persiste ofertas crudas en Postgres (tabla raw_jobs).
// Es el sink "de verdad" a partir de la Fase 2; jobs.json queda como salida
// opcional para inspección rápida.
//
// Idempotencia: las inserciones usan ON CONFLICT (source_id, external_id) DO NOTHING,
// de modo que re-scrapear no duplica filas (ver documentación/V1/02-arquitectura.md).
package pgstore

import (
	"context"
	"encoding/json"
	"fmt"

	"github.com/jackc/pgx/v5"
	"github.com/jackc/pgx/v5/pgxpool"

	"github.com/x3no/tech-job-market-analyzer/scraper/internal/rawjob"
)

// Store envuelve un pool de conexiones a Postgres.
type Store struct {
	pool *pgxpool.Pool
}

// Open abre un pool contra el DSN dado (ej. la DATABASE_URI del entorno).
func Open(ctx context.Context, dsn string) (*Store, error) {
	pool, err := pgxpool.New(ctx, dsn)
	if err != nil {
		return nil, fmt.Errorf("abriendo pool: %w", err)
	}
	if err := pool.Ping(ctx); err != nil {
		pool.Close()
		return nil, fmt.Errorf("ping a la DB: %w", err)
	}
	return &Store{pool: pool}, nil
}

// Close cierra el pool.
func (s *Store) Close() { s.pool.Close() }

// UpsertSource inserta o actualiza la fuente por nombre y devuelve su id.
func (s *Store) UpsertSource(ctx context.Context, name, baseURL string, rateLimitPerMin int) (int, error) {
	var id int
	err := s.pool.QueryRow(ctx, `
		INSERT INTO sources (name, base_url, rate_limit_per_min)
		VALUES ($1, $2, $3)
		ON CONFLICT (name) DO UPDATE
			SET base_url = EXCLUDED.base_url,
			    rate_limit_per_min = EXCLUDED.rate_limit_per_min
		RETURNING id`,
		name, baseURL, rateLimitPerMin,
	).Scan(&id)
	if err != nil {
		return 0, fmt.Errorf("upsert source %q: %w", name, err)
	}
	return id, nil
}

// InsertRawJobs inserta las ofertas de una fuente, omitiendo duplicados
// (source_id, external_id). Devuelve cuántas filas nuevas se insertaron.
func (s *Store) InsertRawJobs(ctx context.Context, sourceID int, jobs []rawjob.RawJob) (int, error) {
	batch := &pgx.Batch{}
	for _, j := range jobs {
		payload, err := json.Marshal(j.Payload)
		if err != nil {
			return 0, fmt.Errorf("serializando payload de %s: %w", j.ExternalID, err)
		}
		batch.Queue(`
			INSERT INTO raw_jobs (source_id, external_id, raw_payload, url, scraped_at, processed)
			VALUES ($1, $2, $3::jsonb, $4, $5, FALSE)
			ON CONFLICT (source_id, external_id) DO NOTHING`,
			sourceID, j.ExternalID, string(payload), nullable(j.URL), j.ScrapedAt,
		)
	}

	br := s.pool.SendBatch(ctx, batch)
	defer br.Close()

	inserted := 0
	for range jobs {
		ct, err := br.Exec()
		if err != nil {
			return inserted, fmt.Errorf("insertando raw_jobs: %w", err)
		}
		inserted += int(ct.RowsAffected())
	}
	return inserted, nil
}

// nullable convierte "" en NULL para no guardar cadenas vacías.
func nullable(s string) any {
	if s == "" {
		return nil
	}
	return s
}
