# GSD Framework — Deep Architecture Analysis

> Research realizado 2026-03-22 como input para el framework propio de flujos (v3.0+)

---

## Architecture Overview

GSD tiene 5 capas:

```
Layer 0: State (.planning/ — PROJECT, REQUIREMENTS, ROADMAP, STATE, config.json)
Layer 1: Orchestration (30+ workflows .md — hand-coded bash + gsd-tools)
Layer 2: Agents (12 specialized agents, 1500-3000 lines each)
Layer 3: Tooling (gsd-tools.cjs — state, roadmap, phase, verify, frontmatter, config, init)
Layer 4: Templates & References (20+ static .md files)
```

## Agent Inventory (12 agents)

| # | Agent | Purpose | Tools | Spawned By |
|---|-------|---------|-------|-----------|
| 1 | gsd-project-researcher | Domain ecosystem research for new projects | Read,Write,Bash,Grep,Glob,WebSearch,WebFetch,Context7 | /gsd:new-project |
| 2 | gsd-research-synthesizer | Synthesize 4 parallel research outputs → SUMMARY.md | Read,Write,Bash | /gsd:new-project |
| 3 | gsd-roadmapper | Requirements → phases → ROADMAP.md + STATE.md | Read,Write,Bash,Glob,Grep | /gsd:new-project |
| 4 | gsd-phase-researcher | Phase-specific research (stack, patterns, pitfalls) | Read,Write,Bash,Grep,Glob,WebSearch,WebFetch,Context7 | /gsd:plan-phase |
| 5 | gsd-planner | Tasks, waves, must-haves, gap closure → PLAN.md | Read,Write,Bash,Glob,Grep,WebFetch,Context7 | /gsd:plan-phase |
| 6 | gsd-plan-checker | Goal-backward plan validation, revision loop | Read,Bash,Glob,Grep | /gsd:plan-phase |
| 7 | gsd-executor | Atomic commits, deviations, checkpoints → SUMMARY.md | Read,Write,Edit,Bash,Grep,Glob | /gsd:execute-phase |
| 8 | gsd-verifier | Goal-backward code verification → VERIFICATION.md | Read,Write,Bash,Grep,Glob | /gsd:verify-work |
| 9 | gsd-integration-checker | Cross-phase wiring verification | Read,Bash,Grep,Glob | /gsd:validate-phase |
| 10 | gsd-nyquist-auditor | Test generation for validation gaps | Read,Write,Edit,Bash,Glob,Grep | /gsd:validate-phase |
| 11 | gsd-codebase-mapper | Static codebase analysis → STACK/ARCH/CONVENTIONS.md | Read,Bash,Grep,Glob,Write | /gsd:map-codebase |
| 12 | gsd-debugger | Hypothesis testing, persistent debug state | Read,Write,Edit,Bash,Grep,Glob,WebSearch | /gsd:debug |

## Core Workflow: plan-phase → execute-phase → verify

```
/gsd:plan-phase N
  ├── gsd-phase-researcher → RESEARCH.md (si --research o no existe)
  ├── gsd-planner → PLAN.md files (tasks, waves, must-haves)
  └── gsd-plan-checker → validate (max 3 revision loops)

/gsd:execute-phase N
  ├── Discover plans, group by wave
  ├── Wave N: spawn gsd-executor per plan (parallel if configured)
  │   ├── Task-by-task execution with atomic commits
  │   ├── Deviation Rules: 1-3 auto-fix, 4 checkpoint
  │   └── Write SUMMARY.md per plan
  └── Wave N+1: after N completes (dependency chain)

/gsd:verify-work N
  ├── gsd-verifier → VERIFICATION.md (goal-backward, 3-level artifact check)
  └── If gaps → /gsd:plan-phase --gaps → closure plans
```

## Strengths (What to Keep)

1. **Goal-backward methodology** — planes derivados del goal, no de la implementación. Verificación confirma goal, no tareas.
2. **Separation of concerns** — cada agente UNA responsabilidad. Orchestrador coordina, no ejecuta.
3. **Persistent state** — STATE.md sobrevive /clear. Debug files persisten entre sesiones.
4. **Atomic commits** — un commit por tarea. Rollback, bisect, trazabilidad.
5. **Wave-based parallelization** — planes agrupados por dependencia, waves paralelas.
6. **Deviation Rules** — Rules 1-3 auto-fix (bugs, missing crit, blocking). Rule 4 checkpoint (architectural changes).
7. **3-level artifact verification** — exists → substantive (not stub) → wired (imported + used).
8. **Revision loop** — planner → checker → revision (max 3). No se ejecuta un plan sin validar.
9. **User decision fidelity** — CONTEXT.md lock decisions. Planner honors, no improvisa.
10. **Nyquist validation** — tests mapeados a requirements, sampling rate por wave.

## Limitations (What to Improve)

### Hardcoded a Software Dev
- Asume git, source code, package managers, test frameworks, API routes
- Verificación busca anti-patterns de código (TODOs, stubs, orphaned exports)
- Templates asumen archivos .ts/.tsx/.py
- **No sirve para:** marketing campaigns, content creation, design workflows, hardware

### Sin Extensibilidad
- **No hay agent registry** — 12 agentes hardcoded. Agregar uno requiere tocar workflows.
- **No hay plugin system** — sin hooks para inyectar custom agents o verificaciones.
- **No hay orchestration DSL** — workflows son bash + gsd-tools, no declarativos.
- **Checkpoint types fijos** — solo 3 tipos (human-verify, decision, human-action).
- **Context inheritance manual** — `<files_to_read>` se copy-pastean en cada agent prompt.

### Complejidad Escondida
- Agent prompts de 1500-3000 líneas — difíciles de versionar, testear, customizar.
- Orchestrator workflows de 300+ líneas de bash — un cambio rompe múltiples flujos.
- Checkpoint resume protocol informal — no hay contrato formal para handoff.
- Wave assignment simple — no hay critical path analysis ni resource leveling.
- Requirements planos — REQ-IDs sin jerarquía ni precedencia.

## Extension Points (Oportunidades para Framework Propio)

### 1. Orchestration DSL (Declarative workflows)
```yaml
workflow: plan-phase
steps:
  - name: research
    agent: phase-researcher
    skip_if: has_research && !--research
  - name: plan
    agent: planner
    loop: checker (max 3)
  - name: brain-validate    # ← NO EXISTE EN GSD
    agent: brain-07-evaluator
    on_fail: cascade_to[domain-brains]
  - name: commit
    command: tools commit "docs: create plan"
```

### 2. Pluggable Agent Registry
```yaml
agents:
  research:
    - project-researcher
    - phase-researcher
    - brain-domain-researcher  # ← NUEVO: consulta cerebros
  planning:
    - planner
    - plan-checker
    - brain-evaluator           # ← NUEVO: Brain-07 valida
  execution:
    - executor
  verification:
    - verifier
    - integration-checker
    - nyquist-auditor
```

### 3. Domain-Agnostic Verification
```yaml
anti_patterns:
  software_dev:
    - TODOs in production code
    - Empty function bodies
    - Orphaned exports
  marketing:
    - Missing CTA in landing page
    - No A/B test variant
    - Missing tracking pixels
  design:
    - Missing accessibility labels
    - Inconsistent spacing tokens
    - Missing dark mode variants
```

### 4. Brain Integration Layer (Lo que GSD NO tiene)
```yaml
brain_gates:
  before_roadmap:
    brains: [product-strategy, evaluator]
    protocol: intermediary
  before_plan:
    brains: [domain-specific]
    protocol: intermediary
  before_execute:
    brains: [evaluator]
    protocol: intermediary + cascade
  after_phase:
    action: update-brain-feed
```

### 5. Custom Checkpoint Types
```yaml
checkpoint_types:
  human-verify: "Verify this works"
  decision: "Choose between options"
  human-action: "Do something external"
  brain-approval: "Brain-07 must approve"     # ← NUEVO
  customer-feedback: "Wait for user testing"  # ← NUEVO
  stakeholder-review: "PM must sign off"      # ← NUEVO
```

### 6. Niche-Specific Flow Templates
```yaml
flow_templates:
  software_dev:
    phases: [research, plan, execute, verify]
    default_agents: [researcher, planner, executor, verifier]
  marketing_campaign:
    phases: [strategy, content, launch, measure]
    default_agents: [strategist, content-creator, launcher, analyst]
  design_system:
    phases: [audit, tokens, components, documentation]
    default_agents: [auditor, token-designer, component-builder, documenter]
```

## Diferenciadores del Framework MasterMind vs GSD

| Aspecto | GSD | MasterMind Framework (propuesto) |
|---------|-----|----------------------------------|
| Dominio | Solo software dev | Cualquier nicho |
| Expert knowledge | Ninguno | 24+ brains con conocimiento destilado |
| Flujos | Fijos (research→plan→execute→verify) | Declarativos YAML, templates por nicho |
| Agentes | 12 hardcoded | Registry dinámico + brain agents |
| Verificación | Code-specific anti-patterns | Domain-agnostic, pluggable detectors |
| Checkpoints | 3 tipos fijos | Extensibles por dominio |
| Learning | Ninguno — cada sesión de cero | BRAIN-FEED acumulativo per-brain |
| Orchestration | Bash scripts | DSL declarativo |
| Context | Manual (<files_to_read>) | Manifest centralizado |
| Inter-agent | Secuencial simple | Parallel dispatch + cascade |
