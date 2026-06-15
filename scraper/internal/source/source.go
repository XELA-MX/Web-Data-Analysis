// Package source define el contrato de una fuente de ofertas (interface Scraper)
// y un Runner que ejecuta varias fuentes en paralelo con un worker pool,
// aislando fallos: una fuente caída no tumba al resto.
// Ver documentación/V1/02-arquitectura.md.
package source

import (
	"context"
	"log/slog"
	"sync"

	"github.com/x3no/tech-job-market-analyzer/scraper/internal/rawjob"
)

// Scraper es una fuente de ofertas. Solo recoge: no interpreta ni limpia.
type Scraper interface {
	// Name identifica la fuente (ej. "remoteok").
	Name() string
	// Fetch obtiene las ofertas crudas, respetando el context (timeout/cancelación).
	Fetch(ctx context.Context) ([]rawjob.RawJob, error)
}

// Run ejecuta todas las fuentes concurrentemente con un pool de `workers`
// goroutines y devuelve todas las ofertas recogidas. Los fallos de una fuente
// se registran y se omiten (no abortan al resto) → tolerancia a fallos.
func Run(ctx context.Context, scrapers []Scraper, workers int) []rawjob.RawJob {
	if workers < 1 {
		workers = 1
	}

	type result struct {
		name string
		jobs []rawjob.RawJob
		err  error
	}

	tasks := make(chan Scraper)
	results := make(chan result)

	var wg sync.WaitGroup
	for i := 0; i < workers; i++ {
		wg.Add(1)
		go func() {
			defer wg.Done()
			for s := range tasks {
				jobs, err := s.Fetch(ctx)
				results <- result{name: s.Name(), jobs: jobs, err: err}
			}
		}()
	}

	// Alimenta el pool y cierra el canal cuando no quedan tareas.
	go func() {
		for _, s := range scrapers {
			tasks <- s
		}
		close(tasks)
	}()

	// Cierra results cuando todos los workers terminan.
	go func() {
		wg.Wait()
		close(results)
	}()

	var all []rawjob.RawJob
	ok, failed := 0, 0
	for r := range results {
		if r.err != nil {
			slog.Error("fuente falló", "source", r.name, "err", r.err)
			failed++
			continue
		}
		slog.Info("fuente ok", "source", r.name, "jobs", len(r.jobs))
		ok++
		all = append(all, r.jobs...)
	}
	slog.Info("resumen fuentes", "ok", ok, "fallidas", failed)
	return all
}
