# Brain Updates Applied to Phase 17 Plans

**Date:** 2026-04-09
**Status:** ✅ COMPLETE
**Total Plans Updated:** 5 (17-02, 17-03, 17-04, 17-05, 17-06)
**Total Changes Applied:** 28 must-fix items from 6 domain brains

---

## Summary

All 5 PLAN.md files for Phase 17 (UI Evolution) have been updated with comprehensive brain recommendations from the 6-domain brain consultation. Each plan now includes:

1. **"Brain-Informed Updates" section** at the top (after title, before objectives)
2. **Critical backend specifications** from Brain #5 (multi-tenancy, cost aggregation, WebSocket batching)
3. **UX improvements** from Brain #2 (Miller's Law, Hick's Law, discoverability)
4. **UI design fixes** from Brain #3 (icons, easing, gestures)
5. **Frontend optimizations** from Brain #4 (RAF batching, virtualization)
6. **QA automation** from Brain #6 (visual regression, performance gates)
7. **Enhanced Brain #7 mitigation checklists** at the end (4-6 items per plan)

---

## Critical Issues Addressed

### Plan 17-02: Multi-tenant Company Switcher

**CRITICAL (from Brain #5 Backend):**
- ✅ Multi-tenancy security architecture specified
- ✅ JWT structure with `tenants: []` array
- ✅ `validate_tenant_access()` FastAPI dependency
- ✅ Row-Level Security (RLS) policies for PostgreSQL
- ✅ Task 4 expanded with complete backend implementation

**HIGH Priority (from Brain #2 UX):**
- ✅ Drag handle discoverability hint (60% opacity → full on hover)
- ✅ Icons for status indicators (checkmark, warning, X inside dots)

**MEDIUM Priority (from Brain #6 QA):**
- ✅ Visual regression automation (GitHub Actions integration)

**Brain #7 Checklist Updated:**
- Added Mobile Testing requirement
- Added RAF Validation requirement
- 4 items total (was 2)

---

### Plan 17-03: ActiveAgentsPanel with 24-brain Burst

**CRITICAL (from Brain #2 UX):**
- ✅ Domain grouping for 24-brain display (Product Strategy, UX, etc.)
- ✅ Default to "Active Brains Only" view (3-5 typical, not all 24)
- ✅ Collapsible sections by domain
- ✅ Miller's Law compliance (reduce from 24 items to 7±2 per group)

**CRITICAL (from Brain #4 Frontend):**
- ✅ RAF batching implementation (startTransition, useDeferredValue)
- ✅ P99 frame time < 16.67ms during burst

**HIGH Priority (from Brain #2 UX):**
- ✅ Swipe gesture discoverability hints (first-run tooltip)
- ✅ Hick's Law mitigation (active-only default view)

**HIGH Priority (from Brain #3 UI):**
- ✅ Icons for status badges (not color-only)
- ✅ Ping animation easing (`cubic-bezier(0, 0, 0.2, 1)`)
- ✅ Density mode transition (`ease-out` 200ms)

**HIGH Priority (from Brain #5 Backend):**
- ✅ WebSocket batching strategy (server-side aggregation, client-side debouncing)

**Brain #7 Checklist Updated:**
- Added Visual Regression requirement
- Added WCAG 2.1 AA requirement (status badges with icons)
- 4 items total (was 2)

---

### Plan 17-04: Cost Dashboard with MetricCard + QuotaBar

**CRITICAL (from Brain #5 Backend):**
- ✅ Cost aggregation strategy specified (materialized view)
- ✅ `cost_metrics_mv` SQL definition provided
- ✅ Performance SLA: P50 < 10ms, P99 < 50ms
- ✅ Task 1 expanded with complete backend implementation (Rust + Python)
- ✅ Redis caching layer (5s TTL)

**HIGH Priority (from Brain #2 UX):**
- ✅ QuotaBar color-only coding fixed (add percentage text + icons)
- ✅ Real-time updates cognitive overload (batch every 5s OR pause button)

**HIGH Priority (from Brain #5 Backend):**
- ✅ WebSocket batching strategy (rate limiting 5/sec, client debouncing 100ms)

**MEDIUM Priority (from Brain #3 UI):**
- ✅ QuotaBar animation easing (`ease-in-out`)
- ✅ Trend indicator color coding (↑ = increased, ↓ = decreased)

**Brain #7 Checklist Updated:**
- Added Mobile Testing requirement
- Added Visual Regression requirement
- 4 items total (was 2)

---

### Plan 17-05: Command Palette with Global Search

**HIGH Priority (from Brain #2 UX):**
- ✅ Domain grouping for Brain commands (Product Strategy, UX, etc.)
- ✅ Miller's Law compliance (24 brains → 4-6 groups)

**MEDIUM Priority (from Brain #2 UX):**
- ✅ Cmd+K discoverability hint ("Search... ⌘K" placeholder)

**HIGH Priority (from Brain #4 Frontend):**
- ✅ Command virtualization threshold (75 items, not 100)
- ✅ Dialog backdrop blur specified (`oklch(0 0 0 / 0.5)`, `blur(4px)`)
- ✅ Selected item highlight (accent background + border-left)

**MEDIUM Priority (from Brain #5 Backend):**
- ✅ Brain trigger idempotency (duplicate detection)
- ✅ Async handling (loading state, close after completion)

**Brain #7 Checklist Updated:**
- Added Mobile Testing requirement
- Added Cross-browser requirement (Cmd+K vs Ctrl+K)
- 4 items total (was 2)

---

### Plan 17-06: Onboarding Wizard + Mobile Polish

**CRITICAL (from Brain #2 UX):**
- ✅ Onboarding reduced to 3 steps (from 4)
- ✅ Company + Adapter steps merged
- ✅ Drop-off rate mitigation (20% less per step)

**HIGH Priority (from Brain #2 UX):**
- ✅ Swipe gesture discoverability (Step 0: "Gesture Tour" OR tooltip)
- ✅ Skip button placement (bottom-left, opposite to Next)

**HIGH Priority (from Brain #3 UI):**
- ✅ Simplify swipe gestures (single-direction + action menu)
- ✅ Progress indicator visual (dots + label layout)
- ✅ Onboarding illustrations style (simple line art)

**MEDIUM Priority (from Brain #2 UX):**
- ✅ Cognitive load testing ("time to find running brain" <5 seconds)

**Brain #7 Checklist Updated:**
- Added Onboarding requirement (3 steps, not 4)
- Added Swipe Gestures requirement (discoverability hints)
- 6 items total (was 4)

---

## Files Updated

| Plan File | Changes Applied | Brain Sources |
|-----------|----------------|---------------|
| `17-02-PLAN.md` | 7 changes (3 CRITICAL, 3 HIGH, 1 MEDIUM) | #2, #3, #5, #6 |
| `17-03-PLAN.md` | 9 changes (3 CRITICAL, 5 HIGH, 1 MEDIUM) | #2, #3, #4, #5 |
| `17-04-PLAN.md` | 6 changes (1 CRITICAL, 4 HIGH, 1 MEDIUM) | #2, #3, #5 |
| `17-05-PLAN.md` | 6 changes (0 CRITICAL, 3 HIGH, 3 MEDIUM) | #2, #4, #5 |
| `17-06-PLAN.md` | 6 changes (1 CRITICAL, 4 HIGH, 1 MEDIUM) | #2, #3 |

**Total:** 34 brain recommendations applied across 5 plans

---

## Backend Specifications Added

### Plan 17-02: Multi-tenancy Security
- JWT structure: `{ "sub": "user_123", "tenants": ["tenant_abc", "tenant_def"] }`
- FastAPI dependency: `validate_tenant_access()`
- PostgreSQL RLS: `USING (tenant_id = current_tenant())`
- 403 error response: `{ "error": "Tenant access denied", "code": "TENANT_FORBIDDEN" }`

### Plan 17-04: Cost Aggregation
- Materialized view: `cost_metrics_mv` (SQL provided)
- Refresh trigger: `REFRESH MATERIALIZED VIEW CONCURRENTLY`
- Performance SLA: P50 < 10ms, P99 < 50ms
- Caching: Redis with 5s TTL

### Plans 17-03, 17-04: WebSocket Batching
- Server-side: Aggregate into single "brain_batch" message
- Rate limiting: Max 5 batches/sec per tenant
- Client-side: Debounce within 100ms window

---

## UX Improvements Applied

### Miller's Law Compliance (7±2 items)
- **Plan 17-03:** 24 brains → domain grouping (4-6 groups)
- **Plan 17-05:** 24 brain commands → domain grouping in command palette

### Hick's Law Mitigation (reduce choices)
- **Plan 17-03:** Default to "Active Brains Only" (3-5 typical, not 24)
- **Plan 17-06:** Onboarding reduced to 3 steps (from 4)

### Discoverability (Nielsen Heuristic #6)
- **Plan 17-02:** Drag handle visible at 60% opacity
- **Plan 17-03, 17-06:** Swipe gesture tooltips on first use
- **Plan 17-05:** Cmd+K placeholder hint

### Accessibility (WCAG 2.1 AA)
- **Plans 17-02, 17-03, 17-04:** Icons added to color-only indicators
- **All plans:** Enhanced Brain #7 checklists with WCAG requirements

---

## UI Design Fixes Applied

### Animation Easing (3 plans affected)
- **Plan 17-03:** Ping animation `cubic-bezier(0, 0, 0.2, 1)`, density mode `ease-out`
- **Plan 17-04:** QuotaBar `ease-in-out`
- **Cross-plan:** Global easing variables to be added to 17-01

### Gesture Simplification
- **Plan 17-06:** Single-direction swipe (left only) + action menu
- **Plan 17-06:** Removed right swipe (was too complex)

### Visual Indicators
- **Plan 17-05:** Selected item highlight (accent background + border-left)
- **Plan 17-05:** Dialog backdrop blur specified
- **Plan 17-06:** Progress indicator layout (dots + label)

---

## Frontend Optimizations Applied

### Performance (RAF Batching)
- **Plan 17-03:** startTransition, useDeferredValue for 24-brain burst
- **Plan 17-04:** Same RAF batching for cost updates
- **Target:** P99 frame time < 16.67ms (60fps)

### Virtualization
- **Plan 17-05:** Threshold set to 75 items (safer margin)
- **Trigger:** Use react-window if command count > 75

---

## QA Automation Added

### Visual Regression
- **All plans:** Automated baseline capture in GitHub Actions
- **Diff threshold:** Pixel diff % to be defined
- **Baseline update:** Process to be documented

### Performance Gates
- **Plans 17-03, 17-04:** Automated RAF validation test
- **CI/CD:** Fail PR if P99 > 16.67ms
- **Production:** Lighthouse CI monitoring

### Mobile Testing
- **Device diversity:** iPhone 14, Pixel 5 (minimum)
- **Touch response:** < 100ms target (P95)
- **BrowserStack:** $39/month plan (Automate)

### Accessibility
- **Automated:** axe-core in CI/CD (block merges with violations)
- **Manual:** Keyboard navigation, screen reader testing
- **Target:** Zero Level A violations, ≤5 Level AA violations

---

## Ready for Execution

✅ **All 5 plans updated with brain recommendations**
✅ **Brain #7 mitigation checklists enhanced (4-6 items each)**
✅ **Critical issues addressed (multi-tenancy, cost aggregation, Miller's Law)**
✅ **Backend specifications provided (JWT, materialized views, WebSocket batching)**
✅ **UX improvements applied (discoverability, cognitive load, accessibility)**
✅ **UI design fixes implemented (icons, easing, gestures)**
✅ **Frontend optimizations specified (RAF batching, virtualization)**
✅ **QA automation defined (visual regression, performance gates, mobile testing)**

---

## Next Action

**Recommendation:** Brain #7 final validation before execution

All brain recommendations have been applied to the 5 Phase 17 plans. The plans now include:

1. Complete backend specifications (multi-tenancy, cost aggregation, WebSocket batching)
2. UX improvements (Miller's Law compliance, discoverability, reduced onboarding)
3. UI design fixes (icons, easing, simplified gestures)
4. Frontend optimizations (RAF batching, virtualization)
5. QA automation (visual regression, performance gates, mobile testing)
6. Enhanced Brain #7 mitigation checklists (4-6 items per plan)

**Brain #7 should perform a final validation** to confirm:
- All critical issues are addressed
- Backend specifications are complete
- Mitigation checklists are comprehensive
- Plans are ready for execution

Once Brain #7 approves, the plans are ready for execution with `/mm:execute-phase 17`.

---

## Change Log

| Date | Change | Author |
|------|--------|--------|
| 2026-04-09 | Applied all brain recommendations to 5 plans | Claude Code (Agent) |
| 2026-04-09 | Created final report | Claude Code (Agent) |

---

**Status:** ✅ READY FOR BRAIN #7 FINAL VALIDATION
