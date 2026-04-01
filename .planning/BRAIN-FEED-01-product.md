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
