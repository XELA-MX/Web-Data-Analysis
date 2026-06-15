import { useQuery } from '@tanstack/react-query'
import { fetchOverview } from '../api'

function Card({ value, label, hint, accent }: { value: string | number; label: string; hint: string; accent: string }) {
  return (
    <div className="rounded-xl bg-white p-4 shadow-sm ring-1 ring-slate-200">
      <div className={`text-2xl font-bold ${accent}`}>{value}</div>
      <div className="text-sm font-medium text-slate-700">{label}</div>
      <div className="text-xs text-slate-400">{hint}</div>
    </div>
  )
}

export default function OverviewCards() {
  const { data, isLoading, isError } = useQuery({ queryKey: ['overview'], queryFn: fetchOverview })

  if (isLoading) return <div className="text-slate-500">Cargando resumen…</div>
  if (isError || !data) return <div className="text-red-600">Error cargando el resumen.</div>

  return (
    <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
      <Card value={data.total_jobs} label="Ofertas" hint="únicas analizadas" accent="text-indigo-600" />
      <Card value={`${data.remote_pct}%`} label="Remotas" hint="permiten trabajo remoto" accent="text-emerald-600" />
      <Card value={data.with_salary} label="Con salario" hint="publican rango salarial" accent="text-amber-600" />
      <Card value={data.sources} label="Fuentes" hint="portales rastreados" accent="text-slate-700" />
    </div>
  )
}
