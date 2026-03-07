---
source_id: "FUENTE-618"
brain: "brain-software-02-ux-research"
niche: "software-development"
title: "Designing for Behavior Change: Applying Psychology and Behavioral Economics"
author: "Stephen Wendel (Hello Wallet), BJ Fogg"
expert_id: "EXP-220"
type: "article"
language: "en"
year: 2020
distillation_date: "2026-03-03"
distillation_quality: "complete"
loaded_in_notebook: false
version: "1.0.0"
last_updated: "2026-03-03"
changelog:
  - version: "1.0.0"
    date: "2026-03-03"
    changes:
      - "Initial distillation from behavioral science literature"
status: "active"
---

# Designing for Behavior Change

**Stephen Wendel, BJ Fogg — Behavioral Science applied to Product Design**

## 1. Principios Fundamentales

> **P1 - El comportamiento es función de motivación, habilidad, y trigger (B=MAP)**: La fórmula de Fogg: Behavior = Motivation × Ability × Prompt. Sin los tres, el comportamiento no ocurre. Diseñar para cambio de comportamiento es diseñar estos tres componentes.

> **P2 - La motivación fluctúa, la habilidad es más estable**: La motivación es emotional y variable. La habilidad (facilidad de hacer la acción) es más estable y predecible. Si quieres que alguien haga algo consistentemente, hazlo fácil, no solo motivante.

> **P3 - Los triggers deben ser oportunos, no intrusivos**: Un trigger (notificación, email, nudge) en el momento equivocado es spam. En el momento justo es helpful. El timing del trigger es más importante que el contenido.

> **P4 - El cambio de comportamiento es un journey, no un evento**: No diseñas para una conversión, diseñas para un hábito. El onboarding es solo el primer paso. El diseño debe soportar la formación del hábito a lo largo del tiempo.

> **P5 - La identidad es el predictor más fuerte de comportamiento a largo plazo**: Las personas actúan consistentemente con su identidad. "Yo soy alguien que hace ejercicio" es más poderoso que "voy a hacer ejercicio hoy". Diseña para reforzar identidad, no solo acción.

## 2. Frameworks y Metodologías

### The Fogg Behavior Model

```
Behavior = Motivation × Ability × Prompt (B = MAP)

High Motivation + Low Ability = Behavior (si trigger presente)
Low Motivation + High Ability = Behavior (si trigger presente)
Low Motivation + Low Ability = No Behavior (incluso con trigger)
```

**High motivation**:
- Celebration, social proof, scarcity
- Excitement, pleasure, pain avoidance

**High ability** (hacerlo fácil):
- Simplificar pasos
- Reducir tiempo/efuerzo/costo
- Hacerlo familiar (use existing patterns)

**Prompt (trigger)**:
- Signal (algo que dice "ahora")
- Context (en el momento oportuno)

### The Hook Model (Nir Eyal)

```
Trigger → Action → Reward → Investment
    ↓         ↓         ↓          ↓
  Internal  Behavior Variable   Return
  External  Effort   Reward    Effort
                    (Unpredictable)
```

**4 steps**:
1. **Trigger**: External (push, email) or Internal (boredom, stress)
2. **Action**: Simple behavior (scroll, like, share)
3. **Variable Reward**: Uncertainty creates addiction
4. **Investment**: User puts something in (data, content, followers)

**Products que se convierten en hábitos** implementan hooks.

### The COM-B Model

```
Capability (Ability)  ─────┐
        ↓                  │
Opportunity (Trigger) ──→ Behavior ←─── Motivation
        ↑                             ↑
    Facilitators               Barriers
```

**Components**:
- **Capability**: Tiene habilidad para hacerlo?
- **Opportunity**: Tiene oportunidad (trigger, access)?
- **Motivation**: Quiere hacerlo?

**Barriers vs Facilitators**:
- Remove barriers = Improve capability
- Add facilitators = Improve motivation

### The Stages of Change Model

```
Pre-contemplation → Contemplation → Preparation → Action → Maintenance
   (No awareness)   (Thinking about it) (Getting ready) (Doing it)   (Keeping it)
```

**Design for each stage**:
- **Pre-contemplation**: Raise awareness
- **Contemplation**: Motivate, show benefits
- **Preparation**: Make easy, provide tools
- **Action**: Support, celebrate progress
- **Maintenance**: Prevent relapse, reinforce identity

### Nudging Techniques

| Nudge | Mechanism | Example |
|-------|-----------|---------|
| **Default bias** | People stick with default | Opt-out organ donation |
| **Social proof** | Do what others do | "10 people bought this" |
| **Scarcity** | Value scarce things | "Only 2 left!" |
| **Loss aversion** | Fear of losing > gaining | "Don't lose your streak" |
| **Commitment** | Public commitment increases follow-through | Share your goal |

## 3. Modelos Mentales

### Modelo de "Habit Formation Loop"

```
Cue → Routine → Reward
  ↑                ↓
  └────────────────┘
```

**Loop se refuerza con cada repetición.**

**Design implications**:
- Identificar el cue (trigger)
- Simplificar la routine (facilitar)
- Asegurar reward (inmediato, satisfactorio)

### Modelo de "Identity-Based Behavior"

**Outcome-based**: "I want to run a marathon" (frágil)
**Process-based**: "I want to run 3x/week" (mejor)
**Identity-based**: "I am a runner" (más robusto)

**Design for identity**:
- Reinforce labels ("You're a saver!")
- Celebrate identity milestones
- Connect small actions to big identity

### Modelo de "Present Bias"

```
Ahora ──────── Futuro
Importancia ↘        ↗
         Present Bias
```

**Preferimos beneficios inmediatos sobre beneficios futuros.**

**Design implications**:
- Traer beneficios futuros al presente (visualización)
- Hacer costos futuros inmediatos (mostrar consecuencias)
- Bridge the gap between now and later

### Modelo de "Social Norms"

```
We do what others around us do
```

**Types of social influence**:
- **Descriptive norms**: "Most people like you do X"
- **Injunctive norms**: "People approve/disapprove of X"

**Design application**:
- Show what others do (social proof)
- Show what others approve (ratings, reviews)
- Leverage social norms for behavior change

## 4. Criterios de Decisión

### When to Use Nudges vs Force

| Nudges (Soft) | Force (Hard) |
|---------------|-------------|
| Preserve freedom of choice | Require action |
| Work with behavioral biases | Override defaults |
| Low resistance | High resistance |
| Ethical (usually) | May feel coercive |

**Rule**: Default to nudges. Use force only when necessary (health, safety).

### Reward Design: Immediate vs Delayed

| Immediate Reward | Delayed Reward |
|------------------|----------------|
| Best for forming new habits | Best for maintaining habits |
| Dopamine spike | Long-term satisfaction |
| Example: Points after action | Example: Monthly summary |

**Combine both** for maximum effect.

### Motivation Types

| Type | Trigger | Example |
|------|---------|---------|
| **Intrinsic** | Internal satisfaction | "I enjoy this" |
| **Extrinsic** | External rewards | Points, badges, money |
| **Identify-based** | Self-concept | "I'm this type of person" |

**Design implication**: Intrinsic motivation is most sustainable.

### Behavior Change Sustaining Strategies

| Strategy | Description | Example |
|----------|-------------|---------|
| **Tracking** | Make behavior visible | Progress bars, streaks |
| **Commitment** | Public or private commitment | Share goal, sign contract |
| **Community** | Social support | Groups, challenges |
| **Reminders** | Timely prompts | Push notifications |
| **Reframing** | Change perspective | "Workout" → "Me time" |

## 5. Anti-patrones

### Anti-patrón: "Dark Patterns"

**Problema**: Manipulative design that tricks users.

**Examples**:
- Confirmshaming ("No, I hate saving money")
- Hidden costs (revealed at checkout)
- Roach motel (easy to join, hard to leave)

**Solución**:
- Ethical nudges > manipulation
- Respect user autonomy
- Transparency about how design works

### Anti-patrón: "Over-Motivating"

**Problema**: Demasiada motivación, no suficiente facilidad.

**Solución**:
- Make easy first, then motivate
- Remove barriers before adding incentives
- Ability > Motivation (para hábitos)

### Anti-patrón: "Ignoring Context"

**Problema**: Triggers fuera de contexto son spam.

**Solución**:
- Trigger cuando/where behavior es relevante
- Context-aware notifications
- Respect user's time/attention

### Anti-patrón: "One-Size-Fits-All Nudging"

**Problema**: Mismo nudge para todos.

**Solución**:
- Personalize based on user segments
- Test different nudges (A/B testing)
- Adapt to individual behavior over time

### Anti-patrón: "Reward Inflation"

**Problema**: Premios se devalúan con el tiempo.

**Solución**:
- Scarce rewards are more valuable
- Variety in rewards
- Introduce new reward types periodically

### Anti-patrón: "Focusing Only on Initial Action"

**Problema**: Diseñar para conversión inicial, ignorando retención.

**Solución**:
- Design for habit formation
- Onboarding is just the beginning
- Long-term engagement > initial conversion

### Anti-patrón: "Ignoring Identity"

**Problema**: Focus on behavior, not identity.

**Solución**:
- Reinforce identity through labels ("You're a saver!")
- Celebrate identity milestones
- Connect actions to who they want to be

### Anti-patrón: "Excessive Triggers"

**Problema**: Demasiados prompts = notification fatigue.

**Solución**:
- Quality over quantity
- Trigger only when behavior is most likely to succeed
- Allow users to customize trigger frequency
