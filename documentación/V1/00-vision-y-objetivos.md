# 00 · Visión y objetivos

## 🎯 Visión

Construir un **agregador del mercado laboral tech** que recopile ofertas de empleo
de varias fuentes públicas, las normalice y enriquezca (extrayendo stack, salario,
seniority y ubicación), y exponga la información en un **dashboard de tendencias**.

El producto responde preguntas reales:
- ¿Qué tecnologías se demandan más este mes?
- ¿Cuánto paga el mercado por un stack concreto y nivel de seniority?
- ¿Qué % de ofertas son remotas?
- ¿Cómo evoluciona la demanda de una tecnología en el tiempo?

## 👤 Para quién

- **Usuario principal:** yo mismo (dev junior buscando orientación de mercado).
- **Audiencia secundaria:** otros devs que quieran datos para decidir qué aprender.
- **Audiencia "real" del proyecto:** reclutadores que verán el repo y el demo.

## 💼 Objetivos de CV / GitHub

Este proyecto está diseñado explícitamente para demostrar competencias clave:

| Competencia | Cómo se demuestra |
|-------------|-------------------|
| **Concurrencia** | Scraper en Go con worker pool y rate limiting |
| **Pipelines de datos / ETL** | scrape → limpiar → enriquecer → almacenar |
| **Diseño de sistemas** | Servicios desacoplados, interfaces, cola opcional |
| **Bases de datos** | Esquema relacional, índices, migrations |
| **Frontend moderno** | Dashboard React + TypeScript con visualizaciones |
| **DevOps** | Docker Compose, CI/CD, deploy en vivo |
| **Buenas prácticas** | Tests, manejo de errores, scraping ético |

## ✅ Criterios de éxito

1. **Demo en vivo** público que cualquiera pueda abrir y tocar.
2. **README excelente** con GIF, diagrama de arquitectura y decisiones técnicas.
3. Datos **reales** actualizándose automáticamente.
4. Código limpio, testeado y desplegable con un solo comando.
5. Que yo pueda explicar **cada decisión técnica** en una entrevista.

## 👥 Producto público y multiusuario

V1 será **público**: cualquiera puede registrarse, tener su cuenta y una **experiencia
personalizada** según su perfil (rol, stack, seniority, modalidad). El feed se filtra y
ordena por afinidad con el usuario — un dev frontend ve ofertas frontend, quien busca
remoto no ve presenciales, etc.

Detalle completo en [08 · Cuentas y personalización](./08-cuentas-y-personalizacion.md).

## 🚫 Fuera de alcance (V1)

- Otros dominios (precios, cripto, inmuebles) → V2+.
- App móvil nativa.
- Ranking personalizado con ML/embeddings avanzado (el MVP usa scoring simple por match
  de stack; el ML queda como extensión futura).

## 📈 Métrica de "buen proyecto"

> Un proyecto **pulido y terminado** > tres proyectos a medias.
> Preferimos hacer bien las Fases 1-4 que dejar 6 fases incompletas.
