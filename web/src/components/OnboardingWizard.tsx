import { useEffect, useState } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { fetchPreferences, savePreferences } from '../api'
import { ALL_TECHS, ROLE_OPTIONS, techsForRoles } from '../roles'
import { SENIORITY_ORDER, seniorityLabel } from '../labels'

const STEPS = ['Tu área', 'Tecnologías', 'Tu perfil']
const input = 'w-full rounded-md border border-slate-300 px-3 py-2 text-sm text-slate-900'

function Chip({ label, active, onClick }: { label: string; active: boolean; onClick: () => void }) {
  return (
    <button
      onClick={onClick}
      className={`rounded-full px-3 py-1.5 text-sm font-medium transition ${
        active ? 'bg-indigo-600 text-white' : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
      }`}
    >
      {label}
    </button>
  )
}

export default function OnboardingWizard({ onClose }: { onClose: () => void }) {
  const qc = useQueryClient()
  const { data: prefs, isLoading } = useQuery({ queryKey: ['preferences'], queryFn: fetchPreferences })

  const [step, setStep] = useState(0)
  const [categories, setCategories] = useState<string[]>([])
  const [techs, setTechs] = useState<string[]>([])
  const [seniority, setSeniority] = useState('')
  const [workMode, setWorkMode] = useState('')
  const [country, setCountry] = useState('')
  const [salary, setSalary] = useState('')
  const [showAll, setShowAll] = useState(false)
  const [custom, setCustom] = useState('')

  // Prefill desde lo guardado (editar = mismo asistente).
  useEffect(() => {
    if (!prefs) return
    setCategories(prefs.categories ?? [])
    setTechs(prefs.tech_stack ?? [])
    setSeniority(prefs.seniority ?? '')
    setWorkMode(prefs.work_mode ?? '')
    setCountry(prefs.country ?? '')
    setSalary(prefs.salary_target != null ? String(prefs.salary_target) : '')
  }, [prefs])

  const save = useMutation({
    mutationFn: () =>
      savePreferences({
        categories,
        tech_stack: techs,
        seniority: seniority || null,
        work_mode: workMode || null,
        country: country || null,
        salary_target: salary ? Number(salary) : null,
      }),
    onSuccess: async () => {
      await qc.invalidateQueries({ queryKey: ['preferences'] })
      await qc.invalidateQueries({ queryKey: ['feed'] })
      onClose()
    },
  })

  const toggleTech = (t: string) =>
    setTechs((prev) => (prev.includes(t) ? prev.filter((x) => x !== t) : [...prev, t]))

  const addCustom = () => {
    const t = custom.trim().toLowerCase()
    if (t && !techs.includes(t)) setTechs((prev) => [...prev, t])
    setCustom('')
  }

  const suggested = showAll ? ALL_TECHS : techsForRoles(categories)
  const techList = Array.from(new Set([...suggested, ...techs]))

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4" onClick={onClose}>
      <div className="w-full max-w-xl rounded-2xl bg-white p-6 shadow-xl" onClick={(e) => e.stopPropagation()}>
        {/* Progreso */}
        <div className="mb-1 flex items-center justify-between">
          <span className="text-xs font-medium text-indigo-600">
            Paso {step + 1} de {STEPS.length} · {STEPS[step]}
          </span>
          <button className="text-slate-400 hover:text-slate-600" onClick={onClose} aria-label="Cerrar">
            ✕
          </button>
        </div>
        <div className="mb-5 h-1.5 w-full overflow-hidden rounded-full bg-slate-100">
          <div
            className="h-full rounded-full bg-indigo-600 transition-all"
            style={{ width: `${((step + 1) / STEPS.length) * 100}%` }}
          />
        </div>

        {isLoading ? (
          <div className="py-10 text-center text-slate-400">Cargando…</div>
        ) : (
          <>
            {/* Paso 1: área */}
            {step === 0 && (
              <div>
                <h2 className="text-lg font-bold text-slate-900">¿En qué áreas te interesa trabajar?</h2>
                <p className="mb-4 text-sm text-slate-500">
                  Elige una o varias ({categories.length} seleccionadas). Tu feed priorizará ofertas de estas áreas.
                </p>
                <div className="grid grid-cols-2 gap-2 sm:grid-cols-3">
                  {ROLE_OPTIONS.map((r) => {
                    const active = categories.includes(r.key)
                    return (
                      <button
                        key={r.key}
                        onClick={() =>
                          setCategories((prev) => (active ? prev.filter((x) => x !== r.key) : [...prev, r.key]))
                        }
                        className={`flex flex-col items-center gap-1 rounded-xl border p-4 text-sm font-medium transition ${
                          active ? 'border-indigo-600 bg-indigo-50 text-indigo-700' : 'border-slate-200 hover:border-indigo-300'
                        }`}
                      >
                        <span className="text-2xl">{r.icon}</span>
                        {r.label}
                      </button>
                    )
                  })}
                </div>
                <p className="mt-3 text-xs text-slate-400">
                  ¿No lo tienes claro? Déjalo en blanco y te mostraremos todas las tecnologías.
                </p>
              </div>
            )}

            {/* Paso 2: tecnologías */}
            {step === 1 && (
              <div>
                <h2 className="text-lg font-bold text-slate-900">¿Qué tecnologías te interesan?</h2>
                <p className="mb-4 text-sm text-slate-500">
                  Marca las que te interesen ({techs.length} seleccionadas). Cuantas más, mejor afinará tu feed.
                </p>
                <div className="flex flex-wrap gap-2">
                  {techList.map((t) => (
                    <Chip key={t} label={t} active={techs.includes(t)} onClick={() => toggleTech(t)} />
                  ))}
                </div>
                {!showAll && (
                  <button className="mt-3 text-sm text-indigo-600 hover:underline" onClick={() => setShowAll(true)}>
                    Ver todas las tecnologías
                  </button>
                )}
                <div className="mt-4 flex gap-2">
                  <input
                    className={input}
                    placeholder="Añadir otra (ej. rust)…"
                    value={custom}
                    onChange={(e) => setCustom(e.target.value)}
                    onKeyDown={(e) => e.key === 'Enter' && (e.preventDefault(), addCustom())}
                  />
                  <button onClick={addCustom} className="rounded-md bg-slate-100 px-3 text-sm font-medium text-slate-600 hover:bg-slate-200">
                    Añadir
                  </button>
                </div>
              </div>
            )}

            {/* Paso 3: perfil */}
            {step === 2 && (
              <div className="space-y-4">
                <div>
                  <h2 className="text-lg font-bold text-slate-900">Cuéntanos un poco más</h2>
                  <p className="text-sm text-slate-500">Todo opcional, pero ayuda a afinar tu feed.</p>
                </div>
                <div>
                  <p className="mb-1 text-xs text-slate-500">Seniority</p>
                  <div className="flex flex-wrap gap-2">
                    {SENIORITY_ORDER.map((s) => (
                      <Chip
                        key={s}
                        label={seniorityLabel(s) ?? s}
                        active={seniority === s}
                        onClick={() => setSeniority(seniority === s ? '' : s)}
                      />
                    ))}
                  </div>
                </div>
                <div>
                  <p className="mb-1 text-xs text-slate-500">Modalidad</p>
                  <div className="flex gap-2">
                    {[
                      ['remote', 'Remoto'],
                      ['hybrid', 'Híbrido'],
                      ['onsite', 'Presencial'],
                    ].map(([k, l]) => (
                      <Chip key={k} label={l} active={workMode === k} onClick={() => setWorkMode(workMode === k ? '' : k)} />
                    ))}
                  </div>
                </div>
                <div className="grid grid-cols-2 gap-3">
                  <label className="flex flex-col text-xs text-slate-500">
                    País
                    <input className={input} placeholder="España…" value={country} onChange={(e) => setCountry(e.target.value)} />
                  </label>
                  <label className="flex flex-col text-xs text-slate-500">
                    Salario objetivo (USD)
                    <input className={input} type="number" min={0} placeholder="60000" value={salary} onChange={(e) => setSalary(e.target.value)} />
                  </label>
                </div>
              </div>
            )}

            {/* Footer */}
            <div className="mt-6 flex items-center justify-between">
              <button
                onClick={() => setStep((s) => Math.max(0, s - 1))}
                disabled={step === 0}
                className="text-sm text-slate-500 hover:text-slate-700 disabled:opacity-0"
              >
                ← Atrás
              </button>
              {step < STEPS.length - 1 ? (
                <button
                  onClick={() => setStep((s) => s + 1)}
                  className="rounded-md bg-indigo-600 px-5 py-2 text-sm font-semibold text-white hover:bg-indigo-700"
                >
                  Siguiente
                </button>
              ) : (
                <button
                  onClick={() => save.mutate()}
                  disabled={save.isPending}
                  className="rounded-md bg-indigo-600 px-5 py-2 text-sm font-semibold text-white hover:bg-indigo-700 disabled:opacity-50"
                >
                  {save.isPending ? 'Guardando…' : 'Guardar y ver mi feed'}
                </button>
              )}
            </div>
          </>
        )}
      </div>
    </div>
  )
}
