---
source_id: "FUENTE-418"
brain: "brain-software-04-frontend"
niche: "software-development"
title: "Component-Driven Development: The Future of Frontend Architecture"
author: "Dan Abramov, Rachel Nabors"
expert_id: "EXP-418"
type: "article"
language: "en"
year: 2023
distillation_date: "2026-03-03"
distillation_quality: "complete"
loaded_in_notebook: false
version: "1.0.0"
last_updated: "2026-03-03"
changelog:
  - version: "1.0.0"
    date: "2026-03-03"
    changes:
      - "Initial distillation from React Docs and talks"
status: "active"
---

# Component-Driven Development

**Dan Abramov, Rachel Nabors, React Team**

## 1. Principios Fundamentales

> **P1 - Components son la unidad de composición**: En frontend moderno, los componentes son los LEGO blocks. No construyes páginas, construyes componentes que se componen en páginas. Composición sobre herencia.

> **P2 - Props son la interfaz pública**: Un componente debe ser tratado como una función pura: recibe props, retorna UI. La API de tu componente son sus props. Diseñala con cuidado.

> **P3 - Colocation sobre separación por tipo**: No separes por "todos los components en una carpeta, todos los hooks en otra". Coloca lo que está relacionado cerca. El código que cambia junto debe vivir junto.

> **P4 - El estado vive donde se usa**: No levantes todo el estado a Redux "porque así se hace". El estado vive en el componente más bajo del árbol que lo necesita. Prop drilling es mejor que over-abstracting.

> **P5 - Composition > Inheritance**: React no usa herencia de clases para UI. Usa composición de componentes. `children` prop es el mecanismo más poderoso de composición.

## 2. Frameworks y Metodologías

### The Component Spectrum

```
Atoms → Molecules → Organisms → Templates → Pages
```

**Atomic Design** (Brad Frost, aplicado a React):

| Level | Descripción | Ejemplo | Reusabilidad |
|-------|-------------|---------|--------------|
| **Atoms** | Componentes más básicos | Button, Input, Icon | Altísima |
| **Molecules** | Grupos de átomos | SearchBox (Input + Button) | Alta |
| **Organisms** | Secciones complejas | Navbar, Card | Media |
| **Templates** | Estructura sin contenido | Page layout | Baja |
| **Pages** | Template + contenido real | Homepage | Nula |

### Component Types in Modern React

**1. Presentational Components (UI Components)**
```jsx
// No tienen lógica de negocio
// Reciben props, renderizan UI
// Son altamente reutilizables
function Button({ variant, size, children, onClick }) {
  return (
    <button className={`btn btn-${variant} btn-${size}`} onClick={onClick}>
      {children}
    </button>
  );
}
```

**2. Container Components (Smart Components)**
```jsx
// Manejan estado, efectos, lógica de negocio
// No renderizan UI directamente
// Componen UI components
function UserListContainer() {
  const users = useUsers();
  const { filter, setFilter } = useFilter();
  return <UserList users={users} filter={filter} onFilterChange={setFilter} />;
}
```

**3. Custom Hooks (Logic Extraction)**
```jsx
// Extraen lógica reutilizable
// No renderizan nada
// Pueden ser compartidos entre componentes
function useUsers() {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    setLoading(true);
    fetchUsers().then(setUsers).finally(() => setLoading(false));
  }, []);

  return { users, loading };
}
```

### State Management Hierarchy

```
Global State (Redux, Zustand, Context)
    ↓
Module State (React Context for feature)
    ↓
Component State (useState)
    ↓
Derived State (computed from props/state)
    ↓
URL State (search params, hash)
```

**Cuándo usar cada nivel**:

| Nivel | Cuándo usar | Herramienta |
|-------|-------------|-------------|
| **Global** | Auth, theme, user settings | Redux, Zustand |
| **Module** | Feature-specific shared state | React Context |
| **Component** | Local UI state | useState, useReducer |
| **Derived** | Computado de otros valores | useMemo |
| **URL** | Filtro, paginación, selección | URLSearchParams, useSearchParams |

### Component Patterns

**1. Compound Components**
```jsx
// Components que trabajan juntos implícitamente
function Tabs({ children }) {
  const [activeTab, setActiveTab] = useState(0);
  return (
    <TabsContext.Provider value={{ activeTab, setActiveTab }}>
      {children}
    </TabsContext.Provider>
  );
}

function Tab({ children, index }) {
  const { activeTab, setActiveTab } = useContext(TabsContext);
  return <button onClick={() => setActiveTab(index)}>{children}</button>;
}

// Uso:
<Tabs>
  <Tab index={0}>Tab 1</Tab>
  <Tab index={1}>Tab 2</Tab>
</Tabs>
```

**2. Render Props**
```jsx
// Pasa control de render al consumer
function DataFetcher({ url, children }) {
  const [data, setData] = useState(null);
  // fetch logic...
  return children(data);
}

// Uso:
<DataFetcher url="/api/users">
  {(data) => <UserList users={data} />}
</DataFetcher>
```

**3. Higher-Order Components (HOCs)**
```jsx
// Extiende component con funcionalidad
function withLoading(WrappedComponent) {
  return function (props) {
    const [loading, setLoading] = useState(false);
    if (loading) return <Spinner />;
    return <WrappedComponent {...props} loading={loading} setLoading={setLoading} />;
  };
}
```

**4. Custom Hooks (Modern Alternative)**
```jsx
// Preferido sobre HOCs y Render Props
function useLoading() {
  const [loading, setLoading] = useState(false);
  return { loading, setLoading };
}
```

### Performance Patterns

**1. Memoization**
```jsx
// useMemo: Valores costosos
const expensiveValue = useMemo(() => computeExpensive(a, b), [a, b]);

// useCallback: Funciones memoizadas (para props de componentes memoizados)
const handleClick = useCallback(() => doSomething(a, b), [a, b]);

// React.memo: Component que solo re-render si props cambian
const ExpensiveComponent = React.memo(function ({ data }) {
  return <ComplexVisualization data={data} />;
});
```

**2. Code Splitting**
```jsx
// Lazy loading de componentes
const Dashboard = lazy(() => import('./Dashboard'));

function App() {
  return (
    <Suspense fallback={<Loading />}>
      <Dashboard />
    </Suspense>
  );
}
```

**3. Virtualization**
```jsx
// Solo renderiza lo visible
import { useVirtualizer } from '@tanstack/react-virtual';

function VirtualList({ items }) {
  const parentRef = useRef();
  const rowVirtualizer = useVirtualizer({
    count: items.length,
    getScrollElement: () => parentRef.current,
    estimateSize: () => 50,
  });

  return (
    <div ref={parentRef} style={{ height: '400px', overflow: 'auto' }}>
      <div style={{ height: `${rowVirtualizer.getTotalSize()}px` }}>
        {rowVirtualizer.getVirtualItems().map((virtualRow) => (
          <div key={virtualRow.key} style={{ position: 'absolute', top: 0, left: 0, width: '100%', transform: `translateY(${virtualRow.start}px)` }}>
            {items[virtualRow.index]}
          </div>
        ))}
      </div>
    </div>
  );
}
```

## 3. Modelos Mentales

### Modelo de "Unidirectional Data Flow"

```
Props ↓
    Component
    State ↓
    Render ↓
    Events ↑ (callback props)
```

**Características**:
- Los datos fluyen hacia abajo (props)
- Los eventos fluyen hacia arriba (callbacks)
- El componente es una función pura: (props, state) → UI

### Modelo de "Thinking in React"

**Paso 1: Break UI into component hierarchy**
- Dibuja boxes alrededor de cada componente
- Nombralos (Single Responsibility Principle)

**Paso 2: Build a static version**
- Sin interactividad
- Props passed, no state
- Reusability es key

**Paso 3: Identify minimal mutable state**
- ¿Qué datos cambian?
- ¿Dónde viven esos datos?

**Paso 4: Identify where state should live**
- ¿Qué componentes lo necesitan?
- ¿Cuál es el ancestro común más bajo?

**Paso 5: Add inverse data flow**
- Callback props para modificar state
- Events bubble up

### Modelo de "Colocation"

**Traditional (por tipo)**:
```
src/
├── components/
│   ├── Button.jsx
│   └── Input.jsx
├── hooks/
│   ├── useUsers.js
│   └── useAuth.js
├── utils/
│   └── formatDate.js
```

**Colocation (por feature)**:
```
src/
├── features/
│   ├── users/
│   │   ├── UsersList.jsx
│   │   ├── UserCard.jsx
│   │   ├── useUsers.js
│   │   └── utils.js
│   └── auth/
│       ├── LoginForm.jsx
│       ├── useAuth.js
│       └── constants.js
```

**Ventajas de colocation**:
- Código relacionado vive junto
- Mover/renovar features es fácil
- Tree-shaking funciona mejor
- Cognitive load es menor

### Modelo de "Derived State"

**Anti-patrón**: Copiar props a state
```jsx
// ❌ MAL
function UserDisplay({ userId }) {
  const [user, setUser] = useState(null);
  useEffect(() => {
    fetchUser(userId).then(setUser);
  }, [userId]);
  // user es derivado de userId, no necesita state separado
}
```

**Patrón correcto**: Derived state
```jsx
// ✅ BIEN
function UserDisplay({ userId }) {
  const user = useUser(userId); // Hook encapsula fetch + cache
  // user es derivado de userId
}
```

## 4. Criterios de Decisión

### Class Components vs Function Components

| Aspecto | Class | Function |
|---------|-------|----------|
| Syntax | Más verbose | Más conciso |
| Hooks | No soportados | Soportados |
| This binding | Confuso | No this |
| Lifecycle methods | componentDidMount, etc. | useEffect |
| Trend | Legacy | Modern |

**Decision**: Siempre function components con hooks para código nuevo.

### When to Extract a Component

| ✅ Extract cuando | ❌ No extraigas cuando |
|--------------------|------------------------|
| Se repite en 2+ lugares | Se usa una sola vez y es simple |
| Tiene lógica compleja | Es un div con className |
| Tiene su propio estado | Es solo agrupación de JSX |
| Tiene más de 200 líneas | Extraer empeora claridad |
| Tests would be valuable | No hay lógica para testear |

### When to Use Custom Hooks

| ✅ Custom hook cuando | ❌ No necesario cuando |
|------------------------|------------------------|
| Lógica de estado compartible | Lógica simple (< 10 líneas) |
| Efectos side-effects reutilizables | Solo useState aislado |
| Data fetching con cache | Component-specific logic |
| Lógica compleja que ensucia componente | No hay reutilización prevista |

### State Management: When to Use What

| Situation | Tool |
|-----------|------|
| Component local state | useState |
| Múltiples states relacionados | useReducer |
| Lógica compartible | Custom hook |
| Feature-wide state | React Context |
| Global state (auth, theme) | Zustand / Redux |
| Server state | React Query / SWR |

**Regla**: Start simple. Escalar cuando tengas un problema real.

### Server Components vs Client Components

**Server Components** (React 18+):
- Se ejecutan en el servidor
- No pueden tener useState, useEffect
- Pueden acceder a recursos del servidor directamente
- Reducen bundle size

**Client Components**:
- Se ejecutan en el browser
- Pueden tener estado, efectos
- "use client" directive

**Decision**:
- Default: Server Components
- Client: Cuando necesitas interactividad

## 5. Anti-patrones

### Anti-patrón: "Prop Drilling Phobia"

**Problema**: Evitar pasar props a través de múltiples niveles "porque es feo".

**Solución**:
- Prop drilling es mejor que over-abstracting
- Solo usa Context/Zustand cuando realmente es global
- 2-3 niveles de drilling es aceptable

### Anti-patrón: "Giant useEffect"

**Problema**: Un useEffect que hace múltiples cosas.

**Solución**:
- Un efecto por concern
- Separa lógica en custom hooks
- Separa fetching de副作用

### Anti-patrón: "Premature Abstraction"

**Problema**: Crear abstracciones antes de tener múltiples usos.

**Solución**:
- Code twice, then abstract (Rule of Three)
- No crees "reusable" components sin segundo uso confirmado
- Copy-paste es mejor que wrong abstraction

### Anti-patrón: "Everything in Context"

**Problema**: Usar Context para todo, incluso estado local.

**Solución**:
- Context es para estado compartido, no para todo
- El estado que solo usa un componente debe ser local
- Context triggers re-renders en todos consumers

### Anti-patrón: "useMemo Everything"

**Problema**: Memoizar todo "por performance".

**Solución**:
- Solo memoiza cálculos costosos (> 1ms)
- Memo tiene coste (memory, comparison)
- Profile primero, optimize después

### Anti-patrón: "Wrapper Hell"

**Problema**: Múltiples layers de HOCs/providers.

```jsx
// ❌
<AuthProvider>
  <ThemeContext>
    <QueryClientProvider>
      <Router>
        <MyComponent />
      </Router>
    </QueryClientProvider>
  </ThemeContext>
</AuthProvider>
```

**Solución**: Composition patterns, compound components

### Anti-patrón: "Collocated CSS-in-JS Overkill"

**Problema**: Styled components para cada elemento.

**Solución**:
- Usa Tailwind / utility classes
- CSS-in-JS solo para dynamic styles
- Component-level styles, not element-level

### Anti-patrón: "Monolithic Component Files"

**Problema**: 500+ line component files.

**Solución**:
- Extraer subcomponentes
- Custom hooks para lógica
- Constants / types en archivos separados
- Folder structure: `ComponentName/` con archivos relacionados
