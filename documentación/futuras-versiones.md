# 🔮 Futuras versiones

> Este documento describe la visión a largo plazo. **V1 (empleos tech)** es el MVP;
> las siguientes versiones **reutilizan la misma arquitectura base**
> (scrape → limpiar → almacenar → analizar → visualizar) cambiando solo el dominio.

## 🧩 La idea clave: una plataforma, varios dominios

El proyecto no es "una app de empleos", es un **motor de agregación y análisis de datos**
que se puede apuntar a cualquier dominio. El 80% del código de V1 (scraper concurrente,
pipeline ETL, deduplicación, API, dashboard) es **reutilizable**. Cada nueva versión es
sobre todo: nuevas fuentes + nuevo modelo de datos + nuevas visualizaciones.

> Cada versión vive en su propia carpeta (`V2/`, `V3/`...) para **no mezclar**. El
> código común se irá extrayendo a paquetes/módulos compartidos a medida que se repita.

---

## 📦 V2 — Analizador de precios / e-commerce 💸

**Idea:** un *price tracker* tipo CamelCamelCamel. Sigue precios de productos en el
tiempo y avisa cuando bajan.

- **Qué scrapea:** páginas/feeds de producto (precio, disponibilidad, vendedor).
- **Funcionalidades:**
  - Histórico de precios por producto (gráfica temporal).
  - Alertas: "avísame si baja de X".
  - Comparativa entre tiendas.
- **Qué demuestra (extra sobre V1):** scheduling fiable, series temporales densas,
  sistema de notificaciones, detección de cambios.
- **Muy demo-friendly:** la gráfica de "precio a lo largo del tiempo" se entiende al instante.
- **Nota ética:** preferir APIs/afiliados oficiales; rate limiting estricto; evitar
  grandes plataformas anti-bot (ver criterio de [V1/07](./V1/07-etica-y-legalidad.md)).

---

## 📈 V3 — Cripto / finanzas

**Idea:** agregar precios, noticias y *sentiment* de criptomonedas.

- **Qué consume:** **APIs públicas** abundantes (CoinGecko, exchanges) → poco/nada de
  HTML scraping. Ideal para practicar **tiempo real**.
- **Funcionalidades:**
  - Dashboard de precios en vivo (WebSockets).
  - Agregación de noticias + análisis de sentiment.
  - Alertas por umbrales.
- **Qué demuestra (extra sobre V1):** **real-time / WebSockets**, manejo de streams,
  posible toque de NLP (sentiment).
- **Por qué encaja:** al haber tantas APIs oficiales, el foco se va a la parte de
  tiempo real y análisis, no a pelear con anti-bots.

---

## 🏠 V4 — Inmuebles / alquileres

**Idea:** agregar listados de pisos/alquileres con vista en mapa y alertas.

- **Qué scrapea:** portales inmobiliarios (precio, m², zona, habitaciones, coords).
- **Funcionalidades:**
  - **Vista en mapa** (Leaflet/Mapbox) con marcadores.
  - Filtros por zona, precio, tamaño.
  - Alertas de nuevos listados que encajen con tus criterios.
- **Qué demuestra (extra sobre V1):** **geodatos** (geocoding, mapas), filtros
  espaciales (PostGIS opcional), problema muy visual y real.
- **Nota:** revisar bien ToS de cada portal; priorizar los más tolerantes.

---

## 🧱 Qué se comparte entre versiones

A medida que aparezcan V2+, conviene **extraer a código común** lo que se repite:

| Componente | Reutilizable | Cambia por dominio |
|------------|--------------|--------------------|
| Worker pool + rate limiting (Go) | ✅ casi 100% | — |
| Interfaz `Scraper` | ✅ | implementaciones concretas |
| Pipeline ETL / procesado | ✅ estructura | reglas de extracción |
| Deduplicación (`fingerprint`) | ✅ patrón | campos del hash |
| Esquema base de DB | ⚠️ patrón | columnas del dominio |
| API REST (búsqueda/agregación) | ✅ patrón | endpoints específicos |
| Dashboard (componentes de gráficas) | ✅ patrón | qué se grafica |
| Scheduler | ✅ | frecuencia |
| Tiempo real (WebSockets) | — | nace en V3 |
| Mapas / geodatos | — | nace en V4 |

> **Posible evolución:** sacar un paquete `core/` (o un módulo Go + lib Python
> compartidos) cuando el código común se estabilice tras V2. No adelantarlo: primero
> que el patrón se repita 2-3 veces, luego abstraer.

---

## 🗺️ Orden sugerido y por qué

1. **V1 · Empleos tech** — base del sistema; te sirve a ti como junior. ← *estamos aquí*
2. **V2 · Precios** — añade scheduling serio + alertas + series temporales. Demo muy claro.
3. **V3 · Cripto** — añade tiempo real (WebSockets); muchas APIs oficiales.
4. **V4 · Inmuebles** — añade geodatos y mapas.

Cada paso suma una **competencia técnica nueva** sobre la anterior → el portfolio
crece en profundidad, no solo en cantidad.

> ⚠️ Recordatorio de la regla de oro: **terminar y pulir V1 antes de empezar V2.**
> Un V1 desplegado y redondo vale más que cuatro versiones a medias.
