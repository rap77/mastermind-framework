---
source_id: "FUENTE-215"
brain: "brain-software-02-ux-research"
niche: "software-development"
title: "Lean UX: Applying Lean Principles to Improve User Experience"
author: "Jeff Gothelf, Josh Seiden"
expert_id: "EXP-215"
type: "book"
language: "en"
year: 2016
distillation_date: "2026-03-03"
distillation_quality: "complete"
loaded_in_notebook: false
version: "1.0.0"
last_updated: "2026-03-03"
changelog:
  - version: "1.0.0"
    date: "2026-03-03"
    changes:
      - "Initial distillation from Lean UX 2nd Edition"
status: "active"
---

# Lean UX: Applying Lean Principles to Improve User Experience

**Jeff Gothelf, Josh Seiden**

## 1. Principios Fundamentales

> **P1 - Outputs ≠ Outcomes**: Diseñar hermosos deliverables (outputs) no garantiza resultados de negocio (outcomes). El outcome es el cambio de comportamiento del usuario, no el artifact.

> **P2 - El diseño es hypothesis, no blueprint**: Lo que creemos que funciona es solo una hipótesis. Hasta que usuarios reales interactúan, es especulación educada, pero especulación al fin.

> **P3 - Shared understanding beats documentation**: 100 páginas de specs que nadie lee vs 2 horas de conversación. Lean UX apuesta por conversación continua sobre documentación exhaustiva.

> **P4 - Small batches, fast feedback**: Lanzar pequeño y medir es mejor que lanzar grande y arriesgar. El learning early es el mayor ROI.

> **P5 - Problem-focused, not solution-focused**: No empieces con "vamos a construir X". Empieza con "qué problema estamos tratando de resolver y para quién".

## 2. Frameworks y Metodologías

### The Lean UX Cycle

```
┌─────────────────────────────────────────────────┐
│  THINK                                            │
│  ┌───────────────────────────────────────────┐  │
│  │ Business outcome → Hypothesis             │  │
│  └───────────────────────────────────────────┘  │
│            ↓                                     │
│  MAKE                                             │
│  ┌───────────────────────────────────────────┐  │
│  │ Prototype → MVP → Feature                 │  │
│  └───────────────────────────────────────────┘  │
│            ↓                                     │
│  CHECK                                            │
│  ┌───────────────────────────────────────────┐  │
│  │ Measure → Learn → Pivot/Persevere         │  │
│  └───────────────────────────────────────────┘  │
└─────────────────────────────────────────────────┘
```

### The Hypothesis Template

```
We believe that
  [type of user]
has [needs/concerns/opportunities]

Our solution will
  [describe solution]

We will achieve
  [business outcome]

We will know this is true when we measure
  [KPI metric]
```

### The MVP: Not What You Think

| Misconception | Reality |
|---------------|----------|
| MVP = Minimum Viable Product | MVP = Minimum Learning Product |
| El objetivo es ser viable | El objetivo es aprender |
| Features recortadas | Experimento focalizado |
| Version 1.0 beta | Hypothesis test vehicle |

**Purpose of MVP**: Answer specific questions, not ship product.

### Definition of Done (DoD) in Lean UX

| Traditional UX DoD | Lean UX DoD |
|--------------------|-------------|
| Wireframes signed off | Hypothesis articulated |
| Pixel-perfect mockups | Prototype built |
| 50-page spec document | Experiment designed |
| Stakeholder approval | Learning plan ready |

**Done** = Ready to learn, not ready to ship.

### The Three Levels of Fidelity

| Level | Purpose | Timeline |
|-------|---------|----------|
| **Lo-Fi** (Sketches, paper) | Ideación rápida, feedback temprano | Hours |
| **Mid-Fi** (Wireframes, clickthroughs) | Estructura, flujo, layout | Days |
| **Hi-Fi** (Pixel-perfect, interactive) | Validación final, investor demo | Weeks |

**Lean UX bias**: Stay lo-fi as long as possible.

### The KPI Tree

```
Business Outcome
    ↓
Leading Indicators
    ↓
User Behaviors
    ↓
Features (what we build)
```

**Ejemplo**:
- Outcome: Revenue $1M
- Leading Indicator: 10% conversion free → paid
- User Behavior: Complete 5 projects/week
- Feature: Project templates

## 3. Modelos Mentales

### Modelo de "Outcome-Based Roadmap"

**Traditional Roadmap** (Output-based):
- Q1: Feature A
- Q2: Feature B
- Q3: Feature C

**Lean Roadmap** (Outcome-based):
- Q1: Increase user engagement 20%
- Q2: Improve trial-to-paid 15%
- Q3: Reduce churn to <5%

**Features son medios, no fines.**

### Modelo de "Waste in UX"

**Waste** (muda): Cualquier trabajo que no crea learning directo.

| Type of Waste | Example |
|---------------|---------|
| **Overproduction** | 100 wireframes cuando 10 bastan |
| **Waiting** | 2 weeks for stakeholder approval |
| **Overprocessing** | Pixel-perfect specs that change |
| **Defects** | Building without validation |
| **Inventory** | Unused designs, rejected concepts |

**Lean UX minimiza waste**: Just-enough design, just-in-time.

### Modelo de "Cross-Functional Teams**

**Anti-pattern**: Handoff entre departments
- UX hands off to Dev → Dev hands off to QA → QA hands off to Ops

**Lean UX model**: Squad cross-functional
- PM + Designer + Dev + QA working together
- From hypothesis to deployment in same team
- No handoffs, just collaboration

### Modelo de "Design as a Team Sport"

**Not "Designer does design, Dev builds, PM manages"**:
- Everyone participates in ideation
- Design happens in collaboration, not isolation
- Devs and PMs contribute design insights
- Designer facilitates, doesn't dictate

## 4. Criterios de Decisión

### When to Use Lean UX

| ✅ Ideal for | ❌ Not ideal for |
|---------------|-----------------|
| Startups,新产品 | Regulated industries (medical, aviation) |
| Digital products | Physical products with high tooling cost |
| Fast-moving markets | Safety-critical systems |
| Uncertain requirements | Well-understood problem space |
| Small cross-functional teams | Large organizations with silos (at first) |

### Validation: Qualitative vs Quantitative

| Qualitative | Quantitative |
|-------------|--------------|
| "Users said X" | "20% of users did X" |
| Small sample (5-10) | Large sample (1000+) |
| Interviews, usability tests | Analytics, A/B tests |
| Early discovery | Later validation |
| Understands "why" | Confirms "what" |

**Lean UX uses both**, but qualitative first, quantitative to confirm.

### MVP Scope: How Small?

| Too Small | Just Right | Too Big |
|-----------|-----------|---------|
| Una pregunta trivial | Una hipótesis clara | Múltiples hipótesis |
| No learning significativo | Learn significa | Demasiado riesgo |
| Landing page sin contexto | Wizard of Oz app | Producto completo |

**Rule**: Smallest thing that answers the question.

### Prioritization: ICE Scoring

| Factor | Score (1-10) | Weight |
|--------|--------------|--------|
| **I**mpact | ¿Cuánto outcome si funciona? | High |
| **C**onfidence | ¿Qué tan seguro estamos? | Medium |
| **E**ase | ¿Qué tan fácil de implementar? | Low |

**ICE Score** = (Impact × Confidence × Ease) / 1000

**Work on highest ICE first.**

### When to Pivot vs Persevere

| Evidence | Pivot | Persevere |
|----------|-------|-----------|
| User interest | ❌ < 10% engaged | ✅ > 30% engaged |
| Behavior | ❌ Not using as expected | ✅ Using as expected |
| Business metrics | ❌ Not moving leading indicators | ✅ Leading indicators improving |
| Team morale | ❌ Lost belief | ✅ Still believe |

**Decision made on data, not ego.**

## 5. Anti-patrones

### Anti-patrón: "Design as Art"

**Problema**: Diseñadores protegen su "work" como si fuera arte personal.

**Solución:**
- Design is hypothesis, not masterpiece
- El usuario es el crítico, no el designer
- Feedback es gift, no attack

### Anti-patrón: "Waterfall UX"

**Problema**: Research → Design → Spec → Dev → Test → Launch (waterfall).

**Solución:**
- Lean UX: Think → Make → Check (continuous loop)
- No gates, no handoffs
- Collaborative throughout

### Anti-patrón: "Feature Factory"

**Problema**: Team produces features without knowing if they matter.

**Solución:**
- Outcome-based roadmap
- Every feature tied to hypothesis
- Measure impact, not just output

### Anti-patrón: "Hi-Fi First"

**Problema**: Empezar con pixel-perfect designs.

**Solución:**
- Paper and sharpie first
- Progressively elaborate
- Hi-fi locks in thinking too early

### Anti-patrón: "Stakeholder-Driven Design"

**Problema**: HiPPO (Highest Paid Person's Opinion) drives decisions.

**Solución:**
- Hypothesis-driven, not opinion-driven
- Test with users, not in boardroom
- Data over hierarchy

### Anti-patrón: "No Time for Research"

**Problema**: "We're moving too fast for research."

**Solución:**
- Research is not a phase, it's continuous
- 5 user interviews > 0 user interviews
- Better to be roughly right than precisely wrong

### Anti-patrón: "Measure Everything"

**Problema**: Vanity metrics, data overload, analysis paralysis.

**Solución:**
- Measure what matters for the hypothesis
- One or two metrics per experiment
- Leading indicators, not just lagging

### Anti-patrón: "MVP = Crap Product"

**Problema**: "It's just MVP" como excusa por mala UX.

**Solución:**
- MVP means learning-focused, not crappy
- User experience must still be quality
- Simplificado no = broken
