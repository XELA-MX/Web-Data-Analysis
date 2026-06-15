import { useEffect, useRef, useState } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { fetchAdminStats, fetchRefreshState, startRefresh } from '../api'

function StatCard({ value, label }: { value: string | number; label: string }) {
  return (
    <div className="rounded-xl bg-white p-5 shadow-sm ring-1 ring-slate-200">
      <div className="text-3xl font-bold text-slate-900">{value}</div>
      <div className="mt-1 text-sm text-slate-500">{label}</div>
    </div>
  )
}

export default function AdminPanel({ onBack }: { onBack: () => void }) {
  const qc = useQueryClient()
  const [full, setFull] = useState(false)
  const { data: stats } = useQuery({ queryKey: ['adminStats'], queryFn: fetchAdminStats })

  const { data: state } = useQuery({
    queryKey: ['refreshState'],
    queryFn: fetchRefreshState,
    refetchInterval: (q) => (q.state.data?.status === 'running' ? 1500 : false),
  })

  const prev = useRef<string | undefined>(undefined)
  useEffect(() => {
    if (prev.current === 'running' && state?.status === 'done') {
      ;['adminStats', 'overview', 'tech', 'categories', 'jobs', 'feed', 'sources'].forEach((k) =>
        qc.invalidateQueries({ queryKey: [k] }),
      )
    }
    prev.current = state?.status
  }, [state?.status, qc])

  const refresh = useMutation({
    mutationFn: () => startRefresh(full),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['refreshState'] }),
  })

  const running = state?.status === 'running'
  const lastScraped = stats?.last_scraped ? new Date(stats.last_scraped).toLocaleString() : '—'

  return (
    <main className="mx-auto max-w-6xl space-y-8 px-4 py-8">
      <div>
        <button onClick={onBack} className="text-sm text-slate-500 hover:text-slate-700">
          ← Volver al panel
        </button>
        <h1 className="mt-2 text-2xl font-bold text-slate-900">Administración</h1>
        <p className="text-sm text-slate-500">Estado del sistema y control de la ingesta de datos.</p>
      </div>

      <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
        <StatCard value={stats?.jobs?.toLocaleString() ?? '—'} label="Ofertas (sin duplicados)" />
        <StatCard value={stats?.users ?? '—'} label="Usuarios registrados" />
        <StatCard value={stats?.pending_raw ?? '—'} label="Crudas sin procesar" />
        <StatCard value={stats?.sources.length ?? '—'} label="Fuentes activas" />
      </div>

      {/* Control de refresco */}
      <section className="rounded-xl bg-white p-6 shadow-sm ring-1 ring-slate-200">
        <h2 className="font-semibold text-slate-900">Buscar nuevas ofertas</h2>
        <p className="mt-1 text-sm text-slate-500">
          Relanza el scraping de todas las fuentes y el procesado. Último scrape: {lastScraped}.
        </p>

        <label className="mt-4 flex items-center gap-2 text-sm text-slate-600">
          <input type="checkbox" checked={full} disabled={running} onChange={(e) => setFull(e.target.checked)} />
          Incluir skills de Manfred (más completo, pero tarda varios minutos)
        </label>

        <div className="mt-4">
          <button
            onClick={() => refresh.mutate()}
            disabled={running || refresh.isPending}
            className="rounded-md bg-indigo-600 px-5 py-2.5 text-sm font-semibold text-white hover:bg-indigo-700 disabled:opacity-50"
          >
            {running ? 'Buscando ofertas…' : 'Buscar ahora'}
          </button>
        </div>

        {/* Progreso en vivo */}
        {state && state.status !== 'idle' && (
          <div className="mt-5 rounded-lg bg-slate-50 p-4">
            <div className="flex items-center justify-between text-sm">
              <span className="font-medium text-slate-700">
                {running && <span className="mr-1.5 inline-block animate-pulse text-indigo-600">●</span>}
                {state.step ?? '—'}
              </span>
              <span
                className={
                  state.status === 'error'
                    ? 'text-red-600'
                    : state.status === 'done'
                      ? 'text-emerald-600'
                      : 'text-slate-400'
                }
              >
                {state.status === 'error' ? 'Error' : state.status === 'done' ? 'Completado' : `${state.progress}%`}
              </span>
            </div>

            <div className="mt-2 h-2 w-full overflow-hidden rounded-full bg-slate-200">
              <div
                className={`h-full rounded-full transition-all duration-500 ${
                  state.status === 'error' ? 'bg-red-500' : state.status === 'done' ? 'bg-emerald-500' : 'bg-indigo-600'
                }`}
                style={{ width: `${state.status === 'done' ? 100 : state.progress}%` }}
              />
            </div>

            {state.message && (
              <p className={`mt-2 text-sm ${state.status === 'error' ? 'text-red-600' : 'text-slate-600'}`}>
                {state.message}
              </p>
            )}

            {state.log.length > 0 && (
              <ul className="mt-3 max-h-40 space-y-1 overflow-auto border-t border-slate-200 pt-2 text-xs text-slate-500">
                {state.log.map((l, i) => (
                  <li key={i} className="flex gap-2">
                    <span className="text-slate-300">›</span>
                    {l}
                  </li>
                ))}
              </ul>
            )}
          </div>
        )}
      </section>

      {/* Desglose por fuente */}
      <section className="rounded-xl bg-white p-6 shadow-sm ring-1 ring-slate-200">
        <h2 className="mb-3 font-semibold text-slate-900">Ofertas por fuente</h2>
        <table className="w-full text-sm">
          <thead>
            <tr className="text-left text-xs uppercase text-slate-400">
              <th className="pb-2">Fuente</th>
              <th className="pb-2 text-right">Ofertas</th>
            </tr>
          </thead>
          <tbody>
            {stats?.sources.map((s) => (
              <tr key={s.source} className="border-t border-slate-100">
                <td className="py-2 font-medium text-slate-700">{s.source}</td>
                <td className="py-2 text-right text-slate-600">{s.jobs.toLocaleString()}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </section>
    </main>
  )
}
