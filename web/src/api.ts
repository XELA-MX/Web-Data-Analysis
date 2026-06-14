// Cliente de la API REST. Tipos espejo de los modelos Pydantic del backend.

const BASE = import.meta.env.VITE_API_URL ?? 'http://localhost:8000'

export interface Job {
  id: number
  source: string
  title: string
  company: string | null
  location: string | null
  country: string | null
  remote: boolean
  salary_min: number | null
  salary_max: number | null
  currency: string | null
  tech_stack: string[]
  seniority: string | null
  url: string | null
  posted_at: string | null
}

export interface JobList {
  total: number
  limit: number
  offset: number
  items: Job[]
}

export interface TechCount {
  tech: string
  count: number
}

export interface SalaryByGroup {
  group: string
  jobs: number
  avg_min: number | null
  avg_max: number | null
}

export interface TrendPoint {
  day: string
  jobs: number
}

export interface SourceCount {
  source: string
  jobs: number
}

export interface Overview {
  total_jobs: number
  remote_jobs: number
  remote_pct: number
  with_salary: number
  with_tech: number
  sources: number
  last_scraped: string | null
}

async function get<T>(path: string): Promise<T> {
  const res = await fetch(`${BASE}${path}`)
  if (!res.ok) throw new Error(`API ${res.status} en ${path}`)
  return res.json() as Promise<T>
}

export interface JobFilters {
  q?: string
  tech?: string[]
  seniority?: string
  remote?: boolean
  source?: string
  limit?: number
  offset?: number
}

export function fetchJobs(f: JobFilters): Promise<JobList> {
  const p = new URLSearchParams()
  if (f.q) p.set('q', f.q)
  f.tech?.forEach((t) => p.append('tech', t))
  if (f.seniority) p.set('seniority', f.seniority)
  if (f.remote !== undefined) p.set('remote', String(f.remote))
  if (f.source) p.set('source', f.source)
  p.set('limit', String(f.limit ?? 20))
  p.set('offset', String(f.offset ?? 0))
  return get<JobList>(`/jobs?${p.toString()}`)
}

export const fetchOverview = () => get<Overview>('/stats/overview')
export const fetchTopTech = (limit = 15) => get<TechCount[]>(`/stats/tech?limit=${limit}`)
export const fetchSalary = (by: 'seniority' | 'tech' = 'seniority') =>
  get<SalaryByGroup[]>(`/stats/salary?by=${by}`)
export const fetchTrends = (days = 30) => get<TrendPoint[]>(`/stats/trends?days=${days}`)
export const fetchSources = () => get<SourceCount[]>('/stats/sources')
