import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { CartesianGrid, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts'
import { fetchTechHistory, fetchTopTech } from '../api'
import ChartCard from './ChartCard'

export default function TechHistoryChart() {
  const { data: top } = useQuery({ queryKey: ['tech'], queryFn: () => fetchTopTech(15) })
  const [picked, setPicked] = useState('')
  const tech = picked || top?.[0]?.tech || 'python'

  const { data } = useQuery({
    queryKey: ['techHistory', tech],
    queryFn: () => fetchTechHistory(tech, 30),
    enabled: !!tech,
  })

  const single = (data?.length ?? 0) <= 1

  return (
    <ChartCard title="Evolución por tecnología" subtitle="Demanda diaria de una tecnología (se llena día a día).">
      <select
        value={tech}
        onChange={(e) => setPicked(e.target.value)}
        className="mb-3 rounded-md border border-slate-300 px-2 py-1.5 text-sm text-slate-900"
      >
        {top?.map((t) => (
          <option key={t.tech} value={t.tech}>
            {t.tech}
          </option>
        ))}
      </select>

      <ResponsiveContainer width="100%" height={240}>
        <LineChart data={data ?? []} margin={{ top: 8, right: 16 }}>
          <CartesianGrid strokeDasharray="3 3" vertical={false} />
          <XAxis dataKey="date" tick={{ fontSize: 11 }} />
          <YAxis allowDecimals={false} width={40} />
          <Tooltip />
          <Line type="monotone" dataKey="count" stroke="#6366f1" strokeWidth={2} dot={{ r: 4 }} />
        </LineChart>
      </ResponsiveContainer>

      {single && (
        <p className="mt-1 text-center text-xs text-slate-400">
          Aún hay un solo día de datos. La línea crecerá conforme se actualicen las ofertas.
        </p>
      )}
    </ChartCard>
  )
}
