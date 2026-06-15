import { useQuery } from '@tanstack/react-query'
import { CartesianGrid, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts'
import { fetchTrends } from '../api'
import ChartCard from './ChartCard'

export default function TrendsChart() {
  const { data } = useQuery({ queryKey: ['trends'], queryFn: () => fetchTrends(30) })

  return (
    <ChartCard
      title="Ofertas nuevas por día"
      subtitle="Se va llenando conforme rastreamos las fuentes cada día (últimos 30 días)."
    >
      <ResponsiveContainer width="100%" height={260}>
        <LineChart data={data ?? []} margin={{ top: 8, right: 16 }}>
          <CartesianGrid strokeDasharray="3 3" vertical={false} />
          <XAxis dataKey="day" tick={{ fontSize: 11 }} />
          <YAxis allowDecimals={false} width={40} />
          <Tooltip />
          <Line type="monotone" dataKey="jobs" stroke="#6366f1" strokeWidth={2} dot={{ r: 3 }} />
        </LineChart>
      </ResponsiveContainer>
    </ChartCard>
  )
}
