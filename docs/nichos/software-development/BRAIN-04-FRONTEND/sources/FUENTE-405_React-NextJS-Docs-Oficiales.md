---
source_id: "FUENTE-405"
brain: "brain-software-04-frontend-architecture"
niche: "software-development"
title: "React Docs (react.dev) + Next.js Docs (nextjs.org/docs) — Documentación Oficial Destilada"
author: "React Team (Meta) + Next.js Team (Vercel)"
expert_id: "EXP-405"
type: "documentation"
language: "en"
year: 2023
isbn: "N/A"
url: "https://react.dev + https://nextjs.org/docs"
skills_covered: ["H3", "H4", "H6"]
distillation_date: "2026-02-26"
distillation_quality: "complete"
loaded_in_notebook: true
version: "1.0.0"
last_updated: "2026-02-26"
changelog:
  - version: "1.0.0"
    date: "2026-02-26"
    changes:
      - "Ficha creada con destilación completa"
      - "Cubre React 18+ (Concurrent features, Suspense) y Next.js 14+ (App Router, Server Components)"
      - "Formato estándar del MasterMind Framework v2"
status: "active"

habilidad_primaria: "React 18 Hooks, Server Components, Concurrent Features"
habilidad_secundaria: "Next.js App Router, Server Actions, Caching y Routing avanzado"
capa: 1
capa_nombre: "Base Conceptual"
relevancia: "CRÍTICA — Es la fuente primaria del stack. React y Next.js son el stack de referencia del Cerebro #4. La documentación oficial (react.dev) fue completamente reescrita en 2023 con los patrones correctos."
---

# FUENTE-405: React Docs + Next.js Docs
## Documentación Oficial | React 18 + Next.js 14+ App Router

---

## Tesis Central

> React 18 y el Next.js App Router representan un cambio de paradigma: el rendering ya no es exclusivamente del cliente. Los React Server Components permiten que parte del árbol se renderice en el servidor sin enviar JS al cliente, reduciendo el bundle y mejorando el LCP. Entender la nueva arquitectura servidor/cliente es la competencia central del frontend moderno.

La pregunta que cambia todo: "¿Este componente NECESITA ser un Client Component, o puede ser Server Component?" La respuesta determina el tamaño del bundle, el tiempo de carga, y la complejidad del estado.

---

## 1. Principios Fundamentales

> **P1: Componentes son funciones que reciben props y devuelven UI**
> La nueva documentación de React refuerza el modelo mental: un componente es una función pura. Dado el mismo estado y props, devuelve el mismo JSX. Los side effects (fetch, suscripciones, DOM mutations) van en `useEffect` o en Server Components.
> *Aplicación: si un componente produce output diferente sin que sus props o estado cambien, hay un side effect no controlado.*

> **P2: React Server Components (RSC) — Servidor por defecto en Next.js App Router**
> En el App Router, todos los componentes son Server Components por defecto. Solo se convierten en Client Components con la directiva `'use client'`. Los Server Components pueden hacer async/await directamente, acceden a la base de datos, y no envían JS al cliente.
> *Aplicación: antes de añadir `'use client'`, pregunta: "¿Este componente necesita interactividad o estado? Si no, dejarlo como Server Component."*

> **P3: El Hook `useState` es la unidad atómica de estado reactivo**
> `useState` crea un par [valor, setter]. Cuando el setter se llama, React re-renderiza el componente y todos sus hijos. El estado es local al componente — no se comparte automáticamente con otros.
> *Aplicación: si dos componentes necesitan el mismo estado, ubicarlo en su ancestro común más cercano (state lifting).*

> **P4: `useEffect` es para sincronizar con sistemas externos**
> `useEffect` conecta un componente a sistemas fuera de React: el DOM, APIs del browser, redes, subscripciones. No es para lógica de rendering ni para transformar datos (eso va en el body del componente).
> *Aplicación: si un `useEffect` solo calcula valores derivados del estado/props, moverlo fuera del effect — solo necesita código en el body del componente.*

> **P5: Las Reglas de Hooks no son opcionales**
> Hooks deben llamarse en el nivel superior del componente (no dentro de condicionales, loops, o funciones anidadas) y solo desde componentes o hooks personalizados. El orden de llamada de hooks debe ser siempre el mismo entre renders.
> *Aplicación: el linter de React (`eslint-plugin-react-hooks`) detecta violaciones automáticamente — no desactivarlo.*

---

## 2. Frameworks y Metodologías

### Framework 1: Hooks de React — Mapa de Uso Correcto

**Propósito:** Elegir el hook correcto para cada necesidad.

```javascript
// ESTADO LOCAL
useState      → Estado simple que un componente necesita
useReducer    → Estado complejo con múltiples sub-values o lógica de actualización compleja

// EFECTOS Y SINCRONIZACIÓN
useEffect     → Sincronizar con sistemas externos (fetch, subscriptions, DOM mutations)
useLayoutEffect → Como useEffect pero sincrónico ANTES del paint (para leer el DOM)

// PERFORMANCE
useMemo       → Memoizar valores calculados caros (solo con medición que lo justifique)
useCallback   → Memoizar funciones (solo si se pasan como props a hijos memoizados)
useTransition → Marcar updates como "no urgentes" para que el UI no se congele
useDeferredValue → Diferir actualización de un valor durante renders concurrentes

// REFERENCIAS
useRef        → Referencia mutable que NO causa re-render al cambiar
               → Acceder a elementos del DOM directamente
               → Guardar valores entre renders sin causar re-render

// CONTEXTO
useContext    → Leer un valor del Context Provider más cercano en el árbol

// ID Y ACCESIBILIDAD
useId         → Generar IDs únicos y estables para accesibilidad (for/id de inputs)

// CUSTOM HOOKS
useFetch      → Tu lógica de fetch encapsulada y reutilizable
useLocalStorage → Persistencia en localStorage con estado reactivo
```

---

### Framework 2: Next.js App Router — Arquitectura de Carpetas

**Propósito:** Estructurar un proyecto Next.js App Router correctamente.

```
app/
├── layout.tsx          → Root layout (HTML, body, providers globales)
├── page.tsx            → Home page (/)
├── loading.tsx         → Loading UI para Suspense automático
├── error.tsx           → Error UI (Error Boundary automático)
├── not-found.tsx       → 404 page
│
├── (auth)/             → Route group (no afecta la URL)
│   ├── login/
│   │   └── page.tsx   → /login
│   └── register/
│       └── page.tsx   → /register
│
├── dashboard/
│   ├── layout.tsx      → Layout específico del dashboard (sidebar, nav)
│   ├── page.tsx        → /dashboard
│   └── [userId]/
│       └── page.tsx   → /dashboard/123 (dynamic route)
│
└── api/
    └── webhooks/
        └── route.ts   → API route (/api/webhooks)
```

**Convenciones clave de archivos especiales:**
```
page.tsx      → La UI de la ruta (solo este archivo hace la ruta pública)
layout.tsx    → UI que envuelve páginas (no re-monta entre navegaciones)
loading.tsx   → Skeleton/spinner automático con Suspense
error.tsx     → Error boundary automático (debe ser Client Component)
not-found.tsx → UI del 404 para esta ruta
route.ts      → API endpoint (GET, POST, PUT, DELETE exports)
```

---

### Framework 3: Server vs Client Components — Árbol de Decisión

**Propósito:** Decidir si un componente debe ser Server o Client.

```
¿El componente necesita alguno de estos?
  ├── useState / useReducer       → Client Component ('use client')
  ├── useEffect                   → Client Component ('use client')
  ├── onClick / onChange / eventos → Client Component ('use client')
  ├── Browser APIs (window, localStorage) → Client Component ('use client')
  └── Hooks de terceros (no RSC-compatible) → Client Component ('use client')

¿El componente hace alguno de esto?
  ├── Fetch de datos async directamente → Server Component (por defecto)
  ├── Acceder a DB, filesystem, variables de entorno → Server Component
  ├── Importar módulos pesados que no deben ir al cliente → Server Component
  └── No tiene interactividad → Server Component (por defecto, no hacer nada)

PATRÓN RECOMENDADO — "Push Client Components Down":
  ├── Page (Server) → fetch datos, pasa props
  │   └── Layout (Server) → estructura
  │       ├── StaticContent (Server) → renders sin JS
  │       └── InteractiveWidget (Client) → solo la parte interactiva
```

---

## 3. Modelos Mentales

| Modelo | Descripción | Aplicación Práctica |
|--------|-------------|---------------------|
| **Componente como Snapshot en el Tiempo** | Cada render es una foto del estado en ese momento. React compara snapshots para saber qué cambió | Si el estado parece "stale" en un event handler, es porque captura el snapshot del render donde fue creado (closure) |
| **El Árbol de Renders** | React mantiene un árbol virtual (Virtual DOM). Solo las diferencias entre renders se aplican al DOM real | Los re-renders no son necesariamente costosos si el Virtual DOM diff es pequeño |
| **Lifting State Up** | Si dos componentes hermanos necesitan el mismo dato, moverlo al ancestro común más cercano | El "ancestro más cercano" minimiza los re-renders por el cambio |
| **Server/Client Boundary** | `'use client'` crea una frontera. Todo lo que esté debajo en el árbol es Client. El Cliente no puede subir al Server. | Un Server Component puede importar un Client Component. Un Client Component NO puede importar un Server Component directamente |
| **Caching en Next.js** | Next.js cachea requests por defecto. `fetch()` en Server Components es cacheado por `revalidate` o `no-store` | Cada `fetch` debe especificar su política de cache: `{ next: { revalidate: 60 } }` o `{ cache: 'no-store' }` |
| **Suspense como Placeholder Declarativo** | `<Suspense fallback={<Spinner />}>` envuelve componentes que "suspenden" (async components, lazy) | Colocar Suspense tan abajo en el árbol como sea posible para mostrar el skeleton solo donde aplica |

---

## 4. Criterios de Decisión

| Situación | Prioriza | Sobre | Por qué |
|-----------|----------|-------|---------|
| Fetch de datos para una página | Server Component con async/await | `useEffect` en Client Component | Server Component: sin JS al cliente, fetch en servidor, mejor LCP |
| Estado que debe sobrevivir navegaciones | URL State (searchParams) o localStorage | useState | useState se resetea en cada navegación; URL state persiste y es bookmarkeable |
| Estado complejo (múltiples sub-values) | `useReducer` | Múltiples `useState` | `useReducer` centraliza la lógica de actualización y es más predecible |
| Comunicación de hijo a padre | Callback prop | Context o global state | Para comunicación directa, un callback es más simple y explícito |
| Datos que necesitan revalidarse | ISR (`revalidate: N`) o Server Action | Polling en el cliente | El servidor invalida el cache sin que el cliente necesite hacer polling |
| Formularios mutating data | Server Actions | API routes + fetch en cliente | Server Actions eliminan la necesidad de un endpoint API para mutaciones simples |

---

## 5. Anti-patrones

| Anti-patrón | Por qué es malo | Qué hacer en su lugar |
|-------------|-----------------|----------------------|
| **`'use client'` en el root layout** | Convierte TODA la aplicación en Client Components, perdiendo todos los beneficios de RSC | Solo usar `'use client'` en los componentes específicos que necesitan interactividad |
| **`useEffect` para derivar estado** | Crea un render extra innecesario (render → effect → setState → re-render) | Calcular el valor derivado directamente en el body del componente |
| **Key que cambia innecesariamente en listas** | Cuando key cambia, React desmonta y remonta el componente completo (se pierde el estado y se hace re-fetch) | Usar un ID estable de los datos como key, nunca el índice del array si el orden puede cambiar |
| **Mutación de estado directamente** | `state.items.push(item)` → React no detecta el cambio (compara referencias) | Crear un nuevo array/objeto: `setState([...state.items, item])` |
| **`useEffect` con dependencias faltantes** | El efecto usa valores que pueden cambiar pero no los declara como dependencias → stale closures | Declarar todas las dependencias. Si el linter advierte, hacer caso. |
| **Fetch en `useEffect` sin librería de data fetching** | Race conditions, falta de cache, sin loading/error states automáticos | Usar React Query / SWR / TanStack Query que manejan todo esto correctamente |

---

## 6. Casos y Ejemplos Reales

### Caso 1: Server Component con Fetch Directo a DB

```typescript
// app/dashboard/page.tsx — Server Component por defecto
// Sin 'use client', sin useEffect, sin useState

import { db } from '@/lib/db'
import { DashboardStats } from '@/components/DashboardStats'
import { RecentActivity } from '@/components/RecentActivity'

// Async directamente — solo posible en Server Components
export default async function DashboardPage() {
  // Fetch paralelo para máxima velocidad
  const [stats, activity] = await Promise.all([
    db.query('SELECT * FROM stats WHERE ...'),
    db.query('SELECT * FROM activity ORDER BY created_at DESC LIMIT 10'),
  ]);

  return (
    <main>
      {/* Pasar datos como props — sin waterfall de fetch */}
      <DashboardStats stats={stats} />
      <RecentActivity activities={activity} />
    </main>
  );
}
```

**Lección:** El Server Component elimina el useEffect de fetch, el estado de loading manual, y el JS enviado al cliente. Los datos llegan en el HTML inicial.

---

### Caso 2: Server Action para Mutación de Datos

```typescript
// app/actions.ts — Server Actions
'use server'

import { revalidatePath } from 'next/cache'
import { db } from '@/lib/db'

export async function createPost(formData: FormData) {
  const title = formData.get('title') as string;
  const content = formData.get('content') as string;

  await db.insert('posts', { title, content });

  // Invalida el cache de la ruta que muestra los posts
  revalidatePath('/dashboard/posts');
}

// app/dashboard/posts/new/page.tsx
import { createPost } from '@/app/actions'

export default function NewPostPage() {
  return (
    // No necesita useState, no necesita fetch, no necesita API endpoint
    <form action={createPost}>
      <input name="title" />
      <textarea name="content" />
      <button type="submit">Publicar</button>
    </form>
  );
}
```

**Lección:** Server Actions eliminan la necesidad de crear endpoints de API para mutaciones simples. El formulario llama directamente a una función del servidor.

---

### Caso 3: Streaming con Suspense para Mejor UX

```typescript
// app/profile/[id]/page.tsx
import { Suspense } from 'react'
import { UserHeader } from './UserHeader'    // Datos rápidos
import { UserPosts } from './UserPosts'      // Datos lentos
import { PostsSkeleton } from './PostsSkeleton'

export default function ProfilePage({ params }) {
  return (
    <main>
      {/* UserHeader se renderiza de inmediato */}
      <UserHeader userId={params.id} />

      {/* UserPosts puede tardar — se muestra skeleton mientras carga */}
      <Suspense fallback={<PostsSkeleton />}>
        <UserPosts userId={params.id} />
      </Suspense>
    </main>
  );
}
```

**Lección:** El usuario ve el header de inmediato (TTFB rápido) y el skeleton de posts. Cuando los posts están listos, se reemplazan. Sin Javascript extra en el cliente.

---

## Conexión con el Cerebro #4

| Habilidad del Cerebro | Aporte de esta fuente |
|------------------------|----------------------|
| Arquitectura de componentes | Server vs Client Component decision tree |
| Rendering patterns | App Router: SSR, SSG, ISR, Streaming automático |
| State management | useState, useReducer, Context — cuándo usar cada uno |
| Performance | Server Components reduce bundle; Suspense mejora percepción de velocidad |
| Data fetching | Server Components async, React Query para cliente, Server Actions para mutaciones |

---

## Preguntas que el Cerebro puede responder

1. ¿Este componente debe ser Server o Client Component? ¿Por qué?
2. ¿Cuándo usar `useState` vs `useReducer`?
3. ¿Cómo implemento data fetching sin race conditions ni memory leaks?
4. ¿Qué es una Server Action y cuándo reemplaza a un API endpoint?
5. ¿Cómo usar Suspense para mostrar skeleton screens mientras carga una sección?
6. ¿Por qué este `useEffect` tiene stale closure y cómo lo corrijo?
7. ¿Cómo estructuro las carpetas de un proyecto con App Router?
