// Medidor de fuerza de contraseña: feedback en vivo (no bloquea; el backend solo
// exige ≥10 caracteres, pero animamos a algo más fuerte).

function strength(pw: string): number {
  if (!pw) return 0
  let s = 0
  if (pw.length >= 10) s++
  if (pw.length >= 14) s++
  if (/[a-z]/.test(pw) && /[A-Z]/.test(pw)) s++
  if (/\d/.test(pw) && /[^A-Za-z0-9]/.test(pw)) s++
  // Sin la longitud mínima, nunca pasa de "débil".
  return pw.length < 10 ? Math.min(s, 1) : Math.min(s, 4)
}

const LEVELS = [
  { label: '', bar: 'bg-slate-200', text: 'text-slate-400' },
  { label: 'Débil', bar: 'bg-red-500', text: 'text-red-600' },
  { label: 'Aceptable', bar: 'bg-amber-500', text: 'text-amber-600' },
  { label: 'Fuerte', bar: 'bg-lime-500', text: 'text-lime-600' },
  { label: 'Excelente', bar: 'bg-emerald-500', text: 'text-emerald-600' },
]

export default function PasswordStrength({ password }: { password: string }) {
  const s = strength(password)
  const level = LEVELS[s]
  const okLen = password.length >= 10

  return (
    <div className="space-y-1.5">
      <div className="flex gap-1">
        {[1, 2, 3, 4].map((i) => (
          <div key={i} className={`h-1.5 flex-1 rounded-full ${i <= s ? level.bar : 'bg-slate-200'}`} />
        ))}
      </div>
      <div className="flex items-center justify-between text-xs">
        <span className={okLen ? 'text-emerald-600' : 'text-slate-400'}>
          {okLen ? '✓' : '○'} Mínimo 10 caracteres
        </span>
        {password && level.label && <span className={`font-medium ${level.text}`}>{level.label}</span>}
      </div>
      {password && s < 3 && (
        <p className="text-xs text-slate-400">Combina mayúsculas, números y símbolos para reforzarla.</p>
      )}
    </div>
  )
}
