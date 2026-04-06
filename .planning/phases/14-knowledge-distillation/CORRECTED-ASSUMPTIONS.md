# Phase 14 — Corrected Assumptions

> Assumptions verified against IMPLEMENTED-REALITY.md

## Assumption 1: "ExperienceLogger needs to be built"

**CORRECTION:** ❌ FALSE — Already exists at `apps/api/mastermind_cli/experience/logger.py`

**Reality:**
- Full async API with `log_execution()`, `get_recent_by_brain()`, `search_by_trace_context()`
- Database schema exists with `experience_records` table
- PII redaction built-in via `redact_for_storage()`
- Zero records because brains don't call it yet

**Implication:** Phase 14 focus is WIRING, not greenfield implementation

---

## Assumption 2: "Delta-velocity is abstract — we need to define it"

**CORRECTION:** ❌ FALSE — Already defined in BRAIN-FEED-01 + BRAIN-FEED-07

**Reality:**
- T1 baseline: 210-270s (pre-migration manual workflow)
- Delta-velocity = T1(first consultation) - T1(second consultation with memory)
- Target: sub-90s after learning kicks in
- Profitability threshold: T1 > 300s = agent-unprofitable

**Implication:** Metrics are defined. Need IMPLEMENTATION, not definition.

---

## Assumption 3: "Need to build brain agent architecture"

**CORRECTION:** ❌ FALSE — 7 brain agents already exist

**Reality:**
- `.claude/agents/mm/brain-0{1..7}-*/` — 22 files total
- All read `global-protocol.md` for stack/architecture constraints
- ExperienceLogger CLI exists but unused by brains

**Implication:** Phase 14 modifies EXISTING brain workflow, doesn't create new agents

---

## Assumption 4: "Dashboard is primary deliverable"

**CORRECTION:** ⚠️ PARTIAL — KD-03 requires dashboard, but KD-01 + KD-02 are backend loops

**Reality:**
- KD-01: Auto-evaluation loop (Brain #7 → feedback → memory adjustment) — NO dashboard
- KD-02: Template generation (successful interactions → reusable patterns) — NO dashboard
- KD-03: Dashboard (patterns, insights, correlations, trends) — YES dashboard

**Implication:** Dashboard is LAST requirement (KD-03), not first. Focus on loop first.

---

## Assumption 5: "Need NLP/AI for pattern extraction"

**CORRECTION:** ❌ UNKNOWN — Need brain consultation

**Question for Brain #1 + #5:**
- Is simple clustering sufficient? (group by brief similarity, success rate)
- Or do we need embedding-based similarity search?
- pgvector is available (v3.0 stack) — should we use it?

---

## Assumption 6: "Brain #7 already evaluates everything"

**CORRECTION:** ❌ FALSE — Brain #7 evaluates during PLANNING (Moment 2 + 3), not PRODUCTION

**Reality:**
- Today: Brain #7 runs in `/mm:plan-phase` (domain consultation) + `/mm:execute-phase` (validation)
- Not today: Brain #7 runs AFTER orchestration session completes

**Implication:** KD-01 requires NEW workflow hook — post-session evaluation

---

## Verified Constraints

1. **Stack hard-lock:** Python 3.14 + uv, no pip/poetry (from global-protocol.md)
2. **Database:** SQLite today, PostgreSQL 16 + pgvector in v3.0 (Phase 15)
3. **No new frameworks:** Only use what's in `uv.lock` + `pnpm-lock.yaml`
4. **T1 profitability:** T1 > 300s = agent-unprofitable (hard business constraint)
5. **No ML training:** Template extraction = pattern clustering, NOT neural network training (out of scope)

## Open Questions for Brains

1. **Brain #1:** What defines a "template"? When is an interaction "successful" enough to template-ize?
2. **Brain #5:** How does Brain #7 get triggered after session? Hook in `StatelessCoordinator`? Separate cron job?
3. **Brain #6:** How do we TEST that learning improves T1? A/B test with memory disabled?
4. **Brain #7:** What's the evaluation rubric for "did this brain output deserve to be remembered"?
