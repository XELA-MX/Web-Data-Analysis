import { keepPreviousData, useQuery } from '@tanstack/react-query'
import type { Job, JobFilters } from '../api'
import { fetchJobs } from '../api'

const PAGE = 20

function salaryLabel(j: Job): string | null {
  if (j.salary_min == null && j.salary_max == null) return null
  const cur = j.currency ?? ''
  const k = (n: number) => `${(n / 1000).toFixed(0)}k`
  if (j.salary_min != null && j.salary_max != null) return `${cur} ${k(j.salary_min)}–${k(j.salary_max)}`
  const n = (j.salary_min ?? j.salary_max) as number
  return `${cur} ${k(n)}`
}

function JobCard({ job }: { job: Job }) {
  const salary = salaryLabel(job)
  return (
    <div className="rounded-xl bg-white p-4 shadow-sm ring-1 ring-slate-200">
      <div className="flex items-start justify-between gap-3">
        <div>
          <a
            href={job.url ?? '#'}
            target="_blank"
            rel="noopener"
            className="font-semibold text-slate-900 hover:text-indigo-600"
          >
            {job.title}
          </a>
          <div className="text-sm text-slate-500">
            {job.company ?? 'Empresa desconocida'}
            {job.location ? ` · ${job.location}` : ''}
          </div>
        </div>
        <div className="flex flex-col items-end gap-1">
          {job.remote && (
            <span className="rounded-full bg-emerald-50 px-2 py-0.5 text-xs font-medium text-emerald-700">
              Remoto
            </span>
          )}
          {job.seniority && (
            <span className="rounded-full bg-slate-100 px-2 py-0.5 text-xs text-slate-600">{job.seniority}</span>
          )}
        </div>
      </div>

      {job.tech_stack.length > 0 && (
        <div className="mt-2 flex flex-wrap gap-1">
          {job.tech_stack.slice(0, 10).map((t) => (
            <span key={t} className="rounded bg-indigo-50 px-1.5 py-0.5 text-xs text-indigo-700">
              {t}
            </span>
          ))}
        </div>
      )}

      <div className="mt-2 flex items-center justify-between text-xs text-slate-400">
        {/* Atribución a la fuente (RemoteOK/Remotive lo exigen). */}
        <span>vía {job.source}</span>
        {salary && <span className="font-medium text-slate-600">{salary}</span>}
      </div>
    </div>
  )
}

export default function JobsList({
  filters,
  onPage,
}: {
  filters: JobFilters
  onPage: (offset: number) => void
}) {
  const { data, isLoading, isError } = useQuery({
    queryKey: ['jobs', filters],
    queryFn: () => fetchJobs({ ...filters, limit: PAGE }),
    placeholderData: keepPreviousData,
  })

  if (isLoading) return <div className="text-slate-500">Cargando ofertas…</div>
  if (isError || !data) return <div className="text-red-600">Error cargando las ofertas.</div>

  const offset = filters.offset ?? 0
  const from = data.total === 0 ? 0 : offset + 1
  const to = Math.min(offset + PAGE, data.total)

  return (
    <div className="space-y-3">
      <div className="text-sm text-slate-500">
        {data.total} ofertas · mostrando {from}–{to}
      </div>

      {data.items.map((job) => (
        <JobCard key={`${job.source}-${job.id}`} job={job} />
      ))}

      {data.items.length === 0 && (
        <div className="rounded-xl bg-white p-6 text-center text-slate-400 ring-1 ring-slate-200">
          No hay ofertas con esos filtros.
        </div>
      )}

      <div className="flex justify-between pt-2">
        <button
          className="rounded-md border border-slate-300 px-3 py-1.5 text-sm disabled:opacity-40"
          disabled={offset === 0}
          onClick={() => onPage(Math.max(0, offset - PAGE))}
        >
          ← Anterior
        </button>
        <button
          className="rounded-md border border-slate-300 px-3 py-1.5 text-sm disabled:opacity-40"
          disabled={to >= data.total}
          onClick={() => onPage(offset + PAGE)}
        >
          Siguiente →
        </button>
      </div>
    </div>
  )
}
