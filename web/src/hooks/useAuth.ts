import { useQuery } from '@tanstack/react-query'
import type { User } from '../api'
import { fetchMe } from '../api'

/** Estado de autenticación: el usuario actual (o null si no hay sesión). */
export function useAuth(): { user: User | null; isLoading: boolean } {
  const { data, isLoading } = useQuery({
    queryKey: ['me'],
    queryFn: fetchMe,
    retry: false,
    staleTime: 5 * 60_000,
  })
  return { user: data ?? null, isLoading }
}
