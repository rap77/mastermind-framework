# BRAIN-FEED-01 — Product Strategy Domain Feed

> Written by Brain #1 (Product Strategy). Read-only for other agents.
> Orchestrator reads this after all domain feeds to write BRAIN-FEED.md (global synthesis).
> Last updated: 2026-03-28

---

## Strategic Anchors — v2.2 Foundation Facts

- Builder IS the user — no external users. Optimize for developer-architect workflow, not general consumer UX.
- T1 reduction = ROI metric — pre-migration baseline: 210-270s. Agent value = further reduction, not rescue of unprofitable flows.
- v2.2 — not greenfield: 7 brain bundles authored (Phase 09), 4 War Room screens shipped (v2.1), 575+407 test baseline established.

---

## 2026-03-28 — v2.2 / Phase 09 — Notification System Feature Evaluation

### Verified Insights

**Feature evaluated:** Notification system (toast alerts, notification center, badge counters)
**Codebase state:** Zero notification infrastructure exists. No toast library in pnpm-lock.yaml. The word "notification" does not appear in any .ts/.tsx file.
**ROADMAP state:** No notification item in any of the 4 v2.2 phases (09-12).

**Verdict: NO-GO — confirmed by knowledge base query + grep verification**

Reasoning chain (survives all 4 Cagan risk dimensions):

1. Value Risk — FAILS: Real-time WS updates already exist in Command Center and The Nexus. For a single-user internal tool where the user just invoked the agent they are watching, the information delta added by a notification system is zero. No unseen state — the user is present.

2. Usability Risk — NOT APPLICABLE: There is no usage pattern to observe. The feature doesn't exist and the user pain hasn't been reported.

3. Feasibility Risk — PASSES: Sonner or shadcn/toast could be added without stack violation. But feasibility is not a reason to build something that solves no problem.

4. Viability Risk — FAILS: Every hour spent on toast/badge logic is an hour stolen from Phase 09-12 brain agent infrastructure (currently 10% complete). Opportunity cost is concrete and named.

**Torres OST position:** The correct node in the tree is "Attention Management During Async Latency" — and WS already solves it. A notification system is a premature solution that skips assumption testing.

**Cagan's Build Trap signal:** Building a notification center outputs a visible feature while delivering zero outcome change. The user behavior that would prove value (faster next-step triggering after agent completion) is not blocked by absence of notifications — the Nexus live-updates already provide that signal.

### Deferred Items

📅 Phase 12+ — If brain agents reach >5 min average execution time (async beyond natural attention span), re-evaluate. That is the ONLY condition that would make a notification system non-premature. Measure first. The concierge MVP if needed: browser Notification API (2 lines) — not a toast library — to validate the assumption before building infrastructure.

---

## 2026-03-29 — v2.2 / Phase 11 — Free Trial Onboarding Feature Evaluation

### Verified Insights

**Feature evaluated:** Free Trial flow / new user onboarding experience
**Codebase state:** Zero trial/onboarding/signup/pricing/subscription infrastructure exists. Grep confirms: no `.tsx` or `.py` file contains "trial", "onboard", "signup", "pricing", or "subscription" in app source. Only existing auth is credential login with JWT + httpOnly cookie — single user, no registration, no user roles, no plan tiers.
**ROADMAP state:** No onboarding item in any of the 4 v2.2 phases (09-12). Phase 11 is Smoke Tests. Phase 12 is Parallel Dispatch + Command Update.

**Verdict: HARD REJECT — Build Trap signal confirmed by knowledge base query + grep verification**

Reasoning chain (all 4 Cagan risk dimensions evaluated):

1. Value Risk — FAILS: "Free Trial" solves the pain of Value Risk (will this work for me before I pay?) and acquisition friction. MasterMind has no external users, no payment model, no acquisition funnel. The builder IS the user. There is no one to convert. The information delta added by a trial flow is zero.

2. Usability Risk — NOT APPLICABLE: No external users exist to observe usage patterns. The single user already has full access and full context.

3. Feasibility Risk — PASSES: The stack could support it (Next.js auth, FastAPI user model). But feasibility is never a reason to build something that solves no problem.

4. Viability Risk — FAILS: A Free Trial is a growth engine component (paid or viral). MasterMind has neither. This is viability-negative. Every hour spent on trial/onboarding UI is an hour stolen from Phase 11-12 brain agent infrastructure.

**Torres OST position:** There is no validated opportunity node in the tree that maps to "Free Trial." The only valid opportunity in scope is "T1 reduction for the builder." A trial flow does not reduce T1 — it increases friction between the user and the War Room screens.

**Cagan Build Trap signal:** The request maps exactly to the Build Trap pattern: an output (Free Trial flow) was proposed without naming an outcome (what user behavior would change, measured how). This is "achieving failure" — successfully executing a plan that was flawed at the root.

### Deferred Items

📅 v3.0+ — If MasterMind pivots to multi-user or commercial product, the correct sequence is: (1) validate external user demand with a Concierge MVP (no code), (2) measure activation rate before building onboarding infrastructure, (3) only then spec the auth/registration/plan-tier model. The current `(auth)/login/` route is the seed — extend it then, not now.

---

## 2026-03-31 — v3.0 Planning / Agent Restructuring — Autonomous Brain Agents Plan Evaluation

### Verified Insights

**Plan evaluated:** Reestructuración a Agentes Autónomos (6 phases — brain_memory.py, experiences.py route, task_runner.py, brain_router.py, POST /api/tasks/auto, replicate to #2-#7)

**Codebase state verified:**
- `ExperienceLogger` is fully implemented at `apps/api/mastermind_cli/experience/logger.py` — `log_execution()`, `get_recent_by_brain()`, `search_by_trace_context()` all exist. 0 records because nothing calls it.
- `create_experience_schema()` exists in `database.py:305` — NOT called in `startup_event` (app.py:136 only calls `create_task_schema()`). Phase 2 gap confirmed real.
- TODO at `tasks.py:98` — verified. POST /api/tasks creates the execution record and returns `pending` but launches nothing.
- `StatelessCoordinator` exists at `orchestrator/stateless_coordinator.py`. `FlowDetector` exists.
- Brain bundles #1-#7 exist at `.claude/agents/mm/` — 22 files, 3 per domain + global-protocol.md.
- Files the plan creates (brain_memory.py, experiences.py route, task_runner.py, brain_router.py) do NOT exist. Plan claims are accurate.

**Verdict: APPROVED WITH CONDITIONS**

Core justification: The problem is real and verified in code. ExperienceLogger at 0 records IS the pain — every consultation starts cold, which directly inflates T1. The plan fixes the disconnection between the API and actual brain execution, which is the minimum viable wiring to make v2.2 infrastructure do what it was built for.

**Risk map (Cagan 4 dimensions):**

1. Value Risk — LOW (mitigated): The core value proposition (brains that don't start cold) is directly T1-reducing. A second consultation that cites past records eliminates the re-injection of context the user currently does manually. Evidence is measurable: T1 before vs. after pilot with Brain #1.

2. Usability Risk — MEDIUM (unnamed in plan): Phase 4 routing (brain_router.py) is opaque by design. If Brain #1 emits `frontend_implications` and Brain #4 auto-dispatches without surfacing the routing decision to the user, the user loses observability into what triggered. For a single-user internal tool, opaque routing becomes a trust problem — the user starts second-guessing the system and manually verifying every dispatch. The plan has no observability hook for routing decisions.

3. Feasibility Risk — LOW: StatelessCoordinator exists, ExperienceLogger exists, WebSocket infrastructure exists. Phase 3 (task_runner.py) is the highest-complexity piece — async background task with SQLite WAL and WebSocket broadcast. Verified feasible with aiosqlite, but connection lifecycle must be explicit.

4. Viability Risk — MEDIUM (the Meadows risk, unnamed in plan): Memory accumulation without a decay or relevance filter creates Systemic Inertia. Brain #1 will eventually cite outdated records as if they are current truth. The plan has no TTL on experience records, no quality score threshold for citation, and no mechanism to mark records as superseded. This is not urgent for Phase 1 pilot (few records) but becomes a liability by Phase 6 (all 7 brains logging).

**Conditions for approval:**

1. Phase 4 (brain_router.py) — add a routing trace field to WebSocket broadcast. When Brain #4 is dispatched because Brain #1 set `frontend_implications`, that routing decision must appear in the Engine Room as a visible event, not a silent auto-dispatch.

2. Definition of Done — keep the technical DoD ("Brain #1 cites past records on second consultation") as smoke test, but add a behavioral DoD: "A 3-brain flow executes without user re-injection of context, with T1 < 90s user attention time." This aligns with the T1 90-110s target from Phase 12 context.

3. Experience record quality gate — before Phase 6 (replicate to #2-#7), define a minimum quality_score threshold for citation. Records below threshold should be retrievable but not cited. ExperienceRecord model already has `custom_metadata` — use it now, not later.

**Phase execution order — no changes needed.** Phases 1+2 parallel is correct. Phase 3 depends on Phase 2 schema. Phase 4 depends on Phase 3 task_runner. Phases 5+6 last.

### Deferred Items

📅 v3.1+ — Memory decay / TTL on experience records. Not needed for pilot (Brain #1 only, few records). Becomes critical at Phase 6 when all 7 brains are logging. Design the relevance filter before Phase 6, not after.

📅 v3.1+ — Brain #7 as meta-evaluator for experience record quality. Currently Brain #7 evaluates domain outputs. Future: also flags when Brain #1 is citing records that contradict current codebase state (stale memory detection). This requires Brain #7 to have read access to ExperienceLogger — design that interface when scaling to all 7 brains.

---

## 2026-04-04 — v3.0 Milestone Planning — Phase Sequencing + Scope Analysis

### Verified Insights

**Context:** v3.0 milestone "enterprise agent orchestration platform" — PRP proposes 6 phases (0-5) covering UI fork, Rust backend, multi-channel, knowledge distillation, marketplace.

**Codebase verification performed:**
- Paperclip `ui/src/api/` = 24 API files, ALL importing from `@paperclipai/shared` (11 direct imports in api/, 131 total across 122 files)
- `@paperclipai/shared` = `packages/shared/src/index.ts` = 644 lines of TypeScript types (enums, interfaces, schemas)
- Paperclip UI uses Vite (not Next.js) — framework mismatch with MasterMind's Next.js 16 App Router
- Paperclip server = 250 TypeScript files, all Node.js — no Rust code exists anywhere
- Zero gRPC/Protobuf/Rust configuration in MasterMind repo (confirmed: no .toml, no Cargo.toml, no proto files)
- MasterMind's existing Next.js 16 frontend = 4 screens (Command Center, Nexus, Strategy Vault, Engine Room) — already working

**CRITICAL FINDING: Framework Mismatch**
The PRP says "Fork Paperclip UI" but Paperclip's UI uses Vite + React Router, while MasterMind uses Next.js 16 App Router. These are fundamentally incompatible architectures. You cannot "copy pages" from one to the other — the routing model, data fetching (Server Components vs client-only), SSR, and layout system are completely different. This is the single highest-risk assumption in the entire PRP.

**CRITICAL FINDING: Type System Dependency**
Every single Paperclip API call depends on `@paperclipai/shared` types (644 lines). Replacing this with Protobuf-generated types means: (1) define all 644 lines of types as .proto files, (2) generate TypeScript from proto, (3) verify every API call still works. This is a hidden phase the PRP does not account for.

**Phase Sequencing Verdict:**

1. Phase 0 (Fork UI) — SCOPE EXPLOSION RISK. Copying 41 pages + 94 components between incompatible frameworks is not "1-2 weeks." The honest scope is: (a) extract design patterns + UX patterns as documentation, (b) re-implement key patterns in Next.js App Router. This is a REBUILD, not a fork.

2. Phase 1 (Rust Control Plane) — SCOPE EXPLOSION RISK. Combines: Rust greenfield bootstrapping + PostgreSQL migration + Protobuf schema design + gRPC wiring + Auth migration + Event Sourcing. This is 4-5 independent phases compressed into one. Each has its own failure mode that blocks the others.

3. Phase 2 (Orchestration Canvas + Real-time Hub) — PARTIAL DUPLICATION. MasterMind already has React Flow DAG (The Nexus) with WebSocket infrastructure + Zustand RAF batching. Rebuilding this from Paperclip patterns is redundant. The evolution path should be: extend existing Nexus, not replace it.

4. Phase 3 (Multi-channel Gateway) — DEPENDENCY RISK. WhatsApp Business API approval takes 2-6 weeks with Meta. This phase CANNOT start until sandbox access is confirmed. Instagram API requires a Facebook App review. These are external blockers, not engineering tasks.

5. Phase 4 (Knowledge Distillation) — WELL-SCOPED. This leverages what already exists (7 brain agents + experience_records + brain_memory.py + brain_router.py). This is the highest-value, lowest-risk phase and should be pulled earlier.

6. Phase 5 (Marketplace + Enterprise) — PREMATURE. No paying customers exist yet. Building multi-tenant + billing + marketplace before validating that a single LATAM SME will pay is the Build Trap in its purest form.

### Recommended Phase Sequence (corrected)

| Phase | Content | Duration Estimate | Why This Order |
|-------|---------|-------------------|----------------|
| 0 | Vertical Slice: One API path end-to-end (Rust + gRPC + Protobuf + UI) | 2-3 weeks | Validates the ENTIRE integration pattern at minimal scope |
| 1 | Knowledge Distillation Engine | 2-3 weeks | Highest value, leverages existing infrastructure, proves the moat |
| 2 | Rust Control Plane (Core only: Auth + DB + gRPC) | 3-4 weeks | Stripped of Event Sourcing and Adapter Registry — those move to later phases |
| 3 | UI Evolution: Extend existing Next.js + extract Paperclip UX patterns | 3-4 weeks | Not a fork — selective pattern adoption into proven architecture |
| 4 | Multi-channel Gateway (WhatsApp first) | 3-4 weeks | External dependency — start sandbox access in Phase 0, implement when approved |
| 5 | Adapter Registry + Event Sourcing | 2-3 weeks | Foundation for scaling |
| 6 | Template Marketplace + Multi-tenant | 4-6 weeks | Only after paying customers validate the model |

### Deferred Items

📅 Phase 7+ — Org Chart, Company Rail, Onboarding Wizard, Import/Export — enterprise features that have no buyer yet.

📅 Redis — the PRP mentions Redis pub/sub for cross-service broadcast. This is premature for a single-host deployment. Start with SQLite WAL + gRPC, add Redis when multi-instance is needed.

📅 Codex Subscription Panel, Claude Subscription Panel — Paperclip-specific features with no MasterMind equivalent. Drop entirely.

---

## 2026-04-06 — Phase 14 / Knowledge Distillation — Product Strategy Analysis

### Context
**Phase:** Knowledge Distillation (KD-01, KD-02, KD-03)
**Codebase State:** ExperienceLogger EXISTS (0 records), brain_memory.py CLI EXISTS (unused), 7 brain agents EXIST (don't call logger), Delta-velocity NOT tracked, Templates NOT generated, Dashboard NOT built
**Knowledge Base Consulted:** NotebookLM `f276ccb3-0bce-4069-8b55-eae8693dbe75` (Cagan, Torres, Ries, Doerr, Meadows)

### Verified Insights

**1. Template Definition (KD-02) — APPROVED with scope refinement**

A "template" is NOT just text storage — it's a **validated solution structure** following the Product Trio pattern (Context + Intention + Output Structure).

**Definition:** A template captures a brain's **opportunity framing** (the brief) AND its **solution structure** (the output schema) that has demonstrated it reduces uncertainty in planning.

**Success criteria for template-ization:** An interaction becomes a template when Brain #7 assigns it a `quality_score >= 0.8` AND the session results in a **high-integrity commitment** (architectural decision, resource allocation, or directional pivot). This prevents polluting the template library with low-value noise.

**Structure:** Must include BOTH brief AND output structure. The brief = the "opportunity" in Opportunity Solution Tree language. The output structure = the "solution" that was validated. This enables **compare-and-contrast** in future sessions — the brain can say "this is like pattern X but with constraint Y."

**Codebase verification:** `ExperienceRecord.custom_metadata` already supports `quality_score` (line 18 in logger.py whitelist). The precedent template at `apps/api/agents/orchestrator/precedents/template.yaml` provides a structural starting point — adapt it for brain-specific templates.

---

**2. Pattern Extraction — APPROVED with pgvector**

**Decision:** Implement embedding-based similarity using pgvector (available in v3.0 PostgreSQL stack). Keyword clustering is insufficient.

**Rationale:** Knowledge distillation is about identifying patterns in the "opportunity space," not just surface text. Keywords match words; embeddings match **semantic intent**. This is the difference between "database query" (shallow) and "data modeling decision with consistency tradeoffs" (deep).

**Technical implication:** Phase 15 (PostgreSQL migration) MUST include pgvector extension. The `embedding_stub` field in ExperienceRecord (line 62-64 in models.py) is a placeholder — replace with actual vector column in v3.0 schema.

**Anti-pattern:** Do NOT build ML training pipelines. Template extraction is clustering over existing embeddings, not neural network training. Out of scope per REQUIREMENTS.md line 62.

---

**3. Brain #7 Trigger — APPROVED with high-value filter**

**Decision:** Brain #7 should NOT evaluate every session. Only evaluate **high-value interactions** to avoid systemic noise.

**Criteria for high-value:**
1. **Strategic Intent Impact:** Sessions connected to milestone-level objectives (e.g., phase completion, architectural pivots)
2. **High-Integrity Commitments:** Sessions concluding in decisions that require resource investment
3. **Planning Pivots:** Sessions where the user changes direction mid-flow (capturing the "why")

**Implementation:** Add a `high_value` flag to `custom_metadata` during session logging. Set it automatically when:
- Session duration > 5 minutes (indicates complexity)
- Brain #7's planning score changed during the session
- User invoked `/mm:complete-phase` (vs. `/mm:execute-phase`)

**Codebase verification:** Brain #7 currently evaluates during PLANNING (Moment 2+3 in GSD workflow), not PRODUCTION sessions. KD-01 requires a NEW post-session hook — modify `StatelessCoordinator` or create a separate cron job.

---

**4. Dashboard Priorities (KD-03) — TOP 3 METRICS DEFINED**

If only 3 metrics for v1 dashboard, these are the MOST valuable (ranked by outcome impact):

**Metric 1: Delta-T1 (Learning Efficiency)**
- **Definition:** Average session duration vs. 210-270s baseline
- **Why:** This is the PRIMARY outcome metric. T1 reduction = ROI proof
- **Target:** Sub-90s after learning kicks in
- **Visualization:** Time series showing T1 trend over sessions, with vertical markers when templates were applied

**Metric 2: Knowledge Yield (Reuse Rate)**
- **Definition:** Percentage of new sessions that cite or accelerate using a distilled template
- **Why:** Measures system learning viability. If knowledge is never reused, distillation has no value
- **Target:** >30% of sessions should leverage templates by week 4
- **Visualization:** Bar chart: "Sessions with template citation" vs. "Cold start sessions"

**Metric 3: Planning Accuracy (Brain #7 Quality Score)**
- **Definition:** Average Brain #7 score for planning coherence (0.0-1.0)
- **Why:** Guards against "velocity at the cost of quality." Fast but wrong = zero value
- **Target:** Maintain >0.75 average even as T1 decreases
- **Visualization:** Scatter plot: T1 (x-axis) vs. Quality Score (y-axis) per session

**Anti-patterns avoided:**
- ❌ "Total sessions logged" — vanity metric, no outcome signal
- ❌ "Number of templates created" — output, not outcome. 100 unused templates = zero value
- ❌ "Brain execution count" — activity metric, irrelevant to learning

### Deferred Items

📅 Phase 15+ — Memory decay / TTL on experience records. Not needed for Phase 14 pilot (few records). Becomes critical when all 7 brains are logging. Design relevance filter before scaling.

📅 v3.1+ — Cross-brain template sharing. Phase 14 focuses on per-brain templates. Future: Brain #1 can cite Brain #5's backend patterns when discussing frontend-backend tradeoffs.

### Open Questions Requiring Brain Consultation

1. **Brain #5:** What's the post-session evaluation hook? Modify `StatelessCoordinator` to call Brain #7 after session completion, or separate async job?
2. **Brain #6:** How do we A/B test "memory enabled" vs. "memory disabled" to prove T1 improvement? Feature flag in brain_memory.py?
3. **Brain #7:** What's the exact evaluation rubric for template worthiness? Is `quality_score >= 0.8` sufficient, or need additional criteria (e.g., session contained architectural decision)?

