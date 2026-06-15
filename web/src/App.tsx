import { useState } from 'react'
import { useQueryClient } from '@tanstack/react-query'
import { logout } from './api'
import { useAuth } from './hooks/useAuth'
import AuthBar from './components/AuthBar'
import AuthModal from './components/AuthModal'
import Landing from './components/Landing'
import Dashboard from './components/Dashboard'
import AdminPanel from './components/AdminPanel'
import OnboardingWizard from './components/OnboardingWizard'

export default function App() {
  const qc = useQueryClient()
  const { user, isLoading } = useAuth()
  const [auth, setAuth] = useState<{ open: boolean; mode: 'login' | 'register' }>({ open: false, mode: 'login' })
  const [showWizard, setShowWizard] = useState(false)
  const [view, setView] = useState<'app' | 'admin'>('app')

  const handleLogout = async () => {
    await logout()
    await qc.invalidateQueries()
    setShowWizard(false)
    setView('app')
  }

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900">
      <header className="sticky top-0 z-40 border-b border-slate-200 bg-white/90 backdrop-blur">
        <div className="mx-auto flex max-w-6xl items-center justify-between px-4 py-3.5">
          <button
            onClick={() => setView('app')}
            className="flex items-center gap-2"
          >
            <span className="flex h-8 w-8 items-center justify-center rounded-lg bg-indigo-600 text-sm font-bold text-white">
              TJ
            </span>
            <span className="font-bold">Tech Job Market</span>
          </button>
          <AuthBar
            user={user}
            onAuth={(mode) => setAuth({ open: true, mode })}
            onLogout={handleLogout}
            onPrefs={() => {
              setView('app')
              setShowWizard(true)
            }}
            onAdmin={() => setView('admin')}
          />
        </div>
      </header>

      {isLoading ? (
        <div className="py-24 text-center text-slate-400">Cargando…</div>
      ) : !user ? (
        <Landing onAuth={(mode) => setAuth({ open: true, mode })} />
      ) : view === 'admin' && user.is_admin ? (
        <AdminPanel onBack={() => setView('app')} />
      ) : (
        <Dashboard user={user} onEditPrefs={() => setShowWizard(true)} />
      )}

      <footer className="mx-auto max-w-6xl px-4 py-8 text-center text-xs text-slate-400">
        Datos de RemoteOK, Remotive, Arbeitnow y Manfred. Proyecto educativo · enlaces a las ofertas originales.
      </footer>

      {auth.open && (
        <AuthModal
          initialMode={auth.mode}
          onClose={() => setAuth((a) => ({ ...a, open: false }))}
          onAuthed={(isNew) => {
            setAuth((a) => ({ ...a, open: false }))
            setView('app')
            if (isNew) setShowWizard(true) // onboarding: asistente de preferencias al registrarse
          }}
        />
      )}

      {showWizard && user && <OnboardingWizard onClose={() => setShowWizard(false)} />}
    </div>
  )
}
