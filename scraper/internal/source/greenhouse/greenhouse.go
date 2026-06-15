// Package greenhouse implementa source.Scraper para boards de empresa en Greenhouse
// (https://boards-api.greenhouse.io). Son publicaciones DIRECTAS del empleador →
// muy poco solape con los agregadores remotos (menos duplicados) y datos limpios.
//
// El listado no trae departamentos, así que filtramos por título "tech" para no
// arrastrar roles de ventas/marketing/etc. Recorre una lista curada de empresas;
// si un board falla (404), se omite (aislamiento de fallos).
package greenhouse

import (
	"context"
	"fmt"
	"regexp"
	"strconv"
	"sync"
	"time"

	"github.com/x3no/tech-job-market-analyzer/scraper/internal/httpx"
	"github.com/x3no/tech-job-market-analyzer/scraper/internal/rawjob"
)

const (
	sourceName  = "greenhouse"
	boardURL    = "https://boards-api.greenhouse.io/v1/boards/%s/jobs"
	concurrency = 6
)

// Empresas (tokens de board) curadas, con foco tech. Las que fallen se omiten.
var companies = []string{
	"gitlab", "stripe", "databricks", "airbnb", "coinbase",
	"brex", "ramp", "figma", "discord", "gusto", "robinhood", "doordash",
}

// Solo ofertas cuyo título parezca tech.
var techTitle = regexp.MustCompile(
	`(?i)\b(engineer|developer|programmer|software|frontend|front-end|backend|back-end|` +
		`full[\s-]?stack|data|devops|sre|qa|tester|machine learning|ml|ai|architect|mobile|` +
		`ios|android|cloud|platform|security|infrastructure|web|scientist|analyst)\b`,
)

// Source es la fuente Greenhouse (multi-empresa).
type Source struct {
	client *httpx.Client
}

// New crea la fuente Greenhouse.
func New(client *httpx.Client) *Source { return &Source{client: client} }

// Name implementa source.Scraper.
func (s *Source) Name() string { return sourceName }

// Fetch recorre los boards en paralelo y junta las ofertas tech.
func (s *Source) Fetch(ctx context.Context) ([]rawjob.RawJob, error) {
	scrapedAt := time.Now().UTC()
	sem := make(chan struct{}, concurrency)
	var wg sync.WaitGroup
	var mu sync.Mutex
	var all []rawjob.RawJob

	for _, token := range companies {
		wg.Add(1)
		sem <- struct{}{}
		go func(token string) {
			defer wg.Done()
			defer func() { <-sem }()

			var resp struct {
				Jobs []map[string]any `json:"jobs"`
			}
			if err := s.client.GetJSON(ctx, fmt.Sprintf(boardURL, token), &resp); err != nil {
				return // board inexistente/caído → se omite
			}

			local := make([]rawjob.RawJob, 0, len(resp.Jobs))
			for _, item := range resp.Jobs {
				title, _ := item["title"].(string)
				if title == "" || !techTitle.MatchString(title) {
					continue
				}
				id := idString(item["id"])
				if id == "" {
					continue
				}
				item["_board"] = token
				url, _ := item["absolute_url"].(string)
				local = append(local, rawjob.RawJob{
					Source:     sourceName,
					ExternalID: token + ":" + id, // id único por empresa
					URL:        url,
					Payload:    item,
					ScrapedAt:  scrapedAt,
				})
			}
			mu.Lock()
			all = append(all, local...)
			mu.Unlock()
		}(token)
	}
	wg.Wait()
	return all, nil
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
