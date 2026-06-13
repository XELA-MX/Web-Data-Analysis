// Package remotive implementa source.Scraper para Remotive (https://remotive.com).
//
// API JSON pública sin auth en /api/remote-jobs: un objeto con las ofertas bajo la
// clave "jobs" (más metadatos como "0-legal-notice").
//
// ⚠️ Como RemoteOK, Remotive pide atribución/enlace de vuelta al usar su API
// (ver el campo "0-legal-notice" de la respuesta). Guardamos el payload con su url.
package remotive

import (
	"context"
	"fmt"
	"strconv"
	"time"

	"github.com/x3no/tech-job-market-analyzer/scraper/internal/httpx"
	"github.com/x3no/tech-job-market-analyzer/scraper/internal/rawjob"
)

const (
	sourceName = "remotive"
	apiURL     = "https://remotive.com/api/remote-jobs"
)

// Source es la fuente Remotive.
type Source struct {
	client *httpx.Client
}

// New crea la fuente Remotive.
func New(client *httpx.Client) *Source { return &Source{client: client} }

// Name implementa source.Scraper.
func (s *Source) Name() string { return sourceName }

// Fetch descarga las ofertas y las mapea a RawJob.
func (s *Source) Fetch(ctx context.Context) ([]rawjob.RawJob, error) {
	var resp struct {
		Jobs []map[string]any `json:"jobs"`
	}
	if err := s.client.GetJSON(ctx, apiURL, &resp); err != nil {
		return nil, fmt.Errorf("remotive: %w", err)
	}

	scrapedAt := time.Now().UTC()
	jobs := make([]rawjob.RawJob, 0, len(resp.Jobs))
	for _, item := range resp.Jobs {
		id := idString(item["id"])
		if id == "" {
			continue
		}
		url, _ := item["url"].(string)
		jobs = append(jobs, rawjob.RawJob{
			Source:     sourceName,
			ExternalID: id,
			URL:        url,
			Payload:    item,
			ScrapedAt:  scrapedAt,
		})
	}
	return jobs, nil
}

// idString convierte el id (numérico en JSON) a string estable.
func idString(v any) string {
	switch n := v.(type) {
	case string:
		return n
	case float64:
		return strconv.FormatFloat(n, 'f', -1, 64)
	default:
		return ""
	}
}
