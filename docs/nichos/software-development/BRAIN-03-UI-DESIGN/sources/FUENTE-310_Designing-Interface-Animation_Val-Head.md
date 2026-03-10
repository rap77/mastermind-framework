---
source_id: "FUENTE-310"
brain: "brain-software-03-ui-design"
niche: "software-development"
title: "Designing Interface Animation: Meaningful Motion for UX"
author: "Val Head"
expert_id: "EXP-310"
type: "book"
language: "en"
year: 2016
isbn: "978-1-933820-32-0"
url: "https://rosenfeldmedia.com/books/designing-interface-animation/"
skills_covered: ["H3", "H5"]
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
      - "Formato adaptado a estándar del MasterMind Framework"
      - "Cubre gap de Motion Design identificado en v1.0"
status: "active"

# Metadatos específicos del Cerebro #3
habilidad_primaria: "Motion Design & Animaciones de Interfaz"
habilidad_secundaria: "Micro-interacciones con Propósito & Feedback Visual"
capa: 2
capa_nombre: "Frameworks Operativos — Motion Design"
relevancia: "ALTA — Las animaciones sin criterio son ruido visual; con criterio son comunicación"
---

# FUENTE-310 — Designing Interface Animation
## Val Head | Motion Design con Propósito para UX

---

## Tesis Central

> La animación en interfaces no es decoración. Es comunicación. Cada movimiento debe tener una razón funcional: orientar, informar, dar feedback, o crear continuidad. La animación sin propósito es ruido que distrae y fatiga al usuario.

La pregunta correcta no es "¿cómo animo esto?" sino "¿**qué** necesita comunicar este movimiento al usuario?". El propósito define el tipo, duración, y easing de la animación.

---

## Principios Fundamentales

### Principio 1 — Animación con Propósito (Las 4 Funciones)

Toda animación de interfaz tiene al menos una de estas funciones:

| Función | Qué comunica | Ejemplo |
|---------|--------------|---------|
| **Orientación** | Dónde está el usuario en el espacio | Slide de pantalla que indica navegación hacia la derecha |
| **Feedback** | Que la acción fue recibida | Botón que comprime al hacer tap |
| **Continuidad** | Que el elemento persiste (no desaparece y reaparece) | Shared element transition entre lista y detalle |
| **Narrativa** | La relación causal entre elementos | Datos que se acumulan en una gráfica mostrando el proceso |

**Regla del Cerebro #3:** Si una animación propuesta no cumple ninguna de estas funciones, no debe existir.

### Principio 2 — Duración: Ni Demasiado Rápido ni Demasiado Lento

| Tipo de animación | Duración recomendada |
|-------------------|---------------------|
| Micro-interacciones (feedback inmediato) | 100–300ms |
| Transiciones de elemento en página | 200–500ms |
| Transiciones de pantalla completa | 300–600ms |
| Animaciones de carga / datos | 600ms–1.2s |
| Animaciones decorativas / ilustrativas | 800ms–3s |

**Regla de oro:** Si el usuario puede percibir que está esperando la animación, es demasiado lenta.

### Principio 3 — Easing: el Lenguaje del Movimiento

El easing define la personalidad del movimiento. No todas las animaciones deben ser lineales.

```
LINEAR      → Robótico, mecánico. Raramente correcto para UI.
EASE-IN     → Empieza lento, termina rápido. Para elementos que salen de pantalla.
EASE-OUT    → Empieza rápido, termina lento. Para elementos que entran a pantalla.
EASE-IN-OUT → Aceleración y desaceleración. Para movimientos en pantalla.
SPRING      → Rebote natural. Para elementos que "aterrizan" (drawers, modals).
```

**Metáfora del mundo físico:** Los objetos reales no se mueven a velocidad constante. Un cajón al abrirse acelera y luego frena. Las interfaces que imitan la física del mundo real se sienten naturales.

### Principio 4 — Jerarquía en el Tiempo

Cuando varios elementos se animan, deben hacerlo en secuencia lógica, no todos a la vez.

```
STAGGER (escalonado): cada elemento empieza 50-80ms después del anterior
→ Guía el ojo del usuario en el orden correcto
→ Evita el "Big Bang": todo aparece de golpe

Ejemplo:
Header       → 0ms
Primera card → 60ms
Segunda card → 120ms
Tercera card → 180ms
```

**Regla:** Máximo 3-4 elementos en stagger. Si hay más, agrupar.

### Principio 5 — Accesibilidad del Movimiento

El movimiento puede causar malestar físico a usuarios con vértigo o sensibilidad al movimiento.

```css
@media (prefers-reduced-motion: reduce) {
  /* Reducir o eliminar animaciones para usuarios que lo solicitan */
}
```

**Reglas de diseño:**
- Nunca usar animaciones de parallax grandes sin versión reducida
- Las animaciones de más de 5 segundos en loop deben poder pausarse
- Las animaciones que cubren más del 25% de la pantalla son de alto riesgo
- Siempre especificar en el handoff qué hacer con `prefers-reduced-motion`

---

## Framework Principal — Motion Design Decision Tree

```
¿Necesito animar algo?
│
├── ¿Qué función cumple?
│   ├── Orientación → Transición de pantalla / spatial navigation
│   ├── Feedback → Micro-interacción del componente
│   ├── Continuidad → Shared element / morph transition
│   └── Narrativa → Datos / onboarding / ilustración
│
├── ¿Cuánto tiempo debe durar?
│   ├── Micro-interacción → 100-300ms
│   ├── Transición en-pantalla → 200-500ms
│   └── Transición de pantalla completa → 300-600ms
│
├── ¿Qué easing corresponde?
│   ├── Elemento entra a pantalla → ease-out
│   ├── Elemento sale de pantalla → ease-in
│   ├── Elemento se mueve en pantalla → ease-in-out
│   └── Elemento "aterriza" (drawer, modal) → spring
│
├── ¿Hay varios elementos?
│   └── SÍ → Aplicar stagger (50-80ms entre cada uno)
│
└── ¿El usuario puede tener sensibilidad al movimiento?
    └── SÍ → Diseñar versión con prefers-reduced-motion
```

---

## Catálogo de Animaciones por Componente

### Botones y Elementos Interactivos
```
HOVER:   Scale 1.02 + background transition (150ms ease-out)
ACTIVE:  Scale 0.98 (sensación de presión) (100ms ease-in)
LOADING: Spinner dentro del botón o pulse del fondo (loop infinito)
SUCCESS: Check mark con scale-in (300ms spring)
ERROR:   Shake horizontal (400ms, 3-4 oscilaciones)
```

### Modals y Sheets
```
ENTRADA:  Fade-in + scale de 0.95 a 1.0 (250ms ease-out)
SALIDA:   Fade-out + scale de 1.0 a 0.95 (200ms ease-in)
FONDO:    Fade-in de overlay (200ms ease-out)
SHEET:    Slide desde abajo (300ms spring)
DRAWER:   Slide desde el lado (300ms ease-out)
```

### Navegación entre Pantallas
```
PUSH (ir más profundo):    Nueva pantalla slide desde la derecha
POP (volver):              Pantalla actual slide hacia la derecha
MODAL:                     Nueva pantalla fade-in desde abajo
TAB:                       Cross-fade (sin dirección espacial)
```

### Estados de Carga
```
SKELETON: Pulse de opacidad 0.6→1.0 en loop (1.2s ease-in-out)
SPINNER:  Rotate 360° en loop (800ms linear)
PROGRESS: Width transition del 0% al 100% (duración = duración real)
DOTS:     Scale bounce en stagger de 3 puntos (400ms loop)
```

### Notificaciones y Toasts
```
ENTRADA:  Slide + fade desde arriba/abajo (300ms ease-out)
SALIDA:   Fade-out (200ms ease-in), o slide hacia afuera
AUTO-DISMISS: No animar la cuenta regresiva; el dismiss sí
```

### Listas y Cards
```
APARICIÓN INICIAL:  Stagger fade-in + translate-y de 20px (60ms entre items)
ELIMINACIÓN:        Height → 0 + opacity → 0 (300ms ease-in)
REORDENAMIENTO:     Translate-y a nueva posición (300ms ease-in-out)
```

---

## Modelos Mentales

### "Animación como Capa de Comunicación"

El diseño visual comunica jerarquía y significado en el espacio (qué es más importante, qué está relacionado). La animación comunica jerarquía y significado en el tiempo (qué viene primero, qué causa qué).

Un buen diseño de animación responde: ¿Qué quiero que el usuario entienda a través del movimiento?

### "El Test de la Abuela"

Si una persona mayor (no tech-savvy) ve la animación y entiende intuitivamente qué pasó, la animación está bien diseñada. Si la animación es "cool" pero confusa, está mal diseñada.

### "Cada Milisegundo Cuenta"

En micro-interacciones (100-300ms), el usuario no "ve" la animación conscientemente, pero la siente. Una animación de 200ms que tiene easing correcto se siente "natural". La misma sin easing se siente "robótica". El usuario no sabe por qué, pero nota la diferencia.

---

## Criterios de Decisión

### ¿Animar o no animar?

**SÍ animar cuando:**
- Un elemento aparece de la nada (necesita contexto de dónde viene)
- Una acción del usuario produce un cambio en pantalla (necesita feedback)
- Hay navegación entre pantallas (necesita continuidad espacial)
- Los datos cambian en tiempo real (necesita contexto temporal)

**NO animar cuando:**
- El contenido estático simplemente se carga (el texto del artículo no necesita fade-in)
- Ya hay muchas animaciones en la misma pantalla
- La animación hace la tarea más lenta (el usuario debe esperar que termine)
- Es puramente decorativa sin función

### ¿Cuándo usar spring vs ease?

```
SPRING: Para objetos que interactúan con el usuario directamente
  → Modals, drawers, cards que el usuario "suelta"
  → Elementos que responden al gesto del usuario
  → Sensación: objeto físico, masa, rebote natural

EASE: Para transiciones de estado y navegación
  → Pantallas que cambian
  → Elementos que aparecen/desaparecen
  → Sensación: transición suave y controlada
```

---

## Anti-Patrones de Motion Design

**AM-301 — Animación sin propósito funcional**
Elementos que se mueven solo para verse dinámicos. Distrae, fatiga, y en usuarios con sensibilidad al movimiento puede causar malestar.

**AM-302 — Duraciones demasiado largas (> 600ms para micro-interacciones)**
El usuario siente que está esperando la UI. Cada milisegundo de espera innecesaria es frustración acumulada.

**AM-303 — Animaciones en loop sin control de pausa**
Cualquier animación que se repite indefinidamente sin poder pausarla viola WCAG 2.2.2 y es molesta para todos.

**AM-304 — Easing lineal en todo**
Las transiciones lineales se sienten robóticas y sin personalidad. Casi nunca es la elección correcta.

**AM-305 — Sin especificación de prefers-reduced-motion**
No especificar qué pasa cuando el usuario activa esta preferencia deja al frontend sin guía y puede generar experiencias que causen malestar físico.

**AM-306 — Stagger demasiado largo**
Si el último elemento del stagger aparece más de 500ms después del primero, el usuario siente que la página "carga lento" aunque todo esté disponible.

---

## Especificación de Handoff para Frontend

El Cerebro #3 debe entregar al Cerebro #4 para cada animación:

```yaml
animation:
  componente: "Modal de confirmación"
  trigger: "Click en botón Confirmar"
  tipo: "entrance"
  duracion: "250ms"
  easing: "cubic-bezier(0.0, 0.0, 0.2, 1)" # ease-out
  propiedades:
    - propiedad: "opacity"
      desde: 0
      hasta: 1
    - propiedad: "transform"
      desde: "scale(0.95)"
      hasta: "scale(1)"
  stagger: null
  reduced_motion: "Solo opacity, sin transform"
  notas: "El overlay de fondo anima simultáneamente con fade-in 200ms"
```

---

## Conexión con el Cerebro #3

| Habilidad del Cerebro #3 | Aporte de esta fuente |
|--------------------------|----------------------|
| Diseño de componentes completos | Estados animados: loading, success, error, hover, active |
| Handoff limpio a Frontend (#4) | Especificación técnica completa de cada animación |
| Coherencia del sistema visual | Tokens de animación: durations, easings, como parte del design system |
| Mobile-first | Consideraciones de performance y reduced-motion para móvil |

## Preguntas que el Cerebro #3 puede responder con esta fuente

1. ¿Qué función cumple esta animación? ¿Orientación, feedback, continuidad, o narrativa?
2. ¿Cuánto debe durar esta transición de pantalla?
3. ¿Qué easing corresponde a este tipo de movimiento?
4. ¿Qué le pasa a esta animación con prefers-reduced-motion activo?
5. ¿Esta micro-interacción comunica el estado correctamente?
6. ¿Cómo especifico esta animación para que el frontend la implemente exactamente?
7. ¿Hay demasiadas animaciones en esta pantalla?
