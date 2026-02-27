---
source_id: "FUENTE-408"
brain: "brain-software-04-frontend-architecture"
niche: "software-development"
title: "Modern State Management: TanStack Query (React Query) + Zustand"
author: "Tanner Linsley (TanStack) + pmndrs team (Zustand)"
expert_id: "EXP-408"
type: "documentation"
language: "en"
year: 2024
isbn: "N/A"
url: "https://tanstack.com/query + https://zustand-demo.pmnd.rs"
skills_covered: ["H3", "H4", "H6"]
distillation_date: "2026-02-26"
distillation_quality: "complete"
loaded_in_notebook: false
version: "1.0.0"
last_updated: "2026-02-26"
changelog:
  - version: "1.0.0"
    date: "2026-02-26"
    changes:
      - "Ficha creada con destilación completa"
      - "Cubre TanStack Query v5 + Zustand v4"
      - "Formato estándar del MasterMind Framework v2"
status: "active"

habilidad_primaria: "State Management Moderno — Server State vs Client State"
habilidad_secundaria: "Caching de datos, Optimistic Updates, Sincronización con el servidor"
capa: 2
capa_nombre: "Frameworks Operativos"
relevancia: "CRÍTICA — El 60% de la complejidad de una app React es manejar estado correctamente. TanStack Query elimina la categoría de bugs de 'datos stale, loading states manuales, y race conditions de fetch'. Zustand reemplaza Redux para UI state sin su boilerplate."
gap_que_cubre: "State management avanzado — las fuentes anteriores cubren useState/useReducer pero no las librerías de producción"
---

# FUENTE-408: Modern State Management
## TanStack Query + Zustand | Server State vs Client State

---

## Tesis Central

> El error conceptual más común en React es tratar todo el estado igual. Los datos del servidor (lo que está en la DB) y el estado del cliente (lo que el usuario está haciendo) son fundamentalmente diferentes y necesitan herramientas diferentes. TanStack Query maneja el server state. Zustand maneja el client state. Cuando usas la herramienta correcta para cada tipo, el 60% de la complejidad de tu app desaparece.

La pregunta que cambia todo: "¿Este estado existe en el servidor, o solo existe en el cliente?" La respuesta determina la herramienta.

---

## 1. Principios Fundamentales

> **P1: Server state y client state son fundamentalmente diferentes**
> El server state (datos de la API, la DB) es asíncrono, potencialmente stale, compartido entre múltiples clientes, y el servidor es la fuente de verdad. El client state (qué tab está activa, si un modal está abierto) es síncrono, local, y el cliente es la fuente de verdad.
> Usar `useState` para ambos es el error de diseño más común en apps React.
> *Aplicación: antes de crear un estado, clasifícalo: "¿Existe en el servidor?" → TanStack Query. "¿Existe solo en este cliente?" → useState o Zustand.*

> **P2: El cache de TanStack Query es la fuente de verdad para server state**
> TanStack Query mantiene un cache de todos los datos fetched, con su estado (fresh, stale, fetching). Múltiples componentes que piden los mismos datos no hacen múltiples requests — comparten el cache. Cuando el cache se invalida, todos los componentes que lo usan se actualizan automáticamente.
> *Aplicación: nunca duplicar datos del servidor en useState. Si lo necesitas en dos componentes, ambos leen del mismo cache de Query.*

> **P3: La invalidación es más importante que la actualización manual**
> En lugar de actualizar el cache manualmente después de una mutación (error-prone), marcar los queries relacionados como "stale" y dejar que TanStack Query los refetch automáticamente. El servidor siempre tiene la verdad; el cliente solo necesita pedir datos frescos.
> *Aplicación: después de un `mutation.mutate()`, llamar `queryClient.invalidateQueries({ queryKey: ['users'] })`. El refetch ocurre automáticamente.*

> **P4: Zustand es un store sin boilerplate — el estado es una función**
> Zustand no necesita providers, reducers, actions, ni dispatchers. Un store es una función `create()` que devuelve el estado y los setters. Se consume con un hook. La API completa cabe en 10 líneas.
> *Aplicación: cuando necesitas estado compartido entre componentes no relacionados (breadcrumbs, cart count, user preferences) sin prop drilling, Zustand es la herramienta más simple.*

> **P5: Optimistic Updates mejoran la UX pero requieren rollback**
> Un optimistic update actualiza el UI antes de que el servidor confirme la mutación. Si el servidor falla, se debe revertir. TanStack Query tiene un patrón explícito para esto: `onMutate` (actualiza el cache), `onError` (revierte), `onSettled` (invalidates para refetch fresco).
> *Aplicación: los optimistic updates son apropiados para acciones de alta frecuencia donde el usuario espera inmediatez (like, follow, marcar como leído). Para transacciones críticas (pago, borrar cuenta), esperar confirmación del servidor.*

---

## 2. Frameworks y Metodologías

### Framework 1: TanStack Query — El Ciclo Completo

**Propósito:** Manejar server state (fetch, cache, sincronización) sin código manual de loading/error/stale.

**Setup:**
```typescript
// app/providers.tsx
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 60 * 1000, // 1 minuto antes de marcar como stale
      retry: 1,              // Solo 1 retry en caso de error
    },
  },
});

export function Providers({ children }) {
  return (
    <QueryClientProvider client={queryClient}>
      {children}
    </QueryClientProvider>
  );
}
```

**Queries (leer datos):**
```typescript
// hooks/useUsers.ts
import { useQuery } from '@tanstack/react-query'

// Query keys como arrays — jerarquía para invalidación granular
const userKeys = {
  all: ['users'] as const,
  lists: () => [...userKeys.all, 'list'] as const,
  list: (filters: UserFilters) => [...userKeys.lists(), { filters }] as const,
  details: () => [...userKeys.all, 'detail'] as const,
  detail: (id: string) => [...userKeys.details(), id] as const,
};

function useUsers(filters: UserFilters) {
  return useQuery({
    queryKey: userKeys.list(filters),
    queryFn: () => api.users.getAll(filters),
    staleTime: 5 * 60 * 1000, // 5 minutos para esta query específica
  });
}

function useUser(id: string) {
  return useQuery({
    queryKey: userKeys.detail(id),
    queryFn: () => api.users.getById(id),
    enabled: !!id, // Solo hacer el fetch si hay un id
  });
}

// Uso en el componente — cero boilerplate de loading/error manual
function UsersList() {
  const { data, isLoading, isError, error } = useUsers({ role: 'admin' });

  if (isLoading) return <UsersSkeleton />;
  if (isError) return <ErrorMessage message={error.message} />;

  return <ul>{data.map(user => <UserRow key={user.id} user={user} />)}</ul>;
}
```

**Mutations (modificar datos):**
```typescript
// hooks/useCreateUser.ts
import { useMutation, useQueryClient } from '@tanstack/react-query'

function useCreateUser() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (newUser: CreateUserInput) => api.users.create(newUser),

    // Optimistic update — actualiza el UI antes de la respuesta
    onMutate: async (newUser) => {
      // Cancela refetches en curso para evitar race conditions
      await queryClient.cancelQueries({ queryKey: userKeys.lists() });

      // Guarda el estado anterior para poder revertir
      const previousUsers = queryClient.getQueryData(userKeys.lists());

      // Actualiza el cache optimísticamente
      queryClient.setQueryData(userKeys.lists(), (old: User[]) => [
        ...old,
        { ...newUser, id: 'temp-' + Date.now(), status: 'pending' },
      ]);

      return { previousUsers }; // Context para onError
    },

    // Si el servidor falla, revertir al estado anterior
    onError: (err, newUser, context) => {
      queryClient.setQueryData(userKeys.lists(), context?.previousUsers);
    },

    // Siempre invalidar para obtener datos frescos del servidor
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: userKeys.lists() });
    },
  });
}

// Uso
function CreateUserButton() {
  const { mutate, isPending } = useCreateUser();

  return (
    <button
      onClick={() => mutate({ name: 'Alice', email: 'alice@example.com' })}
      disabled={isPending}
    >
      {isPending ? 'Creando...' : 'Crear Usuario'}
    </button>
  );
}
```

---

### Framework 2: Zustand — Store Minimalista para Client State

**Propósito:** Compartir client state entre componentes sin prop drilling ni Redux boilerplate.

**Cuándo usar:** State que existe solo en el cliente (UI state, user preferences, shopping cart, modal stack, theme).

```typescript
// stores/useCartStore.ts
import { create } from 'zustand'
import { persist } from 'zustand/middleware'

interface CartItem {
  productId: string;
  quantity: number;
  price: number;
}

interface CartStore {
  // State
  items: CartItem[];
  isOpen: boolean;

  // Actions (mutators)
  addItem: (item: CartItem) => void;
  removeItem: (productId: string) => void;
  updateQuantity: (productId: string, quantity: number) => void;
  clearCart: () => void;
  toggleCart: () => void;

  // Computed (selectores derivados)
  totalItems: () => number;
  totalPrice: () => number;
}

export const useCartStore = create<CartStore>()(
  persist( // Middleware: persiste en localStorage automáticamente
    (set, get) => ({
      items: [],
      isOpen: false,

      addItem: (item) => set((state) => ({
        items: state.items.some(i => i.productId === item.productId)
          ? state.items.map(i =>
              i.productId === item.productId
                ? { ...i, quantity: i.quantity + item.quantity }
                : i
            )
          : [...state.items, item],
      })),

      removeItem: (productId) => set((state) => ({
        items: state.items.filter(i => i.productId !== productId),
      })),

      updateQuantity: (productId, quantity) => set((state) => ({
        items: state.items.map(i =>
          i.productId === productId ? { ...i, quantity } : i
        ),
      })),

      clearCart: () => set({ items: [] }),
      toggleCart: () => set((state) => ({ isOpen: !state.isOpen })),

      // Computed — calculado en el momento de leer
      totalItems: () => get().items.reduce((sum, i) => sum + i.quantity, 0),
      totalPrice: () => get().items.reduce((sum, i) => sum + i.price * i.quantity, 0),
    }),
    { name: 'cart-storage' } // Key en localStorage
  )
);

// Uso — leer solo el slice que necesitas (evita re-renders innecesarios)
function CartIcon() {
  const totalItems = useCartStore(state => state.totalItems());
  // Solo re-renderiza cuando totalItems cambia, no con cualquier cambio del store
  return <span>{totalItems}</span>;
}

function CartPanel() {
  const { items, removeItem, totalPrice } = useCartStore();
  return (/* ... */);
}
```

---

### Framework 3: Árbol de Decisión de State Management

**Propósito:** Determinar qué herramienta usar para cada tipo de estado.

```
¿De dónde vienen estos datos?

├── SERVIDOR (API, DB) → TanStack Query
│   ├── Datos de usuario, productos, posts, etc.
│   ├── Cualquier cosa que venga de un fetch/async
│   └── Datos que pueden cambiar desde otro cliente
│
└── CLIENTE (solo existe aquí) → useState / Zustand
    │
    ├── ¿Solo lo necesita un componente?
    │   └── useState / useReducer (local)
    │
    └── ¿Lo necesitan múltiples componentes no relacionados?
        ├── ¿Es estado de UI temporal? (modal open, tab activo)
        │   └── Zustand (no necesita persistencia)
        │
        ├── ¿Necesita persistir entre sesiones? (tema, preferencias, carrito)
        │   └── Zustand + persist middleware
        │
        └── ¿Es estado de URL? (filtros, página, sort)
            └── URL state (searchParams) — el mejor storage para estado compartible
```

---

## 3. Modelos Mentales

| Modelo | Descripción | Aplicación Práctica |
|--------|-------------|---------------------|
| **Cache como Base de Datos del Cliente** | TanStack Query es una base de datos en memoria para datos del servidor. Los componentes "leen" del cache; las queries lo populan; las mutations lo invalidan. | Dos componentes que piden `useUser('123')` comparten el mismo cache — solo hay un fetch. |
| **Stale-While-Revalidate** | El usuario ve datos cacheados inmediatamente (aunque sean stale) mientras el refetch ocurre en background. UX percibida: instantánea. | Al navegar a una página ya visitada, los datos aparecen de inmediato + se actualizan silenciosamente. |
| **Slices de Zustand** | Leer solo el slice del store que necesitas evita re-renders. `useCartStore(s => s.totalItems)` solo re-renderiza cuando `totalItems` cambia. | Nunca hacer `const store = useCartStore()` — seleccionar el mínimo necesario. |
| **Invalidación Cascada** | Las query keys son jerárquicas. Invalidar `['users']` invalida `['users', 'list']` y `['users', 'detail', '123']` al mismo tiempo. | Después de crear un usuario, invalidar `['users']` — automáticamente refresca listas y detalles. |
| **Error Boundary de Queries** | Los errores de TanStack Query pueden capturarse con Error Boundaries de React. Un query que falla puede mostrar un UI de error sin que el componente lo maneje explícitamente. | Usar `throwOnError: true` en queries críticas para que el Error Boundary los capture. |
| **Optimistic vs Pessimistic UI** | Optimistic: actualiza el UI antes de la confirmación del servidor. Pessimistic: espera la confirmación. | Optimistic para acciones de bajo riesgo (like, reorder). Pessimistic para transacciones críticas (pago, borrar). |

---

## 4. Criterios de Decisión

| Situación | Prioriza | Sobre | Por qué |
|-----------|----------|-------|---------|
| Datos que vienen de una API | TanStack Query | `useState` + `useEffect` | Query maneja cache, loading, error, stale, refetch automático |
| Estado compartido entre componentes lejanos | Zustand | Prop drilling o Context | Zustand es más simple, performante (solo re-render los suscriptores), y testeable |
| Estado de filtros de búsqueda en URL | URL state (searchParams) | useState o Zustand | Los filtros en URL son compartibles, bookmarkeables, y sobreviven reloads |
| Actualizaciones de alta frecuencia en tabla | Zustand con immer | Redux Toolkit | Zustand con immer es más simple para mutations complejas |
| Estado global de Auth | Zustand o Context | TanStack Query | El user auth es client state (token, permisos) aunque los datos vengan del servidor |
| Cache de datos por tiempo limitado | `staleTime` en TanStack Query | setTimeout + invalidación manual | `staleTime` es declarativo, no imperativo — se define una vez, funciona siempre |

---

## 5. Anti-patrones

| Anti-patrón | Por qué es malo | Qué hacer en su lugar |
|-------------|-----------------|----------------------|
| **`useState` + `useEffect` para fetch** | Race conditions, sin cache, loading/error manual, datos duplicados, sin deduplication | TanStack Query — maneja todo esto por defecto |
| **Duplicar server state en Zustand** | Dos fuentes de verdad → datos pueden divergir → bugs sutiles | Solo Zustand para client state. TanStack Query es la fuente de verdad para server state. |
| **`queryClient.setQueryData` en lugar de invalidateQueries** | Actualización manual puede desincronizarse con el servidor | Invalidar después de mutations — el servidor siempre tiene la verdad |
| **Query keys como strings simples** | `useQuery('users')` — no es posible invalidar queries relacionadas parcialmente | Query keys como arrays jerárquicos: `['users', 'list', { filters }]` |
| **Zustand store gigante con todo** | Un store enorme produce re-renders en componentes no relacionados | Múltiples stores pequeños por dominio (useCartStore, useUIStore, useAuthStore) |
| **`useStore()` sin selector** | Lee todo el store y re-renderiza con cualquier cambio | `useStore(state => state.specificField)` — solo re-renderiza cuando ese campo cambia |

---

## 6. Casos y Ejemplos Reales

### Caso 1: Eliminando 300 líneas de código con TanStack Query

**Situación:** Un equipo tenía un dashboard con 12 componentes que hacían fetch independientemente con el mismo patrón: `useState(loading/error/data)` + `useEffect(fetch)`. 300 líneas de boilerplate idéntico.

**Migración:**
```typescript
// Antes — 25 líneas por componente × 12 = 300 líneas
const [data, setData] = useState(null);
const [loading, setLoading] = useState(true);
const [error, setError] = useState(null);

useEffect(() => {
  setLoading(true);
  fetch('/api/stats')
    .then(r => r.json())
    .then(data => { setData(data); setLoading(false); })
    .catch(err => { setError(err); setLoading(false); });
}, []);

// Después — 4 líneas por componente
const { data, isLoading, isError } = useQuery({
  queryKey: ['stats'],
  queryFn: () => api.getStats(),
});
```

**Resultado:** 300 → ~50 líneas. Sin race conditions. Cache automático — si dos componentes piden `/api/stats`, solo hay un request. Refetch automático cuando la ventana recupera el foco.

---

### Caso 2: Linear — Optimistic Updates en un Kanban

**Situación:** Linear (el tool de gestión de proyectos) necesita que cuando el usuario arrastra un issue entre columnas, el cambio sea instantáneo en el UI. Esperar la respuesta del servidor crearía latencia perceptible.

**Patrón de optimistic update:**
```typescript
const { mutate: moveIssue } = useMutation({
  mutationFn: ({ issueId, newStatus }) =>
    api.issues.updateStatus(issueId, newStatus),

  onMutate: async ({ issueId, newStatus }) => {
    await queryClient.cancelQueries({ queryKey: ['issues'] });
    const previousIssues = queryClient.getQueryData(['issues']);

    // Mueve el issue instantáneamente en el cache
    queryClient.setQueryData(['issues'], (old: Issue[]) =>
      old.map(issue =>
        issue.id === issueId ? { ...issue, status: newStatus } : issue
      )
    );

    return { previousIssues };
  },

  onError: (err, vars, context) => {
    // Revierte si el servidor rechaza el cambio
    queryClient.setQueryData(['issues'], context?.previousIssues);
    toast.error('No se pudo mover el issue. Revertiendo...');
  },

  onSettled: () => {
    queryClient.invalidateQueries({ queryKey: ['issues'] });
  },
});
```

**Lección:** El usuario experimenta latencia cero. Si el servidor falla (raro), el revert es automático con un mensaje claro. Esta es la arquitectura detrás de la sensación de "rapidez" de Linear.

---

### Caso 3: Auth Store con Zustand + Persistencia

**Situación:** El estado de autenticación (token, user data, permissions) necesita estar disponible en toda la app, persistir entre reloads, y ser fácil de actualizar desde cualquier componente.

```typescript
// stores/useAuthStore.ts
interface AuthState {
  token: string | null;
  user: User | null;
  permissions: string[];
  login: (credentials: LoginInput) => Promise<void>;
  logout: () => void;
  hasPermission: (permission: string) => boolean;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      token: null,
      user: null,
      permissions: [],

      login: async (credentials) => {
        const { token, user } = await api.auth.login(credentials);
        set({ token, user, permissions: user.permissions });
      },

      logout: () => set({ token: null, user: null, permissions: [] }),

      hasPermission: (permission) =>
        get().permissions.includes(permission),
    }),
    {
      name: 'auth-storage',
      // Solo persistir el token, no el user completo
      partialize: (state) => ({ token: state.token }),
    }
  )
);

// Uso en cualquier componente — sin prop drilling ni Provider
function AdminButton() {
  const hasPermission = useAuthStore(s => s.hasPermission);
  if (!hasPermission('admin:write')) return null;
  return <button>Acción Admin</button>;
}
```

**Lección:** Zustand con `persist` y `partialize` es el patrón ideal para auth state: persiste solo el token (seguro), rehidrata el estado en reloads, y es accesible desde cualquier componente.

---

## Conexión con el Cerebro #4

| Habilidad del Cerebro | Aporte de esta fuente |
|------------------------|----------------------|
| Data fetching sin boilerplate | TanStack Query elimina el patrón `useState + useEffect + fetch` manual |
| Estado global simple | Zustand reemplaza Redux sin su boilerplate para UI state |
| UX de alta calidad | Optimistic updates, stale-while-revalidate, skeleton automático |
| Contratos con Cerebro #5 (Backend) | Query keys como mapa explícito de los endpoints que el frontend consume |
| Performance | Deduplication de requests, cache automático, re-renders mínimos con selectores |

---

## Preguntas que el Cerebro puede responder

1. ¿Debo usar TanStack Query o Zustand para este estado?
2. ¿Cómo implemento un optimistic update con rollback automático?
3. ¿Por qué mis datos se ven stale aunque acabo de hacer una mutación?
4. ¿Cómo compartir datos del servidor entre múltiples componentes sin hacer dos requests?
5. ¿Cuándo usar `invalidateQueries` vs `setQueryData` después de una mutación?
6. ¿Cómo persistir estado de Zustand en localStorage sin perder type safety?
7. ¿Cómo estructurar las query keys para poder invalidar granularmente?
