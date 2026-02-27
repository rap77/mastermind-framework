---
source_id: "FUENTE-412"
brain: "brain-software-04-frontend-architecture"
niche: "software-development"
title: "Modern Web APIs: Intersection Observer, Service Workers, Web Workers & PWA"
author: "MDN Web Docs + Google Web.dev Team + Philip Walton"
expert_id: "EXP-412"
type: "documentation"
language: "en"
year: 2024
isbn: "N/A"
url: "https://developer.mozilla.org/en-US/docs/Web/API + https://web.dev/learn/pwa"
skills_covered: ["H1", "H6", "H7", "H11"]
distillation_date: "2026-02-26"
distillation_quality: "complete"
loaded_in_notebook: true
version: "1.0.0"
last_updated: "2026-02-26"
changelog:
  - version: "1.0.0"
    date: "2026-02-26"
    changes:
      - "Ficha creada — gap de Web APIs modernas ausente en versión inicial del Cerebro #4"
status: "active"

habilidad_primaria: "Web APIs Modernas — Intersection Observer, Service Workers, Web Workers, PWA"
habilidad_secundaria: "Performance avanzada y experiencias offline-capable"
capa: 2
capa_nombre: "Frameworks Operativos"
relevancia: "ALTA — Estas APIs son la diferencia entre una web app básica y una experiencia de alta calidad. Lazy loading, offline support, y cálculos en background son impossibles sin ellas."
gap_que_cubre: "Web APIs modernas — YDKJS cubre JS del lenguaje pero no las APIs del browser de 2024"
---

# FUENTE-412: Modern Web APIs — Intersection Observer, Service Workers, Web Workers & PWA

## Tesis Central

> Las Web APIs modernas del browser son superpoderes que la mayoría de developers no usa porque no saben que existen o porque asumen que son complicadas. Intersection Observer reemplaza a los scroll event listeners con 5 líneas de código más eficiente. Service Workers dan offline support con relativa poca configuración. Web Workers desbloquean computación paralela sin bloquear el UI. PWA es la combinación de estas APIs más manifest.json para crear apps que se sienten nativas.

La regla: antes de escribir un scroll handler manual o usar una librería pesada de animación on-scroll, verificar si una Web API nativa resuelve el problema.

---

## 1. Principios Fundamentales

> **P1: APIs Nativas > Librerías para el Caso de Uso Principal**
> Las Web APIs nativas tienen cero overhead de bundle, acceso a primitivas del browser que las librerías no tienen, y soporte nativo de mantenimiento. Antes de instalar una librería de lazy loading, verificar si `IntersectionObserver` + `loading="lazy"` resuelve el caso.
> *Aplica a: lazy loading, infinite scroll, resize detection, form validation.*

> **P2: El Main Thread es Sagrado**
> El main thread del browser es responsable de renders, user interactions, y JavaScript. Cualquier trabajo pesado en el main thread bloquea la UI y hace la aplicación no responsive. Los Web Workers mueven el trabajo pesado a un thread separado.
> *Aplica a: cualquier cálculo que tome más de 16ms (un frame a 60fps).*

> **P3: Progressive Enhancement para PWA**
> Una PWA funciona perfectamente sin sus características avanzadas (offline, push notifications). Las características avanzadas mejoran la experiencia para quienes tienen soporte, sin romperla para quien no lo tiene.
> *Aplica a: Service Workers, Web Push Notifications, instalación de PWA.*

> **P4: Caché con Estrategia, no Caché de Todo**
> Los Service Workers permiten controlar exactamente qué se cachea y cómo. Cachear todo indiscriminadamente produce apps que muestran datos desactualizados. Cada recurso tiene su estrategia óptima.
> *Aplica a: estrategia de caché en Service Workers.*

> **P5: Observar, No Preguntar**
> El patrón de Observer APIs (IntersectionObserver, MutationObserver, ResizeObserver) es más eficiente que el patrón de polling (preguntar periódicamente si algo cambió). El browser notifica cuando hay un cambio; el código no necesita preguntar constantemente.
> *Aplica a: scroll position, resize, DOM mutations, elementos en viewport.*

---

## 2. Frameworks y Metodologías

### Framework 1: Intersection Observer — Lazy Loading y Animaciones on-scroll

**Propósito:** Detectar cuándo un elemento entra o sale del viewport sin scroll event listeners.

**Lazy loading de imágenes:**
```typescript
// Hook reutilizable de Intersection Observer
function useIntersectionObserver(
  ref: RefObject<Element>,
  options: IntersectionObserverInit = {}
) {
  const [isIntersecting, setIsIntersecting] = useState(false);

  useEffect(() => {
    const observer = new IntersectionObserver(
      ([entry]) => setIsIntersecting(entry.isIntersecting),
      { threshold: 0.1, ...options }
    );

    if (ref.current) observer.observe(ref.current);
    return () => observer.disconnect();
  }, [ref, options]);

  return isIntersecting;
}

// Componente de imagen lazy
function LazyImage({ src, alt, ...props }: ImgHTMLAttributes<HTMLImageElement>) {
  const imgRef = useRef<HTMLImageElement>(null);
  const isVisible = useIntersectionObserver(imgRef, { rootMargin: '200px' });
  // rootMargin: empieza a cargar 200px antes de que entre al viewport

  return (
    <img
      ref={imgRef}
      src={isVisible ? src : undefined}
      data-src={src}
      alt={alt}
      {...props}
    />
  );
}
```

**Infinite scroll:**
```typescript
function useInfiniteScroll(onLoadMore: () => void, hasMore: boolean) {
  const loaderRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting && hasMore) {
          onLoadMore();
        }
      },
      { threshold: 0.5 }
    );

    if (loaderRef.current) observer.observe(loaderRef.current);
    return () => observer.disconnect();
  }, [onLoadMore, hasMore]);

  return loaderRef;
}

// Uso
function ProductList() {
  const { data, fetchNextPage, hasNextPage } = useInfiniteQuery(/* ... */);
  const loaderRef = useInfiniteScroll(() => fetchNextPage(), hasNextPage);

  return (
    <div>
      {data?.pages.flatMap(page => page.products).map(p => <ProductCard key={p.id} {...p} />)}
      <div ref={loaderRef}>
        {hasNextPage && <Spinner />}
      </div>
    </div>
  );
}
```

---

### Framework 2: Service Workers & Estrategias de Caché

**Propósito:** Dar soporte offline y acelerar la app con caché inteligente.

**Estrategias de caché por tipo de recurso:**

```javascript
// sw.js (Service Worker)

// ESTRATEGIA 1: Cache First (para assets estáticos)
// Sirve del caché; si no está, fetch y cachear
// Ideal: imágenes, fuentes, archivos CSS/JS con hash en el nombre
async function cacheFirst(request) {
  const cache = await caches.open('static-v1');
  const cached = await cache.match(request);
  if (cached) return cached;

  const response = await fetch(request);
  cache.put(request, response.clone());
  return response;
}

// ESTRATEGIA 2: Network First (para datos de API)
// Intenta fetch; si falla (offline), sirve del caché
// Ideal: APIs que cambian frecuentemente
async function networkFirst(request) {
  const cache = await caches.open('api-v1');
  try {
    const response = await fetch(request);
    cache.put(request, response.clone());
    return response;
  } catch {
    return cache.match(request);
  }
}

// ESTRATEGIA 3: Stale While Revalidate (balance)
// Sirve del caché inmediatamente Y actualiza en background
// Ideal: contenido que puede estar levemente desactualizado
async function staleWhileRevalidate(request) {
  const cache = await caches.open('content-v1');
  const cached = cache.match(request);

  const fetchPromise = fetch(request).then(response => {
    cache.put(request, response.clone());
    return response;
  });

  return (await cached) || fetchPromise;
}
```

**Implementación simplificada con Workbox (en Next.js/Vite):**
```javascript
// vite.config.ts con vite-plugin-pwa
import { VitePWA } from 'vite-plugin-pwa';

VitePWA({
  registerType: 'autoUpdate',
  workbox: {
    runtimeCaching: [
      {
        urlPattern: /^https:\/\/api\.miapp\.com\/.*/,
        handler: 'NetworkFirst',
        options: { cacheName: 'api-cache', expiration: { maxAgeSeconds: 300 } }
      },
      {
        urlPattern: /\.(?:png|jpg|jpeg|svg|gif|webp)$/,
        handler: 'CacheFirst',
        options: { cacheName: 'image-cache', expiration: { maxEntries: 100 } }
      }
    ]
  },
  manifest: {
    name: 'Mi App',
    short_name: 'MiApp',
    theme_color: '#0066CC',
    icons: [
      { src: '/icon-192.png', sizes: '192x192', type: 'image/png' },
      { src: '/icon-512.png', sizes: '512x512', type: 'image/png' },
    ],
  },
})
```

---

### Framework 3: Web Workers — Computación sin Bloquear el UI

**Propósito:** Mover cálculos pesados a un thread separado para mantener la UI responsive.

**Casos de uso típicos:**
- Parsear archivos CSV grandes
- Criptografía (hash de passwords en el cliente)
- Procesamiento de imágenes
- Algoritmos de búsqueda complejos
- Cálculos de datos para gráficas

```typescript
// worker.ts
self.onmessage = (event: MessageEvent) => {
  const { type, data } = event.data;

  if (type === 'PARSE_CSV') {
    const result = parseHugeCsv(data);  // Puede tomar segundos, no bloquea UI
    self.postMessage({ type: 'CSV_PARSED', result });
  }
};

// Uso en el componente React
function CsvUploader() {
  const workerRef = useRef<Worker | null>(null);
  const [result, setResult] = useState(null);

  useEffect(() => {
    // Instanciar el worker
    workerRef.current = new Worker(new URL('./worker.ts', import.meta.url));

    workerRef.current.onmessage = (event) => {
      if (event.data.type === 'CSV_PARSED') {
        setResult(event.data.result);
      }
    };

    return () => workerRef.current?.terminate();
  }, []);

  const handleFile = (file: File) => {
    file.text().then(text => {
      workerRef.current?.postMessage({ type: 'PARSE_CSV', data: text });
    });
  };

  return <input type="file" onChange={e => handleFile(e.target.files![0])} />;
}
```

---

### Framework 4: PWA — Web App Instalable

**Requisitos para una PWA instalable:**
1. `manifest.json` con nombre, íconos (192px + 512px), y theme color
2. Service Worker registrado
3. HTTPS
4. Al menos una estrategia de caché de los assets del shell

**Checklist de PWA:**
```
☐ manifest.json enlazado en <head>
☐ Íconos de 192x192 y 512x512 (PNG)
☐ theme-color meta tag que coincide con el manifest
☐ Service Worker registrado y activo
☐ App funciona offline (al menos muestra algo útil)
☐ Primer load con Lighthouse PWA score ≥ 80
☐ `beforeinstallprompt` event manejado para prompt personalizado de instalación
```

---

## 3. Modelos Mentales

| Modelo | Descripción | Aplicación Práctica |
|--------|-------------|---------------------|
| **Observer Pattern en el Browser** | El browser notifica cambios; el código no pregunta periódicamente | `IntersectionObserver`, `ResizeObserver`, `MutationObserver` reemplazan a polling y scroll listeners |
| **Main Thread vs Worker Thread** | El UI thread hace renders; los worker threads hacen cálculos | Si una función tarda > 50ms, considerarla candidata para Web Worker |
| **Caché como Optimización de Red** | El caché del Service Worker es como un proxy local | Diseñar la estrategia de caché pensando en la frecuencia de cambio de cada tipo de recurso |
| **Offline First** | Diseñar para que la app funcione sin conexión como base, no como excepción | Service Worker debe pre-cachear el shell de la app; los datos pueden ser "best effort" |
| **Progressive Enhancement for APIs** | Verificar soporte antes de usar APIs modernas | `if ('IntersectionObserver' in window)` antes de usarlo. Aunque el soporte es >96% en 2024 |

---

## 4. Criterios de Decisión

| Situación | Prioriza | Sobre | Por qué |
|-----------|----------|-------|---------|
| ¿Lazy loading de imágenes? | `loading="lazy"` nativo | IntersectionObserver custom | El atributo nativo tiene cero JS overhead. IO solo si necesitas control extra |
| ¿Infinite scroll? | IntersectionObserver | `onScroll` event | Los scroll events se disparan cientos de veces por segundo; IO solo cuando el elemento es visible |
| ¿Detectar resize de elemento? | `ResizeObserver` | `window.resize` listener | `window.resize` no detecta cambios de un elemento específico; ResizeObserver sí |
| ¿Computación pesada (> 100ms)? | Web Worker | Main thread | El main thread bloqueado hace la UI no-responsive. Cualquier función > 50ms es candidata |
| ¿App necesita offline support? | Service Worker + Workbox | Sin service worker | Workbox abstrae la complejidad de los service workers manualmente |

---

## 5. Anti-patrones

| Anti-patrón | Por qué es malo | Qué hacer en su lugar |
|-------------|-----------------|----------------------|
| Scroll event listeners para lazy loading | Se disparan cientos de veces por segundo, aunque no haya cambio relevante | `IntersectionObserver` — solo se llama cuando el elemento cruza el threshold |
| Parsear CSV de 50MB en el main thread | Congela la UI completamente durante el parse | Web Worker para cualquier procesamiento de datos grande |
| Service Worker que cachea todo indiscriminadamente | APIs con datos críticos pueden servir datos obsoletos hasta que el caché expira | Estrategia por tipo de recurso: CacheFirst para assets, NetworkFirst para APIs |
| `window.onresize` para detectar cambio de tamaño de un elemento | `window.resize` no se dispara cuando el elemento cambia por flexbox/grid | `ResizeObserver` — detecta cambio de tamaño del elemento específico |
| PWA sin mensaje de instalación personalizado | El browser muestra su propio prompt, que los usuarios tienden a ignorar | Manejar `beforeinstallprompt` para mostrar el prompt en el momento correcto (después de engagement) |
| No limpiar observers al desmontar el componente | Memory leaks — el observer sigue activo aunque el componente no exista | Siempre `observer.disconnect()` o `observer.unobserve(element)` en el cleanup del useEffect |

---

## 6. Casos y Ejemplos Reales

### Caso 1: Twitter/X — Virtualización con IntersectionObserver

- **Situación:** Twitter renderizaba miles de tweets en el DOM simultáneamente, causando scroll lento y alto uso de memoria.
- **Decisión:** Usar IntersectionObserver para detectar qué tweets están en el viewport y virtualizar el resto (mantener solo los visibles en el DOM real).
- **Resultado:** Reducción del 60% en uso de memoria, scroll fluido en feeds largos.
- **Lección:** IntersectionObserver es la base de la virtualización de listas. Las librerías como `react-virtual` lo usan internamente.

### Caso 2: Spotify Web Player — Web Workers para Audio Processing

- **Situación:** El web player de Spotify necesitaba hacer procesamiento de audio (equalizer, normalization) sin interrumpir la UI.
- **Decisión:** Audio processing en Web Workers (y Audio Worklets para procesamiento en tiempo real).
- **Resultado:** El audio se procesa en un thread separado. La UI (botones, slider de volumen) responde instantáneamente aunque el procesamiento de audio esté corriendo.
- **Lección:** Los Web Workers no son solo para computación de datos. Cualquier trabajo que deba ocurrir en paralelo con la UI es candidato.

### Caso 3: Starbucks — PWA que Funciona Offline

- **Situación:** Starbucks necesitaba que su web app funcionara en zonas con mala conectividad (centros comerciales con WiFi lento, usuarios en tránsito).
- **Decisión:** PWA con Service Worker que pre-cachea el menú completo. Los usuarios pueden navegar el menú y personalizar su pedido offline. Al recuperar conexión, el pedido se envía.
- **Resultado:** La PWA tiene el mismo tamaño de bundle que la app nativa de Android (233KB). Las conversiones offline-to-online son significativas.
- **Lección:** PWA no es solo "instalar la app". Es diseñar la experiencia offline primero y la experiencia online como mejora.

---

## Conexión con el Cerebro #4

| Habilidad del Cerebro | Aporte de esta fuente |
|------------------------|----------------------|
| Performance (Core Web Vitals) | IntersectionObserver para lazy loading mejora LCP. Caché de Service Worker mejora TTFB |
| Arquitectura de componentes | Hooks reutilizables de useIntersectionObserver, useResizeObserver |
| Features avanzadas | Offline support, push notifications, instalación como app |
| Computación compleja | Web Workers para no bloquear el UI thread |

---

## Preguntas que el Cerebro puede responder

1. ¿Cómo implemento lazy loading de imágenes sin una librería externa?
2. ¿Cómo hago infinite scroll que no degrade el rendimiento del scroll?
3. ¿Cómo muevo este cálculo pesado de CSV parsing a un Web Worker?
4. ¿Qué estrategia de caché de Service Worker es correcta para esta API?
5. ¿Qué necesita esta app para ser instalable como PWA?
6. ¿Por qué mi Service Worker no está actualizando el caché cuando deplojo una nueva versión?
7. ¿Cómo detecto cuando un elemento específico cambia de tamaño para ajustar el layout?
