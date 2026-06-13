# 09 · Seguridad 🔒 (PRIORIDAD MÁXIMA)

> **Principio rector:** la seguridad no es una fase al final, es una **decisión en cada
> línea de código**. Al ser un producto público con cuentas, somos responsables de los
> datos de otras personas. Esto se construye bien **desde el día 1**, no se parchea después.

Este documento es la **checklist de seguridad** del proyecto. Revísalo en cada fase.

---

## 🔑 1. Autenticación

### Contraseñas (si hay email+password)
- **NUNCA** guardar contraseñas en texto plano. Hashing con **argon2id** (preferido) o
  **bcrypt** (cost ≥ 12). Nunca MD5/SHA1.
- El hashing incluye **salt** automático (argon2/bcrypt ya lo hacen). No reinventar.
- **Política mínima:** longitud mínima razonable (p. ej. ≥ 10), y comprobar contra
  listas de contraseñas filtradas (ej. API de HaveIBeenPwned con k-anonymity) si se quiere subir nivel.
- **No revelar** si un email existe en errores de login ("credenciales inválidas",
  genérico) → evita enumeración de usuarios.

### OAuth (GitHub)
- Validar el parámetro **`state`** (anti-CSRF en el flujo OAuth).
- Usar **PKCE** si el proveedor lo soporta.
- Guardar **solo lo necesario** del perfil OAuth (id, email, nombre). No pedir scopes de más.
- Los **secrets de OAuth** (client secret) van en variables de entorno, **nunca** en el repo.

### Sesiones / tokens
- **Recomendado MVP:** sesiones server-side con **cookie httpOnly + Secure + SameSite=Lax/Strict**.
  - `httpOnly` → JS no puede leer la cookie (mitiga robo por XSS).
  - `Secure` → solo se envía por HTTPS.
  - `SameSite` → mitiga CSRF.
- Si se usa **JWT:** access token corto (15 min) + refresh token; firmar con secreto
  fuerte; poder revocar (lista de revocación o refresh rotativo).
- **Expiración** de sesión y opción de "cerrar sesión en todos los dispositivos".

---

## 🛡️ 2. Autorización y aislamiento por usuario

- **Toda** consulta a datos personales (`user_preferences`, `saved_jobs`, `alerts`)
  filtra por el `user_id` **del token/sesión**, nunca por un id que venga del cliente.
- Validar **propiedad del recurso** antes de leer/modificar/borrar
  (ej. `DELETE /saved_jobs/:id` debe comprobar que ese registro es del usuario actual).
- Evitar **IDOR** (Insecure Direct Object Reference): que cambiar un id en la URL no
  dé acceso a datos de otro.
- Principio de **mínimo privilegio** en todo (DB, tokens, scopes OAuth).

---

## 💉 3. Inyección y validación de entrada

- **SQL Injection:** usar **siempre consultas parametrizadas** / ORM. **Jamás**
  concatenar strings en SQL. (Aplica a Go y Python por igual.)
- **Validación de entrada:** validar y normalizar TODO lo que llega del cliente
  (tipos, rangos, longitudes, formato). En FastAPI → Pydantic; en Go → validación explícita.
- **Allowlist > denylist:** aceptar lo conocido-bueno en vez de intentar bloquear lo malo.
- **Tamaño de payloads:** limitar el body de las requests para evitar abusos.

---

## 🧨 4. Ataques web comunes

| Ataque | Mitigación |
|--------|------------|
| **XSS** | Escapar/encodear salida; React ya escapa por defecto (evitar `dangerouslySetInnerHTML`); `Content-Security-Policy` |
| **CSRF** | Cookies `SameSite` + token anti-CSRF en formularios que muten estado |
| **Clickjacking** | Cabecera `X-Frame-Options: DENY` / CSP `frame-ancestors` |
| **Open redirect** | No redirigir a URLs arbitrarias del query string; validar contra allowlist |
| **SSRF** (¡ojo en el scraper!) | Ver sección 7 |

### Cabeceras de seguridad recomendadas
```
Content-Security-Policy: default-src 'self'; ...
X-Frame-Options: DENY
X-Content-Type-Options: nosniff
Referrer-Policy: strict-origin-when-cross-origin
Strict-Transport-Security: max-age=63072000; includeSubDomains
```

---

## 🚦 5. Rate limiting y abuso

- **Rate limit en endpoints sensibles:** login, registro, recuperación de contraseña
  (mitiga fuerza bruta y enumeración).
- **Lockout / backoff progresivo** tras varios intentos fallidos de login.
- Rate limit general por IP/usuario en la API pública.
- **CAPTCHA** en registro si aparece spam (extensión).

---

## 🔐 6. Gestión de secretos y configuración

- **Nada de secretos en el repo.** Ni claves, ni tokens, ni contraseñas de DB.
- Usar **variables de entorno** + un archivo **`.env`** que esté en **`.gitignore`**.
- Incluir un **`.env.example`** (sin valores reales) para documentar qué variables hacen falta.
- En producción: usar el **gestor de secretos** del PaaS (Fly/Railway/Render).
- **Rotar** secretos si se filtran. Considerar un escáner de secretos en CI (ej. gitleaks).
- Conexión a Postgres con **usuario de mínimos privilegios**, no superusuario.

---

## 🕷️ 7. Seguridad específica del scraper

- **SSRF:** el scraper hace peticiones a URLs. Si alguna URL llegara a ser
  influenciable por un usuario, validar el destino contra una **allowlist de dominios**
  y bloquear IPs internas/privadas (`127.0.0.1`, `169.254.x`, rangos privados).
- **Validar/sanear** todo dato externo antes de procesar o almacenar (no confiar en el HTML/JSON de terceros).
- **Timeouts** en todas las peticiones HTTP (evitar cuelgues).
- Tamaño máximo de respuesta (evitar que una fuente devuelva GB y agote memoria).
- (Recordatorio ético/legal en [07 · Ética y legalidad](./07-etica-y-legalidad.md).)

---

## 🌐 8. Transporte y red

- **HTTPS en todo** producción (TLS). HSTS activado.
- **CORS** restringido al dominio del frontend, no `*`.
- No exponer puertos internos (DB) a internet.

---

## 📦 9. Dependencias y supply chain

- **Escaneo de dependencias** en CI: `govulncheck` (Go), `pip-audit` (Python), `npm audit` (front).
- **Dependabot** / renovate para actualizaciones de seguridad.
- Fijar versiones (lockfiles) y revisar antes de actualizar.

---

## 👁️ 10. Logging, errores y privacidad

- **No loguear** datos sensibles: contraseñas, tokens, cookies, PII innecesaria.
- **Errores genéricos** al usuario; el detalle (stack trace) solo en logs internos.
- **Logs estructurados** para auditoría de eventos de seguridad (logins, cambios de cuenta).
- **RGPD:** permitir **borrar la cuenta** y todos sus datos; pedir solo lo necesario;
  consentimiento explícito para emails de alertas.

---

## ✅ Checklist por fase

| Fase | Foco de seguridad |
|------|-------------------|
| **0 · Cimientos** | `.gitignore` con `.env`; `.env.example`; usuario DB de mínimos privilegios |
| **1-3 · Scraper/ETL** | Consultas parametrizadas; timeouts HTTP; saneo de datos externos; anti-SSRF |
| **4 · API/Dashboard** | Validación de entrada; CORS; cabeceras de seguridad; React sin `dangerouslySetInnerHTML` |
| **4.5 · Cuentas** | Hashing argon2/bcrypt; cookies httpOnly+Secure+SameSite; rate limit login; autorización/IDOR; OAuth `state` |
| **5 · Automatización** | Secretos del scheduler en env; sin credenciales en logs |
| **6 · Deploy** | HTTPS+HSTS; secretos en gestor del PaaS; escaneo de deps en CI; escáner de secretos |

---

## 🎓 Por qué esto es ORO para el CV

La mayoría de proyectos junior **ignoran la seguridad por completo**. Documentar y
aplicar esto demuestra **mentalidad de ingeniería seria**. En el README, una sección
"Security" que explique estas decisiones te diferencia muchísimo — y es de lo primero
que mira un buen revisor técnico.

> Frase para el README: *"Auth con argon2 + OAuth (state validado), sesiones httpOnly,
> consultas parametrizadas, rate limiting en login, secretos fuera del repo y escaneo de
> dependencias en CI."*
