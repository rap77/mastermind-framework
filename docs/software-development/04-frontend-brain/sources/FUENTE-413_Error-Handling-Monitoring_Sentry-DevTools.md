---
source_id: "FUENTE-413"
brain: "brain-software-04-frontend-architecture"
niche: "software-development"
title: "Frontend Error Handling, Monitoring & Debugging — Sentry, Error Boundaries & DevTools"
author: "Sentry.io Team + Chrome DevTools Team + Addy Osmani"
expert_id: "EXP-413"
type: "guide"
language: "en"
year: 2024
isbn: "N/A"
url: "https://docs.sentry.io/platforms/javascript/guides/react/ + https://developer.chrome.com/docs/devtools"
skills_covered: ["H1", "H5", "H6", "H12"]
distillation_date: "2026-02-26"
distillation_quality: "complete"
loaded_in_notebook: false
version: "1.0.0"
last_updated: "2026-02-26"
changelog:
  - version: "1.0.0"
    date: "2026-02-26"
    changes:
      - "Ficha creada — gap de error handling y monitoring ausente; las fuentes anteriores cubren testing pero no producción monitoring"
status: "active"

habilidad_primaria: "Error Handling en Producción — Error Boundaries, Sentry, Observabilidad Frontend"
habilidad_secundaria: "Debugging avanzado con Chrome DevTools y análisis de problemas de performance"
capa: 2
capa_nombre: "Frameworks Operativos"
relevancia: "ALTA — El código llega a producción. Los errores de producción sin monitoring son invisibles. Esta fuente cierra el loop entre desarrollo y producción."
gap_que_cubre: "Error handling y monitoring de producción — FUENTE-404 cubre testing pero no monitoring en producción"
---

# FUENTE-413: Frontend Error Handling, Monitoring & Debugging

## Tesis Central

> El código en producción siempre tiene errores que los tests no detectaron. La pregunta no es si habrá errores, sino si te enterarás de ellos antes o después que tus usuarios. Un sistema de monitoring correcto te avisa de un error antes que el primer usuario envíe un ticket de soporte. Un Error Boundary correcto hace que el error rompa solo la parte afectada, no toda la aplicación.

La distinción clave: los tests previenen errores conocidos; el monitoring detecta errores desconocidos en producción.

---

## 1. Principios Fundamentales

> **P1: Fail Gracefully — Un Error No Debe Romper Toda la App**
> Una excepción no capturada en React desmonta el árbol completo de componentes, dejando al usuario con una pantalla en blanco. Los Error Boundaries contienen el daño: solo el árbol del componente que falló se desmonta; el resto de la app sigue funcionando.
> *Aplica a: cualquier feature independiente que pueda fallar sin afectar el resto.*

> **P2: Logging != Monitoring**
> `console.error` es logging local. Monitoring es saber qué errores están ocurriendo en producción, con qué frecuencia, en qué navegadores, y qué código los causa. Sin una herramienta de monitoring (Sentry, Datadog, Bugsnag), los errores de producción son invisibles hasta que un usuario reporta.
> *Aplica a: cualquier aplicación que llegue a usuarios reales.*

> **P3: Contexto en los Errores es Tan Importante como el Error Mismo**
> "TypeError: cannot read property of undefined" sin contexto es inútil. El mismo error con el userId del usuario, el URL donde ocurrió, el estado de la aplicación en ese momento, y el stack trace completo es accionable. Los errores deben capturarse con contexto.
> *Aplica a: configuración de Sentry, custom error logging.*

> **P4: Distinguir Errores de Infraestructura de Errores de Lógica**
> Un error de red (500 del servidor, timeout) es diferente de un error de lógica en el código. La UX correcta es diferente: los errores de red son temporales y vale la pena reintentar; los errores de lógica necesitan mostrar un estado de error permanente.
> *Aplica a: manejo de errores en fetch/TanStack Query.*

> **P5: DevTools son el Debugger, no el Editor**
> Chrome DevTools permiten inspeccionar, modificar, y experimentar en tiempo real sin cambiar el código fuente. Un developer que domina DevTools resuelve bugs de performance y lógica en minutos en lugar de horas.
> *Aplica a: debugging de cualquier bug de producción.*

---

## 2. Frameworks y Metodologías

### Framework 1: Error Boundaries en React — Arquitectura de Contención

**Propósito:** Contener errores para que no rompan toda la aplicación.

```typescript
// ErrorBoundary.tsx — Componente reutilizable
import { Component, ErrorInfo, ReactNode } from 'react';

interface Props {
  children: ReactNode;
  fallback?: ReactNode | ((error: Error) => ReactNode);
  onError?: (error: Error, errorInfo: ErrorInfo) => void;
}

interface State {
  hasError: boolean;
  error: Error | null;
}

class ErrorBoundary extends Component<Props, State> {
  state: State = { hasError: false, error: null };

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    // Reportar a Sentry
    captureException(error, { extra: { errorInfo } });
    // Callback opcional del padre
    this.props.onError?.(error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      const { fallback, children } = this.props;
      if (typeof fallback === 'function') {
        return fallback(this.state.error!);
      }
      return fallback ?? <DefaultErrorFallback />;
    }
    return this.props.children;
  }
}

// Fallback por default
function DefaultErrorFallback() {
  return (
    <div role="alert">
      <h2>Algo salió mal</h2>
      <p>Esta sección no está disponible temporalmente.</p>
      <button onClick={() => window.location.reload()}>Recargar</button>
    </div>
  );
}

// Uso: envolver features independientes
function Dashboard() {
  return (
    <div>
      {/* Si Analytics falla, el Dashboard sigue funcionando */}
      <ErrorBoundary fallback={<div>Analytics no disponible</div>}>
        <AnalyticsWidget />
      </ErrorBoundary>

      {/* Si RecentOrders falla, tiene su propio fallback */}
      <ErrorBoundary fallback={(err) => <ErrorCard error={err} />}>
        <RecentOrders />
      </ErrorBoundary>
    </div>
  );
}
```

**Estrategia de granularidad de Error Boundaries:**
```
App root → ErrorBoundary global (captura errores que escapan todo)
  │
  ├── Layout → NO ErrorBoundary (la nav no debería fallar)
  │
  ├── Feature A → ErrorBoundary por feature
  │   ├── Widget A1 → ErrorBoundary si es suficientemente independiente
  │   └── Widget A2 → Compartir ErrorBoundary con A1 si están relacionados
  │
  └── Feature B → ErrorBoundary por feature
```

---

### Framework 2: Sentry — Monitoring de Producción

**Propósito:** Conocer los errores de producción antes que los usuarios los reporten.

**Setup en React + Next.js:**
```typescript
// sentry.client.config.ts
import * as Sentry from '@sentry/nextjs';

Sentry.init({
  dsn: process.env.NEXT_PUBLIC_SENTRY_DSN,

  environment: process.env.NODE_ENV,

  // Sampling: no capturar el 100% en producción (puede ser costoso)
  tracesSampleRate: 0.1,   // 10% de transacciones
  replaysSessionSampleRate: 0.1,  // Session replay en 10%
  replaysOnErrorSampleRate: 1.0,  // 100% cuando hay error

  // Filtrar errores de terceros que no podemos controlar
  ignoreErrors: [
    'ResizeObserver loop limit exceeded',  // Bug de Chrome, no nuestro
    /chrome-extension:\/\//,               // Errores de extensiones del navegador
    'Network request failed',              // Errores de red transitorios
  ],

  integrations: [
    Sentry.replayIntegration(),
  ],
});
```

**Añadir contexto a los errores:**
```typescript
// Asociar errores con el usuario autenticado
function AuthProvider({ children }) {
  const { user } = useAuth();

  useEffect(() => {
    if (user) {
      Sentry.setUser({
        id: user.id,
        email: user.email,
        // NUNCA incluir: passwords, tokens, datos PII sensibles
      });
    } else {
      Sentry.setUser(null);
    }
  }, [user]);

  return children;
}

// Capturar errores con contexto adicional
function handleCheckoutError(error: Error, cartData: Cart) {
  Sentry.withScope((scope) => {
    scope.setTag('feature', 'checkout');
    scope.setContext('cart', {
      itemCount: cartData.items.length,
      totalAmount: cartData.total,
      // No incluir datos de tarjeta de crédito
    });
    Sentry.captureException(error);
  });
}
```

**Alertas de Sentry — configuración recomendada:**
```
ALERTA CRÍTICA (Slack + PagerDuty):
  - Error rate > 1% en los últimos 15 minutos
  - Nuevo error que no se había visto antes
  - Error en el checkout flow o auth flow

ALERTA MEDIA (Slack):
  - Error rate > 0.1% en los últimos 30 minutos
  - Performance regression: LCP > 4s

ALERTA BAJA (Email diario):
  - Resumen de errores nuevos del día
```

---

### Framework 3: Chrome DevTools — Debugging Toolkit

**Performance Tab — Detectar Jank y Bottlenecks:**
```
1. Abrir DevTools → Performance tab
2. Click "Record" → Realizar la acción lenta → Stop
3. Analizar:
   - Frames rojos = dropped frames (jank)
   - Funciones en "Long Tasks" (> 50ms en el main thread)
   - "Scripting" vs "Rendering" vs "Painting" en el flame chart
   - Layout Thrashing: forced reflows que bloquean el thread
```

**Network Tab — Debugging de Requests:**
```
Columnas importantes a habilitar:
  - Initiator: qué código disparó el request
  - Waterfall: cuándo empieza y termina cada request

Filtros útiles:
  - "Slow" o "From cache": requests lentos o cacheados
  - XHR/Fetch: solo los requests de API
  - Bloquear un request: click derecho → Block request URL

Throttling para testear en condiciones reales:
  - "Slow 3G": simula conexión móvil lenta
  - "Offline": testear el comportamiento sin conexión
```

**Application Tab — Storage y Service Workers:**
```
Storage:
  - LocalStorage, SessionStorage, IndexedDB: ver y editar
  - Cookies: ver, editar, y eliminar (útil para testing de auth)

Service Workers:
  - Ver el SW activo
  - "Update on reload": fuerza actualización del SW en cada reload
  - "Offline": simular estado offline con el SW activo

  Debugging de caché:
  - Cache Storage: ver qué está cacheado por el Service Worker
  - Limpiar caché específico para testear actualizaciones
```

**Memory Tab — Detectar Memory Leaks:**
```
Proceso para detectar memory leak:
1. Take Heap Snapshot (baseline)
2. Realizar la acción sospechosa (abrir/cerrar un modal, navegar y volver)
3. Take Heap Snapshot (después)
4. Comparar: Comparison view → objetos que crecen sin reducirse son el leak

Señales de memory leak:
  - Event listeners que no se limpian en useEffect cleanup
  - Closures que retienen referencias a componentes desmontados
  - Suscripciones a observables que no se cancelan
```

---

## 3. Modelos Mentales

| Modelo | Descripción | Aplicación Práctica |
|--------|-------------|---------------------|
| **Error Containment Zones** | Los errores se propagan hacia arriba en el árbol de componentes hasta encontrar un Error Boundary | Colocar Error Boundaries en los límites de features independientes, no en cada componente |
| **The Three Environments** | Development (debug), Staging (integration), Production (monitoring) tienen necesidades distintas | Sentry solo en staging y producción. Logging verboso solo en development |
| **Error Taxonomy** | No todos los errores son igual de urgentes: infraestructura (transiente), lógica (bug), usuario (input inválido) | La UX de error y la urgencia de fix son distintos según el tipo |
| **Observability Triangle** | Logs + Metrics + Traces = visibilidad completa del sistema | Sentry da traces de errores. Datadog/New Relic para métricas de performance |
| **Reproduce → Isolate → Fix** | El proceso de debugging siempre es el mismo: reproducir consistentemente, aislar la causa raíz, corregir | Los DevTools son la herramienta de "Isolate" — aislar qué línea de código causa el problema |

---

## 4. Criterios de Decisión

| Situación | Prioriza | Sobre | Por qué |
|-----------|----------|-------|---------|
| ¿Granularidad del Error Boundary? | Un Error Boundary por feature independiente | Un Error Boundary global o uno por componente | Global = toda la app rompe. Por componente = overhead excesivo |
| ¿Error de red en TanStack Query? | Retry automático + mensaje de "reintentando" | Mostrar error inmediatamente | Los errores de red son transitorios; el usuario no debería ver el error si reintentando funciona |
| ¿Qué incluir en el contexto de Sentry? | User ID, feature, estado de la app | Datos PII (email, nombre) o datos financieros | Sentry es un tercero; minimizar PII por privacidad y regulación |
| ¿Cuándo hacer alert crítica vs logging? | Alert cuando el error afecta a múltiples usuarios o al flujo principal | Solo logging cuando es error aislado de bajo impacto | Los alertas que se ignoran son inútiles; calibrar el umbral correctamente |
| ¿Reintentar automáticamente o mostrar error? | Reintentar con backoff para errores de red | Reintentar para errores de lógica (4xx) | Los errores 4xx no se van a resolver solos. Reintentar los empeora |

---

## 5. Anti-patrones

| Anti-patrón | Por qué es malo | Qué hacer en su lugar |
|-------------|-----------------|----------------------|
| Sin Error Boundaries en producción | Un error en cualquier componente desmonta toda la app. El usuario ve pantalla en blanco | Error Boundaries alrededor de cada feature independiente |
| `console.error` como único sistema de monitoring | Los logs del cliente son invisibles para el equipo de desarrollo | Sentry (o equivalente) con alertas configuradas |
| `try/catch` que silencia el error | `catch(e) {}` (vacío) hace que el error sea invisible | Si no se puede manejar el error, al menos logear en Sentry |
| Error Boundary demasiado granular | Cada componente con su propio ErrorBoundary = overhead de re-renders | Un Error Boundary por feature, no por componente |
| Incluir PII en errores de Sentry | Emails, nombres, y datos sensibles quedan en un tercero | Solo IDs anónimos y contexto de estado de la app, no datos del usuario |
| Debuggear con `console.log` en producción | Los logs quedan visibles a usuarios y llenan el storage de logs | DevTools Breakpoints durante desarrollo. Sentry en producción. Limpiar `console.log` antes de merge |

---

## 6. Casos y Ejemplos Reales

### Caso 1: Notion — Error Boundary que Salvó la App

- **Situación:** Notion tenía un bug en su feature de base de datos que causaba un error de renderizado para algunos usuarios con propiedades específicas.
- **Sin Error Boundary:** El error habría desmontado toda la aplicación, dejando al usuario sin acceso a sus notas.
- **Con Error Boundary:** Solo el bloque de base de datos afectado mostraba el error. El usuario podía seguir usando el resto de la app y reportar el problema.
- **Lección:** Los Error Boundaries no solo son buenas prácticas; son la diferencia entre "el feature X está roto" y "toda la app está caída".

### Caso 2: Airbnb — Sentry para Detectar Bugs de Browser Específico

- **Situación:** Una feature de mapa funcionaba en 99% de los browsers pero lanzaba un error en Safari iOS 15. No se detectó en testing porque el equipo no tenía ese entorno.
- **Con Sentry:** El error apareció en el dashboard 2 horas después del deploy con el browser y OS en el contexto. El equipo lo vio antes que cualquier reporte de usuario.
- **Resultado:** Fix desplegado en 4 horas. Solo 0.3% de los usuarios lo vieron.
- **Lección:** El monitoring de producción detecta bugs que el testing no puede: combinaciones específicas de browser/OS/red que son imposibles de anticipar.

### Caso 3: Debugging de Memory Leak con Chrome DevTools

- **Situación:** Una SPA tenía memory leak: después de navegar por 30 minutos, el uso de memoria subía a 2GB y el tab se crashes.
- **Proceso de debugging:**
  1. Memory tab → Heap Snapshot inicial
  2. Navegar por la app durante 5 minutos
  3. Heap Snapshot → Comparación → Objetos que crecen: `EventListener` y `AbortController`
  4. Búsqueda en el código: un `useEffect` que añadía event listeners pero no los limpiaba en el cleanup
- **Fix:**
  ```typescript
  useEffect(() => {
    const controller = new AbortController();
    window.addEventListener('resize', handler, { signal: controller.signal });
    return () => controller.abort();  // Cleanup que faltaba
  }, []);
  ```
- **Lección:** Los memory leaks en React casi siempre son event listeners o suscripciones que no se limpian en el cleanup del useEffect.

---

## Conexión con el Cerebro #4

| Habilidad del Cerebro | Aporte de esta fuente |
|------------------------|----------------------|
| Producción estable | Error Boundaries + Sentry = errores visibles y contenidos |
| Testing + Monitoring | Los tests previenen errores conocidos; Sentry detecta los desconocidos |
| Performance | Chrome DevTools para debugging de performance y memory leaks |
| Handoff con QA | Sentry como fuente de verdad de errores en staging y producción |

---

## Preguntas que el Cerebro puede responder

1. ¿Cómo implemento un Error Boundary que no rompa toda la app cuando falla este componente?
2. ¿Cómo configuro Sentry para que los errores tengan suficiente contexto para debuggear?
3. ¿Cómo uso Chrome DevTools para encontrar qué función está bloqueando el main thread?
4. ¿Cómo detecto si hay un memory leak en esta SPA?
5. ¿Qué errores de producción deben generar alertas inmediatas vs solo logging?
6. ¿Por qué este error de TanStack Query debería reintentarse vs mostrarse como error permanente?
7. ¿Qué información NO debo incluir en Sentry por razones de privacidad?
