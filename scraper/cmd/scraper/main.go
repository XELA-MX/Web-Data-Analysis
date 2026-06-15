// Comando scraper: orquesta las fuentes y persiste las ofertas crudas.
//
// Sinks (flag -sink):
//   - json     → escribe jobs.json (rápido para iterar, sin DB)
//   - postgres → inserta en la tabla raw_jobs (idempotente)
//   - both     → ambos (por defecto)
//
// Uso:
//
//	go run ./cmd/scraper                      # both: jobs.json + Postgres
//	go run ./cmd/scraper -sink=json           # solo jobs.json
//	go run ./cmd/scraper -sink=postgres       # solo DB
//
// La conexión a Postgres se toma de la variable de entorno DATABASE_URI.
package main

import (
	"context"
	"flag"
	"fmt"
	"os"
	"os/signal"
	"time"

	"log/slog"

	"github.com/x3no/tech-job-market-analyzer/scraper/internal/httpx"
	"github.com/x3no/tech-job-market-analyzer/scraper/internal/rawjob"
	"github.com/x3no/tech-job-market-analyzer/scraper/internal/source"
	"github.com/x3no/tech-job-market-analyzer/scraper/internal/source/arbeitnow"
	"github.com/x3no/tech-job-market-analyzer/scraper/internal/source/greenhouse"
	"github.com/x3no/tech-job-market-analyzer/scraper/internal/source/jobicy"
	"github.com/x3no/tech-job-market-analyzer/scraper/internal/source/manfred"
	"github.com/x3no/tech-job-market-analyzer/scraper/internal/source/remoteok"
	"github.com/x3no/tech-job-market-analyzer/scraper/internal/source/remotive"
	"github.com/x3no/tech-job-market-analyzer/scraper/internal/store"
	"github.com/x3no/tech-job-market-analyzer/scraper/internal/store/pgstore"
)

// User-Agent honesto: identifica el proyecto y deja una vía de contacto.
const userAgent = "tech-job-market-analyzer/0.1 (+https://github.com/x3no/tech-job-market-analyzer; portfolio project)"

// sourceMeta describe una fuente para la tabla sources (catálogo).
type sourceMeta struct {
	baseURL         string
	rateLimitPerMin int
}

// catálogo de metadatos por nombre de fuente (para upsert en sources).
var sourceCatalog = map[string]sourceMeta{
	"remoteok":  {baseURL: "https://remoteok.com", rateLimitPerMin: 60},
	"remotive":  {baseURL: "https://remotive.com", rateLimitPerMin: 60},
	"arbeitnow":  {baseURL: "https://www.arbeitnow.com", rateLimitPerMin: 60},
	"manfred":    {baseURL: "https://www.getmanfred.com", rateLimitPerMin: 60},
	"jobicy":     {baseURL: "https://jobicy.com", rateLimitPerMin: 60},
	"greenhouse": {baseURL: "https://boards-api.greenhouse.io", rateLimitPerMin: 120},
}

func main() {
	out := flag.String("out", "jobs.json", "ruta del fichero JSON de salida")
	sink := flag.String("sink", "both", "destino: json | postgres | both")
	workers := flag.Int("workers", 4, "número de fuentes a scrapear en paralelo")
	rps := flag.Float64("rps", 1.0, "peticiones por segundo (cortesía; RemoteOK pide crawl-delay 1)")
	manfredDetails := flag.Bool("manfred-details", true, "enriquecer Manfred con el detalle por oferta (skills)")
	manfredRPS := flag.Float64("manfred-rps", 8.0, "peticiones/seg para Manfred (tiene ~1600 detalles que pedir)")
	timeout := flag.Duration("timeout", 300*time.Second, "timeout global de la ejecución")
	flag.Parse()

	slog.SetDefault(slog.New(slog.NewTextHandler(os.Stderr, &slog.HandlerOptions{Level: slog.LevelInfo})))

	wantJSON := *sink == "json" || *sink == "both"
	wantPG := *sink == "postgres" || *sink == "both"
	if !wantJSON && !wantPG {
		slog.Error("sink inválido", "sink", *sink, "válidos", "json|postgres|both")
		os.Exit(2)
	}

	// Context con timeout global + cancelación por Ctrl-C.
	ctx, cancel := signal.NotifyContext(context.Background(), os.Interrupt)
	defer cancel()
	ctx, cancelTimeout := context.WithTimeout(ctx, *timeout)
	defer cancelTimeout()

	// Un cliente HTTP por fuente → rate limiting independiente por dominio.
	scrapers := []source.Scraper{
		remoteok.New(httpx.New(userAgent, *rps, 1)),
		remotive.New(httpx.New(userAgent, *rps, 1)),
		arbeitnow.New(httpx.New(userAgent, *rps, 1)),
		// Manfred tiene su propio cliente con rps más alto por el volumen de detalles.
		manfred.New(httpx.New(userAgent, *manfredRPS, 4), *manfredDetails),
		jobicy.New(httpx.New(userAgent, *rps, 1)),
		// Greenhouse pega a varios boards → rps algo más alto.
		greenhouse.New(httpx.New(userAgent, 5, 2)),
	}

	start := time.Now()
	slog.Info("scrape iniciado", "sources", len(scrapers), "workers", *workers, "sink", *sink)

	jobs := source.Run(ctx, scrapers, *workers)
	if len(jobs) == 0 {
		slog.Error("no se recogió ninguna oferta — ¿sin conexión a las fuentes?")
		os.Exit(1)
	}

	if wantJSON {
		if err := store.WriteJSON(*out, jobs); err != nil {
			slog.Error("error escribiendo JSON", "err", err)
			os.Exit(1)
		}
		slog.Info("jobs.json escrito", "jobs", len(jobs), "out", *out)
	}

	if wantPG {
		if err := persistPostgres(ctx, jobs); err != nil {
			slog.Error("error persistiendo en Postgres", "err", err)
			os.Exit(1)
		}
	}

	slog.Info("scrape completado",
		"jobs", len(jobs),
		"dur", time.Since(start).Round(time.Millisecond).String(),
	)
}

// persistPostgres agrupa las ofertas por fuente, hace upsert de cada fuente en
// `sources` y vuelca las crudas en `raw_jobs` (idempotente).
func persistPostgres(ctx context.Context, jobs []rawjob.RawJob) error {
	dsn := os.Getenv("DATABASE_URI")
	if dsn == "" {
		slog.Error("falta DATABASE_URI en el entorno para el sink postgres")
		os.Exit(2)
	}

	st, err := pgstore.Open(ctx, dsn)
	if err != nil {
		return err
	}
	defer st.Close()

	// Agrupar por nombre de fuente (un scrape puede traer varias).
	bySource := map[string][]rawjob.RawJob{}
	for _, j := range jobs {
		bySource[j.Source] = append(bySource[j.Source], j)
	}

	failed := 0
	for name, group := range bySource {
		meta, ok := sourceCatalog[name]
		if !ok {
			slog.Warn("fuente sin metadatos en el catálogo; usando defaults", "source", name)
		}
		// Aislamiento de fallos: si una fuente falla al persistir, se registra
		// y se continúa con el resto (no se aborta toda la ingesta).
		sourceID, err := st.UpsertSource(ctx, name, meta.baseURL, meta.rateLimitPerMin)
		if err != nil {
			slog.Error("upsert source falló", "source", name, "err", err)
			failed++
			continue
		}
		inserted, updated, err := st.InsertRawJobs(ctx, sourceID, group)
		if err != nil {
			slog.Error("insert raw_jobs falló", "source", name, "err", err)
			failed++
			continue
		}
		slog.Info("raw_jobs persistidos",
			"source", name,
			"source_id", sourceID,
			"recibidos", len(group),
			"nuevas", inserted,
			"actualizadas", updated,
		)
	}
	if failed > 0 {
		return fmt.Errorf("%d fuente(s) fallaron al persistir", failed)
	}
	return nil
}
