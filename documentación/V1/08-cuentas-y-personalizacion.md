# 08 · Cuentas de usuario y personalización

> **Cambio de alcance:** V1 será **público y multiusuario**. Cada usuario se registra,
> tiene su propia cuenta y una **experiencia personalizada** según su perfil e intereses.
> Esto convierte el proyecto en un **producto SaaS** (mucho mejor para el CV).

## 🎯 Objetivo

Que al registrarse, el usuario configure su perfil (rol, stack, preferencias) y a
partir de ahí vea un feed **relevante para él**: un dev frontend ve ofertas frontend,
quien busca remoto no ve presenciales, un junior no se ahoga en ofertas senior, etc.

> El ejemplo "un contador no debería ver ofertas de cocina" aplicado a nuestro dominio:
> **filtrar y priorizar ofertas por el perfil tech del usuario.**

## 🔐 Autenticación

### Recomendación: OAuth con GitHub (+ email/password opcional)
- **Por qué GitHub OAuth:** el público objetivo son **devs** → casi todos tienen GitHub.
  Reduce fricción (un clic) y evita gestionar contraseñas (menos superficie de seguridad).
  Además queda muy coherente con un producto para programadores.
- **Email + contraseña** como alternativa para quien no quiera usar GitHub.
- **Tokens:** JWT (access + refresh) o sesiones con cookie httpOnly. Para el MVP,
  **sesiones con cookie httpOnly** son más simples y seguras por defecto.

> ⚠️ Seguridad mínima innegociable: contraseñas con **hashing fuerte** (bcrypt/argon2),
> nunca en texto plano. HTTPS en producción. Rate limit en login/registro.
>
> 🔒 **La seguridad es PRIORIDAD MÁXIMA en este proyecto.** Todo lo relativo a auth,
> sesiones, autorización, validación y privacidad está detallado en
> [09 · Seguridad](./09-seguridad.md) — léelo antes de implementar cuentas.

### Decisión a confirmar
- [ ] ¿Solo GitHub OAuth, solo email/password, o ambos? _(recomendado: GitHub + email/password)_

## 🧭 Onboarding (al registrarse)

Un pequeño asistente captura las preferencias iniciales:

1. **Rol / categoría:** frontend, backend, fullstack, mobile, data, devops, QA...
2. **Stack de interés:** ej. `go`, `react`, `python`, `kubernetes`...
3. **Seniority objetivo:** junior / mid / senior.
4. **Modalidad:** remoto / híbrido / presencial.
5. **Ubicación / país** (si no es 100% remoto).
6. (Opcional) **Rango salarial deseado.**

Todo editable después desde "Ajustes".

## ✨ Cómo se personaliza la experiencia

| Mecanismo | Qué hace |
|-----------|----------|
| **Filtrado** | El feed por defecto aplica las preferencias del usuario (rol, stack, remoto, seniority) |
| **Ranking / scoring** | Las ofertas se ordenan por afinidad con el perfil (match de stack, seniority, etc.) |
| **Ofertas guardadas** | El usuario marca favoritas / descartadas |
| **Alertas** | Avisar de nuevas ofertas que encajan con su perfil |
| **Dashboard personal** | Tendencias filtradas por SU stack ("¿cómo está el mercado para MÍ?") |

> **MVP de personalización:** empezar por **filtrado + scoring simple** (cuántas de sus
> tecnologías aparecen en la oferta). El ranking sofisticado (ML/embeddings) es extensión futura.

## 🏢 Multitenencia (separación por cuentas)

- Los **datos de ofertas son compartidos** (un solo dataset global scrapeado).
- Lo que es **por usuario**: preferencias, ofertas guardadas/descartadas, alertas,
  historial. Todo ligado a `user_id`.
- **Aislamiento:** toda query "personal" filtra por el `user_id` autenticado. Un usuario
  **nunca** debe poder leer/modificar datos de otro → validar siempre la propiedad del recurso.

## 🗄️ Impacto en el modelo de datos

Nuevas tablas (detalle en [04 · Modelo de datos](./04-modelo-de-datos.md)):

- `users` — cuenta (id, email, provider, password_hash?, created_at...).
- `user_preferences` — rol, stack[], seniority, modalidad, ubicación, salario deseado.
- `saved_jobs` — relación usuario ↔ oferta (estado: guardada / descartada / aplicada).
- `alerts` — criterios de alerta por usuario (extensión).

Las ofertas (`jobs`) siguen siendo globales y compartidas.

## 🔒 Consideraciones de privacidad (RGPD-friendly)

- Pedir **solo los datos necesarios**.
- Permitir **borrar la cuenta** y sus datos.
- Si se usan emails para alertas → consentimiento explícito.
- No exponer datos personales en la API pública.

## 📌 Impacto en el roadmap

Se añade una fase de **Cuentas y personalización** (ver [05 · Roadmap](./05-roadmap.md)).
Recomendación: **construir primero el núcleo de datos (Fases 1-4) y luego añadir cuentas**,
para no acoplar autenticación a un pipeline que aún está cambiando.

## 🎓 Por qué esto mejora el CV

Pasar de "un scraper con dashboard" a "un producto multiusuario con auth, onboarding y
personalización" demuestra:
- **Autenticación y seguridad** (OAuth, hashing, sesiones).
- **Multitenencia** y aislamiento de datos por usuario.
- **Diseño de producto** (onboarding, UX personalizada).
- **Lógica de negocio** (scoring/ranking de relevancia).

Es exactamente el tipo de funcionalidad que tienen los SaaS reales → muy vendible.
