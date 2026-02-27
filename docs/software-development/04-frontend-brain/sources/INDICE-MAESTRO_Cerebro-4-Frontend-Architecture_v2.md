---
source_id: "INDICE-MAESTRO-04"
brain: "brain-software-04-frontend-architecture"
niche: "software-development"
title: "Índice Maestro — Cerebro #4 Frontend Architecture"
author: "MasterMind Framework"
expert_id: "EXP-INDICE-04"
type: "guide"
language: "es"
year: 2026
isbn: "N/A"
url: "N/A"
skills_covered: ["H1", "H2", "H3", "H4", "H5", "H6", "H7"]
distillation_date: "2026-02-26"
distillation_quality: "complete"
loaded_in_notebook: false
version: "2.0.0"
last_updated: "2026-02-26"
changelog:
  - version: "2.0.0"
    date: "2026-02-26"
    changes:
      - "Agrega FUENTE-409 al 415 (Seguridad, Accesibilidad, Tooling, Web APIs, Error Handling, Animaciones, Radar)"
      - "Todos los gaps de la versión 1.0 cubiertos"
      - "0 gaps identificados en v2.0"
  - version: "1.0.0"
    date: "2026-02-26"
    changes:
      - "Fuentes FUENTE-401 al 408 iniciales"
status: "active"
---

# ÍNDICE MAESTRO v2.0 — Cerebro #4 Frontend Architecture
## MasterMind Framework | Software Development

---

## Rol del Cerebro #4

**Pregunta Central:** ¿Cómo se construye la interfaz correctamente en código?

**Función:** Transforma las especificaciones del Cerebro #3 (UI Design) en código React/TypeScript robusto, performante, accesible, seguro, y testeable que el Cerebro #5 (Backend API) puede integrar limpiamente.

**Si el Cerebro #4 falla:** El código es inconsistente, tiene bugs difíciles de rastrear, es lento en producción, es inaccesible, o tiene vulnerabilidades de seguridad.

---

## Fuentes Maestras — Versión Completa v2.0

### Capa 1 — Base Conceptual

| ID | Fuente | Autor | Habilidad Principal | Estado |
|----|--------|-------|---------------------|--------|
| FUENTE-401 | You Don't Know JS | Kyle Simpson | JavaScript Profundo — Scope, Closures, Async | ✅ |
| FUENTE-402 | CSS for JavaScript Developers | Josh Comeau | CSS Avanzado — Layouts, Cascade, Stacking Contexts | ✅ |
| FUENTE-405 | React Docs + Next.js Docs | Meta + Vercel | React 18 Hooks, Server Components, App Router | ✅ |
| FUENTE-407 | Effective TypeScript | Dan Vanderkam | TypeScript — Tipado estático efectivo, Generics | ✅ |

### Capa 2 — Frameworks Operativos

| ID | Fuente | Autor | Habilidad Principal | Estado |
|----|--------|-------|---------------------|--------|
| FUENTE-403 | Learning Patterns | Addy Osmani & Lydia Hallie | Design Patterns JS/React, Rendering Patterns | ✅ |
| FUENTE-404 | Testing JavaScript | Kent C. Dodds | Testing Unit/Integration/E2E, Testing Library | ✅ |
| FUENTE-406 | Web Performance & Core Web Vitals | Google web.dev | LCP, INP, CLS — Optimización de performance | ✅ |
| FUENTE-408 | State Management: TanStack + Zustand | Tanner Linsley + pmndrs | Server State vs Client State, Caching | ✅ |
| **FUENTE-409** | **Frontend Security** | **OWASP + MDN** | **XSS, CSRF, CSP, Auth segura** | ✅ NEW |
| **FUENTE-410** | **Accessibility in Practice** | **W3C WAI + Deque** | **ARIA, Focus Management, jest-axe** | ✅ NEW |
| **FUENTE-411** | **Modern Frontend Tooling** | **Evan You + ESLint + Prettier** | **Vite, ESLint, CI/CD, DX** | ✅ NEW |
| **FUENTE-412** | **Modern Web APIs** | **MDN + Google** | **IntersectionObserver, Service Workers, PWA** | ✅ NEW |
| **FUENTE-413** | **Error Handling & Monitoring** | **Sentry + Chrome DevTools** | **Error Boundaries, Sentry, Debugging** | ✅ NEW |
| **FUENTE-414** | **Animation in Code** | **Matt Perry (Framer Motion)** | **CSS Transitions, Framer Motion, GPU perf** | ✅ NEW |

### Capa 3 — Radar Auto-generado

| ID | Fuente | Tipo | Contenido | Estado |
|----|--------|------|-----------|--------|
| **FUENTE-415** | **Anti-Patrones y Radar de Calidad** | **Radar interno** | **60 anti-patrones + Checklist + Score** | ✅ NEW |

---

## Mapa de Habilidades Cubiertas (v2.0)

| Habilidad | Fuentes | Cobertura |
|-----------|---------|-----------|
| JavaScript Profundo (Scope, Closures, Async, Event Loop) | FUENTE-401 | ✅ Alta |
| CSS Avanzado (Cascade, Flexbox, Grid, Stacking Contexts) | FUENTE-402 | ✅ Alta |
| React Patterns y Arquitectura de Componentes | FUENTE-403, 405 | ✅ Alta |
| TypeScript Efectivo (Generics, Utility Types, Narrowing) | FUENTE-407 | ✅ Alta |
| State Management (TanStack Query + Zustand) | FUENTE-408 | ✅ Alta |
| Testing (Unit, Integration, E2E, Testing Library) | FUENTE-404 | ✅ Alta |
| Web Performance y Core Web Vitals | FUENTE-406 | ✅ Alta |
| Rendering Patterns (SSR, SSG, ISR, Streaming) | FUENTE-403, 405 | ✅ Alta |
| **Seguridad Frontend (XSS, CSRF, CSP, Auth)** | **FUENTE-409** | ✅ Alta — NEW |
| **Accesibilidad en Código (ARIA, Focus, jest-axe)** | **FUENTE-410** | ✅ Alta — NEW |
| **Tooling Moderno (Vite, ESLint, CI/CD)** | **FUENTE-411** | ✅ Alta — NEW |
| **Web APIs Modernas (IntersectionObserver, SW, PWA)** | **FUENTE-412** | ✅ Alta — NEW |
| **Error Handling y Monitoring (Error Boundaries, Sentry)** | **FUENTE-413** | ✅ Alta — NEW |
| **Implementación de Animaciones (CSS, Framer Motion)** | **FUENTE-414** | ✅ Media-Alta — NEW |

**Gaps en v1.0: 6 (Seguridad, Accesibilidad, Tooling, Web APIs, Error Handling, Animaciones)**
**Gaps en v2.0: 0 ✅**

---

## Gaps Residuales (Fase 3 — Bajo Impacto)

| Gap | Fuente Sugerida | Prioridad | Justificación |
|-----|----------------|-----------|---------------|
| Internacionalización (i18n) | next-intl, react-i18next | Baja | Relevante solo para productos multi-idioma |
| React Native / Mobile | React Native docs | Muy Baja | Out of scope — el #4 es web frontend |
| Web Components (Custom Elements) | MDN Web Components | Muy Baja | Solo si el stack no es React |
| Micro-frontends | Module Federation (Webpack/Vite) | Baja | Solo para arquitecturas enterprise muy grandes |

---

## Árbol de Decisión del Cerebro #4

```
INPUT DEL CEREBRO #3 (componentes, tokens, animaciones, especificación)
│
├── ¿Es un componente nuevo?
│   ├── ¿Existe un elemento HTML semántico nativo? → Usarlo (FUENTE-410)
│   ├── ¿Tiene estados interactivos? → Diseñar estados: hover, focus, active, disabled, error (FUENTE-410)
│   └── ¿Tiene animaciones especificadas? → Implementar con CSS/Framer Motion (FUENTE-414)
│
├── ¿Hay datos del servidor involucrados?
│   └── → Usar TanStack Query (FUENTE-408) — nunca useState + useEffect + fetch
│
├── ¿Hay estado de UI compartido entre componentes?
│   └── → Zustand para UI state global; Context para UI state local de feature
│
├── ¿Es una feature que puede fallar?
│   └── → Error Boundary alrededor (FUENTE-413)
│
├── ¿La feature maneja datos del usuario o autenticación?
│   └── → Aplicar FUENTE-409: verificar auth storage, CSP, sanitización
│
├── ¿Hay imágenes, listas largas, o contenido heavy?
│   └── → IntersectionObserver / loading="lazy" (FUENTE-412) + Image optimization (FUENTE-406)
│
├── ¿Es un feature Next.js?
│   ├── → ¿Necesita hooks o eventos? → "use client" + Client Component
│   └── → ¿Solo datos y UI estática? → Server Component (default)
│
└── ANTES DE MERGE → Ejecutar Checklist FUENTE-415
                    → Score mínimo 85% para APPROVE
                    → CI verde (tsc + lint + test + build)
```

---

## Instrucciones de Carga en NotebookLM

**Nombre del cuaderno:** `[CEREBRO] Frontend Architecture — Software Development`

**Orden de carga recomendado:**

*Capa 1 — Base conceptual:*
1. FUENTE-401 — You Don't Know JS (base de JS)
2. FUENTE-407 — Effective TypeScript (tipado)
3. FUENTE-402 — CSS for JS Developers (CSS)
4. FUENTE-405 — React + Next.js Docs (framework)

*Capa 2 — Frameworks operativos:*
5. FUENTE-403 — Learning Patterns (arquitectura)
6. FUENTE-408 — State Management (datos)
7. FUENTE-404 — Testing JavaScript (calidad)
8. FUENTE-406 — Web Performance (velocidad)
9. FUENTE-409 — Frontend Security (seguridad)
10. FUENTE-410 — Accessibility in Practice (accesibilidad)
11. FUENTE-411 — Frontend Tooling (setup)
12. FUENTE-412 — Modern Web APIs (browser APIs)
13. FUENTE-413 — Error Handling & Monitoring (producción)
14. FUENTE-414 — Animation in Code (motion)

*Capa 3 — Radar:*
15. FUENTE-415 — Anti-Patrones y Radar (cargar al final)

**Consultas de prueba post-carga:**
1. "¿Este componente debe ser Server Component o Client Component y por qué?"
2. "¿Es seguro guardar el JWT en localStorage?"
3. "¿Por qué este useEffect tiene una race condition y cómo la corrijo?"
4. "¿Cómo implemento la trampa de foco de este modal?"
5. "¿Qué estrategia de caché de Service Worker es correcta para esta API?"
6. "¿Cuáles son los anti-patrones críticos que bloquean el deploy?"
7. "¿Cómo implemento esta animación de entrada especificada en 300ms ease-out?"

---

## Estadísticas del Cerebro #4 — v2.0

| Métrica | v1.0 | v2.0 |
|---------|------|------|
| Fuentes maestras totales | 8 | **15** |
| Fuentes Capa 1 (Base) | 4 | **4** |
| Fuentes Capa 2 (Frameworks) | 4 | **10** |
| Fuentes Capa 3 (Radar) | 0 | **1** |
| Anti-patrones catalogados | 0 | **60** |
| Anti-patrones críticos | — | **14** |
| Anti-patrones altos | — | **28** |
| Anti-patrones medios | — | **18** |
| Habilidades con cobertura alta | 8/14 | **14/14** |
| Gaps identificados | 6 | **0** |
