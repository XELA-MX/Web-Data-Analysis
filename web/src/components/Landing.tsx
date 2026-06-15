import { useQuery } from '@tanstack/react-query'
import { fetchOverview, fetchTopTech } from '../api'

const FEATURES = [
  { icon: '📊', title: 'Tendencias del mercado', text: 'Las tecnologías más demandadas y los rangos salariales, en gráficas claras.' },
  { icon: '🎯', title: 'Feed personalizado', text: 'Ofertas ordenadas por afinidad con tu stack, seniority y modalidad.' },
  { icon: '🔍', title: 'Filtros potentes', text: 'Filtra por categoría, tecnología, seniority, remoto o fuente sin perderte.' },
  { icon: '💰', title: 'Salarios reales', text: 'Miles de ofertas con rango salarial declarado, sobre todo en España.' },
  { icon: '💾', title: 'Guarda y descarta', text: 'Organiza tu búsqueda: marca lo que te interesa y oculta lo que no.' },
  { icon: '🌍', title: 'En tu idioma', text: 'Ofertas en español (Manfred) además de remoto global en inglés.' },
]

const STEPS = [
  { n: 1, title: 'Reunimos las ofertas', text: 'Rastreamos varias fuentes con APIs públicas, respetando sus términos.' },
  { n: 2, title: 'Las enriquecemos', text: 'Extraemos stack, salario, seniority y categoría, y quitamos duplicados.' },
  { n: 3, title: 'Tú decides', text: 'Exploras el mercado y recibes un feed hecho a tu medida.' },
]

const SOURCES = ['RemoteOK', 'Remotive', 'Arbeitnow', 'Manfred']

export default function Landing({ onAuth }: { onAuth: (mode: 'login' | 'register') => void }) {
  const { data: overview } = useQuery({ queryKey: ['overview'], queryFn: fetchOverview })
  const { data: topTech } = useQuery({ queryKey: ['tech'], queryFn: () => fetchTopTech(12) })

  return (
    <main>
      {/* Hero */}
      <section className="bg-gradient-to-br from-indigo-600 via-indigo-600 to-violet-600 text-white">
        <div className="mx-auto max-w-5xl px-4 py-20 text-center">
          <h1 className="text-4xl font-extrabold tracking-tight sm:text-5xl">
            Encuentra tu próximo trabajo tech, con datos
          </h1>
          <p className="mx-auto mt-5 max-w-2xl text-lg text-indigo-100">
            Reunimos miles de ofertas de varias fuentes y te mostramos qué se pide, dónde y cuánto pagan.
            Crea tu perfil y recibe ofertas hechas a tu medida.
          </p>
          <div className="mt-8 flex flex-wrap justify-center gap-3">
            <button
              onClick={() => onAuth('register')}
              className="rounded-lg bg-white px-6 py-3 text-sm font-semibold text-indigo-700 shadow hover:bg-indigo-50"
            >
              Crear cuenta gratis
            </button>
            <button
              onClick={() => onAuth('login')}
              className="rounded-lg border border-white/40 px-6 py-3 text-sm font-semibold text-white hover:bg-white/10"
            >
              Ya tengo cuenta
            </button>
          </div>

          {overview && (
            <div className="mx-auto mt-10 flex max-w-lg flex-wrap justify-center gap-x-8 gap-y-2 text-indigo-100">
              <span>
                <b className="text-white">{overview.total_jobs.toLocaleString()}</b> ofertas
              </span>
              <span>
                <b className="text-white">{overview.remote_pct}%</b> remotas
              </span>
              <span>
                <b className="text-white">{overview.with_salary.toLocaleString()}</b> con salario
              </span>
              <span>
                <b className="text-white">{overview.sources}</b> fuentes
              </span>
            </div>
          )}
        </div>
      </section>

      {/* Features */}
      <section className="mx-auto max-w-6xl px-4 py-16">
        <h2 className="text-center text-2xl font-bold text-slate-900">Todo lo que necesitas para tu búsqueda</h2>
        <div className="mt-8 grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
          {FEATURES.map((f) => (
            <div key={f.title} className="rounded-xl bg-white p-5 shadow-sm ring-1 ring-slate-200">
              <div className="text-2xl">{f.icon}</div>
              <h3 className="mt-2 font-semibold text-slate-900">{f.title}</h3>
              <p className="mt-1 text-sm text-slate-500">{f.text}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Top tech preview (datos en vivo) */}
      {topTech && topTech.length > 0 && (
        <section className="bg-white py-16">
          <div className="mx-auto max-w-4xl px-4 text-center">
            <h2 className="text-2xl font-bold text-slate-900">Lo más pedido ahora mismo</h2>
            <p className="mt-1 text-sm text-slate-500">Datos reales de las ofertas que tenemos en este momento.</p>
            <div className="mt-6 flex flex-wrap justify-center gap-2">
              {topTech.map((t) => (
                <span key={t.tech} className="rounded-full bg-indigo-50 px-3 py-1.5 text-sm font-medium text-indigo-700">
                  {t.tech} <span className="text-indigo-400">· {t.count}</span>
                </span>
              ))}
            </div>
          </div>
        </section>
      )}

      {/* How it works */}
      <section className="mx-auto max-w-5xl px-4 py-16">
        <h2 className="text-center text-2xl font-bold text-slate-900">Cómo funciona</h2>
        <div className="mt-8 grid gap-6 sm:grid-cols-3">
          {STEPS.map((s) => (
            <div key={s.n} className="text-center">
              <div className="mx-auto flex h-10 w-10 items-center justify-center rounded-full bg-indigo-600 font-bold text-white">
                {s.n}
              </div>
              <h3 className="mt-3 font-semibold text-slate-900">{s.title}</h3>
              <p className="mt-1 text-sm text-slate-500">{s.text}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Sources */}
      <section className="bg-white py-12">
        <div className="mx-auto max-w-4xl px-4 text-center">
          <p className="text-sm font-medium text-slate-400">DATOS DE FUENTES PÚBLICAS</p>
          <div className="mt-4 flex flex-wrap items-center justify-center gap-x-8 gap-y-2 text-lg font-semibold text-slate-600">
            {SOURCES.map((s) => (
              <span key={s}>{s}</span>
            ))}
          </div>
          <p className="mt-4 text-xs text-slate-400">
            Priorizamos APIs oficiales y respetamos los términos de cada fuente. Enlazamos siempre a la oferta original.
          </p>
        </div>
      </section>

      {/* CTA final */}
      <section className="bg-slate-900 py-16 text-center text-white">
        <div className="mx-auto max-w-2xl px-4">
          <h2 className="text-2xl font-bold sm:text-3xl">Empieza a buscar con ventaja</h2>
          <p className="mt-2 text-slate-300">Gratis. Configura tu perfil en un minuto y recibe ofertas relevantes.</p>
          <button
            onClick={() => onAuth('register')}
            className="mt-6 rounded-lg bg-indigo-600 px-6 py-3 text-sm font-semibold text-white hover:bg-indigo-500"
          >
            Crear cuenta gratis
          </button>
        </div>
      </section>
    </main>
  )
}
