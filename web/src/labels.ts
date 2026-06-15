// Etiquetas legibles (ES) para las categorías de oferta.

export const CATEGORY_LABELS: Record<string, string> = {
  frontend: 'Frontend',
  backend: 'Backend',
  fullstack: 'Full-stack',
  mobile: 'Mobile',
  data: 'Data',
  devops: 'DevOps',
  qa: 'QA',
  security: 'Seguridad',
  other: 'Otros',
}

export const categoryLabel = (c?: string | null): string | null =>
  c ? (CATEGORY_LABELS[c] ?? c) : null

export const SENIORITY_LABELS: Record<string, string> = {
  intern: 'Prácticas',
  junior: 'Junior',
  mid: 'Mid',
  senior: 'Senior',
}

// Niveles en orden, para selects y chips.
export const SENIORITY_ORDER = ['intern', 'junior', 'mid', 'senior'] as const

export const seniorityLabel = (s?: string | null): string | null =>
  s ? (SENIORITY_LABELS[s] ?? s) : null
