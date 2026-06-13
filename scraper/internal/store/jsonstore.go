// Package store persiste las ofertas crudas. En la Fase 1 escribimos a un
// jobs.json local (iterar rápido sin DB); en la Fase 2 esto se sustituye/complementa
// con la inserción en la tabla raw_jobs de Postgres.
package store

import (
	"encoding/json"
	"fmt"
	"os"

	"github.com/x3no/tech-job-market-analyzer/scraper/internal/rawjob"
)

// WriteJSON escribe las ofertas a `path` como JSON indentado, de forma atómica
// (escribe a un temporal y renombra) para no dejar un fichero a medias si algo falla.
func WriteJSON(path string, jobs []rawjob.RawJob) error {
	data, err := json.MarshalIndent(jobs, "", "  ")
	if err != nil {
		return fmt.Errorf("serializando jobs: %w", err)
	}

	tmp := path + ".tmp"
	if err := os.WriteFile(tmp, data, 0o644); err != nil {
		return fmt.Errorf("escribiendo %s: %w", tmp, err)
	}
	if err := os.Rename(tmp, path); err != nil {
		return fmt.Errorf("renombrando a %s: %w", path, err)
	}
	return nil
}
