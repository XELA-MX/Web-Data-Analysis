// Áreas (roles) y las tecnologías que se sugieren para cada una en el onboarding.
// Los nombres de tech coinciden con el vocabulario canónico del backend, para que
// el feed personalizado puntúe bien la afinidad.

export interface RoleOption {
  key: string
  label: string
  icon: string
  techs: string[]
}

export const ROLE_OPTIONS: RoleOption[] = [
  { key: 'frontend', label: 'Frontend', icon: '🎨', techs: ['react', 'vue', 'angular', 'svelte', 'nextjs', 'typescript', 'javascript', 'tailwind', 'css', 'html'] },
  { key: 'backend', label: 'Backend', icon: '⚙️', techs: ['go', 'python', 'java', 'php', 'ruby', 'nodejs', 'dotnet', 'spring', 'django', 'flask', 'rails', 'sql', 'postgres', 'graphql'] },
  { key: 'fullstack', label: 'Full-stack', icon: '🧩', techs: ['react', 'typescript', 'nodejs', 'python', 'go', 'postgres', 'docker', 'graphql'] },
  { key: 'mobile', label: 'Mobile', icon: '📱', techs: ['swift', 'kotlin', 'react', 'javascript'] },
  { key: 'data', label: 'Data / IA', icon: '📊', techs: ['python', 'sql', 'pandas', 'spark', 'tensorflow', 'pytorch', 'machine learning', 'postgres'] },
  { key: 'devops', label: 'DevOps / Cloud', icon: '☁️', techs: ['docker', 'kubernetes', 'terraform', 'ansible', 'aws', 'gcp', 'azure', 'linux', 'ci/cd'] },
  { key: 'qa', label: 'QA / Testing', icon: '🧪', techs: ['python', 'javascript', 'typescript', 'sql'] },
]

// Para "no estoy seguro": el catálogo completo, deduplicado y ordenado.
export const ALL_TECHS: string[] = Array.from(
  new Set(ROLE_OPTIONS.flatMap((r) => r.techs).concat(['c++', 'c#', 'rust', 'kotlin', 'redis', 'mysql', 'mongodb', 'express', 'laravel'])),
).sort()

// Unión de las tecnologías sugeridas para varias áreas. Sin áreas → catálogo completo.
export function techsForRoles(keys: string[]): string[] {
  if (!keys.length) return ALL_TECHS
  const set = new Set<string>()
  keys.forEach((k) => ROLE_OPTIONS.find((r) => r.key === k)?.techs.forEach((t) => set.add(t)))
  return set.size ? Array.from(set) : ALL_TECHS
}
