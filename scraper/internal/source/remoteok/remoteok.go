// Package remoteok implementa source.Scraper para RemoteOK (https://remoteok.com).
//
// RemoteOK expone una API JSON pública sin auth en /api: un array donde el
// PRIMER elemento es metadata legal (sin "id") y el resto son ofertas.
//
// ⚠️ Términos de RemoteOK: al usar su API hay que enlazar de vuelta a la oferta
// en su web y mencionar "Remote OK" como fuente, o suspenden el acceso. Guardamos
// el payload original (incluida la url) para poder cumplir la atribución en el frontend.
package remoteok

import (
	"context"
	"fmt"
	"time"

	"github.com/x3no/tech-job-market-analyzer/scraper/internal/httpx"
	"github.com/x3no/tech-job-market-analyzer/scraper/internal/rawjob"
)

const (
	sourceName = "remoteok"
	apiURL     = "https://remoteok.com/api"
)

// Source es la fuente RemoteOK.
type Source struct {
	client *httpx.Client
}

// New crea la fuente RemoteOK con el cliente HTTP dado.
func New(client *httpx.Client) *Source {
	return &Source{client: client}
}

// Name implementa source.Scraper.
func (s *Source) Name() string { return sourceName }

// Fetch descarga el endpoint /api y lo convierte en RawJob, descartando el
// elemento de metadata legal (el que no tiene "id").
func (s *Source) Fetch(ctx context.Context) ([]rawjob.RawJob, error) {
	var raw []map[string]any
	if err := s.client.GetJSON(ctx, apiURL, &raw); err != nil {
		return nil, fmt.Errorf("remoteok: %w", err)
	}

	scrapedAt := time.Now().UTC()
	jobs := make([]rawjob.RawJob, 0, len(raw))
	for _, item := range raw {
		// El primer elemento es metadata legal: sin "id" → lo saltamos.
		id, ok := item["id"].(string)
		if !ok || id == "" {
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
