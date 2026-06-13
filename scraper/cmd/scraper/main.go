// Comando scraper: orquesta las fuentes y vuelca las ofertas crudas a jobs.json.
//
// Uso:
//
//	go run ./cmd/scraper            # escribe jobs.json
//	go run ./cmd/scraper -out=/tmp/jobs.json -workers=4
package main

import (
	"context"
	"log/slog"
	"os"
	"os/signal"
	"time"

	"flag"

	"github.com/x3no/tech-job-market-analyzer/scraper/internal/httpx"
	"github.com/x3no/tech-job-market-analyzer/scraper/internal/source"
	"github.com/x3no/tech-job-market-analyzer/scraper/internal/source/remoteok"
	"github.com/x3no/tech-job-market-analyzer/scraper/internal/store"
)

// User-Agent honesto: identifica el proyecto y deja una vía de contacto.
const userAgent = "tech-job-market-analyzer/0.1 (+https://github.com/x3no/tech-job-market-analyzer; portfolio project)"

func main() {
	out := flag.String("out", "jobs.json", "ruta del fichero de salida")
	workers := flag.Int("workers", 4, "número de fuentes a scrapear en paralelo")
	rps := flag.Float64("rps", 1.0, "peticiones por segundo (cortesía; RemoteOK pide crawl-delay 1)")
	timeout := flag.Duration("timeout", 60*time.Second, "timeout global de la ejecución")
	flag.Parse()

	slog.SetDefault(slog.New(slog.NewTextHandler(os.Stderr, &slog.HandlerOptions{Level: slog.LevelInfo})))

	// Context con timeout global + cancelación por Ctrl-C.
	ctx, cancel := signal.NotifyContext(context.Background(), os.Interrupt)
	defer cancel()
	ctx, cancelTimeout := context.WithTimeout(ctx, *timeout)
	defer cancelTimeout()

	client := httpx.New(userAgent, *rps, 1)
	scrapers := []source.Scraper{
		remoteok.New(client),
		// Fase 3: añadir más fuentes aquí detrás de la misma interfaz.
	}

	start := time.Now()
	slog.Info("scrape iniciado", "sources", len(scrapers), "workers", *workers)

	jobs := source.Run(ctx, scrapers, *workers)
	if len(jobs) == 0 {
		slog.Error("ninguna oferta recogida; no se escribe el fichero")
		os.Exit(1)
	}

	if err := store.WriteJSON(*out, jobs); err != nil {
		slog.Error("error escribiendo salida", "err", err)
		os.Exit(1)
	}

	slog.Info("scrape completado",
		"jobs", len(jobs),
		"out", *out,
		"dur", time.Since(start).Round(time.Millisecond).String(),
	)
}
