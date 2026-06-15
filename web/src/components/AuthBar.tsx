import type { User } from '../api'

export default function AuthBar({
  user,
  onAuth,
  onLogout,
  onPrefs,
  onAdmin,
}: {
  user: User | null
  onAuth: (mode: 'login' | 'register') => void
  onLogout: () => void
  onPrefs: () => void
  onAdmin: () => void
}) {
  if (!user) {
    return (
      <div className="flex items-center gap-2">
        <button
          onClick={() => onAuth('login')}
          className="rounded-md px-3 py-1.5 text-sm font-medium text-slate-600 hover:bg-slate-100"
        >
          Entrar
        </button>
        <button
          onClick={() => onAuth('register')}
          className="rounded-md bg-indigo-600 px-3 py-1.5 text-sm font-medium text-white hover:bg-indigo-700"
        >
          Crear cuenta
        </button>
      </div>
    )
  }

  const initial = (user.display_name ?? user.email).charAt(0).toUpperCase()

  return (
    <div className="flex items-center gap-3 text-sm">
      <div className="flex items-center gap-2">
        <span className="flex h-7 w-7 items-center justify-center rounded-full bg-indigo-100 text-xs font-semibold text-indigo-700">
          {initial}
        </span>
        <span className="hidden text-slate-600 sm:inline">{user.display_name ?? user.email}</span>
      </div>
      {user.is_admin && (
        <button onClick={onAdmin} className="rounded-md px-2 py-1 text-amber-600 hover:bg-amber-50">
          Admin
        </button>
      )}
      <button onClick={onPrefs} className="rounded-md px-2 py-1 text-indigo-600 hover:bg-indigo-50">
        Preferencias
      </button>
      <button onClick={onLogout} className="rounded-md px-2 py-1 text-slate-500 hover:bg-slate-100">
        Salir
      </button>
    </div>
  )
}
