// Package manfred implementa source.Scraper para Manfred (https://www.getmanfred.com).
//
// API pública sin auth: el listado /api/v2/public/offers?lang=ES da ofertas tech EN
// ESPAÑOL (con salario y % remoto) pero SIN el stack tecnológico. El detalle por
// oferta /api/v2/public/offers/{id}?lang=ES sí trae `techs`. Cuando withDetails está
// activo, enriquecemos cada oferta con esos techs (fetch concurrente y rate-limited).
package manfred

import (
	"context"
	"fmt"
	"strconv"
	"sync"
	"time"

	"github.com/x3no/tech-job-market-analyzer/scraper/internal/httpx"
	"github.com/x3no/tech-job-market-analyzer/scraper/internal/rawjob"
)

const (
	sourceName = "manfred"
	listURL    = "https://www.getmanfred.com/api/v2/public/offers?lang=ES"
	offerAPI   = "https://www.getmanfred.com/api/v2/public/offers/"
	offerWeb   = "https://www.getmanfred.com/es/job-offers/"

	detailConcurrency = 8 // peticiones de detalle en paralelo (cortesía)
)

// Source es la fuente Manfred.
type Source struct {
	client      *httpx.Client
	withDetails bool
}

// New crea la fuente Manfred. Si withDetails, enriquece cada oferta con sus techs.
func New(client *httpx.Client, withDetails bool) *Source {
	return &Source{client: client, withDetails: withDetails}
}

// Name implementa source.Scraper.
func (s *Source) Name() string { return sourceName }

// Fetch descarga el listado y (opcionalmente) enriquece con el detalle.
func (s *Source) Fetch(ctx context.Context) ([]rawjob.RawJob, error) {
	var offers []map[string]any
	if err := s.client.GetJSON(ctx, listURL, &offers); err != nil {
		return nil, fmt.Errorf("manfred: %w", err)
	}

	if s.withDetails {
		s.enrich(ctx, offers)
	}

	scrapedAt := time.Now().UTC()
	jobs := make([]rawjob.RawJob, 0, len(offers))
	for _, item := range offers {
		id := idString(item["id"])
		if id == "" {
			continue
		}
		slug, _ := item["slug"].(string)
		jobs = append(jobs, rawjob.RawJob{
			Source:     sourceName,
			ExternalID: id,
			URL:        offerWeb + id + "/" + slug,
			Payload:    item,
			ScrapedAt:  scrapedAt,
		})
	}
	return jobs, nil
}

// enrich añade a cada oferta la clave "techNames" con sus tecnologías, leídas del
// detalle. Concurrencia acotada; un fallo deja la oferta sin techs (no se aborta).
func (s *Source) enrich(ctx context.Context, offers []map[string]any) {
	sem := make(chan struct{}, detailConcurrency)
	var wg sync.WaitGroup

	for _, off := range offers {
		id := idString(off["id"])
		if id == "" {
			continue
		}
		wg.Add(1)
		sem <- struct{}{}
		go func(off map[string]any, id string) {
			defer wg.Done()
			defer func() { <-sem }()

			var detail map[string]any
			if err := s.client.GetJSON(ctx, offerAPI+id+"?lang=ES", &detail); err != nil {
				return // mantener la oferta sin techs
			}
			off["techNames"] = techNames(detail)
		}(off, id)
	}
	wg.Wait()
}

// techNames extrae los nombres de detail["techs"][].name.
func techNames(detail map[string]any) []string {
	raw, ok := detail["techs"].([]any)
	if !ok {
		return nil
	}
	names := make([]string, 0, len(raw))
	for _, t := range raw {
		if m, ok := t.(map[string]any); ok {
			if n, ok := m["name"].(string); ok && n != "" {
				names = append(names, n)
			}
		}
	}
	return names
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
