---
source_id: "FUENTE-415"
brain: "brain-software-04-frontend-architecture"
niche: "software-development"
title: "Anti-Patrones y Radar de Calidad — Cerebro #4 Frontend Architecture"
author: "Auto-generado | MasterMind Framework"
expert_id: "EXP-415"
type: "radar-interno"
language: "es"
year: 2026
isbn: "N/A"
url: "N/A"
skills_covered: ["H1", "H2", "H3", "H4", "H5", "H6", "H7"]
distillation_date: "2026-02-26"
distillation_quality: "complete"
loaded_in_notebook: true
version: "1.0.0"
last_updated: "2026-02-26"
changelog:
  - version: "1.0.0"
    date: "2026-02-26"
    changes:
      - "Radar creado — consolida anti-patrones de las 14 fuentes del Cerebro #4"
      - "60 anti-patrones catalogados: 14 críticos, 28 altos, 18 medios"
status: "active"

habilidad_primaria: "Auto-Evaluación y Control de Calidad del Frontend"
habilidad_secundaria: "Pre-Delivery Checklist y Score de Calidad"
capa: 3
capa_nombre: "Radar — Auto-generado"
relevancia: "CRÍTICA — Es el mecanismo de auto-evaluación del cerebro. Antes de cualquier handoff al Cerebro #5 (Backend) o al Cerebro #7 (Growth), el Cerebro #4 verifica sus outputs contra este radar."
---

# FUENTE-415: Anti-Patrones y Radar de Calidad
## Cerebro #4 — Frontend Architecture | Sistema de Auto-Evaluación

---

## Propósito

Este radar es el mecanismo de auto-evaluación del Cerebro #4. Antes de hacer merge a main, antes de un deploy, y antes de cualquier handoff al Cerebro #5 (Backend API) o al Cerebro #7 (Growth & Data), el Cerebro #4 verifica sus decisiones contra este radar.

**Total de anti-patrones: 60**
- 🔴 CRÍTICOS (bloquean el merge/deploy): **14**
- 🟠 ALTOS (requieren revisión antes de merge): **28**
- 🟡 MEDIOS (reducen calidad pero no bloquean): **18**

---

## 🔴 ANTI-PATRONES CRÍTICOS — Bloquean el merge/deploy

### SEGURIDAD (de FUENTE-409)

**SC-01 — Auth token en localStorage**
Cualquier XSS puede robar el token y usarlo para hacerse pasar por el usuario.
*Corrección: Access token en memoria (Zustand sin persist). Refresh token en cookie HttpOnly.*

**SC-02 — `innerHTML` con datos no sanitizados**
Ejecuta HTML/JavaScript del atacante en el browser del usuario.
*Corrección: `textContent` para texto. `DOMPurify.sanitize()` antes de `dangerouslySetInnerHTML`.*

**SC-03 — Sin CSP Headers configurados**
Sin CSP, cualquier script inyectado se ejecuta. El primer vector de XSS que pase tiene impacto total.
*Corrección: CSP configurado en next.config.js con `default-src 'self'` como mínimo.*

**SC-04 — `eval()` con cualquier dato externo**
Ejecuta código arbitrario. El vector de ataque más directo posible.
*Corrección: No usar `eval()`. Refactorizar la lógica que lo requiere.*

### JAVASCRIPT CORE (de FUENTE-401, 407)

**JS-01 — Race condition en useEffect con fetch**
Dos requests concurrentes pueden resolverse en orden incorrecto → UI muestra datos del request anterior.
*Corrección: AbortController en el cleanup del useEffect o usar TanStack Query.*

**JS-02 — Memory leak por event listeners no limpiados**
El componente se desmonta pero el listener sigue activo, reteniendo la referencia al componente en memoria.
*Corrección: Cleanup en useEffect: `return () => window.removeEventListener(...)` o AbortController signal.*

**JS-03 — `any` en TypeScript sin justificación**
Pierde la protección de tipos. Los errores de tipo se detectan en runtime en lugar de compile time.
*Corrección: Usar `unknown` + type guards. Si no hay opción, comentario que justifique el `any`.*

### REACT/NEXT.JS (de FUENTE-403, 405)

**RX-01 — Estado del servidor duplicado en useState**
Los datos del servidor se guardan en React state además de la caché de TanStack Query → dos fuentes de verdad, inconsistencias.
*Corrección: Los datos del servidor solo viven en TanStack Query. useState solo para UI state.*

**RX-02 — Re-renders infinitos por dependencias de useEffect incorrectas**
`useEffect` con objeto o función como dep en el array → nuevo objeto en cada render → loop infinito.
*Corrección: Usar `useMemo`/`useCallback` para estabilizar dependencias. ESLint exhaustive-deps como linter.*

**RX-03 — Client Component innecesario en Next.js App Router**
`"use client"` en componentes que no usan hooks ni eventos → aumenta bundle innecesariamente.
*Corrección: Los componentes son Server Components por default. Solo añadir `"use client"` cuando se usen hooks.*

### PERFORMANCE (de FUENTE-406)

**PF-01 — Bundle sin code splitting (todo en un chunk)**
El usuario descarga todo el JavaScript aunque solo use el 20% de la app.
*Corrección: Dynamic imports, `React.lazy()`, manualChunks en Vite.*

**PF-02 — Imágenes sin optimizar (sin formato WebP, sin dimensiones)**
Las imágenes no optimizadas son la causa #1 de LCP alto.
*Corrección: Next.js `<Image>` component o `<img loading="lazy" width height>` con WebP.*

### ACCESIBILIDAD (de FUENTE-410)

**A11-01 — `<div>` clickeable sin semántica de botón**
No tiene focus, no se activa con Enter/Space, no anuncia su función al screen reader.
*Corrección: `<button type="button">` para acciones. `<a href>` para navegación.*

**A11-02 — `outline: none` sin estado de foco visual alternativo**
El usuario de teclado no sabe dónde está el foco. Viola WCAG 2.1 AA.
*Corrección: Diseñar `:focus-visible` con contraste mínimo 3:1 contra el fondo.*

---

## 🟠 ANTI-PATRONES ALTOS — Requieren revisión antes del merge

### JAVASCRIPT Y TYPESCRIPT

**JS-04 — Closures con variables mutables que no se capturan correctamente**
El valor de la variable al momento de ejecutar el callback no es el esperado.
*(Ver FUENTE-401 — Scope & Closures)*

**JS-05 — `async forEach` que no espera las promesas**
`array.forEach(async fn)` ejecuta todas las promesas en paralelo sin control, sin esperar a que terminen.
*Corrección: `for...of` con `await`, o `Promise.all(array.map(async fn))`.*

**JS-06 — No tipificar las respuestas de API**
El tipo `any` implícito de un `fetch()` sin tipificar elimina la protección en todo el downstream.
*Corrección: Tipificar la respuesta con un type/interface + validación en runtime (zod).*

**JS-07 — Error handling con solo `console.log` en producción**
Los errores en producción son invisibles para el equipo.
*Corrección: Sentry (FUENTE-413) + Error Boundaries (FUENTE-413) en producción.*

### CSS Y LAYOUT

**CSS-01 — Animar `width`, `height`, `top`, `left` con CSS**
Causa reflows del layout. Imposible mantener 60fps.
*Corrección: Solo animar `opacity` y `transform` (FUENTE-414).*

**CSS-02 — Specificity wars (`!important` para todo)**
El CSS se vuelve imposible de mantener. Cada nuevo estilo necesita más `!important`.
*Corrección: Arquitectura CSS con scope (CSS Modules, Tailwind) que evita conflictos.*

**CSS-03 — Valores hardcodeados en CSS (colores hex, px de espaciado)**
Cuando el design token cambia, hay que encontrar y cambiar cada instancia.
*Corrección: CSS custom properties que mapean los tokens del Cerebro #3.*

**CSS-04 — Sin `prefers-reduced-motion` en animaciones de movimiento**
Puede causar malestar físico a usuarios con vestibular disorders.
*Corrección: `@media (prefers-reduced-motion: reduce)` o `useReducedMotion()` de Framer Motion.*

### REACT / NEXT.JS

**RX-04 — Props drilling más de 2 niveles**
El componente intermedio recibe props que no usa, solo para pasarlas hacia abajo.
*Corrección: Context API para estado de UI, TanStack Query para datos del servidor.*

**RX-05 — `useEffect` para derivar estado de estado**
Si el nuevo estado puede calcularse a partir del estado existente, es estado derivado → no `useEffect`.
*Corrección: Calcular el valor derivado durante el render o con `useMemo`.*

**RX-06 — Mutación directa del estado**
`state.push(item)` en lugar de `setState([...state, item])` → React no detecta el cambio.
*Corrección: Siempre crear un nuevo objeto/array: `setState(prev => [...prev, item])`.*

**RX-07 — Key prop con index del array en listas con reordenamiento**
`key={index}` hace que React no pueda rastrear qué elemento es cuál al reordenar → re-renders incorrectos.
*Corrección: `key={item.id}` con un ID estable y único.*

**RX-08 — Server Action sin validación de input en el servidor**
El cliente puede enviar cualquier dato a una Server Action. La validación solo en el cliente es inútil.
*Corrección: Validar con zod en el servidor, independientemente de la validación del cliente.*

### TESTING

**TST-01 — Tests que prueban implementación, no comportamiento**
Tests frágiles que fallan con cualquier refactor aunque el comportamiento sea correcto.
*Corrección: Testing Library — `getByRole`, `getByText`, no `getByTestId` o acceso a state interno.*

**TST-02 — Sin tests de casos de error**
Solo se testea el "happy path". Los errores de API, estados vacíos, y validaciones quedan sin cobertura.
*Corrección: Por cada feature, escribir al menos 1 test de caso de error y 1 de estado vacío.*

**TST-03 — Tests con `waitFor` sin timeout adecuado**
Los tests flaky que a veces pasan y a veces fallan usualmente tienen race conditions en los `waitFor`.
*Corrección: Usar `findBy*` (que incluye `waitFor`) con queries apropiados.*

### PERFORMANCE

**PF-03 — Fetch de datos en useEffect (en lugar de TanStack Query)**
El patrón `useState + useEffect + fetch` no tiene: caché, deduplication, retry, ni loading states.
*Corrección: TanStack Query para todos los datos del servidor (FUENTE-408).*

**PF-04 — LCP > 2.5s por imagen above-the-fold no priorizada**
La imagen más grande visible al cargar no está siendo priorizada por el browser.
*Corrección: `<Image priority>` en Next.js o `<img fetchpriority="high">` para la imagen hero.*

**PF-05 — Terceras partes (analytics, chat) bloqueando el main thread**
Scripts de terceros se cargan síncronamente y bloquean el parse de HTML.
*Corrección: `<script async>` o `<script defer>` para todos los scripts de terceros.*

### TOOLING Y CI

**TL-01 — Sin `npm ci` en CI (usar `npm install`)**
`npm install` puede actualizar versiones dentro del rango semver → builds no reproducibles.
*Corrección: `npm ci` en todo pipeline de CI.*

**TL-02 — Sin verificación de tipos en CI**
Los errores de TypeScript no se detectan si solo corre ESLint y tests.
*Corrección: `tsc --noEmit` como paso separado en el pipeline de CI.*

**TL-03 — Variables de entorno hardcodeadas en el código**
API keys, URLs de entorno, y secrets en el código → se commitean al repo.
*Corrección: `.env.local` (gitignored) + validación con zod al iniciar la app.*

**TL-04 — Sin Dependabot o equivalente**
Las dependencias con vulnerabilidades conocidas no se actualizan automáticamente.
*Corrección: GitHub Dependabot o Renovate para PRs automáticos de actualización.*

### SEGURIDAD

**SC-05 — Stack traces y errores técnicos mostrados al usuario**
Expone rutas del servidor, IDs internos, y arquitectura al atacante.
*Corrección: Mapear errores técnicos a mensajes de usuario genéricos.*

**SC-06 — Dependencias sin `npm audit` en CI**
Vulnerabilidades conocidas en dependencias pasan desapercibidas.
*Corrección: `npm audit --audit-level=high` como paso en CI.*

---

## 🟡 ANTI-PATRONES MEDIOS — Reducen calidad pero no bloquean

### CÓDIGO Y ARQUITECTURA

**CM-01 — Componentes de más de 300 líneas**
Componentes grandes son difíciles de testear, mantener, y de entender. Señal de que hace demasiado.
*Corrección: Extraer subcomponentes y hooks custom.*

**CM-02 — Lógica de negocio en componentes de UI**
El componente de UI decide si el usuario puede ver algo vs el hook que valida permisos.
*Corrección: Lógica en custom hooks; componentes solo renderizan.*

**CM-03 — Imports sin path aliases (`../../../components`)**
Imports relativos profundos son frágiles al mover archivos.
*Corrección: `@/components/...` alias configurado en Vite + tsconfig.*

**CM-04 — Magic numbers sin constante nombrada**
`if (score > 7)` — ¿qué es 7? ¿De dónde viene? ¿Puede cambiar?
*Corrección: `const PREMIUM_SCORE_THRESHOLD = 7` con nombre descriptivo.*

### ACCESIBILIDAD

**A11-03 — Imágenes informativas sin `alt` descriptivo**
El screen reader anuncia "imagen" sin descripción de la información que transmite.
*Corrección: `alt` que describe la información, no la apariencia.*

**A11-04 — Formulario sin mensajes de error asociados via aria**
El screen reader anuncia el error pero el usuario no sabe a qué campo corresponde.
*Corrección: `aria-describedby="error-id"` en el input, `id="error-id"` en el mensaje de error.*

**A11-05 — Modal sin trampa de foco**
El tab sale del modal hacia contenido invisible del fondo.
*Corrección: Focus trap — el tab cicla solo dentro del modal mientras está abierto.*

### WEB APIS Y PERFORMANCE

**WA-01 — `window.onscroll` para detectar elementos en viewport**
Se dispara cientos de veces por segundo aunque no haya cambio relevante.
*Corrección: `IntersectionObserver` — solo se llama cuando el elemento cruza el threshold.*

**WA-02 — `window.resize` para detectar cambio de un elemento específico**
`window.resize` no detecta cambios de tamaño de un elemento por flexbox/grid.
*Corrección: `ResizeObserver` en el elemento específico.*

**WA-03 — Procesamiento de datos pesados en el main thread**
Parsear un CSV grande, hacer cálculos complejos, o procesar imágenes congela la UI.
*Corrección: Web Worker para cualquier operación > 50ms en el main thread.*

### MONITORING Y DEBUGGING

**MN-01 — Sentry sin contexto de usuario**
Los errores de producción no tienen el userId asociado — imposible reproducir el bug para ese usuario.
*Corrección: `Sentry.setUser({ id: user.id })` al autenticarse.*

**MN-02 — Sin alertas configuradas en Sentry**
Sentry captura errores pero nadie los ve hasta que un usuario reporta.
*Corrección: Alertas en Slack para error rate > 1% en 15 minutos.*

**MN-03 — Error Boundary demasiado granular (uno por componente)**
Overhead innecesario de re-renders; además oscurece qué features son independientes.
*Corrección: Un Error Boundary por feature independiente, no por componente.*

### ANIMACIONES

**AN-01 — `will-change: transform` en todos los elementos**
Cada elemento promovido consume memoria GPU → puede empeorar el performance en dispositivos con poca RAM.
*Corrección: Solo en elementos que se animan frecuentemente. Remover después de la animación.*

**AN-02 — Animaciones sin especificación de duración y easing**
El developer inventa los valores → inconsistencia con el sistema de diseño del Cerebro #3.
*Corrección: Usar exactamente los valores de la especificación de FUENTE-310.*

**AN-03 — Animaciones de `exit` sin `AnimatePresence`**
Framer Motion no puede animar un componente que ya fue removido del DOM.
*Corrección: Envolver con `<AnimatePresence>` el padre del componente con prop `exit`.*

---

## Checklist de Calidad — Pre-Merge (Code Review)

```
SEGURIDAD
☐ ¿Ningún auth token en localStorage o sessionStorage?
☐ ¿No se usa innerHTML con datos del usuario sin DOMPurify?
☐ ¿No se usa eval() con datos externos?
☐ ¿Los errores técnicos no se exponen al usuario?
☐ ¿Las dependencias pasan npm audit?

JAVASCRIPT / TYPESCRIPT
☐ ¿No hay any implícito (respuestas de fetch sin tipificar)?
☐ ¿Los useEffect tienen cleanup (removeEventListener, abort)?
☐ ¿No hay async forEach (usar for...of o Promise.all(map))?
☐ ¿Las respuestas de API están validadas con zod o similar?

REACT / NEXT.JS
☐ ¿Los datos del servidor solo viven en TanStack Query (no duplicados en useState)?
☐ ¿Los componentes de Next.js son Server Components por default (no "use client" innecesario)?
☐ ¿Las keys de listas son IDs estables, no índices del array?
☐ ¿No hay props drilling más de 2 niveles sin justificación?

CSS / ANIMACIONES
☐ ¿Las animaciones solo usan opacity y transform?
☐ ¿Hay media query de prefers-reduced-motion para animaciones de movimiento?
☐ ¿No hay !important innecesario?
☐ ¿Los valores de CSS referencian tokens/variables, no valores hardcodeados?

ACCESIBILIDAD
☐ ¿Todos los elementos interactivos son semánticamente correctos (button, a, input)?
☐ ¿El estado de foco es visible (no outline: none sin alternativa)?
☐ ¿Las imágenes informativas tienen alt text descriptivo?
☐ ¿Los formularios tienen labels asociados?
☐ ¿Se corre jest-axe en los tests de los componentes nuevos?

PERFORMANCE
☐ ¿Las imágenes above-the-fold tienen priority?
☐ ¿Los chunks grandes tienen code splitting?
☐ ¿Los scripts de terceros tienen async o defer?

TESTING
☐ ¿Los tests verifican comportamiento (getByRole) y no implementación?
☐ ¿Hay al menos 1 test de caso de error y 1 de estado vacío por feature?
☐ ¿Los tests pasan en CI (no solo localmente)?

TOOLING / CI
☐ ¿El pipeline de CI incluye: tsc, lint, test, y build?
☐ ¿No hay variables de entorno hardcodeadas?
☐ ¿El lockfile está commitado y se usa npm ci en CI?
```

---

## Checklist de Calidad — Pre-Deploy

```
☐ Lighthouse Accessibility Score ≥ 90
☐ Lighthouse Performance Score ≥ 80
☐ Core Web Vitals en "Good" en Staging (LCP < 2.5s, INP < 200ms, CLS < 0.1)
☐ npm audit --audit-level=high pasa sin vulnerabilidades
☐ Sentry configurado y capturando errores en staging
☐ Error Boundaries en todas las features principales
☐ CSP Headers configurados y verificados
☐ Comportamiento offline verificado (si la app es PWA)
```

---

## Score de Evaluación del Output del Cerebro #4

| Categoría | Peso | Criterio de Aprobación |
|-----------|------|------------------------|
| Seguridad (0 críticos) | 25% | Sin SC-01 al SC-04 en el código |
| TypeScript correcto (sin any injustificado) | 15% | `tsc --noEmit` pasa sin errores |
| Tests pasan con cobertura ≥ 80% | 15% | CI verde en testing |
| Accesibilidad (axe sin violaciones críticas) | 15% | jest-axe pasa, `outline: none` sin alternativa ausente |
| Performance (Core Web Vitals en Good) | 15% | Lighthouse ≥ 80 en staging |
| Código limpio (sin anti-patrones medios > 3) | 10% | Code review sin más de 3 medios sin resolver |
| Animaciones con spec del Cerebro #3 | 5% | Valores de duration/easing de la spec |

**APROBACIÓN:**
- Score > 85%: **APPROVE** — Listo para deploy
- Score 70-85%: **CONDITIONAL** — Deploy con notas de follow-up documentadas
- Score < 70%: **REJECT** — Requiere revisión antes del deploy

---

## Preguntas de Auto-Evaluación del Cerebro #4

1. ¿Un atacante con XSS puede robar las credenciales de sesión del usuario?
2. ¿Si TypeScript está en modo strict y se hace `tsc`, pasa sin errores?
3. ¿Qué pasa si el servidor devuelve un error 500 en el checkout? ¿La app sigue funcionando?
4. ¿Un usuario de teclado puede completar el flujo principal sin mouse?
5. ¿El Lighthouse de staging está en verde para los Core Web Vitals?
6. ¿Si el usuario vuelve a esta pantalla 100 veces, hay memory leaks?
7. ¿El equipo se va a enterar si hay un error en producción antes que el primer ticket de soporte?
8. ¿Este código está listo para que un developer nuevo lo entienda en 10 minutos?

---

## Conexión con otros Cerebros

| Cerebro | Relación con el Output del #4 |
|---------|-------------------------------|
| Cerebro #3 (UI Design) | INPUT: especificación de componentes, tokens, animaciones. El #4 implementa exactamente eso. |
| Cerebro #5 (Backend API) | CONTRATO: tipos de los endpoints, validación de inputs, autenticación. El #4 y el #5 deben compartir los schemas de API. |
| Cerebro #7 (Growth & Data) | EVALUADOR: Core Web Vitals, conversion rates, error rates. Si algo bajo el #4 afecta métricas, el #7 retroalimenta al #4. |

---

## Registro de Precedentes del Cerebro #4

*(Se actualiza con cada decisión arquitectural relevante)*

```yaml
precedents: []
# Formato:
# - id: "PREC-4XX"
#   date: "YYYY-MM-DD"
#   decision: "descripción de la decisión tomada"
#   context: "por qué se tomó esta decisión"
#   applies_to: ["feature o componente"]
#   supersedes: "PREC-4YY"  # si reemplaza a una decisión anterior
```
