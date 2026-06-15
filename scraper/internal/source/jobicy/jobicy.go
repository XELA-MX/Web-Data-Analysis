// Package jobicy implementa source.Scraper para Jobicy (https://jobicy.com).
// API JSON pública sin auth: ofertas remotas tech bajo la clave "jobs".
// ⚠️ Jobicy pide atribución y enlazar a la oferta original (lo guardamos en la url).
package jobicy

import (
	"context"
	"fmt"
	"strconv"
	"time"

	"github.com/x3no/tech-job-market-analyzer/scraper/internal/httpx"
	"github.com/x3no/tech-job-market-analyzer/scraper/internal/rawjob"
)

const (
	sourceName = "jobicy"
	apiURL     = "https://jobicy.com/api/v2/remote-jobs?count=100"
)

// Source es la fuente Jobicy.
type Source struct {
	client *httpx.Client
}

// New crea la fuente Jobicy.
func New(client *httpx.Client) *Source { return &Source{client: client} }

// Name implementa source.Scraper.
func (s *Source) Name() string { return sourceName }

// Fetch descarga las ofertas remotas y las mapea a RawJob.
func (s *Source) Fetch(ctx context.Context) ([]rawjob.RawJob, error) {
	var resp struct {
		Jobs []map[string]any `json:"jobs"`
	}
	if err := s.client.GetJSON(ctx, apiURL, &resp); err != nil {
		return nil, fmt.Errorf("jobicy: %w", err)
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
