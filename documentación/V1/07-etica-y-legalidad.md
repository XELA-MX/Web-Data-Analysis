# 07 · Ética y legalidad del scraping

> Hacer scraping **bien** no es solo evitar problemas: es un **punto a favor en el CV**.
> Demuestra criterio y madurez de ingeniería. Documenta estas decisiones en el README.

## ⚖️ Principios

1. **Solo datos públicos.** Nada detrás de login, paywall o autenticación.
2. **Respetar `robots.txt`.** Comprobarlo antes de scrapear y honrar sus reglas.
3. **Rate limiting de verdad.** No martillear el servidor. Pocas peticiones por minuto,
   espaciadas. Mejor lento y respetuoso que rápido y abusivo.
4. **`User-Agent` honesto e identificable.** Nada de hacerse pasar por un navegador
   para esconderse. Ej: `TechJobAnalyzer/1.0 (+https://github.com/tu-usuario/repo)`.
5. **Preferir APIs/RSS oficiales** sobre HTML scraping siempre que existan.
6. **Respetar los Términos de Servicio** de cada fuente.
7. **No revender los datos.** Proyecto educativo/personal.
8. **Atribución** cuando la fuente la pida.

## 🛡️ Cómo se traduce en código

| Principio | Implementación |
|-----------|----------------|
| Rate limiting | `golang.org/x/time/rate` con límite por dominio |
| Backoff | reintentos con espera exponencial ante errores/429 |
| Cortesía | `User-Agent` identificable + cabeceras razonables |
| robots.txt | chequeo previo (`temoto/robotstxt` o similar) |
| Respeto a 429/503 | parar o ralentizar ante señales del servidor |
| Caché | no re-scrapear lo que no cambió (usar `external_id`) |

## 🚦 Señales de que debes parar/ralentizar

- Respuestas `429 Too Many Requests` o `503`.
- La fuente publica un `Crawl-delay` en `robots.txt`.
- Los ToS prohíben explícitamente el uso automatizado.

→ En esos casos: respetar el límite, o descartar la fuente. **Nunca** intentar evadir
bloqueos (rotar IPs/proxies para esquivar anti-bot) — eso sí es una red flag y zona
legalmente turbia.

## 📜 Nota legal (sin ser asesoría jurídica)

- El scraping de datos **públicos** es generalmente tolerado, pero el marco legal varía
  por jurisdicción y por los ToS de cada sitio.
- Evitar datos personales sensibles. Las ofertas de empleo (empresa, puesto, salario,
  stack) no son datos personales del candidato → terreno cómodo.
- Ante la duda con una fuente: **no integrarla**. Hay alternativas limpias de sobra
  (ver [06 · Fuentes de datos](./06-fuentes-de-datos.md)).

## ✅ Por qué esto suma en tu CV

> "Implementé scraping respetando `robots.txt`, con rate limiting por dominio y
> `User-Agent` identificable, priorizando APIs oficiales sobre HTML."

Esa frase en un README comunica **madurez de ingeniería**. Muchos juniors hacen
scraping agresivo y sin criterio; tú demuestras lo contrario.
