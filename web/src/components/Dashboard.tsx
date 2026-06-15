import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import type { JobFilters, User } from '../api'
import { fetchPreferences } from '../api'
import OverviewCards from './OverviewCards'
import TopTechChart from './TopTechChart'
import SalaryChart from './SalaryChart'
import TrendsChart from './TrendsChart'
import JobFiltersBar from './JobFilters'
import JobsList from './JobsList'
import PersonalFeed from './PersonalFeed'

function SectionHeader({ title, description }: { title: string; description: string }) {
  return (
    <div>
      <h2 className="text-lg font-bold text-slate-900">{title}</h2>
      <p className="text-sm text-slate-500">{description}</p>
    </div>
  )
}

export default function Dashboard({ user, onEditPrefs }: { user: User; onEditPrefs: () => void }) {
  const [filters, setFilters] = useState<JobFilters>({ offset: 0 })
  const [tab, setTab] = useState<'feed' | 'all'>('feed')

  const { data: prefs } = useQuery({ queryKey: ['preferences'], queryFn: fetchPreferences })
  const needsProfile = prefs != null && prefs.categories.length === 0 && prefs.tech_stack.length === 0

  return (
    <main className="mx-auto max-w-6xl space-y-10 px-4 py-8">
      <div>
        <h1 className="text-2xl font-bold">Hola, {user.display_name ?? user.email.split('@')[0]} 👋</h1>
        <p className="text-sm text-slate-500">Esto es lo que está pidiendo el mercado tech ahora mismo.</p>
      </div>

      {/* Aviso: completa tu perfil (si no lo ha hecho) */}
      {needsProfile && (
        <div className="flex flex-wrap items-center justify-between gap-3 rounded-xl bg-indigo-50 p-4 ring-1 ring-indigo-200">
          <div>
            <p className="font-semibold text-indigo-900">✨ Personaliza tu experiencia</p>
            <p className="text-sm text-indigo-700">
              Cuéntanos tu stack y preferencias para recibir ofertas hechas a tu medida. Tardas 1 minuto.
            </p>
          </div>
          <button
            onClick={onEditPrefs}
            className="rounded-md bg-indigo-600 px-4 py-2 text-sm font-semibold text-white hover:bg-indigo-700"
          >
            Completar perfil
          </button>
        </div>
      )}

      <section className="space-y-3">
        <SectionHeader title="El mercado de un vistazo" description="Cifras clave de todas las ofertas analizadas." />
        <OverviewCards />
      </section>

      <section className="space-y-3">
        <SectionHeader
          title="Tendencias"
          description="Qué tecnologías se piden, cuánto pagan y cómo evoluciona la demanda."
        />
        <div className="grid gap-4 lg:grid-cols-2">
          <TopTechChart />
          <SalaryChart />
        </div>
        <TrendsChart />
      </section>

      <section className="space-y-3">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <SectionHeader
            title="Explora las ofertas"
            description="“Para ti” las ordena por afinidad con tu perfil. “Todas” deja que filtres a mano."
          />
          <div className="flex items-center gap-2">
            {tab === 'feed' && (
              <button onClick={onEditPrefs} className="text-sm text-indigo-600 hover:underline">
                Editar preferencias
              </button>
            )}
            <div className="flex gap-1 rounded-lg bg-slate-100 p-0.5 text-sm">
              <button
                onClick={() => setTab('feed')}
                className={`rounded-md px-3 py-1.5 font-medium ${tab === 'feed' ? 'bg-white shadow-sm' : 'text-slate-500'}`}
              >
                Para ti
              </button>
              <button
                onClick={() => setTab('all')}
                className={`rounded-md px-3 py-1.5 font-medium ${tab === 'all' ? 'bg-white shadow-sm' : 'text-slate-500'}`}
              >
                Todas
              </button>
            </div>
          </div>
        </div>

        {tab === 'feed' ? (
          <PersonalFeed />
        ) : (
          <>
            <JobFiltersBar filters={filters} onChange={setFilters} />
            <JobsList filters={filters} onPage={(offset) => setFilters((f) => ({ ...f, offset }))} />
          </>
        )}
      </section>
    </main>
  )
}
