# Vision Document — Multi-Harness Architecture

## 1. Problem Statement

MasterMind es una plataforma de orquestación de agentes con Knowledge Distillation que opera sobre múltiples nichos, modelos y proyectos. Su Coordinator (`apps/api/mastermind_cli/orchestrator/coordinator.py`) ya ejecuta tareas con un iteration loop básico (`MAX_ITERATIONS=3`) y routing a cerebros especializados vía MCP.

Sin embargo, el sistema carece de cuatro capacidades críticas para operar de forma confiable, autónoma y medible:

### 1.1 Falta de governance sobre ejecución de agentes

Los agentes pueden ejecutar acciones destructivas (borrar archivos, commits sin tests, llamadas a API sin validar) sin control determinista. No hay un policy gate que intercepte intenciones antes de ejecutarlas.

### 1.2 Ausencia de evaluación medible

La calidad de la Memory Layer y del retrieval no se evalúan con métricas reproducibles (recall@k, MRR, nDCG). Sin esto, las mejoras son por intuición y las regresiones pasan inadvertidas.

### 1.3 Token waste sin presupuesto

No hay budget enforcement por tarea/sesión. El multi-backend routing (z.ai, Claude, OpenRouter) descrito en los docs de arquitectura no tiene un scheduler operacional implementado.

### 1.4 Harness estático sin mejora continua

El sistema no evoluciona sus propias reglas basándose en fallos observados. Cada error requiere intervención manual para prevenir repetición.

---

## 2. Users / Stakeholders

| Rol | Descripción | Interacción con el harness |
|---|---|---|
| **Desarrollador principal** | rpadron — único operador actual | Configura policies, aprueba reglas del meta-loop, define qrels |
| **Agentes AI** | Claude Code, Codex, futuros modelos | Operan dentro del harness; sus acciones son interceptadas por SAL |
| **Cerebros especializados** | 8 brains con doctrina experta | Ejecutan tasks orquestadas; el eval harness mide su calidad |
| **Futuros adoptantes** | Equipos que usen MasterMind como framework (modelo Core + Project Adapter, doc 13) | Heredan governance policies configurables |
| **Target comercial** | Pymes LATAM que necesitan automatización con IA | Beneficiarios finales de calidad garantizada por el harness |

---

## 3. Success Criteria (Medibles)

| # | Criterio | Métrica | Target |
|---|---|---|---|
| SC-1 | Menos errores repetidos | Tasa de re-ocurrencia de fallos ya capturados por meta-loop | <10% |
| SC-2 | Token waste reducido | Tokens consumidos vs. baseline sin budget enforcement | -30% ahorro |
| SC-3 | Calidad medible | Scorecards de Memory Layer con recall@5 en qrels | ≥0.80 |
| SC-4 | Regression prevention | PRs que degradan score bloqueados en CI | 100% blocked |
| SC-5 | Continuidad entre sesiones | Otro modelo puede resumir desde checkpoint sin chat memory | Success rate ≥90% |
| SC-6 | Ejecución nocturna segura | Mode cautious ejecuta 8h sin intervención, zero destructive actions | 0 incidents/week |
| SC-7 | Governance compliance | Todas las acciones de alto riesgo pasan por approval gate | 100% intercepted |

---

## 4. Risks + Mitigations

| # | Riesgo | Impacto | Probabilidad | Mitigación |
|---|---|---|---|---|
| R-1 | Over-engineering | Alto: infra de harness que nunca se usa | Media | Thin slices incrementales; cada componente debe tener uso en <1 semana |
| R-2 | Token overhead del harness | Medio: policies consumen tokens del budget | Media | Policy gate 100% determinista (no LLM-based); <5% del budget |
| R-3 | Complejidad multi-harness | Alto: 4 harnesses que se acoplan mal | Baja | Memoria compartida via `.mm-flow/planning/`; DAG explícito; interfaces typed |
| R-4 | Regresión por meta-loop | Alto: auto-aplica regla mala que degrada | Media | Regression tests obligatorios; rollback automático; human approval para reglas de ejecución |
| R-5 | Backend scheduling premature | Bajo: scheduler sin backends configurados | Alta | Solo scheduler para backends confirmados (Claude Code CLI, Codex CLI); planned backends después |
| R-6 | Eval harness con corpus ruidoso | Medio: métricas engañosas | Baja | Phase 1 solo con corpus estable (99 docs); planning/audit en phase 3 |

---

## 5. Non-Functional Requirements (NFRs)

| NFR | Requisito | Justificación | Source |
|---|---|---|---|
| **Continuidad** | Checkpoint-based resume entre modelos/backends sin pérdida de progreso | Otro modelo debe poder resumir sin chat memory | Doc 21, 45 |
| **Auditabilidad** | Toda acción trazable: quién, cuándo, por qué, con qué costo | Compliance, debugging, meta-loop input | Doc 25, 35 |
| **Agnosticismo de modelo** | Harness funciona con Claude, z.ai, OpenRouter, modelos locales | Evitar vendor lock-in; DR-004 | Doc 16, DR-004 |
| **Budget-aware** | Limits por tarea (100K default), sesión (500K), con warning al 80% y gate al exceder | Token waste prevention | Doc 19, Q2 |
| **Determinismo en bordes** | Policy gates son código Python, no prompts; sin LLM para validar acciones | Predecibilidad; no depender del modelo para seguridad | Notebook Harness Engineering |
| **Bajo overhead de tokens** | El harness no debe consumir >5% del budget total de una tarea | Valor > costo | Design decision |
| **Resistencia a fallos** | Circuit breakers, reintentos, escalación a humano tras 2-3 fallos consecutivos | Night mode seguro | Doc 17, Q7 |
| **Reversibilidad** | Meta-loop: auto-rollback si regression tests fallan tras nueva regla | Prevenir degradación acumulativa | Q3 |

---

## 6. MVP Scope vs Future Scope

### 6.1 MVP (este módulo — Multi-Harness Architecture v1)

| Componente | Entregable | Criterio de completitud |
|---|---|---|
| **SAL Policy Gate** | Interceptor Python antes del Coordinator con 10 categorías de bloqueo | Todas las acciones destructivas interceptadas en test suite |
| **Token Budget Enforcer** | Counter por tarea/sesión con warning/approval/stop tiers | Tests demuestran enforcement correcto |
| **Memory Eval Harness** | 18-20 qrels + scorer (recall@k, MRR) + CI gate | Baseline v0 capturado; PR que degrada score se bloquea |
| **Pre-commit Regression Gate** | Hook que valida tests relevantes según tipo de cambio | Code changes → tests; docs → no tests |
| **Overnight Mode (Cautious)** | Execution loop con checkpoint + reevaluación por tarea | 8h run sin incidents |

### 6.2 Future Scope (post-MVP)

| Componente | Descripción | Prerequisite |
|---|---|---|
| Multi-backend scheduler loop | Night Mode con z.ai/OpenRouter/Claude rotation | Backends configurados con API keys |
| Meta-loop de mejora continua | Weekly cycle: metrics → pattern detection → rule update → validate | MVP stable, ≥20 tasks ejecutadas con audit |
| Brain Learning feedback loop | Experience → doctrine update automático | Memory Layer Phase 5 operational |
| Evaluation harness como servicio | Módulo comercializable per doc 60 | MVP eval harness estable 3+ meses |
| Runtime eval (online scoring) | Sampling en producción con alertas de drift | CI eval harness maduro; memory layer runtime estable |
| Rust migration de hot-path gates | SAL gate en Rust si demuestra ser bottleneck | Medición que justifique la migración |

---

## 7. Competitive Landscape

| Alternativa | Qué resuelve | Limitación vs MasterMind |
|---|---|---|
| **Paperclip** | Orquestación de agentes (solo ejecución) | No tiene Knowledge Distillation, ni governance, ni eval harness |
| **LangGraph** | State machine para LLM workflows | No tiene brains especializados, ni doctrina, ni memory eval |
| **CrewAI** | Multi-agent roles colaborativos | Roles genéricos vs. 8 cerebros con fuentes expertas destiladas |
| **Claude Code / Kiro nativo** | IDE agents con steering rules | MasterMind es el harness que LOS envuelve; agrega governance + eval |
| **AI-DLC Workflows** | Lifecycle de desarrollo con phases | Complementario (ya instalado); no incluye eval harness ni SAL |
| **Promptfoo** | Eval framework para prompts | Solo evaluación; no governance, no orquestación, no brains |
| **RAGAS** | RAG evaluation metrics | Solo métricas de retrieval; no lifecycle, no policy gates |

**Diferenciador único de MasterMind:** Es el único sistema que combina orquestación de agentes especializados (con doctrina experta destilada) + governance determinista + evaluation medible + mejora continua del harness mismo. Los competidores resuelven una pieza; MasterMind las integra bajo un mismo framework.

---

## 8. Architectural Context

### 8.1 Multi-Harness Ecosystem

```
┌──────────────────────────────────────────────────┐
│           MASTERMIND HARNESS ECOSYSTEM            │
├──────────────────────────────────────────────────┤
│                                                  │
│  ┌─────────────────┐    ┌──────────────────┐    │
│  │ EXECUTION       │    │ EVALUATION       │    │
│  │ HARNESS         │    │ HARNESS          │    │
│  │ (MM-Flow)       │    │ (Memory Eval)    │    │
│  │                 │    │                  │    │
│  │ • Coordinator   │    │ • Qrels sellados │    │
│  │ • Brain routing │    │ • Scorer CI      │    │
│  │ • Task pipeline │    │ • Baselines      │    │
│  │ • MCP calls     │    │ • Regression gate│    │
│  └───────┬─────────┘    └────────┬─────────┘    │
│          │                       │               │
│          ▼                       ▼               │
│  ┌────────────────────────────────────────────┐  │
│  │        GOVERNANCE HARNESS                  │  │
│  │        (SAL Interceptor)                   │  │
│  │                                            │  │
│  │  • Policy gate (deterministic)             │  │
│  │  • Token budget enforcement                │  │
│  │  • Secret detection                        │  │
│  │  • Scope validation                        │  │
│  │  • Audit trail                             │  │
│  └────────────────────────────────────────────┘  │
│                                                  │
│  ┌─────────────────┐    ┌──────────────────┐    │
│  │ DISCOVERY       │    │ LEARNING         │    │
│  │ HARNESS         │    │ HARNESS          │    │
│  │ (AI-DLC)        │    │ (Future)         │    │
│  │                 │    │                  │    │
│  │ • Product disc. │    │ • Experience     │    │
│  │ • Tech disc.    │    │ • Brain evolve   │    │
│  │ • Interviews    │    │ • Meta-loop      │    │
│  └─────────────────┘    └──────────────────┘    │
│                                                  │
└──────────────────────────────────────────────────┘
```

### 8.2 Coordination Pattern

Los harnesses se coordinan mediante:
1. **Memoria compartida** — `.mm-flow/planning/` (archivos de estado)
2. **DAG de dependencias** — Cada harness recibe solo contexto necesario del anterior
3. **Typed interfaces** — Pydantic models para intercambio entre capas
4. **Event trail** — Audit log compartido para trazabilidad cross-harness

---

## 9. Decision Records Relevantes

| DR | Decisión | Relevancia para Multi-Harness |
|---|---|---|
| DR-001 | Core vs Project Adapter boundary | El harness es CORE; project-specific policies son ADAPTER |
| DR-003 | Backend switch audit minimums | Define qué auditar en cada switch → input para governance harness |
| DR-004 | Context budget strategy | Define tiers y presupuestos → implementación directa en budget enforcer |
| DR-005 | Model access through backend services | Todo acceso a modelos pasa por servicios → punto de intercepción natural para SAL |
| DR-007 | Rust control plane consolidation | Rust para performance; Python para policy reasoning → Q8 confirmed |

---

## 10. Handoff to AI-DLC Workflows

Este documento, junto con `technical-environment.md` y `open-questions.md`, está listo para ser consumido por AI-DLC Workflows en fase de Inception:

```
Load Product-Definition/vision-document.md and Product-Definition/technical-environment.md.
There are 8 open questions in Product-Definition/open-questions.md — resolve them during
Requirements Analysis before proceeding to Application Design.
Then execute the AI-DLC workflow for the Multi-Harness Architecture module.
Current phase: Inception (Requirements Analysis → Application Design → Units Generation).
```
