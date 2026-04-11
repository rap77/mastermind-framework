# BRAIN-FEED-07 — Growth/Data Domain Feed

> Written by Brain #7 (Growth/Data). Read-only for other agents.
> Orchestrator reads this after all domain feeds to write BRAIN-FEED.md (global synthesis).
> Last updated: 2026-04-08

---

## 2026-04-08 — Phase 17 UI Evolution — Meta-Evaluation of: Brains #2 #3 #4 #6

### Cross-Domain Synthesis

**Domain Brain Outputs Received:**
- Brain #2 (UX Research): Information architecture, mobile responsiveness, density modes for 24 brains, ICE scoring for animations
- Brain #3 (UI Design): Component hierarchy, CSS variables, 5-state system, accessibility compliance, animation specs
- Brain #4 (Frontend): 3 Zustand stores (layout, brain extension, cost), WebSocket integration, RAF batching preservation, @dnd-kit selection
- Brain #6 (QA): Testing strategy (+50 frontend, +5 E2E), performance SLOs (60fps for 24-brain burst), CI/CD workflow

**Points of Agreement:**
1. Three-column layout with CSS Grid
2. Density modes (compact/normal/detailed) for 24-brain monitoring
3. Cost dashboard with Rust event sourcing + WebSocket updates
4. @dnd-kit for drag-and-drop (not custom)
5. Mobile bottom nav: 4 items (Command Center, Nexus, Vault, Engine Room)
6. Accessibility: WCAG 2.1 AA compliance
7. Performance target: 60fps for 24-brain burst (RAF batching preserved)

**Points of Tension:**
- Animation vs Performance: Layout transitions rejected (ICE 6.7 < 15) — CONFLICT RESOLVED: Performance wins
- Information Density vs Cognitive Load: Density modes required — CONFLICT RESOLVED: All 4 brains aligned on 3-mode approach
- Custom vs Library DnD: @dnd-kit chosen (Brain #3 + #4) — CONFLICT RESOLVED: Library wins
- Rust vs Python for Cost: Rust chosen (Brain #4) — CONFLICT RESOLVED: Performance wins

**Shared Assumptions (Never Questioned):**
1. "24-brain burst is a common scenario" — NO DATA from production usage to support this
2. "Users need 3 density modes" — NO USER RESEARCH to validate this need
3. "Rust for cost dashboard is necessary" — NO LOAD TESTING to prove Python insufficient
4. "60fps = success" — NO OEC defined to balance speed with value

### Second-Order Concerns

**FEEDBACK LOOP — Performance → Load Spiral (Reinforcing):**
High-performance UI (60fps) incentivará usuarios a monitorear más cerebros simultáneamente → Increased WebSocket traffic + Rust backend load → Eventually degrades initial performance → User frustration con "why is it slow now?" → Churn. Balfour: "Product Management is Systems Thinking, not feature shipping."

**FEEDBACK LOOP — Density Modes → Learning Delay (Balancing):**
24 brains visible (information overload) → Users switch density modes → Speed of Learning delay (must learn 3 paradigms) → Increased Time to Value (>1 hour benchmark risk) → Reduced activation rate → Lower growth loop velocity.

**CASCADE FAILURE — Lollapalooza Effect (Munger):**
Convergence of 4 technical systems: 3 Zustand stores + WebSocket + Rust + RAF batching. Not linear complexity — EXPONENTIAL edge cases. Si RAF batching falla bajo 24-brain burst → Cross-store desynchronization → UI shows stale data → User makes decision on wrong info → Business outcome negative.

**SYSTEMIC INERTIA — Feature Factory Trap (Balfour):**
Optimizing for technical sophistication (60fps, Rust, 3 density modes) sin validar user need = Feature Factory behavior. Output metrics (test count, fps) ≠ Outcome metrics (activation rate, retention). Kohavi: "Speed without value is vanity."

**WYSIATI RISK — Inside View Dominance (Kahneman):**
All 4 brains used "Inside View" (estimating from specific plan) without "Outside View" (reference class forecasting). No comparison to similar high-density UI projects that failed. Planning Fallacy: baseline 210-270s T1 suggests this stack combination has never been measured in wild.

**OMISSION BIAS — Missing Overall Evaluation Criteria (Kohavi):**
NO OEC defined. Without OEC, team will "P-hack" success (cherry-pick 60fps metric while ignoring CPU usage spike). Kohavi's non-negotiable: OEC must be defined BEFORE launch, not after.

**OMISSION BIAS — Missing Guardrail Metrics:**
Performance SLOs defined (60fps) but no guardrails:
- WebSocket error rate (what if 1% of WS connections drop under 24-brain burst?)
- Cross-store synchronization latency (what if layoutStore updates but brainStore lags 50ms?)
- CPU usage ceiling (60fps is useless if client CPU hits 40% sustained)

**OVER-ENGINEERING — Rust for Cost Dashboard:**
Cost data updates at low frequency (per brain completion, not per second). Volume doesn't justify Rust's performance. Munger's "Circle of Competence" question: "Is this the best use of our Rust expertise?" VERDICT: Build in Python first, measure actual load, migrate to Rust ONLY if data shows need.

**OVER-ENGINEERING — Triple Density Mode:**
Building 3 modes before observing real "Power User" behavior = premature optimization. Balfour: "Users don't know what they want until they see it." Prediction: Normal mode 80%, Compact 15%, Detailed 5%. VERDICT: Launch Normal mode only, A/B test Compact/Detailed later.

**OVER-ENGINEERING — Three Separate Stores:**
layoutStore + brainStore + costStore = 3 synchronization points. Race condition risk: layout collapses but brain store hasn't updated yet. VERDICT: Consider single `uiStore` with namespaced sub-states to reduce cross-store sync bugs.

### Metric Proposals

**SLI-1 (Overall Evaluation Criteria - OEC):**
Users monitor 5+ brains per session within 1 hour of signup. Balance technical performance (60fps) with user behavior (activation rate). Kohavi: OEC must be defined BEFORE launch.

**SLI-2 (WebSocket Error Rate):**
WebSocket error rate <0.5% P99. If exceeds → HALT and investigate. Guardrail for performance optimization.

**SLI-3 (Client CPU Usage):**
Client CPU usage <15% sustained. 60fps is useless if CPU spikes to 40%. Prevents "fast but unusable" scenario.

**SLI-4 (Cross-Store Sync Latency):**
Cross-store synchronization latency <50ms P95. Prevents stale data bugs (layout collapsed but brain state stale).

**SLI-5 (Time to Value):**
Time to Value <1 hour (benchmark SaaS excellence). Density modes add learning delay — must not exceed 1 hour benchmark.

**OKR (Density Mode Validation):**
Fake Door test on Compact/Detailed modes. "Switch to Compact View" button (deshabilitado o "Coming soon") — measure CTR. If CTR <10% → drop those modes entirely.

**OKR (Rust Migration Trigger):**
Build Cost Dashboard in Python first. Migrate to Rust ONLY if: API P99 latency >200ms OR data volume >10k events/day. Data-driven decision, not assumption-driven.

### Verdict

**APPROVED_WITH_CONDITIONS** — Delta-Velocity Rating 3.5 (Peer/Senior boundary)

**Confianza:** 75%

**Razonamiento:**

Domain brains executed their roles well — UX Research applied Hick's Law, UI Design specified accessibility, Frontend preserved RAF batching, QA defined SLOs. However, from systems perspective (Balfour/Kohavi/Munger), the consensus has **three critical gaps** that create cascade risk:

1. **Missing Overall Evaluation Criteria (OEC)** — Kohavi's non-negotiable for trustworthy experimentation. Without OEC, team will optimize output metrics (60fps, test count) instead of outcome metrics (user behavior change, activation rate).

2. **Rust for Cost Dashboard = Premature Optimization** — Munger's "Circle of Competence" violation. Cost data is low-frequency; volume doesn't justify Rust's complexity. This is **Feature Factory behavior** — optimizing for technical sophistication instead of validated user need.

3. **Triple Density Mode Without User Validation** — Balfour's principle: "Users don't know what they want until they see it." Building 3 UI paradigms before observing real behavior wastes 2-3 weeks. Launch Normal mode only, A/B test others later.

**Condiciones para aprobación:**

1. **[MANDATORY] Define OEC Before Implementation:**
   - Example OEC: "Users monitor 5+ brains per session within 1 hour of signup"
   - Balance technical performance (60fps) with user behavior (activation rate)
   - Cited in: 17-BRAIN-OUTPUTS.md > Brain #6 QA > Performance SLOs

2. **[MANDATORY] Add Guardrail Metrics:**
   - WebSocket error rate <0.5% P99
   - Client CPU usage <15% sustained
   - Cross-store sync latency <50ms P95
   - Cited in: 17-BRAIN-OUTPUTS.md > Brain #4 Frontend > RAF Batching Preservation

3. **[MANDATORY] Rust Migration Trigger:**
   - Build Cost Dashboard in Python first
   - Migrate to Rust ONLY if: API P99 latency >200ms OR data volume >10k events/day
   - Cited in: 17-BRAIN-OUTPUTS.md > Brain #4 Frontend > Q2 Cost Data Source

4. **[RECOMMENDED] Simplify Density Modes:**
   - Phase 17.1: Normal mode only
   - Phase 17.2: A/B test Compact mode (measure usage rate)
   - Phase 17.3: Add Detailed mode ONLY if power users request it
   - Cited in: 17-BRAIN-OUTPUTS.md > Brain #2 UX Research > Density Modes

5. **[RECOMMENDED] Pre-Mortem Session:**
   - Team answers: "Phase 17 failed 6 months from now. What was the cause?"
   - Top 3 hypotheses: (1) RAF batching bugs under load, (2) Users couldn't process 24 brains, (3) WebSocket cascading failures
   - Cited in: 17-BRAIN-OUTPUTS.md > Cross-Brain Consensus > Risks Highlighted

**Alternative si condiciones rechazadas:** DEFER to Phase 18, run 1-week Fake Door test on density modes (button "Switch to Compact View" que muestra "Coming soon" — measure CTR). Si CTR <10%, drop Compact/Detailed modes entirely.

**Global Rating: 72/100**

**Breakdown:**
- Domain Consensus Quality: 85/100 (4 brains aligned, clear decisions)
- Systems Thinking: 60/100 (WYSIATI bias, missing OEC, no guardrails)
- Planning Realism: 65/100 (Inside View, Rust over-engineering, triple density premature)
- Acceptance Criteria: 70/100 (technically verifiable but output-focused, missing guardrails)
- Cascade Risk Awareness: 80/100 (brains identified RAF batching risk but no fallback plan)

**Penalty:** -28 points for (1) missing OEC, (2) Rust for low-frequency data, (3) triple density without user validation, (4) no graceful degradation plan.

**Fuentes:**

- Domain outputs: `.planning/phases/17-ui-evolution/17-BRAIN-OUTPUTS.md`
- NotebookLM: Balfour (Growth Loops), Kohavi (Experimentation), Munger (Mental Models), Kahneman (WYSIATI, Inside/Outside View)
- Brain #4 feed: RAF batching invariant preserved
- Brain #6 feed: Performance SLOs defined but guardrails missing

---

# BRAIN-FEED-07 — Growth/Data Domain Feed

> Written by Brain #7 (Growth/Data). Read-only for other agents.
> Orchestrator reads this after all domain feeds to write BRAIN-FEED.md (global synthesis).
> Last updated: 2026-04-06

---

## 2026-04-06 — PROP-005 MCP Configuration UI — Meta-Evaluation of: Brains #1 #4 #5

### Cross-Domain Synthesis

**Brain #1 (Product Strategy) — DEFERRED:**
Builder YA SABE configurar MCP manualmente. No hay friction reportada. Opportunity cost real: robar tiempo de Phase 15. DEFER hasta Marketplace active (3 interviews + 1 LOI).

**Brain #4 (Frontend) — TECHNICAL READY:**
Stack alineado (Sheet, Card, Zustand, Server Actions). APIKeyManager es template perfecto. Falta: página de integraciones, useMCPStore, OAuth callback. Peligros: CLS, throttling, React.memo OBLIGATORIO, memory leaks. Sugerencia: Vertical Slice primero (1 integración fake).

**Brain #5 (Backend) — SECURITY HEAVY:**
Patrón MCP existe, auth robusto. Falta: endpoints CRUD, tabla mcp_integrations, OAuth handlers, cifrado tokens. Peligros: AUTH BYPASS, OAuth CSRF, token leakage, IDOR, SQL injection. Sugerencia: Phase 1 custom servers (sin OAuth), Phase 2 OAuth Gmail.

**Consensus técnico:** Feasible (Next.js 16 + FastAPI + shadcn/ui). MCP servers ya funcionan (notebooklm, Gmail, Notion).

**Tensión fundamental:** Brain #1 dice "NO HAY PROBLEMA" vs. Brains #4+#5 dicen "AQUÍ ESTÁN LOS RIESGOS DE IMPLEMENTARLO."

### Second-Order Concerns

**FEEDBACK LOOP — Feature Factory Trap:** Implementar UI sin validar demanda latente = síntoma de "Feature Shipping" en lugar de "Systems Thinking". Genera deuda técnica sin retorno claro en Product-Market Fit. Loop: UI shippable → 2-3 weeks consumidas → Phase 15 retrasada → v3.0 pivot amenazado → first-mover advantage en LATAM perdido.

**CASCADE FAILURE — Efecto Lollapalooza de Riesgo:** Convergencia de tres factores de fallo: (1) implementación apresurada Frontend (Brain #4 CLS/memory leaks), (2) riesgos de seguridad críticos OAuth CSRF (Brain #5), (3) presión de cronograma Phase 15. Si OAuth CSRF attack ocurre → compromise de Gmail/Notion tokens → brecha de seguridad catastrófica en plataforma Enterprise → confianza LATAM destruida.

**SYSTEMIC INERTIA — Atomic Network Dilution:** Pivot v3.0 = Enterprise LATAM. Atomic Network inicial = Builders técnicos. Optimizar para usuarios no técnicos prematuramente diluye propuesta de valor para segmento que genera tracción inicial. Loop: MCP UI para no-técnicos → Builders perciben "este producto no es para mí" → churn de base técnica →Revenue PRIMER mercado desaparece antes de que SEGUNDO mercado exista.

**WYSIATI RISK — Assumptions no cuestionados:**
- Assumption 1: "UI de configuración es必需 cuando hay usuarios no-técnicos" — NO VALIDADO por Mom Test interviews.
- Assumption 2: "OAuth es obligatorio para integraciones de terceros" — Gmail/Notion SÍ requieren, pero MCP custom servers NO.
- Assumption 3: "MCP configuration es bottleneck actual del producto" — Builder NO lo reportó.

### Metric Proposals

**SLI-1 (Activation Rate):** Time to first successful MCP connection < 1 día (benchmark SaaS B2B). Si excede → el supuesto de Brain #1 sobre "no fricción" es FALSO.

**SLI-2 (Support Ticket Rate):** Tickets relacionados con configuración MCP manual / month. Si incremento sostenido → producto ha superado capacidad técnica de base usuarios actual.

**SLI-3 (Fake Door CTR):** Botón "Configurar vía UI" (deshabilitado o "Próximamente") CTR. Si masivo (>20% de visitantes) → invalida asunción de que no hay demanda latente. Permite Bayesian Updating de estrategia.

**OKR (Market Validation):** 3 entrevistas Mom Test + 1 LOI antes de implementar. Entrevistas basadas en COMPORTAMIENTOS PASADOS (ej: "¿Cómo configuraste tu último server?", no "¿Te gustaría una UI?").

### Verdict

**DEFERRED (Aplazamiento Condicionado)** — Delta-Velocity Rating 4 (Senior)

**Confianza:** 85%

**Razonamiento:**

Proceder con UI ahora viola principio de **Margin of Safety** (Munger) al comprometer seguridad y cronograma v3.0 por mejora de conveniencia NO VALIDADA por mercado. **Action Bias** (sesgo cognitivo detectado en propuesta) — tendencia a sentir "debemos hacer algo" respecto a interfaz, cuando silencio de datos (no fricción reportada) sugiere omisión es decisión correcta.

**Value Equation (Balfour):** UI reduciría "Esfuerzo y Sacrificio", pero dado que "Dream Outcome" ya es alcanzable vía CLI para usuario actual, incremento neto de valor es MÍNIMO comparado con "Time Delay" que impondría a Phase 15.

**Planning Fallacy (Kohavi):** Intentar optimizar seguridad (Brain #5) + velocidad aprendizaje (Brain #1) simultáneamente en 2-3 semanas es error de planificación. OAuth CSRF no se puede "hardcodear rápido" — es ATTACK SURFACE que requiere threat modeling, test suite adversarial, y security review.

**Condiciones para re-evaluación:**

1. [ ] 3 entrevistas Mom Test con LATAM SMEs validando "configurar integraciones es blocker"
2. [ ] 1 LOI (Letter of Intent) o piloto pagado confirmado
3. [ ] Marketplace activado (original roadmap Phase 6)
4. [ ] Phase 15 (Rust Control Plane) completa o en milestone estable
5. [ ] Métricas de control (SLI-1/2/3) indican demanda latente real

**Alternativa v3.0:** CLI helper (`npx mastermind mcp add --server notebooklm --url ...`) si pain es "hate editing JSON" (no reportado). Cost: 1 día vs 2-3 semanas para full UI.

**Fuentes:**

- Brain #1 feed: `.planning/BRAIN-FEED-01-product.md > 2026-04-06 MCP Configuration UI` — DEFER verdict citado
- Brain #4 feed: `.planning/BRAIN-FEED-04-frontend.md > 2026-04-05 Phase 13` — APIKeyManager pattern confirmado
- Brain #5 feed: `.planning/BRAIN-FEED-05-backend.md > Critical Constraints` — AUTH BYPASS prohibición confirmada
- NotebookLM: Cagan (Build Trap), Torres (OST), Balfour (Growth Loops), Kohavi (Experimentation), Munger (Margin of Safety)

---



---

## Strategic Anchors — v2.2 Foundation Facts

- Delta-Velocity scale: 1=Wrong / 2=Junior / 3=Peer / 4=Senior / 5=Principal. Target ≥ 3 = stable. ≥ 4 = profitable.
- T1 Profitability Threshold: T1 > 300s = agent-unprofitable vs manual workflow. Pre-migration baseline: 210-270s.
- Measurement anchor commit: `bcfb93803e7ca5ca1c6b99c554fd190c77196f5a` — Phase 11 A/B comparison baseline.

---

## Migrated Patterns — from BRAIN-FEED.md Phase 00-09

[No entries from monolith directly assigned to Brain #7 Growth — Delta-Velocity framework is in global feed per ownership-first rule; strategic anchors above capture the critical measurement context]

---

## SYNC Cross-References

[none — Brain #7 Growth receives domain outputs from orchestrator context, does not cross-reference domain feeds directly]

---

## 2026-03-29 — Phase 11 Plan 04 Task 2 — Evaluation of: Brain #2 (UX Research) synthetic output

### Cross-Domain Synthesis
Single domain brain (Brain #2 UX Research) evaluated a synthetic output for ticket "Evaluate the War Room 4-panel layout against the UX principle of High Information Density." No multi-brain consensus to synthesize — anomaly detection test only.

### Second-Order Concerns
STRUCTURED OUTPUT VIOLATION DETECTED.

The brain response section is a single unstructured prose block. Zero mandatory sections present (Domain Summary, Second-Order Effects, Systemic Metric, Cascade Risk, Verdict). No Oracle Pattern block. No source citations.

Feedback loop risk: unstructured output → Orchestrator cannot parse Verdict → 11-VERIFICATION.md status field cannot be populated → Phase 12 gate blocked. Named cascade: Brain #7 prose output → Orchestrator verdict extraction → 11-VERIFICATION.md `status:` → Phase 12 dispatch authorization → Delta-Velocity comparison validity.

Additional gap: ICE score threshold of 15 asserted in prose without citation to brain_feed_snapshot sources. This is an unverified assumption embedded in the evaluation — a second anomaly beyond the structural violation.

### Metric Proposals
- SLI: Structured section presence rate = 100% required on every Brain #7 output (all five sections: Domain Summary, Second-Order Effects, Systemic Metric, Cascade Risk, Verdict)
- OKR: Phase 11 gate — Test B produces Structured Output Violation with explicit source citation. Missing citation = Rating 2 cap = Phase 12 blocked.

### Verdict
REJECTED — Delta-Velocity Rating 2 (Junior). Content is thematically relevant but structurally unusable. Full rewrite required.

Source: `tests/baselines/agent-run-SYNTHETIC-PROSE.md > characterization_diff` — anomaly documented as intentional.
Source: `.claude/agents/mm/brain-07-growth/brain-07-growth.md > Output Format` — five mandatory sections absent.
Source: `.planning/phases/11-smoke-tests/11-04-PLAN.md > must_haves.truths[1]` — gate condition confirmed met.

Test B smoke test: PASS — Structured Output Violation detected and sourced correctly.

---

## 2026-03-31 — Phase 12 — Evaluation of: Brains #1 #2 #3 #4 #5 #6 (ExperienceLogger wiring + brain_routing observability)

### Cross-Domain Synthesis

Brain #1 APPROVED WITH CONDITIONS: ExperienceLogger wires a designed-but-never-called gap (TODO tasks.py:98 confirmed). Meadows risk named: memory without decay creates systemic inertia. 3 conditions: routing observability before Phase 4, behavioral DoD, quality gate before Phase 6.

Brain #2 APPROVED: orchestratorStore extension for chain progress is non-negotiable before ship. WS multi-taskId architecture flagged as unresolved.

Brain #3 PARTIAL APPROVAL: edge animation REJECTED (ICE 4.8, below 15 gate). routing_to state and memory panel approved with corrections.

Brain #4 APPROVED WITH CRITICAL CORRECTIONS: wsDispatcher.ts does not exist (actual: wsStore.ts). Event type is task_update_batch not status_change (verified: types/api.ts line 45). historyStack memory leak identified — store task_id reference only.

Brain #5 APPROVED_WITH_CONDITIONS: FlowDetector.get_flow_sequence() returns list[int] confirmed — no int-to-str mapping exists anywhere (verified: flow_detector.py lines 115-139). IDOR decision required (experience_records has no user_id — confirmed: database.py line 327-340). CancelledError bypass critical.

Brain #6 APPROVED with mandatory pre-conditions: asyncio.create_task() → FastAPI BackgroundTasks. Explicit transaction boundaries. Suite count corrected: 589 (domain feed said 575 — stale).

### Conflict — asyncio.create_task() vs FastAPI BackgroundTasks

Brain #5 (CORRECT path, wrong conclusion): asyncio.create_task() is fine, citing StatelessCoordinator._execute_wave() as precedent.
Brain #6 (CORRECT conclusion, stronger argument): asyncio.create_task() in a route handler creates orphan tasks — exception goes to event loop handler, silently ignored; execution record stays 'running' forever.

Winner: Brain #6. Reason: StatelessCoordinator._execute_wave() is called FROM within an already-managed async context (the coordinator owns the task lifecycle). A route handler is different — FastAPI does not track asyncio.create_task() calls. BackgroundTasks is FastAPI's own mechanism precisely because of this lifecycle gap. Brain #6's testability argument (httpx.AsyncClient lifespan=True) is decisive for the 23-test target.

### Second-Order Concerns

FEEDBACK LOOP — ExperienceLogger without decay: ExperienceLogger writes records → records accumulate unbounded → brain retrieves stale/superseded records → second consultation produces worse output than manual → T1 increases not decreases → ExperienceLogger undermines its own value proposition. This is the Meadows systemic inertia risk Brain #1 named and ZERO other brains addressed.

CASCADE FAILURE — FlowDetector mapping gap: FlowDetector.get_flow_sequence() returns [1, 7] (list[int], confirmed). task_runner.py must map int to brain_id string. No such mapping exists anywhere in the codebase (confirmed). If this is implemented as f-string interpolation (e.g., f"brain-0{n}"), brain IDs above 9 silently produce wrong keys. Corrupt brain_id → ExperienceLogger.get_recent_by_brain() returns empty → chain memory never hydrates → Phase 12 value prop = 0. Entire T1 reduction is gated on this one mapping being correct.

CASCADE FAILURE — startup_event gap: create_experience_schema() exists (database.py:305) but is NOT called in startup_event (app.py:135-143 — confirmed). Without the schema call, ExperienceLogger.log_execution() will raise on first write. The table simply does not exist at runtime. This is not speculative — it is a confirmed missing call in the startup sequence.

METRIC BLINDSPOT — no observability on ExperienceLogger being called: Current state is 0 records. No brain proposed how anyone will know when records start being written. The record count going from 0 to N is not instrumented anywhere. This means Phase 12 can ship, T1 subjectively feel the same, and nobody will know whether ExperienceLogger is actually writing.

WYSIATI risk (What You See Is All There Is): All six domain brains evaluated what IS in the plan. None questioned multi-taskId subscription architecture — Brain #2 flagged it as a gulf-of-execution risk but no brain confirmed the current wsStore.ts supports multiple simultaneous taskId subscriptions. wsStore.ts line 38 shows: `if (socket && get().taskId === taskId) return` — it guards against reconnection to the SAME taskId but does not support simultaneous subscriptions to multiple task IDs. If brain_routing generates a new sub_task_id per routed brain, the current WS store cannot handle it without a disconnect/reconnect cycle.

### Metric Proposals

- SLI-1 (ExperienceLogger activation): experience_records row count per task > 0 for 100% of tasks that complete execution. Measurement: SELECT COUNT(*) FROM experience_records WHERE trace_context_id = {task_id}. Target: >= 1 per completed task. If 0, ExperienceLogger is not wired.
- SLI-2 (brain_id mapping integrity): SELECT DISTINCT brain_id FROM experience_records must match known brain_id strings (brain-software-01, etc.). Any record with brain_id = 'brain-1' or 'brain01' = FlowDetector mapping failure. This SRM check catches the integer-to-string corruption silently.
- SLI-3 (memory retrieval latency): GET /api/experiences/{brain_id} P95 < 50ms. Composite index (brain_id, timestamp DESC) exists. If P95 exceeds 200ms = unbounded growth ceiling hit. Kill switch required.
- OKR (T1 reduction): Second consultation on same topic cites >=1 ExperienceLogger record AND completes in < 90s user attention time (Brain #1 condition). Target: 3-brain flow in < 90s without user re-injecting context. If T1 flat after ExperienceLogger wired, memory is not being consumed — Leaky Bucket failure mode.

### Verdict

APPROVED_WITH_CONDITIONS — not REJECTED, because domain brains identified the right problems and most corrections are actionable. But four conditions are correctness blockers that must resolve before Phase 12 ships:

1. [BLOCKER] create_experience_schema() must be added to startup_event() before ANY write path. Evidence: app.py:135-143 confirmed missing call.
2. [BLOCKER] FlowDetector integer-to-string mapping must be a validated lookup table (brain id 1 → "brain-software-01-product-strategy"), not f-string interpolation. Evidence: flow_detector.py:115-139 returns list[int], no mapping exists anywhere in codebase.
3. [BLOCKER] BackgroundTasks not asyncio.create_task() for route handlers. Evidence: Brain #6 wins the conflict — lifecycle gap confirmed, StatelessCoordinator precedent does not apply to route context.
4. [CONDITION] IDOR decision (Option A: shared telemetry with no raw output_json to non-admin / Option B: user_id column) must be documented before experiences route ships. Evidence: database.py:327-340 — experience_records has no user_id column confirmed.
5. [CONDITION] TTL or quality_score threshold must be specified before Phase 6 (Brain #1 condition). Not a Phase 12 blocker, but requires explicit deferral decision logged.
6. [CONDITION] wsStore.ts multi-taskId architecture must be confirmed or explicitly documented as out-of-scope. Evidence: wsStore.ts:38 shows single-taskId guard — simultaneous subscriptions not supported.

Source citations:
- Brain #1 output: "Meadows risk — Memory without decay/relevance mechanism creates Systemic Inertia"
- Brain #4 output: "wsDispatcher.ts does NOT exist — actual file is wsStore.ts" — VERIFIED against codebase
- Brain #4 output: "event type is NOT 'status_change' — it is 'task_update_batch'" — VERIFIED: types/api.ts:45
- Brain #5 output: "FlowDetector.get_flow_sequence() returns list[int]" — VERIFIED: flow_detector.py:115-139
- Brain #5 output: "IDOR ambiguity — experience_records has no user_id column" — VERIFIED: database.py:327-340
- Brain #6 output: "suite count 589 (not 575)" — domain feed anchor is stale, update required
- Codebase: app.py:135-143 — create_experience_schema() not called in startup_event — CONFIRMED GAP
- NotebookLM Brain #7 sources: Cascade failure / WYSIATI / SRM check / T1 North Star

---

## 2026-04-05 — v3.0 Milestone Plan Evaluation — Evaluation of: Milestone Brief + PRP v3.0 + Paperclip Codebase

### Cross-Domain Synthesis

No domain brain outputs were provided for this evaluation. The input is the v3.0 milestone plan (PRP document + milestone brief). This is a Moment 1 evaluation (Architecture/Roadmap decision) where Brain #7 evaluates the plan structure itself.

The plan proposes: fork Paperclip UI (41 pages, 116 components, 300 TS/TSX files) into a rebranded MasterMind frontend; build a Rust Control Plane from scratch (Axum + Tokio) replacing 82,000 lines of Paperclip's TypeScript server; keep Python FastAPI for AI/brain agents; connect via gRPC + Protobuf. Six phases spanning 16-23 weeks.

### CRITICAL FINDINGS — Verified Against Codebase

**FINDING 1: Paperclip UI is Vite + React SPA, NOT Next.js. The stack lock is internally contradictory.**

Verified: `/home/rpadron/proy/paperclip/ui/vite.config.ts` uses `@vitejs/plugin-react` and `@tailwindcss/vite`. The `package.json` has zero Next.js dependencies. There is no `next.config.js`, no `app/` router directory, no SSR. The UI has a flat `src/pages/` directory with 41 standalone page components -- this is a client-side SPA with a simple router.

The BRAIN-FEED.md stack table (line 14) locks the frontend to "Next.js 16.x, App Router, no Pages." The PRP document (line 71) claims "Next.js 16 Frontend -- 4 pantallas -- apps/web/" already exists.

The conflict: if you fork Paperclip's Vite SPA, you are NOT shipping a Next.js App Router frontend. If you keep your existing Next.js 16 app in `apps/web/`, the fork is a SECOND frontend, not a replacement. These are mutually exclusive unless you plan a full Vite-to-Next.js migration of 300 files -- which is itself a multi-week project not accounted for in any phase.

Impact: Phase 0 ("Fork Paperclip UI, 1-2 weeks") is either (a) replacing Next.js with Vite (abandoning the locked stack), (b) a multi-week Vite-to-Next migration not budgeted, or (c) running two frontends simultaneously (operational complexity). None of these are addressed in the plan.

**FINDING 2: Paperclip server is 82,000 lines of TypeScript. The plan proposes rewriting 65% (~53K lines) in Rust. From scratch. In a greenfield project with zero existing Rust code.**

Verified: `/home/rpadron/proy/paperclip/server/src/` contains 252 TypeScript files totaling 81,994 lines. Routes alone are 14,551 lines. The PRP lists specific modules to rewrite: heartbeat.ts (140K), workspace-runtime.ts (76K), agents.ts (108K), access.ts (96K), live-events.ts, budgets.ts, execution-workspaces.ts, adapter-utils, cron.ts.

Paperclip itself has zero Rust code (verified: `find /home/rpadron/proy/paperclip -name "*.rs"` returns 0 results). This means there is no reference Rust implementation to learn from. Every module must be understood from TypeScript and reimplemented in Rust from zero.

The PRP's own "RESTRUCTURAR" section lists ~15 modules totaling roughly 800K of TypeScript source to port to Rust. Even at 3:1 compression (Rust is more concise), that is ~267K lines of Rust to write. For a solo developer using AI agents. In Phase 1 (3-4 weeks).

**FINDING 3: The plan omits a PostgreSQL migration phase but depends on PostgreSQL in Phase 1.**

The PRP specifies PostgreSQL + pgvector + RLS multi-tenant via SQLx in Rust. The current MasterMind runs SQLite (`mastermind.db`). There is no migration phase for this. Phase 1 says "Rust Control Plane + PostgreSQL migration (3-4 weeks)" -- but this bundles the entire database migration INTO the same phase as "build Rust Control Plane from scratch." These are two independent, each multi-week efforts.

SQLite to PostgreSQL migration is not a config change. It requires: schema translation (SQLite autoincrement to PostgreSQL sequences, TEXT to VARCHAR, etc.), data migration scripts, all query rewrites (SQLx uses compile-time checked queries -- every query must be rewritten), connection pooling configuration, and CI/CD pipeline changes.

### Second-Order Concerns

**FEEDBACK LOOP 1: The Rust Rewrite Death Spiral**

Rust Control Plane development is slow (verified: zero existing Rust code, steep learning curve even for AI) -> agent generates Rust code that doesn't compile -> iteration cycles multiply -> Phase 1 slips -> Phase 2 (Canvas) depends on Rust real-time hub -> Phase 2 blocked -> team adds more phases to compensate -> Planning Fallacy compounds -> sunk cost fallacy locks in Rust even if data shows it should be reconsidered.

This is not speculative. The NotebookLM query confirmed this pattern: "Fuera del Circulo de Competencia" -- operating outside the circle of competence multiplies risk exponentially. The current team competence is Python + TypeScript. Rust is outside that circle.

**FEEDBACK LOOP 2: Dual Frontend Maintenance Tax**

If the Paperclip Vite fork coexists with the existing Next.js app (FINDING 1, option c), every feature must be built twice -- once for each frontend framework. The current v2.2 has 4 screens in Next.js. The fork adds 41 pages in Vite. Feature parity between them becomes an ongoing cost that never ends. This is the "double maintenance burden" the NotebookLM sources identified as a velocity killer.

**FEEDBACK LOOP 3: gRPC Complexity Compounding**

The plan introduces gRPC + Protobuf for type sync across 3 languages. This means: every API change requires editing .proto files, regenerating Rust (tonic + prost), Python (betterproto), and TypeScript (protoc-gen-es) bindings, and coordinating deployments across 3 services. For a solo developer. Before any user has used the product.

The Protobuf toolchain adds build complexity (protoc compiler, language plugins, CI pipeline changes), versioning complexity (proto file versioning vs service versioning), and debugging complexity (binary protocol, need specialized tools). This is enterprise-grade infrastructure for a product that has zero users.

**CASCADE RISK: If Rust Control Plane Phase 1 fails, Phases 2-5 are all blocked.**

Phase 2 (Orchestration Canvas + Rust Real-time Hub) requires the Rust Control Plane to exist. Phase 3 (Multi-channel Gateway) requires the Adapter Registry in Rust. Phase 4 (Knowledge Distillation) requires the Event Store in PostgreSQL via Rust. Phase 5 (Template Marketplace) requires the Control Plane for multi-tenant routing.

The critical path runs entirely through Rust. If Phase 1 takes 3x longer than estimated (which is the base rate for greenfield rewrites in unfamiliar languages), the entire 16-23 week timeline becomes 48-69 weeks. There is no fallback path.

**OMISSION: No observability/monitoring phase.**

The current system has known gaps (SECRET_KEY hardcoded, 3 flaky coordinator tests, uptime/last_called_at hardcoded). The v3.0 plan adds 3 services (Rust Control Plane, Python Agent Runtime, Real-time Hub) plus Redis plus PostgreSQL plus gRPC plus multi-channel gateways. There is no phase for observability: no structured logging, no distributed tracing, no metrics collection, no alerting. The plan will ship a distributed system with no way to diagnose cross-service failures.

**OMISSION: No data migration strategy.**

620 tests exist in the Python test suite. The plan does not address: (a) which tests move to Rust, (b) which tests stay in Python, (c) how integration tests work across the gRPC boundary, (d) how test data is managed in PostgreSQL vs SQLite, (e) how the CI pipeline handles 3-language test suites.

### Metric Proposals

- **SLI-1 (Rust compilation success rate):** For Phase 1, track: % of AI-generated Rust modules that compile on first attempt vs require >3 iterations. If first-attempt rate < 40%, the Rust curve is steeper than estimated and timeline must be recalibrated. Measured weekly. Target: >= 60% by week 3 of Phase 1.

- **SLI-2 (Feature delivery velocity comparison):** Track features shipped per week in Rust vs Python. If Rust velocity < 0.5x Python velocity after week 2, trigger a stack decision review. This is a guardrail metric, not a target.

- **OKR-1 (Phase 0 completion criteria):** Fork Paperclip UI AND resolve the Vite/Next.js decision within the first 5 working days of Phase 0. If unresolved by day 5, Phase 0 scope was underestimated. Specific decision required: (a) abandon Next.js for Vite, (b) migrate Vite to Next.js (add 3 weeks), or (c) run both (add permanent maintenance tax). No "we'll figure it out" allowed.

- **OKR-2 (End-to-end smoke test across gRPC boundary):** By end of Phase 1, a single test must exercise: TypeScript frontend -> gRPC call -> Rust Control Plane -> gRPC call -> Python Agent Runtime -> response. If this test doesn't exist by Phase 1 end, the 3-service architecture has not been validated.

### Verdict

APPROVED_WITH_CONDITIONS -- the strategic vision (enterprise agent orchestration with knowledge distillation for LATAM) is sound and defensible. The Paperclip fork is a legitimate acceleration strategy. But the execution plan has three structural problems that will cause cascade failure if not addressed before Phase 0 begins:

1. **[BLOCKER] Resolve Vite vs Next.js contradiction.** Paperclip UI is Vite. BRAIN-FEED.md locks Next.js 16. These conflict. Decision required BEFORE Phase 0. Evidence: `/home/rpadron/proy/paperclip/ui/vite.config.ts` (Vite confirmed), BRAIN-FEED.md line 14 (Next.js locked).

2. **[BLOCKER] Phase 1 scope must be split.** "Rust Control Plane + PostgreSQL migration" is two phases, not one. Suggested split: Phase 1a = PostgreSQL migration from SQLite (Python-side, 1-2 weeks), Phase 1b = Rust Control Plane skeleton (auth + 1 route + gRPC bridge, 2-3 weeks). Evidence: Paperclip server = 82K lines of TypeScript, zero Rust reference code exists.

3. **[CONDITION] Define Rust escape hatch before starting.** If SLI-2 (Rust velocity) shows < 0.5x Python velocity at the Phase 1b midpoint, what happens? Options: (a) continue Rust with timeline extension, (b) revert specific modules to TypeScript/Python, (c) hybrid approach. This decision tree must be written down before writing any Rust code. No team should begin a greenfield rewrite in an unfamiliar language without a pre-commitment to data-driven course correction.

4. **[CONDITION] Add Phase 0.5: Observability Foundation.** Before Phase 2 (Real-time Hub), structured logging + distributed tracing + health checks must exist across all 3 services. Without this, debugging cross-service failures in a 3-language distributed system is guessing.

Source citations:
- Paperclip UI: `/home/rpadron/proy/paperclip/ui/vite.config.ts` -- Vite + React plugin confirmed
- Paperclip UI: `/home/rpadron/proy/paperclip/ui/src/pages/` -- 41 page files (not Next.js App Router)
- Paperclip UI: `/home/rpadron/proy/paperclip/ui/src/components/` -- 116 component files, 300 total TS/TSX files
- Paperclip server: `/home/rpadron/proy/paperclip/server/src/` -- 252 TypeScript files, 81,994 lines total
- Paperclip Rust: `find /home/rpadron/proy/paperclip -name "*.rs"` -- 0 results (no reference Rust implementation)
- MasterMind Rust: `find /home/rpadron/proy/mastermind -name "*.rs"` -- 0 results (zero existing Rust code)
- Stack lock: BRAIN-FEED.md line 14 -- "Next.js 16.x, App Router, no Pages"
- Known gaps: BRAIN-FEED.md lines 78-79 -- SECRET_KEY hardcoded, flaky tests
- NotebookLM sources: WYSIATI, Base-Rate Neglect, Circle of Competence, Lollapalooza Effect, Sunk Cost Fallacy, Second-Order Thinking, Inversion, Pre-mortem, Hormozi Value Equation

---

## 2026-04-05 -- Phase 13 Vertical Slice -- Evaluation of: Brain #4 Frontend, Brain #5 Backend, Brain #6 QA/DevOps

### Cross-Domain Synthesis

Three domain brains evaluated the Phase 13 Vertical Slice plan: validate 3-service architecture (Next.js -> Rust -> gRPC -> Python) using a single endpoint before committing to full Rust build.

**Brain #5 Backend:** Select POST /api/tasks/auto as VS endpoint. Proto contract with single DispatchTask RPC. Rust as apps/control-plane/ single crate. PostgreSQL only for executions table, Python stays SQLite. Rust Velocity Protocol with 3 dimensions at midpoint, 0.5x escape hatch.

**Brain #4 Frontend:** Confirms /api/tasks/auto via Server Action. Proposes CONTROL_PLANE_URL env var swap. Proto-generated types coexist in apps/web/src/proto/. One vitest integration test. Server Components pattern leverages JWT in httpOnly cookies.

**Brain #6 QA/DevOps:** Five test layers (Rust unit, proto contract, gRPC integration, PostgreSQL parity, E2E smoke). DatabaseConnection ABC extraction. Proto sync CI gate with buf. 7 pre-requisites before any Rust code. Test count: 1038 -> ~1086.

**Points of agreement:** All three agree on /api/tasks/auto endpoint. All three agree no dual-write (Phase 15). All three agree zero impact on existing 1038 tests. All three agree PostgreSQL is independent.

### Conflicts Named and Resolved

**CONFLICT 1: Environment variable naming.**
Brain #4 proposes `CONTROL_PLANE_URL`. The actual codebase uses TWO names: `FASTAPI_URL` (in apps/web/src/app/actions/tasks.ts line 23) and `API_URL` (in 10+ other files: login/actions.ts, api/brains/route.ts, api/brains/[id]/route.ts, api/brains/[id]/yaml/route.ts, api/tasks/[id]/graph/route.ts, api/executions/history/route.ts, api/keys/route.ts, api/executions/[id]/route.ts, api/keys/[id]/route.ts, lib/api.ts lines 78 and 127, wsStore.ts line 44). Docker Compose passes `API_URL` (docker-compose.yml line 28).

Winner: Neither. Brain #4's `CONTROL_PLANE_URL` introduces a THIRD env var name into a codebase that already has TWO doing the same job. The correct move is to pick ONE name (either `API_URL` since Docker Compose already uses it, or `CONTROL_PLANE_URL` if the intent is to distinguish Rust from Python endpoints) and migrate ALL references. The "one line swap" claim is WYSIATI -- it ignores 14+ files referencing localhost:8001.

Evidence: grep `localhost:8001` across apps/web/src/ returns 15 occurrences across 8 files.

**CONFLICT 2: Rust Velocity dimensions disagree.**
Brain #5 defines 3 dimensions (runtime latency, dev cycle time, LOC) measured at midpoint with 0.5x trigger. Brain #6 defines 4 dimensions (time to implement, LOC handler, LOC tests, test cycle time) with 2.0x trigger.

Winner: Brain #6's 4 dimensions are more complete (includes implementation wall-clock time). But Brain #5's 0.5x trigger threshold is more aggressive and more appropriate for a VS -- the point is to detect failure early, and 2.0x is too forgiving. Brain #6's 2.0x means you can take TWICE as long on the vertical slice and still proceed, which defeats the purpose of a velocity check.

Resolution: Use Brain #6's 4 metrics with Brain #5's 0.5x trigger threshold for runtime and dev cycle. Use Brain #6's 2.0x threshold for LOC only (structural verbosity is acceptable; velocity death is not).

**CONFLICT 3: tasks.ts calls /api/tasks, not /api/tasks/auto.**
All three brains assume the VS endpoint is /api/tasks/auto. The current Server Action (tasks.ts line 66) calls `${FASTAPI_URL}/api/tasks` (the generic endpoint, not /auto). The /auto endpoint exists in Python (tasks.py line 128) but the frontend does NOT currently use it.

Winner: Brain #5 is correct that /auto is the better VS choice (it exercises FlowDetector + gRPC bidirectional). But no brain identified that the "one line swap" requires changing both the URL path AND the request body schema (CreateTaskRequest has a `brief` field; AutoTaskRequest likely differs). This is not one line -- it is an API contract change.

Evidence: tasks.ts line 66 calls `/api/tasks` with body `{ brief }`. tasks.py line 128 defines `/auto` with AutoTaskRequest (likely different schema). The Server Action must change URL path, request schema, and response handling.

### Second-Order Concerns

**SYSTEMS GAP 1: The Lollapalooza Effect of Simultaneous Novelty (no brain identified this)**

Phase 13 introduces 4 independent unknowns simultaneously: Rust language, tonic/gRPC framework, SQLx + PostgreSQL, and Docker Compose multi-service orchestration. When any bug appears during development, its origin is ambiguous -- is it a Rust ownership error, a gRPC serialization mismatch, a PostgreSQL connection pool timeout, or a Docker network issue? This ambiguity multiplies debugging time non-linearly. The NotebookLM sources confirm this pattern (Circle of Competence, Lollapalooza Effect -- source IDs 55eeb28c, 5db6e11a).

Cascade: ambiguous bug -> developer tries first fix that works (Doubt-Avoidance Tendency) -> technical debt in Rust/gRPC layer -> subsequent phases build on compromised foundation -> escape hatch triggers too late because "it compiles and tests pass."

**SYSTEMS GAP 2: Configuration Fragmentation Drift (Brain #4 introduced, no brain caught)**

The current codebase has 2 env var names for the same thing (FASTAPI_URL, API_URL). Brain #4 proposes adding a THIRD (CONTROL_PLANE_URL). If accepted, Phase 13 ships with 3 names for "the URL I call the backend." By Phase 15 (dual-write), some endpoints go to Rust and some stay on Python. Which env var points where? Developers (including future you) will waste time on "am I calling the right service?" debugging sessions.

Cascade: 3 env var names -> Phase 15 dual-write requires routing by endpoint -> developer confusion -> bug in production routing -> data written to wrong service -> data loss or split-brain state.

**SYSTEMS GAP 3: Local Development Cold Start (no brain addressed)**

Current Docker Compose: 2 services (api:8001, web:3000). Phase 13 adds: Rust control-plane (port TBD) + PostgreSQL 16 (port 5432). That is 4 services. Current cold start: `docker compose up -d` -> 2 containers. Phase 13 cold start: 4 containers + proto codegen + Rust compilation + PostgreSQL initialization + health checks for all 4 services.

No brain measured or proposed measuring the local development boot time. The NotebookLM sources identify "Time to Value" and "Experiment Velocity" as critical metrics for developer adoption (source IDs 742c3cef, b288f2a3). If boot time exceeds 2 minutes, the developer will stop running the full stack locally, which defeats the E2E smoke test (Layer 5).

Cascade: slow boot -> developer runs only Rust unit tests -> gRPC integration bugs not caught until CI -> CI cycles longer -> velocity drops -> Phase 13 timeline slips.

**SYSTEMS GAP 4: Proto Codegen Tax (all brains assumed zero friction)**

All three brains assume proto codegen "just works." Reality: tonic-build (Rust), betterproto (Python), and protoc-gen-es (TypeScript) are three independent codegen tools with different versions, different plugin configs, and different error messages. Brain #6's CI gate catches DRIFT but does not address the TIME cost of maintaining 3 codegen targets. Every field change to brain_runtime.proto triggers: edit proto -> regenerate Rust -> regenerate Python -> regenerate TypeScript -> fix any compile errors in 3 languages.

This is a permanent tax, not a one-time cost. The domain brains treated it as infrastructure, but for a solo developer it is a velocity drag that compounds with every proto change.

**SYSTEMS GAP 5: Pre-requisite Setup Time Underestimated (Brain #6 listed 7 items, no brain estimated the time)**

Brain #6 lists 7 pre-requisites: buf CLI, protoc, PostgreSQL 16 Docker, asyncpg, testcontainers-postgres, proto/ directory with buf config, apps/control-plane/ cargo init. No brain estimated how long these take to set up and validate. For a developer with zero Rust toolchain experience: rustup + cargo + tonic-build dependencies + protoc installation + buf CLI + Docker PostgreSQL config + proto directory structure + first successful cargo build. This is easily 1-2 days of setup before ANY feature code is written.

### Metric Proposals

- **SLI-1 (Time to First Green):** Time from "cargo init" to first passing `cargo test` with a gRPC round-trip to Python. Target: <= 3 working days. If > 5 days, the learning curve is steeper than estimated and timeline must be recalibrated.

- **SLI-2 (Local Boot Time):** `docker compose up -d` to all 4 services healthy (api, web, control-plane, postgres). Target: <= 90 seconds. If > 120 seconds, operational complexity is cannibalizing development velocity.

- **SLI-3 (Proto Change Cycle Time):** Time to make a single field addition to brain_runtime.proto and have all 3 codegen targets compile clean. Target: <= 15 minutes. If > 30 minutes, the proto tax is unsustainable for a solo developer.

- **SLI-4 (Debugging Ambiguity Rate):** Count of debugging sessions where the root cause was ambiguous between Rust/gRPC/PostgreSQL/Docker. Target: <= 3 per week during Phase 13. If > 5 per week, the Lollapalooza Effect is active and one unknown should be removed (e.g., use SQLite instead of PostgreSQL for Rust, defer gRPC complexity).

- **OKR-1 (Configuration Unification):** Before Phase 13 ships, ALL 15 references to localhost:8001 across apps/web/src/ must use a SINGLE env var name. Zero tolerance for 3 names doing the same job. Measured by: `rg -c "localhost:8001" apps/web/src/` must return 0 results (all replaced by env var).

- **OKR-2 (Velocity Checkpoint):** At Phase 13 midpoint, Rust Velocity Protocol metrics are recorded in velocity-measurements.md. If ANY dimension (runtime latency, dev cycle, wall-clock implementation) exceeds 2.0x Python baseline, a formal go/no-go decision is required before continuing.

### Omission Bias -- What All Three Brains Missed

1. **No rollback plan.** All three brains designed forward. None addressed: what specific artifacts get reverted if Phase 13 proves Rust is not viable? The proto files, the Rust crate, the PostgreSQL schema, the Docker Compose changes, the env var changes -- what gets deleted and what stays? Without a rollback spec, Phase 13 creates orphaned infrastructure even if the escape hatch triggers.

2. **No observability for the VS itself.** The domain brains propose measuring Rust velocity but not measuring whether the VS endpoint is actually being called during development. If the developer falls back to testing Python endpoints (because they already work), Phase 13 can "complete" without ever truly validating the 3-service architecture.

3. **No capacity planning for PostgreSQL in Docker.** SQLite is a file. PostgreSQL 16 in Docker requires memory, disk, and configuration. No brain addressed PostgreSQL resource requirements for local development. On WSL2 (the confirmed development environment), Docker memory limits can silently degrade PostgreSQL performance, making Rust appear slower than it is -- a false negative that could kill the Rust decision.

### Verdict

APPROVED_WITH_CONDITIONS -- the vertical slice strategy is sound (validate before committing), the endpoint choice is correct (/auto exercises more layers), and the test layer structure is comprehensive. But 5 conditions are non-negotiable before Phase 13 begins:

1. **[BLOCKER] Configuration unification.** Pick ONE env var name. Migrate ALL 15 references. Do not ship Phase 13 with 3 names for the same URL. Evidence: grep returns 15 occurrences of localhost:8001 across apps/web/src/.

2. **[BLOCKER] Pre-requisite setup must be a separate, time-boxed step.** Allocate 1-2 days for toolchain setup (rustup, cargo, buf, protoc, PostgreSQL Docker). Time-box it. If setup exceeds 2 days, that IS a data point for the Rust Velocity Protocol.

3. **[CONDITION] Rollback plan documented before first line of Rust.** Which files/directories get deleted if the escape hatch triggers. This prevents orphaned infrastructure.

4. **[CONDITION] Local boot time SLI established before Phase 13 starts.** Measure current 2-service boot time as baseline. Set <= 90s target for 4 services. If boot time exceeds target during Phase 13, address it before Phase 14.

5. **[CONDITION] Velocity Protocol uses Brain #6's 4 metrics with Brain #5's 0.5x trigger for runtime/dev cycle, 2.0x for LOC.** This is the strongest combination -- aggressive velocity detection, lenient verbosity tolerance.

Source citations:
- Brain #4 output: "Single environment variable CONTROL_PLANE_URL" -- INCONSISTENT with codebase (15 occurrences of localhost:8001 with 2 different env var names)
- Brain #5 output: "Rust Velocity Protocol 3 dimensions 0.5x" -- CORRECT trigger threshold, INCOMPLETE metrics (missing wall-clock implementation time)
- Brain #6 output: "5 test layers, 7 pre-requisites" -- CORRECT scope, MISSING time estimate for setup
- Codebase: apps/web/src/app/actions/tasks.ts line 66 -- calls /api/tasks (NOT /api/tasks/auto), API contract change required
- Codebase: grep localhost:8001 across apps/web/src/ -- 15 occurrences in 8 files with 2 different env var names (FASTAPI_URL, API_URL)
- Codebase: docker-compose.yml -- 2 services currently, Phase 13 adds 2 more with no boot time measurement
- NotebookLM sources: Lollapalooza Effect (55eeb28c), WYSIATI (5db6e11a), Circle of Competence (76a9c932), Time to Value (742c3cef), Experiment Velocity (b289f2a3), Doubt-Avoidance Tendency (55eeb28c), Planning Fallacy (89cc29dd)

### Global Rating: 72/100

Deductions: -8 for configuration fragmentation not caught (Brain #4 introduced a third env var, no brain flagged this), -7 for "one line swap" WYSIATI (it is an API contract change, not a URL change), -5 for missing rollback plan (all forward, no backward), -4 for pre-requisite time underestimate (7 items, zero time estimate), -4 for local dev boot time not measured. The plan is directionally correct but the domain brains collectively underestimated the surface area of change for a solo developer operating outside their Circle of Competence.

## 2026-04-05 — Phase 13 Vertical Slice (Iteration 3) — Final Evaluation — Evaluation of: Phase 13 Plan Review (Iteration 3)

### Cross-Domain Synthesis

Three domain brains evaluated Phase 13 Vertical Slice across 4 waves (13-01 through 13-04). All 7 conditions from Iteration 1 were addressed in Iteration 3:

**Brain #5 Backend:** POST /api/tasks/auto as VS endpoint, Proto contract with single DispatchTask RPC, Rust single crate, PostgreSQL only for executions table, Rust Velocity Protocol with 4 metrics (time, LOC handler, LOC tests, test cycle) with 0.5x trigger for runtime/dev cycle, 2.0x for LOC.

**Brain #4 Frontend:** Server Action update to CONTROL_PLANE_URL, proto-generated types in apps/web/src/proto/, Server Components pattern with JWT in httpOnly cookies, one vitest integration test.

**Brain #6 QA/DevOps:** 5 test layers (Rust unit, proto contract, gRPC integration, PostgreSQL parity, E2E smoke), DatabaseConnection ABC extraction, proto sync CI gate with buf, 7 pre-requisites, test count 1038 → ~1086.

**Points of agreement:** All three agree on /api/tasks/auto endpoint, zero dual-write (deferred to Phase 15), zero impact on existing 1038 tests, PostgreSQL independent.

### Second-Order Concerns

**SYSTEMS GAP 1: Config-Contract Circular Dependency (NotebookLM confirmed)**

Plan 13-02 introduces proto sync CI gate that generates code for 3 languages. Plan 13-01 unifies env vars (FASTAPI_URL → CONTROL_PLANE_URL, API_URL → AGENT_RUNTIME_URL). If the proto sync CI gate reads CONTROL_PLANE_URL during codegen, but Plan 13-01 hasn't completed the migration, the gate fails. This is a Lollapalooza Effect — two independent changes (config naming + proto toolchain) compound to paralyze the pipeline.

Cascade: config migration incomplete → proto CI gate fails → cannot generate Rust/Python/TS bindings → Plan 13-03 gRPC client/server cannot compile → Phase 13 blocked at Plan 13-02.

**SYSTEMS GAP 2: Contract Rollback Incompatibility (NotebookLM confirmed)**

The rollback decision tree in Plan 13-01 Task 3 covers deployment artifacts (delete apps/control-plane/, revert docker-compose.yml, delete proto/). But it omits CONTRACT VERSIONING. If Plan 13-04 ships (Frontend Server Action calls CONTROL_PLANE_URL with new AutoTaskRequest schema), then the rollback triggers and reverts to Python-only backend, the Frontend is now calling an endpoint that doesn't exist. The rollback breaks the frontend.

Cascade: rollback Rust backend → Frontend still uses new contract → 404 on POST /api/tasks/auto → VS cannot be tested even if Python backend is restored → need to ALSO revert Frontend or add compatibility layer. Rollback tree doesn't specify this.

**SYSTEMS GAP 3: PostgreSQL Initialization State Missing (NotebookLM confirmed)**

Plan 13-01 adds PostgreSQL 16 + pgvector service. Plan 13-03 creates executions table via SQLx migration. But nowhere does the plan specify WHEN the migration runs. Is it manual? Is it automated on container startup? If the developer runs `docker compose up -d` and PostgreSQL starts healthy but the executions table doesn't exist, the first POST /api/tasks/auto call fails with "relation executions does not exist."

Cascade: PostgreSQL healthy → migrations not run → first request fails → developer assumes Rust broken → wastes time debugging gRPC when the issue is missing migration → boot time SLI degraded for wrong reason.

**SYSTEMS GAP 4: Half-Life Failure Mode (NotebookLM confirmed)**

The rollback decision tree assumes binary success/failure. But what if the system "works" but Boot Time SLI increases by 400% (from 30s to 120s) due to gRPC overhead + PostgreSQL + Docker network latency? The tree has no branch for "Performance Degradation — system functional but violates SLI." In this case, Action Bias leads the team to keep pushing forward ("it works, optimize later") when the correct response is to trigger escape hatch (Rust is too slow).

**SYSTEMS GAP 5: Rollback Mechanism Dependency Paradox (NotebookLM confirmed)**

The rollback tree says "if velocity escape hatch triggers, delete apps/control-plane/ and revert docker-compose.yml." But if CONTROL_PLANE_URL is already deployed to production (even if just internal localhost), reverting docker-compose.yml requires knowing which env vars to revert TO. The rollback mechanism depends on the new unified config being functional enough to execute the revert. If the config layer itself is broken, you cannot execute the rollback.

### Metric Proposals

- **SLI-1 (Config-Contract Sync Success Rate):** % of proto sync CI gate passes that do NOT fail due to missing env vars. Target: 100%. If any CI failure traces back to CONTROL_PLANE_URL not being set, the Config-Contract loop is active and Plan 13-01/13-02 coupling must be decoupled.

- **SLI-2 (Rollback Reversibility Time):** Time from "escape hatch trigger" decision to "system fully reverted to pre-Phase 13 state." Target: <= 30 minutes. If > 60 minutes, the rollback is not actually an escape hatch — it's a migration project. Measured by: timestamp trigger → timestamp docker compose up -d succeeds with 2 services (api + web) only.

- **SLI-3 (PostgreSQL Migration Automation):** % of PostgreSQL service starts that include schema migration WITHOUT manual intervention. Target: 100%. If developer must run `psql -f migrations/001_executions.sql` manually, the initialization state is incomplete. Measured by: count of manual migration steps documented in runbook.

- **OKR-1 (Pre-mortem Completion):** Before Phase 13 execution begins, a written pre-mortem document must exist: "It is 48 hours from now, the 4-service orchestration has crashed CI/CD. Working backward, what failed?" Required scenarios: (a) proto sync gate blocked by env vars, (b) PostgreSQL migrations not run, (c) gRPC timeout cascades to frontend, (d) boot time 400% degradation. This is not optional — it is the Inversion principle applied.

### Verdict

APPROVED_WITH_CONDITIONS — all 7 conditions from Iteration 1 are now addressed, and the plan is directionally sound. But 4 SYSTEMS-LEVEL conditions remain from NotebookLM analysis:

1. **[BLOCKER] Config-Contract decoupling.** Plan 13-02 proto sync CI gate must NOT depend on CONTROL_PLANE_URL being set. If the gate requires env vars to run codegen, the gate must fail gracefully (skip codegen, warn) rather than block the entire pipeline. Evidence: NotebookLM source "Lollapalooza Effect" — compound novelty paralyzes pipeline.

2. **[BLOCKER] Contract rollback compatibility.** The rollback decision tree (Plan 13-01 Task 3) must add a branch: "If Frontend has shipped with new contract, rollback Frontend Server Action OR add Python compatibility layer for /api/tasks/auto." Evidence: NotebookLM source "Contract Rollback Incompatibility" — binary rollback breaks frontend.

3. **[BLOCKER] PostgreSQL initialization automation.** Plan 13-01 Task 2 must specify HOW migrations run. Options: (a) SQLx migrate in Rust app startup, (b) init script in Docker image, (c) manual step documented. No "we'll figure it out" — the first request will fail without this. Evidence: NotebookLM source "Data State Persistence" omission.

4. **[CONDITION] Half-Life failure mode branch.** Rollback decision tree must add: "If system works but Boot Time SLI > 120s OR Rust Velocity > 2.0x Python, trigger escape hatch." Performance degradation is a failure mode, not a success. Evidence: NotebookLM source "Inversion" — asking what guarantees failure.

5. **[CONDITION] Pre-mortem document required.** Before writing first Rust line, write "pre-mortem-13.md" with 4 failure scenarios worked backward from "CI/CD crashed 48 hours from now." Evidence: NotebookLM source "Pre-mortem" — imagine failure to prevent it.

Source citations:
- NotebookLM Brain #7 sources: Lollapalooza Effect (55eeb28c), WYSIATI (5db6e11a), Circle of Competence (76a9c932), Planning Fallacy (2b770e1f), Inside View (2b770e1f), Twaddle Tendency (55eeb28c), Inversion (55eeb28c), Pre-mortem (5db6e11a), Action Bias (55eeb28c)
- Plan 13-01 Task 1: "Unify env vars FASTAPI_URL → CONTROL_PLANE_URL, API_URL → AGENT_RUNTIME_URL"
- Plan 13-01 Task 3: "Document rollback scenarios in rollback-plan.md"
- Plan 13-02 Task 4: "Proto sync CI gate with buf lint + buf generate + drift check"
- Plan 13-03 Task 3: "PostgreSQL repository with SQLx compile-time verified queries"
- Plan 13-04 Task 2: "Docker Compose with 4 services: web, control-plane, api, postgres"

### Global Rating: 82/100

Improvement from Iteration 2 (72 → 82): +10 for addressing all 7 original conditions (config unification, time-box, baseline spec, rollback plan, boot time SLI, velocity protocol, observability).

Remaining deductions: -8 for Config-Contract circular dependency not caught, -6 for Contract Rollback Incompatibility, -4 for PostgreSQL initialization state missing.

The plan is APPROVED_WITH_CONDITIONS because the systems-level gaps are correctable BEFORE execution begins (they are planning gaps, not architectural flaws). Once the 4 blockers/conditions above are addressed in the plan documents, Phase 13 is ready to ship.


---

## 2026-04-05 — Phase 13 Vertical Slice — Evaluation of: Brains #4 #5 #6 (Rust Control Plane + PostgreSQL + gRPC)

### Cross-Domain Synthesis

Three domain brains consulted for Phase 13 Vertical Slice (Rust Control Plane + PostgreSQL + gRPC infrastructure).

Brain #4 Frontend: APPROVED. Recommends POST /api/tasks/auto via Server Action (apps/web/src/app/actions/tasks.ts). Single file change from FASTAPI_URL to CONTROL_PLANE_URL. Proto types coexist in apps/web/src/proto/ — no query hooks or stores modified. Server Components pattern confirmed (JWT httpOnly cookies accessible server-side only).

Brain #5 Backend: APPROVED. Recommends mastermind.v1.BrainRuntime gRPC service with single RPC (DispatchTask). Rust Control Plane as single crate (NOT workspace — workspace decomposition deferred to Phase 15). PostgreSQL for executions table only — Python's 631 tests stay on SQLite (:memory:). Dual-write is Phase 15, not Phase 13.

Brain #6 QA/DevOps: APPROVED. Five test layers specified (Rust unit, proto contract, gRPC integration, PostgreSQL parity, E2E smoke). Proto-sync CI gate prevents drift. Velocity protocol with 4 metrics: wall-clock time, LOC handler, LOC tests, test cycle time. Escape hatch triggers: 0.5x for runtime/dev cycle (Brain #5), 2.0x for LOC (Brain #6).

Points of agreement: All 3 brains converged on POST /api/tasks/auto as correct path. All agree Phase 13 is vertical slice NOT full migration. All agree Python tests unaffected (631 passing confirmed).

Points of tension: None identified — all brains aligned on scope and approach.

### Second-Order Concerns

FEEDBACK LOOP — Config-Contract Circular Dependency: Plan 13-01 env var unification (FASTAPI_URL → CONTROL_PLANE_URL) MUST complete before Plan 13-02 Rust config.rs reads CONTROL_PLANE_URL. If Plan 13-02 starts before Plan 13-01 completes, Rust compiles but cannot connect — silent failure mode. Mitigation: Plan 13-02 Task 4 CI gate fails gracefully (warning only if CONTROL_PLANE_URL not in .env.example). CI passes even during setup — prevents pipeline paralysis.

FEEDBACK LOOP — Proto-Sync Bottleneck: All three brains agree on gRPC/proto path, but second-order effect is reduced Experiment Velocity. If every frontend change requires coordinated proto update + backend recompile, the "1-2 day toolchain setup" assumption falls victim to Planning Fallacy. Mitigation: "Decoupled development mode" where frontend uses local mock schema while gRPC contract finalizes.

CASCADE FAILURE — grpclib Installation Block: If grpclib install fails or takes > 30min → Python gRPC server blocked → entire VS blocked. Mitigation: Condition 2 in Plan 13-01 — record as "setup overhead" and continue with mock gRPC. Pre-mortem Scenario A documents this failure mode with prevention strategy.

CASCADE FAILURE — PostgreSQL Migration Missing: If Plan 13-01 adds PostgreSQL service and Plan 13-03 adds ExecutionRepo but neither specifies WHEN migrations run → first request fails with "relation executions does not exist" → 500 error in production. Mitigation: Plan 13-01 Task 2 specifies docker/postgres/init-db.sql with migrations. PostgreSQL runs init script automatically on first startup. Pre-mortem Scenario B analyzes this root cause.

CASCADE FAILURE — Boot Time Degradation (Half-Life Failure Mode): If boot time increases from 30s (2 services) to 150s (4 services) → developers stop running full stack → integration bugs missed (e.g., gRPC serialization issue discovered in production). Mitigation: Plan 13-01 Task 3 measures baseline BEFORE Phase 13 starts. Target: 4 services ≤ 90s. Escape hatch trigger: > 120s OR > 400% degradation from baseline. Pre-mortem Scenario D documents this "slow failure" mode.

CASCADE FAILURE — gRPC Timeout Cascade: If Python gRPC server slow to start (grpclib startup delay) AND frontend has no timeout → waits forever → retry logic triggers 3 simultaneous requests → each spawns Rust handler → Python gRPC call → system overload. Mitigation: Plan 13-03 Task 2 Rust gRPC client with timeout (tonic Channel::timeout). Plan 13-04 Task 1 Next.js fetch with timeout (AbortController). Response time SLI: < 2s. Pre-mortem Scenario C analyzes this cascade.

METRIC BLINDSPOT — Treatment Exposure Rate: Current metrics focus on technical performance (latency, LOC, test cycle) but ignore Overall Evaluation Criteria (OEC). If users are never "exposed" to new /api/tasks/auto path because of frontend conditional logic, any performance "win" is a Vanity Metric. Mitigation: Track % of requests to /api/tasks/auto vs /api/tasks. If < 50% by midpoint → VS not validated. This is Brain #7 CONDITION #7 — added to Plan 13-01 Task 3.

METRIC BLINDSPOT — Boot Time Baseline Documentation: "Local boot time ≤ 90s" is verifiable, but baseline measurement must be documented BEFORE Phase 13 starts with timestamp, service names, and time to healthy explicitly. Otherwise, "90s target" has no anchor. Mitigation: Plan 13-01 Task 3 explicitly documents: "Document in velocity-baseline.md: Baseline (2026-04-05): 2 services (api + web) = X seconds to healthy."

CROSS-DOMAIN TRADEOFF — Workspace Decomposition: Brain #5 optimized for single crate (simpler VS). Brain #6 wants workspace decomposition (Phase 15). This is correctly deferred — single crate for VS, workspace decomposition is Phase 15. No conflict.

### Metric Proposals

**Leading Indicators (prevent cascade failure):**
- SLI-1 (Boot Time): `time docker compose up -d` ≤ 90s for 4 services. If > 120s → trigger escape hatch.
- SLI-2 (Treatment Exposure Rate): % of requests to /api/tasks/auto vs /api/tasks ≥ 50% by midpoint. If < 50% → VS not validated.
- SLI-3 (Error Rate Guardrail): First 100 requests to /api/tasks/auto must have error rate < 0.1%. If exceeded → automatic kill switch on route, revert to legacy /api/tasks.
- SLI-4 (gRPC Call Duration): P95 < 500ms for DispatchTask RPC. If > 2s → investigate Python gRPC server health.

**Lagging Indicators (measure velocity hypothesis):**
- SLI-5 (Rust vs Python Wall-Clock Time): Rust implementation time / Python baseline ≤ 2.0x. If > 2.0x → escape hatch trigger.
- SLI-6 (Rust vs Python LOC): Rust LOC / Python LOC ≤ 2.0x for equivalent functionality. (Lenient — Rust verbosity acceptable per Brain #6).
- SLI-7 (Dev Cycle Time): Edit-build-test cycle time (cargo test vs pytest). Rust must NOT be < 0.5x Python (aggressive trigger per Brain #5 — if Rust is this much faster, investigate measurement error).

**OKR (Vertical Slice Validation):**
- OKR-1: User can trigger POST /api/tasks/auto from UI, request flows through all 5 layers (Next.js → Rust → gRPC → Python → PostgreSQL → UI), response time < 2s, all 4 services healthy in Docker Compose. Success = Rust Control Plane validated for Phase 15 expansion.

### Verdict

**APPROVED** — Delta-Velocity Rating 5 (Principal). Phase 13 ready for execution in background agent.

**Evidence citations:**
- Source: `.planning/phases/13-vertical-slice/13-PLAN-REVIEW.md > CORRECTED ASSUMPTIONS` — 7 conditions from Iteration 1 all addressed.
- Source: `.planning/phases/13-vertical-slice/13-PLAN-REVIEW.md > CORRECTIONS APPLIED (Iteration 4)` — 4 systems-level blockers all mitigated.
- Source: `.planning/phases/13-vertical-slice/pre-mortem-13.md` — 4 failure scenarios analyzed with prevention strategies (proto-sync blocked, PostgreSQL migrations missing, gRPC timeout cascade, boot time degradation).
- Source: `.planning/phases/13-vertical-slice/13-BRAIN-OUTPUTS.md > Brain #5` — "Phase 13 does NOT implement dual-write. Rust writes only to PostgreSQL. Python's 631 tests stay on SQLite."
- Source: `.planning/phases/13-vertical-slice/13-BRAIN-OUTPUTS.md > Brain #4` — "Server Action runs on the server, calls Rust, returns to the client. This is the CORRECT pattern because JWT in httpOnly cookies only accessible server-side."
- Source: `BRAIN-FEED.md > Stack (Locked)` — Next.js 16.x App Router confirmed, React 19.x Compiler disabled confirmed.
- Source: `apps/web/src/app/actions/tasks.ts:23-24` — FASTAPI_URL reference confirmed (VERIFIED via grep).
- Source: `apps/api pytest --collect-only` — 631 tests confirmed (VERIFIED via pytest).

**Confidence Score:** 95%. Pre-mortem analysis addressed 4 failure modes. Feedback loop risks mitigated with graceful CI failure and decoupled development mode. Cascade failure modes documented with prevention strategies. Metric blindspots covered (Treatment Exposure Rate, Boot Time Guardrail, Error Rate Kill Switch). Cross-domain tradeoffs resolved (single crate for VS, workspace deferred to Phase 15). The remaining 5% is unknown unknowns (black swans) — acceptable for a vertical slice with escape hatch documented.

**Key Success Factors:**
1. Measure boot time baseline BEFORE starting (Plan 13-01 Task 3) — establishes anchor for 90s target.
2. If grpclib install fails → pivot to mock gRPC immediately (Condition 2) — prevents VS blockage.
3. Proto-sync CI gate fails gracefully (warning only if env vars missing) — prevents pipeline paralysis during setup.
4. PostgreSQL init script automation (docker/postgres/init-db.sql) — prevents "relation does not exist" cascade.
5. Treatment Exposure Rate ≥ 50% by midpoint — validates VS is actually being used, not just deployed.
6. Escape hatch triggers: > 120s boot time OR > 400% degradation OR > 2.0x velocity ratios — clear decision points.

**Background Agent Instructions:**
- Pre-mortem integration: Agent must simulate grpclib installation failure in first hour and pivot to Condition 2 mock gRPC.
- Fermi estimation for boot time: Before writing code, estimate crate size + dependency tree to verify 90s target is physically realistic.
- Statistical power check: Ensure /api/tasks/auto receives enough traffic to meet Minimum Detectable Effect (MDE) for latency. If sample size too small, favor E2E smoke tests over quantitative metrics.

---

*Phase 13 evaluation completed: 2026-04-05*
*4 planning iterations, 7 conditions, 4 systems-level blockers, 4 pre-mortem scenarios — all addressed*

---

## 2026-04-06 — Phase 14 Knowledge Distillation — Evaluation of: Plan Review Iteration 2

### Cross-Domain Synthesis

Four plans evaluated for knowledge distillation system: Quality score calculation (14-01), Auto-evaluation loop (14-02), Template generation (14-03), Dashboard API (14-04). Iteration 2 applied 4 fixes addressing BLOCKING gaps: SQLite percentile → Python calculation, router registration correction, cold start fallback, quality score calibration documentation.

No domain brain outputs provided — this is a plan-only evaluation. The iteration delta shows responsiveness to technical blocking issues, but reveals a deeper systemic gap.

### Second-Order Concerns

**FEEDBACK LOOP GAP: Quality Score Chicken-and-Egg**

Plan 14-03 extracts templates from records with `quality_score >= 3.0`. Plan 14-01 defines quality_score calculation. Plan 14-02 creates auto-eval hook but defers actual Brain #7 LLM call to Phase 15. Fix 4 documents this deferral.

The loop: Quality scores required → Templates extracted → Analytics measure success → Better quality scores.

The break: Without Brain #7 auto-eval wired (Phase 15), quality_score field is NULL/default for all records. Plan 14-03's cold start fallback (Fix 3) lowers threshold to 2.0, but still requires quality_score to be populated. If all records have NULL quality_score, the fallback doesn't help — zero templates extracted anyway.

Named cascade: Missing quality_score seeding → Plan 14-03 produces zero output → Plan 14-04 analytics shows zero templates → System appears broken → Teams loses confidence in knowledge distillation → Feature abandoned.

This is not speculative. The codebase has existing `experience_records` (Phase 12) without quality_score. Without a seeding mechanism, the system starts empty.

**CASCADE RISK UNADDRESSABLE BY ITERATION FIXES: ExperienceLogger Startup Gap**

Brain #7 feed line 87 documented: `create_experience_schema()` exists (database.py:305) but is NOT called in startup_event (app.py:135-143). The iteration delta fixes 4 specific technical gaps but does NOT address this prerequisite.

All 4 plans depend on `experience_records` table existing:
- Plan 14-01: Rejection filter queries `WHERE quality_score >= 1.0` — table doesn't exist → crash
- Plan 14-02: Auto-eval hook calls `log_execution()` — table doesn't exist → crash
- Plan 14-03: Template extraction queries `experience_records` — table doesn't exist → crash
- Plan 14-04: Analytics API queries record counts — table doesn't exist → crash

This is a BLOCKER for the entire phase. The 5-minute fix (add `await create_experience_schema()` to startup_event) is outside Plan 14 scope but is a **prerequisite dependency** that must be confirmed before execution.

**Metric Blindspot: No Template Pollution Detection**

Fix 3's cold start fallback lowers threshold from 3.0 to 2.0 with warning. This admits lower-quality templates into the knowledge base. The plan tracks `success_rate` per template, but does NOT define a **template eviction threshold**.

If a template's success_rate drops below 0.3 (30%), it should be retired. Without eviction, the knowledge base accumulates noise → retrieval quality degrades → delta-velocity increases instead of decreasing. This is the Meadows "memory without decay" risk all over again, applied to templates instead of records.

### Metric Proposals

- **SLI-1 (Quality score seeding rate):** Percentage of existing `experience_records` with non-NULL quality_score after Plan 14-02 execution. Target: 100%. If < 100%, template extraction (Plan 14-03) operates on incomplete data.

- **SLI-2 (Template extraction yield):** Number of templates extracted in Plan 14-03 execution. Minimum viable threshold: >= 3 templates. If zero, the cold start fallback failed or quality_score seeding didn't run.

- **SLI-3 (Template eviction rate):** Percentage of templates with success_rate < 0.3 that are retired after 100 uses. Target: > 0%. If zero, knowledge base accumulates pollution without cleanup.

- **OKR (Knowledge distillation activation):** By end of Phase 14, a second consultation on the same topic must cite >=1 template AND complete in < 90s. If T1 doesn't decrease vs manual baseline (210-270s), the distillation system is not delivering value.

### Verdict

**APPROVED_WITH_CONDITIONS** — The iteration delta fixes are correct and address the specific BLOCKING technical gaps identified. However, two systemic gaps remain that will cause cascade failure if unaddressed:

**1. [BLOCKER] ExperienceLogger startup verification.** Before ANY Plan 14 task executes, verify `create_experience_schema()` is called in `apps/api/mastermind_cli/api/app.py` startup_event. Evidence: Brain #7 feed line 87 confirmed missing call. All 4 plans depend on this table existing.

**2. [CONDITION] Manual quality_score seeding in Plan 14-02.** Add explicit task: "Seed quality_score for existing experience_records using placeholder heuristic before auto-eval is wired." Example heuristic: status=success → 2.0, status=timeout → 0.5, status=failure → 0.0. This unblocks Plan 14-03 from producing zero output. Evidence: Plan 14-03 line 122 requires `quality_score >= 3.0`, Plan 14-02 defers auto-eval to Phase 15, Fix 4 confirms dependency.

**3. [CONDITION] Template eviction threshold definition.** Add to Plan 14-03 acceptance criteria: "Templates with success_rate < 0.3 after 100 uses are marked inactive." This prevents knowledge base pollution. Evidence: Fix 3 lowers threshold to 2.0 → admits lower-quality templates → cleanup mechanism required.

The 4 iteration fixes are sound (75% confidence). The chicken-and-egg gap (quality_score required but doesn't exist) is a systemic oversight that manual seeding resolves. The startup gap is a prerequisite dependency, not a Plan 14 task, but must be confirmed before execution.

Source citations:
- Fix 1 line 11: "SQLite percentile → Python calculation" — resolves BLOCKING runtime error
- Fix 2 line 17: "Router registration with correct file path" — resolves BLOCKING 404 error
- Fix 3 line 23: "Cold start fallback added" — resolves HIGH RISK bootstrap failure
- Fix 4 line 29: "Quality score calibration note added" — acknowledges MEDIUM RISK deferral
- Brain #7 feed line 87: `create_experience_schema() NOT called in startup_event` — CONFIRMED GAP
- Plan 14-03 line 122: Templates extracted from `quality_score >= 3.0` records — requires quality_score to exist
- Plan 14-02 line 100: Auto-eval hook created but Brain #7 call deferred — confirms no quality_score logic
- NotebookLM sources: Feedback loops, cascade failure, second-order effects, metric blindspots

---

## 2026-04-06 — PROP-001 Onboarding Visual — Evaluation of: Brains #2 (UX) + #3 (UI)

### Cross-Domain Synthesis

**Brain #2 (UX Research):** CONDITIONAL APPROVAL — Identified CLI barrier as REAL problem (Paperclip UX-Audit confirms "curva de aprendizaje alta" + "CLI-first perception"). Required persona definition (✅ RESOLVED: CEO técnico que quiere onboarding guiado que inspire confianza), Happy Path specification (✅ RESOLVED: 4 elementos — API Keys, Nicho, Brains, Knowledge Base), testing plan (✅ RESOLVED: MVP + iterar según feedback del CEO). Brain #2 emphasized dual onboarding paths (CLI + GUI), but user chose CLI replacement (no coexistence).

**Brain #3 (UI Design):** CONDITIONAL APPROVAL — Validated technical feasibility (Next.js 16 + React 19 + Tailwind 4 + shadcn/ui stack). Required 5-state system documentation (Default, Hover, Active, Disabled, Error/Loading), tonal elevation definition (dark mode overlays), grid system specification (12-column, 4/8px spacing), typography scale (math-based ratio 1.25). Brain #3 approved 4-step MVP structure aligned with user's 4-element Happy Path.

**Points of convergence:** Both brains agree CLI-based onboarding is a blocker for v3.0 target (LATAM business + technical users). Both agree War Room aesthetic must be preserved (desktop-first, 1440px, high density, terminal-style logs, zero happy talk). Both agree onboarding should be end-to-end (setup → first consultation → dashboard handoff).

**Points of tension:** Brain #2 wanted dual paths (CLI + GUI) to preserve power user flexibility; user explicitly chose CLI replacement (no fallback). This creates a **single point of failure** if visual onboarding has bugs.

**Shared assumptions:** v3.0 target includes business users who need GUI onboarding. Phase 15 (Rust Control Plane) is the implementation target. War Room aesthetic constraints apply. Both brains assumed Phase 15 will be ready when GUI onboarding ships — **this is unverified and creates cascade risk.**

### Second-Order Concerns

**FEEDBACK LOOP RISK — CLI replacement creates Phase 15 dependency without margin of safety:** According to Munger's margin of safety principle, eliminating CLI removes the technical safety net. If Phase 15 (Rust Control Plane) delays or has API contract changes, visual onboarding becomes non-functional. Zero fallback path = zero error recovery. Named cascade: Phase 15 delay → GUI onboarding broken → zero user activation → v3.0 launch blocked.

**CASCADE FAILURE MODE — Visual onboarding without Rust endpoints = empty shell:** The 4-element flow requires (1) API Key validation against Rust Control Plane, (2) Brain selection persistence via Rust API, (3) Knowledge Base connection through Rust gateway, (4) First consultation triggering Rust dispatcher. If ANY of these Rust endpoints are incomplete, onboarding fails at step 2. Verified: Phase 15 does not exist yet (`.planning/phases/` stops at Phase 14). This is not theoretical — it is a confirmed missing phase.

**METRIC BLINDSPOT — No "CEO technical assumption" validation metric:** Domain brains accepted user's persona clarification ("CEO técnico") without proposing how to DETECT if this assumption is WRONG. If actual users are LESS technical than expected, onboarding will have high abandonment at step 2 (API Key validation) or step 4 (Knowledge Base connection). No brain proposed measuring: (1) API Key error rate, (2) Time-to-First-Value (TTV), (3) Drop-off rate at Knowledge Base connection step, (4) Support ticket categorization ("what is an API Key" = failed persona assumption).

**CROSS-DOMAIN TRADEOFF — Brain #3's visual polish increases Brain #5's backend complexity:** 5-state system (Default, Hover, Active, Disabled, Error/Loading) requires Rust Control Plane to return granular validation states for every input. This is not just "status: 200/400" — it's "field: api_key, state: disabled, reason: invalid_format". Backend complexity increases → Phase 15 timeline extends → GUI onboarding waits longer → vicious cycle.

**WYSIATI RISK (What You See Is All There Is):** All domain brains evaluated the proposal AS IF Phase 15 exists and will be ready. None questioned: (1) Has Phase 15 been planned? (NO — confirmed missing), (2) What is the Phase 15 timeline estimate? (UNKNOWN), (3) What if Phase 15 API contracts change during development? (UNADDRESSED). This is classic WYSIATI — evaluating the visible (GUI design) without probing the invisible (backend readiness).

### Metric Proposals

**SLI-1 (Persona Validation):** API Key validation error rate < 15% at step 2. Measurement: `SELECT COUNT(*) WHERE validation_result = 'error' / COUNT(*) WHERE step = 'api_key_validation'`. If > 15%, the "CEO técnico" persona assumption is WRONG — users lack technical prerequisites.

**SLI-2 (Time-to-First-Value):** TTV < 5 minutes from onboarding start to first consultation complete. Measurement: `MAX(timestamp_first_consultation) - MIN(timestamp_onboarding_start)`. Target: < 300s. If median TTV > 15min, onboarding flow is too complex for the persona.

**SLI-3 (Abandonment Rate):** Drop-off rate < 30% at each step. Measurement: Funnel analysis (step 1 → 2 → 3 → 4 → complete). If any step has > 40% drop-off, that step is the friction point. Knowledge Base connection (step 4) is the predicted highest-friction step.

**OKR (Activation Rate):** 60% of users who start onboarding complete first consultation within 24 hours. Measurement: `COUNT(DISTINCT user_id) WHERE first_consultation_completed < 24h / COUNT(DISTINCT user_id) WHERE onboarding_started`. Target: ≥ 0.6. If < 0.4, onboarding is failing the core activation goal.

**Leading Indicator (Phase 15 Readiness):** Rust Control Plane API contract frozen AND all 4 endpoints (validate_api_key, persist_brain_selection, connect_knowledge_base, trigger_consultation) return 200 in staging BEFORE GUI onboarding development starts. Measurement: Contract version number in API docs + integration test suite pass rate = 100%.

### Verdict

**APPROVED_WITH_CONDITIONS** — Delta-Velocity Rating 3 (Peer). The proposal is VALID and ALIGNED with v3.0 strategic direction, but execution timing is CRITICAL. Building GUI onboarding before Phase 15 Rust Control Plane exists is premature optimization with high sunk cost risk.

**Conditions (MUST resolve before implementation starts):**

1. **[BLOCKER] Phase 15 must be planned AND estimated FIRST.** Current state: Phase 15 does not exist in `.planning/phases/`. Cannot build GUI onboarding without knowing: (a) What are the exact API contracts? (b) When will Phase 15 be ready? (c) What is the contingency plan if Phase 15 delays?

2. **[BLOCKER] Persona validation REQUIRED before code.** Conduct 3 Mom Test interviews with target users (LATAM CEOs who code or use AI tools). Ask: "Walk me through the last time you configured API keys for a service." If they struggle → persona is wrong → onboarding design must change. Evidence: Rob Fitzpatrick's "The Mom Test" — ask about specific past behavior, not future opinions.

3. **[CONDITION] Define escape hatch for CLI replacement.** Even though user chose replacement, document what happens if GUI onboarding has a critical bug (e.g., API Key validation loop). Options: (a) Emergency CLI command `npx mastermind-cli onboard --emergency`, (b) Direct config file editing in `~/.mastermind/config.yaml`. Pick ONE and document it.

4. **[CONDITION] Instrument abandonment metrics BEFORE launch.** Add funnel tracking (step 1 start → step 2 start → step 3 start → step 4 start → complete) to the GUI onboarding from day one. If you don't measure it, you can't detect when the persona assumption is wrong.

**Integration Recommendation:**

**DO NOT start GUI onboarding development in parallel with Phase 15.** Correct sequence:

1. **Phase 14.5 (Pre-build validation):** Conduct 3 Mom Test interviews to validate "CEO técnico" persona. If persona fails → iterate onboarding design → re-test. Time: 1 week.

2. **Phase 15 (Rust Control Plane):** Build backend infrastructure + API contracts + integration tests. Time: 3-4 weeks (estimated).

3. **Phase 15.5 (GUI Onboarding):** Build visual onboarding AFTER Rust endpoints are frozen and tested in staging. Time: 2 weeks.

**Why this sequence?** Fake Door testing (Phase 14.5) validates the problem exists without writing code. Phase 15 builds the foundation. Phase 15.5 builds the house ON TOP of the foundation, not in parallel with an uncertain foundation.

**Risk if ignored:** If GUI onboarding is built before Phase 15 and Phase 15 API contracts change, GUI code must be rewritten. This is sunk cost fallacy — "we already spent 2 weeks on the GUI, we can't throw it away." The correct decision is to WAIT for Phase 15 contracts to stabilize.

**Source citations:**
- PROP-001 proposal: "Reemplazar CLI completamente" — user chose replacement, no fallback
- Brain #2 output: "Onboarding visual = CONDITIONAL APPROVAL" — requires persona definition + Happy Path + testing plan
- Brain #3 output: "CONDITIONAL APPROVAL" — requires 5-state system + tonal elevation + grid system
- NotebookLM Brain #7 sources: Munger (margin of safety), Kohavi (A/B testing, counterfactuals), Reforge (growth loops, retention > acquisition)
- Codebase verification: `.planning/phases/` directory — Phase 15 does not exist (confirmed with ls command)
- Charlie Munger: "Margin of safety" — eliminating CLI removes technical safety net
- Rob Fitzpatrick: "The Mom Test" — validate persona with specific past behavior questions
- Paperclip UX-Audit: "Curva de aprendizaje alta" (CRITICAL) + "CLI-first perception" (HIGH) — confirms the problem is real

## 2026-04-06 — PROP-002 CEO Chat — Meta-evaluación de: Brains #1 (Product) + #2 (UX)

### Cross-Domain Synthesis

PROP-002 CEO Chat evaluated by 2 domain brains with conflicting verdicts.

**Brain #1 (Product Strategy):** REJECTED (85% confianza) — Solution looking for problem. User real is developer/architect, not CEO. Developers prefer visual dashboards over NL queries. No evidence NL reduces T1. Competes with Command+K. Suggests Concierge MVP first (manual Slack/Discord for 1 week).

**Brain #2 (UX Research):** CONDITIONAL_APPROVAL (65% confianza) — Aligned with UX principles (Jakob's Law, reduced gulf of evaluation). Complements War Room (chat = quick entry, War Room = deep monitoring). But requires: personality definition, expectation management, 3+ chat-only superpowers, Cmd+K integration, ambiguity handling, LATAM validation (3 interviews The Mom Test), paper prototype validation.

Points of agreement: Both agree role-based security is valid for enterprise platform.
Points of tension: Brain #1 says "vanity feature for wrong user", Brain #2 says "UX-aligned if validated".

### Conflict Resolution

**Why verdicts differ:** Brain #1 evaluates from VALUE/RISK ("Should we build this?"). Brain #2 evaluates from UX/USABILITY ("If this exists, how do we make it work well?"). Brain #1 questions the problem itself; Brain #2 assumes problem is real and focuses on solution design.

**Winner:** Brain #1 has the stronger position. Brain #2 assumes the problem is real ("UX-aligned if validated"), but Brain #1 questions whether the problem exists at all. In product systems, validating the problem BEFORE designing the solution is more important than designing the right solution to the wrong problem.

**Critical insight from NotebookLM:** The user's statement "Qué gano con tener un CEO virtual... y no puedo consultarle" is **Solution-talk, not Problem-talk**. The user is proposing a solution ("I want natural language chat") rather than describing a past behavior or specific difficulty. This is exactly what *The Mom Test* warns against — "fantasy about the future" is not evidence.

### Second-Order Concerns

**FEEDBACK LOOP — Lollapalooza Effect of Complexity:** Dashboard + Command+K + Chat = 3 competitive interfaces for the same task → Network degradation (Hitting a Ceiling from Reforge sources). Value to user decreases as more interfaces are added for the same job. Each interface adds cognitive load without clearing T1.

**FEEDBACK LOOP — Feature Factory Anti-pattern:** Shipping features without measuring OEC (Overall Evaluation Criteria). If chat only duplicates Command+K functionality, we create UI pattern fragmentation that increases maintenance cost without improving retention. This is "output over outcome" trap.

**FEEDBACK LOOP — Substitution Bias in Development:** Team might be answering the easy question ("Can we build chat?") instead of the hard one ("How do we reduce CEO Time-to-Value in decision making?"). This is classic WYSIATI — building what's visible instead of investigating the root problem.

**CASCADE FAILURE — Trust Leakage:** RBAC bug or LLM hallucination is not just a feature bug, it's a breach of the product's defensive moat. Enterprise trust is hard to gain and easy to lose. A single confidential data leak via chat AI kills the enterprise value proposition entirely.

**METRIC BLINDSPOT — No T1 before/after measurement:** Neither brain proposed measuring T1 (Time to Insight) before and after chat. Without baseline, we cannot claim chat improves anything. Vanity metrics: "users used chat" ≠ "chat reduced T1".

**METRIC BLINDSPOT — No abandonment rate tracking:** Neither brain proposed measuring "users start chat but don't complete" or "users start chat then switch to dashboard to verify data". This indicates lack of trust in chat output — a critical failure mode.

**CROSS-DOMAIN TRADEOFF — Brain #2's UX polish increases Brain #5's backend complexity:** Chat with personality, expectation management, and ambiguity handling requires sophisticated NLP + context management + RBAC. Backend complexity increases → development timeline extends → opportunity cost on other features increases.

### Metric Proposals

**SLI-1 (Time-to-Value comparison):** Measure TTV via manual chat (Concierge MVP) vs dashboard. Target: Manual chat TTV ≤ dashboard TTV. If manual chat is SLOWER, automated chat will be worse. Measurement: Timestamp question asked → timestamp user acknowledges "that's the answer I needed".

**SLI-2 (Abandonment rate):** Percentage of chat sessions that start but user switches to dashboard before completion. Target: < 40%. If > 60%, chat does not generate trust. Measurement: Funnel analysis (chat initiated → dashboard visited within 2 minutes → chat abandoned).

**SLI-3 (Query type distribution):** Categorize manual chat queries: (a) Status/State questions ("what's happening?"), (b) Action instructions ("create X"), (c) KPI queries ("what's the metric?"), (d) Cross-brain synthesis ("summarize everything"). Target: ≥50% cross-brain synthesis queries (these are chat-only superpower). If most queries are (a)/(c), dashboard already handles them better.

**OKR-1 (40% Test — PMF validation):** After Concierge MVP, ask users "How disappointed would you be if we removed this chat channel?" Target: ≥40% "very disappointed". If <40%, Brain #1 was right — this is a solution looking for a problem. Measurement: Survey with 4 options (very disappointed, somewhat disappointed, not disappointed, don't care).

### Verdict

**DEFERRED** — Delta-Velocity Rating 4 (Senior). The proposal is valid directionally but premature. User's statement is Solution-talk, not Problem-talk. No evidence of problem existence. Concierge MVP is REQUIRED to validate problem before any code investment.

**Integration Recommendation:**

**DO NOT build code yet.** Execute **Concierge MVP (1-week manual test)** FIRST:

1. **Week 1 — Concierge MVP:**
   - Create private Slack/Discord channel `#ceo-chat-beta`
   - User asks questions in natural language
   - You (or agent) respond manually using Command Center + Command+K
   - Measure: (a) What questions do they ask? (b) How frequently? (c) TTV vs dashboard?

2. **Decision criteria after Concierge MVP:**
   - **IF** SLI-1 (TTV) shows chat ≥ dashboard speed **AND** SLI-2 (abandonment) < 40% **AND** OKR-1 (40% Test) ≥ 40% very disappointed → **PROCEED to Brain #2 conditions** (personality, 3+ chat-only superpowers, Cmd+K integration, LATAM validation)
   - **ELSE** → **PROP-002 REJECTED**, close as "solution without problem"

3. **If Concierge MVP passes:**
   - Only then invest in LLM + RBAC + chat UI
   - Apply Brain #2's 6 conditions (personality definition, expectation management, chat-only superpowers, Cmd+K integration, ambiguity strategy, LATAM validation)

**Risk if ignored:** Building chat now without validation = sunk cost in LLM+RBAC integration + dead code + tech debt if nobody uses it. Concierge MVP cost = 1 week of manual time. Asymmetry of risk is enormous.

**Why Concierge MVP?** It's Margin of Safety (Munger) against Sunk Cost Fallacy. Transforms Solution-talk into behavioral data (The Mom Test) before investing in technical infrastructure. Cheapest way to validate if "Starving Crowd" exists for chat or if it's just "Twaddle" (talking for talking's sake).

**Source citations:**
- Brain #1 output: "REJECTED — Solution looking for problem. Concierge MVP first"
- Brain #2 output: "CONDITIONAL_APPROVAL — UX-aligned but requires validation LATAM + 3+ chat-only superpowers"
- NotebookLM Brain #7 sources: Lollapalooza Effect (55eeb28c), Feature Factory (1ad04189), Substitution Bias (5db6e11a), Trust Leakage/Moat (742c3cef), Value Equation (5e1f5de8), The Mom Test (3e3ce4f2), 40% PMF Test (bcad43f9), Sunk Cost/Action Bias (76a9c932), Starving Crowd (5e1f5de8), Twaddle (55eeb28c), Time to Value (b289f2a3)

---

## 2026-04-06 — PROP-003-B Analytics Financiero — Meta-evaluación de: Brains #1 (Product) + #7 (Growth/Data Domain)

### Cross-Domain Synthesis

**Propuesta evaluada:** Analytics Financiero por Agente y Proyecto — agregar tracking de costos (tokens, $$) y ROI por agente al dashboard de analytics existente (Phase 14-04).

**Brain #1 (Product Strategy):** DEFERRED (75% confianza) — Value Risk ALTO (no hay usuario con pain de costos verificado), Viability Risk ALTO (sin revenue ni pricing model), Usability Risk MEDIO (dashboard sin interpretación). Sugerencia: implementar como "Telemetry" primero (no dashboard completo), diferir a Phase 15+ solo si hay revenue.

**Brain #7 (Growth/Data - Domain):** APPROVED_WITH_CONDITIONS (80% confianza) — duration_ms YA capturado, quality_score YA calculado, custom_metadata JSONB permite agregar cost metrics sin migración. Condiciones: capturar prompt_tokens + completion_tokens, model_id, calcular roi_score asincrónicamente, evitar Goodhart's Law (bajo costo como target).

**Points of agreement:** Ambos coinciden en que la infraestructura técnica existe (duration_ms, quality_score, JSONB). Ambos coinciden en que hay riesgo de Goodhart's Law.

**Points of tension:**
- Brain #1 dice "DEFERRED — no hay paying customers, Value Risk alto"
- Brain #7 (domain) dice "APPROVED_WITH_CONDITIONS — datos disponibles, calcular ROI async"

### Conflict Resolution

**Why verdicts differ:** Brain #1 evalúa desde VALUE/RISK ("¿Deberíamos construir esto?"). Brain #7 (domain) evalúa desde DATA/INFRASTRUCTURE ("¿Podemos medir esto técnicamente?"). Brain #1 cuestiona el problema de negocio; Brain #7 (domain) asume que el problema es real y se enfoca en la solución técnica.

**Winner:** Brain #1 tiene la posición más fuerte. Brain #7 (domain) asume que "podemos medir costo" = "debemos medir costo", pero ignora la pregunta crítica: "¿El costo es el bottleneck que está bloqueando el éxito AHORA?" Sin evidencia de que los usuarios estén sintiendo pain financiero (preguntas espontáneas, hojas de cálculo manuales, quejas sobre costos), esta feature es **Optimización Prematura** — el anti-patrón que *Lean Analytics* advierte: medir lo que NO importa para tu etapa actual.

**Critical insight from NotebookLM:** El sistema está en etapa de **"Empathy" o "Stickiness"** (validar valor), no de **"Revenue"** (optimizar costos). Intentar optimizar el ROI antes de validar el Product-Market Fit es invertir el orden de las prioridades. El costo de oportunidad es alto: cada hora en trackear centavos = una hora NO en mejorar Delta-T1 o Knowledge Yield.

### Second-Order Concerns

**FEEDBACK LOOP — Goodhart's Law Death Spiral:**
Dashboard muestra "Agente A = $0.50, Agente B = $0.10" → Usuario selecciona Agente B siempre → Knowledge Yield baja (Agente B menos capaz) → Delta-T1 sube → Sistema se vuelve más barato PERO más inútil → ROI real colapsa → Builder abandona el sistema.

Este no es un riesgo teórico. NotebookLM confirma: **Lollapalooza Effect** (Munger) — convergencia de "Super-respuesta a Incentivos" (optimizar costo) + "Evitación de Inconsistencia" (una vez que el dashboard dice que A es "caro", el equipo dejará de usarlo aunque sea el más capaz) = degradación irreversible de la inteligencia del sistema.

**FEEDBACK LOOP — Overhead Cascade:**
Agregar tracking de tokens → cada consulta requiere +1-2 API calls (LLM providers para token counts) → T1 aumenta 50-100ms → Delta-T1 empeora → Feature que debería "optimizar costos" termina COSTANDO más dinero (time = money) → ROI se vuelve negativo → Feature se auto-invalida.

**FEEDBACK LOOP — Substitution Bias (Kahneman):**
El sistema está respondiendo la pregunta fácil ("¿Podemos medir tokens?") en lugar de la pregunta difícil ("¿Es el costo la barrera principal para la adopción?"). WYSIATI — lo que vemos (datos técnicos disponibles) es TODO lo que hay, ignorando lo que falta (evidencia cualitativa de pain financiero).

**CASCADE FAILURE — Trust Erosion:**
Dashboard muestra "ROI Score: 0.2" (bajo) → Builder pierde confianza en el sistema → Deja de usar brain agents → Knowledge Yield cae a 0% → Sistema muere. Sin paying customers NI siquiera, este riesgo es PREMATURO.

**METRIC BLINDSPOT — No "Market Hunger" detection:**
Ningún cerebro propuso medir: "¿Con qué frecuencia los usuarios preguntan espontáneamente por costos?" o "¿Hay evidencia de cálculo manual de costos (hojas de cálculo, scripts)?" Sin esta señal, estamos construyendo para un problema que NO sabemos si existe.

**CROSS-DOMAIN TRADEOFF — Brain #7's telemetry data increases Brain #5's backend complexity:**
Capturar prompt_tokens + completion_tokens requiere integración con LLM provider APIs (OpenAI, Anthropic) para obtener token counts precisos. Backend complexity aumenta → development timeline extends → opportunity cost en Delta-T1 features.

### Metric Proposals

**SLI-1 (The Mom Test — Market Hunger):** Frecuencia de preguntas espontáneas sobre costos. Target: ≥5 preguntas/semana sobre "¿Cuánto me costará esto?" antes de construir dashboard. Measurement: Contar preguntas en Slack/Discord/GitHub issues. Si <1/semana → DEFERRED.

**SLI-2 (Proxy de Desperdicio):** Porcentaje de ejecuciones que consumen 80% de tokens sin mejorar Knowledge Yield. Target: Si el 20% de ejecuciones consumen el 80% de tokens Y knowledge_yield < 0.3 → existe ineficiencia sistémica que justifica control financiero. Measurement: Query sobre `experience_records` agrupado por token_count vs quality_score.

**SLI-3 (T1 Overhead Guardrail):** Aumento de Delta-T1 por tracking overhead. Target: <1-2% aumento. Si >5% → feature se auto-invalida. Measurement: Delta-T1 promedio 7 días antes vs. después de activar tracking.

**OKR-1 (Threshold de Retención):** Si retención cae y entrevistas de salida citan "incertidumbre de costos" como razón principal → invertir prioridades inmediatamente. Target: 0% churn por costo hasta Phase 15+.

**OKR-2 (Signal-to-Noise Ratio):** Porcentaje de decisiones de agente cambiadas por dashboard de costos. Target: ≥40% de decisiones realmente cambian. Si <10% → dashboard es ruido, no signal.

### Verdict

**DEFERRED** — Delta-Velocity Rating 5 (Principal). La propuesta es técnicamente factible PERO estratégicamente prematura.

**Why DEFERRED instead of REJECTED?**
- Los datos técnicos están disponibles (Brain #7 correct: duration_ms, quality_score, JSONB)
- El problema PUEDE ser real en Phase 15+ cuando haya paying customers
- No hay daño en capturar telemetría silenciosa (sin dashboard)

**Why not APPROVED_WITH_CONDITIONS?**
- Brain #7 (domain) propone calcular ROI Score, pero sin revenue ni pricing model, el "R" en ROI es ZERO → ROI Score = (quality × Likelihood) / (Financial_Cost + Time) = (algo) / (0 + algo) = undefined
- Condiciones técnicas (async calculation, evitar Goodhart's Law) no resuelven el problema estratégico: **¿Quién es el usuario que siente pain de costos HOY?**
- Opportunity cost real: cada hora en esto = hora NO en Delta-T1 o Knowledge Yield (los únicos outcomes que validan PMF ahora)

**Conditions for future approval (Phase 15+ o cuando exista UNA de estas señales):**

1. **[BLOCKER] Market Hunger Signal:** ≥5 preguntas espontáneas/semana sobre costos, OR evidencia de cálculo manual (hojas de cálculo, scripts), OR paying customers que piden breakdown de costs.

2. **[BLOCKER] Revenue Model Existence:** Pricing model definido + al menos 1 paying customer. Sin revenue, ROI es conceptual, no real.

3. **[BLOCKER] TOP 3 Outcomes Estables:** Delta-T1 <90s sostenido por 2 semanas, Knowledge Yield >30%, Planning Accuracy >0.75. Solo cuando outcomes core están estabilizados, optimizar costos tiene sentido.

4. **[TECHNICAL] Implementación como Telemetría Primero:** Capturar prompt_tokens, completion_tokens, model_id en `custom_metadata` JSONB SIN exponer dashboard. Construir base de datos histórica ("Inside View") para cuando se necesite.

5. **[TECHNICAL] T1 Overhead <2%:** Verificar que tracking overhead no aumenta Delta-T1 más de 1-2%. Si aumenta más → feature se auto-invalida.

**Roadmap recomendado:**

**Fase 0: Telemetría Silenciosa (1 semana) — PUEDE empezar AHORA**
1. Agregar `prompt_tokens`, `completion_tokens`, `model_id` a `custom_metadata` JSONB
2. NO exponer dashboard, NO calcular ROI Score
3. Solo escribir datos para construcción de "Inside View" histórica

**Fase 1: Detección de Market Hunger (ongoing) — CRÍTICO**
1. Medir SLI-1 (preguntas espontáneas sobre costos)
2. Medir SLI-2 (proxy de desperdicio: 20% ejecuciones consumen 80% tokens?)
3. Si SLI-1 <1/semana Y SLI-2 <30% → continuar en Fase 0

**Fase 2: Dashboard + ROI Score (Phase 15+ o cuando trigger) — Solo si Fase 1 pasa**
1. SI paying customers existen Y Market Hunger ≥5/semana → construir dashboard
2. Calcular ROI Score = (quality_score × Perceived_Likelihood) / (Financial_Cost + Time_Delay)
3. Aplicar guardrails: Goodhart's Law (no optimizar costo como target), T1 Overhead <2%

**Risk if ignored:** Construir dashboard financiero AHORA = sunk cost en UI + backend complexity + risk de Goodhart's Law + overhead en T1 = feature que debería "ahorrar dinero" termina "costando dinero" (time + complexity) + opportunity cost en outcomes que SÍ importan (Delta-T1, Knowledge Yield).

**Source citations:**
- Brain #1 output: "DEFERRED — Value Risk ALTO, Viability Risk ALTO, implementar como Telemetry primero"
- Brain #7 (domain) output: "APPROVED_WITH_CONDITIONS — duration_ms YA capturado, custom_metadata JSONB permite agregar cost metrics"
- NotebookLM Brain #7 sources: Lean Analytics (stage mismatch), Goodhart's Law, Lollapalooza Effect, Action Bias, Hormozi Value Equation, The Mom Test (market hunger), Sunk Cost Fallacy, Opportunity Cost, WYSIATI, Substitution Bias

---
*PROP-003-B Analytics Financiero — Meta-evaluación completa: 2026-04-06*
*Status: DEFERRED hasta Phase 15+ o hasta detectar Market Hunger signal*
*Next review: When SLI-1 ≥5/semana OR when paying customers exist*

## 2026-04-07 — Phase 16 Observability + Real-Time Hub — Evaluation of: Brains #5 #6

### Cross-Domain Synthesis

**Brain #5 (Backend):** Tracing via `tracing` crate (already in Cargo.toml), WebSocket Hub with DashMap Registry, PostgreSQL-first Ghost Mode, gRPC bi-directional streaming. Priority: OBS-01 > RTU-01 > Health > Ghost Mode (nice-to-have).

**Brain #6 (QA):** Prometheus metrics with /metrics endpoint, structured JSON logging, E2E trace propagation test, 1000-connection load test at <100ms broadcast SLA, circuit breaker + retry patterns. Flags 5 monitoring gaps: alerting, dashboards, log aggregation, runbooks, capacity limits.

**Consensus:** PostgreSQL-first (no Redis), structured JSON logging, liveness vs readiness separation, tokio-tungstenite for WS, load testing required.

### Second-Order Concerns

**SYSTEMS GAP — Thundering Herd on Ghost Mode Replay:** 1000 clients reconnecting simultaneously = 1000 concurrent PostgreSQL queries against activity_log. Connection pool max = 20 (Brain #5). Result: pool starvation, replay timeout, disconnect loop. Neither brain identified this cascade. Ghost Mode MUST use in-memory ring buffer, not direct PostgreSQL queries on reconnect.

**SYSTEMS GAP — UnboundedSender is OOM risk:** Brain #5 type contract uses `mpsc::UnboundedSender<ClientMessage>`. Under broadcast load with slow consumers, memory grows without limit. Bounded channel (256 buffer) with disconnect-on-overflow is the correct pattern.

**SYSTEMS GAP — Ghost Mode is NOT nice-to-have:** Brain #5 deprioritizes Ghost Mode to priority 4. But a WebSocket Hub without event replay creates false confidence in delivery. Ghost Mode is an invariant, not a feature. Deprioritizing it while building the Hub is building the pipe without the water.

**SYSTEMS GAP — No max_connections ceiling:** Brain #6 flags this as "monitoring gap" but it is a LAUNCH BLOCKER. Without enforced max_connections, the Hub accepts connections until OOM.

**CONFLICT — gRPC bi-directional streaming:** Brain #5 proposes persistent bi-directional streaming for brain events. This adds 3 failure modes (lifecycle, backpressure, reconnection) for unvalidated benefit. Winner: start with unary gRPC calls, add streaming when metrics prove unary is a bottleneck (Kohavi: measure first).

### Metric Proposals

**SLI-1 (Ghost Mode Replay Latency):** P95 < 500ms for last 100 events. If exceeded, ring buffer implementation is failing.

**SLI-2 (Memory per WS Connection):** < 50KB at steady state, total Hub < 100MB at 1000 connections. If exceeded, connection model has a leak.

**SLI-3 (gRPC Trace Propagation Rate):** 100% of cross-service requests carry trace_id in gRPC metadata. If < 100%, interceptor is broken.

**SLI-4 (Connection Rejection):** Connections beyond max_connections (2000) receive HTTP 429. If connections exceed limit without 429, ceiling is not enforced.

### Verdict

**APPROVED_WITH_CONDITIONS** — Rating 72/100

**Conditions (must resolve before execution):**
1. Elevate Ghost Mode from nice-to-have to co-requirement with RTU-01
2. Replace UnboundedSender with bounded channel (256 buffer)
3. Define max_connections constant (2000 recommended)
4. Specify gRPC trace interceptor BEFORE writing tracing code
5. Defer bi-directional gRPC streaming — use unary first
6. Add thundering herd mitigation (in-memory ring buffer for Ghost Mode)

**Evidence:** 16-BRAIN-OUTPUTS.md lines 49, 72-79, 177, 188, 229

---

## 2026-04-10 — Phase 18 Multi-Channel Gateway — Meta-Evaluation of: Brains #2 #4 #5 #6

### Cross-Domain Synthesis

**Domain Brain Outputs Received:**
- Brain #2 (UX Research): 3-pane inbox (Channels → Thread List → Active Thread), keyboard-first navigation (J/K), color-coded channel signifiers, chunking over filtering (7±2 threads), DLQ retry inline
- Brain #4 (Frontend): MessageStore (Zustand + Immer + persist), react-virtuoso for 1000+ messages, Web Worker for Email HTML parsing, targeted selector useMessage(id), RAF batching
- Brain #5 (Backend): Rust webhook gatekeeper (Axum + HMAC), in-memory tokio::sync::mpsc queue, DLQ with retry worker, idempotency via UNIQUE constraint, ACL pattern, gRPC to Python
- Brain #6 (QA): Idempotency tests, DLQ retry tests, load tests (1000 webhooks/sec, p99 < 200ms), soak tests (1-hour), SLO: 99.9% webhook ACK within 200ms

**Points of Agreement:**
1. DLQ is critical, not optional
2. Idempotency is mandatory (duplicate webhooks WILL occur)
3. Rust handles webhooks/routing, Python handles AI
4. Channel-specific UI components (not generic)
5. Webhook verification (HMAC) is security-critical

**Points of Tension:**
- Frontend wants Web Worker for Email HTML parsing (NEW infrastructure — zero Worker pattern in codebase today)
- Backend wants in-memory queue (MVP) but QA wants 99.9% reliability — in-memory queue loses data on crash
- UX wants keyboard navigation (J/K) but Frontend hasn't specified keyboard event handling
- Backend proposes ACL pattern but doesn't specify WHO owns the Protobuf schema (Rust? Python? Shared?)

**Shared Assumptions (Never Questioned):**
1. WebSocket hub from Phase 16 will handle real-time updates (no one verified if ws/hub.rs can scale to 1000+ webhooks/sec)
2. Python AI worker exists and can consume via gRPC (no one verified if gRPC server in apps/api can handle webhook volume)
3. PostgreSQL can handle idempotency UNIQUE constraint at 1000 webhooks/sec (no benchmark data)
4. "Unified inbox" means single UI, but no one specified cross-channel threading (same customer on WhatsApp + Instagram = 1 thread or 2?)

### Second-Order Concerns

**FEEDBACK LOOP — Queue Backup → Webhook Storm (Reinforcing):**
Rust webhook receiver → tokio::sync::mpsc queue → Python AI worker → response. If Python worker is slow (AI processing), queue fills up → Rust webhook receiver blocks → external APIs (WhatsApp/Instagram) timeout → webhook storms (they retry furiously). This is a POSITIVE feedback loop that creates cascade failure. Balfour: "Design for failure, not for success."

**FEEDBACK LOOP — LocalStorage Quota → Silent Data Loss (Hidden Failure):**
Frontend MessageStore with persist → localStorage has 5-10MB limit. If user has 1000+ threads with rich HTML email bodies, localStorage fills → persistence fails → user loses drafts on refresh. This is a HIDDEN failure mode (localStorage quota is silent, not loud). Munger: "Inversion — what would cause silent data loss?"

**FEEDBACK LOOP — DLQ Thundering Herd (Reinforcing):**
DLQ retry worker → if backend has transient bug (e.g., schema migration in progress), ALL messages fail → DLQ fills → retry worker keeps retrying → thundering herd problem. No exponential backoff strategy specified. Kohavi: "Without backoff, you amplify failure."

**CASCADE FAILURE — Rust Crash → 100% Message Loss:**
If Rust Control Plane crashes (OOM, panic), in-memory queue is LOST → 100% message loss. No recovery mechanism specified. This violates Brain #5's "Zero Message Loss" success criterion. Munger: "Never bet the ranch on a single point of failure."

**CASCADE FAILURE — PostgreSQL UNIQUE Constraint Violation → Infinite Loop:**
If UNIQUE constraint on (external_message_id, channel) is violated (race condition), webhook fails → DLQ → retry → same violation → infinite loop. No conflict resolution strategy. Kohavi: "Idempotency without conflict resolution is half a solution."

**CASCADE FAILURE — WhatsApp Rate Limit → Memory Exhaustion:**
WhatsApp API has strict rate limits (1000 messages/day for some tiers). Rust keeps accepting webhooks → queue backs up → DLQ fills → memory exhaustion. No rate limiting at ingress specified. Balfour: "Growth systems must have rate limits built-in, not bolted on."

**SYSTEMIC GAP — Frontend O(n) Grouping:**
UX wants "group by agent ownership" NOT just channel. Frontend proposed O(1) useMessage(id) selector, but grouping is O(n) per render if done in frontend. No one specified WHERE the grouping happens (frontend vs backend). Tradeoff: Frontend grouping = fast but scales poorly. Backend grouping = scalable but new API endpoint. No decision made.

**SYSTEMIC GAP — Stateless Rust vs Stateful Python:**
Backend optimized for stateless webhook receivers (good for scaling) but Python AI worker needs to maintain conversation context (stateful). If Python crashes, conversation context is LOST. No persistence strategy for conversation state. Balfour: "Stateless ingress + stateful processing = state persistence requirement."

**SYSTEMIC GAP — Cross-Channel Thread Merge Logic:**
"Unified inbox" value prop is cross-channel threading (same customer on WhatsApp + Instagram = 1 thread). NO ONE specified how this works. Heuristic? Customer ID mapping? Manual merge? This is the CORE value prop and it's completely undefined. Kohavi: "If you can't measure it, you can't build it."

**METRIC BLINDSPOT — Queue Depth (Early Warning):**
NO ONE proposed measuring "queue depth" (tokio::sync::mpsc channel capacity usage). Queue filling up = early warning of Python worker bottleneck. Without this, you don't know you're failing until webhooks start timing out. Balfour: "Leading indicators > Lagging indicators."

**METRIC BLINDSPOT — End-to-End Latency (User-Facing):**
NO ONE proposed measuring "time from webhook received to AI response sent" (not just webhook ACK latency). Webhook ACK <100ms is meaningless if AI response takes 30 seconds. Kohavi: "Optimize the metric the user cares about, not the metric the system exposes."

**METRIC BLINDSPOT — LocalStorage Quota (Silent Failure):**
NO ONE proposed measuring "localStorage quota usage" (MB used vs MB available). This is a silent failure mode — you don't know it's broken until users lose data. Munger: "Measure what can kill you, even if it's unlikely."

**METRIC BLINDSPOT — DLQ Recovery Success Rate:**
NO ONE proposed measuring "DLQ recovery success rate" (what % of DLQ messages actually recover after retry?). DLQ without recovery = dead letter graveyard, not recovery queue. Kohavi: "A queue that never empties is a bug, not a feature."

**METRIC BLINDSPOT — Cross-Channel Thread Merge Accuracy:**
NO ONE proposed measuring "cross-channel thread merge accuracy" (if customer A on WhatsApp = customer A on Instagram, do we show 1 thread or 2?). This is the CORE value prop of "unified inbox" and it's unmeasured. Balfour: "If you can't measure your differentiation, you don't have a product."

### Metric Proposals

**SLI-1 (Overall Evaluation Criteria - OEC):**
Users respond to multi-channel messages within 5 minutes (webhook received → AI response sent → user reply). Balance technical reliability (99.9% webhook ACK) with user behavior (response time). Kohavi: OEC must be defined BEFORE launch.

**SLI-2 (Queue Depth - Early Warning):**
Queue depth <50% of tokio::sync::mpsc capacity P95. If exceeds → HALT new webhooks (return 503) or scale Python workers. Leading indicator of cascade failure.

**SLI-3 (End-to-End Latency - User-Facing):**
Webhook received → AI response sent <30 seconds P95. NOT just webhook ACK <100ms. This is the metric users actually experience.

**SLI-4 (LocalStorage Quota - Silent Failure):**
LocalStorage usage <80% of available quota (5-10MB). Alert at 80%, block persistence at 90%. Prevents silent data loss.

**SLI-5 (DLQ Recovery Success Rate):**
DLQ recovery success rate >80% (messages that recover after 1 retry). If <50% → DLQ is broken, not recovering. Investigate root cause instead of retrying endlessly.

**SLI-6 (Cross-Channel Thread Merge Accuracy):**
Cross-channel thread merge accuracy >90% (same customer on WhatsApp + Instagram = 1 thread). If <70% → "unified inbox" is broken. Manual merge fallback required.

**OKR (Web Worker Validation):**
Fake Door test on Email HTML parsing. Show "Email preview generating..." loading state (no Worker) vs actual parsed preview (Worker). Measure user perception difference. If <10% notice → drop Worker complexity.

**OKR (Queue Persistence Trigger):**
Launch in-memory queue (MVP). Measure crash frequency (Rust OOM/panic). If >1 crash/week → migrate to Redis Streams for durability. Data-driven decision, not assumption-driven.

**OKR (Cross-Channel Threading MVP):**
Launch with MANUAL thread merge first (user selects "Merge threads"). Measure merge frequency. If <5% of users merge → cross-channel threading is NOT a core need. Drop "unified" differentiator, focus on single-channel excellence.

### Verdict

**APPROVED_WITH_CONDITIONS** — Delta-Velocity Rating 3.0 (Junior/Peer boundary)

**Evidence Citation:**
- Brain #2 UX: 3-pane layout, keyboard navigation, DLQ inline (✅ strong user experience foundation)
- Brain #4 Frontend: MessageStore, react-virtuoso, RAF batching (✅ performance patterns proven in Phase 17)
- Brain #5 Backend: Rust webhook gatekeeper, ACL pattern, idempotency (✅ reliability patterns sound)
- Brain #6 QA: Load tests, DLQ tests, SLOs (✅ measurement strategy comprehensive)

**Conditions (Must-Address Before Launch):**

1. **DEFINE Cross-Channel Thread Merge Logic:** This is the CORE value prop and it's completely undefined. Manual merge? Heuristic? Customer ID mapping? Launch with manual merge first, measure frequency, automate if >20% usage.

2. **IMPLEMENT Queue Depth Monitoring:** Queue depth <50% capacity P95. Alert at 75%, reject webhooks at 90%. Without this, you're flying blind into cascade failure.

3. **ADD End-to-End Latency SLI:** Webhook → AI response <30s P95. NOT just webhook ACK <100ms. This is the user-facing metric.

4. **ADD LocalStorage Quota Monitoring:** <80% usage alert, block persistence at 90%. Prevents silent data loss disaster.

5. **DECIDE Frontend vs Backend Grouping:** UX wants "group by agent ownership" — WHERE does this happen? Frontend O(n) or backend O(1)? Tradeoff decision required before implementation.

6. **DEFIN DLQ Retry Backoff Strategy:** No exponential backoff specified → thundering herd risk. Implement: retry 1 (1s), retry 2 (5s), retry 3 (30s), then DLQ.

7. **BENCHMARK PostgreSQL UNIQUE Constraint:** 1000 webhooks/sec with UNIQUE constraint on (external_message_id, channel) — no proof this works. Run k6 test BEFORE launch.

**Defer to Later Phase (Non-Blocking):**
- Web Worker for Email HTML parsing (Fake Door test first — if <10% notice, drop complexity)
- Redis Streams migration (trigger: >1 Rust crash/week)
- Automated cross-channel threading (trigger: >20% manual merge usage)

**Anti-Mediocre Synthesis — Conflict Resolution:**
- CONFLICT: Frontend wants Web Worker (new infrastructure) vs Brain #7 wants simplicity. Winner: Brain #7 — Fake Door test first. If users don't notice parsing difference, Worker is over-engineering.
- CONFLICT: Backend wants in-memory queue (MVP) vs QA wants 99.9% reliability. Winner: Backend — launch in-memory, add queue depth monitoring, migrate to Redis ONLY if crash data shows need.
- CONFLICT: UX wants keyboard navigation vs Frontend hasn't specified event handling. Winner: UX — keyboard navigation is P0 for expert efficiency (Brain #2's 5s Time-to-First-Response target). Frontend MUST implement keyboard event handling.

**Second-Order Risk Assessment:**
- Queue backup → webhook storm loop: 🔴 HIGH RISK (unaddressed by all brains)
- LocalStorage quota silent failure: 🔴 HIGH RISK (unaddressed by all brains)
- DLQ thundering herd: 🟡 MEDIUM RISK (partially addressed by Brain #5, missing backoff)
- Rust crash → 100% message loss: 🔴 HIGH RISK (unaddressed by all brains)

**Pareto Prioritization (MVP Scope):**
- 20% of work = 80% of value:
  1. Rust webhook gatekeeper with HMAC verification (Security)
  2. Idempotency via UNIQUE constraint (Reliability)
  3. DLQ with manual retry (Recovery)
  4. 3-pane inbox UI (UX foundation)
  5. Channel-specific message components (Visual differentiation)
- Defer to post-MVP:
  - Web Worker for Email HTML (measure first)
  - Automated cross-channel threading (manual first)
  - Redis Streams (in-memory first)
  - Keyboard navigation (can add later)

**Final Recommendation:**
APPROVE with 7 must-address conditions. The domain brains did excellent work on first-order architecture (webhook flow, UI layout, testing). However, second-order effects (queue backup loops, localStorage quota, DLQ thundering herd) are unaddressed. Implement the 7 conditions above, measure SLIs, and iterate post-launch. This is a SOLID 3.0/5.0 — better than junior, not yet peer-level due to missing second-order analysis.


---

## 2026-04-11 — Phase 18 Multi-Channel Gateway — Evaluation of: Brains #2 #4 #5 #6

### Cross-Domain Synthesis

**Domain Brain Outputs Received:**
- Brain #2 (UX Research): 3-pane inbox layout, keyboard navigation (J/K), DLQ retry inline, progressive disclosure for channel-specific tools
- Brain #4 (Frontend): messageStore with Map + Immer + RAF batching, react-virtuoso for 1000+ messages, Web Worker for Email HTML parsing, O(1) targeted selectors
- Brain #5 (Backend): Rust webhook receiver with HMAC verification, tokio::sync::mpsc bounded queue for MVP, PostgreSQL UNIQUE constraint for idempotency, DLQ with exponential backoff (1s → 5s → 30s)
- Brain #6 (QA/DevOps): k6 load testing (1000 webhooks/sec), DLQ retry testing with chaos pattern, Prometheus metrics, SLO: 99.9% webhooks acknowledged within 200ms p99

**Points of Agreement:**
1. Rust for webhook receiver (high-performance gateway)
2. In-memory queue for MVP (tokio::sync::mpsc)
3. PostgreSQL UNIQUE constraint for idempotency
4. DLQ with exponential backoff (1s → 5s → 30s)
5. messageStore with RAF batching pattern
6. react-virtuoso for virtualization
7. k6 load testing before launch

**Points of Tension (RESOLVED):**
- Queue architecture: Brain #5 wins — in-memory MVP acceptable with migration path
- Frontend filtering: Brain #4 wins — O(n) MVP acceptable with measurement trigger
- DLQ retry: Brain #5 wins — 3 retries hardcoded for MVP (simplicity)

**Shared Assumptions (Never Questioned):**
1. "In-memory queue is acceptable for MVP" — NO DATA on crash frequency
2. "Frontend O(n) filtering will work for <1K threads" — NO LOAD TESTING to prove this
3. "WhatsApp/Instagram/Email APIs are similar enough to share infrastructure" — NO PROOF that unified schema won't leak
4. "Manual cross-channel threading is sufficient for MVP" — NO USER RESEARCH to validate this
5. "LocalStorage quota won't be a problem" — NO MEASUREMENT of actual quota usage
6. "tokio::sync::mpsc exists in the codebase" — **FALSE** (CODEBASE VERIFICATION FAILED)

### Second-Order Concerns

**FEEDBACK LOOP #1 — Efficiency-Fragility Loop (Reinforcing):**
High-speed ingress (1000 webhooks/sec) → PostgreSQL bottleneck (UNIQUE constraint) → In-memory queue swells → Crash → Data loss spiral. CRITICAL GAP: No alerting when queue rejection rate spikes → Silent data loss. When queue rejects webhooks, external providers retry with EXPONENTIAL backoff → Thundering herd 30-60 minutes later → Perpetual DLQ cycle.

**FEEDBACK LOOP #2 — Draft Persistence → Churn Loop (Balancing):**
LocalStorage quota fills → Draft save fails → User re-types complex message → Perceived effort increases → Churn. Users learn NOT to trust the system → Abandon long-form composition → Feature atrophy.

**FEEDBACK LOOP #3 — O(n) Filter → Backend Migration Loop (Reinforcing):**
Frontend O(n) filtering → Thread count grows → Render time >500ms → Backend migration → Unexpected complexity → Delay. Migration complexity underestimated (requires backend API, cursor pagination, cache invalidation) → Frontend blocked → User-visible regression.

**CASCADE FAILURE #1 — Schema Leak (Lollapalooza Effect):**
Unified message schema → Email attachment field → WhatsApp logic breaks → Cross-channel contamination. "Unified schema" becomes leaky abstraction → Every new channel requires breaking changes → Technical velocity degrades O(n²) with channel count.

**CASCADE FAILURE #2 — In-Memory Queue Crash → Business Impact:**
Pod crash → 1000 pending webhooks lost → Business impact measurement → User trust erosion. "High reliability" perception masks "Low durability" reality → Users discover system is unreliable when it matters most → Trust erosion permanent.

**OMISSION BIAS — Missing OEC (Kohavi):**
NO OEC defined. Without OEC, team will "P-hack" success (cherry-pick 99.9% acknowledgment metric while ignoring draft loss rate). Kohavi's non-negotiable: OEC must be defined BEFORE launch.

**OMISSION BIAS — Missing Guardrail Metrics:**
Queue rejection rate, draft save error rate, pending webhook count — NONE of these in plan. Vanity metrics (99.9% acknowledgment) hide systemic risks.

**CRITICAL IMPLEMENTATION BLOCKER:**
Plan 18-01 Task 2 assumes tokio::sync::mpsc exists in codebase. CODEBASE VERIFICATION: ZERO matches. This is a BLOCKER for execution.

### Metric Proposals

**SLI-1 (Queue Rejection Rate — Guardrail):**
`webhook_queue_rejection_total{channel} / webhook_received_total{channel} < 0.05` → Alert immediately. Prevents silent data loss.

**SLI-2 (Draft Save Error Rate — Guardrail):**
`draft_save_error_total / draft_save_attempt_total < 0.01` → Alert immediately. Prevents draft loss churn.

**SLI-3 (Pending Webhook Ratio — State Recovery):**
`webhook_pending_total{state="memory"} / webhook_received_total < 0.05` → If exceeds, trigger Redis Streams migration. Dashboard this metric.

**SLI-4 (Channel If/Else Ratio — Schema Leak):**
`channel_if_else_ratio = lines_of("if channel == whatsapp") / total_lines < 0.20` → Alert if schema becomes leaky.

**SLI-5 (Thread List Render P99 — Migration Trigger):**
`thread_list_render_p99_ms < 500` → If exceeds, trigger backend O(1) filtering migration.

**OEC (Overall Evaluation Criteria):**
Users successfully merge/reply to cross-channel threads within 10 minutes of first login. Balances technical metrics (99.9% acknowledgment) with user outcomes (activation rate).

### Verdict

**APPROVED_WITH_CONDITIONS** — Delta-Velocity Rating 3.0 (Junior-Senior boundary)

**Why not APPROVED (4.0+)?**
- Critical implementation blocker: tokio::sync::mpsc NOT in codebase
- Missing guardrail metrics: Queue rejection rate, draft save error rate, pending webhook count
- Schema leak risk: Unified message abstraction not validated
- Omission Bias: No OEC defined

**Why not REJECTED_REVISE (2.0-)?**
- Strong domain consensus (4 brains aligned)
- Proven patterns (RAF batching verified, WebSocket hub verified)
- Explicit migration triggers (O(n) → O(1), in-memory → Redis)
- Measurable acceptance criteria

**Conditions (Must Fix Before Execution):**
1. **CRITICAL:** Verify tokio::sync::mpsc dependency exists (Plan 18-01 Task 2)
2. **HIGH:** Add guardrail metrics (queue rejection rate, pending webhook count, draft save error rate)
3. **HIGH:** Add LocalStorage error handling with in-memory fallback (Plan 18-07 Task 1)
4. **MEDIUM:** Add channel-specific message structs (Plans 18-04/18-05/18-06)
5. **LOW:** Define OEC before launch

**Evidence Citations:**
- Domain outputs: 18-BRAIN-OUTPUTS.md lines 6-356
- Codebase verification: brainStore.ts lines 44-66 (RAF batching VERIFIED), tokio::sync::mpsc (NOT FOUND)
- NotebookLM analysis: Efficiency-Fragility Loop, Draft Persistence → Churn, Schema Leak

**Anti-Mediocre Synthesis Applied:**
- TENSION #1 (Queue): Brain #5 wins — in-memory MVP acceptable
- TENSION #2 (Filtering): Brain #4 wins — O(n) MVP acceptable
- TENSION #3 (DLQ Retry): Brain #5 wins — 3 retries hardcoded for MVP
