# Brain #7 (Growth & Data) Evaluation — Phase 17

> **Generated:** 2026-04-09T12:30:00Z
> **Evaluator:** Brain #7 (Growth/Data — Systems Thinker)
> **Input:** `.planning/phases/17-ui-evolution/17-PLAN-REVIEW.md`
> **Verdict:** APPROVED_WITH_CONDITIONS

---

## Executive Summary

Phase 17 plans are **well-structured with strong technical foundation** (17-01 complete, RAF batching proven, WebSocket infrastructure exists). However, **three systemic risks** emerge at the systems level:

1. **Feature Bloat Trap:** Extracting 10 UX patterns from Paperclip without validating which ones MasterMind users actually need. Risk: Building for the 1% power users at the expense of the 99% mainstream users.

2. **Performance Optimization Paradox:** Optimizing for 24-brain burst (synthetic load) without real-world concurrency data. Risk: Over-engineering code that's harder to maintain for marginal gain.

3. **Mobile-First Assumption:** Adding mobile features (swipe gestures, bottom nav) without validating mobile usage percentage. Risk: Desktop-first users (80%+) pay complexity tax for features they never use.

**Top Concern:** Plan 17-06 (Onboarding + Mobile Polish) tries to do everything in 5-6 days — WCAG 2.1 AA audit, BrowserStack validation, swipe gestures, bottom nav, onboarding wizard, documentation. This is **unrealistic** given the scope.

**Recommendation:** APPROVE plans 17-02 through 17-05 with conditions. REVISE plan 17-06 to split into 17-06a (Onboarding) + 17-06b (Mobile Polish), or reduce scope to MVP (WCAG 2.1 A only, skip BrowserStack, skip swipe gestures).

---

## Plan-by-Plan Analysis

### Plan 17-02: Multi-tenant Company Switcher

**Planning Fallacy:**
- **Underestimating backend integration:** 3-4 days is optimistic for tenant isolation (Rust + Python + JWT + RLS policies). Realistic: 5-6 days.
- **Hidden complexity:** X-Tenant-ID header spoofing protection requires JWT structure change (add `tenants: []` array). This is a **breaking change** to existing auth flow. Not accounted for in timeline.

**Omission Bias:**
- **Missing rollback plan:** What if tenant isolation breaks existing API endpoints? Plan mentions "make X-Tenant-ID optional (backward compatibility)" but this is in Rollback Plan, not in Task 4. Should be in Task 4 acceptance criteria.
- **Missing data migration:** How do we migrate existing single-tenant users to multi-tenant structure? Do we auto-create a default tenant? Not mentioned.

**Systems Thinking:**
- **Feedback loop:** Company switch → brainStore clear? If user switches from Company A to Company B, do we clear brain state? If not, Company B sees Company A's brain runs (data leak risk). If yes, user loses context (frustration risk). **Plan doesn't address this.**
- **Second-order effect:** Multi-tenant architecture increases API latency (tenant validation overhead). All API requests become slower for single-tenant users (90% of users). **Trade-off not quantified.**

**Over-Engineering Risk:**
- **Draggable company ordering:** Is this a power-user feature that < 10% of users will touch? Plan mentions "drag-and-drop reordering" but doesn't validate user demand. **Recommendation:** Defer to v3.1, ship MVP with static ordering first.

**Acceptance Criteria:**
- ✅ "Integration test proves tenant isolation (user_A cannot access user_B data)" — Verifiable (Playwright test).
- ✅ "Store persists across page refreshes" — Verifiable (Vitest test).
- ❌ "Drag-and-drop reordering works smoothly" — Not quantifiable. What does "smoothly" mean? Should be "DnD completes in < 200ms with visual feedback."

**Verdict:** **APPROVED_WITH_CONDITIONS**

**Conditions:**
1. Add brainStore clear logic to Task 4 (tenant isolation section): "When switching companies, clear brainStore to prevent cross-tenant data leak."
2. Add data migration task to Task 4: "Auto-create default tenant for existing single-tenant users on first login after migration."
3. Defer draggable company ordering to v3.1: Remove @dnd-kit from Task 2, replace with static ordering.
4. Quantify API latency overhead: Add performance test to Task 4: "Measure P99 latency increase for tenant validation (target: < 5ms overhead)."

---

### Plan 17-03: ActiveAgentsPanel with Density Modes

**Planning Fallacy:**
- **Underestimating BrowserStack setup:** 4-5 days is optimistic for ActiveAgentsPanel + RAF validation + BrowserStack swipe gestures. BrowserStack account creation ($39/month), device configuration, test debugging — this is **2-3 days alone**. Realistic: 6-7 days.

**Omission Bias:**
- **Missing RAF monitor implementation:** Plan mentions "Create RAFMonitor class" in Task 4 but doesn't specify **where** it lives (utils? component?), **how** it measures P99 frame time (Performance API? Custom instrumentation?), or **what** the baseline is (current frame time without optimization?).
- **Missing swipe gesture fallback:** What if swipe gestures fail on real devices? Plan mentions "fallback to button actions" in Rollback Plan but not in Task 5. Should be in Task 5 acceptance criteria.

**Systems Thinking:**
- **Feedback loop:** Density mode → mobile swipe? If user is in "detailed" mode on desktop, then opens mobile, do we force switch to "compact" mode? If yes, user loses preference. If no, mobile UI breaks (detailed mode doesn't fit). **Plan doesn't address this.**
- **Second-order effect:** 3 density modes increase cognitive load. Users spend time choosing mode instead of monitoring brains. Hick's Law violation: 3 choices = 1.5x decision time vs 2 choices.

**Over-Engineering Risk:**
- **3 density modes:** Is "detailed" mode overkill? Plan shows detailed mode has "full stats (tokens, duration, cost, error count)" — this is a lot of visual noise. **Recommendation:** Reduce to 2 modes (compact/normal) or make "detailed" opt-in (click to expand).

**Acceptance Criteria:**
- ✅ "P99 frame time < 16.67ms during burst update" — Verifiable (RAFMonitor class).
- ✅ "Zero long tasks (> 50ms) in Chrome DevTools" — Verifiable (Performance tab).
- ❌ "Swipe gestures work on mobile panels" — Not quantifiable. Should be "Swipe gesture success rate ≥ 95% on iPhone 14 and Pixel 5 (measured via 100 test swipes)."

**Verdict:** **APPROVED_WITH_CONDITIONS**

**Conditions:**
1. Specify RAFMonitor implementation in Task 4: "Create utils/raf-monitor.ts with RAFMonitor class that measures P99 frame time via Performance API, exports measureFrameTime() and getP99() methods."
2. Add density mode sync logic to Task 3: "When viewport changes from desktop to mobile, auto-switch to compact mode (override user preference). When viewport changes back to desktop, restore previous mode."
3. Reduce to 2 density modes: Remove "detailed" mode from Task 3, keep compact/normal only. (Or make detailed opt-in: click BrainCard to expand.)
4. Quantify swipe gesture success rate in Task 5: "Swipe gesture success rate ≥ 95% on iPhone 14 and Pixel 5 (measured via 100 test swipes, success = action revealed on first swipe)."

---

### Plan 17-04: Cost Dashboard with MetricCard + QuotaBar

**Planning Fallacy:**
- **Underestimating backend complexity:** 3-4 days is **wildly optimistic** for Rust materialized view + Python API + WebSocket + 60fps optimization. This is **5-7 days minimum**. Rust MV creation, trigger implementation, Redis caching, Python API endpoint, WebSocket integration, RAF batching — each is 1+ day.

**Omission Bias:**
- **Missing cost accuracy validation:** How do we verify cost metrics are accurate? Plan mentions "Materialized view refreshes < 1s after new event" but doesn't specify **how** we validate accuracy (compare MV vs raw events? integration test?).
- **Missing WebSocket flood protection:** Plan mentions "server-side rate limiting (max 5 batches/sec), client-side debouncing (100ms)" in Brain-Informed Updates but doesn't specify **where** this logic lives (Rust Hub? Python API? Frontend?).

**Systems Thinking:**
- **Feedback loop:** Cost dashboard → WebSocket load? If cost dashboard streams real-time updates for 24 brains, do we flood WebSocket connection? If yes, other features (brain status, inbox) lag. If no, cost dashboard isn't real-time (misleading UX). **Plan doesn't address bandwidth budget.**
- **Second-order effect:** Hierarchical cost breakdown (per brain → per company → total) increases query complexity. Per-company aggregation = JOIN across tenant_id + company_id. Does this scale? **Plan doesn't address query performance at 100+ companies.**

**Over-Engineering Risk:**
- **Hierarchical cost breakdown:** Is "per company" aggregation necessary? Plan shows "toggle (per brain → per company → total)" — do users need this? Or is "per brain + total" sufficient? **Recommendation:** Validate with user interview, defer per-company aggregation to v3.1.

**Acceptance Criteria:**
- ✅ "Cost dashboard loads in < 100ms (end-to-end)" — Verifiable (Playwright performance test).
- ✅ "P99 frame time < 16.67ms during 24-brain cost update burst" — Verifiable (RAFMonitor).
- ❌ "Materialized view refreshes < 1s after new event" — Not verifiable without test. Should be "Integration test: INSERT into activity_log → wait 1s → SELECT from cost_metrics_mv → verify new brain's cost is present."

**Verdict:** **APPROVED_WITH_CONDITIONS**

**Conditions:**
1. Add cost accuracy validation to Task 1: "Integration test: INSERT into activity_log → wait 1s → SELECT from cost_metrics_mv → verify new brain's cost matches SUM(activity_log.cost_usd) WHERE brain_id = 'new_brain'."
2. Specify WebSocket rate limiting implementation in Task 5: "Add rate limiting to Rust WebSocket Hub (max 5 cost_updates batches/sec), add client-side debouncing to costStore (100ms window via setTimeout)."
3. Defer per-company aggregation to v3.1: Remove "per company" toggle from Task 4, keep "per brain + total" only.
4. Split Task 1 into subtasks: 1a (Frontend: costStore), 1b (Backend: Rust MV), 1c (Backend: Python API). Current Task 1 is too large.

---

### Plan 17-05: Command Palette with Global Search

**Planning Fallacy:**
- **2-3 days is realistic** — Command palette is well-understood pattern (Cmd+K from VSCode, Spotlight, Slack). Fuzzy search (fuse.js or custom) is trivial. Keyboard navigation is standard. **No concerns here.**

**Omission Bias:**
- **Missing keyboard shortcut conflict handling:** What if cmd+k conflicts with browser dev tools (Chrome cmd+k = dev console on Mac)? Plan mentions "Prevent default browser behavior" in Implementation Notes but doesn't specify **which** browsers have conflicts. **Should document known conflicts.**

**Systems Thinking:**
- **Feedback loop:** Command palette → onboarding? Can first-time users access command palette? Plan 17-06 (Onboarding) doesn't mention command palette. **Gap:** New users don't know cmd+k exists. **Recommendation:** Add onboarding hint ("Press ⌘K to search anything") to Plan 17-06 Task 1.
- **Second-order effect:** 50 commands (4 screens + 24 brains + actions + settings) exceeds Miller's limit (7±2 items). Plan mentions "If command list > 100 items, use react-window" but 50 is already a lot. **Recommendation:** Group brains by domain (Product Strategy brains, UX brains, etc.) to reduce cognitive load.

**Over-Engineering Risk:**
- **Fuzzy search:** Is fuse.js necessary? Plan mentions "Option A: fuse.js (battle-tested, but adds dependency), Option B: Custom implementation (lighter, full control)" and recommends Option B. **Good call** — custom implementation is sufficient for 50 commands. **No concern here.**

**Acceptance Criteria:**
- ✅ "Fuzzy search finds commands with typos (e.g., 'strat' → 'Strategy Vault')" — Verifiable (Vitest test).
- ✅ "Debouncing reduces input lag (≤ 300ms)" — Verifiable (Performance API).
- ❌ "Keyboard navigation works (Arrow keys, Enter, Escape)" — Not quantifiable. Should be "Keyboard navigation latency < 50ms (measured via Performance API between keydown and focus update)."

**Verdict:** **APPROVED_WITH_CONDITIONS**

**Conditions:**
1. Add keyboard shortcut conflict documentation to Task 2: "Document known browser conflicts (Chrome Mac: cmd+k = dev console, provide alternative cmd+shift+k)."
2. Add onboarding hint to Plan 17-06 Task 1: "Add 'Press ⌘K to search anything' hint to WelcomeStep in OnboardingWizard."
3. Group brains by domain in Task 3: "Create subcategories under Brains: Product Strategy (4 brains), UX Research (4 brains), UI Design (4 brains), Frontend (4 brains), Backend (4 brains), QA (4 brains)."
4. Quantify keyboard navigation latency in Task 2: "Keyboard navigation latency < 50ms (measured via Performance API between keydown and focus update)."

---

### Plan 17-06: Onboarding Wizard + Mobile Polish

**Planning Fallacy:**
- **5-6 days is UNREALISTIC** — This plan has **8 tasks** covering onboarding wizard, mobile bottom nav, swipe gestures, WCAG 2.1 AA audit, BrowserStack validation, user guide, Storybook stories, cross-browser testing. **This is 10-12 days minimum.**

**Breakdown:**
- Task 1 (OnboardingWizard component): 2-3 days
- Task 2 (onboardingStore + validation): 1 day
- Task 3 (Mobile bottom nav): 1 day
- Task 4 (Swipe gestures): 2-3 days (BrowserStack testing alone is 1+ day)
- Task 5 (WCAG 2.1 AA audit): 2-3 days (full audit is time-consuming)
- Task 6 (BrowserStack validation): 1-2 days
- Task 7 (User guide + Storybook): 1-2 days
- Task 8 (Cross-browser testing): 1-2 days

**Total: 11-17 days, not 5-6 days.**

**Omission Bias:**
- **Missing onboarding completion rate target:** Plan mentions "Onboarding completion rate ≥ 80%" in Success Metrics but doesn't specify **how** we measure this (analytics? event tracking?). **Gap: No analytics integration.**
- **Missing WCAG audit tooling:** Plan mentions "axe-core scan" but doesn't specify **which** axe-core tool (axe DevTools Chrome extension? @axe-core/playwright? axe-core CI/CD integration?). **Gap: No tooling spec.**

**Systems Thinking:**
- **Feedback loop:** Onboarding → activation → retention? If onboarding is too long (4 steps → 3 steps merged), do users drop off? Plan mentions "Drop-off rate ≤ 20% per step" but doesn't model the funnel: 100% → 80% → 64% → 51% (3 steps) vs 100% → 80% → 64% → 51% → 41% (4 steps). **Gap: No A/B test plan to validate 3 vs 4 steps.**
- **Second-order effect:** Mobile features (swipe gestures, bottom nav) increase bundle size. Desktop users (80%+) download mobile code they never use. **Gap: No code-splitting strategy.**

**Over-Engineering Risk:**
- **Swipe gestures:** Are swipe gestures necessary for MVP? Plan mentions "Swipe left reveals actions (edit, delete, archive)" — but do users swipe on desktop? No. This is mobile-only feature. **Recommendation:** Defer swipe gestures to v3.1, ship MVP with button actions only.
- **WCAG 2.1 AA:** Is AA level necessary for MVP? Plan mentions "Zero WCAG Level A violations, ≤ 5 Level AA violations" — but AA is stricter than A (contrast 4.5:1 vs 3:1, focus visible always, etc.). **Recommendation:** Target WCAG 2.1 A only for MVP, iterate to AA based on user feedback.

**Acceptance Criteria:**
- ✅ "Onboarding wizard guides new users through setup (3-5 steps)" — Verifiable (E2E test).
- ✅ "Mobile responsive polish complete (bottom nav, swipe gestures, touch targets)" — Verifiable (Playwright test).
- ❌ "All WCAG 2.1 AA criteria met (zero Level A violations, ≤ 5 AA violations)" — Not verifiable without axe-core tool. Should be "axe-core @axe-core/playwright scan returns zero Level A violations, ≤ 5 Level AA violations."
- ❌ "Swipe gestures validated on BrowserStack (iPhone 14, Pixel 5)" — Not quantifiable. Should be "Swipe gesture success rate ≥ 95% on BrowserStack (measured via 100 test swipes per device)."

**Verdict:** **REJECTED_REVISE**

**Revise Reasons:**
1. **Scope is too large for 5-6 days** — Realistic: 11-17 days. Split into 17-06a (Onboarding) + 17-06b (Mobile Polish), or reduce scope.
2. **WCAG 2.1 AA is overkill for MVP** — Target WCAG 2.1 A only (zero Level A violations), defer AA to v3.1.
3. **Swipe gestures are non-essential for MVP** — Defer to v3.1, ship MVP with button actions only.
4. **BrowserStack validation is non-essential for MVP** — Use device emulators (Chrome DevTools device mode) for MVP, defer BrowserStack to v3.1.
5. **Missing analytics integration** — Add event tracking for onboarding completion rate measurement.

**Revised Scope (MVP):**
- Task 1: OnboardingWizard component (3 steps, not 4) — 2 days
- Task 2: onboardingStore + validation — 1 day
- Task 3: Mobile bottom nav — 1 day
- Task 4: WCAG 2.1 A audit (axe-core @axe-core/playwright, zero Level A violations) — 1 day
- Task 5: User guide (README only, defer Storybook to v3.1) — 1 day

**Total: 6 days (realistic).**

**Deferred to v3.1:**
- Swipe gestures (Task 4)
- BrowserStack validation (Task 6)
- Storybook stories (Task 7)
- Cross-browser testing (Task 8)
- WCAG 2.1 AA (upgrade from A to AA)

---

## Cross-Plan Concerns

### Feedback Loops

1. **Company Switch → Brain State Clear:**
   - **Risk:** User switches from Company A to Company B, brainStore NOT cleared → Company B sees Company A's brain runs (data leak).
   - **Mitigation:** Add brainStore clear logic to Plan 17-02 Task 4: "When switching companies, clear brainStore to prevent cross-tenant data leak."

2. **Density Mode → Mobile Swipe:**
   - **Risk:** User in "detailed" mode on desktop → opens mobile → detailed mode doesn't fit (UI break).
   - **Mitigation:** Add density mode sync logic to Plan 17-03 Task 3: "When viewport changes from desktop to mobile, auto-switch to compact mode (override user preference)."

3. **Cost Dashboard → WebSocket Load:**
   - **Risk:** Cost dashboard streams real-time updates for 24 brains → WebSocket flood → other features (brain status, inbox) lag.
   - **Mitigation:** Add WebSocket rate limiting to Plan 17-04 Task 5: "Server-side rate limiting (max 5 cost_updates batches/sec), client-side debouncing (100ms window)."

4. **Command Palette → Onboarding:**
   - **Risk:** First-time users don't know cmd+k exists → low feature usage → wasted effort.
   - **Mitigation:** Add onboarding hint to Plan 17-06 Task 1: "Add 'Press ⌘K to search anything' hint to WelcomeStep in OnboardingWizard."

### Cascading Failures

1. **WebSocket Hub Failure → All Real-Time Features Break:**
   - **Impact:** ActiveAgentsPanel (17-03) can't show brain status, CostDashboard (17-04) can't stream cost updates.
   - **Mitigation:** Add fallback to polling (GET /api/brains/status every 5s) in both plans. Already mentioned in 17-04 Rollback Plan, should be in 17-03 too.

2. **Tenant Isolation Bug → Cross-Company Data Leak:**
   - **Impact:** Multi-tenant switcher (17-02) fails → User A sees User B's data (security breach).
   - **Mitigation:** Add integration test to Plan 17-02 Task 4: "User A with tenant_A cannot access tenant_B data (403 Forbidden)."

3. **RAF Batching Failure → 60fps Target Missed:**
   - **Impact:** ActiveAgentsPanel (17-03) janks at 24-brain burst, CostDashboard (17-04) janks at cost update burst.
   - **Mitigation:** Add RAFMonitor class to both plans (17-03 Task 4, 17-04 Task 6), measure P99 frame time, if > 16.67ms → fallback to polling (reduce update frequency).

### Resource Bottlenecks

1. **BrowserStack Account ($39/month):**
   - **Bottleneck:** Plan 17-03 Task 6 (BrowserStack mobile validation) + Plan 17-06 Task 6 (BrowserStack mobile validation) both require BrowserStack.
   - **Mitigation:** Share BrowserStack account across plans, or defer 17-06 Task 6 to v3.1 (use device emulators for MVP).

2. **Backend Developer Time:**
   - **Bottleneck:** Plan 17-02 Task 4 (tenant isolation: Rust + Python + JWT) + Plan 17-04 Task 1 (cost metrics: Rust MV + Python API) both require backend work.
   - **Mitigation:** Parallelize backend tasks (17-02 Task 4 + 17-04 Task 1), or sequence them (do 17-02 Task 4 first, then 17-04 Task 1).

3. **QA/Testing Time:**
   - **Bottleneck:** Plan 17-06 Task 5 (WCAG 2.1 AA audit) is time-consuming (2-3 days). Plan 17-06 Task 8 (Cross-browser testing) is also time-consuming (1-2 days).
   - **Mitigation:** Reduce scope (WCAG 2.1 A only for MVP), defer cross-browser testing to v3.1 (test Chrome + Firefox only for MVP).

### Integration Risks

1. **Highest Risk Integration: Tenant Isolation (Plan 17-02 Task 4) + Cost Aggregation (Plan 17-04 Task 1):**
   - **Risk:** Tenant isolation adds `tenant_id` to all tables. Cost aggregation (Rust MV) must filter by `tenant_id`. If MV doesn't filter by tenant, cost dashboard shows cross-tenant data (security breach).
   - **Mitigation:** Add integration test to Plan 17-04 Task 1: "Cost metrics filtered by tenant_id (user A cannot see user B's costs)."

2. **High Risk Integration: Density Modes (Plan 17-03) + Mobile Swipe (Plan 17-06):**
   - **Risk:** Density modes (compact/normal/detailed) don't work on mobile (detailed mode doesn't fit). Swipe gestures (17-06) conflict with density mode toggle (both use touch).
   - **Mitigation:** Disable density mode toggle on mobile (force compact mode), defer swipe gestures to v3.1 (use button actions only).

3. **Medium Risk Integration: Command Palette (Plan 17-05) + Onboarding (Plan 17-06):**
   - **Risk:** First-time users don't know cmd+k exists → low feature usage → wasted effort building command palette.
   - **Mitigation:** Add onboarding hint to Plan 17-06 Task 1: "Add 'Press ⌘K to search anything' hint to WelcomeStep."

---

## Final Verdict

**Overall:** **APPROVED_WITH_CONDITIONS**

### Plans Approved

- **17-02 (Multi-tenant Company Switcher)** — APPROVED_WITH_CONDITIONS (4 conditions)
- **17-03 (ActiveAgentsPanel)** — APPROVED_WITH_CONDITIONS (4 conditions)
- **17-04 (Cost Dashboard)** — APPROVED_WITH_CONDITIONS (4 conditions)
- **17-05 (Command Palette)** — APPROVED_WITH_CONDITIONS (4 conditions)

### Plans Rejected (Must Revise)

- **17-06 (Onboarding Wizard + Mobile Polish)** — REJECTED_REVISE

**Revise Reasons:**
1. Scope is too large for 5-6 days (realistic: 11-17 days)
2. WCAG 2.1 AA is overkill for MVP (target WCAG 2.1 A only)
3. Swipe gestures are non-essential for MVP (defer to v3.1)
4. BrowserStack validation is non-essential for MVP (use device emulators)
5. Missing analytics integration (add event tracking)

**Revised Scope (MVP):**
- Task 1: OnboardingWizard (3 steps, not 4) — 2 days
- Task 2: onboardingStore + validation — 1 day
- Task 3: Mobile bottom nav — 1 day
- Task 4: WCAG 2.1 A audit (zero Level A violations) — 1 day
- Task 5: User guide (README only) — 1 day

**Total: 6 days (realistic).**

**Deferred to v3.1:**
- Swipe gestures
- BrowserStack validation
- Storybook stories
- Cross-browser testing
- WCAG 2.1 AA (upgrade from A to AA)

### Conditions Summary

**Plan 17-02 (4 conditions):**
1. Add brainStore clear logic to Task 4 (tenant isolation).
2. Add data migration task to Task 4 (auto-create default tenant).
3. Defer draggable company ordering to v3.1.
4. Quantify API latency overhead (target: < 5ms).

**Plan 17-03 (4 conditions):**
1. Specify RAFMonitor implementation in Task 4 (utils/raf-monitor.ts).
2. Add density mode sync logic to Task 3 (auto-switch to compact on mobile).
3. Reduce to 2 density modes (compact/normal, remove detailed).
4. Quantify swipe gesture success rate (≥ 95% on iPhone 14 and Pixel 5).

**Plan 17-04 (4 conditions):**
1. Add cost accuracy validation to Task 1 (integration test).
2. Specify WebSocket rate limiting in Task 5 (server-side + client-side).
3. Defer per-company aggregation to v3.1.
4. Split Task 1 into subtasks (1a Frontend, 1b Backend Rust, 1c Backend Python).

**Plan 17-05 (4 conditions):**
1. Add keyboard shortcut conflict documentation to Task 2.
2. Add onboarding hint to Plan 17-06 Task 1 ("Press ⌘K to search anything").
3. Group brains by domain in Task 3 (Product Strategy, UX Research, etc.).
4. Quantify keyboard navigation latency (< 50ms).

**Plan 17-06 (revise):**
- Split into 17-06a (Onboarding MVP) + 17-06b (Mobile Polish v3.1)
- Or reduce scope to 6 days (WCAG 2.1 A only, device emulators, no swipe gestures)

---

## Risk Score: 65/100

**Breakdown:**
- Planning Fallacy Risk: 70/100 (underestimating backend complexity, BrowserStack setup, WCAG audit)
- Omission Bias Risk: 60/100 (missing rollback plans, RAF monitor spec, analytics integration)
- Systems Thinking Risk: 70/100 (missing feedback loops, second-order effects, cascade failures)
- Over-Engineering Risk: 75/100 (feature bloat: 10 UX patterns without validation, 3 density modes, hierarchical cost breakdown)
- Acceptance Criteria Risk: 50/100 (most criteria verifiable, but some vague: "smoothly", "works")

**Overall:** 65/100 (Medium-High Risk)

**Top 3 Mitigations:**
1. Reduce Plan 17-06 scope to MVP (6 days, not 5-6 days for everything)
2. Defer non-essential features to v3.1 (draggable ordering, swipe gestures, per-company aggregation, WCAG AA)
3. Add missing integration tests (tenant isolation, cost accuracy, cross-tenant data leak)

---

## Confidence Level: 75%

**Why not 100%?**
- I haven't seen real-world usage data (mobile usage %, brain concurrency, company switch frequency)
- I haven't validated user demand for multi-tenant architecture (is this a top user request?)
- I haven't validated user demand for 10 UX patterns (are users asking for these, or are we copying Paperclip blindly?)

**Why 75% and not 50%?**
- I've read the codebase (17-01 complete, RAF batching proven, WebSocket infrastructure exists)
- I've read all 6 plans in detail (17-02 through 17-06)
- I've applied systems thinking lens (feedback loops, second-order effects, cascade failures)
- I've been specific about conditions (not generic "be careful", but exact tasks to add/revise)

**What would increase confidence to 90%?**
- User interviews (validate multi-tenant demand, mobile usage %, need for 10 UX patterns)
- Analytics data (brain concurrency in production, company switch frequency, cmd+k usage in similar apps)
- A/B test results (3-step vs 4-step onboarding, 2 vs 3 density modes, fuzzy vs exact search)

---

## Next Steps

1. **Fix Plan 17-06** — Revise scope to MVP (6 days) or split into 17-06a + 17-06b.
2. **Apply conditions to Plans 17-02 through 17-05** — Add missing tasks, acceptance criteria, mitigations.
3. **Re-dispatch Brain #7** — After revisions, re-evaluate (max 3 iterations total).
4. **Delegate to GSD execution** — After Brain #7 APPROVED, execute Phase 17 via `/mm:execute-phase 17`.

---

**Evaluation complete. Ready for iteration.**
