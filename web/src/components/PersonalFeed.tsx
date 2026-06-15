import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { fetchFeed, saveJob } from '../api'
import JobCard from './JobCard'

export default function PersonalFeed() {
  const qc = useQueryClient()
  const { data, isLoading, isError } = useQuery({ queryKey: ['feed'], queryFn: () => fetchFeed(20, 0) })

  const save = useMutation({
    mutationFn: (jobId: number) => saveJob(jobId, 'saved'),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['saved'] }),
  })
  const dismiss = useMutation({
    mutationFn: (jobId: number) => saveJob(jobId, 'dismissed'),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['feed'] }),
  })

  if (isLoading) return <div className="text-slate-500">Cargando tu feed…</div>
  if (isError || !data) return <div className="text-red-600">Error cargando tu feed.</div>

  return (
    <div className="space-y-3">
      <p className="text-sm text-slate-500">
        Ordenadas por afinidad con tu perfil. Ajusta tus preferencias para afinar el ranking.
      </p>
      {data.map((job) => (
        <JobCard
          key={`${job.source}-${job.id}`}
          job={job}
          score={job.score}
          busy={save.isPending || dismiss.isPending}
          onSave={() => save.mutate(job.id)}
          onDismiss={() => dismiss.mutate(job.id)}
        />
      ))}
      {data.length === 0 && (
        <div className="rounded-xl bg-white p-6 text-center text-slate-400 ring-1 ring-slate-200">
          No hay ofertas que mostrar.
        </div>
      )}
    </div>
  )
}
