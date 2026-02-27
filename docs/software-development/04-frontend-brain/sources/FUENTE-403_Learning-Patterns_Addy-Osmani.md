---
source_id: "FUENTE-403"
brain: "brain-software-04-frontend-architecture"
niche: "software-development"
title: "Learning Patterns: Design Patterns for JavaScript and React"
author: "Addy Osmani & Lydia Hallie"
expert_id: "EXP-403"
type: "book"
language: "en"
year: 2022
isbn: "978-1098134280"
url: "https://www.patterns.dev"
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
      - "Formato estándar del MasterMind Framework v2"
status: "active"

habilidad_primaria: "Design Patterns para JavaScript y React"
habilidad_secundaria: "Web Performance y Rendering Patterns (SSR, SSG, ISR, Streaming)"
capa: 2
capa_nombre: "Frameworks Operativos"
relevancia: "CRÍTICA — Conocer los patrones evita reinventar soluciones a problemas ya resueltos. Los rendering patterns determinan directamente los Core Web Vitals del producto."
---

# FUENTE-403: Learning Patterns
## Addy Osmani & Lydia Hallie | Design Patterns para JS y React

---

## Tesis Central

> Los patrones no son recetas — son vocabulario. Cuando un equipo conoce los patrones, puede comunicar "esto es un Observer" o "necesitamos un HOC aquí" en lugar de describir el mecanismo completo cada vez. Más importante: los rendering patterns determinan la experiencia del usuario antes de que escribas una sola línea de lógica de negocio.

Un producto construido con el rendering pattern incorrecto puede tener métricas de CWV malas desde la primera línea de código, sin importar cuánto se optimice después.

---

## 1. Principios Fundamentales

> **P1: El rendering pattern correcto es la decisión más impactante en performance**
> Antes de escribir componentes, elegir entre CSR, SSR, SSG, ISR, o Streaming define el TTFB, FCP y LCP del producto. No hay optimización posterior que compense haber elegido mal este punto inicial.
> *Aplicación: la primera pregunta de arquitectura de cualquier feature es "¿cómo se va a renderizar esto y por qué?"*

> **P2: La composición es superior a la herencia para componentes**
> Construir componentes pequeños y componibles (que aceptan `children` o render props) es más flexible y mantenible que crear jerarquías de herencia o mega-componentes. Un componente que hace una cosa bien es más valioso que uno que hace todo.
> *Aplicación: si un componente tiene >200 líneas o >5 props, probablemente necesita descomponerse.*

> **P3: El estado debe vivir en el nivel más bajo posible**
> State lifting innecesario causa re-renders en toda la cadena de padres. Si solo un componente necesita un estado, ese estado debe vivir en ese componente, no en el padre o en el store global.
> *Aplicación: antes de mover estado "arriba", pregunta: "¿realmente necesito compartirlo con otro componente?"*

> **P4: Los patrones de carga importan tanto como el contenido**
> La percepción de velocidad del usuario depende de cuándo ve algo útil (FCP), no solo de cuándo termina de cargar todo. Progressive loading, skeleton screens y streaming mejoran la percepción sin cambiar el tiempo total de carga.
> *Aplicación: optimizar para "cuándo el usuario puede empezar a usar la página" es más valioso que optimizar el tiempo total de carga.*

> **P5: La memoización es una optimización — aplícala solo con medición**
> `React.memo`, `useMemo`, `useCallback` tienen un costo (comparación) y una ganancia (evitar re-render). El costo solo vale si el render que se evita es significativamente más caro que la comparación. La memoización prematura oscurece el código sin beneficio real.
> *Aplicación: primero mide con React DevTools Profiler. Solo memoiza lo que el profiler confirma que es un cuello de botella.*

---

## 2. Frameworks y Metodologías

### Framework 1: Rendering Patterns — Árbol de Decisión

**Propósito:** Elegir el rendering pattern correcto para cada tipo de página o feature.

```
¿El contenido cambia por usuario o en tiempo real?
│
├── NO — Contenido estático o semi-estático
│   ├── ¿Cambia cada días/semanas? → SSG (Static Site Generation)
│   │     Build-time: genera HTML estático. Máximo performance.
│   │     Ejemplos: landing pages, documentación, blogs
│   │
│   └── ¿Cambia cada minutos/horas? → ISR (Incremental Static Regeneration)
│         Regenera en background. HTML pre-generado + actualización silenciosa.
│         Ejemplos: e-commerce catálogo, noticias, dashboards con datos semi-frescos
│
└── SÍ — Contenido dinámico o personalizado
    ├── ¿Requiere SEO o buen FCP/LCP? → SSR (Server-Side Rendering)
    │     Genera HTML por request. TTFB mayor que SSG pero contenido fresco.
    │     Ejemplos: perfil de usuario, search results, páginas autenticadas con SEO
    │
    ├── ¿Es una app SPA sin requerimientos SEO? → CSR (Client-Side Rendering)
    │     El browser renderiza todo. Sin TTFB de server render, pero FCP más lento.
    │     Ejemplos: dashboards internos, apps con auth wall, herramientas
    │
    └── ¿Hay partes estáticas + partes dinámicas en la misma página? → Streaming SSR
          React 18 + Next.js App Router. Envía el HTML estático primero,
          streamed partes dinámicas cuando están listas (Suspense boundaries).
          Ejemplos: e-commerce con header estático + personalization dinámico
```

**Métricas que cada pattern afecta:**

| Pattern | TTFB | FCP | LCP | TTI | SEO |
|---------|------|-----|-----|-----|-----|
| CSR | ⚡ | 🐌 | 🐌 | 🐌 | ❌ |
| SSR | 🐌 | ⚡ | ⚡ | 🐌 | ✅ |
| SSG | ⚡ | ⚡ | ⚡ | ⚡ | ✅ |
| ISR | ⚡ | ⚡ | ⚡ | ⚡ | ✅ |
| Streaming | ⚡ | ⚡ | ⚡ | 🟡 | ✅ |

---

### Framework 2: Patrones de Componentes React

**Propósito:** Resolver problemas recurrentes de organización de componentes con soluciones probadas.

**Compound Components Pattern** — Para componentes que comparten estado implícito:
```jsx
// En lugar de un mega-componente con 15 props:
<Select
  options={options}
  placeholder="Selecciona..."
  isMulti={true}
  isSearchable={true}
  maxMenuHeight={200}
  onMenuOpen={...}
  onMenuClose={...}
/>

// Compound pattern — componible y legible:
<Select>
  <Select.Trigger placeholder="Selecciona..." />
  <Select.Menu maxHeight={200}>
    {options.map(opt => (
      <Select.Option key={opt.value} value={opt.value}>
        {opt.label}
      </Select.Option>
    ))}
  </Select.Menu>
</Select>
```

**Provider Pattern** — Para state compartido entre un subárbol:
```jsx
// Context + Provider para evitar prop drilling
const ThemeContext = createContext();

function ThemeProvider({ children }) {
  const [theme, setTheme] = useState('light');
  return (
    <ThemeContext.Provider value={{ theme, setTheme }}>
      {children}
    </ThemeContext.Provider>
  );
}

// Custom hook para consumir el contexto
function useTheme() {
  return useContext(ThemeContext);
}
```

**Container/Presentational Pattern** — Separación de lógica y UI:
```jsx
// Presentational: solo UI, sin lógica de negocio
function UserCard({ name, avatar, role, onFollow }) {
  return (
    <div className="card">
      <img src={avatar} alt={name} />
      <h3>{name}</h3>
      <p>{role}</p>
      <button onClick={onFollow}>Follow</button>
    </div>
  );
}

// Container: lógica y data fetching
function UserCardContainer({ userId }) {
  const { data, isLoading } = useFetchUser(userId);
  const { mutate: follow } = useFollowUser();

  if (isLoading) return <UserCardSkeleton />;
  return <UserCard {...data} onFollow={() => follow(userId)} />;
}
```

**Custom Hooks Pattern** — Extraer y reutilizar lógica stateful:
```jsx
// En lugar de repetir lógica de fetch en cada componente:
function useUserData(userId) {
  const [data, setData] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetch(`/api/users/${userId}`)
      .then(r => r.json())
      .then(setData)
      .catch(setError)
      .finally(() => setIsLoading(false));
  }, [userId]);

  return { data, isLoading, error };
}
```

---

### Framework 3: Optimización de Performance — El Proceso

**Propósito:** Mejorar Core Web Vitals de forma sistemática, no por instinto.

```
1. MEDIR primero
   → Lighthouse (Chrome DevTools o CI)
   → Web Vitals extension
   → React DevTools Profiler para re-renders

2. IDENTIFICAR el cuello de botella
   → LCP alto: imagen grande sin priority, fuente con FOIT, SSR lento
   → CLS alto: imágenes sin dimensiones, fuentes que cargan tarde, ads dinámicos
   → INP alto: JavaScript bloqueante, event handlers pesados, re-renders excesivos

3. APLICAR la solución específica
   → LCP: <Image priority />, preload, server components
   → CLS: aspect-ratio, skeleton screens, width/height en imágenes
   → INP: code splitting, debounce, memoización confirmada con profiler

4. MEDIR de nuevo para confirmar mejora

5. DOCUMENTAR la causa y la solución para el equipo
```

---

## 3. Modelos Mentales

| Modelo | Descripción | Aplicación Práctica |
|--------|-------------|---------------------|
| **Rendering como Presupuesto** | El browser tiene un presupuesto de ~16ms por frame para 60fps. Cualquier trabajo que exceda ese presupuesto causa jankyness | Dividir el trabajo pesado en chunks con `setTimeout` o web workers |
| **Estado como Single Source of Truth** | Cada dato debe tener una sola fuente. Derivaciones se calculan, no se duplican | Si tienes `isLoading` y `data`, no añadir `isEmpty` — calcularlo: `!isLoading && !data` |
| **Componente como Función Pura** | Dado el mismo estado y props, un componente debe producir el mismo output siempre | Side effects en `useEffect`, no en el body del componente |
| **Cascade de Re-renders** | Un re-render del padre re-renderiza todos sus hijos (a menos que estén memoizados) | Identificar el componente más alto que puede encapsular el state sin propagarlo innecesariamente |
| **Chunking como Respeto al Usuario** | El bundle completo de JS bloquea el thread antes de que el usuario pueda interactuar | Code splitting por ruta y por feature; cargar solo lo necesario para la interacción actual |
| **Progressive Enhancement** | Construir para el caso básico (HTML/CSS) y mejorar con JS cuando está disponible | Los componentes que pueden funcionar sin JS son más resilientes y mejores para SEO |

---

## 4. Criterios de Decisión

| Situación | Prioriza | Sobre | Por qué |
|-----------|----------|-------|---------|
| Página con datos estáticos y SEO importante | SSG / ISR | SSR | SSG es más rápido (CDN cache) y sin costo de server por request |
| Dashboard con auth y datos personalizados | CSR o SSR con auth boundary | SSG | Los datos son únicos por usuario; SSG no puede pre-generarlos |
| Componente con renders frecuentes | Verificar con Profiler primero | Memoizar inmediatamente | La memoización tiene costo; solo vale si el render es más costoso |
| Estado compartido entre componentes distantes | Context o Zustand | Prop drilling de 3+ niveles | Prop drilling más de 2 niveles es señal de necesitar un patrón de state management |
| Imágenes en el fold | `priority` prop en Next.js `<Image>` | Lazy load (default) | Las imágenes LCP deben precargarse; el lazy load las retrasa |
| Rutas grandes y complejas | Dynamic import / lazy loading | Bundle monolítico | Code splitting por ruta reduce el JS inicial y mejora el TTI |

---

## 5. Anti-patrones

| Anti-patrón | Por qué es malo | Qué hacer en su lugar |
|-------------|-----------------|----------------------|
| **State en el nivel más alto posible** | Re-renders innecesarios en toda la cadena de componentes | State en el componente más bajo que lo necesita. Compartir solo lo que realmente necesita múltiples componentes |
| **`useEffect` para sincronizar state derivado** | Crea re-renders extra (efecto dispara actualización que dispara efecto) | Calcular el estado derivado directamente en el render: `const isEmpty = data.length === 0` |
| **Un mega-componente para todo** | Difícil de testear, mantener, reutilizar. Genera props drilling y re-renders masivos | Descomponer en componentes con una responsabilidad cada uno (SRP) |
| **Memoización prematura** | Añade complejidad sin garantía de mejora; la comparación de dependencias también tiene costo | Medir primero con React Profiler; memoizar solo lo que el profiler confirma como problema |
| **Importar toda la librería** | Bundle grande que el usuario descarga aunque solo use una función | Tree-shakeable imports: `import { debounce } from 'lodash-es'` en lugar de `import _ from 'lodash'` |
| **Fetch en useEffect sin cleanup** | Race conditions (respuestas que llegan desordenadas) y memory leaks en componentes desmontados | Usar AbortController en el cleanup function, o usar React Query / SWR que lo manejan automáticamente |

---

## 6. Casos y Ejemplos Reales

### Caso 1: Airbnb y la Migración de CSR a SSR

**Situación:** El listing page de Airbnb era una SPA con CSR. El LCP era alto porque el HTML inicial no tenía contenido — el browser debía descargar JS, ejecutarlo, y luego renderizar.

**Decisión:** Migrar el listing page a SSR (luego a streaming SSR con React 18). El HTML inicial ya contiene el contenido del listado; el browser puede pintar inmediatamente.

**Resultado:** LCP mejoró significativamente. El contenido que el usuario necesita (fotos, precio, descripción) está en el HTML inicial sin depender de JS.

**Lección:** Para páginas con contenido público y SEO crítico, SSR o SSG son siempre superiores a CSR en métricas de LCP.

---

### Caso 2: Compound Components en una Design System

**Situación:** Un equipo de design system necesita un componente `Modal` que soporte muchas variaciones: con/sin footer, con/sin scrollable content, diferentes tamaños.

```jsx
// ❌ Prop-driven — explosión de props
<Modal
  title="Confirmar"
  content="¿Estás seguro?"
  showFooter={true}
  footerContent={<Button>Confirmar</Button>}
  size="md"
  scrollable={false}
  onClose={handleClose}
/>

// ✅ Compound pattern — composible
<Modal onClose={handleClose}>
  <Modal.Header>Confirmar</Modal.Header>
  <Modal.Body>¿Estás seguro?</Modal.Body>
  <Modal.Footer>
    <Button variant="ghost" onClick={handleClose}>Cancelar</Button>
    <Button onClick={handleConfirm}>Confirmar</Button>
  </Modal.Footer>
</Modal>
```

**Resultado:** El componente soporta cualquier variación sin cambiar su API. Nuevas partes (e.g., `Modal.Tabs`) se añaden sin modificar el componente base.

**Lección:** El compound pattern es el más escalable para componentes de design system con múltiples variaciones.

---

### Caso 3: Code Splitting por Ruta en Next.js

**Situación:** Una aplicación de dashboards tiene 15 rutas. El bundle inicial incluye el código de todas las rutas aunque el usuario solo visite 2-3.

```javascript
// Next.js App Router hace code splitting automático por página
// app/dashboard/page.jsx → solo se carga en /dashboard
// app/reports/page.jsx → solo se carga en /reports

// Para componentes pesados dentro de una página:
import dynamic from 'next/dynamic';

const HeavyChart = dynamic(() => import('./HeavyChart'), {
  loading: () => <ChartSkeleton />,
  ssr: false, // Solo en el cliente (útil para librerías que usan window)
});

// El bundle de HeavyChart solo se descarga cuando se renderiza
```

**Resultado:** El bundle inicial se reduce drásticamente. El usuario solo descarga JS de lo que visita.

**Lección:** Code splitting por ruta es automático en Next.js App Router. Para componentes pesados dentro de una ruta, usar `dynamic()` con skeleton como loading state.

---

## Conexión con el Cerebro #4

| Habilidad del Cerebro | Aporte de esta fuente |
|------------------------|----------------------|
| Arquitectura de componentes React | Compound, Provider, Container/Presentational, Custom Hooks patterns |
| Decisiones de rendering | CSR vs SSR vs SSG vs ISR vs Streaming con árbol de decisión y trade-offs |
| Optimización de Core Web Vitals | Proceso medición → identificación → solución → verificación |
| State management | Patrones para elegir dónde vive el estado y cómo evitar re-renders innecesarios |
| Entrega al Cerebro #5 (Backend) | Contratos de API, qué datos se necesitan en qué rendering pattern |

---

## Preguntas que el Cerebro puede responder

1. ¿Qué rendering pattern (SSR, SSG, ISR, CSR) es correcto para esta página y por qué?
2. ¿Cuál patrón de componente (Compound, HOC, Custom Hook) resuelve mejor este problema?
3. ¿Por qué el LCP de esta página es alto y cómo mejorarlo?
4. ¿Dónde debe vivir este estado para evitar re-renders innecesarios?
5. ¿Cómo implemento code splitting en este componente pesado?
6. ¿Por qué hay un race condition en este useEffect y cómo prevenirlo?
7. ¿Cuándo vale la pena memoizar este componente?
