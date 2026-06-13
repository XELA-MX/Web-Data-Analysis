// Package httpx envuelve net/http con las cortesías y resiliencia que pide el
// scraping responsable: User-Agent honesto, rate limiting por cliente, timeouts
// y reintentos con backoff exponencial. Ver documentación/V1/02-arquitectura.md
// y 07-etica-y-legalidad.md.
package httpx

import (
	"context"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"time"

	"golang.org/x/time/rate"
)

// Client es un cliente HTTP cortés y resiliente.
type Client struct {
	hc         *http.Client
	limiter    *rate.Limiter
	userAgent  string
	maxRetries int
}

// New crea un Client.
//   - userAgent: identificación honesta hacia la fuente.
//   - rps: peticiones por segundo permitidas (rate limit de cortesía).
//   - burst: ráfaga máxima instantánea.
func New(userAgent string, rps float64, burst int) *Client {
	if burst < 1 {
		burst = 1
	}
	return &Client{
		hc:         &http.Client{Timeout: 30 * time.Second},
		limiter:    rate.NewLimiter(rate.Limit(rps), burst),
		userAgent:  userAgent,
		maxRetries: 3,
	}
}

// GetJSON hace GET sobre url y deserializa el cuerpo JSON en dest.
// Respeta el rate limit, reintenta ante errores transitorios (red, 429, 5xx)
// con backoff exponencial, y aborta si el context se cancela.
func (c *Client) GetJSON(ctx context.Context, url string, dest any) error {
	var lastErr error

	for attempt := 0; attempt <= c.maxRetries; attempt++ {
		if attempt > 0 {
			// Backoff exponencial: 500ms, 1s, 2s...
			backoff := time.Duration(500*(1<<(attempt-1))) * time.Millisecond
			select {
			case <-ctx.Done():
				return ctx.Err()
			case <-time.After(backoff):
			}
		}

		// Espera a tener cupo en el rate limiter (cortesía con la fuente).
		if err := c.limiter.Wait(ctx); err != nil {
			return err
		}

		body, status, err := c.get(ctx, url)
		if err != nil {
			lastErr = err
			continue // error de red → reintentar
		}
		switch {
		case status == http.StatusTooManyRequests || status >= 500:
			lastErr = fmt.Errorf("respuesta %d de %s", status, url)
			continue // transitorio → reintentar
		case status != http.StatusOK:
			return fmt.Errorf("respuesta inesperada %d de %s", status, url)
		}
		if err := json.Unmarshal(body, dest); err != nil {
			return fmt.Errorf("json inválido de %s: %w", url, err)
		}
		return nil
	}

	return fmt.Errorf("agotados %d reintentos contra %s: %w", c.maxRetries, url, lastErr)
}

func (c *Client) get(ctx context.Context, url string) ([]byte, int, error) {
	req, err := http.NewRequestWithContext(ctx, http.MethodGet, url, nil)
	if err != nil {
		return nil, 0, err
	}
	req.Header.Set("User-Agent", c.userAgent)
	req.Header.Set("Accept", "application/json")

	resp, err := c.hc.Do(req)
	if err != nil {
		return nil, 0, err
	}
	defer resp.Body.Close()

	// Límite defensivo de lectura (10 MiB) para no agotar memoria ante respuestas anómalas.
	body, err := io.ReadAll(io.LimitReader(resp.Body, 10<<20))
	if err != nil {
		return nil, resp.StatusCode, err
	}
	return body, resp.StatusCode, nil
}
