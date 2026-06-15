import { keepPreviousData, useQuery } from '@tanstack/react-query'
import type { JobFilters } from '../api'
import { fetchJobs } from '../api'
import JobCard from './JobCard'

const PAGE = 20

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
