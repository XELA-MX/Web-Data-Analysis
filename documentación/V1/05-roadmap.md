# 05 · Roadmap por fases

> **Filosofía:** cada fase entrega algo funcional y demostrable. Desde la Fase 3 ya
> tienes un proyecto digno de CV. Llegando al final, destaca de verdad.

## 🧱 Fase 0 — Cimientos · _1-2 días_
Montar el esqueleto y las decisiones, sin lógica todavía.

- [ ] Monorepo: `/scraper` (Go), `/processor` (Python), `/api`, `/web` (React+TS)
- [ ] Git + README desde el día 1
- [ ] `docker-compose.yml` con Postgres levantándose
- [ ] Esquema de datos inicial + primera migration (ver [04](./04-modelo-de-datos.md))

✅ **Entregable:** repo con estructura y `docker compose up` arrancando Postgres.

---

## ⚡ Fase 1 — Scraper MVP (UNA fuente) · _3-4 días_ · **Go**
La fase más importante. Elegir una fuente *scraping-friendly* (ver [06](./06-fuentes-de-datos.md)).

- [ ] Cliente HTTP con `User-Agent` honesto y rate limiting
- [ ] Parsear la fuente → structs `RawJob`
- [ ] Respetar `robots.txt`
- [ ] Guardar en `jobs.json` local primero (iterar rápido, sin DB aún)
- [ ] Worker pool con goroutines para paralelizar

✅ **Entregable:** binario que escupe `jobs.json` con ofertas reales.

---

## 🗄️ Fase 2 — Persistencia + Procesado · _3-4 días_ · **Python + Postgres**

- [ ] El scraper inserta `RawJob` en Postgres (tabla `raw_jobs`)
- [ ] Procesador Python: extraer `tech_stack`, normalizar `salary`, inferir `seniority`, detectar `remote`
- [ ] Migrations versionadas

✅ **Entregable:** DB con ofertas limpias y enriquecidas. **Pipeline ETL completo.**

---

## 🔀 Fase 3 — Multi-fuente + Deduplicación · _3-4 días_

- [ ] Añadir 2-3 fuentes más tras la interfaz `Scraper`
- [ ] Deduplicación por `fingerprint`
- [ ] Manejo de errores robusto: reintentos con backoff; aislamiento de fallos

✅ **Entregable:** agregador real multi-fuente. **Ya es un proyecto fuerte.**

---

## 📊 Fase 4 — API + Dashboard · _4-6 días_ · **React + TS**
Lo que el reclutador VE y toca.

- [ ] API REST: búsqueda/filtros + agregaciones
- [ ] Dashboard con:
  - 📈 Tecnologías más demandadas
  - 💰 Rangos salariales por stack/seniority
  - 🗺️ Distribución geográfica / % remoto
  - 🔍 Buscador con filtros
- [ ] Gráficas con Recharts/visx

✅ **Entregable:** demo navegable. **Lo que va primero en el CV.**

---

## 👥 Fase 4.5 — Cuentas y personalización · _4-6 días_
Convierte el proyecto en un **producto multiusuario público**. Va **después** del
núcleo de datos (Fases 1-4) para no acoplar auth a un pipeline que aún cambia.

- [ ] Autenticación: GitHub OAuth y/o email+contraseña (hashing fuerte, sesiones httpOnly)
- [ ] Onboarding: capturar rol, stack, seniority, modalidad, ubicación
- [ ] Pantalla de ajustes de preferencias
- [ ] Feed personalizado: filtrado + scoring por afinidad de stack/seniority
- [ ] Guardar / descartar ofertas
- [ ] Aislamiento de datos por `user_id`

✅ **Entregable:** registro, login y experiencia personalizada por usuario.
Ver [08 · Cuentas y personalización](./08-cuentas-y-personalizacion.md).

---

## 🤖 Fase 5 — Automatización · _2-3 días_

- [ ] Scheduler: scraping cada X horas
- [ ] Histórico → tendencias en el tiempo ("React +12% este mes") 🔥
- [ ] (Opcional) Alertas por criterios

✅ **Entregable:** datos vivos que se actualizan solos.

---

## ✨ Fase 6 — Pulido y Deploy · _3-4 días_
Lo que separa "proyecto de tutorial" de "proyecto profesional".

- [ ] Tests (unit en procesador y scrapers; `httptest` en Go)
- [ ] CI/CD con GitHub Actions (lint + test + build)
- [ ] Docker Compose levanta TODO con un comando
- [ ] Deploy en Fly.io / Railway / Render → demo público
- [ ] README de lujo: GIF, diagrama, decisiones técnicas, cómo correrlo

✅ **Entregable:** proyecto desplegado, testeado y documentado.

---

## ⏱️ Resumen

| Fase | Qué consigues | ¿CV-ready? |
|------|---------------|------------|
| 1-2 | Pipeline ETL básico | 🟡 Decente |
| 3 | Multi-fuente + dedup | 🟢 Sólido |
| 4 | Dashboard en vivo | 🟢🟢 Fuerte |
| 4.5 | Cuentas + feed personalizado | 🟢🟢 Producto multiusuario |
| 5-6 | Tendencias + deploy + tests | 🟢🟢🟢 Destaca |

**Total estimado:** ~3-5 semanas a ritmo tranquilo.

## 🎁 Extensiones futuras (post-V1)
- Otros dominios (precios, cripto, inmuebles) → `V2/`, reutilizando arquitectura.
- Categorización con ML/embeddings en vez de regex.
- Alertas por email/Telegram.
- Comparador "tu perfil vs. mercado".
