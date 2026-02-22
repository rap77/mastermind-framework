# Cerebros #2 a #7 — Especificaciones

Este documento contiene las especificaciones de los cerebros 2 a 7. Cada uno seguirá la misma profundidad que el Cerebro #1 cuando se implemente, pero aquí se define la estructura, habilidades, expertos, y fuentes recomendadas.

---

## Cerebro #2 — UX Research & Strategy

**Nombre NotebookLM:** [CEREBRO] UX Research — Software Development
**Rol:** Define CÓMO debe funcionar la experiencia para que el usuario logre su objetivo sin fricción.
**Pregunta Central:** ¿Cómo debe sentirse y funcionar esta experiencia para el usuario?

### 5 Capas

| Capa | Contenido |
|------|-----------|
| Base Conceptual | Human-Centered Design, Psicología Cognitiva, Affordances, Ley de Hick, Ley de Fitts |
| Frameworks | Design Thinking (IDEO), User Journey Mapping, Card Sorting, Heurísticas de Nielsen |
| Modelos Mentales | Empatía radical, Cognitive load theory, Progressive disclosure, Mental models del usuario |
| Criterios de Decisión | Simplicidad vs Funcionalidad, Convención vs Innovación, Accesibilidad como requisito |
| Retroalimentación | SUS Score, Task success rate, Time-on-task, Error rates, Testing de usabilidad |

### Habilidades y Expertos

| Habilidad | Experto | Fuente Clave | ISBN |
|-----------|---------|-------------|------|
| Diseño centrado en humanos | Don Norman | The Design of Everyday Things | 978-0465050659 |
| Usabilidad | Jakob Nielsen | Usability Engineering + NN/g Articles | 978-0125184069 |
| Simplificación UX | Steve Krug | Don't Make Me Think (3rd Ed) | 978-0321965516 |
| Diseño emocional | Aarron Walter | Designing for Emotion (2nd Ed) | 978-1937557584 |
| Research cualitativo | Indi Young | Practical Empathy | 978-1933820583 |
| Research práctico | Erika Hall | Just Enough Research (2nd Ed) | 978-1937557744 |

### Inputs/Outputs

- **Recibe de:** Cerebro #1 (problema validado, persona, propuesta de valor)
- **Entrega a:** Cerebro #3 (journey maps, wireframes, arquitectura de información)

---

## Cerebro #3 — UI Design

**Nombre NotebookLM:** [CEREBRO] UI Design — Software Development
**Rol:** Convierte la experiencia en interfaz visual atractiva, coherente, y escalable.
**Pregunta Central:** ¿Cómo se ve y se comunica visualmente este producto?

### 5 Capas

| Capa | Contenido |
|------|-----------|
| Base Conceptual | Teoría del color, Tipografía, Gestalt, Grid Systems, Visual Hierarchy |
| Frameworks | Atomic Design (Brad Frost), Design Tokens, Material Design, Design Systems |
| Modelos Mentales | Consistencia > Creatividad, Mobile-first, Component-driven design |
| Criterios de Decisión | Escalabilidad vs Personalización, Estética vs Performance, Handoff limpio |
| Retroalimentación | Design review, A/B testing visual, Consistency audits, Component reuse rate |

### Habilidades y Expertos

| Habilidad | Experto | Fuente Clave | ISBN |
|-----------|---------|-------------|------|
| Design Systems | Brad Frost | Atomic Design | 978-0998296609 |
| UI práctica | Adam Wathan & Steve Schoger | Refactoring UI | N/A (digital only) |
| Mobile-first | Luke Wroblewski | Mobile First | 978-1937557027 |
| Tipografía | Ellen Lupton | Thinking with Type (2nd Ed) | 978-1568989693 |
| Grid Systems | Josef Müller-Brockmann | Grid Systems in Graphic Design | 978-3721201451 |

### Inputs/Outputs

- **Recibe de:** Cerebro #2 (wireframes, journey maps, arquitectura de info)
- **Entrega a:** Cerebro #4 (design system, componentes, especificaciones, assets)

---

## Cerebro #4 — Frontend Architecture

**Nombre NotebookLM:** [CEREBRO] Frontend — Software Development
**Rol:** Convierte diseño en experiencia interactiva real. Si falla, el producto se siente lento o roto.
**Pregunta Central:** ¿Cómo construimos una interfaz que sea rápida, accesible, y mantenible?

### 5 Capas

| Capa | Contenido |
|------|-----------|
| Base Conceptual | DOM, Browser rendering pipeline, Event loop, HTTP/2, Web APIs |
| Frameworks | React/Next.js, Component architecture, State management, Server Components |
| Modelos Mentales | Declarative > Imperative, Composition over inheritance, Progressive enhancement |
| Criterios de Decisión | Performance vs DX, Bundle size vs Features, SSR vs CSR vs ISR |
| Retroalimentación | Core Web Vitals (LCP, FID, CLS), Lighthouse, Error tracking, Bundle analysis |

### Habilidades y Expertos

| Habilidad | Experto | Fuente Clave | ISBN/URL |
|-----------|---------|-------------|----------|
| React / Mental models | Dan Abramov | Overreacted blog + Just JavaScript | overreacted.io |
| Testing frontend | Kent C. Dodds | Testing Library + Epic React | epicreact.dev |
| Web Performance | Addy Osmani | Learning Patterns | 978-1098134280 |
| JavaScript profundo | Kyle Simpson | You Don't Know JS (series) | 978-1491924464 |
| CSS avanzado | Josh Comeau | CSS for JS Developers | css-for-js.dev |
| Next.js / React patterns | Documentación oficial | Next.js Docs + React Docs | nextjs.org/docs |

### Inputs/Outputs

- **Recibe de:** Cerebro #3 (design system, componentes, specs)
- **Entrega a:** Cerebro #5 (requisitos de API, contratos de datos)

---

## Cerebro #5 — Backend & Systems Architecture

**Nombre NotebookLM:** [CEREBRO] Backend — Software Development
**Rol:** Construye la lógica, datos, y seguridad del sistema. Si falla, el sistema colapsa al crecer.
**Pregunta Central:** ¿Cómo diseñamos un sistema que sea seguro, escalable, y mantenible?

### 5 Capas

| Capa | Contenido |
|------|-----------|
| Base Conceptual | Clean Architecture, SOLID, DDD, CAP Theorem, ACID |
| Frameworks | REST/GraphQL API design, ORM patterns, Message queues, Caching |
| Modelos Mentales | Separation of concerns, Fail-fast, Idempotency, Event sourcing |
| Criterios de Decisión | SQL vs NoSQL, Monolith vs Microservices, Consistency vs Availability |
| Retroalimentación | Query performance, Error rates, Latency p99, Uptime SLA |

### Habilidades y Expertos

| Habilidad | Experto | Fuente Clave | ISBN |
|-----------|---------|-------------|------|
| Clean Code / SOLID | Robert C. Martin | Clean Architecture | 978-0134494166 |
| Patrones de arquitectura | Martin Fowler | Patterns of Enterprise App Architecture | 978-0321127426 |
| System Design | Alex Xu | System Design Interview (Vol 1 & 2) | 978-1736049211 |
| Sistemas distribuidos | Martin Kleppmann | Designing Data-Intensive Applications | 978-1449373320 |
| TDD | Kent Beck | Test Driven Development | 978-0321146533 |

### Inputs/Outputs

- **Recibe de:** Cerebro #4 (requisitos de API, contratos de datos)
- **Entrega a:** Cerebro #6 (código, configuración, documentación de despliegue)

---

## Cerebro #6 — QA & DevOps

**Nombre NotebookLM:** [CEREBRO] QA DevOps — Software Development
**Rol:** Garantiza estabilidad y despliegue continuo. Sin este cerebro, el producto se vuelve inestable.
**Pregunta Central:** ¿Cómo desplegamos y mantenemos este sistema de forma segura y confiable?

### 5 Capas

| Capa | Contenido |
|------|-----------|
| Base Conceptual | CI/CD, Infrastructure as Code, Shift-left testing, Observabilidad |
| Frameworks | GitHub Actions, Docker, Kubernetes basics, Terraform |
| Modelos Mentales | Everything as code, Immutable infrastructure, Blast radius minimization |
| Criterios de Decisión | Speed vs Safety, Automation cost vs Manual risk, Monitoring depth vs Alert fatigue |
| Retroalimentación | DORA metrics: Deployment frequency, Lead time, MTTR, Change failure rate |

### Habilidades y Expertos

| Habilidad | Experto | Fuente Clave | ISBN |
|-----------|---------|-------------|------|
| DevOps Culture | Gene Kim | The Phoenix Project | 978-1942788294 |
| Métricas DevOps | Nicole Forsgren | Accelerate | 978-1942788331 |
| Continuous Delivery | Jez Humble | Continuous Delivery | 978-0321601919 |
| Observabilidad | Charity Majors | Observability Engineering | 978-1492076445 |
| QA Agile | Lisa Crispin | Agile Testing | 978-0321534460 |

### Inputs/Outputs

- **Recibe de:** Cerebro #5 (código, configs, docs de deploy)
- **Entrega a:** Cerebro #7 (sistema en producción, métricas de estabilidad)

---

## Cerebro #7 — Growth & Data (Meta-Cerebro Evolutivo)

**Nombre NotebookLM:** [CEREBRO] Growth Data — Software Development
**Rol:** No construye. **Observa todos los cerebros en tiempo real, cuestiona, evalúa, y obliga a evolucionar.** Es el único cerebro que tiene autoridad sobre todos los demás.
**Pregunta Central:** ¿Está funcionando? ¿Dónde se rompe? ¿Qué optimizamos?

### 5 Capas

| Capa | Contenido |
|------|-----------|
| Base Conceptual | Growth loops, Pirate Metrics (AARRR), North Star Framework, Behavioral Economics |
| Frameworks | A/B testing, Cohort analysis, Funnel analysis, Experiment design, Retention curves |
| Modelos Mentales | Compounding growth, Power user curves, Activation moments, Habit loops |
| Criterios de Decisión | Growth vs Retention, Short-term wins vs Long-term value, Data vs Intuition |
| Retroalimentación | North Star Metric, LTV/CAC ratio, Activation rate, Retention curves, NPS trends |

### Habilidades y Expertos

| Habilidad | Experto | Fuente Clave | ISBN |
|-----------|---------|-------------|------|
| Ofertas y monetización | Alex Hormozi | $100M Offers | 978-1737475712 |
| Growth Hacking | Sean Ellis | Hacking Growth | 978-0451497215 |
| Product Growth | Lenny Rachitsky | Lenny's Newsletter | lennysnewsletter.com |
| Network Effects | Andrew Chen | The Cold Start Problem | 978-0062969743 |
| Growth Systems | Brian Balfour | Reforge Essays | brianbalfour.com |

### Función especial: Evaluador en Tiempo Real

Este cerebro NO espera al final. Está presente en cada paso:

```
Cerebro 1 genera output → #7 evalúa → aprueba o rechaza
Cerebro 2 genera output → #7 evalúa → aprueba o rechaza
...
Cerebro 6 genera output → #7 evalúa → aprueba o rechaza
```

### Cómo guía y cuestiona

1. **Recibe copia de cada output** generado por cualquier cerebro
2. **Evalúa contra:** coherencia, completitud, calidad profesional, viabilidad
3. **Puede:** aprobar, pedir iteración, pedir clarificación, señalar conflicto, escalar
4. **Acumula logs** de evaluación para detectar patrones de error
5. **Propone mejoras** al knowledge base y a los criterios de evaluación

### Inputs/Outputs

- **Recibe de:** TODOS los cerebros (cada output generado)
- **Entrega a:** Orquestador (verdicts), cerebros individuales (feedback), CEO (reportes)
