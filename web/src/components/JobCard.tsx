import type { Job } from '../api'
import { categoryLabel, seniorityLabel } from '../labels'

export function salaryLabel(j: Job): string | null {
  if (j.salary_min == null && j.salary_max == null) return null
  const cur = j.currency ?? ''
  const k = (n: number) => `${(n / 1000).toFixed(0)}k`
  if (j.salary_min != null && j.salary_max != null) return `${cur} ${k(j.salary_min)}–${k(j.salary_max)}`
  const n = (j.salary_min ?? j.salary_max) as number
  return `${cur} ${k(n)}`
}

interface Props {
  job: Job
  score?: number
  onSave?: () => void
  onDismiss?: () => void
  onRemove?: () => void
  busy?: boolean
}

export default function JobCard({ job, score, onSave, onDismiss, onRemove, busy }: Props) {
  const salary = salaryLabel(job)
  const hasActions = onSave || onDismiss || onRemove

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
          {score !== undefined && (
            <span className="rounded-full bg-indigo-600 px-2 py-0.5 text-xs font-semibold text-white" title="Afinidad con tu perfil">
              ★ {score}
            </span>
          )}
          {job.category && (
            <span className="rounded-full bg-violet-50 px-2 py-0.5 text-xs font-medium text-violet-700">
              {categoryLabel(job.category)}
            </span>
          )}
          {job.remote && (
            <span className="rounded-full bg-emerald-50 px-2 py-0.5 text-xs font-medium text-emerald-700">Remoto</span>
          )}
          {job.seniority && (
            <span className="rounded-full bg-slate-100 px-2 py-0.5 text-xs text-slate-600">
              {seniorityLabel(job.seniority)}
            </span>
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

      {hasActions && (
        <div className="mt-3 flex gap-2 border-t border-slate-100 pt-3">
          {onSave && (
            <button
              onClick={onSave}
              disabled={busy}
              className="rounded-md bg-indigo-50 px-2.5 py-1 text-xs font-medium text-indigo-700 hover:bg-indigo-100 disabled:opacity-50"
            >
              Guardar
            </button>
          )}
          {onDismiss && (
            <button
              onClick={onDismiss}
              disabled={busy}
              className="rounded-md bg-slate-50 px-2.5 py-1 text-xs font-medium text-slate-600 hover:bg-slate-100 disabled:opacity-50"
            >
              Descartar
            </button>
          )}
          {onRemove && (
            <button
              onClick={onRemove}
              disabled={busy}
              className="rounded-md bg-slate-50 px-2.5 py-1 text-xs font-medium text-slate-600 hover:bg-slate-100 disabled:opacity-50"
            >
              Quitar
            </button>
          )}
        </div>
      )}
    </div>
  )
}
