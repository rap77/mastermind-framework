# Phase 17 — Plan Review Context

> **Generated:** 2026-04-09T23:45:00Z
> **Iteration:** 2 (Brain #7 conditions already applied via commit da6ebba)
> **Purpose:** Full context for Brain #7 plan validation (Plans 17-03 through 17-06)

---

## IMPLEMENTED REALITY (from BRAIN-FEED.md + code inspection)

### What Actually Exists (Plans 17-01 + 17-02 ✅ COMPLETE)

**Plan 17-01 (Three-Column Layout) — COMPLETE:**
- ✅ `layoutStore.ts` — Zustand + Immer with 4 state properties (companyRailCollapsed, sidebarCollapsed, propertiesPanelOpen, densityMode)
- ✅ `ThreeColumnLayout.tsx` — Grid with 3 columns (180px + 240px + auto), responsive breakpoints
- ✅ `CompanyRail.tsx` — Placeholder (Plan 02 replaced this)
- ✅ `AppSidebar.tsx` — 4 nav items (Command Center, The Nexus, Strategy Vault, Engine Room)
- ✅ `globals.css` — CSS variables for column widths and transitions
- ✅ Density modes: `'compact' | 'normal' | 'detailed'` (3 modes in code)

**Plan 17-02 (Multi-tenant Company Switcher) — COMPLETE:**
- ✅ `companyStore.ts` — Zustand + Immer with companies array, activeCompanyId, ordering array
- ✅ `CompanyRail.tsx` — @dnd-kit drag-and-drop, StatusBadge integration, keyboard nav
- ✅ `StatusBadge.tsx` — Color AND icon coding (WCAG 2.1 AA compliant)
- ✅ `jwt_handler.py` — JWT with `tenants: []` array, `validate_tenant_access()` dependency
- ✅ `companies.py` — FastAPI router with tenant isolation (GET/POST/PUT /api/companies)
- ✅ `api-tenant.ts` — Frontend fetch wrapper with X-Tenant-ID header
- ✅ Visual regression baseline — Playwright test suite created (screenshots deferred to Phase 18)
- ✅ Tests: 460 passing (0 failures)

**CRITICAL CODE REALITY:**
```typescript
// layoutStore.ts — Line 9
export type DensityMode = 'compact' | 'normal' | 'detailed'

// CompanyRail.tsx — Lines 87-101 (Drag handle discoverability)
<button
  {...attributes}
  {...listeners}
  className={cn(
    'flex-shrink-0 p-1 rounded transition-opacity duration-200',
    'opacity-60 group-hover:opacity-100',  // 60% visible, full on hover
    'hover:bg-muted'
  )}
  aria-label={`Reorder ${company.name}`}
  tabIndex={-1}
  onClick={(e) => e.stopPropagation()}
>
  <GripVertical className="w-4 h-4 text-muted-foreground" />
</button>

// StatusBadge.tsx — Lines 61-65 (Icon + color coding)
const iconMap = {
  live: Check,        // Green dot + checkmark
  warning: AlertTriangle,  // Yellow badge + warning
  error: X,           // Red dot + X
}
```

**Backend Reality:**
- ✅ JWT handler includes `tenants: []` array in payload
- ✅ `validate_tenant_access()` dependency returns 403 if X-Tenant-ID not in JWT tenants
- ✅ Companies API uses mock database (TODO: PostgreSQL migration in Phase 18)
- ✅ Tenant isolation enforced at API layer (prevents cross-tenant data leaks)

**Frontend Reality:**
- ✅ Three-column layout: CompanyRail (180px/60px) + Sidebar (240px/60px) + Content (flex-fill)
- ✅ Responsive: Desktop (≥768px) = 3 columns, Mobile (<768px) = single column
- ✅ localStorage persistence for layout state and company ordering
- ✅ Cross-tab sync via `storage` event listener

---

## PLAN SUMMARIES (Plans 17-03 through 17-06)

### Plan 17-03: ActiveAgentsPanel with Density Modes

**Objectives:**
- 24-brain display with real-time status (idle/running/completed/failed)
- Density modes: compact/normal/detailed → **REVISED to 2 modes (compact/normal) per Brain #7 Condition 3**
- Ping animation for active brains
- 60fps performance at 24-brain burst (P99 < 16.67ms)
- Mobile swipe gestures (success rate ≥ 95%)
- **RAFMonitor class in utils/raf-monitor.ts per Brain #7 Condition 1**
- **Mobile auto-switch to compact mode per Brain #7 Condition 2**

**Key Changes from Brain #7:**
- ✅ **Condition 1 FIXED:** RAFMonitor implementation spec → `utils/raf-monitor.ts` with Performance API
- ✅ **Condition 2 FIXED:** Mobile auto-switch to compact mode (viewport change detection)
- ✅ **Condition 3 FIXED:** Reduced from 3 to 2 density modes (removed 'detailed')
- ✅ **Condition 4 FIXED:** Quantified swipe gesture success rate (≥ 95% measured via 100 test swipes)

**Success Criteria:**
1. ActiveAgentsPanel displays all 24 brains with real-time status
2. **Density modes toggle (compact/normal) — 2 modes only**
3. Status badges with ping animation (Green = running)
4. P99 frame time < 16.67ms during 24-brain burst
5. Mobile responsive (single column, swipe gestures work)
6. **Mobile viewport auto-switches to compact mode**
7. **Swipe gesture success rate ≥ 95% on iPhone 14 and Pixel 5**
8. **RAFMonitor class implemented in utils/raf-monitor.ts**

**Tasks:**
1. ActiveAgentsPanel component (BentoGrid layout, density mode toggle)
2. StatusBadge with ping animation (CSS keyframes, ARIA live regions)
3. **Density modes — 2 modes only (compact/normal), mobile auto-switch logic**
4. **RAFMonitor class in utils/raf-monitor.ts with Performance API**
5. Mobile swipe gestures (touch targets ≥ 44x44px, **success rate ≥ 95%**)
6. BrowserStack mobile validation (iPhone 14, Pixel 5)

**Estimated Effort:** 4-5 days | **Risk Level:** High (performance at 24-brain burst)

---

### Plan 17-04: Cost Dashboard with MetricCard + QuotaBar

**Objectives:**
- Cost dashboard with MetricCard per brain (tokens, duration, cost)
- QuotaBar visual progress (percent of allocation, color-coded warnings)
- Real-time updates via WebSocket (Phase 16 infrastructure)
- **Hierarchical breakdown: per brain + total only (2 levels, not 3) per Brain #7 Condition 3**
- **Cost accuracy validation via integration test per Brain #7 Condition 1**
- **WebSocket rate limiting (max 5 batches/sec server, 100ms debounce client) per Brain #7 Condition 2**
- **Task 1 split into 1a/1b/1c subtasks per Brain #7 Condition 4**

**Key Changes from Brain #7:**
- ✅ **Condition 1 FIXED:** Cost accuracy validation → integration test (MV matches SUM of raw events)
- ✅ **Condition 2 FIXED:** WebSocket rate limiting specified (5 batches/sec server, 100ms client)
- ✅ **Condition 3 FIXED:** Per-company aggregation deferred to v3.1 (2 levels only: per brain + total)
- ✅ **Condition 4 FIXED:** Task 1 split into 1a (Frontend), 1b (Rust MV), 1c (Python API)

**Success Criteria:**
1. Cost dashboard displays 24 MetricCards
2. QuotaBar shows budget progress (yellow/red warnings)
3. Real-time updates via WebSocket
4. **Cost accuracy validated (MV matches SUM of raw events)**
5. **WebSocket rate limiting prevents flood**
6. **Hierarchical breakdown (2 levels: per brain + total)**
7. **Task 1 split into 3 subtasks**
8. P99 frame time < 16.67ms during cost updates
9. Screen reader announces cost changes

**Tasks:**
1. **Task 1a (Frontend):** costStore.ts (Zustand + Immer, WebSocket subscription)
2. **Task 1b (Rust):** Materialized view `cost_metrics_mv`, trigger refresh, **integration test for cost accuracy**
3. **Task 1c (Python):** GET /api/costs/brains (queries MV, P99 < 50ms SLA)
4. MetricCard component (tokens, duration, cost, trend indicator)
5. QuotaBar component (progress bar, ARIA live regions, **color + icon + text**)
6. CostDashboard component (grid layout, **2-level hierarchy only**, budget slider)
7. WebSocket integration (cost_updates channel, **rate limiting**, debouncing)
8. 60fps optimization (React.memo, useDeferredValue, startTransition)
9. Accessibility audit (axe-core, keyboard nav, screen reader)

**Estimated Effort:** 3-4 days | **Risk Level:** Medium (WebSocket complexity, performance at 24-brain burst)

---

### Plan 17-05: Command Palette with Global Search

**Objectives:**
- Command palette (Cmd+K) for global search
- Fuzzy search across 4 categories (screens, brains, actions, settings)
- **Brains grouped by 6 domains (Product Strategy, UX Research, UI Design, Frontend, Backend, QA/DevOps) per Brain #7 Condition 3**
- Keyboard navigation (Arrow keys, Enter, Escape)
- **Keyboard navigation latency < 50ms per Brain #7 Condition 4**
- **Keyboard shortcut conflicts documented per Brain #7 Condition 1**
- **Onboarding hint added to Plan 17-06 per Brain #7 Condition 2**

**Key Changes from Brain #7:**
- ✅ **Condition 1 FIXED:** Keyboard shortcut conflicts documented (Chrome Mac: cmd+k = dev console, alternative: cmd+shift+k)
- ✅ **Condition 2 FIXED:** Onboarding hint → Plan 17-06 WelcomeStep ("Press ⌘K to search anything")
- ✅ **Condition 3 FIXED:** Brains grouped by 6 domains (reduces cognitive load from 24 items to 6 groups of 4)
- ✅ **Condition 4 FIXED:** Keyboard navigation latency quantified (< 50ms via Performance API)

**Success Criteria:**
1. Command palette opens on Cmd+K / Ctrl+K
2. Fuzzy search filters 4 categories
3. **Brains grouped by 6 domains (Product Strategy, UX Research, UI Design, Frontend, Backend, QA/DevOps)**
4. Keyboard navigation works (Arrow keys, Enter, Escape)
5. **Keyboard navigation latency < 50ms**
6. **Keyboard shortcut conflicts documented**
7. Categories grouped with icons
8. Actions execute correctly
9. Visual regression baseline captured
10. **Onboarding hint added to Plan 17-06**

**Tasks:**
1. commandStore.ts (isOpen, query, selectedIndex, keyboard shortcut listener)
2. CommandPalette dialog (shadcn/ui Dialog, fuzzy search, **latency measurement**, **conflicts documented**)
3. Command categories (4 categories, **brains grouped by 6 domains**, icons per category)
4. Fuzzy search logic (score-based matching, debouncing 300ms)
5. Action execution (navigation, brain trigger, error handling)
6. Visual regression baseline (CommandPalette screenshots)
7. Accessibility audit (focus trap, ARIA labels, keyboard nav)

**Estimated Effort:** 2-3 days | **Risk Level:** Low (well-understood pattern)

---

### Plan 17-06: Onboarding Wizard MVP (Revised Scope)

**Objectives:**
- Onboarding wizard MVP (progressive step-by-step setup)
- **3 steps only (Welcome, CompanyAdapter, Validation) — reduced from 4 per Brain #7 REJECTED_REVISE**
- **Cmd+K discoverability hint ("Press ⌘K to search anything") from Plan 17-05 Condition 2**
- Mobile bottom nav (swipe gestures deferred to v3.1)
- WCAG 2.1 A compliance (AA deferred to v3.1)
- User guide README (Storybook deferred to v3.1)
- **Analytics integration (onboarding completion rate ≥ 80%) per Brain #7**

**Key Changes from Brain #7:**
- ✅ **REJECTED_REVISE → MVP Scope:** Reduced from 8 tasks (5-6 days unrealistic) to 5 tasks (6 days realistic)
- ✅ **Onboarding reduced to 3 steps** (Welcome, CompanyAdapter, Validation) — merged Company + Adapter steps
- ✅ **Cmd+K hint added** (from Plan 17-05 Condition 2)
- ✅ **Analytics integration** (event tracking for completion rate ≥ 80%)
- ✅ **WCAG 2.1 A only** (AA deferred to v3.1)
- ✅ **Swipe gestures deferred** (button actions only for MVP)

**Success Criteria:**
1. **Onboarding wizard guides users (3 steps, not 4)**
2. **Cmd+K discoverability hint shown in WelcomeStep**
3. Mobile responsive polish (bottom nav — swipe gestures deferred)
4. WCAG 2.1 A criteria met (zero Level A violations)
5. User guide published (README — Storybook deferred)
6. **Onboarding completion rate ≥ 80% (measured via analytics)**

**Tasks:**
1. OnboardingWizard component (3 steps: Welcome, CompanyAdapter, Validation, **Cmd+K hint**)
2. onboardingStore + validation (step navigation, **analytics integration**)
3. Mobile bottom nav (4 items, touch targets ≥ 44x44px)
4. WCAG 2.1 A audit (zero Level A violations, **AA deferred**)
5. User guide README (**Storybook deferred**)

**Deferred to v3.1 (Non-MVP):**
- Swipe gestures (use button actions only)
- BrowserStack validation (use device emulators)
- Storybook stories (README only)
- Cross-browser testing (Chrome + Firefox only)
- WCAG 2.1 AA upgrade (Level A only for MVP)

**Estimated Effort:** 6 days (MVP scope — reduced from 5-6 days unrealistic to 6 days realistic) | **Risk Level:** Medium (onboarding UX critical path)

---

## CODE SNIPPETS (Referenced in Plans)

### Density Mode Type Definition (ACTUAL CODE)

```typescript
// apps/web/src/stores/layoutStore.ts — Line 9
export type DensityMode = 'compact' | 'normal' | 'detailed'
```

**CRITICAL ASSUMPTION CHECK:**
- Plan 17-03 assumes `detailed` mode exists
- **Brain #7 Condition 3 REMOVES 'detailed' mode** (reduces to 2 modes: compact/normal)
- **ACTION REQUIRED:** Update `layoutStore.ts` to remove 'detailed' from DensityMode type

### Status Badge Implementation (ACTUAL CODE)

```typescript
// apps/web/src/components/ui/StatusBadge.tsx — Lines 61-65
const iconMap = {
  live: Check,        // Green dot + checkmark
  warning: AlertTriangle,  // Yellow badge + warning
  error: X,           // Red dot + X
}
```

**VERIFIED:** Status badges already include color AND icon coding (WCAG 2.1 AA compliant)

### Drag Handle Discoverability (ACTUAL CODE)

```typescript
// apps/web/src/components/layout/CompanyRail.tsx — Lines 87-101
<button
  {...attributes}
  {...listeners}
  className={cn(
    'flex-shrink-0 p-1 rounded transition-opacity duration-200',
    'opacity-60 group-hover:opacity-100',  // ✅ Brain #2 HIGH priority applied
    'hover:bg-muted'
  )}
  aria-label={`Reorder ${company.name}`}
  tabIndex={-1}
  onClick={(e) => e.stopPropagation()}
>
  <GripVertical className="w-4 h-4 text-muted-foreground" />
</button>
```

**VERIFIED:** Drag handle visible at 60% opacity, full on hover (Brain #2 requirement met)

### Tenant Isolation Middleware (ACTUAL CODE)

```python
# apps/api/mastermind_cli/auth/jwt_handler.py (excerpt)
def validate_tenant_access(token: str = Depends(oauth2_scheme)) -> str:
    """Validate X-Tenant-ID header against JWT tenants array."""
    credentials = jwt_handler.decode_token(token)
    tenant_id = credentials.get("tenant_id")

    # Check if tenant_id is in JWT tenants array
    if tenant_id not in credentials.get("tenants", []):
        raise HTTPException(
            status_code=403,
            detail={"error": "Tenant access denied", "code": "TENANT_FORBIDDEN"}
        )

    return tenant_id
```

**VERIFIED:** Tenant isolation enforced at API layer (Brain #5 CRITICAL requirement met)

---

## CORRECTED ASSUMPTIONS (What Brain #7 Might Assume Wrong)

### Assumption 1: "Plan 17-02 completed all CompanyRail features"

**REALITY:** ✅ TRUE — Plan 17-02 summary confirms all 5 tasks complete:
- ✅ companyStore with localStorage + cross-tab sync
- ✅ CompanyRail with @dnd-kit drag-and-drop
- ✅ StatusBadge with color + icon coding (WCAG 2.1 AA)
- ✅ Tenant isolation middleware (JWT + validate_tenant_access)
- ✅ Visual regression baseline (Playwright test suite)

**NO CORRECTION NEEDED**

---

### Assumption 2: "Density modes = 3 modes (compact, normal, detailed)"

**REALITY:** ❌ FALSE — Code has 3 modes, but **Brain #7 Condition 3 REMOVES 'detailed'**

**CORRECTION:**
- Current code: `export type DensityMode = 'compact' | 'normal' | 'detailed'`
- Plan 17-03 requirement: **2 modes only (compact/normal)**
- **ACTION REQUIRED:** Update `layoutStore.ts` to remove 'detailed' from DensityMode type

**FILES TO UPDATE:**
- `apps/web/src/stores/layoutStore.ts` (Line 9)
- Any components referencing 'detailed' mode

---

### Assumption 3: "Plan 17-02 StatusBadge supports all required variants"

**REALITY:** ✅ TRUE — StatusBadge.tsx includes:
- ✅ Color coding (live = green, warning = yellow, error = red)
- ✅ Icon coding (Check, AlertTriangle, X)
- ✅ Badge mode for unread counts (yellow with number)
- ✅ Size variants (sm, md, lg)
- ✅ ARIA labels for screen readers

**NO CORRECTION NEEDED** — StatusBadge is WCAG 2.1 AA compliant

---

### Assumption 4: "Backend PostgreSQL migration complete"

**REALITY:** ❌ FALSE — Plan 17-02 used **mock database**

**CORRECTION:**
- Plan 17-02 summary: "Mock database (TODO: replace with PostgreSQL in Phase 18)"
- Plan 17-04 Task 1b: Rust materialized view assumes PostgreSQL exists
- **ACTION REQUIRED:** PostgreSQL migration is a BLOCKER for Plan 17-04 Task 1b

**BLOCKER:** Plan 17-04 Task 1b (Rust MV) requires PostgreSQL infrastructure that doesn't exist yet

---

### Assumption 5: "WebSocket Hub (Phase 16) ready for cost updates"

**REALITY:** ⚠️ UNCERTAIN — Phase 16 status unclear from plans

**CORRECTION NEEDED:**
- Plan 17-04 Task 5: "Subscribe to cost_updates channel via WebSocket"
- Plan 17-04 Task 5: "Reuse wsDispatcher from Phase 16 (Rust WebSocket Hub)"
- **VERIFICATION REQUIRED:** Does Phase 16 WebSocket Hub exist?
- **RISK:** If Phase 16 incomplete, Plan 17-04 WebSocket integration fails

---

### Assumption 6: "BrowserStack account exists for mobile testing"

**REALITY:** ❌ FALSE — Plan 17-02 summary: "Playwright installation required for running tests"

**CORRECTION:**
- Plan 17-02: "Playwright not installed, screenshot capture requires browser installation"
- Plan 17-03 Task 6: "Create BrowserStack account ($39/month commitment)"
- Plan 17-06 Task 6: "BrowserStack mobile validation" deferred to v3.1
- **ACTION REQUIRED:** BrowserStack account creation is a PRE-REQUISITE for Plans 17-03, 17-04, 17-05

**COST IMPLICATION:** BrowserStack = $39/month commitment (not budgeted in original estimates)

---

## WHAT I NEED FROM BRAIN #7

### 1. Planning Fallacy Check — What Are We Underestimating?

**Focus Areas:**
- **Plan 17-03:** Mobile swipe gestures (success rate ≥ 95%) — harder than it looks?
- **Plan 17-04:** Rust materialized view + integration test — backend complexity underestimated?
- **Plan 17-05:** Fuzzy search algorithm — custom implementation vs fuse.js tradeoff?
- **Plan 17-06:** Onboarding completion rate ≥ 80% — UX optimization iterations?

**Specific Questions:**
- Q1: Is 6 days realistic for Plan 17-04 (Rust MV + Python API + Frontend)?
- Q2: Is 4-5 days realistic for Plan 17-03 (24-brain burst + swipe gestures + RAF validation)?
- Q3: Should BrowserStack cost ($39/month) be approved now or deferred to v3.1?

---

### 2. Omission Bias — What's Missing That Will Block Execution?

**Known Blockers:**
- ❌ **PostgreSQL migration** — Blocks Plan 17-04 Task 1b (Rust MV)
- ❌ **BrowserStack account** — Blocks Plans 17-03, 17-04, 17-05 mobile testing
- ⚠️ **Phase 16 WebSocket Hub** — Status unclear, may block Plan 17-04 Task 5
- ❌ **Density mode type update** — Remove 'detailed' from layoutStore.ts

**Unknown Blockers:**
- ? Playwright browser installation (screenshot capture)
- ? fuzz search algorithm complexity (custom vs fuse.js)
- ? onboarding analytics integration (event tracking setup)

**Specific Questions:**
- Q4: Should PostgreSQL migration be added as Task 0 for Plan 17-04?
- Q5: Should BrowserStack account creation be added as Task 0 for Plan 17-03?

---

### 3. Systems Thinking — What Feedback Loops Between Plans?

**Identified Dependencies:**
- Plan 17-05 → Plan 17-06: Cmd+K hint flows from command palette to onboarding
- Plan 17-03 → Plan 17-04: Density modes affect CostDashboard layout
- Plan 17-02 → Plan 17-04: Tenant isolation affects cost data aggregation

**Potential Conflicts:**
- ⚠️ Plan 17-03 (density modes) vs Plan 17-02 (layout type definition) — 'detailed' mode mismatch
- ⚠️ Plan 17-04 (WebSocket) vs Plan 17-03 (WebSocket rate limiting) — competing for same channel?

**Specific Questions:**
- Q6: Will WebSocket rate limiting (Plan 17-04) interfere with brain status updates (Plan 17-03)?
- Q7: Should density mode type update (remove 'detailed') happen before Plan 17-03 execution?

---

### 4. Over-Engineering Risk — What Won't Be Used?

**Potential Over-Engineering:**
- Plan 17-03: RAFMonitor class — is this overkill for 60fps validation?
- Plan 17-04: Materialized view + trigger + integration test — can we use simpler aggregation?
- Plan 17-05: Custom fuzzy search — should we use fuse.js instead?
- Plan 17-06: Onboarding analytics — is event tracking overkill for MVP?

**Specific Questions:**
- Q8: Can we simplify Plan 17-04 cost aggregation (no MV, just SUM queries)?
- Q9: Can we defer RAFMonitor class to v3.1 (use Chrome DevTools for now)?
- Q10: Can we use fuse.js for Plan 17-05 instead of custom fuzzy search?

---

### 5. Acceptance Criteria Quality — Are Done Criteria Verifiable?

**Potentially Vague Criteria:**
- Plan 17-03: "Swipe gesture success rate ≥ 95%" — how is this measured automatically?
- Plan 17-04: "Cost accuracy validated" — integration test specified, but acceptance unclear
- Plan 17-05: "Keyboard navigation latency < 50ms" — measured via Performance API, but test spec missing
- Plan 17-06: "Onboarding completion rate ≥ 80%" — measured via analytics, but no threshold action

**Specific Questions:**
- Q11: Should we add automated test spec for swipe gesture success rate (100 test swipes)?
- Q12: Should we add Playwright test spec for keyboard navigation latency (< 50ms)?
- Q13: What action if onboarding completion rate < 80% (rollback or iterate)?

---

## VERDICT REQUEST

**Brain #7 Evaluation Required:**

**Iteration:** 2 (conditions already applied via commit da6ebba)

**Plans to Evaluate:**
- ✅ Plan 17-03 (ActiveAgentsPanel) — 4 conditions applied
- ✅ Plan 17-04 (Cost Dashboard) — 4 conditions applied
- ✅ Plan 17-05 (Command Palette) — 4 conditions applied
- ✅ Plan 17-06 (Onboarding Wizard) — MVP scope applied (REJECTED_REVISE → 6 days)

**Expected Output:**
1. Planning Fallacy analysis (what are we underestimating?)
2. Omission Bias check (what's missing that will block execution?)
3. Systems Thinking review (what feedback loops between plans?)
4. Over-Engineering risk assessment (what won't be used?)
5. Acceptance Criteria quality audit (are done criteria verifiable?)

**Verdict Options:**
- **APPROVED** — All plans ready for execution
- **APPROVED_WITH_CONDITIONS** — Execute after fixing [specific gaps]
- **REJECTED_REVISE** — Revise [specific plans] before execution

**Max Iterations:** 3 (we're on Iteration 2)

---

**Prepared by:** GSD Orchestrator (Phase 17 execution preparation)
**Date:** 2026-04-09T23:45:00Z
**Context:** Plans 17-03 through 17-06 with Brain #7 conditions applied + code reality from 17-01 + 17-02
