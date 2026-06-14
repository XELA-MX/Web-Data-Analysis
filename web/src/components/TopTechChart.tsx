import { useQuery } from '@tanstack/react-query'
import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts'
import { fetchTopTech } from '../api'
import ChartCard from './ChartCard'

export default function TopTechChart() {
  const { data } = useQuery({ queryKey: ['tech'], queryFn: () => fetchTopTech(15) })

  return (
    <ChartCard title="Tecnologías más demandadas">
      <ResponsiveContainer width="100%" height={380}>
        <BarChart data={data ?? []} layout="vertical" margin={{ left: 20 }}>
          <CartesianGrid strokeDasharray="3 3" horizontal={false} />
          <XAxis type="number" allowDecimals={false} />
          <YAxis type="category" dataKey="tech" width={100} tick={{ fontSize: 12 }} />
          <Tooltip />
          <Bar dataKey="count" fill="#6366f1" radius={[0, 4, 4, 0]} />
        </BarChart>
      </ResponsiveContainer>
    </ChartCard>
  )
}
