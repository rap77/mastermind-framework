---
source_id: "FUENTE-219"
brain: "brain-software-02-ux-research"
niche: "software-development"
title: "Service Design: From Insight to Implementation"
author: "This is Service Design Doing (Livework, Stefanie Koehler)"
expert_id: "EXP-219"
type: "book"
language: "en"
year: 2018
distillation_date: "2026-03-03"
distillation_quality: "complete"
loaded_in_notebook: false
version: "1.0.0"
last_updated: "2026-03-03"
changelog:
  - version: "1.0.0"
    date: "2026-03-03"
    changes:
      - "Initial distillation from Service Design"
status: "active"
---

# Service Design: From Insight to Implementation

**This is Service Design Doing — Livework, Stefanie Koehler**

## 1. Principios Fundamentales

> **P1 - El servicio es la experiencia, no el touchpoint**: Un servicio es un sistema que ayuda a usuarios a lograr un objetivo a través del tiempo y a través de múltiples canales. No es una app, un website, o un call center. Es el journey completo, end-to-end, de todas las interacciones.

> **P2 - Los servicios se co-crean con múltiples actores**: No existe "el usuario" en aislamiento. Un servicio involucra usuarios, employees, partners, sistemas. Diseñar servicios es diseñar para todos estos actores y sus interacciones. Si los employees están frustrados, la experiencia del usuario también sufrirá.

> **P3 - Lo invisible es tan importante como lo visible**: El backend, los procesos internos, la cultura organizacional — estos "invisibles" afectan la experiencia del usuario tanto o más que el frontend. Service design expone y mejora todo el sistema, no solo la interfaz.

> **P4 - Los servicios son sistemas vivos que evolucionan**: No hay "terminado". Un servicio se usa, se mide, se mejora continuamente. El diseño es iterativo, basado en feedback real de todas las partes involucradas.

> **P5 - Los mapas de servicios son herramientas de alineación, no deliverables finales**: El valor de un blueprint o journey map no es el artifact en sí. Es la conversación que crea el artifact, el shared understanding que emerge, y las decisiones que se toman basadas en esa visualización.

## 2. Frameworks y Metodologías

### The Service Design Framework

```
INSIGHT → IDEATION → IMPLEMENTATION → ITERATION
    ↓           ↓              ↓            ↓
Research     Prototyping      Launch      Measurement
(Ethnography) (Service protos) (Pilot)    (KPIs)
```

### The Service Blueprint

**Capas (de frontstage a backstage)**:

| Layer | Description | Example |
|-------|-------------|---------|
| **Customer Actions** | Lo que hace el usuario | "Busco vuelo" |
| **Frontstage** | Interacciones visibles con usuario | App, website, agent |
| **Backstage** | Procesos internos invisibles | Sistema de reservas, crew scheduling |
| **Support Processes** | Procesos de soporte | Training, software maintenance |
| **Physical Evidence** | Tangibles del servicio | Boarding pass, app UI |

**El blueprint conecta user journey con operaciones internas.**

### The Customer Journey Map

**Componentes**:
```
1. Stages: Fases del journey (Awareness → Research → Purchase → Use → Support)
2. Touchpoints: Donde el usuario interactúa con el servicio
3. Customer Actions: Qué hace el usuario
4. Emotions: Cómo se siente el usuario
5. Pain Points: Dónde se rompe la experiencia
6. Opportunities: Dónde podemos mejorar
```

**Multiple perspectives**:
- **Current state map**: Cómo funciona hoy (con problemas)
- **Future state map**: Cómo funcionará después de mejoras

### Service Prototyping

**Levels**:
1. **Roleplay**: Actuar el servicio con team members
2. **Wizard of Oz**: Parece real, humanos detrás del telón
3. **Pilot**: Servicio real en escala limitada
4. **Beta**: Servicio real con usuarios reales

**Rule**: Prototipar servicios, no solo interfaces.

### The Double Diamond (Service Design)

```
Discover      Define         Develop         Deliver
  ↓              ↓               ↓               ↓
Research       Synthesis       Co-design       Implementation
(Ethnography) (Insights)      (Prototyping)   (Pilot)
```

**Iterative**: No es lineal, puedes volver a cualquier fase.

## 3. Modelos Mentales

### Modelo de "Servicio como Sistema"

```
┌─────────────────────────────────────────────────┐
│  Service Ecosystem                              │
│  ┌──────────────┐      ┌──────────────┐        │
│  │   Users      │◄────►│   Employees  │        │
│  └──────────────┘      └──────────────┘        │
│         ↕                     ↕                │
│  ┌──────────────────────────────────────────┐ │
│  │       Service Platform (Systems)         │ │
│  └──────────────────────────────────────────┘ │
│         ↕                     ↕                │
│  ┌──────────────┐      ┌──────────────┐        │
│  │   Partners   │      │   Policies   │        │
│  └──────────────┘      └──────────────┘        │
└─────────────────────────────────────────────────┘
```

**Todos los componentes afectan la experiencia.**

### Modelo de "Moment of Truth"

**Cada touchpoint es una oportunidad para delight o disappoint**:
- Primera impresión (onboarding)
- Momento de verdad (algo sale mal, cómo reaccionas)
- Momento peak (emotional high del journey)

**Jan Carlzon (SAS)**: "Hay 50 million moments of truth al día para SAS."

### Modelo de "Frontstage vs Backstage"

**Frontstage**: Visible al usuario
- Interface (app, web)
- Interacciones humanas (agents, support)
- Physical evidence (boarding pass, store)

**Backstage**: Invisible al usuario
- Procesos internos
- Sistemas (databases, APIs)
- Employee tools

**Service design asegura que backstage soporte frontstage efectivamente.**

### Modelo de "Co-creation"

**Stakeholders**:
- **Users**: Quienes usan el servicio
- **Employees**: Quienes entregan el servicio
- **Management**: Quienes deciden recursos
- **Partners**: Quienes proveen components del servicio

**Todos participan en el diseño del servicio.**

## 4. Criterios de Decisión

### Service Design vs Product Design

| Service Design | Product Design |
|----------------|----------------|
| Focus: Journey across channels | Focus: Specific artifact (app, site) |
| Multi-disciplinary team | Often product-centric team |
| Includes operations | Often excludes operations |
| Timescale: months-years | Timescale: weeks-months |
| Ecosystem thinking | Product thinking |

### When to Use Service Design

| ✅ Use service design when | ❌ Product design sufficient when |
|-----------------------------|-------------------------------|
| Multi-channel experience | Single-channel product |
| Complex user journey | Simple, linear journey |
| Operational efficiency critical | Operational concerns minimal |
- Employee experience matters | Only end-user experience matters |

### Measurement: SLAs vs User Experience

| SLA (Service Level Agreement) | UX Metrics |
|-------------------------------|------------|
| System uptime | NPS, CSAT |
| Response time | Effort score |
| Resolution rate | Completion rate |
| Internal metrics | Customer perception |

**Measure both**: SLAs ensure operations work; UX metrics ensure customers are happy.

### Channel Strategy: Omni-channel vs Multi-channel

| Multi-channel | Omni-channel |
|---------------|--------------|
| Multiple channels operate independently | Channels integrated seamlessly |
| Customer restarts journey in each channel | Journey continues across channels |
| Easier to implement | Harder but better UX |

**Examples**:
- Multi-channel: Bank (branch, app, website — separate accounts)
- Omni-channel: Bank (start on app, continue in branch, same context)

## 5. Anti-patrones

### Anti-patrón: "Designing Only the Frontstage"

**Problema**: Diseñar la app sin considerar cómo employees la soportan.

**Solución**:
- Blueprint incluye backstage
- Co-design con employees
- Employee experience matters

### Anti-patrón: "Ignoring the Invisible"

**Problema**: No considerar sistemas internos, políticas, cultura.

**Solución**:
- Blueprint all layers
- Interview employees
- Understand constraints

### Anti-patrón: "Service Design as One-Off"

**Problema**: Hacer service design una vez, nunca volver.

**Solución**:
- Continuous improvement
- Measure and iterate
- Service is living system

### Anti-patrón: "Siloed Service Design"

**Problema**: Cada departamento optimiza su parte, no el servicio completo.

**Solución**:
- Cross-functional team
- Shared goals
- End-to-end ownership

### Anti-patrón: "Prototype Only the Interface"

**Problema**: Prototipar app sin prototipar el servicio completo.

**Solución**:
- Roleplay service
- Wizard of Oz test
- Pilot real service

### Anti-patrón: "Measuring Only Outputs"

**Problema**: Medir solo lo que produce el servicio (transactions), no la experiencia.

**Solución**:
- Measure outcomes (satisfaction, effort)
- Measure both SLAs and UX metrics
- Balance efficiency and experience

### Anti-patrón: "Ignoring Employee Experience"

**Problema**: Diseñar para usuarios, ignorando employees.

**Solución**:
- Happy employees = happy customers
- Employee experience es parte del service design
- Co-design con staff

### Anti-patrón: "Over-Engineering Service"

**Problema**: Diseñar servicio complejo sin necesidad.

**Solución**:
- Start simple
- Add complexity only if needed
- Simple is better than complex
