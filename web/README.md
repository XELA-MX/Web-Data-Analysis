# web (React + TypeScript)

Dashboard de tendencias del mercado laboral tech. Consume la API de `/api`.

- **Stack:** React + TypeScript + Vite.
- **Datos:** TanStack Query (caché + estados de carga).
- **Gráficas:** Recharts.
- **Estilos:** Tailwind CSS v4 (plugin de Vite).

## Qué muestra (RF-13..RF-17)

- Tarjetas resumen (ofertas, % remoto, con salario, fuentes).
- Top tecnologías más demandadas (barras).
- Salario medio por seniority (barras).
- Ofertas vistas por día (línea, tendencia temporal).
- Buscador con filtros combinables (texto, tecnología, seniority, modalidad, fuente) + paginación.
- Atribución a la fuente y enlace a la oferta original en cada tarjeta.

## Estructura

```
src/
  api.ts                cliente de la API + tipos (espejo de los modelos del backend)
  main.tsx              entrypoint (QueryClientProvider)
  App.tsx               layout del dashboard
  components/
    OverviewCards.tsx   tarjetas resumen
    TopTechChart.tsx    barras de tecnologías
    SalaryChart.tsx     barras de salario por seniority
    TrendsChart.tsx     línea temporal
    JobFilters.tsx      buscador + filtros
    JobsList.tsx        lista de ofertas (con atribución) + paginación
    ChartCard.tsx       contenedor visual de gráfica
```

## Uso

```bash
cd web
npm install
cp .env.example .env        # ajustar VITE_API_URL si la API no está en :8000
npm run dev                 # http://localhost:5173 (requiere la API levantada)
npm run build               # type-check + bundle de producción
```

> La API debe estar corriendo (`cd ../api && uvicorn app.main:app`) y permitir el
> origen del dashboard vía `CORS_ORIGINS`.

## Estado / pendientes

- ✅ **Fase 4 (dashboard) — hecha:** dashboard completo; `npm run build` verde; CORS verificado.
- ⚠️ **Vulnerabilidad dev-only (Fase 6):** `esbuild` (transitivo de Vite 6) tiene un
  advisory que **solo afecta al tooling de desarrollo, no al bundle de producción**. El
  parche (`esbuild@0.28.1`) requiere **Vite 8** (cambio mayor); se aborda al endurecer
  para deploy. Forzarlo con `overrides` rompe el build de Vite 6.
- ⬜ Code-splitting (el bundle pasa de 500 kB por Recharts).
- ⬜ Auth + feed personalizado: **Fase 4.5**.
