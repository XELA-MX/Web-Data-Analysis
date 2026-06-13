# 06 · Fuentes de datos

> **Regla:** priorizar fuentes con **API/RSS/JSON público** sobre HTML scraping.
> Son más estables, más rápidas y éticamente más limpias.
> ⚠️ **Verificar siempre los Términos de Servicio y `robots.txt` vigentes** antes de
> integrar una fuente — pueden cambiar. La info de abajo es un punto de partida a confirmar.

## ✅ Candidatas recomendadas (scraping-friendly)

| Fuente | Acceso | Notas |
|--------|--------|-------|
| **RemoteOK** | Endpoint JSON público | Histórico bueno; ideal para el MVP. Confirmar ToS/atribución |
| **We Work Remotely** | Feeds RSS por categoría | RSS = estable y cómodo de parsear |
| **Hacker News "Who is Hiring"** | API oficial de HN (Firebase) | Hilo mensual; requiere parsear texto libre, pero la API es abierta |
| **Remotive** | API pública documentada | Empleos remotos; buena para empezar |
| **Arbeitnow** | API pública | Empleos (foco europeo); JSON limpio |
| **GitHub Jobs-like / Greenhouse / Lever** | Cada empresa expone su board vía API | Muchas startups publican en `boards.greenhouse.io` / `jobs.lever.co` con endpoints JSON |

> Para el **MVP (Fase 1)** recomiendo **RemoteOK** o **Remotive**: JSON directo, sin
> HTML, datos ricos. Empieza con una sola.

## ⚠️ Fuentes a evitar (al menos al principio)

| Fuente | Por qué evitar |
|--------|----------------|
| **LinkedIn** | ToS muy estrictos, anti-bot agresivo, riesgo legal. **No.** |
| **Indeed** | Bloqueos anti-scraping fuertes; su API pública está restringida |
| **Glassdoor** | Anti-bot agresivo, login |

> Estas grandes plataformas dan dolores de cabeza y zona gris legal. No aportan más
> valor de CV que las fuentes limpias — y sí más riesgo.

## 🔌 Estrategia de integración por tipo

### Fuente con API/JSON
1. Leer la documentación del endpoint.
2. Mapear el JSON a `RawJob`.
3. Respetar rate limits indicados.

### Fuente con RSS
1. Parsear el feed XML (`gofeed` en Go va muy bien).
2. Cada `<item>` → `RawJob`.

### Fuente HTML (último recurso)
1. Comprobar `robots.txt` (`/robots.txt`).
2. `goquery`/`colly` para extraer con selectores CSS.
3. Rate limiting estricto + `User-Agent` identificable.
4. Selectores aislados por fuente (se rompen cuando cambia el HTML → mantener acotado).

## 🧩 Diseño para añadir fuentes sin fricción

Cada fuente implementa la interfaz común:

```go
type Scraper interface {
    Name() string
    Fetch(ctx context.Context) ([]RawJob, error)
}
```

Añadir una fuente = crear un archivo nuevo que implemente la interfaz y registrarlo.
El resto del sistema no cambia. Esto es un buen punto a destacar en el README/entrevista.

## ✅ Checklist antes de integrar una fuente

- [ ] ¿Tiene API/RSS oficial? (preferible)
- [ ] Revisar `robots.txt`.
- [ ] Revisar Términos de Servicio (¿permite uso automatizado de datos públicos?).
- [ ] ¿Requiere login? → si sí, **descartar** para V1.
- [ ] Definir rate limit cortés.
- [ ] ¿Pide atribución? → respetarla.
