import { useQuery } from '@tanstack/react-query'
import { Bar, BarChart, CartesianGrid, Legend, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts'
import { fetchSalary } from '../api'
import ChartCard from './ChartCard'

const fmt = (n: number) => `$${(n / 1000).toFixed(0)}k`

export default function SalaryChart() {
  const { data } = useQuery({ queryKey: ['salary', 'seniority'], queryFn: () => fetchSalary('seniority') })

  return (
    <ChartCard
      title="Salario medio por seniority"
      subtitle="Media de los rangos declarados, en USD anuales. Pocas ofertas publican salario."
    >
      {data && data.length > 0 ? (
        <ResponsiveContainer width="100%" height={380}>
          <BarChart data={data} margin={{ top: 8 }}>
            <CartesianGrid strokeDasharray="3 3" vertical={false} />
            <XAxis dataKey="group" tick={{ fontSize: 12 }} />
            <YAxis tickFormatter={fmt} width={48} />
            <Tooltip formatter={(v: number) => fmt(v)} />
            <Legend />
            <Bar dataKey="avg_min" name="Mín" fill="#94a3b8" radius={[4, 4, 0, 0]} />
            <Bar dataKey="avg_max" name="Máx" fill="#6366f1" radius={[4, 4, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      ) : (
        <div className="flex h-[380px] items-center justify-center text-sm text-slate-400">
          Aún hay pocas ofertas con salario declarado.
        </div>
      )}
    </ChartCard>
  )
}
