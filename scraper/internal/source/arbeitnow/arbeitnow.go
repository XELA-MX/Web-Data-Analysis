// Package arbeitnow implementa source.Scraper para Arbeitnow
// (https://www.arbeitnow.com). API JSON pública sin auth en /api/job-board-api:
// las ofertas vienen bajo la clave "data". Aporta empleos con foco europeo y un
// campo `remote` booleano real.
package arbeitnow

import (
	"context"
	"fmt"
	"time"

	"github.com/x3no/tech-job-market-analyzer/scraper/internal/httpx"
	"github.com/x3no/tech-job-market-analyzer/scraper/internal/rawjob"
)

const (
	sourceName = "arbeitnow"
	apiURL     = "https://www.arbeitnow.com/api/job-board-api"
)

// Source es la fuente Arbeitnow.
type Source struct {
	client *httpx.Client
}

// New crea la fuente Arbeitnow.
func New(client *httpx.Client) *Source { return &Source{client: client} }

// Name implementa source.Scraper.
func (s *Source) Name() string { return sourceName }

// Fetch descarga las ofertas y las mapea a RawJob. El id estable es el "slug".
func (s *Source) Fetch(ctx context.Context) ([]rawjob.RawJob, error) {
	var resp struct {
		Data []map[string]any `json:"data"`
	}
	if err := s.client.GetJSON(ctx, apiURL, &resp); err != nil {
		return nil, fmt.Errorf("arbeitnow: %w", err)
	}

	scrapedAt := time.Now().UTC()
	jobs := make([]rawjob.RawJob, 0, len(resp.Data))
	for _, item := range resp.Data {
		slug, _ := item["slug"].(string)
		if slug == "" {
			continue
		}
		url, _ := item["url"].(string)
		jobs = append(jobs, rawjob.RawJob{
			Source:     sourceName,
			ExternalID: slug,
			URL:        url,
			Payload:    item,
			ScrapedAt:  scrapedAt,
		})
	}
	return jobs, nil
}
