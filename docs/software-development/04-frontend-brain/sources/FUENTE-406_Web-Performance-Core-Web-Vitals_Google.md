---
source_id: "FUENTE-406"
brain: "brain-software-04-frontend-architecture"
niche: "software-development"
title: "Web Performance & Core Web Vitals — Guía Consolidada"
author: "Addy Osmani (Google) + web.dev team + Lighthouse team"
expert_id: "EXP-403"
type: "guide"
language: "en"
year: 2024
isbn: "N/A"
url: "https://web.dev/performance + https://web.dev/vitals"
skills_covered: ["H6", "H7"]
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
      - "Cubre CWV 2024: LCP, INP (reemplaza FID), CLS"
      - "Formato estándar del MasterMind Framework v2"
status: "active"

habilidad_primaria: "Web Performance — Core Web Vitals, Lighthouse, optimización"
habilidad_secundaria: "Métricas de Performance y su impacto en conversión"
capa: 2
capa_nombre: "Frameworks Operativos"
relevancia: "CRÍTICA — Los Core Web Vitals afectan el ranking en Google y directamente la tasa de conversión. Un producto lento pierde usuarios antes de que vean el contenido."
---

# FUENTE-406: Web Performance & Core Web Vitals
## Google Web Platform Team | Guía Consolidada 2024

---

## Tesis Central

> La performance no es un feature — es la base sobre la que todos los demás features se sostienen. Un usuario que abandona por lentitud no ve ningún feature. Los Core Web Vitals son las métricas que Google usa para medir la experiencia real del usuario, y son el lenguaje común entre diseño, frontend y negocio para hablar de calidad percibida.

Regla del 100ms/1s/10s: reacciones por debajo de 100ms se sienten instantáneas. Entre 100ms y 1s, el usuario nota el delay pero tolera. Más de 10s, el usuario abandona.

---

## 1. Principios Fundamentales

> **P1: Core Web Vitals — Las 3 métricas que importan en 2024**
> LCP (Largest Contentful Paint), INP (Interaction to Next Paint), y CLS (Cumulative Layout Shift) son los tres pilares. LCP mide velocidad de carga percibida. INP mide responsividad a interacciones. CLS mide estabilidad visual.
> *Aplicación: estas tres métricas deben estar en el dashboard de monitoreo de todo producto. Mejorarlas mejora directamente SEO y conversión.*

> **P2: La performance percibida importa más que la performance real**
> Un usuario que ve contenido útil en 1.5s con el resto cargando percibe la página como rápida. Un usuario que ve pantalla en blanco 3s aunque el contenido llegue todo junto en 3s percibe lentitud. Progressive rendering y skeleton screens mejoran la percepción sin cambiar el tiempo real.
> *Aplicación: optimizar para "¿cuándo el usuario ve algo útil?" (FCP, LCP) antes que para "¿cuándo termina de cargar todo?".*

> **P3: El JavaScript es el recurso más costoso que existe en la web**
> Un archivo JavaScript de 200KB y una imagen de 200KB cuestan lo mismo en bytes. Pero el JS tiene que parsearse, compilarse, y ejecutarse. La imagen solo se decodifica. En dispositivos de gama media, compilar 200KB de JS puede tomar 1 segundo.
> *Aplicación: antes de añadir una nueva dependencia npm, pregunta su impacto en bundle size con bundlephobia.com.*

> **P4: Las imágenes son el CWV issue más común y más fácil de resolver**
> La mayoría de sites con LCP alto lo tienen porque la imagen hero se carga sin `priority`, en el formato incorrecto (PNG/JPG en lugar de WebP/AVIF), o sin dimensiones explícitas.
> *Aplicación: toda imagen above-the-fold debe tener `priority` (Next.js) o `loading="eager"` + `fetchpriority="high"`. Usar `<Image>` de Next.js que maneja todo esto automáticamente.*

> **P5: CLS se previene reservando espacio antes de que el contenido llegue**
> El Layout Shift ocurre cuando el browser coloca un elemento y luego tiene que moverlo (porque llegó una imagen sin dimensiones, una fuente, o un anuncio). La solución es siempre reservar el espacio antes de que el contenido llegue.
> *Aplicación: todas las imágenes deben tener width/height declarados. Las fuentes deben usar `font-display: swap` + un font fallback con métricas similares.*

---

## 2. Frameworks y Metodologías

### Framework 1: Core Web Vitals — Definición, Objetivos y Causas

**LCP — Largest Contentful Paint (Velocidad de carga percibida)**

| Valor | Clasificación |
|-------|---------------|
| ≤ 2.5s | ✅ Good |
| 2.5s – 4.0s | ⚠️ Needs Improvement |
| > 4.0s | ❌ Poor |

**Elemento LCP típico:** La imagen hero, el background de header, un bloque de texto grande.

**Causas comunes de LCP alto:**
1. Imagen LCP sin `preload` o `priority` — el browser la descubre tarde
2. Imagen LCP en formato PNG/JPG — WebP/AVIF son 30-50% más pequeños
3. Time to First Byte (TTFB) alto — el servidor tarda en responder
4. CSS bloqueante que retrasa el render
5. Render-blocking JavaScript

**Soluciones por causa:**
```html
<!-- 1. Preload de la imagen LCP -->
<link rel="preload" as="image" href="/hero.webp" fetchpriority="high">

<!-- 2. Formato moderno con fallback -->
<picture>
  <source srcset="/hero.avif" type="image/avif">
  <source srcset="/hero.webp" type="image/webp">
  <img src="/hero.jpg" alt="Hero" width="1200" height="600">
</picture>

<!-- Next.js maneja esto automáticamente -->
<Image src="/hero.jpg" priority alt="Hero" width={1200} height={600} />
```

---

**INP — Interaction to Next Paint (Responsividad)**

| Valor | Clasificación |
|-------|---------------|
| ≤ 200ms | ✅ Good |
| 200ms – 500ms | ⚠️ Needs Improvement |
| > 500ms | ❌ Poor |

**Qué mide:** El tiempo desde que el usuario interactúa (click, tap, key press) hasta que el browser pinta la respuesta visual.

**Causas comunes de INP alto:**
1. Event handlers que hacen trabajo pesado en el main thread
2. Re-renders de React muy costosos
3. JavaScript de terceros que bloquea el main thread
4. Long Tasks (tareas > 50ms en el main thread)

**Soluciones:**
```javascript
// 1. Dividir el trabajo pesado con scheduler API
function handleClick() {
  // Trabajo inmediato (respuesta visual rápida)
  setButtonState('loading');

  // Trabajo pesado diferido (no bloquea el paint)
  scheduler.postTask(() => {
    processHeavyData();
  }, { priority: 'background' });
}

// 2. Debounce en inputs de alta frecuencia
const debouncedSearch = useMemo(
  () => debounce(search, 300),
  [search]
);

// 3. useTransition para marcar updates como no urgentes
const [isPending, startTransition] = useTransition();
function handleFilter(value) {
  startTransition(() => {
    setFilteredResults(expensiveFilter(data, value));
  });
}
```

---

**CLS — Cumulative Layout Shift (Estabilidad visual)**

| Valor | Clasificación |
|-------|---------------|
| ≤ 0.1 | ✅ Good |
| 0.1 – 0.25 | ⚠️ Needs Improvement |
| > 0.25 | ❌ Poor |

**Causas comunes de CLS alto:**
1. Imágenes sin dimensiones (browser no reserva espacio)
2. Anuncios o embeds dinámicos sin espacio reservado
3. Fuentes con FOIT/FOUT que cambian el layout al cargar
4. Contenido insertado dinámicamente arriba del fold

**Soluciones:**
```css
/* 1. Aspect-ratio para reservar espacio de imagen */
.hero-image {
  aspect-ratio: 16 / 9;
  width: 100%;
}

/* 2. Font-display para controlar FOUT */
@font-face {
  font-family: 'Inter';
  src: url('/inter.woff2') format('woff2');
  font-display: swap; /* Muestra fallback mientras carga */
}

/* 3. Skeleton screens — reservan el espacio exacto */
.skeleton {
  width: 100%;
  height: 200px; /* Mismo height que el contenido real */
  background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
}
```

---

### Framework 2: El Proceso de Optimización de Performance

```
1. AUDIT — ¿Cuál es el estado actual?
   → Lighthouse en Chrome DevTools (modo Incógnito)
   → WebPageTest (múltiples locaciones, dispositivos reales)
   → Core Web Vitals report en Google Search Console (datos reales de usuarios)
   → Chrome User Experience Report (CrUX) para datos de campo

2. IDENTIFICAR — ¿Cuál es el cuello de botella más impactante?
   → LCP > 2.5s: buscar la imagen LCP y optimizarla primero
   → INP > 200ms: buscar Long Tasks en el Performance panel de DevTools
   → CLS > 0.1: buscar elementos que se mueven en el panel de Rendering

3. HIPÓTESIS — ¿Cuál es la causa raíz?
   → Network Waterfall: ¿qué bloquea qué?
   → Bundle Analyzer: ¿qué módulos pesan más?
   → React Profiler: ¿qué componentes re-renderizan sin necesidad?

4. IMPLEMENTAR — Una sola optimización a la vez
   → Así sabes exactamente cuánto impactó cada cambio

5. MEDIR — ¿Mejoró? ¿Cuánto?
   → Antes vs después en las mismas condiciones (mismo dispositivo, red)

6. DOCUMENTAR — ¿Qué se hizo y por qué?
   → Para el equipo y para no revertir sin querer
```

---

### Framework 3: Presupuesto de Performance (Performance Budget)

**Propósito:** Establecer límites que no se deben sobrepasar, incorporados al CI.

```javascript
// next.config.js — Performance budget
module.exports = {
  experimental: {
    bundlePagesRouterDependencies: true,
  },
};

// lighthouse-ci.json — Límites que fallan el CI
{
  "ci": {
    "assert": {
      "assertions": {
        "categories:performance": ["error", {"minScore": 0.9}],
        "largest-contentful-paint": ["error", {"maxNumericValue": 2500}],
        "cumulative-layout-shift": ["error", {"maxNumericValue": 0.1}],
        "total-blocking-time": ["error", {"maxNumericValue": 300}],
        "interactive": ["error", {"maxNumericValue": 5000}]
      }
    }
  }
}
```

---

## 3. Modelos Mentales

| Modelo | Descripción | Aplicación Práctica |
|--------|-------------|---------------------|
| **Critical Rendering Path** | El browser debe parsear HTML → construir DOM → parsear CSS → construir CSSOM → construir Render Tree → Layout → Paint | Cualquier recurso que bloquee este camino retrasa el primer paint |
| **Presupuesto de 100ms** | Para que una interacción se sienta instantánea, todo el trabajo debe completarse en 100ms | Si un event handler hace más de 100ms de trabajo, debe dividirse |
| **Main Thread como Recurso Único** | Solo hay un main thread. Si está ocupado (JavaScript), no puede responder a inputs del usuario | JS pesado → INP alto. Solución: diferir, dividir, o mover a web worker |
| **Cache como Arma Principal** | El recurso más rápido es el que no se descarga. CDN cache, browser cache, y service workers son los multiplicadores más potentes | La primera visita paga el costo. Las visitas siguientes deben usar cache |
| **PRPL Pattern** | Push critical resources, Render initial route, Pre-cache remaining, Lazy-load routes | El orden en que los recursos se cargan importa tanto como el tamaño |
| **Field Data vs Lab Data** | Lighthouse es "lab" (condiciones controladas). Google Search Console es "field" (usuarios reales). Ambos importan. | Un Lighthouse de 100 no garantiza buena experiencia en campo; el hardware real de los usuarios varía |

---

## 4. Criterios de Decisión

| Situación | Prioriza | Sobre | Por qué |
|-----------|----------|-------|---------|
| Imagen above-the-fold | `priority` / `fetchpriority="high"` | Lazy loading (default) | El lazy loading retrasa la imagen LCP; above-the-fold debe cargar ASAP |
| Bundle grande de terceros | Verificar con bundlephobia + alternativa | Instalar directamente | Una librería de 100KB puede tener alternativas de 5KB |
| Fonts web | `font-display: swap` + subsetting | Cargar todas las variantes | Subsetting reduce el tamaño de fuente 60-80%; swap evita FOIT |
| Muchos componentes en una lista | Virtualización (react-virtual) | Renderizar todos | 10,000 filas en el DOM congela el browser; virtualizar renderiza solo las visibles |
| Animaciones costosas | CSS transforms y opacity | Animaciones de layout properties | transforms y opacity se animan en el compositor (no bloquean main thread) |

---

## 5. Anti-patrones

| Anti-patrón | Por qué es malo | Qué hacer en su lugar |
|-------------|-----------------|----------------------|
| **Imágenes sin dimensiones explícitas** | El browser no puede reservar espacio → CLS cuando la imagen carga | Siempre especificar `width` y `height` o usar `aspect-ratio` en CSS |
| **JavaScript síncrono en el `<head>`** | Bloquea el parsing del HTML completo hasta que se descarga y ejecuta | Usar `defer` o `async` en scripts, o moverlos al final del `<body>` |
| **Cargar todos los recursos al inicio** | Bundle grande → más tiempo de parse/compile → TTI alto | Code splitting, lazy loading, y presupuesto de bundle |
| **No tener Lighthouse en CI** | Los regressions de performance se detectan tarde (en producción) | Lighthouse CI en cada PR; fallar el build si los scores bajan |
| **Optimizar sin medir** | Las micro-optimizaciones sin datos pueden empeorar otras métricas | Siempre medir antes y después. El impacto real puede ser diferente a la intuición |
| **Ignorar el performance en mobile** | 50%+ del tráfico es mobile, con CPU 4-5x más lento que desktop y redes más lentas | Testear siempre con "CPU throttling 4x" y "Slow 3G" en Lighthouse |

---

## 6. Casos y Ejemplos Reales

### Caso 1: Deloitte y el Impacto de CWV en Conversión

**Situación:** Deloitte estudió cómo el performance afecta la conversión en sitios de retail y B2B.

**Resultado:** 0.1s de mejora en el tiempo de carga se correlaciona con un 8% de mejora en conversión en retail y 10% en B2B. El LCP por encima de 4s duplicaba la tasa de abandono vs LCP < 2s.

**Lección:** Performance no es vanidad técnica — es ROI directo. Cada segundo importa.

---

### Caso 2: Next.js Image Component — Optimización Automática

```jsx
// ❌ Sin Next.js Image — requiere optimización manual
<img
  src="/hero.jpg"
  alt="Hero"
  // Sin width/height → CLS
  // Sin WebP → formato subóptimo
  // Sin lazy loading → carga aunque esté below-the-fold
  // Sin priority → la imagen LCP compite con otros recursos
/>

// ✅ Con Next.js Image — todo automático
import Image from 'next/image'

<Image
  src="/hero.jpg"
  alt="Hero"
  width={1200}
  height={600}
  priority // Hace preload de la imagen LCP
  // Automático: WebP/AVIF, lazy loading (excepto priority), tamaños responsivos
/>
```

**Lección:** `next/image` resuelve automáticamente: formato moderno (WebP/AVIF), lazy loading, dimensiones para CLS, srcset responsivo. Es la solución default para imágenes en Next.js.

---

### Caso 3: Splitting Long Tasks para Mejor INP

**Situación:** Un componente de búsqueda filtra 10,000 items en el cliente. Cada keystroke tarda 400ms, bloqueando el main thread → INP de 400ms.

```javascript
// ❌ Long Task — bloquea el main thread 400ms
function handleSearch(query) {
  const results = massiveDataset.filter(item =>
    item.name.includes(query) // 10,000 comparaciones síncronas
  );
  setResults(results);
}

// ✅ Usando useTransition — marca el update como no urgente
function SearchComponent() {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState([]);
  const [isPending, startTransition] = useTransition();

  function handleSearch(newQuery) {
    setQuery(newQuery); // Urgente — actualiza el input inmediatamente

    startTransition(() => {
      // No urgente — React puede interrumpir esto si hay interacción más urgente
      setResults(massiveDataset.filter(item => item.name.includes(newQuery)));
    });
  }

  return (
    <>
      <input onChange={e => handleSearch(e.target.value)} value={query} />
      {isPending ? <Spinner /> : <ResultsList results={results} />}
    </>
  );
}
```

**Lección:** `useTransition` es la herramienta de React 18 para mantener el UI responsive mientras procesa trabajo pesado.

---

## Conexión con el Cerebro #4

| Habilidad del Cerebro | Aporte de esta fuente |
|------------------------|----------------------|
| Core Web Vitals | Definiciones, objetivos, causas y soluciones específicas por métrica |
| Optimización de imágenes | Formatos, priority, dimensiones, Next.js Image component |
| INP y responsividad | useTransition, scheduler API, división de Long Tasks |
| CLS y estabilidad | Dimensiones de imágenes, skeleton screens, font-display |
| Performance budget en CI | Lighthouse CI configuración para bloquear regressions |

---

## Preguntas que el Cerebro puede responder

1. ¿Cuál es el LCP, INP y CLS objetivo y cómo los mido?
2. ¿Por qué la imagen hero tarda tanto en cargar y cómo lo soluciono?
3. ¿Por qué el INP es alto en esta interacción y cómo lo reduzco?
4. ¿Qué causa el CLS en esta página y cómo lo prevengo?
5. ¿Cómo configuro Lighthouse CI para detectar regressions de performance?
6. ¿Cómo reduzco el bundle size de esta ruta?
7. ¿Cuándo usar `useTransition` vs `useDeferredValue`?
