// Package rawjob define el dato crudo que produce el scraper: lo que llega de la
// fuente, sin interpretar. El procesado (extraer tech, normalizar salario, etc.)
// es responsabilidad de /processor. Ver documentación/V1/04-modelo-de-datos.md.
package rawjob

import "time"

// RawJob es una oferta tal cual la devuelve una fuente, antes de procesar.
// Payload guarda la respuesta original completa para poder reprocesar sin
// volver a scrapear.
type RawJob struct {
	Source     string         `json:"source"`
	ExternalID string         `json:"external_id"`
	URL        string         `json:"url"`
	Payload    map[string]any `json:"payload"`
	ScrapedAt  time.Time      `json:"scraped_at"`
}
