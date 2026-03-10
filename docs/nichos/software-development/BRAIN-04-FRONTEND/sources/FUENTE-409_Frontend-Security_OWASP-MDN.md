---
source_id: "FUENTE-409"
brain: "brain-software-04-frontend-architecture"
niche: "software-development"
title: "Frontend Security: XSS, CSRF, CSP y Seguridad en el Browser — Guía Consolidada"
author: "OWASP Foundation + MDN Web Docs + Google Security Team"
expert_id: "EXP-409"
type: "guide"
language: "en"
year: 2024
isbn: "N/A"
url: "https://owasp.org/www-project-top-ten/ + https://developer.mozilla.org/en-US/docs/Web/Security + https://web.dev/security"
skills_covered: ["H1", "H3", "H8"]
distillation_date: "2026-02-26"
distillation_quality: "complete"
loaded_in_notebook: true
version: "1.0.0"
last_updated: "2026-02-26"
changelog:
  - version: "1.0.0"
    date: "2026-02-26"
    changes:
      - "Ficha creada — gap crítico de seguridad ausente en versión inicial del Cerebro #4"
status: "active"

habilidad_primaria: "Seguridad Frontend — XSS, CSRF, CSP, Sanitización"
habilidad_secundaria: "Prácticas defensivas en el browser y handoff seguro con Backend (#5)"
capa: 2
capa_nombre: "Frameworks Operativos"
relevancia: "CRÍTICA — Un bug de seguridad puede comprometer a todos los usuarios del producto. La seguridad frontend no es responsabilidad exclusiva del backend."
gap_que_cubre: "Seguridad frontend — completamente ausente en las 8 fuentes originales del Cerebro #4"
---

# FUENTE-409: Frontend Security — XSS, CSRF, CSP y Seguridad en el Browser

## Tesis Central

> El frontend es la primera línea de ataque, no la primera línea de defensa. Un desarrollador frontend que no entiende XSS, CSRF y CSP construye aplicaciones que pueden ser comprometidas por cualquier atacante con conocimiento básico. La seguridad no es una feature del backend; es una responsabilidad compartida que empieza en el HTML que se renderiza.

La regla de oro: **nunca confiar en input del usuario, nunca confiar en datos que vienen de fuera del sistema, y nunca asumir que el DOM es seguro.**

---

## 1. Principios Fundamentales

> **P1: Defense in Depth — La defensa nunca es una sola capa**
> Ninguna medida de seguridad es suficiente por sí sola. XSS puede bypassearse con un vector no anticipado; CSP puede configurarse mal. El frontend debe implementar múltiples capas: escape de output, sanitización de input, CSP, SRI, y validación. Si una capa falla, las otras contienen el daño.
> *Aplica a: cualquier punto donde el frontend procesa o renderiza datos externos.*

> **P2: Principio del Mínimo Privilegio — Solo pedir lo que se necesita**
> El browser tiene APIs poderosas (cámara, micrófono, geolocalización, localStorage, cookies). Pedir solo los permisos necesarios. Si una librería de terceros no necesita acceso al DOM completo, no dárselo. Si una cookie no necesita ser accesible desde JS, marcarla `HttpOnly`.
> *Aplica a: configuración de cookies, permisos de browser APIs, configuración de iframes.*

> **P3: Sanitizar != Validar — Son operaciones distintas con propósitos distintos**
> Validación: verificar que el dato tiene el formato correcto (ej: es un email válido). Sanitización: limpiar el dato para que no pueda ejecutar código malicioso cuando se use. Ambas son necesarias. Un email puede ser válido según formato pero contener un payload XSS si se inserta en el DOM sin sanitizar.
> *Aplica a: todo punto donde datos externos llegan al DOM.*

> **P4: Los Errores No Deben Filtrar Información Sensible**
> Los stack traces, mensajes de error detallados, y respuestas de API con IDs internos o rutas del servidor son información útil para un atacante. El frontend muestra mensajes de error user-friendly; los detalles técnicos solo en logs privados.
> *Aplica a: error boundaries, error handling global, mensajes de validación.*

> **P5: Dependencias de Terceros Son Superficie de Ataque**
> Cada npm package que se instala tiene potencial de introducir vulnerabilidades (supply chain attacks). `npm audit`, Snyk, y Subresource Integrity (SRI) para scripts externos son las herramientas de mitigación.
> *Aplica a: gestión de dependencias, CDN scripts, actualizaciones de paquetes.*

---

## 2. Frameworks y Metodologías

### Framework 1: El Modelo de Amenazas Frontend

**Propósito:** Identificar sistemáticamente los vectores de ataque antes de construir una feature.

**Preguntas de evaluación de amenaza (antes de implementar):**
1. ¿Esta feature recibe input del usuario? → Sanitizar antes de usar
2. ¿Esta feature renderiza datos externos al DOM? → Escapar el output
3. ¿Esta feature hace requests a APIs? → Verificar autenticación/autorización
4. ¿Esta feature usa localStorage/sessionStorage? → Nunca guardar tokens sensibles ahí si hay riesgo XSS
5. ¿Esta feature carga scripts o recursos de terceros? → Usar SRI
6. ¿Esta feature expone URLs con datos sensibles? → Usar POST, no GET con params

**Output esperado:** Una lista de riesgos identificados con mitigación asignada antes de codificar.

---

### Framework 2: XSS Prevention (Cross-Site Scripting)

**Propósito:** Prevenir la ejecución de código malicioso en el browser del usuario.

**Los 3 tipos de XSS y su mitigación:**

```
TIPO 1 — REFLECTED XSS
El payload viene en la URL o request y se refleja en la respuesta.
Ejemplo: /search?q=<script>alert('xss')</script>
Mitigación: Escapar output al renderizar. React lo hace por default con JSX.

TIPO 2 — STORED XSS
El payload se guarda en la base de datos y se sirve a otros usuarios.
Ejemplo: Un comentario que contiene <img src=x onerror="robarCookies()">
Mitigación: Sanitizar en el servidor antes de guardar Y escapar al renderizar.

TIPO 3 — DOM-BASED XSS
El payload nunca llega al servidor; el JS del cliente lee una fuente insegura
(URL hash, localStorage, postMessage) y escribe en el DOM.
Ejemplo: document.getElementById('output').innerHTML = location.hash.slice(1);
Mitigación: Nunca usar innerHTML con datos no-confiables. Usar textContent.
```

**Reglas anti-XSS en React/JavaScript:**

```javascript
// ❌ NUNCA hacer esto
<div dangerouslySetInnerHTML={{ __html: userInput }} />
element.innerHTML = userInput;
eval(userInput);
new Function(userInput)();
document.write(userInput);

// ✅ Hacer esto
<div>{userInput}</div>  // React escapa automáticamente

// Si necesitas HTML real de fuente confiable, sanitizar PRIMERO:
import DOMPurify from 'dompurify';
<div dangerouslySetInnerHTML={{ __html: DOMPurify.sanitize(trustedHtmlContent) }} />

// Para texto plano:
element.textContent = userInput;  // Nunca ejecuta HTML
```

**Output esperado:** Una aplicación donde ningún dato externo puede ejecutar código en el browser del usuario.

---

### Framework 3: Content Security Policy (CSP)

**Propósito:** Indicarle al browser qué fuentes de contenido son legítimas, bloqueando cualquier script o recurso no autorizado.

**CSP Header básico para una SPA:**
```
Content-Security-Policy:
  default-src 'self';
  script-src 'self' 'nonce-{random}';
  style-src 'self' 'unsafe-inline';
  img-src 'self' data: https:;
  font-src 'self' https://fonts.gstatic.com;
  connect-src 'self' https://api.tudominio.com;
  frame-ancestors 'none';
```

**Directivas críticas:**
- `default-src 'self'`: Solo permitir recursos del mismo origen por default
- `script-src`: Controlar qué scripts pueden ejecutarse (usar nonces para inline scripts)
- `frame-ancestors 'none'`: Prevenir clickjacking (la página no puede embeberse en un iframe)
- `connect-src`: Controlar a qué URLs puede hacer fetch el JS

**Implementación en Next.js (next.config.js):**
```javascript
const securityHeaders = [
  {
    key: 'Content-Security-Policy',
    value: "default-src 'self'; script-src 'self' 'unsafe-eval' 'unsafe-inline';"
  },
  {
    key: 'X-Frame-Options',
    value: 'DENY'
  },
  {
    key: 'X-Content-Type-Options',
    value: 'nosniff'
  },
];

module.exports = {
  async headers() {
    return [{ source: '/(.*)', headers: securityHeaders }];
  },
};
```

---

### Framework 4: Autenticación Segura con Cookies vs Tokens

**El debate más común en frontend security:**

```
OPCIÓN A — JWT en localStorage
  Pros: Simple, funciona en SPAs
  Contras: Vulnerable a XSS. Cualquier script inyectado puede leer localStorage.
  → NUNCA para tokens de auth si el sitio tiene cualquier vector XSS.

OPCIÓN B — JWT en cookie HttpOnly + Secure
  Pros: No accesible desde JS (XSS no puede robarla)
  Contras: Necesita CSRF protection, más compleja de implementar
  → RECOMENDADA para auth tokens

OPCIÓN C — Short-lived JWT en memoria (variable JS)
  Pros: No persiste en disco, XSS solo funciona durante esa sesión
  Contras: Se pierde en cada refresh, necesita refresh token en cookie HttpOnly
  → BUENA para tokens de acceso de vida corta

IMPLEMENTACIÓN RECOMENDADA:
  - Access token: en memoria (variable de módulo, Zustand sin persistir)
  - Refresh token: en cookie HttpOnly + Secure + SameSite=Strict
  - Al refrescar la página: el refresh token en cookie genera un nuevo access token
```

**CSRF Protection cuando se usan cookies:**
```javascript
// El servidor envía un CSRF token en un header X-CSRF-Token
// El cliente lo lee y lo envía en cada request mutante

const csrfToken = document.cookie
  .split('; ')
  .find(row => row.startsWith('csrf='))
  ?.split('=')[1];

fetch('/api/action', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'X-CSRF-Token': csrfToken,
  },
  body: JSON.stringify(data),
});
```

---

## 3. Modelos Mentales

| Modelo | Descripción | Aplicación Práctica |
|--------|-------------|---------------------|
| **Trust Boundaries** | Delimitar qué datos vienen de fuentes confiables vs no confiables | Cualquier dato que viene del usuario, URL, localStorage, o APIs externas es "no confiable" hasta que se sanitiza |
| **Output Encoding** | El escape debe ocurrir en el momento de usar el dato, no al recibirlo | Si guardas el dato sin escapar y lo escapas al renderizar, el escape siempre es correcto para el contexto actual |
| **Fail Secure** | Cuando algo falla, fallar en el estado más seguro posible | Si la validación de CSRF falla, bloquear la acción, no ignorar el error |
| **Security by Default** | Las configuraciones por default deben ser las más seguras | CSP restrictivo por default, `SameSite=Strict` en cookies por default, `HttpOnly` por default |
| **Attack Surface Minimization** | Cuanto menos código y menos funcionalidad, menos vectores de ataque | Eliminar dependencias no usadas, deshabilitar features de browser no necesarias, no exponer información en URLs |

---

## 4. Criterios de Decisión

| Situación | Prioriza | Sobre | Por qué |
|-----------|----------|-------|---------|
| ¿Dónde guardar el auth token? | Cookie HttpOnly | localStorage | localStorage es accesible por cualquier script en la página |
| ¿Cómo renderizar HTML de usuario? | DOMPurify + `dangerouslySetInnerHTML` | `innerHTML` directo | DOMPurify elimina vectores de ataque manteniendo el HTML legítimo |
| ¿Cómo cargar scripts de CDN? | Con SRI hash (`integrity=`) | Sin atributo integrity | SRI garantiza que el script no fue modificado en el CDN |
| ¿Cómo configurar CSP inicial? | `default-src 'self'` estricto + whitelist explícita | `unsafe-inline` / `unsafe-eval` globales | Evitar `unsafe-inline` hace que scripts inyectados no se ejecuten |
| ¿Mensajes de error para el usuario? | Mensajes genéricos + log interno | Stack traces completos al usuario | Los detalles técnicos ayudan al atacante a entender la arquitectura |

---

## 5. Anti-patrones

| Anti-patrón | Por qué es malo | Qué hacer en su lugar |
|-------------|-----------------|----------------------|
| `innerHTML` con datos del usuario | Ejecuta HTML y scripts del atacante | `textContent` para texto, `DOMPurify` para HTML |
| Auth token en `localStorage` | XSS puede robarlo y enviarlo al servidor del atacante | Cookie `HttpOnly` + `Secure` + `SameSite=Strict` |
| `eval()` con cualquier dato externo | Ejecuta código arbitrario | No usar `eval`; refactorizar la lógica que lo necesita |
| CSP con `unsafe-inline` global | Anula la protección de CSP contra XSS | Usar nonces para scripts inline legítimos |
| Filtrar errores sin sanitizar en la UI | Expone rutas, IDs internos, stack traces al atacante | Mapear errores técnicos a mensajes de usuario genéricos |
| Dependencias sin auditar | Un paquete comprometido en la supply chain puede insertar XSS | `npm audit` + Snyk + Dependabot en CI |
| URLs con datos sensibles (GET params) | Aparece en logs del servidor, referrer headers, historial del browser | POST para operaciones sensibles; tokens en headers, no URLs |

---

## 6. Casos y Ejemplos Reales

### Caso 1: British Airways — XSS que robó datos de tarjetas de crédito (2018)

- **Situación:** Atacantes inyectaron 22 líneas de JavaScript en la página de pago de British Airways a través de una librería de terceros comprometida.
- **Decisión del atacante:** Aprovechar que el script de terceros se cargaba sin SRI y sin CSP restrictiva.
- **Resultado:** 500,000 clientes expuestos, datos de tarjetas de crédito robados, multa de £20 millones del ICO.
- **Lección:** SRI en todos los scripts de terceros. CSP que bloquee scripts no listados explícitamente. No asumir que los CDNs son seguros.

### Caso 2: GitHub — Stored XSS en comentarios de código (2013)

- **Situación:** GitHub tenía una vulnerabilidad en el renderizado de Markdown que permitía inyectar HTML en comentarios.
- **Decisión de GitHub al corregirla:** Implementar un sanitizador de HTML estricto (whitelist de tags permitidos) + CSP header que bloqueara scripts inline.
- **Resultado:** La vulnerabilidad fue corregida y el patrón de sanitización se volvió estándar en la industria.
- **Lección:** Sanitizar HTML con whitelist (solo permitir `<b>`, `<i>`, `<code>`, etc.) es más seguro que blacklist (bloquear `<script>`). Los atacantes siempre encuentran vectores no listados en la blacklist.

### Caso 3: Implementación de Auth en una SPA moderna

- **Situación:** Un equipo construía una SPA en React que necesitaba autenticación con JWT.
- **Decisión inicial:** Guardar el JWT en localStorage por simplicidad.
- **Problema descubierto:** Una librería de analytics de terceros tenía un bug que permitía XSS. Los tokens habrían sido robados.
- **Corrección:** Access token en memoria (Zustand sin `persist`), refresh token en cookie `HttpOnly`. Al recargar la página, un refresh silencioso en el servidor usa la cookie para generar un nuevo access token.
- **Resultado:** La SPA mantiene la misma UX (no pide login en cada refresh) con seguridad comparable a cookie-based auth.
- **Lección:** El patrón "token en memoria + refresh en cookie HttpOnly" tiene lo mejor de ambos mundos: no persiste el token sensible en disco, pero mantiene la sesión entre refreshes.

---

## Conexión con el Cerebro #4

| Habilidad del Cerebro | Aporte de esta fuente |
|------------------------|----------------------|
| Implementación de autenticación | Framework de decisión: token en memoria + refresh en cookie HttpOnly |
| Renderizado de contenido de usuario | Reglas anti-XSS: cuándo usar `textContent`, `DOMPurify`, y nunca `innerHTML` |
| Configuración del proyecto | CSP headers en Next.js, SRI en scripts externos |
| Handoff con Cerebro #5 (Backend) | CSRF protection, autenticación correcta, validación de inputs |
| Code reviews | Checklist de seguridad para revisar código de otros |

---

## Preguntas que el Cerebro puede responder

1. ¿Es seguro guardar el JWT en localStorage?
2. ¿Cómo renderizo HTML que viene del servidor sin abrir vectores XSS?
3. ¿Qué CSP Header necesita esta aplicación Next.js?
4. ¿Por qué esta cookie de auth debe tener `HttpOnly`, `Secure` y `SameSite`?
5. ¿Cómo implemento CSRF protection en las mutaciones de esta API?
6. ¿Qué riesgos introduce esta librería de terceros y cómo los mitigamos?
7. ¿Por qué no debo mostrar este error de API directamente al usuario?
