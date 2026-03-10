---
source_id: "FUENTE-417"
brain: "brain-software-04-frontend"
niche: "software-development"
title: "React Server Components - Complete Guide"
author: "Vercel, React Team"
expert_id: "EXP-417"
type: "documentation"
language: "en"
year: 2023
distillation_date: "2026-03-02"
distillation_quality: "complete"
loaded_in_notebook: false
version: "1.0.0"
last_updated: "2026-03-02"
changelog:
  - version: "1.0.0"
    date: "2026-03-02"
    changes:
      - "Destilación inicial completa"
status: "active"
---

# React Server Components - Complete Guide

## 1. Principios Fundamentales

> **P1: Server-first por defecto** - Render en el server siempre que sea posible; solo usar client components cuando sea necesario.

> **P2: Cero JS al cliente** - Los Server Components envían HTML al cliente sin JavaScript, mejorando performance.

> **P3: Data fetching en el server** - Acceso directo a bases de datos y APIs sin exponer credenciales.

> **P4: Streaming es nativo** - Los Server Components soportan streaming de HTML incremental por defecto.

## 2. Frameworks y Metodologías

### Server vs Client Components

**Server Components (default):**
- Render en server
- Acceso a backend (DB, APIs)
- No envían JavaScript al cliente
- No pueden usar hooks o event handlers
- Archivos: `*.server.tsx` o sin `"use client"`

**Client Components:**
- Render en client (browser)
- Usan hooks, state, effects
- Manejan interacción (onClick, onChange)
- Requieren `"use client"` directive
- Archivos: `*.client.tsx` o con `"use client"`

### Mental Model

```
┌─────────────────────────────────────┐
│  Server Component (render en server) │
│  ├─ Server Component (nested)       │
│  ├─ Client Component (boundary)     │
│  │   ├─ Client Component (nested)   │
│  │   └─ Server Component (child)    │ ← Server en Client
│  └─ Server Component (nested)       │
└─────────────────────────────────────┘
```

### Streaming con Suspense

```tsx
// Server Component
async function Page() {
  return (
    <main>
      <Header />
      <Suspense fallback={<Skeleton />}>
        <Posts /> {/* async Server Component */}
      </Suspense>
      <Footer />
    </main>
  );
}
```

## 3. Modelos Mentales

**Component Hierarchy**
- ServerComponents pueden contener Client Components
- Client Components pueden contener Server Components
- Pero: Client Components pasados como props deben estar serializables

**Serializability**
- Server Components pasan props a Client Components via JSON
- Funciones, class instances, symbols NO son serializables
- Workaround: Server Component children pasados como `children` prop

**Interactivity Boundaries**
- El límite entre Server y Client es donde empieza la interactividad
- Client Component crea un "interactive subtree"
- Event handlers solo en Client Components

## 4. Criterios de Decisión

### ¿Cuándo usar Server Components?

✅ **Usa Server cuando:**
- Fetching data (DB, APIs)
- Render contenido estático
- Acceso a recursos del server (filesystem, env vars)
- Componentes presentational sin interacción

❌ **Usa Client cuando:**
- Requieres useState, useEffect, hooks
- Manejas eventos (onClick, onChange)
- Usas browser APIs (window, document, localStorage)
- Componentes interactivos (forms, animations)

### Patrón: Server Component con Client Interactive

```tsx
// PostList.server.tsx (Server)
async function PostList() {
  const posts = await db.posts.findMany();

  return (
    <div>
      {posts.map(post => (
        <PostCard key={post.id} post={post} />
      ))}
    </div>
  );
}

// PostCard.client.tsx (Client)
"use client";

function PostCard({ post }) {
  const [liked, setLiked] = useState(false);

  return (
    <article>
      <h3>{post.title}</h3>
      <button onClick={() => setLiked(!liked)}>
        {liked ? '♥' : '♡'} Like
      </button>
    </article>
  );
}
```

### Props que cruzan el boundary

✅ **Serializable (Server → Client):**
- Primitives: string, number, boolean
- Arrays, Objects (con valores serializables)
- Date, Map, Set (con soporte)
- JSX (Server Component children)

❌ **Non-serializable:**
- Functions
- Class instances
- Symbols
- Server Actions (pasados como refs)

## 5. Anti-patrones

❌ **`"use client"` en todo** - Derrota el propósito de RSC; usa solo cuando sea necesario.

❌ **Data fetching en Client Components** - Siempre que sea posible, haz data fetching en Server Components.

❌ **Server Components anidados dentro de Client sin 'children'** - No funciona; el Server Component se serializa como prop.

```tsx
❌ MAL:
function Client() {
  return <Server />; // No funciona
}

✅ BIEN:
function Client({ children }) {
  return <div>{children}</div>;
}

// Uso:
<Client>
  <Server />
</Client>
```

❌ **Hooks en Server Components** - useState, useEffect solo en Client Components.

❌ **Olvidar Suspense boundaries** - Los componentes async deben estar envueltos en Suspense.

## Server Actions

**Server Actions** permiten mutations desde Client Components sin crear API endpoints:

```tsx
// actions.ts (Server)
"use server";

export async function createPost(formData: FormData) {
  const title = formData.get("title");
  await db.posts.create({ title });
  revalidatePath("/posts"); // Invalidate cache
}

// PostForm.client.tsx (Client)
"use client";

import { createPost } from "./actions";

function PostForm() {
  return (
    <form action={createPost}>
      <input name="title" />
      <button type="submit">Create</button>
    </form>
  );
}
```

## Best Practices

1. **Server-first architecture**
   - Server Components por defecto
   - Client Components solo para interactividad

2. **Data fetching donde corresponda**
   - En Server Components, no en useEffect
   - Parallel queries con Promise.all()

3. **Streaming con Suspense**
   - Envolver componentes async en Suspense
   - Proporcionar skeletons/loading states

4. **Server Actions para mutations**
   - Reemplazan API endpoints para mutations
   - Validación en el server
   - revalidatePath() para invalidación de caché

5. **Composición inteligente**
   - Pasar Server Components como `children` a Client Components
   - Minimizar prop drilling con composition

## Performance Implications

**Beneficios:**
- Bundle size reducido (menos JavaScript al cliente)
- Faster TTI (Time to Interactive)
- SEO mejorado (HTML completo en server)
- Data fetching más rápido (sin client-side round trips)

**Costos:**
- Server compute increase
- Complexity en composition
- Learning curve para el equipo

## Referencias

- **React Server Components RFC**: https://github.com/reactjs/rfcs/blob/main/text/0188-server-components.md
- **Next.js RSC Docs**: https://nextjs.org/docs/app/building-your-application/rendering/server-components
- **Vercel RSC Guide**: https://vercel.com/docs/frameworks/nextjs
