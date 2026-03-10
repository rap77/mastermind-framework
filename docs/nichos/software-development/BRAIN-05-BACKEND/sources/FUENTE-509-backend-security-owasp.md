---
source_id: "FUENTE-509"
brain: "brain-software-05-backend"
niche: "software-development"
title: "Backend Security: OWASP Top 10 + Security Engineering Principles"
author: "Ross Anderson + OWASP Foundation"
expert_id: "EXP-005"
type: "guide"
language: "en"
year: 2021
url: "https://owasp.org/www-project-top-ten"
skills_covered: ["H5", "H6"]
distillation_date: "2026-02-27"
distillation_quality: "complete"
loaded_in_notebook: true
version: "1.0.0"
last_updated: "2026-02-27"
changelog:
  - version: "1.0.0"
    date: "2026-02-27"
    changes:
      - "Ficha creada con destilación completa"
      - "Formato estándar del MasterMind Framework"
status: "active"

habilidad_primaria: "Seguridad en aplicaciones backend — autenticación, autorización, protección de datos"
habilidad_secundaria: "OWASP Top 10 — las vulnerabilidades más críticas y cómo prevenirlas"
capa: 2
capa_nombre: "Frameworks"
relevancia: "CRÍTICA — La seguridad no es opcional. Un sistema no seguro tiene valor negativo: destruye la confianza del usuario y la reputación del producto."
gap_que_cubre: "Conocimiento de seguridad que todo backend engineer debe tener — el gap más peligroso si no está cubierto"
---

# FUENTE-509: Backend Security — OWASP Top 10 & Principios

## Tesis Central

> La seguridad no es una feature que se agrega al final — es una propiedad del sistema que debe estar presente desde el diseño. Las vulnerabilidades más devastadoras no son exploits sofisticados: son errores de implementación básicos que aparecen en el OWASP Top 10 año tras año. Conocerlos y prevenirlos es responsabilidad de todo backend engineer.
> Es el gap más crítico si no está cubierto — una brecha de seguridad puede destruir un producto.

---

## 1. Principios Fundamentales

> **P1: Defensa en Profundidad**
> Un sistema seguro tiene múltiples capas de defensa. Si una falla, hay otra. No depender de un solo mecanismo. Autenticación + Autorización + Validación de input + Encryption + Auditoría. Si falla la autenticación, la autorización es la segunda línea.
> *Contexto de aplicación: Al diseñar cualquier endpoint sensible. Listar todas las capas de seguridad y verificar que ninguna es el único punto de defensa.*

> **P2: Least Privilege — Mínimo Privilegio**
> Cada componente solo tiene los permisos que necesita para funcionar, nada más. Un microservicio de "lecturas de catálogo" no necesita acceso de escritura a la DB. Un usuario regular no necesita acceso a endpoints de administración.
> *Contexto de aplicación: Al configurar credenciales de DB, tokens de API, y roles de usuario. Siempre preguntar: ¿realmente necesita este permiso?*

> **P3: Nunca Confiar en el Input del Usuario**
> Todo input que viene del cliente es potencialmente malicioso. Validar, sanitizar, y escapar TODO lo que viene de fuera del sistema. Esto incluye headers HTTP, query params, bodies, cookies, y datos provenientes de APIs de terceros.
> *Contexto de aplicación: En la capa de entrada (controllers/middlewares). Nunca ejecutar SQL, HTML, o comandos construidos con input del usuario sin validación.*

> **P4: Fail Secure — Fallar de Forma Segura**
> Cuando el sistema falla, el comportamiento por defecto debe ser la denegación de acceso, no el permiso. Un error en la verificación de JWT no debe resultar en acceso concedido.
> *Contexto de aplicación: En los handlers de errores de autenticación/autorización. El catch de un error de verificación debe retornar 401/403, nunca continuar.*

> **P5: Audit Logging — Lo que No se Registra No se Puede Investigar**
> Todas las acciones sensibles deben quedar en un log de auditoría: logins, intentos fallidos, cambios de privilegios, acceso a datos sensibles. Sin logs, una brecha es indetectable e imposible de investigar.
> *Contexto de aplicación: En cualquier operación que involucre autenticación, autorización, o modificación de datos críticos. El log debe ser inmutable (append-only).*

---

## 2. Frameworks y Metodologías

### Framework 1: OWASP Top 10 — Las 10 Vulnerabilidades Críticas

**Propósito:** Catálogo de las vulnerabilidades más frecuentes y peligrosas en aplicaciones web.
**Cuándo usar:** Como checklist de revisión de seguridad en code review y auditorías.

| # | Vulnerabilidad | Descripción | Prevención |
|---|----------------|-------------|------------|
| A01 | **Broken Access Control** | Usuarios acceden a recursos que no les pertenecen. La más crítica del 2021. | RBAC o ABAC. Verificar ownership en CADA request. Default deny. |
| A02 | **Cryptographic Failures** | Datos sensibles sin cifrar o cifrado débil (MD5, SHA1). | HTTPS everywhere. bcrypt/Argon2 para passwords. AES-256 para datos en reposo. |
| A03 | **Injection (SQL, NoSQL, OS)** | Input del usuario ejecutado como código. SQL Injection destruyó bases de datos de millones. | Prepared statements siempre. ORMs. Nunca concatenar SQL con input. |
| A04 | **Insecure Design** | La arquitectura tiene fallas de seguridad desde el diseño. | Threat modeling. Security requirements desde el inicio. |
| A05 | **Security Misconfiguration** | Credenciales por defecto, puertos abiertos, errores verbosos en producción. | Hardening de configuración. Variables de entorno. No exponer stack traces. |
| A06 | **Vulnerable Components** | Dependencias con CVEs conocidas sin actualizar. | Usar `npm audit`. Actualizar dependencias regularmente. Dependabot/Renovate. |
| A07 | **Auth & Session Failures** | Passwords débiles, sessions sin expiración, tokens predecibles. | JWT con expiración corta. Refresh tokens. Rate limiting en login. MFA. |
| A08 | **Software & Data Integrity** | CI/CD sin verificación de integridad. Dependencias no verificadas. | Firmar commits. Verificar checksums. Pipelines con security gates. |
| A09 | **Logging & Monitoring Failures** | No detectar ni registrar ataques en curso. | Structured logging. Alertas en intentos fallidos de login. SIEM. |
| A10 | **Server-Side Request Forgery** | El servidor hace requests a URLs controladas por el atacante. | Validar y whitelist de URLs destino. No pasar URLs del cliente al servidor sin validación. |

---

### Framework 2: Autenticación y Autorización Seguros

**Propósito:** Implementar auth correctamente — la fuente más frecuente de brechas.
**Cuándo usar:** Al diseñar el sistema de autenticación y control de acceso.

**Pasos para Autenticación Segura:**
1. **Password Storage:** bcrypt (cost factor 12+) o Argon2id. NUNCA MD5, SHA1, o SHA256 para passwords.
2. **JWT:** Firmar con RS256 (asimétrico) o HS256 con secret de 256 bits. `exp` corto (15-60 min). `iat` siempre presente.
3. **Refresh Tokens:** Rotativos. Invalidar el anterior al usar. Almacenar en DB para poder revocar.
4. **Rate Limiting en Login:** Máximo 5-10 intentos por IP y por cuenta. Backoff exponencial. CAPTCHA tras fallos.
5. **Session Management:** HTTPOnly + Secure cookies. SameSite=Strict o Lax. Regenerar session ID tras login.

**Pasos para Autorización Segura:**
1. **Verificar autenticación** en CADA request (middleware).
2. **Verificar autorización** antes de CADA operación: ¿tiene este usuario permiso para esta acción sobre este recurso?
3. **Verificar ownership:** `WHERE id = ? AND user_id = ?` — nunca confiar en que el user_id del body es el correcto.
4. **Default deny:** Si no hay regla explícita de permiso, denegar.
5. **Principio de Least Privilege:** Roles granulares, no un solo rol de admin para todo.

---

## 3. Modelos Mentales

| Modelo | Descripción | Aplicación Práctica |
|--------|-------------|---------------------|
| **Threat Modeling** | Identificar sistemáticamente quién podría atacar, qué intentarían hacer, y cómo prevenirlo. STRIDE: Spoofing, Tampering, Repudiation, Info Disclosure, DoS, Elevation of Privilege. | Al diseñar un feature nuevo, preguntar: ¿cómo podría un atacante abusar de esto? Documentar las amenazas y las mitigaciones. |
| **Defense in Depth** | Capas concéntricas de seguridad. Si una falla, la siguiente la contiene. No un único mecanismo de defensa. | Auth → Authz → Input validation → Rate limiting → Audit log. No asumir que ninguna capa es infalible. |
| **Zero Trust** | No confiar en ninguna entidad por defecto, incluso dentro de la red interna. Verificar siempre, no importa el origen. | Entre microservicios: autenticación mutua (mTLS) o tokens de servicio. No asumir que un request interno es seguro. |
| **Principle of Least Privilege** | El mínimo acceso necesario. Un servicio de lectura no necesita acceso de escritura. Un usuario sin rol de admin no accede a endpoints de admin. | Al crear usuarios de DB: uno por servicio, con solo los permisos necesarios para ese servicio. |
| **Security by Obscurity no funciona** | Ocultar el puerto, el framework, o la tecnología no es seguridad. Un atacante dedicado lo descubre. La seguridad real viene de controles técnicos probados. | No confiar en "nadie sabe que esto existe". Implementar controles reales: auth, authz, encryption, rate limiting. |

---

## 4. Criterios de Decisión

| Situación | Prioriza | Sobre | Por qué |
|-----------|----------|-------|---------|
| Almacenar passwords | bcrypt (cost 12) o Argon2id | SHA-256, MD5, o cualquier hash sin salt | Los hashes rápidos son vulnerables a ataques de fuerza bruta. bcrypt/Argon2 son lentos por diseño. |
| Tokens de autenticación | JWT con expiración corta + refresh token rotativo | Sessions en DB o JWT sin expiración | JWT sin expiración no puede revocarse. Con refresh rotativo, la ventana de vulnerabilidad es mínima. |
| Queries con input del usuario | Prepared statements / Parameterized queries | String concatenation con input | La concatenación directa es SQL Injection. Los prepared statements separan datos de código. |
| Errores en producción | Mensajes genéricos al cliente + detalle en logs | Stack traces completos al cliente | Los stack traces revelan tecnología, estructura de archivos, y posibles vectores de ataque. |
| CORS en API | Whitelist explícita de orígenes | `Access-Control-Allow-Origin: *` | El wildcard permite que cualquier website haga requests autenticados a tu API desde el browser del usuario. |

---

## 5. Anti-patrones

| Anti-patrón | Por qué es malo | Qué hacer en su lugar |
|-------------|-----------------|----------------------|
| **SQL con concatenación de string** | `"SELECT * FROM users WHERE id = " + userId` — si `userId` es `1 OR 1=1`, retorna todos los usuarios. SQL Injection. | `db.query("SELECT * FROM users WHERE id = $1", [userId])` — prepared statement. |
| **Passwords hasheados con MD5 o SHA256** | Son hashes rápidos. Una GPU moderna prueba 10 mil millones de SHA256/segundo. Todas las passwords se descifran en minutos. | bcrypt (work factor 12) o Argon2id. Son lentos por diseño — 100ms por hash. |
| **JWT sin expiración** | Si el token es robado, es válido para siempre. No hay forma de invalidarlo. | JWT con `exp` corto (15-60 min) + Refresh token en DB (revocable). |
| **Errores verbosos en producción** | `Error: Connection to PostgreSQL at localhost:5432 failed` revela tecnología y arquitectura al atacante. | En producción: mensajes genéricos. En logs: el detalle completo. Configurar el middleware de errores correctamente. |
| **Verificar autorización solo en el frontend** | El frontend puede ser modificado por el usuario. Las verificaciones del frontend son solo UX, no seguridad. | Verificar autorización en CADA endpoint del backend. El frontend es untrusted. |

---

## 6. Casos y Ejemplos Reales

### Caso 1: Equifax Breach 2017 — Vulnerable Components

- **Situación:** La mayor brecha de datos en historia de EE.UU. 147 millones de registros expuestos.
- **Causa:** CVE-2017-5638 en Apache Struts — una vulnerabilidad conocida con patch disponible hace 2 meses. No actualizaron.
- **Resultado:** $700 millones en multas y acuerdos. Destrucción de reputación.
- **Lección:** Las dependencias desactualizadas son el vector de ataque más evitable. Automatizar `npm audit` y mantener un proceso de actualización de dependencias.

### Caso 2: SQL Injection en Formulario de Login

- **Situación:** Un e-commerce con query: `SELECT * FROM users WHERE email='` + email + `' AND password='` + password + `'`
- **Ataque:** Email = `admin@tienda.com' --` — el `--` comenta el resto del SQL. La query ignora el password.
- **Resultado:** Acceso a cualquier cuenta sin conocer el password.
- **Prevención:** `db.query("SELECT * FROM users WHERE email=$1 AND password_hash=$2", [email, hashedPassword])` — prepared statement hace imposible el injection.

### Caso 3: Broken Access Control — IDOR

- **Situación:** API endpoint: `GET /api/orders/:orderId`. No verifica que la orden pertenezca al usuario autenticado.
- **Ataque:** Un usuario autenticado cambia el orderId en la URL. Puede ver órdenes de otros usuarios.
- **Resultado:** Acceso a datos privados de todos los usuarios. Violación de GDPR/privacidad.
- **Prevención:** `WHERE id = $1 AND user_id = $2` — siempre verificar ownership en la query, no asumir que el ID es suficiente.

---

## Conexión con el Cerebro #5

| Habilidad del Cerebro | Aporte de esta fuente |
|-----------------------|----------------------|
| Autenticación segura | bcrypt/Argon2, JWT con refresh tokens, rate limiting |
| Autorización correcta | RBAC, verificación de ownership, default deny |
| Protección contra inyecciones | Prepared statements, validación de input |
| Configuración segura | Variables de entorno, errores no verbosos en producción |
| Auditoría y monitoring | Logging de eventos de seguridad |
| Gestión de dependencias | `npm audit`, Dependabot, actualización regular |

---

## Preguntas que el Cerebro puede responder

1. ¿Cómo almaceno los passwords de usuarios de forma segura?
2. ¿Cómo implemento JWT correctamente con refresh tokens?
3. ¿Cómo prevengo SQL Injection en mi aplicación?
4. ¿Cómo verifico que un usuario solo puede acceder a sus propios datos (Broken Access Control)?
5. ¿Cuáles son las vulnerabilidades más comunes en aplicaciones backend y cómo prevenirlas?
6. ¿Cómo configuro CORS correctamente en mi API?
