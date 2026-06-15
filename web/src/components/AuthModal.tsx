import { useState } from 'react'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { ApiError, login, register } from '../api'
import PasswordStrength from './PasswordStrength'

const input = 'w-full rounded-md border border-slate-300 px-3 py-2 text-sm text-slate-900 focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500'

export default function AuthModal({
  initialMode = 'login',
  onClose,
  onAuthed,
}: {
  initialMode?: 'login' | 'register'
  onClose: () => void
  onAuthed: (isNew: boolean) => void
}) {
  const qc = useQueryClient()
  const [mode, setMode] = useState<'login' | 'register'>(initialMode)
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [displayName, setDisplayName] = useState('')

  const m = useMutation({
    mutationFn: () =>
      mode === 'login' ? login(email, password) : register(email, password, displayName || undefined),
    onSuccess: async () => {
      await qc.invalidateQueries()
      onAuthed(mode === 'register')
    },
  })

  const err = m.error instanceof ApiError ? m.error.detail : m.error ? 'Algo salió mal' : null
  const switchTo = (next: 'login' | 'register') => {
    setMode(next)
    m.reset()
  }

  const tab = (key: 'login' | 'register', text: string) => (
    <button
      type="button"
      onClick={() => switchTo(key)}
      className={`flex-1 rounded-md px-3 py-1.5 text-sm font-medium transition ${
        mode === key ? 'bg-white text-slate-900 shadow-sm' : 'text-slate-500 hover:text-slate-700'
      }`}
    >
      {text}
    </button>
  )

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4" onClick={onClose}>
      <div className="w-full max-w-sm rounded-2xl bg-white p-6 shadow-xl" onClick={(e) => e.stopPropagation()}>
        <div className="mb-1 flex items-center justify-between">
          <h2 className="text-lg font-bold text-slate-900">
            {mode === 'login' ? 'Bienvenido de vuelta' : 'Crea tu cuenta'}
          </h2>
          <button className="text-slate-400 hover:text-slate-600" onClick={onClose} aria-label="Cerrar">
            ✕
          </button>
        </div>
        <p className="mb-4 text-sm text-slate-500">
          {mode === 'login'
            ? 'Entra para ver tu feed personalizado.'
            : 'Configura tu perfil y recibe ofertas a tu medida.'}
        </p>

        <div className="mb-4 flex gap-1 rounded-lg bg-slate-100 p-0.5">
          {tab('login', 'Entrar')}
          {tab('register', 'Crear cuenta')}
        </div>

        <form
          className="space-y-3"
          onSubmit={(e) => {
            e.preventDefault()
            m.mutate()
          }}
        >
          {mode === 'register' && (
            <input
              className={input}
              placeholder="Nombre (opcional)"
              value={displayName}
              onChange={(e) => setDisplayName(e.target.value)}
            />
          )}
          <input
            className={input}
            type="email"
            required
            placeholder="tucorreo@ejemplo.com"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
          />
          <input
            className={input}
            type="password"
            required
            minLength={mode === 'register' ? 10 : undefined}
            placeholder="Contraseña"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />
          {mode === 'register' && <PasswordStrength password={password} />}

          {err && <p className="rounded-md bg-red-50 px-3 py-2 text-sm text-red-600">{err}</p>}

          <button
            type="submit"
            disabled={m.isPending}
            className="w-full rounded-md bg-indigo-600 px-3 py-2.5 text-sm font-semibold text-white hover:bg-indigo-700 disabled:opacity-50"
          >
            {m.isPending ? 'Un momento…' : mode === 'login' ? 'Entrar' : 'Crear cuenta'}
          </button>
        </form>

        <p className="mt-4 text-center text-sm text-slate-500">
          {mode === 'login' ? (
            <>
              ¿Nuevo por aquí?{' '}
              <button className="font-medium text-indigo-600 hover:underline" onClick={() => switchTo('register')}>
                Crea una cuenta
              </button>
            </>
          ) : (
            <>
              ¿Ya tienes cuenta?{' '}
              <button className="font-medium text-indigo-600 hover:underline" onClick={() => switchTo('login')}>
                Inicia sesión
              </button>
            </>
          )}
        </p>
      </div>
    </div>
  )
}
