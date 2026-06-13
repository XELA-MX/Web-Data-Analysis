# 01 · Requisitos

## 🧩 Requisitos funcionales (RF)

### Scraping / ingesta
- **RF-01** — El sistema scrapea ofertas de empleo de al menos **1 fuente** (MVP) y
  hasta **3-4 fuentes** (objetivo).
- **RF-02** — Cada fuente se implementa tras una interfaz común `Scraper`, de forma
  que añadir una nueva fuente no afecte a las demás.
- **RF-03** — El scraping respeta `robots.txt` y aplica **rate limiting** configurable
  por fuente.
- **RF-04** — Si una fuente falla, el resto continúa (aislamiento de fallos).

### Procesado / enriquecimiento
- **RF-05** — Por cada oferta se extrae el **stack tecnológico** (`tech_stack[]`).
- **RF-06** — Se normaliza el **salario** a un rango (`salary_min`, `salary_max`,
  `currency`) cuando esté disponible.
- **RF-07** — Se infiere el **seniority** (junior / mid / senior) desde título/descripción.
- **RF-08** — Se detecta si la oferta es **remota**.
- **RF-09** — Se **deduplican** ofertas iguales publicadas en varias fuentes.

### Almacenamiento
- **RF-10** — Las ofertas limpias se persisten en **PostgreSQL**.
- **RF-11** — Se guarda histórico para poder analizar **tendencias en el tiempo**.

### API
- **RF-12** — API REST con endpoints de:
  - búsqueda y filtrado de ofertas (por tech, ubicación, remoto, seniority, salario),
  - agregaciones (top tecnologías, rangos salariales, % remoto),
  - series temporales (evolución de la demanda).

### Dashboard
- **RF-13** — Visualización de **tecnologías más demandadas**.
- **RF-14** — Visualización de **rangos salariales** por stack y seniority.
- **RF-15** — Visualización de **distribución geográfica / % remoto**.
- **RF-16** — **Buscador** con filtros combinables.
- **RF-17** — Vista de **tendencias temporales**.

### Automatización
- **RF-18** — El scraping se ejecuta de forma **programada** (cada X horas).

### Cuentas y personalización
- **RF-19** — Los usuarios pueden **registrarse** e **iniciar sesión** (GitHub OAuth
  y/o email+contraseña).
- **RF-20** — Tras el registro, un **onboarding** captura su perfil: rol, stack de
  interés, seniority, modalidad (remoto/híbrido/presencial), ubicación.
- **RF-21** — El usuario puede **editar sus preferencias** en cualquier momento.
- **RF-22** — El **feed por defecto se personaliza** según las preferencias (filtrado).
- **RF-23** — Las ofertas se **ordenan por afinidad** con el perfil (scoring por match
  de stack/seniority).
- **RF-24** — El usuario puede **guardar / descartar** ofertas.
- **RF-25** — Los datos personales (preferencias, guardados) están **aislados por
  usuario**: nadie puede acceder a los de otro.
- **RF-26** — (Extensión) Alertas de nuevas ofertas que encajan con el perfil.

## ⚙️ Requisitos no funcionales (RNF)

| ID | Requisito | Detalle |
|----|-----------|---------|
| **RNF-01** | Rendimiento | Scraper concurrente; una pasada completa en minutos, no horas |
| **RNF-02** | Cortesía | Rate limit por dominio; `User-Agent` identificable |
| **RNF-03** | Robustez | Reintentos con backoff exponencial; tolerancia a fallos de fuente |
| **RNF-04** | Mantenibilidad | Código modular, interfaces claras, tests |
| **RNF-05** | Reproducibilidad | `docker compose up` levanta todo el sistema |
| **RNF-06** | Observabilidad | Logs estructurados; métricas básicas de scraping |
| **RNF-07** | Portabilidad | Funciona en local y en deploy cloud (free tier) |
| **RNF-08** | Calidad | CI con lint + tests en cada push |
| **RNF-09** | Seguridad | Contraseñas con hashing fuerte (bcrypt/argon2); HTTPS; rate limit en auth; cookies httpOnly |
| **RNF-10** | Privacidad | RGPD-friendly: pedir mínimos datos, permitir borrar cuenta y datos |

## 📋 Dependencias y supuestos

- Las fuentes elegidas exponen datos **públicos** (sin login).
- Se priorizan fuentes con **API/RSS/JSON** sobre HTML scraping cuando sea posible.
- Free tier de un PaaS (Fly.io / Railway / Render) es suficiente para el demo.
