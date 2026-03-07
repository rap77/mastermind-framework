---
source_id: "FUENTE-320"
brain: "brain-software-03-ui-design"
niche: "software-development"
title: "Microinteractions: Designing with Details"
author: "Dan Saffer"
expert_id: "EXP-320"
type: "book"
language: "en"
year: 2013
distillation_date: "2026-03-03"
distillation_quality: "complete"
loaded_in_notebook: false
version: "1.0.0"
last_updated: "2026-03-03"
changelog:
  - version: "1.0.0"
    date: "2026-03-03"
    changes:
      - "Initial distillation from Microinteractions"
status: "active"
---

# Microinteractions: Designing with Details

**Dan Saffer**

## 1. Principios Fundamentales

> **P1 - Los detalles no son los detalles, son el producto**: La diferencia entre un producto bueno y uno excelente está en los microinteractions. Un "like" animado, un botón que responde, un mensaje que carga graceful-mente. Estos detalles crean delight.

> **P2 - Las microinteractions son feedback, no decoración**: No se trata de ser "lindo". Se trata de comunicación. El usuario realiza una acción, el sistema responde. Esa respuesta es la microinteracción.

> **P3 - La emoción se construye con pequeños momentos**: Un producto no es emocional por un gran anuncio. Es emocional por miles de pequeños momentos que hacen sentir al usuario entendido, valorado, y competente.

> **P4 - La animación tiene propósito funcional**: La animación no es para "hacerlo dinámico". Es para guiar atención, comunicar estado, y proveer feedback. Si la animación no tiene propósito funcional, es distracción.

> **P5 - Lo invisible importa tanto como lo visible**: El timing, la easing, el delay — estas propiedades invisibles definen si una microinteracción se siente natural o robótica. La diferencia está en los detalles de movimiento.

## 2. Frameworks y Metodologías

### The Structure of a Microinteraction

```
┌─────────────────────────────────────────────────┐
│  1. TRIGGER                                      │
│     What initiates the microinteraction          │
│     - System trigger (automatic)                 │
│     - User trigger (manual)                      │
├─────────────────────────────────────────────────┤
│  2. RULES                                        │
│  │  Determina qué pasa y cuando                  │
│  │  - Constraints                                │
│  │  - What data is needed                        │
│  ├─────────────────────────────────────────────┤
│  │  3. FEEDBACK                                  │
│  │  What the user sees/hears/feels               │
│  │  - Visual, auditory, haptic                   │
│  │  - Timing matters                             │
│  ├─────────────────────────────────────────────┤
│  │  4. LOOPS & MODES                             │
│  │  What happens next / repetition               │
│  │  - Long loops (meta-interactions)             │
│  │  - Modes (different states)                   │
│  └─────────────────────────────────────────────┘
```

### Trigger Types

**System Triggers** (Automáticos):
- App launches → splash screen
- Data loads → skeleton screen
- Error occurs → error message
- Battery low → warning

**User Triggers** (Manuales):
- Click → button press
- Swipe → navigation
- Type → character animation
- Drag → movement feedback

### Feedback Mechanisms

| Type | When to Use | Examples |
|------|-------------|----------|
| **Visual** | Always | Button states, loading spinners, success toasts |
| **Auditory** | Enhancement (never solo) | Click sounds, notification sounds |
| **Haptic** | Mobile, physical confirmation | Vibration on press, resistance on scroll |
| **Motion** | Guide attention, continuity | Page transitions, element transforms |

### Timing Principles

| Duration | Perception | Use Case |
|----------|------------|----------|
| **0-100ms** | Instant | Button press, hover feedback |
| **100-300ms** | Fast, fluid | Toggle switches, dropdowns |
| **300-500ms** | Noticeable | Page transitions, modal fades |
| **500ms-1s** | Deliberate | Loading states, progress bars |
| **1s+** | Frustrating if blocking | Anything longer needs progress indication |

### Easing Functions

```
Linear     → Mechanical, rare in UI
Ease-in    → Starts slow, ends fast (exit)
Ease-out   → Starts fast, ends slow (enter) ✅ Common
Ease-in-out → Slow both ends (duration > 500ms)
```

**Regla**: Enter = ease-out, Exit = ease-in

### Common Microinteractions

**1. Button Press**
```
Hover → Scale 1.05 (100ms, ease-out)
Click → Scale 0.95 (50ms, ease-in-out)
Release → Return (150ms, ease-out)
```

**2. Like/Heart Animation**
```
Click → Burst (scale + rotate)
      → Particles
      → Color fill
      → Bounce (200ms)
      → Settle (300ms)
```

**3. Loading States**
```
Skeleton → Pulse opacity (1.5s, infinite)
Spinner → Rotate (1s, linear, infinite)
Progress → Fill from 0% to 100% (ease-out)
```

**4. Input Validation**
```
Focus → Border highlight (150ms, ease-out)
Type → No feedback
Blur → Validate
     → Success: Checkmark fade in (200ms)
     → Error: Shake + red (300ms)
```

**5. Page Transition**
```
Exit → Old page fade + slide left (300ms, ease-in)
     → Gap of white (50ms)
Enter → New page slide from right (400ms, ease-out)
```

## 3. Modelos Mentales

### Modelo de "Perceived Performance"

**Objective vs Perceived performance**:
- Objective: 2 seconds to load
- Perceived: "It feels fast" or "It feels slow"

**Microinteractions mejoran perceived performance**:
- Skeleton screens > blank screens
- Progressive loading > waiting for everything
- Animated progress > static "loading..."

**Principle**: Make the wait feel shorter, even if time is same.

### Modelo de "Emotional Design" (Norman)

| Level | Description | Microinteraction role |
|-------|-------------|----------------------|
| **Visceral** | Immediate emotional reaction | Delight, surprise, beauty |
| **Behavioral** | Use, feel, control | Feedback, clarity, predictability |
| **Reflective** | Memory, meaning, self-image | Achievement, status, delight |

**Great microinteractions hit all three levels.**

### Modelo de "The Uncanny Valley of Animation"

```
Realismo ──────→
    ↓
Bad animation: "Especio, not natural"
Good animation: "Smooth, fluid"
Too real: "Unsettling" (uncanny valley)
Perfect real: "Invisible"
```

**Sweet spot**: Deliberately stylized, not photorealistic

### Modelo de "Affordance in Motion"

**Static affordance**: "This looks clickable"
**Motion affordance**: "This responds like it's clickable"

**The difference**:
- Hover = invitation to interact
- Press = confirmation of interaction
- Release = completion of interaction

**Motion makes affordance tangible.**

## 4. Criterios de Decisión

### When to Animate, When Not to

| ✅ Animate cuando | ❌ No animar cuando |
|--------------------|---------------------|
| State changes (on/off) | Static content |
| Transitions (A→B) | Loading-critical flows |
| Feedback (user action) | User wants speed > delight |
| Guidance (draw attention) | Accessibility: respect prefers-reduced-motion |
| Delight (brand moments) | Repetitive tasks become annoying |

### Animation Duration Guidelines

| Task | Duration | Rationale |
|------|----------|-----------|
| **Button press** | 100-200ms | Instant feedback |
| **Dropdown reveal** | 150-250ms | Noticeable but not slow |
| **Modal open** | 200-400ms | Feels substantial |
| **Page transition** | 300-500ms | Context switch |
| **Element entry** | 400-600ms | Delightful entrance |
| **Loading loop** | 1-2s per cycle | Soothing repetition |

**Never block user > 100ms for animation.**

### Easing Selection

| Scenario | Easing | Why |
|----------|--------|-----|
| **UI entry** | ease-out | Fast start, smooth land |
| **UI exit** | ease-in | Gentle leave |
| **Bounce** | spring | Physics-based, playful |
| **Loop** | linear | Consistent speed |
| **Color/opacity** | ease-in-out | Smooth transition both ends |

### Performance Budget for Animation

| Metric | Target | Why |
|--------|--------|-----|
| **Frame rate** | 60fps | Smooth motion |
| **Jank** | < 5% dropped frames | Perceptual limit |
| **CPU during anim** | < 50% | Leave headroom for other tasks |
| **Anim duration** | < 500ms (most cases) | Don't block user |

**Test**: Chrome DevTools Performance tab, look for long frames.

### Accessibility Considerations

| Respect | Implementation |
|---------|----------------|
| **prefers-reduced-motion** | `@media (prefers-reduced-motion: reduce)` → disable animations |
| **Screen readers** | Animations should not interfere with SR announcements |
| **Photosensitive epilepsy** | No flashing > 3 times per second |
| **Cognitive load** | Don't animate everything, prioritize |

## 5. Anti-patrones

### Anti-patrón: "Animation for Animation's Sake"

**Problema**: Animaciones que no sirven a propósito.

**Solución:**
- Every animation should have functional purpose
- Delight is purpose, but not sole purpose
- Test: Remove animation, does experience suffer?

### Anti-patrón: "Long Blocking Animations"

**Problema**: Animaciones que bloquean interacción > 500ms.

**Solución:**
- Keep animations under 300ms for interactive elements
- Or allow interruption (user can click away)
- Or make non-blocking (background)

### Anti-patrón: "Synchronous Animations"

**Problema**: Todo se anima al mismo tiempo. Caos visual.

**Solución:**
- Stagger animations (elements enter one after another)
- Hierarchy: important elements animate first
- Restraint: not everything needs to move

### Anti-patrón: "Linear Spring"

**Problema**: Movimiento lineal = robótico.

**Solución:**
- Use easing functions
- Spring physics for natural feel
- Or simple ease-out for most UI

### Anti-patrón: "Infinite Loading Spinner"

**Problema**: Spinner que gira sin contexto, sin progreso.

**Solución:**
- Skeleton screens for content
- Progress bars for determinate waits
- Time estimate: "This will take ~30 seconds"

### Anti-patrón: "Surprise Interactions"

**Problema**: Interacciones inesperadas, sin affordance.

**Solución:**
- Hover before click (invitation)
- Test with real users
- Follow platform conventions

### Anti-patrón: "Delight Over Function"

**Problema**: Priorizar delight sobre function.

**Solución:**
- Function first, delight second
- Delight enhances, not replaces
- If in doubt, function > delight

### Anti-patrón: "No Feedback on Interaction"

**Problema**: User clicks, nothing happens (or too subtle to notice).

**Solución:**
- Instant feedback (< 100ms)
- Visual + state change
- Confirm: "Yes, I clicked and something happened"

### Anti-patrón: "Same Animation Everywhere"

**Problema**: Reusing same animation in all contexts.

**Solución:**
- Context matters
- Primary actions get more emphasis
- Secondary actions get subtler feedback
- Hierarchy of animation importance

### Anti-patrón: "Ignoring Motion Sickness"

**Problema**: Parallax, zoom, rotations that make people dizzy.

**Solución:**
- Avoid parallax on mobile
- No rapid zoom/pan without user initiation
- Respect prefers-reduced-motion
- Test with motion-sensitive users
