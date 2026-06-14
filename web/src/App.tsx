import { useState } from 'react'
import type { JobFilters } from './api'
import OverviewCards from './components/OverviewCards'
import TopTechChart from './components/TopTechChart'
import SalaryChart from './components/SalaryChart'
import TrendsChart from './components/TrendsChart'
import JobFiltersBar from './components/JobFilters'
import JobsList from './components/JobsList'

export default function App() {
  const [filters, setFilters] = useState<JobFilters>({ offset: 0 })

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900">
      <header className="border-b border-slate-200 bg-white">
        <div className="mx-auto max-w-6xl px-4 py-5">
          <h1 className="text-xl font-bold">Tech Job Market Analyzer</h1>
          <p className="text-sm text-slate-500">
            ¿Qué tecnologías se piden más, dónde y cuánto pagan?
          </p>
        </div>
      </header>

      <main className="mx-auto max-w-6xl space-y-6 px-4 py-6">
        <OverviewCards />

        <section className="grid gap-4 lg:grid-cols-2">
          <TopTechChart />
          <SalaryChart />
        </section>

        <TrendsChart />

        <section className="space-y-3">
          <h2 className="text-lg font-semibold">Ofertas</h2>
          <JobFiltersBar filters={filters} onChange={setFilters} />
          <JobsList filters={filters} onPage={(offset) => setFilters((f) => ({ ...f, offset }))} />
        </section>
      </main>

      <footer className="mx-auto max-w-6xl px-4 py-8 text-center text-xs text-slate-400">
        Datos de RemoteOK, Remotive y Arbeitnow. Proyecto educativo · enlaces a las ofertas originales.
      </footer>
    </div>
  )
}
