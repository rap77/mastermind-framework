---
source_id: "FUENTE-414"
brain: "brain-software-04-frontend-architecture"
niche: "software-development"
title: "Animation in Code: Framer Motion, CSS Transitions & Web Animations API"
author: "Matt Perry (Framer Motion) + Jake Archibald (Google) + CSS Working Group"
expert_id: "EXP-414"
type: "documentation"
language: "en"
year: 2024
isbn: "N/A"
url: "https://www.framer.com/motion/ + https://web.dev/animations-guide + https://developer.mozilla.org/en-US/docs/Web/API/Web_Animations_API"
skills_covered: ["H2", "H3", "H6", "H13"]
distillation_date: "2026-02-26"
distillation_quality: "complete"
loaded_in_notebook: false
version: "1.0.0"
last_updated: "2026-02-26"
changelog:
  - version: "1.0.0"
    date: "2026-02-26"
    changes:
      - "Ficha creada — gap de implementación de animaciones; FUENTE-310 del Cerebro #3 diseña animaciones, esta fuente las implementa"
status: "active"

habilidad_primaria: "Implementación de Animaciones — CSS, Framer Motion, Web Animations API"
habilidad_secundaria: "Performance de Animaciones y Reducción de Movimiento Accesible"
capa: 2
capa_nombre: "Frameworks Operativos"
relevancia: "MEDIA-ALTA — El Cerebro #3 especifica animaciones (FUENTE-310). El Cerebro #4 las implementa. Sin esta fuente, el handoff de motion design queda incompleto."
gap_que_cubre: "Implementación de animaciones — el diseño existe en el Cerebro #3 pero no la implementación en el #4"
---

# FUENTE-414: Animation in Code — Framer Motion, CSS Transitions & Web Animations API

## Tesis Central

> La animación mal implementada destruye el performance del producto. La animación bien implementada es invisible para el CPU y GPU. La diferencia es simple: solo `opacity` y `transform` se pueden animar sin causar reflows del layout. Todo lo demás (width, height, top, left, background-color) causa repaints costosos. Esta regla de oro, correctamente aplicada, es la diferencia entre 60fps y jank.

La jerarquía correcta: CSS Transitions/Animations (más rápido) → Framer Motion (más expresivo) → Web Animations API (control programático).

---

## 1. Principios Fundamentales

> **P1: Solo Animar opacity y transform — El Resto Causa Reflows**
> El browser tiene un pipeline: JavaScript → Style → Layout → Paint → Composite. Las animaciones de `opacity` y `transform` solo tocan el paso "Composite" (el más rápido). Animar `width`, `height`, `top`, `margin`, o `background-color` obliga al browser a recalcular Layout, lo cual es costoso y causa jank.
> *Aplica a: toda animación que deba correr a 60fps.*

> **P2: GPU Acceleration con will-change — Con Precaución**
> `will-change: transform` le indica al browser que promueva el elemento a su propia capa GPU, acelerando la animación. Pero cada capa GPU consume memoria. Usar solo en elementos que realmente van a animarse, y remover el `will-change` cuando la animación termina.
> *Aplica a: elementos que se animan frecuentemente (carruseles, drawers, modals).*

> **P3: prefers-reduced-motion es Obligatorio**
> El 35% de los usuarios con epilepsia fotosensible o con vestibular disorders pueden sufrir malestar físico por animaciones de movimiento. Siempre implementar la versión reducida de cualquier animación.
> *Aplica a: toda animación que involucre movimiento de elementos por la pantalla.*

> **P4: Composición > Secuencia Manual**
> Manejar animaciones con `setTimeout` encadenados es frágil y difícil de mantener. Las herramientas de animación (Framer Motion, GSAP) tienen orchestration primitives que hacen que las secuencias sean declarativas y sincronizadas.
> *Aplica a: animaciones de entrada, stagger animations, shared element transitions.*

> **P5: La Especificación del Cerebro #3 es la Fuente de Verdad**
> El Cerebro #3 (FUENTE-310) especifica: duración, easing, propiedades animadas, y comportamiento de reduced-motion. El Cerebro #4 implementa exactamente eso — no inventa animaciones adicionales ni ignora las especificadas.
> *Aplica a: handoff de diseño a implementación.*

---

## 2. Frameworks y Metodologías

### Framework 1: CSS Transitions y Animations — Para Casos Simples

**Propósito:** Animar estados simples sin JavaScript.

**Cuándo usar CSS puro:**
- Hover states, focus states
- Transiciones entre 2 estados bien definidos (visible/oculto, abierto/cerrado)
- Animaciones en loop (spinners, pulses)

```css
/* Transición de hover — siempre en el elemento base, no en :hover */
.button {
  background-color: var(--color-primary);
  transform: translateY(0);

  /* Transición aquí, no en .button:hover */
  transition:
    background-color 150ms ease-out,
    transform 100ms ease-in;
}

.button:hover {
  background-color: var(--color-primary-dark);
  transform: translateY(-2px);
}

.button:active {
  transform: translateY(0) scale(0.98);
  transition-duration: 100ms;
}

/* Animación de entrada para skeleton */
@keyframes pulse {
  0%, 100% { opacity: 0.6; }
  50% { opacity: 1; }
}

.skeleton {
  animation: pulse 1.5s ease-in-out infinite;
}

/* SIEMPRE incluir reduced-motion */
@media (prefers-reduced-motion: reduce) {
  .button { transition: none; }
  .skeleton { animation: none; opacity: 0.8; }
}
```

---

### Framework 2: Framer Motion en React — Para Animaciones Declarativas

**Propósito:** Animaciones complejas, stagger, exit animations, y shared element transitions.

**Instalación y setup:**
```bash
npm install framer-motion
```

**Patrones fundamentales:**

```typescript
import { motion, AnimatePresence } from 'framer-motion';
import { useReducedMotion } from 'framer-motion';

// 1. ANIMACIÓN DE ENTRADA
function Card({ children }) {
  const prefersReducedMotion = useReducedMotion();

  return (
    <motion.div
      initial={{ opacity: 0, y: prefersReducedMotion ? 0 : 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.25, ease: 'easeOut' }}
    >
      {children}
    </motion.div>
  );
}

// 2. ANIMACIÓN DE SALIDA (exit) — Requiere AnimatePresence
function Notification({ isVisible, message }) {
  return (
    <AnimatePresence>
      {isVisible && (
        <motion.div
          key="notification"
          initial={{ opacity: 0, x: 50 }}
          animate={{ opacity: 1, x: 0 }}
          exit={{ opacity: 0, x: 50 }}
          transition={{ duration: 0.2, ease: 'easeOut' }}
        >
          {message}
        </motion.div>
      )}
    </AnimatePresence>
  );
}

// 3. STAGGER — Lista con items que aparecen en secuencia
const containerVariants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: 0.06,  // 60ms entre cada hijo
    },
  },
};

const itemVariants = {
  hidden: { opacity: 0, y: 20 },
  visible: { opacity: 1, y: 0 },
};

function ProductList({ products }) {
  return (
    <motion.ul
      variants={containerVariants}
      initial="hidden"
      animate="visible"
    >
      {products.map(product => (
        <motion.li key={product.id} variants={itemVariants}>
          <ProductCard {...product} />
        </motion.li>
      ))}
    </motion.ul>
  );
}

// 4. LAYOUT ANIMATION — Transición suave cuando el layout cambia
function ExpandableCard({ title, details }) {
  const [isExpanded, setIsExpanded] = useState(false);

  return (
    <motion.div layout>  {/* layout prop = anima cambios de tamaño automáticamente */}
      <h3>{title}</h3>
      {isExpanded && (
        <motion.p
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
        >
          {details}
        </motion.p>
      )}
      <button onClick={() => setIsExpanded(!isExpanded)}>
        {isExpanded ? 'Menos' : 'Más'}
      </button>
    </motion.div>
  );
}

// 5. SHARED ELEMENT TRANSITION (con layoutId)
function ProductList() {
  const [selected, setSelected] = useState(null);

  return (
    <div>
      {products.map(product => (
        <motion.div
          key={product.id}
          layoutId={`product-${product.id}`}  // Misma layoutId = framer anima la transición
          onClick={() => setSelected(product)}
        >
          <img src={product.thumbnail} />
        </motion.div>
      ))}

      <AnimatePresence>
        {selected && (
          <motion.div layoutId={`product-${selected.id}`}>
            <img src={selected.fullImage} />
            <button onClick={() => setSelected(null)}>Cerrar</button>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
```

---

### Framework 3: Traducir la Especificación del Cerebro #3 a Código

**Propósito:** Convertir la especificación técnica de FUENTE-310 en código correcto.

**Mapa de easings (spec → código):**
```typescript
const easings = {
  // Spec del Cerebro #3 → valor en código
  'ease-out':     [0.0, 0.0, 0.2, 1.0],    // Para entradas
  'ease-in':      [0.4, 0.0, 1.0, 1.0],    // Para salidas
  'ease-in-out':  [0.4, 0.0, 0.2, 1.0],    // Para movimientos en pantalla
  'spring':       { type: 'spring', stiffness: 300, damping: 30 },  // Para modals, drawers
};

// Uso en Framer Motion
<motion.div
  animate={{ y: 0 }}
  transition={{ ease: easings['ease-out'], duration: 0.25 }}
/>

// Uso en CSS
.modal { transition: transform 250ms cubic-bezier(0.0, 0.0, 0.2, 1); }
```

**Traducción de la especificación de FUENTE-310:**
```typescript
// Spec: "Modal: fade-in + scale de 0.95 a 1.0, 250ms ease-out"
const modalVariants = {
  hidden: { opacity: 0, scale: 0.95 },
  visible: {
    opacity: 1,
    scale: 1,
    transition: { duration: 0.25, ease: [0.0, 0.0, 0.2, 1] }
  },
  exit: {
    opacity: 0,
    scale: 0.95,
    transition: { duration: 0.2, ease: [0.4, 0.0, 1.0, 1.0] }
  },
};

// Spec: "Notificación: slide + fade desde arriba, 300ms ease-out"
const notificationVariants = {
  hidden: { opacity: 0, y: -20 },
  visible: { opacity: 1, y: 0, transition: { duration: 0.3, ease: [0.0, 0.0, 0.2, 1] } },
  exit: { opacity: 0, y: -20, transition: { duration: 0.2 } },
};

// Spec: "Lista con stagger 60ms entre items"
const listVariants = {
  visible: { transition: { staggerChildren: 0.06 } },
};
```

---

## 3. Modelos Mentales

| Modelo | Descripción | Aplicación Práctica |
|--------|-------------|---------------------|
| **Compositor vs Painter** | `opacity` y `transform` van al GPU compositor. Todo lo demás pasa por Paint | Antes de animar cualquier propiedad, verificar si puede ser reemplazada por opacity/transform |
| **Declarative Animation** | Describir el estado final, no los pasos intermedios | `animate={{ x: 100 }}` en lugar de `setInterval` con incrementos manuales |
| **AnimatePresence como Guardia** | Framer Motion no puede animar exit de componentes que ya no están en el DOM | Siempre envolver con `AnimatePresence` cuando se use la prop `exit` |
| **layoutId = Portal de Transición** | Dos elementos con el mismo `layoutId` en distintas posiciones del árbol comparten la animación de transición | Usar para hero animations y shared element transitions entre lista y detalle |
| **Reduced Motion as Default for Complex Animations** | Si hay dudas sobre si la animación puede causar malestar, la versión reducida es el default | Usar `useReducedMotion()` hook de Framer Motion para leer la preferencia del usuario |

---

## 4. Criterios de Decisión

| Situación | Prioriza | Sobre | Por qué |
|-----------|----------|-------|---------|
| ¿CSS Transition o Framer Motion? | CSS Transition | Framer Motion | CSS tiene cero overhead de JS. Solo usar Framer Motion cuando CSS no alcanza (exit animations, stagger, layout animations) |
| ¿Animar width/height o transform? | `transform: scaleX()` / `scaleY()` | `width` / `height` | scale evita reflows; cambiar width/height recalcula el layout |
| ¿Framer Motion o GSAP? | Framer Motion en proyectos React | GSAP | Framer Motion está integrado con el modelo de React (componentes, estado). GSAP para casos avanzados o vanilla JS |
| ¿layout prop o CSS transition? | `layout` prop de Framer Motion | CSS transition de height/width | La prop `layout` usa transform internamente (60fps). CSS height transition causa reflows |
| ¿Cuándo NO animar? | Nunca | Cuando la spec del Cerebro #3 no especifica animación | Si el diseño no lo especificó, no inventar animaciones — añaden peso sin diseño |

---

## 5. Anti-patrones

| Anti-patrón | Por qué es malo | Qué hacer en su lugar |
|-------------|-----------------|----------------------|
| Animar `width`, `height`, `top`, `left` | Causa reflows del layout → jank → drop de frames | `transform: translate()`, `transform: scale()`, `opacity` |
| Animaciones sin `prefers-reduced-motion` | Puede causar malestar físico a usuarios sensibles | `@media (prefers-reduced-motion: reduce)` en CSS o `useReducedMotion()` en Framer Motion |
| `exit` animation sin `AnimatePresence` | Framer Motion no puede animar un componente que ya fue removido del DOM | Envolver con `<AnimatePresence>` el padre del componente con `exit` |
| `will-change: transform` en todos los elementos | Cada elemento promovido a GPU layer consume memoria → puede empeorar performance en dispositivos con poca RAM | Solo en elementos que se animan frecuentemente; remover después de la animación |
| `setTimeout` encadenados para secuencias | Frágil, difícil de mantener, se desincroniza si cambia la duración | `staggerChildren` de Framer Motion o `sequence()` de la Web Animations API |
| Inventar animaciones que el Cerebro #3 no especificó | Introduce inconsistencia en el sistema de diseño | Si la animación no está en la spec, preguntar al Cerebro #3 antes de implementar |

---

## 6. Casos y Ejemplos Reales

### Caso 1: Linear — Shared Element Transitions como Signature Feature

- **Situación:** Linear necesitaba una transición fluida entre la vista de lista de issues y el detalle de un issue.
- **Implementación:** Shared element transition con Framer Motion (`layoutId`). El card de la lista se expande directamente hasta convertirse en la vista de detalle.
- **Resultado:** La transición se convirtió en un elemento de identidad de Linear — los usuarios la mencionan como parte de por qué la app "se siente premium".
- **Lección:** Las shared element transitions son el tipo de animación con mayor impacto percibido de calidad. Valen el esfuerzo de implementación.

### Caso 2: Stripe — Animaciones de Formulario que Reducen Errores

- **Situación:** El formulario de pago de Stripe necesitaba feedback visual inmediato al tipear.
- **Implementación:** Micro-animaciones de 150ms en los campos: el label flota hacia arriba al hacer focus (CSS transition de `transform` para evitar reflows), el campo hace un shake de 300ms cuando hay error de validación.
- **Resultado:** La tasa de abandono de formulario bajó significativamente. El feedback visual inmediato reduce la frustración del usuario.
- **Lección:** Las micro-animaciones de formulario tienen ROI directo en conversión. Son el caso de uso más ROI-positivo de animaciones en productos de negocio.

### Caso 3: La Migración de CSS a Framer Motion en el Lugar Correcto

- **Situación:** Un equipo usaba Framer Motion para TODAS las animaciones, incluyendo simples hover states de botones.
- **Problema:** El bundle aumentó 50KB por Framer Motion. Los hover states con Framer Motion tenían una latencia perceptible vs CSS puro.
- **Solución:** CSS Transitions para hover, focus, y active states (zero JS). Framer Motion solo para: entrada/salida de componentes, stagger de listas, layout animations, y shared element transitions.
- **Resultado:** Bundle reducido en 35KB (Framer Motion tree-shaken). Hover states instantáneos.
- **Lección:** Framer Motion no es la solución para todas las animaciones. Es la solución para las animaciones que CSS no puede hacer elegantemente.

---

## Conexión con el Cerebro #4

| Habilidad del Cerebro | Aporte de esta fuente |
|------------------------|----------------------|
| Implementar specs del Cerebro #3 | Mapa directo de especificación → código (easing, duración, propiedades) |
| Performance de animaciones | Solo opacity/transform → 60fps garantizado |
| Accesibilidad de animaciones | `prefers-reduced-motion` en CSS y `useReducedMotion()` en Framer Motion |
| Arquitectura de componentes React | Variants, AnimatePresence, layoutId como patterns reutilizables |

---

## Preguntas que el Cerebro puede responder

1. ¿Por qué esta animación de `width` está causando jank y cómo la reemplazo?
2. ¿Cuándo usar CSS Transitions vs Framer Motion?
3. ¿Cómo implemento la animación de salida de este modal con Framer Motion?
4. ¿Cómo convierto esta especificación de FUENTE-310 (`300ms ease-out`) en código?
5. ¿Cómo implemento `prefers-reduced-motion` en esta animación de Framer Motion?
6. ¿Cómo hago una shared element transition entre este list item y su página de detalle?
7. ¿Por qué `will-change: transform` en todos los elementos está empeorando el performance?
