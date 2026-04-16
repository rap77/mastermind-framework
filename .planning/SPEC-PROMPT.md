# Spec Prompt — MasterMind v3.0 Integration

**Este prompt está diseñado para usarse con:** `/spec` (agent-skills spec-driven-development)

**Fecha:** 2026-04-15
**Propósito:** Crear una especificación completa de MasterMind v3.0 integrando lo mejor de 5 repositorios

---

## 📋 PROMPT PARA /SPEC

```
Eres el arquitecto principal de MasterMind Framework v3.0. Tu tarea es crear una especificación técnica completa (PRD) que integre lo mejor de 5 repositorios analizados: GSD, OpenClaw, Paperclip, Agent-skills y el sistema actual de MasterMind.

## CONTEXTO DEL PROYECTO

MasterMind Framework es una arquitectura cognitiva modular para crear cerebros especializados alimentados con conocimiento destilado de expertos mundiales. Actualmente estamos en v3.0 con:

### Stack Tecnológico Actual
- **Backend (Python):** FastAPI 0.115+ + PostgreSQL + SQLAlchemy + Pydantic v2
- **Control Plane (Rust):** Axum + Tokio + SQLx + gRPC/Protobuf (Phase 15 completado)
- **Frontend (TypeScript):** Next.js 16 + React 19 + Zustand 5 + Tailwind 4 + Zod 4
- **Testing:** Pytest (818/827 tests passing), Vitest (628/628 tests passing)
- **MCP Integration:** NotebookLM (knowledge), Context7 (docs), Engram (memory)

### Estado Actual del Milestone v3.0
- **Phases 13-18:** COMPLETADAS y VERIFICADAS
- **Phase 19 (MM-Flow Completion):** Plan v4 aprobado por Brain #7 (100/100) — NADA ejecutado aún
- **Test coverage:** Python 99.0%, TypeScript 100%

## LOS 5 REPOSITORIOS A INTEGRAR

### 1. GSD (Project Management Framework)
**Lo mejor que aporta:**
- Goal-backward methodology: planes derivados del goal, no de la implementación
- Atomic commits: un commit por tarea, trazabilidad perfecta
- Wave-based parallelization: tareas agrupadas por dependencia
- Deviation Rules: Rules 1-3 auto-fix, Rule 4 checkpoint
- 3-level artifact verification: exists → substantive → wired
- Persistent state: STATE.md sobrevive /clear

**Patrones ya adoptados en Phase 19:**
- Task 2.1: --start/--complete flags (atomic commits)
- Task 3.1: Stop hook + checkpoint_writer.py
- Task 4.1: JWT auth verification gates

### 2. OpenClaw (Omnichannel Messaging Platform)
**Lo mejor que aporta:**
- 22+ messaging channels: WhatsApp, Telegram, Slack, Discord, iMessage, Signal...
- Unified session model: aislamiento por DM/group/workspace
- Local-first gateway: single control plane loopback (ws://127.0.0.1:18789)
- Enterprise ops: Tailscale Serve/Funnel, logging, model failover
- Security-first: DM pairing codes, allowlists, permission gating

**Patrones ya implementados:**
- Phase 18: 7 gateways (WhatsApp, Instagram, Email, Webhook, Google Chat, Discord, Slack)
- Rust Hub (Phase 16): WebSocket server con Tokio-tungstenite

### 3. Paperclip (Enterprise Orchestration Platform)
**Lo mejor que aporta:**
- RBAC patterns: company_id pattern para multi-tenant
- Heartbeat system: heartbeat.ts para execution engine
- ActiveAgentsPanel: ping animation, status visualization
- Enterprise monitoring: budget enforcement, audit logs

**Patrones ya implementados:**
- Phase 15: agent_registry con UNIQUE(organization_id, project_id, brain_id)
- Phase 16: Heartbeat protocol en Rust Hub

### 4. Agent-skills (Production-Grade Engineering Workflows)
**Lo mejor que aporta:**
- TDD discipline: Red-Green-Refactor, test pyramid (80/15/5), Prove-It pattern
- Code review framework: 5-axis review (correctness, readability, architecture, security, performance)
- Security patterns: OWASP Top 10 prevention, auth patterns, secrets management
- API design: Contract-first, Hyrum's Law, One-Version Rule
- Process rigor: Anti-rationalization tables, verification gates

**Disponible globalmente:**
- 51 skills instalados
- 7 slash commands: /spec, /plan, /build, /test, /review, /code-simplify, /ship
- 3 agent personas: code-reviewer, test-engineer, security-auditor

### 5. MasterMind Actual (Knowledge Distillation Engine)
**Nuestra ventaja competitiva única:**
- 7 Brain Agents con conocimiento destilado de expertos mundiales:
  - Brain #1: Product Strategy (Cagan, Torres, Perri, Ries, Doerr, Meadows)
  - Brain #2: UX Research (Norman, Nielsen, Hall)
  - Brain #3: UI Design (Cooper, Wroblewski, Saffer)
  - Brain #4: Frontend (Abramov, Markbåge, Kyle Simpson)
  - Brain #5: Backend (Fowler, Evans, Hohpe)
  - Brain #6: QA/DevOps (Humble, Majors, Feathers)
  - Brain #7: Growth/Data (Balfour, Kohani, Munger)
- NotebookLM integration: 86 libros destilados accesibles vía MCP
- Cross-brain communication: Option D (file-based: NN-BRAIN-OUTPUTS.md)
- BRAIN-FEED system: learning loop cross-session

## OBJETIVOS DE LA ESPECIFICACIÓN

### Frontend Goals
1. **Dashboard en tiempo real:** Monitoreo de 7 brain agents con live updates (WebSocket)
2. **ActiveAgentsPanel:** UI inspirada en Paperclip con ping animation, status visualization
3. **Canvas UI (A2UI):** Agent-to-User Interface para interactuar con los brains
4. **Multi-tenant workspace:** Switch entre organizaciones/proyectos
5. **Real-time collaboration:** Broadcast de eventos (brain_started, brain_completed, brain_failed)

### Backend Goals
1. **DynamicDispatchEngine:** Reemplazar brain_router.py con sistema tipo GSD
2. **JWT Auth + RBAC:** Migrar FastAPI JWT → Rust middleware con agent_registry
3. **Audit Trail:** activity_log inmutable con Depends(get_current_user_any) en 13 endpoints
4. **Budget Enforcement:** Límites de tokens/costos por sesión (prevenir sorpresas)
5. **Adapter Registry:** Dynamic routing a gateways (WhatsApp, IG, Email, etc.)

### Functional Goals
1. **MM-Flow Completion:** 4 fases planificadas (Infrastructure, CLI Bridge, Context, Audit)
2. **CLI ↔ Skills Bridge:** Wire /mm:execute-phase y /mm:plan-phase con CLI bookends
3. **Context Persistence:** Checkpoint system con write-tool-call detection
4. **Statusline Extension:** EXTENDER mm-flow-statusline.js (no reemplazar)
5. **Multi-channel Gateway:** 7 canales ya implementados, añadir voice capabilities

## ARQUITECTURA PROPUESTA (5 Layers)

```
LAYER 1: Knowledge & Expertise (MasterMind)
  └─ 7 Brain Agents + NotebookLM + 86 libros destilados

LAYER 2: Process & Engineering (Agent-skills)
  └─ /spec → /plan → /build → /test → /review → /ship

LAYER 3: Project Management (GSD)
  └─ Goal-backward + Atomic Commits + Waves

LAYER 4: Execution Engine (Paperclip patterns)
  └─ DynamicDispatchEngine + Heartbeat + Checkpoints

LAYER 5: Infrastructure (OpenClaw patterns)
  └─ Rust Control Plane + WS Hub + Gateways
```

## PHASE 19 - MM-FLOW COMPLETION (Plan v4 Aprobado)

### FASE 1 - Infrastructure Foundation
**Task 1.1:** ✅ PostgreSQL levantado (docker compose up -d postgres)
**Task 1.2:** Aplicar audit trail SQL (docker/postgres/mm-flow-audit.sql)
**Task 1.3:** Verificar seed data (workspaces con current_phase)
**Task 1.4:** Crear agent_registry + seed 7 brains con UNIQUE(org, project, brain)
**Task 1.5:** Crear config.yml loader + model profiles (quality/balanced/budget)

### FASE 2 - CLI ↔ Skills Bridge
**Task 2.1:** --start/--complete flags en mm-flow execute-phase
**Task 2.2:** DynamicDispatchEngine con DispatchResult Pydantic v2 strict
**Task 2.3:** Wire skills /mm:execute-phase y /mm:plan-phase con CLI bookends

### FASE 3 - Context Persistence
**Task 3.1:** Stop hook mm-flow-stop.js + checkpoint_writer.py (Python, testeable CI)
**Task 3.2:** Modificar mm-flow-session-init.js → stale checkpoint detection (>48h)
**Task 3.3:** Extender mm-flow-context-monitor.js → write-tool-call detection
**Task 3.4:** Fix context_loader flow (skill genera CONTEXT.md via mem_search)

### FASE 4 - Audit Trail + Statusline
**Task 4.1:** Depends(get_current_user_any) en 13 endpoints audit.py + 26 tests + CI gate
**Task 4.3:** Crear ~/.claude/backends.sh (credentials loader)
**Task 4.4:** EXTENDER mm-flow-statusline.js (preservar líneas 24-43, agregar phase state)

## SUCCESS CRITERIA

### Frontend Success Criteria
- [ ] Dashboard muestra 7 brain agents con status en tiempo real (WebSocket)
- [ ] ActiveAgentsPanel con ping animation funcional
- [ ] Multi-tenant workspace switch implementado
- [ ] Canvas UI (A2UI) permite interacción con brains
- [ ] Real-time collaboration: brain_started/completed/failed broadcasts funcionan
- [ ] TypeScript tests: 628/628 passing (100%)

### Backend Success Criteria
- [ ] DynamicDispatchEngine reemplaza brain_router.py
- [ ] JWT auth migrado a Rust middleware con agent_registry RBAC
- [ ] Audit trail: 13 endpoints con Depends(get_current_user_any) + 26 tests passing
- [ ] Budget enforcement: token quotas por sesión funcionando
- [ ] Adapter registry: dynamic routing a 7 gateways + fallback
- [ ] Python tests: 818/827 passing (99.0%+)

### Functional Success Criteria
- [ ] Phase 19 FASE 1 completada (infrastructure foundation)
- [ ] Phase 19 FASE 2 completada (CLI ↔ Skills bridge)
- [ ] Phase 19 FASE 3 completada (context persistence)
- [ ] Phase 19 FASE 4 completada (audit trail + statusline)
- [ ] /mm:execute-phase y /mm:plan-phase wireados con CLI bookends
- [ ] Checkpoint system con write-tool-call detection funcional
- [ ] mm-flow-statusline.js extendido con phase state + active brain status

### Integration Success Criteria
- [ ] Agent-skills workflows funcionan con Brain Agents:
  - Brain #1 + spec-driven-development
  - Brain #4 + frontend-ui-engineering
  - Brain #5 + api-and-interface-design
  - Brain #6 + test-driven-development
  - Brain #7 + code-review-and-quality
- [ ] /review después de cada /mm:complete-phase funciona
- [ ] GSD patterns (atomic commits, waves, verification) integrados
- [ ] OpenClaw patterns (gateway unificado, session management) funcionan
- [ ] Paperclip patterns (RBAC, heartbeat) verificados en producción

## ARCHIVOS CLAVE DE REFERENCIA

### Documentación de Planeación
- `.planning/STATE.md` — Estado global del milestone v3.0
- `.planning/.continue-here.md` — Estado actual de Phase 19
- `.planning/MM-FLOW-COMPLETION-PLAN.md` — Plan v4 aprobado
- `.planning/research/FIVE-REPOS-SYNTHESIS.md` — Análisis de 5 repositorios

### Análisis de Repositorios
- `.planning/research/GSD-FRAMEWORK-ANALYSIS.md`
- `.planning/research/OPENCLAW-ANALYSIS.md`
- `.planning/research/FEATURES.md` (Paperclip patterns)

### Implementación Actual
- `apps/api/` — FastAPI backend (631+ tests)
- `apps/web/` — Next.js 16 frontend (407 tests)
- `rust_control_plane/` — Rust Axum control plane
- `apps/api/routers/audit.py` — 1593 líneas, 13 routes sin JWT (FASE 4)
- `~/.claude/hooks/mm-flow-statusline.js` — 74 líneas, EXTENDER (FASE 4)

## INSTRUCCIONES PARA LA ESPECIFICACIÓN

Usa el formato de spec-driven-development:

1. **Objective** — Qué estamos construyendo y por qué
2. **Tech Stack** — Frameworks, lenguajes, dependencias clave
3. **Commands** — Comandos ejecutables (build, test, lint, dev)
4. **Project Structure** — Layout de directorios
5. **Code Style** — Ejemplo de código + convenciones
6. **Testing Strategy** — Framework, ubicación, coverage, test levels
7. **Boundaries** — Always/Ask First/Never
8. **Success Criteria** — Condiciones testables de "done"
9. **Open Questions** — Qué falta resolver

## OUTPUT ESPERADO

Una especific completa (PRD) que incluya:

1. **Especificación de Phase 19 completa** con las 4 fases detalladas
2. **Frontend spec** para Dashboard, ActiveAgentsPanel, Canvas UI
3. **Backend spec** para DynamicDispatchEngine, JWT auth, Audit trail
4. **Integration spec** para CLI ↔ Skills bridge, Context persistence
5. **Success criteria** verificables para cada fase
6. **Dependencies** entre fases y tareas
7. **Risks y mitigation strategies**
8. **Testing strategy** para cada componente
9. **Deployment strategy** para cada fase
10. **Rollback procedures** si algo falla

---

## NOTA FINAL

Esta especificación debe ser lo suficientemente detallada para que:
- El equipo pueda implementar Phase 19 sin ambigüedades
- Los tests puedan verificar que cada criterio de éxito se cumple
- El code review (usando /review + agentes code-reviewer/test-engineer/security-auditor) pueda validar calidad
- El deployment sea incremental y seguro (una fase a la vez)

Recuerda: MasterMind v3.0 = Lo mejor de 5 mundos, pero nuestra ventaja competitiva ÚNICA es el Knowledge Distillation Engine con 7 brain agents. Todo lo demás (GSD, OpenClaw, Paperclip, Agent-skills) son COMMODITIES. La especificación debe reflejar esto.
```

---

## 🚀 CÓMO USAR ESTE PROMPT

### Paso 1: Ejecutar /spec
```bash
cd /home/rpadron/proy/mastermind
/spec < COPIAR EL PROMPT DE ARRIBA >
```

### Paso 2: Revisar la spec generada
- ¿Cubre todos los objetivos?
- ¿Los success criteria son medibles?
- ¿Los risks están identificados?

### Paso 3: Iterar con /plan
```bash
/plan < DE LA SPEC GENERADA >
```

### Paso 4: Ejecutar con /build
```bash
/build < TASK DEL PLAN >
```

### Paso 5: Verificar con /test
```bash
/test < COMPONENTE A PROBAR >
```

### Paso 6: Revisar con /review
```bash
/review < CAMBIOS IMPLEMENTADOS >
```

---

## 📋 CHECKLIST DE VALIDACIÓN

Antes de considerar la spec completa, verificar:

- [ ] Phase 19 tiene 4 fases claramente definidas
- [ ] Cada fase tiene tasks con acceptance criteria
- [ ] Frontend goals están especificados (Dashboard, ActiveAgentsPanel, Canvas UI)
- [ ] Backend goals están especificados (DynamicDispatchEngine, JWT, Audit)
- [ ] Functional goals están especificados (MM-Flow, CLI Bridge, Context)
- [ ] Success criteria son medibles y testables
- [ ] Testing strategy está definida para cada componente
- [ ] Deployment strategy es incremental (fase por fase)
- [ ] Rollback procedures están documentados
- [ ] Integration con 5 repositorios es clara
