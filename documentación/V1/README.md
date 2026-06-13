# 📊 Tech Job Market Analyzer — V1

> Agregador y analizador del mercado laboral tech. Scrapea ofertas de empleo de
> múltiples fuentes, extrae el stack tecnológico, salarios y ubicación, y lo
> presenta en un dashboard de tendencias.

Este proyecto demuestra un **pipeline de datos completo** (scrape → limpiar →
almacenar → analizar → visualizar) con concurrencia real, scraping ético y un
frontend pulido. Pensado para tener alto valor en CV/GitHub.

---

## 🎯 En una frase

Una herramienta que responde: **"¿Qué tecnologías se piden más, dónde y cuánto pagan?"**
— usando datos reales y públicos del mercado.

---

## 📁 Índice de la documentación

| Documento | Contenido |
|-----------|-----------|
| [00 · Visión y objetivos](./00-vision-y-objetivos.md) | Qué es, para quién, y por qué aporta valor al CV |
| [01 · Requisitos](./01-requisitos.md) | Requisitos funcionales y no funcionales |
| [02 · Arquitectura](./02-arquitectura.md) | Diagrama, componentes y flujo de datos |
| [03 · Stack tecnológico](./03-stack-tecnologico.md) | Qué tecnología usamos y **por qué** |
| [04 · Modelo de datos](./04-modelo-de-datos.md) | Esquema de la base de datos e índices |
| [05 · Roadmap por fases](./05-roadmap.md) | Plan de desarrollo incremental |
| [06 · Fuentes de datos](./06-fuentes-de-datos.md) | Job boards candidatos y cuáles tienen API |
| [07 · Ética y legalidad](./07-etica-y-legalidad.md) | Scraping responsable, rate limiting, ToS |
| [08 · Cuentas y personalización](./08-cuentas-y-personalizacion.md) | Auth, multiusuario y feed personalizado |
| [09 · Seguridad 🔒](./09-seguridad.md) | **PRIORIDAD MÁXIMA** — checklist de seguridad del proyecto |

---

## 🗂️ Versionado de la documentación

- **`V1/`** → MVP enfocado en **empleos tech** (esta carpeta).
- `V2/`, `V3/`... → futuras integraciones (precios/e-commerce, cripto, inmuebles)
  reutilizando la misma arquitectura base.

> 🔮 La visión completa a futuro está en
> [`../futuras-versiones.md`](../futuras-versiones.md).

---

## 🚀 Quick start (se completará en la Fase 0)

```bash
# Levantar todo el stack
docker compose up

# Dashboard
open http://localhost:3000
```

---

_Última actualización: 2026-06-13_
