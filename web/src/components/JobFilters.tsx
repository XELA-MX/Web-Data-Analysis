import { useQuery } from '@tanstack/react-query'
import type { JobFilters } from '../api'
import { fetchSources } from '../api'

interface Props {
  filters: JobFilters
  onChange: (next: JobFilters) => void
}

export default function JobFiltersBar({ filters, onChange }: Props) {
  const { data: sources } = useQuery({ queryKey: ['sources'], queryFn: fetchSources })

  const set = (patch: Partial<JobFilters>) => onChange({ ...filters, ...patch, offset: 0 })

  return (
    <div className="flex flex-wrap items-end gap-3 rounded-xl bg-white p-4 shadow-sm ring-1 ring-slate-200">
      <label className="flex flex-col text-xs text-slate-500">
        Buscar
        <input
          className="mt-1 w-56 rounded-md border border-slate-300 px-2 py-1.5 text-sm text-slate-900"
          placeholder="título o empresa"
          value={filters.q ?? ''}
          onChange={(e) => set({ q: e.target.value || undefined })}
        />
      </label>

      <label className="flex flex-col text-xs text-slate-500">
        Tecnología
        <input
          className="mt-1 w-40 rounded-md border border-slate-300 px-2 py-1.5 text-sm text-slate-900"
          placeholder="react, go…"
          value={filters.tech?.join(', ') ?? ''}
          onChange={(e) => {
            const tech = e.target.value
              .split(',')
              .map((t) => t.trim().toLowerCase())
              .filter(Boolean)
            set({ tech: tech.length ? tech : undefined })
          }}
        />
      </label>

      <label className="flex flex-col text-xs text-slate-500">
        Seniority
        <select
          className="mt-1 rounded-md border border-slate-300 px-2 py-1.5 text-sm text-slate-900"
          value={filters.seniority ?? ''}
          onChange={(e) => set({ seniority: e.target.value || undefined })}
        >
          <option value="">Todos</option>
          <option value="junior">Junior</option>
          <option value="mid">Mid</option>
          <option value="senior">Senior</option>
        </select>
      </label>

      <label className="flex flex-col text-xs text-slate-500">
        Modalidad
        <select
          className="mt-1 rounded-md border border-slate-300 px-2 py-1.5 text-sm text-slate-900"
          value={filters.remote === undefined ? '' : String(filters.remote)}
          onChange={(e) => set({ remote: e.target.value === '' ? undefined : e.target.value === 'true' })}
        >
          <option value="">Todas</option>
          <option value="true">Remoto</option>
          <option value="false">Presencial</option>
        </select>
      </label>

      <label className="flex flex-col text-xs text-slate-500">
        Fuente
        <select
          className="mt-1 rounded-md border border-slate-300 px-2 py-1.5 text-sm text-slate-900"
          value={filters.source ?? ''}
          onChange={(e) => set({ source: e.target.value || undefined })}
        >
          <option value="">Todas</option>
          {sources?.map((s) => (
            <option key={s.source} value={s.source}>
              {s.source} ({s.jobs})
            </option>
          ))}
        </select>
      </label>
    </div>
  )
}
