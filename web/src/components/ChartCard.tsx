import type { ReactNode } from 'react'

export default function ChartCard({ title, children }: { title: string; children: ReactNode }) {
  return (
    <div className="rounded-xl bg-white p-4 shadow-sm ring-1 ring-slate-200">
      <h2 className="mb-3 text-sm font-semibold text-slate-700">{title}</h2>
      {children}
    </div>
  )
}
