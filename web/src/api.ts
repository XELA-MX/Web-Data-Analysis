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
  category: string | null
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

export interface CategoryCount {
  category: string
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

// ─────────────────────────── auth / personalización ───────────────────────────

export interface User {
  id: number
  email: string
  display_name: string | null
  provider: string
  created_at: string
  last_login_at: string | null
  is_admin: boolean
}

export interface AdminStats {
  users: number
  jobs: number
  pending_raw: number
  last_scraped: string | null
  sources: SourceCount[]
}

export interface RefreshState {
  status: string // idle | running | done | error
  step: string | null
  progress: number
  message: string | null
  log: string[]
  started_at: string | null
  finished_at: string | null
}

export interface Preferences {
  categories: string[]
  tech_stack: string[]
  seniority: string | null
  work_mode: string | null
  country: string | null
  salary_target: number | null
  updated_at: string | null
}

export interface SavedJob extends Job {
  saved_status: string
  saved_at: string
}

export interface FeedItem extends Job {
  score: number
}

export class ApiError extends Error {
  constructor(
    public status: number,
    public detail: string,
  ) {
    super(detail)
  }
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    credentials: 'include', // envía/recibe la cookie de sesión
    headers: { 'Content-Type': 'application/json' },
    ...init,
  })
  if (!res.ok) {
    let detail = `Error ${res.status}`
    try {
      const body = await res.json()
      if (body?.detail) detail = typeof body.detail === 'string' ? body.detail : JSON.stringify(body.detail)
    } catch {
      /* sin cuerpo JSON */
    }
    throw new ApiError(res.status, detail)
  }
  if (res.status === 204) return undefined as T
  return res.json() as Promise<T>
}

const get = <T>(path: string) => request<T>(path)

// ── ofertas globales + agregaciones ──

export interface JobFilters {
  q?: string
  tech?: string[]
  seniority?: string
  category?: string
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
  if (f.category) p.set('category', f.category)
  if (f.remote !== undefined) p.set('remote', String(f.remote))
  if (f.source) p.set('source', f.source)
  p.set('limit', String(f.limit ?? 20))
  p.set('offset', String(f.offset ?? 0))
  return get<JobList>(`/jobs?${p.toString()}`)
}

export const fetchOverview = () => get<Overview>('/stats/overview')
export const fetchTopTech = (limit = 15) => get<TechCount[]>(`/stats/tech?limit=${limit}`)
export const fetchCategories = () => get<CategoryCount[]>('/stats/categories')
export const fetchSalary = (by: 'seniority' | 'tech' = 'seniority') =>
  get<SalaryByGroup[]>(`/stats/salary?by=${by}`)
export const fetchTrends = (days = 30) => get<TrendPoint[]>(`/stats/trends?days=${days}`)
export const fetchSources = () => get<SourceCount[]>('/stats/sources')

// ── auth ──

export const login = (email: string, password: string) =>
  request<User>('/auth/login', { method: 'POST', body: JSON.stringify({ email, password }) })

export const register = (email: string, password: string, display_name?: string) =>
  request<User>('/auth/register', { method: 'POST', body: JSON.stringify({ email, password, display_name }) })

export const logout = () => request<void>('/auth/logout', { method: 'POST' })

export async function fetchMe(): Promise<User | null> {
  try {
    return await get<User>('/auth/me')
  } catch (e) {
    if (e instanceof ApiError && e.status === 401) return null
    throw e
  }
}

// ── personalización ──

export const fetchPreferences = () => get<Preferences>('/me/preferences')
export const savePreferences = (p: Partial<Preferences>) =>
  request<Preferences>('/me/preferences', { method: 'PUT', body: JSON.stringify(p) })

// ── admin ──

export const fetchAdminStats = () => get<AdminStats>('/admin/stats')
export const startRefresh = (full = false) =>
  request<RefreshState>(`/admin/refresh?full=${full}`, { method: 'POST' })
export const fetchRefreshState = () => get<RefreshState>('/admin/refresh')

export const fetchFeed = (limit = 20, offset = 0) => get<FeedItem[]>(`/me/feed?limit=${limit}&offset=${offset}`)
export const fetchSaved = (status?: string) => get<SavedJob[]>(`/me/saved${status ? `?status=${status}` : ''}`)
export const saveJob = (job_id: number, status: 'saved' | 'dismissed' | 'applied') =>
  request<SavedJob>('/me/saved', { method: 'PUT', body: JSON.stringify({ job_id, status }) })
export const deleteSaved = (job_id: number) => request<void>(`/me/saved/${job_id}`, { method: 'DELETE' })
