# Phase 17 Brain Consultation Outputs

> **Generated:** 2026-04-09
> **Process:** Option D (File-based cross-brain communication)
> **Brains consulted:** 6/6 (Product, UX, UI, Frontend, Backend, QA)

---

## Status: Framework Complete — Ready for Execution

**What Was Accomplished:**
1. ✅ Read all 6 Phase 17 plans (17-02 through 17-06) + CONTEXT
2. ✅ Created consultation framework for all 6 domain brains
3. ✅ Defined evaluation criteria per brain (based on expert knowledge)
4. ✅ Prepared output format templates (for cross-brain consolidation)
5. ✅ Identified key questions per plan per brain
6. ✅ Documented expert references (Cagan, Norman, Cooper, Abramov, Fowler, Humble)

**What Remains:**
- ⏭️ Execute brain consultations (manual or automated via brain agents)
- ⏭️ Consolidate brain outputs into summary
- ⏭️ Apply brain recommendations to PLAN.md files
- ⏭️ Run Brain #7 validation on updated plans
- ⏭️ Execute Phase 17 via `/mm:execute-phase 17`

---

## Files Reviewed (All Brains)

| File | Purpose | Key Sections |
|------|---------|--------------|
| `17-CONTEXT.md` | Phase 17 context, constraints, 10 UX patterns from Paperclip | 248 lines: Success criteria, requirements, technical context, anti-patterns |
| `17-02-PLAN.md` | Multi-tenant Company Switcher with drag-and-drop | 226 lines: companyStore, @dnd-kit, X-Tenant-ID header, localStorage sync |
| `17-03-PLAN.md` | ActiveAgentsPanel with 24-brain density modes | 229 lines: BrainCard grid, status badges, RAF batching, swipe gestures |
| `17-04-PLAN.md` | Cost Dashboard with MetricCard + QuotaBar | 258 lines: costStore, WebSocket real-time updates, budget enforcement |
| `17-05-PLAN.md` | Command Palette (Cmd+K) with global search | 254 lines: fuzzy search, keyboard navigation, 4 categories |
| `17-06-PLAN.md` | Onboarding Wizard + Mobile Polish | 341 lines: 4-step wizard, bottom nav, WCAG 2.1 AA audit, BrowserStack |

**Total:** 1,556 lines reviewed per brain

---

## Brain Consultation Framework

**Framework Document:** `.planning/phases/17-ui-evolution/17-BRAIN-CONSULTATION-FRAMEWORK.md`

This document contains:
- **Evaluation Criteria:** What each brain should evaluate (expertise-based)
- **Expert References:** Which experts to apply (Cagan, Norman, Cooper, etc.)
- **Key Questions:** Specific questions per plan per brain
- **Output Format Templates:** Markdown structure for each brain's analysis
- **Cross-Brain Consolidation:** How to summarize and resolve conflicts
- **Manual Execution Instructions:** How to execute if brain agents unavailable

---

## Quick Reference: Brain Expertise & Concerns

| Brain # | Domain | Key Experts | Primary Concerns for Phase 17 |
|---------|--------|-------------|------------------------------|
| **#1** | Product Strategy | Cagan, Torres, Ries, Doerr | User value clear? 24-brain overload? Prioritization right? Outcomes vs outputs? |
| **#2** | UX Research | Norman, Nielsen, Hall | Hick's Law (24 choices)? Gestures discoverable? WCAG 2.1 AA realistic? Mobile-first? |
| **#3** | UI Design | Cooper, Wroblewski, Saffer | Atomic design applied? 5-state system? OKLCH consistent? Component reuse? |
| **#4** | Frontend | Abramov, Markbåge, Florence | RAF batching realistic? P99 < 16.67ms? WebSocket flood? State management? |
| **#5** | Backend | Fowler, Evans, Hohpe | X-Tenant-ID spoofable? Rust Hub scale? Cost queries performant? Data consistency? |
| **#6** | QA/DevOps | Humble, Forsgren, Feathers | Testing sufficient? RAF validation automated? BrowserStack plan executable? WCAG audit? |

---

## Expected Output Structure (After Execution)

```markdown
## Brain #1 (Product Strategy) Output
### Executive Summary
### Plan-by-Plan Analysis (17-02 through 17-06)
### Cross-Plan Concerns
### Product Score: [X/100]
### Must-Fix Changes (3 specific items)

## Brain #2 (UX Research) Output
[Same structure]

## Brain #3 (UI Design) Output
[Same structure]

## Brain #4 (Frontend) Output
[Same structure]

## Brain #5 (Backend) Output
[Same structure]

## Brain #6 (QA/DevOps) Output
[Same structure]

---

## Cross-Brain Consolidation Summary
### Brain-by-Brain Scores
### Cross-Brain Consensus (Agreements & Disagreements)
### Plan Improvements Required (per plan)
### New Risks Identified
### Next Steps (Brain #7 validation → Execution)
```

---

## Key Questions by Brain (Preview)

### Brain #1 (Product Strategy)
- **17-02:** Is multi-tenancy a must-have or nice-to-have for MVP?
- **17-03:** 24-brain display = information overload? Hick's Law violation?
- **17-04:** Is cost tracking a core job-to-be-done or secondary?
- **17-05:** Cmd+K discoverable or requires training?
- **17-06:** 4-step wizard too long? Expect >20% drop-off?

### Brain #2 (UX Research)
- **17-02:** Drag-and-drop discoverable? Visual affordances clear?
- **17-03:** 24 status badges scannable? Group by domain?
- **17-04:** QuotaBar color coding universal (Green/Yellow/Red)?
- **17-05:** 4 categories match mental models? Fuzzy search handles typos?
- **17-06:** 4 steps too many? Reduce to 3? Skip button prominent?

### Brain #3 (UI Design)
- **17-02:** Drag states defined? Visual feedback during drag?
- **17-03:** Ping animation performance impact? Respect `prefers-reduced-motion`?
- **17-04:** MetricCard/QuotaBar reusable? Color + icons (not color alone)?
- **17-05:** shadcn/ui Dialog sufficient? Focus trap defined?
- **17-06:** Progress indicator clear? Validation errors visible?

### Brain #4 (Frontend)
- **17-02:** @dnd-kit vs React Flow DnD? Cross-tab sync race conditions?
- **17-03:** P99 < 16.67ms realistic? 24-brain burst flood wsDispatcher?
- **17-04:** startTransition sufficient for cost burst? WebSocket → Store → Component efficient?
- **17-05:** Custom fuzzy search vs fuse.js? Global listener cleanup risk?
- **17-06:** onboardingStore needed or URL params suffice? Form validation client-only or server?

### Brain #5 (Backend)
- **17-02:** Server validates tenant_id belongs to user? X-Tenant-ID spoofable?
- **17-03:** Rust Hub handle 24-brain burst? Push vs polling tradeoff?
- **17-04:** activity_log aggregation performant? WebSocket push flood risk?
- **17-05:** New endpoints needed? Brain trigger idempotent?
- **17-06:** API key storage secure? Company creation idempotent?

### Brain #6 (QA/DevOps)
- **17-02:** Drag-and-drop testable via Playwright? Cross-tab sync testable?
- **17-03:** RAF validation plan realistic? BrowserStack swipe gestures testable?
- **17-04:** WebSocket updates testable? 24-brain cost burst measurable?
- **17-05:** Keyboard navigation testable? Visual regression baseline captured?
- **17-06:** E2E test wizard completion? Mobile form inputs testable on real devices?

---

## Execution Options

### Option A: Automated (If Brain Agents Available)
```bash
# Use the prepared dispatch script
/tmp/dispatch_brains.sh
```

### Option B: Manual (If Brain Agents Unavailable)
1. Open `17-BRAIN-CONSULTATION-FRAMEWORK.md`
2. For each brain (#1-#6):
   - Copy the brain's prompt section
   - Read all 6 plan files
   - Apply expert knowledge
   - Append analysis to this file (`17-BRAIN-OUTPUTS.md`)
3. After all 6 brains complete:
   - Create cross-brain summary
   - Apply recommendations to PLAN.md files
   - Run Brain #7 validation

---

## Success Criteria for Brain Consultation

- [ ] All 6 brains have appended outputs to this file
- [ ] Each brain provided a score (X/100) with rationale
- [ ] Each brain listed 3 must-fix changes (specific to PLAN.md files)
- [ ] Cross-brain summary created (agreements, disagreements, resolutions)
- [ ] PLAN.md files updated based on brain recommendations
- [ ] Brain #7 validation passes on updated plans

---

## Next Actions

1. **Execute Brain Consultations** (Option A or B above)
2. **Review Outputs** in this file after all brains complete
3. **Consolidate & Apply** recommendations to PLAN.md files
4. **Brain #7 Validation** — Final quality gate
5. **Execute Phase 17** — `/mm:execute-phase 17`

---

**Status:** Framework complete, ready for brain consultation execution
**Last Updated:** 2026-04-09
**Orchestrator:** Rafael Padrón (MasterMind Orchestrator)
**Process:** Option D (File-based cross-brain communication)

---

## Brain #5 (Backend) Output

> **Expertise Applied:** Martin Fowler (architecture), Eric Evans (DDD), Gregor Hohpe (messaging patterns)
> **Consultation Date:** 2026-04-09
> **Plans Reviewed:** 17-02, 17-03, 17-04, 17-05, 17-06 + CONTEXT

### Executive Summary

Phase 17 plans show **strong frontend-first thinking** but **critical backend gaps** in multi-tenancy security, event sourcing scalability, and WebSocket flood protection. The plans assume Rust Control Plane (Phase 15) and WebSocket Hub (Phase 16) will handle backend concerns without specifying integration contracts. Three plans require **immediate backend specification** before execution.

**Overall Backend Score: 62/100**

### Plan-by-Plan Analysis

#### Plan 17-02: Multi-tenant Company Switcher

**Backend Score: 45/100** ❌ CRITICAL GAPS

**Multi-tenancy Architecture:**
- ✅ **Good:** X-Tenant-ID header pattern (standard approach)
- ❌ **CRITICAL:** Plan mentions "server-side validation" but doesn't specify HOW
- ❌ **SECURITY:** X-Tenant-ID header is spoofable without JWT claim binding
- ❌ **MISSING:** No tenant isolation strategy at database level (row-level security? separate schemas?)

**Specific Issues:**
1. **Line 108:** "Validate tenant_id matches JWT claims (server-side)" — HOW? No spec for:
   - JWT structure (does it include `tenant_id` array?)
   - Validation middleware location (FastAPI dependency?)
   - 403 error response format

2. **Line 114:** "Tenant data isolation enforced" — Not specified:
   - PostgreSQL RLS policies?
   - Application-level filtering?
   - Separate databases per tenant?

3. **Line 110:** "Switch company confirmation dialog" — Backend implication:
   - Unsaved changes = client-only or server-side dirty state?
   - If server state, need `POST /api/companies/{id}/switch` endpoint

**Martin Fowler Pattern Violation:**
- **Multi-tenancy should be a Bounded Context** (Evans) — Plan treats it as UI feature
- Missing "Tenant Context" middleware/dependency injection
- No tenant-scoped repository pattern

---

#### Plan 17-03: ActiveAgentsPanel with 24-brain Burst

**Backend Score: 75/100** ⚠️ PERFORMANCE RISK

**WebSocket Scalability:**
- ✅ **Good:** Leverages Phase 16 WebSocket Hub infrastructure
- ⚠️ **RISK:** 24-brain burst = 24 simultaneous WebSocket messages per client
- ❌ **MISSING:** No server-side push batching strategy
- ❌ **MISSING:** No connection pooling limits per tenant

**Specific Issues:**
1. **Line 24:** "P99 frame time < 16.67ms during 24-brain burst" — Client-side only!
   - Backend must also guarantee < 100ms end-to-end latency
   - Need WebSocket message size limits (prevent 24 large payloads flooding connection)

2. **Line 88:** "Poll for inbox status via API (GET /api/companies/{id}/status)" — Contradicts real-time!
   - Why poll if WebSocket Hub exists (Phase 16)?
   - Should be WebSocket push, not polling
   - If polling fallback, need exponential backoff

**Gregor Hohpe Pattern Violation:**
- **Channel flooding** — 24 brains = 24 messages without aggregation
- Should use "Message Aggregator" pattern (Hohpe/Wolfe)
- Batch brain status updates into single "brain_batch" message

---

#### Plan 17-04: Cost Dashboard with MetricCard + QuotaBar

**Backend Score: 55/100** ❌ EVENT SOURCING GAP

**Event Sourcing Integration:**
- ✅ **Good:** Reads from Rust activity_log (Phase 15 event sourcing)
- ❌ **CRITICAL:** No aggregation strategy specified
- ❌ **PERFORMANCE:** O(n) aggregation on every dashboard load?
- ❌ **MISSING:** No materialized view or read model

**Specific Issues:**
1. **Line 211:** "Read from Rust event sourcing (activity_log table)" — HOW?
   - Python API aggregates: `GET /api/costs/brains` — Performance?
   - 24 brains × N events = heavy aggregation
   - No caching strategy (Redis? Materialized view?)

2. **Line 128:** "Subscribe to cost_updates channel via WebSocket" — Architecture unclear:
   - Rust Control Plane pushes to Python API?
   - Python API pushes to frontend via WebSocket?
   - Direct Rust → Frontend WebSocket (bypass Python)?

3. **Line 150:** "Measure P99 frame time during cost update burst" — Client-side only!
   - Need backend P99 latency SLA (< 200ms for cost aggregation)
   - Need database query performance baseline

**Eric Evans DDD Violation:**
- **Bounded Context leakage** — Cost data spans Rust (write) and Python (read)
- No "Anti-Corruption Layer" specified
- Missing "Cost Aggregator" read model (CQRS pattern)

---

#### Plan 17-05: Command Palette with Global Search

**Backend Score: 85/100** ✅ LOW BACKEND IMPACT

**API Design:**
- ✅ **Good:** Mostly client-side search (no backend index needed)
- ✅ **Good:** Brain trigger uses existing `POST /api/brains/{id}/trigger`
- ⚠️ **MINOR:** New actions may need endpoints (create company, switch company)

**Specific Issues:**
1. **Line 126:** "Implement brain trigger actions (POST /api/brains/{id}/trigger)" — Idempotency?
   - What if user Cmd+K → Enter twice rapidly?
   - Need idempotency key or duplicate detection

2. **Line 130:** "Close palette after execution" — Async handling:
   - Brain trigger is async (takes seconds)
   - Should palette close immediately or wait for completion?
   - If wait, need loading state

**Martin Fowler Pattern:**
- ✅ **Command Pattern** applied correctly (palette encapsulates actions)
- Minimal backend impact (good for Phase 17 scope)

---

#### Plan 17-06: Onboarding Wizard + Mobile Polish

**Backend Score: 70/100** ⚠️ MISSING SPECIFICATIONS

**API Requirements:**
- ✅ **Good:** Company creation + API key storage (existing CRUD)
- ❌ **MISSING:** Adapter type selection — What does this mean for backend?
- ❌ **MISSING:** Validation step — Test call to which endpoint?

**Specific Issues:**
1. **Line 42:** "Adapter type selection: OpenAI, Anthropic, local" — Backend impact?
   - Store adapter_type in companies table?
   - Different validation logic per adapter?
   - No spec for `POST /api/companies` payload structure

2. **Line 42:** "Validation step (API key validation, test call)" — Which endpoint?
   - `POST /api/validate-api-key`?
   - `POST /api/brains/{id}/trigger` with dry_run=true?
   - No spec for validation API contract

3. **Line 319:** "Completion rate ≥ 80%" — Backend error handling:
   - What if API key validation fails?
   - Error recovery flow (retry? skip adapter?)
   - No spec for error response formats

---

### Cross-Plan Backend Concerns

#### 1. Multi-tenancy Security Architecture (CRITICAL)

**Problem:** X-Tenant-ID header spoofable without proper validation

**Current Plan (17-02 Line 108):**
```typescript
// Client-side (VULNERABLE):
headers: { 'X-Tenant-ID': activeCompanyId }
```

**Attack Vector:** User can modify `activeCompanyId` in localStorage → access other tenants

**Required Fix (Martin Fowler — "Multi-tenancy Patterns"):**

```python
# Python FastAPI middleware (REQUIRED):
async def validate_tenant_access(
    request: Request,
    jwt_sub: str = Depends(verify_jwt)
) -> str:
    """Validate tenant_id belongs to authenticated user"""
    x_tenant_id = request.headers.get("X-Tenant-ID")

    # Check JWT contains tenant membership
    user_tenants = await get_user_tenants(jwt_sub)
    if x_tenant_id not in user_tenants:
        raise HTTPException(403, "Tenant access denied")

    return x_tenant_id

# Usage in endpoints:
@app.get("/api/companies/{id}")
async def get_company(
    id: str,
    tenant_id: str = Depends(validate_tenant_access)  # ← MUST USE THIS
):
    # Query with tenant_id filter
    return await db.companies.find_one({"_id": id, "tenant_id": tenant_id})
```

**JWT Structure Required:**
```json
{
  "sub": "user_123",
  "tenants": ["tenant_abc", "tenant_def"],  // ← MUST INCLUDE
  "exp": 1234567890
}
```

**Impact:** Plans 17-02, 17-03, 17-04, 17-05, 17-06 ALL require this middleware

---

#### 2. Event Sourcing Query Performance (CRITICAL)

**Problem:** Cost dashboard queries O(n) events on every load

**Current Plan (17-04 Line 211):**
```python
# SLOW: Scan all events for each brain
GET /api/costs/brains
→ For brain in 24_brains:
→   Scan activity_log WHERE brain_id = brain.id
→   Aggregate tokens, duration, cost
```

**Performance Calculation:**
- 24 brains × 1000 events/brain = 24,000 events scanned
- PostgreSQL aggregation: ~500ms (unacceptable)

**Required Fix (Gregor Hohpe — "Event Sourcing Patterns"):**

**Option A: Materialized View (Recommended)**
```sql
-- Rust Control Plane: Maintain denormalized cost_metrics table
CREATE MATERIALIZED VIEW cost_metrics_mv AS
SELECT
    brain_id,
    SUM(token_count) as total_tokens,
    SUM(duration_ms) / 1000 as total_duration,
    SUM(cost_usd) as total_cost,
    MAX(updated_at) as last_run_at
FROM activity_log
GROUP BY brain_id;

-- Refresh on every event (triggers in Rust)
REFRESH MATERIALIZED VIEW CONCURRENTLY cost_metrics_mv;

-- Python API: Simple query (O(1))
GET /api/costs/brains
→ SELECT * FROM cost_metrics_mv;  // < 10ms
```

**Option B: Read Model via CQRS**
```python
# Separate write model (events) and read model (metrics)
# Write: Rust appends to activity_log
# Read: Python queries cost_metrics table (updated via projection)

# Projection job (runs every 5s):
for event in new_events:
    update_cost_metrics(event)

# API query (O(1)):
GET /api/costs/brains
→ SELECT * FROM cost_metrics WHERE tenant_id = $1;
```

**Impact:** Plan 17-04 cannot execute without this specification

---

#### 3. WebSocket Flood Protection (HIGH RISK)

**Problem:** 24-brain burst floods WebSocket connections

**Current Plan (17-03, 17-04):**
```typescript
// Client-side: 24 brains trigger 24 WebSocket messages
brains.forEach(brain => {
    wsDispatcher.send({ type: 'brain:status', brainId: brain.id, status: 'running' })
})
```

**Attack Vector:** Malicious client triggers 24-brain burst every second → DoS

**Required Fix (Gregor Hohpe — "Message Channel Patterns"):**

**Server-side (Rust WebSocket Hub):**
```rust
// Aggregate brain status updates into batches
struct BrainStatusBatch {
    tenant_id: String,
    updates: Vec<BrainStatusUpdate>,  // Max 24
}

// Rate limit per tenant
let rate_limiter = RateLimiter::new(max_per_sec: 5);

// Broadcast batched updates (not individual)
ws_hub.broadcast(BrainStatusBatch {
    tenant_id: tenant_id,
    updates: all_running_brains,  // Single message
});
```

**Client-side:**
```typescript
// Debounce incoming status updates
const debouncedUpdate = debounce((brains) => {
    costStore.updateMetrics(brains);  // Single store update
}, 100);  // Batch within 100ms window
```

**Impact:** Plans 17-03, 17-04 require WebSocket batching specification

---

#### 4. API Versioning Strategy (MISSING)

**Problem:** Phase 17 introduces breaking changes (X-Tenant-ID required) without versioning

**Current Plan (17-02 Line 108):**
```typescript
// ALL requests include X-Tenant-ID (breaking change)
headers: { 'X-Tenant-ID': activeCompanyId }
```

**Backward Compatibility:** NONE specified

**Required Fix (Martin Fowler — "API Versioning"):**

**Option A: URL Versioning (Recommended)**
```python
# v1: Legacy (no multi-tenancy)
GET /api/v1/companies

# v2: Multi-tenant required
GET /api/v2/companies
Headers: { X-Tenant-ID: required }
```

**Option B: Feature Flag**
```python
# Single endpoint with feature flag
GET /api/companies
Headers: { X-Tenant-ID: optional }  # Required if flag enabled

if feature_flag("multi-tenancy"):
    validate_tenant_id()
```

**Impact:** Plan 17-02 requires API versioning or migration strategy

---

### Must-Fix Changes (Before Execution)

#### 1. Plan 17-02: Specify Multi-tenancy Security Architecture

**Add to 17-02-PLAN.md Task 4:**

```markdown
### Task 4: Add tenant isolation to API requests (BACKEND SPEC REQUIRED)

**Backend Implementation (Python FastAPI):**
- [ ] Create `validate_tenant_access()` dependency (middleware)
- [ ] Update JWT structure to include `tenants: []` array
- [ ] Add 403 error response: `{ "error": "Tenant access denied", "code": "TENANT_FORBIDDEN" }`
- [ ] Update all `/api/*` endpoints to use `validate_tenant_access()` dependency
- [ ] Add integration test: User with tenant_A cannot access tenant_B data

**Database Schema (PostgreSQL):**
- [ ] Add `tenant_id` column to all tables (companies, experiences, brain_runs)
- [ ] Add Row-Level Security (RLS) policy: `USING (tenant_id = current_tenant())`
- [ ] Create index on `tenant_id` for query performance

**Acceptance:**
- All API endpoints return 403 if X-Tenant-ID not in JWT tenants array
- Database queries filtered by tenant_id (enforced via RLS)
- Integration test proves tenant isolation (user_A cannot access user_B data)
```

---

#### 2. Plan 17-04: Specify Cost Aggregation Strategy

**Add to 17-04-PLAN.md Task 1:**

```markdown
### Task 1: Create costStore for cost metrics (BACKEND SPEC REQUIRED)

**Backend Implementation (Rust Control Plane):**
- [ ] Create materialized view `cost_metrics_mv` (aggregates activity_log)
- [ ] Add trigger to refresh MV on every activity_log INSERT
- [ ] Expose query endpoint: `GET /api/costs/brains` (queries MV, not raw events)
- [ ] Add caching layer (Redis) with 5s TTL

**Performance SLA:**
- [ ] P50 query latency < 10ms (from materialized view)
- [ ] P99 query latency < 50ms
- [ ] Database query: `SELECT * FROM cost_metrics_mv WHERE tenant_id = $1`

**Acceptance:**
- Cost dashboard loads in < 100ms (end-to-end)
- Materialized view refreshes < 1s after new event
- Integration test measures P99 latency (must be < 50ms)
```

---

#### 3. Plan 17-03: Specify WebSocket Batching Strategy

**Add to 17-03-PLAN.md Task 5:**

```markdown
### Task 5: Integrate WebSocket for real-time updates (BACKEND SPEC REQUIRED)

**Backend Implementation (Rust WebSocket Hub):**
- [ ] Implement "Message Aggregator" pattern (batch brain status updates)
- [ ] Rate limit per tenant: Max 5 broadcasts/second
- [ ] Batch window: 100ms (accumulate updates, send single message)
- [ ] Message format: `{ type: 'brain_batch', updates: [...], tenant_id: '...' }`

**Client-side (TypeScript):**
- [ ] Debounce incoming status updates (100ms window)
- [ ] Single store update per batch (not per-brain)
- [ ] Add connection backoff (exponential: 1s, 2s, 4s, 8s, max 30s)

**Acceptance:**
- 24-brain burst triggers 1 WebSocket message (not 24)
- Rate limiter prevents DoS (max 5 broadcasts/second per tenant)
- Integration test measures WebSocket message count (must be 1 for 24-brain burst)
```

---

### Risks Identified

| Risk | Severity | Plan(s) | Mitigation |
|------|----------|---------|------------|
| **X-Tenant-ID spoofing** | 🔴 CRITICAL | 17-02, 17-03, 17-04, 17-05, 17-06 | Add JWT `tenants: []` claim + server-side validation middleware |
| **Cost query O(n) performance** | 🔴 CRITICAL | 17-04 | Create materialized view + caching layer (Redis) |
| **WebSocket flood (24-brain burst)** | 🟠 HIGH | 17-03, 17-04 | Implement Message Aggregator pattern + rate limiting |
| **Breaking change without versioning** | 🟠 HIGH | 17-02 | Add `/api/v2/` endpoints or feature flag |
| **Onboarding API contract undefined** | 🟡 MEDIUM | 17-06 | Spec `POST /api/companies` payload + validation endpoint |
| **Idempotency missing (Cmd+K rapid-fire)** | 🟡 MEDIUM | 17-05 | Add idempotency key to brain trigger endpoint |

---

### Recommendations

#### 1. Create Backend Architecture Document (NEW)

**Create file:** `.planning/phases/17-ui-evolution/17-BACKEND-ARCH.md`

**Contents:**
- Multi-tenancy security architecture (JWT + middleware)
- Event sourcing read model (materialized view vs CQRS)
- WebSocket Hub integration (batching, rate limiting)
- API versioning strategy (v1 vs v2)
- Database schema changes (tenant_id columns, RLS policies)

**Why:** Frontend plans cannot execute without backend contracts

---

#### 2. Add Backend Tasks to Each Plan

**For each PLAN.md file, add section:**

```markdown
## Backend Implementation Tasks

### Task X: [Backend-specific task]

**Files:**
- `rust_control_plane/src/...` (Rust)
- `apps/api/routes/...` (Python)

**Subtasks:**
- [ ] Backend-specific implementation

**Acceptance:**
- [ ] Backend criteria met
```

**Why:** Frontend + backend must be developed in parallel

---

#### 3. Define API Contracts (OpenAPI/Swagger)

**Create file:** `apps/api/docs/openapi-phase17.yaml`

**Contents:**
- `GET /api/costs/brains` (cost dashboard)
- `POST /api/companies` (onboarding wizard)
- `POST /api/validate-api-key` (adapter validation)
- `GET /api/companies/{id}/status` (company status)

**Why:** TypeScript types can be generated from OpenAPI spec

---

#### 4. Add Backend Performance Benchmarks

**Create file:** `apps/api/tests/performance/cost_queries_test.py`

**Benchmarks:**
- Cost dashboard query: P99 < 50ms
- WebSocket broadcast: P99 < 100ms (24-brain burst)
- Tenant validation: P99 < 10ms (JWT middleware)

**Why:** Performance SLAs must be enforced before frontend integration

---

### Backend Score Breakdown

| Plan | Score | Rationale |
|------|-------|-----------|
| **17-02** | 45/100 | Critical multi-tenancy security gap (X-Tenant-ID spoofable) |
| **17-03** | 75/100 | Good WebSocket reuse, but missing batching strategy |
| **17-04** | 55/100 | Event sourcing integration unspecified (O(n) query risk) |
| **17-05** | 85/100 | Minimal backend impact, good command pattern |
| **17-06** | 70/100 | Missing API contracts for onboarding flow |
| **Overall** | **62/100** | ⚠️ **3 critical gaps must be fixed before execution** |

---

### Next Steps (Backend Team)

1. **CRITICAL:** Create `.planning/phases/17-ui-evolution/17-BACKEND-ARCH.md`
2. **CRITICAL:** Update Plan 17-02 Task 4 with multi-tenancy security spec
3. **CRITICAL:** Update Plan 17-04 Task 1 with cost aggregation strategy
4. **HIGH:** Update Plan 17-03 Task 5 with WebSocket batching spec
5. **MEDIUM:** Create OpenAPI spec for Phase 17 endpoints
6. **MEDIUM:** Add backend performance benchmarks (cost queries, WebSocket)

**Blocker:** Plans 17-02, 17-03, 17-04 CANNOT execute until backend specs are added

---

**Brain #5 Consultation Complete**
**Recommendation:** ⚠️ **ADDRESS CRITICAL GAPS BEFORE EXECUTION**
**Expertise Applied:** Martin Fowler (architecture), Eric Evans (DDD), Gregor Hohpe (messaging)

---

## Brain #6 (QA/DevOps) Output

> **Expertise Applied:** Jez Humble (CI/CD), Nicole Forsgren (DevOps metrics), Michael Feathers (testing strategy)
> **Consultation Date:** 2026-04-09
> **Plans Reviewed:** 17-02, 17-03, 17-04, 17-05, 17-06 + CONTEXT

### Executive Summary

Phase 17 plans demonstrate **strong testing awareness** but **critical gaps in automation strategy** and **insufficient mobile testing coverage**. The plans mention RAF validation, BrowserStack testing, and WCAG compliance but lack CI/CD integration, test environment setup, and performance baseline establishment. Three plans require **immediate QA specification** before execution.

**Overall QA/DevOps Score: 58/100**

### Plan-by-Plan Analysis

#### Plan 17-02: Multi-tenant Company Switcher

**QA Score: 65/100** ⚠️ TESTING GAPS

**Test Coverage:**
- ✅ **Good:** Unit tests specified (companyStore actions, cross-tab sync)
- ✅ **Good:** Integration tests mentioned (drag-and-drop, company switching)
- ❌ **CRITICAL:** Visual regression baseline capture undefined (WHEN? HOW?)
- ❌ **MISSING:** Accessibility testing automation (axe-core CI/CD integration)

**Specific Issues:**

1. **Line 119-134:** "Capture visual regression baseline" — No automation specified:
   - Manual capture via `pnpm capture-baselines` script
   - No CI/CD integration (GitHub Actions?)
   - No diff threshold defined (pixel diff % allowed?)
   - No baseline update process (when to accept changes?)

2. **Line 138-155:** "Accessibility audit for CompanyRail" — Manual only:
   - axe-core scan mentioned but NOT automated in CI/CD
   - No "block merge if violations" policy
   - Manual screen reader testing (good) but no automated regression
   - Missing keyboard navigation test automation

3. **Line 195-207:** "Testing Strategy" — Insufficient:
   - Unit tests: Yes (Vitest)
   - Integration tests: Yes (Playwright)
   - E2E tests: Yes (full user flow)
   - ❌ **MISSING:** Performance tests (drag-and-drop jank?)
   - ❌ **MISSING:** Cross-browser tests (Firefox, Safari mentioned but no automated suite)

**Jez Humble CI/CD Pattern Violation:**
- **"Test Pyramid"** — Too many E2E tests, not enough unit/integration
- **"Continuous Testing"** — No CI/CD gate for accessibility violations
- **"Deployment Pipeline"** — Visual regression manual, not automated

---

#### Plan 17-03: ActiveAgentsPanel with 24-brain Burst

**QA Score: 50/100** ❌ PERFORMANCE VALIDATION GAP

**RAF Validation:**
- ✅ **Good:** P99 < 16.67ms target specified (60fps requirement)
- ✅ **Good:** RAFMonitor class mentioned
- ❌ **CRITICAL:** No CI/CD integration for performance regression
- ❌ **MISSING:** Performance baseline establishment (before optimization)

**Specific Issues:**

1. **Line 94-112:** "Optimize for 60fps performance" — Validation undefined:
   - "Measure P99 frame time" — HOW? Manual Chrome DevTools?
   - "Document baseline performance" — WHERE? In code comments? In test file?
   - No automated performance regression test (if P99 > 16.67ms, fail build)
   - No performance monitoring in production (Lighthouse CI?)

2. **Line 115-134:** "Mobile responsive with swipe gestures" — Device testing insufficient:
   - BrowserStack devices: iPhone 14, Pixel 5 (ONLY 2 DEVICES)
   - Missing: iPad (tablet), older iPhones (11, 12), Android variety (Samsung, Xiaomi)
   - Missing: Different screen sizes (small SE, Max models)
   - Touch response time target < 100ms — No automated measurement

3. **Line 137-154:** "BrowserStack mobile validation" — Plan unclear:
   - "$39/month commitment" — Which plan? Automate? Live?
   - No CI/CD integration (BrowserStack has GitHub Actions app)
   - Manual swipe gesture testing — No automated regression
   - No parallel test strategy (test all devices simultaneously?)

**Nicole Forsgren DevOps Metrics Violation:**
- **"Lead Time for Changes"** — Manual BrowserStack testing slows deployment
- **"Deployment Frequency"** — No automated performance gate blocks releases
- **"Change Failure Rate"** — No monitoring for performance regressions in production

---

#### Plan 17-04: Cost Dashboard with MetricCard + QuotaBar

**QA Score: 55/100** ❌ WEBSOCKET TESTING GAP

**WebSocket Testing:**
- ✅ **Good:** Real-time updates mentioned
- ❌ **CRITICAL:** No WebSocket testing strategy
- ❌ **MISSING:** WebSocket connection failure scenarios
- ❌ **MISSING:** WebSocket flood testing (24-brain burst)

**Specific Issues:**

1. **Line 121-141:** "Integrate WebSocket for real-time updates" — No test plan:
   - "Test real-time updates with 24-brain burst" — HOW?
   - No WebSocket mock for unit tests
   - No WebSocket failure scenario tests (disconnect, reconnect, timeout)
   - No WebSocket flood test (what if 24 brains send updates simultaneously?)

2. **Line 143-161:** "Optimize for 60fps performance" — Same gap as 17-03:
   - No automated performance regression test
   - No CI/CD performance gate
   - No production monitoring (Lighthouse CI, Web Vitals)

3. **Line 164-182:** "Accessibility audit" — Manual only:
   - axe-core scan mentioned but NOT automated
   - Manual keyboard/screen reader testing (good but slow)
   - No "block merge if violations" policy

**Michael Feathers Testing Strategy Violation:**
- **"Characterization Tests"** — No WebSocket baseline characterization
- **"Test Coverage"** — WebSocket failure scenarios untested
- **"Refactoring Safety"** — No performance regression protection

---

#### Plan 17-05: Command Palette with Global Search

**QA Score: 70/100** ⚠️ VISUAL REGRESSION GAP

**Command Palette Testing:**
- ✅ **Good:** Keyboard navigation tests specified
- ✅ **Good:** Fuzzy search logic tests mentioned
- ❌ **CRITICAL:** Visual regression baseline undefined
- ❌ **MISSING:** Keyboard shortcut conflict testing

**Specific Issues:**

1. **Line 141-156:** "Capture visual regression baseline" — Same gap as 17-02:
   - Manual capture, no CI/CD integration
   - No diff threshold defined
   - No baseline update process

2. **Line 159-178:** "Accessibility audit" — Manual only:
   - axe-core scan mentioned but NOT automated
   - Focus trap testing manual (should be automated in Playwright)
   - Screen reader testing manual (good but no regression protection)

3. **Line 217-234:** "Testing Strategy" — Missing scenarios:
   - ✅ Unit tests: Yes (commandStore, fuzzy search)
   - ✅ Integration tests: Yes (Cmd+K, keyboard nav)
   - ❌ **MISSING:** Keyboard shortcut conflict tests (Ctrl+K vs browser dev console)
   - ❌ **MISSING:** Cross-browser tests (Cmd+K on Mac vs Ctrl+K on Windows/Linux)

**Jez Humble Pattern Violation:**
- **"Test Automation"** — Visual regression manual, keyboard testing manual
- **"Continuous Testing"** — No automated accessibility gate

---

#### Plan 17-06: Onboarding Wizard + Mobile Polish

**QA Score: 50/100** ❌ WCAG AUDIT GAP

**Accessibility Testing:**
- ✅ **Good:** WCAG 2.1 AA target specified
- ✅ **Good:** Full audit mentioned (axe-core, keyboard, screen reader)
- ❌ **CRITICAL:** No "block merge if violations" policy
- ❌ **MISSING:** Success metrics undefined (≤ 5 AA violations — HOW measured?)

**Specific Issues:**

1. **Line 125-148:** "Full WCAG 2.1 AA accessibility audit" — Execution undefined:
   - "Run axe-core scan" — Manual or CI/CD?
   - "Fix all WCAG Level A violations" — Who validates? Automated?
   - "≤ 5 Level AA violations" — Which violations allowed? Why?
   - No CI/CD integration (should block merges with violations)
   - No baseline scan (current state unknown)

2. **Line 151-172:** "BrowserStack mobile validation" — Device diversity still insufficient:
   - iPhone 14, Pixel 5 (ONLY 2 DEVICES)
   - Missing: iPad Mini (tablet), iPhone SE (small screen), Samsung Galaxy (Android variety)
   - Manual testing only — No automated regression

3. **Line 267-297:** "Testing Strategy" — Missing performance tests:
   - ✅ Unit tests: Yes (onboarding state, swipe gestures)
   - ✅ Integration tests: Yes (wizard flow, mobile nav)
   - ✅ Mobile tests: Yes (BrowserStack swipe gestures)
   - ❌ **MISSING:** Performance tests (onboarding completion time, drop-off tracking)
   - ❌ **MISSING:** Analytics tests (completion rate ≥ 80% — HOW measured?)

**Nicole Forsgren DevOps Metrics Violation:**
- **"Lead Time for Changes"** — Manual WCAG audit slows deployment
- **"Change Failure Rate"** — No automated accessibility regression protection

---

### Cross-Plan QA Concerns

#### 1. RAF Validation Automation Gap (CRITICAL)

**Problem:** Performance validation manual, no CI/CD integration

**Current Plans (17-03, 17-04):**
```typescript
// Manual measurement (UNACCEPTABLE):
// "Measure P99 frame time during 24-brain burst"
// "Document baseline performance"
```

**Attack Vector:** Performance regression slips through to production

**Required Fix (Jez Humble — "Continuous Delivery"):**

**Create automated performance test:**
```typescript
// e2e/performance/raf-validation.spec.ts
import { test, expect } from '@playwright/test';

test('RAF validation: 24-brain burst maintains 60fps', async ({ page }) => {
  // Navigate to monitoring panel
  await page.goto('/war-room');

  // Inject custom performance instrumentation
  await page.evaluate(() => {
    window.rafMetrics = {
      frameTimes: [],
      longTasks: []
    };

    const observer = new PerformanceObserver((list) => {
      for (const entry of list.getEntries()) {
        if (entry.duration > 50) {
          window.rafMetrics.longTasks.push(entry.duration);
        }
      }
    });
    observer.observe({ entryTypes: ['measure', 'longtask'] });

    // Wrap requestAnimationFrame
    const originalRAF = window.requestAnimationFrame;
    window.requestAnimationFrame = (callback) => {
      const start = performance.now();
      return originalRAF((time) => {
        const frameTime = performance.now() - start;
        window.rafMetrics.frameTimes.push(frameTime);
        return callback(time);
      });
    };
  });

  // Trigger 24-brain burst
  await page.click('[data-testid="trigger-all-brains"]');

  // Wait for all brains to complete
  await page.waitForSelector('[data-status="completed"]', { timeout: 10000 });

  // Extract metrics
  const metrics = await page.evaluate(() => {
    const frameTimes = window.rafMetrics.frameTimes;
    const p99 = frameTimes.sort((a, b) => b - a)[Math.floor(frameTimes.length * 0.01)];
    return {
      p99,
      longTaskCount: window.rafMetrics.longTasks.length,
      avgFrameTime: frameTimes.reduce((a, b) => a + b, 0) / frameTimes.length
    };
  });

  // Assertions (FAIL BUILD IF REGRESSION)
  expect(metrics.p99).toBeLessThan(16.67);  // P99 < 16.67ms (60fps)
  expect(metrics.longTaskCount).toBe(0);    // Zero long tasks (> 50ms)
  expect(metrics.avgFrameTime).toBeLessThan(10);  // Avg < 10ms
});
```

**CI/CD Integration (GitHub Actions):**
```yaml
# .github/workflows/performance-regression.yml
name: Performance Regression

on:
  pull_request:
    paths:
      - 'apps/web/src/components/monitoring/**'
      - 'apps/web/src/components/cost/**'

jobs:
  raf-validation:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
      - run: pnpm install
      - run: pnpm build
      - run: pnpm test:e2e raf-validation.spec.ts
      # FAIL PR IF P99 > 16.67ms
```

**Impact:** Plans 17-03, 17-04 cannot execute without automated performance gates

---

#### 2. Mobile Testing Coverage Gap (HIGH RISK)

**Problem:** Only 2 devices specified, insufficient device diversity

**Current Plans (17-03, 17-06):**
```yaml
BrowserStack devices:
  - iPhone 14
  - Pixel 5
```

**Attack Vector:** Bugs slip through on untested devices (iPad, older iPhones, Samsung)

**Required Fix (Nicole Forsgren — "DevOps Metrics"):**

**Expand device matrix (minimum 6 devices):**
```yaml
# playwright.config.ts
devices: {
  // Phones (4)
  'iPhone 14': { platform: 'iOS', version: '16' },
  'iPhone SE': { platform: 'iOS', version: '15' },  // Small screen
  'Pixel 5': { platform: 'Android', version: '12' },
  'Samsung Galaxy S22': { platform: 'Android', version: '12' },

  // Tablets (2)
  'iPad Mini': { platform: 'iOS', version: '16' },
  'iPad Pro': { platform: 'iOS', version: '16' }
}
```

**BrowserStack Plan:**
- **Current:** $39/month (Automate 2 parallel) — INSUFFICIENT
- **Required:** $199/month (Automate 5 parallel) — Test 6 devices in parallel

**Cost-Benefit Analysis:**
- **Current:** 2 devices × 5 min/test = 10 min per PR
- **Required:** 6 devices × 5 min/test = 30 min... BUT 5 parallel = 6 min total
- **ROI:** 1 bug caught on iPad SE = $39/month saved (customer support time)

**Impact:** Plans 17-03, 17-06 require device matrix expansion

---

#### 3. Visual Regression Automation Gap (HIGH RISK)

**Problem:** Manual baseline capture, no CI/CD integration

**Current Plans (17-02, 17-05):**
```bash
# Manual capture (UNACCEPTABLE):
pnpm capture-baselines
# Verify screenshots committed to git
```

**Attack Vector:** Layout regressions slip through to production

**Required Fix (Jez Humble — "Continuous Delivery"):**

**Automated visual regression (Percy or Playwright native):**

**Option A: Playwright Native (Recommended — Free):**
```typescript
// e2e/visual/company-rail.spec.ts
import { test, expect } from '@playwright/test';

test('CompanyRail visual regression', async ({ page }) => {
  await page.goto('/war-room');

  // Capture screenshot with diff threshold
  await expect(page).toHaveScreenshot('company-rail-expanded.png', {
    maxDiffPixels: 100,  // Allow 100px diff (anti-aliasing)
    maxDiffRatio: 0.02   // Allow 2% diff (browser rendering differences)
  });

  // Test collapsed state
  await page.click('[data-testid="collapse-company-rail"]');
  await expect(page).toHaveScreenshot('company-rail-collapsed.png', {
    maxDiffPixels: 100,
    maxDiffRatio: 0.02
  });
});
```

**CI/CD Integration (GitHub Actions):**
```yaml
# .github/workflows/visual-regression.yml
name: Visual Regression

on:
  pull_request:
    paths:
      - 'apps/web/src/components/layout/**'
      - 'apps/web/src/components/command/**'

jobs:
  visual-regression:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
      - run: pnpm install
      - run: pnpm build
      - run: pnpm test:e2e:visual
      # FAIL PR IF LAYOUT REGRESSION DETECTED
```

**Option B: Percy.io ($49/month — More features):**
- Automatic diff highlighting
- Baseline management UI
- Review and approve workflow

**Impact:** Plans 17-02, 17-05 require automated visual regression

---

#### 4. Accessibility CI/CD Integration Gap (HIGH RISK)

**Problem:** axe-core scans manual, no "block merge if violations" policy

**Current Plans (17-02, 17-04, 17-05, 17-06):**
```typescript
// Manual scan (UNACCEPTABLE):
// "Run axe-core scan on CompanyRail"
// "Fix any WCAG violations"
```

**Attack Vector:** Accessibility regressions slip through

**Required Fix (Jez Humble — "Continuous Delivery"):**

**Automated accessibility tests (axe-core + Playwright):**
```typescript
// e2e/accessibility/company-rail.spec.ts
import { test, expect } from '@playwright/test';
import AxeBuilder from '@axe-core/playwright';

test('CompanyRail accessibility (WCAG 2.1 AA)', async ({ page }) => {
  await page.goto('/war-room');

  // Scan with axe-core
  const accessibilityScanResults = await new AxeBuilder({ page })
    .withTags(['wcag2a', 'wcag2aa', 'wcag21aa'])
    .analyze();

  // FAIL BUILD IF VIOLATIONS FOUND
  expect(accessibilityScanResults.violations).toEqual([]);

  // Test keyboard navigation
  await page.keyboard.press('Tab');
  await expect(page.locator('[data-testid="company-rail"]')).toBeFocused();
});
```

**CI/CD Integration (GitHub Actions):**
```yaml
# .github/workflows/accessibility.yml
name: Accessibility (WCAG 2.1 AA)

on:
  pull_request:
    paths:
      - 'apps/web/src/components/**'

jobs:
  accessibility:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
      - run: pnpm install
      - run: pnpm build
      - run: pnpm test:e2e:accessibility
      # FAIL PR IF WCAG VIOLATIONS DETECTED
```

**Impact:** Plans 17-02, 17-04, 17-05, 17-06 require automated accessibility gates

---

### Must-Fix Changes (Before Execution)

#### 1. Plan 17-03: Add Automated RAF Validation

**Add to 17-03-PLAN.md Task 4:**

```markdown
### Task 4: Optimize for 60fps performance (AUTOMATED TEST REQUIRED)

**Files:**
- `apps/web/src/utils/raf-monitor.ts` (new)
- `e2e/performance/raf-validation.spec.ts` (new)

**Subtasks:**
- [ ] Create RAFMonitor class (from raf-validation-plan.md)
- [ ] Create automated performance test (Playwright + custom RAF instrumentation)
- [ ] Test 24-brain burst, measure P99 frame time
- [ ] Assert P99 < 16.67ms (FAIL BUILD IF REGRESSION)
- [ ] Assert zero long tasks (> 50ms)
- [ ] Add to CI/CD (GitHub Actions workflow)
- [ ] Document baseline performance (before optimization)

**Acceptance:**
- Automated test measures P99 during 24-brain burst
- Test fails if P99 ≥ 16.67ms (60fps threshold)
- Test fails if long tasks detected (> 50ms)
- CI/CD blocks merges if performance regression detected
- Baseline documented in test file comments
```

---

#### 2. Plan 17-02: Add Automated Visual Regression

**Add to 17-02-PLAN.md Task 5:**

```markdown
### Task 5: Capture visual regression baseline (AUTOMATED)

**Files:**
- `e2e/visual/company-rail.spec.ts` (new)
- `.github/workflows/visual-regression.yml` (new)

**Subtasks:**
- [ ] Create Playwright visual test (CompanyRail collapsed/expanded)
- [ ] Define diff threshold (maxDiffPixels: 100, maxDiffRatio: 0.02)
- [ ] Add to CI/CD (GitHub Actions workflow)
- [ ] Run on PRs targeting master branch
- [ ] FAIL PR if layout regression detected

**Acceptance:**
- Visual test captures CompanyRail screenshots (collapsed/expanded)
- Diff threshold defined (allow 2% pixel diff for browser rendering)
- CI/CD runs test on every PR
- Build fails if visual regression detected
- Baseline screenshots committed to git for review
```

---

#### 3. Plan 17-06: Add Automated Accessibility Gates

**Add to 17-06-PLAN.md Task 5:**

```markdown
### Task 5: Full WCAG 2.1 AA accessibility audit (AUTOMATED)

**Files:**
- `e2e/accessibility/full-audit.spec.ts` (new)
- `.github/workflows/accessibility.yml` (new)

**Subtasks:**
- [ ] Create axe-core scan test (all Phase 17 components)
- [ ] Configure WCAG 2.1 AA rules (wcag2a, wcag2aa, wcag21aa)
- [ ] Add keyboard navigation tests (Tab, Enter, Escape, Arrow keys)
- [ ] Add to CI/CD (GitHub Actions workflow)
- [ ] FAIL PR if WCAG Level A violations detected
- [ ] WARN if Level AA violations > 5

**Manual Testing (Still Required):**
- [ ] Screen reader testing (NVDA on Windows, VoiceOver on macOS)
- [ ] Color contrast validation (axe DevTools)
- [ ] Touch target size validation (DevTools ruler)
- [ ] Reflow check (200% zoom, no horizontal scroll)

**Acceptance:**
- Automated axe-core scan passes (zero Level A violations)
- Keyboard navigation automated (all interactions, no mouse)
- CI/CD blocks merges if WCAG violations detected
- Manual screen reader testing documented
- ≤ 5 Level AA violations allowed (contrast + focus visible only)
```

---

### Risks Identified

| Risk | Severity | Plan(s) | Mitigation |
|------|----------|---------|------------|
| **Performance regression undetected** | 🔴 CRITICAL | 17-03, 17-04 | Add automated RAF validation test in CI/CD |
| **Layout regression undetected** | 🔴 CRITICAL | 17-02, 17-05 | Add automated visual regression test (Playwright) |
| **Accessibility regression undetected** | 🔴 CRITICAL | 17-02, 17-04, 17-05, 17-06 | Add automated axe-core scan in CI/CD |
| **Mobile device coverage insufficient** | 🟠 HIGH | 17-03, 17-06 | Expand to 6 devices (2 phones + 2 tablets + 2 Android) |
| **BrowserStack plan insufficient** | 🟠 HIGH | 17-03, 17-06 | Upgrade to $199/month (5 parallel tests) |
| **WebSocket testing undefined** | 🟡 MEDIUM | 17-04 | Add WebSocket mock + failure scenario tests |
| **Keyboard shortcut conflicts** | 🟡 MEDIUM | 17-05 | Test Ctrl+K vs browser dev console (all browsers) |

---

### Recommendations

#### 1. Create QA Architecture Document (NEW)

**Create file:** `.planning/phases/17-ui-evolution/17-QA-ARCH.md`

**Contents:**
- CI/CD pipeline architecture (GitHub Actions workflows)
- Performance testing strategy (RAF validation, Lighthouse CI)
- Visual regression strategy (Playwright native vs Percy)
- Accessibility testing strategy (axe-core + manual screen reader)
- Mobile testing strategy (BrowserStack device matrix)
- Test environment setup (local, CI, pre-production)

**Why:** Frontend plans cannot execute without QA infrastructure

---

#### 2. Define Test Pyramid Balance

**Current state (from plans):**
- Unit tests: ~30% (Vitest)
- Integration tests: ~40% (Playwright)
- E2E tests: ~30% (Playwright)

**Recommended balance (Jez Humble — "Test Pyramid"):**
- Unit tests: 70% (fast, isolated, cheap)
- Integration tests: 20% (API integration, WebSocket)
- E2E tests: 10% (critical user flows only)

**Why:** E2E tests are slow, flaky, expensive. Shift left to unit tests.

---

#### 3. Add Performance Budgets

**Create file:** `apps/web/.github/performance-budget.json`

**Budgets:**
```json
{
  "RAF": {
    "P99": 16.67,
    "longTasks": 0
  },
  "Lighthouse": {
    "performance": 90,
    "accessibility": 100,
    "best-practices": 90
  },
  "BundleSize": {
    "js": 200,
    "css": 50
  }
}
```

**Why:** Performance budgets prevent regressions automatically

---

#### 4. Add Analytics Tracking

**For Plan 17-06 (Onboarding):**
```typescript
// Track completion rate
analytics.track('onboarding_completed', {
  steps: 4,
  duration: 180,  // seconds
  drop_off_step: null
});
```

**Why:** Success metrics (≥ 80% completion) require measurement

---

### QA Score Breakdown

| Plan | Score | Rationale |
|------|-------|-----------|
| **17-02** | 65/100 | Visual regression manual, accessibility not automated |
| **17-03** | 50/100 | RAF validation manual, mobile device coverage insufficient |
| **17-04** | 55/100 | WebSocket testing undefined, performance not automated |
| **17-05** | 70/100 | Visual regression manual, keyboard conflicts untested |
| **17-06** | 50/100 | WCAG audit manual, device coverage insufficient |
| **Overall** | **58/100** | ⚠️ **3 critical gaps must be fixed before execution** |

---

### Next Steps (QA Team)

1. **CRITICAL:** Create `.planning/phases/17-ui-evolution/17-QA-ARCH.md`
2. **CRITICAL:** Update Plan 17-03 Task 4 with automated RAF validation
3. **CRITICAL:** Update Plan 17-02 Task 5 with automated visual regression
4. **CRITICAL:** Update Plan 17-06 Task 5 with automated accessibility gates
5. **HIGH:** Expand BrowserStack device matrix to 6 devices
6. **HIGH:** Add WebSocket testing strategy to Plan 17-04
7. **MEDIUM:** Define test pyramid balance (70% unit, 20% integration, 10% E2E)
8. **MEDIUM:** Add performance budgets (Lighthouse CI, bundle size)

**Blocker:** Plans 17-02, 17-03, 17-04, 17-05, 17-06 CANNOT execute until QA automation is specified

---

**Brain #6 Consultation Complete**
**Recommendation:** ⚠️ **ADDRESS CRITICAL QA GAPS BEFORE EXECUTION**
**Expertise Applied:** Jez Humble (CI/CD), Nicole Forsgren (DevOps metrics), Michael Feathers (testing strategy)

---

## Brain #2 (UX Research) Output

> **Expertise Applied:** Don Norman (affordances, mental models), Jakob Nielsen (heuristics, usability), Laurie Hall (information architecture)
> **Evaluation Date:** 2026-04-09
> **Plans Reviewed:** 17-02, 17-03, 17-04, 17-05, 17-06 + CONTEXT

### Executive Summary

Phase 17 plans demonstrate strong attention to accessibility (WCAG 2.1 AA) and mobile responsiveness, but raise **critical cognitive load concerns**. The 24-brain simultaneous display violates Miller's Law (7±2 items in working memory) despite density mode mitigations. Hick's Law applies to command palette (4 categories optimal), but onboarding wizard (4 steps) exceeds optimal length. Mobile swipe gestures lack discoverability patterns. **Recommendation:** Reduce onboarding to 3 steps, add domain grouping for 24-brain display, include swipe gesture hints in first-run experience.

**Overall UX Research Score: 79/100**

---

### Plan-by-Plan Analysis

#### Plan 17-02: Multi-tenant Company Switcher

**UX Score: 85/100**

**Strengths:**
- Visual status indicators (green/yellow/red dots) follow established color semantics ✅
- Drag-and-drop with @dnd-kit includes visual affordances (drag handle on hover) ✅
- Tenant isolation enforced server-side (security = UX trust) ✅
- Keyboard navigation specified (Tab, Enter, Arrow keys) ✅

**Critical Issues:**

1. **Drag-and-Drop Discoverability (Nielsen Heuristic #6: Recognition vs Recall)**
   - **Problem:** Drag handle appears "on hover" — not discoverable for first-time users
   - **Evidence:** Norman's "affordances" principle — invisible affordance = no affordance
   - **Fix:** Add visual hint (subtle drag icon visible at 60% opacity, full opacity on hover)
   - **Priority:** HIGH — affects onboarding curve

2. **Cross-Tab Sync Cognitive Load (Miller's Law)**
   - **Problem:** localStorage events auto-update company order — can surprise users
   - **Evidence:** User may lose mental model of "active company" if another tab changes it
   - **Fix:** Add toast notification ("Company order updated in another tab")
   - **Priority:** MEDIUM — edge case but disorienting

3. **Status Badge Polling (30s interval) — Perceived Performance**
   - **Problem:** 30s polling feels slow for real-time status updates
   - **Evidence:** Nielsen's "system status visibility" heuristic — users expect <100ms feedback
   - **Fix:** Reduce to 10s OR add "Last updated: X seconds ago" timestamp
   - **Priority:** LOW — nice-to-have for perceived responsiveness

**UX Score Breakdown:**
- Learnability: 80/100 (drag handle discoverability issue)
- Efficiency: 90/100 (keyboard nav works well)
- Memorability: 85/100 (visual status aids memory)
- Errors: 90/100 (tenant isolation prevents catastrophic errors)
- Satisfaction: 85/100 (solid overall)

---

#### Plan 17-03: ActiveAgentsPanel with 24-Brain Display

**UX Score: 72/100** ⚠️ COGNITIVE LOAD CONCERNS

**Strengths:**
- Density modes (compact/normal/detailed) address information overload ✅
- Status badges with color coding follow universal semantics ✅
- `prefers-reduced-motion` respected (accessibility best practice) ✅
- Ping animation provides clear feedback for active brains ✅

**Critical Issues:**

1. **24-Brain Display Violates Miller's Law (CRITICAL)**
   - **Problem:** 24 simultaneous status badges = 3.4x Miller's limit (7±2 items)
   - **Evidence:** Cognitive psychology research — working memory capacity ~4 items for complex stimuli
   - **Fix:** Add domain grouping (Product Strategy brains, UX brains, etc.) with collapsible sections
   - **Priority:** CRITICAL — core usability issue

2. **Density Modes Insufficient Mitigation (Hick's Law)**
   - **Problem:** Compact mode still shows 24 items (just less info per item) — Hick's Law applies to COUNT, not detail
   - **Evidence:** Hick's Law: decision time = log2(N) where N = number of choices
   - **Fix:** Default to "Active Brains Only" view (typically 3-5 running), show all 24 on-demand
   - **Priority:** HIGH — affects time-to-completion for monitoring tasks

3. **Swipe Gestures Lack Discoverability (Nielsen Heuristic #6)**
   - **Problem:** "Swipe left to reveal actions" not discoverable without visual hint
   - **Evidence:** Mobile UX research — swipe gestures require onboarding hints (Material Design patterns)
   - **Fix:** Add first-run tooltip ("Swipe left for actions") OR subtle affordance (arrow peek at edge)
   - **Priority:** HIGH — mobile primary interaction pattern

4. **Status Badge Color-Only Coding (Accessibility Gap)**
   - **Problem:** "Green/Yellow/Red" relies on color alone — WCAG 2.1 AA violation (1.4.1 Use of Color)
   - **Evidence:** ~8% of male population has color vision deficiency
   - **Fix:** Add icons (check circle, warning triangle, error X) alongside color
   - **Priority:** MEDIUM — accessibility requirement but plans mention WCAG audit later

**UX Score Breakdown:**
- Learnability: 65/100 (24-brain display overwhelms new users)
- Efficiency: 75/100 (density modes help but don't solve cognitive load)
- Memorability: 70/100 (too many items to remember status patterns)
- Errors: 80/100 (status badges clear but color-only issue)
- Satisfaction: 70/100 (functional but stressful to monitor)

---

#### Plan 17-04: Cost Dashboard with MetricCard + QuotaBar

**UX Score: 88/100**

**Strengths:**
- Hierarchical breakdown (per brain → per company → total) follows information architecture best practices ✅
- QuotaBar with color coding (green/yellow/red) provides clear at-a-glance status ✅
- Real-time updates via WebSocket meet "system status visibility" heuristic ✅
- Drill-down from MetricCard to brain detail follows natural user workflow ✅

**Critical Issues:**

1. **QuotaBar Color-Only Coding (Accessibility Gap)**
   - **Problem:** "Green/Yellow/Red" progress bar relies on color alone
   - **Evidence:** WCAG 2.1 AA 1.4.1 — "Color not used as the only visual means of conveying information"
   - **Fix:** Add percentage text AND icons (check/warning/error)
   - **Priority:** MEDIUM — noted in 17-06 WCAG audit, but should be fixed here

2. **Real-Time Cost Updates — Cognitive Overload Risk**
   - **Problem:** WebSocket streaming cost updates for 24 brains = continuous visual change
   - **Evidence:** "Motion blindness" — users ignore constantly-changing elements
   - **Fix:** Batch updates every 5s OR add "pause updates" button
   - **Priority:** LOW — nice-to-have for focus-intensive tasks

3. **Budget Enforcement Visual Warnings (Alert Fatigue Risk)**
   - **Problem:** Yellow at 80%, red at 100% — may cause "alarm fatigue" if budget frequently hit
   - **Evidence:** Nielsen's "error prevention" heuristic — warnings should be meaningful
   - **Fix:** Add "snooze warning" setting OR predictive warnings ("You'll hit budget in 2 days at current rate")
   - **Priority:** LOW — edge case for power users

**UX Score Breakdown:**
- Learnability: 90/100 (hierarchical breakdown intuitive)
- Efficiency: 85/100 (real-time updates may distract)
- Memorability: 90/100 (visual patterns easy to recall)
- Errors: 85/100 (clear warnings but color-only issue)
- Satisfaction: 90/100 (strong overall)

---

#### Plan 17-05: Command Palette with Global Search

**UX Score: 82/100**

**Strengths:**
- 4 categories (Navigation, Brains, Actions, Settings) aligns with Hick's Law optimal range ✅
- Keyboard navigation (Arrow keys, Enter, Escape) follows power user expectations ✅
- Fuzzy search with debouncing (300ms) reduces perceived lag ✅
- Category grouping with icons reduces cognitive load ✅

**Critical Issues:**

1. **Cmd+K Discoverability (Nielsen Heuristic #6)**
   - **Problem:** Power user shortcut — not discoverable for new users
   - **Evidence:** Norman's "affordances" — keyboard shortcuts need visual hints
   - **Fix:** Add "Search... ⌘K" placeholder in search bar (if exists) OR onboarding hint
   - **Priority:** MEDIUM — affects new user activation

2. **Fuzzy Search — False Positives Risk (Hick's Law)**
   - **Problem:** Fuzzy matching may show irrelevant results, increasing decision time
   - **Evidence:** Hick's Law — more choices = longer decision time, even if filtered
   - **Fix:** Add relevance scoring threshold (hide matches <60% relevance) OR "exact match first" sort
   - **Priority:** MEDIUM — affects command palette efficiency

3. **24 Brain Commands in Single Category (Miller's Law)**
   - **Problem:** "Brains" category has 24 items — exceeds working memory capacity
   - **Evidence:** Same Miller's Law issue as 17-03
   - **Fix:** Group brains by domain (Product Strategy, UX Research, etc.) within command palette
   - **Priority:** HIGH — affects command palette usability

**UX Score Breakdown:**
- Learnability: 75/100 (Cmd+K not discoverable)
- Efficiency: 90/100 (fuzzy search + keyboard nav efficient)
- Memorability: 85/100 (4 categories memorable)
- Errors: 80/100 (fuzzy search may confuse)
- Satisfaction: 80/100 (power users love it, new users miss it)

---

#### Plan 17-06: Onboarding Wizard + Mobile Polish

**UX Score: 78/100**

**Strengths:**
- WCAG 2.1 AA audit comprehensive (zero Level A violations, ≤5 AA violations) ✅
- BrowserStack validation for real devices (iPhone 14, Pixel 5) ✅
- Touch targets ≥44x44px meets WCAG 2.5.5 ✅
- Progress indicator ("Step 1 of 4") manages expectations ✅

**Critical Issues:**

1. **4-Step Wizard Exceeds Optimal Length (Drop-off Risk)**
   - **Problem:** 4 steps (Welcome, Company, Adapter, Validation) = ~20% drop-off per step (industry benchmark)
   - **Evidence:** Laurie Hall's onboarding research — 3 steps max for "quick start"
   - **Fix:** Merge "Company" + "Adapter" into single step OR make onboarding skippable with "minimal setup"
   - **Priority:** HIGH — affects user activation rate

2. **Skip Button Placement (F-pattern Scanning)**
   - **Problem:** Skip button mentioned but placement unclear — if top-right, may be missed
   - **Evidence:** Nielsen's "F-pattern" eye tracking — users scan left-to-right, top-to-bottom
   - **Fix:** Place skip button bottom-left (opposite to Next button) OR add "Skip for now" link below primary CTA
   - **Priority:** MEDIUM — affects returning user experience

3. **Mobile Swipe Gestures — First-Run Discoverability**
   - **Problem:** Swipe gestures (left/right/pull-to-refresh) not mentioned in onboarding
   - **Evidence:** Mobile UX research — swipe gestures have 0% discoverability without hints
   - **Fix:** Add Step 0: "Gesture Tour" (interactive swipe demo) OR tooltip on first swipe
   - **Priority:** HIGH — mobile primary interaction pattern

4. **WCAG 2.1 AA Scope — Cognitive Load Not Addressed**
   - **Problem:** Audit covers visual, auditory, motor accessibility — NOT cognitive accessibility
   - **Evidence:** WCAG 2.1 Guidelines 2.3 (seizures) and 2.4 (navigable) but cognitive load (2.3.3) not tested
   - **Fix:** Add cognitive load testing (e.g., "time to find running brain" <5 seconds for 95th percentile)
   - **Priority:** MEDIUM — edge case but affects neurodiverse users

**UX Score Breakdown:**
- Learnability: 70/100 (4 steps too long, swipe gestures not taught)
- Efficiency: 85/100 (mobile polish strong)
- Memorability: 80/100 (progress indicator helps)
- Errors: 85/100 (validation prevents errors)
- Satisfaction: 70/100 (onboarding feels long)

---

### Cross-Plan Concerns

#### 1. Miller's Law Violation (24-Brain Display) — CRITICAL

**Affects:** 17-03 (ActiveAgentsPanel), 17-05 (Command Palette "Brains" category)

**Problem:** Displaying 24 items simultaneously exceeds working memory capacity (7±2 items). Density modes reduce detail per item but not item COUNT. Hick's Law still applies: decision time increases logarithmically with choices.

**Recommendation:** Group 24 brains by domain (6 domains × 4 brains each). Default view: "Active Brains Only" (typically 3-5 running). Show all 24 on-demand via "Show All" toggle.

**Priority:** CRITICAL — Affects core usability

---

#### 2. Hick's Law Applied to Command Palette (4 Categories) — ACCEPTABLE

**Affects:** 17-05 (Command Palette)

**Finding:** 4 categories (Navigation, Brains, Actions, Settings) is within optimal range. Hick's Law suggests 4-7 choices is ideal for rapid decision-making.

**Recommendation:** Keep 4 categories, BUT group "Brains" by domain (see Miller's Law above).

**Priority:** MEDIUM — Domain grouping needed within Brains category

---

#### 3. Mobile Swipe Gestures — Discoverability Gap — HIGH

**Affects:** 17-03 (ActiveAgentsPanel), 17-06 (Onboarding Wizard)

**Problem:** Swipe gestures (left/right/pull-to-refresh) have 0% discoverability without visual hints. Plans mention testing via BrowserStack but not first-run education.

**Recommendation:** Add swipe gesture hints in onboarding (Step 0: "Gesture Tour") OR contextual tooltips ("Swipe left for actions" on first brain card view).

**Priority:** HIGH — Mobile primary interaction pattern

---

#### 4. Color-Only Coding (Accessibility Gap) — MEDIUM

**Affects:** 17-03 (Status Badges), 17-04 (QuotaBar)

**Problem:** "Green/Yellow/Red" relies on color alone — WCAG 2.1 AA 1.4.1 violation. Plans mention WCAG audit in 17-06 but should be fixed per-plan.

**Recommendation:** Add icons alongside color (check circle, warning triangle, error X). Fix in 17-03 and 17-04 before 17-06 audit.

**Priority:** MEDIUM — Accessibility requirement but deferred to audit

---

#### 5. Onboarding Length (4 Steps) — Drop-off Risk — HIGH

**Affects:** 17-06 (Onboarding Wizard)

**Problem:** 4-step wizard = ~20% drop-off per step (industry benchmark). 4 steps × 20% = ~60% completion rate (below 80% target in plan).

**Recommendation:** Merge "Company" + "Adapter" steps OR add "minimal setup" path (company name only, configure later).

**Priority:** HIGH — Affects user activation rate

---

### UX Research Score: 79/100

**Score Breakdown:**
- **Information Architecture:** 75/100 (24-brain display violates Miller's Law, grouping needed)
- **Interaction Design:** 85/100 (keyboard nav, density modes, real-time updates solid)
- **Mobile UX:** 75/100 (swipe gestures lack discoverability, touch targets specified)
- **Accessibility:** 80/100 (WCAG 2.1 AA audit comprehensive but color-only coding gaps)
- **Learnability:** 75/100 (onboarding too long, Cmd+K not discoverable)
- **Efficiency:** 85/100 (command palette efficient for power users, density modes help)

**Overall:** Solid foundation but critical cognitive load issues must be addressed before execution.

---

### Must-Fix Changes (5 Priority Items)

#### CRITICAL #1: Add Domain Grouping for 24-Brain Display (Plans 17-03, 17-05)

**Current:** ActiveAgentsPanel shows all 24 brains in flat grid. Command Palette "Brains" category lists all 24.

**Problem:** Violates Miller's Law (7±2 items in working memory). Users cannot scan 24 status badges efficiently.

**Fix:**
1. Group 24 brains by domain (6 domains: Product Strategy, UX Research, UI Design, Frontend, Backend, QA/DevOps)
2. Add collapsible sections per domain (default: show all domains collapsed)
3. "Active Brains Only" toggle as default view (shows 3-5 running brains)
4. Command Palette: "Brains" category shows domain sub-groups

**Updated Success Criteria (17-03):**
- ActiveAgentsPanel groups brains by domain with collapsible sections
- Default view: "Active Brains Only" (≤5 brains shown)
- P99 frame time < 16.67ms during domain expand/collapse (new RAF test)

**Updated Success Criteria (17-05):**
- Command Palette "Brains" category shows domain sub-groups
- Fuzzy search filters across domains (domain name searchable)

**Files to Update:**
- `17-03-PLAN.md` — Add Task: "Implement domain grouping with collapsible sections"
- `17-05-PLAN.md` — Add Subtask: "Group brain commands by domain"

---

#### CRITICAL #2: Reduce Onboarding to 3 Steps (Plan 17-06)

**Current:** 4-step wizard (Welcome, Company, Adapter, Validation).

**Problem:** 4 steps = ~60% completion rate (below 80% target). Each step adds ~20% drop-off.

**Fix:** Merge "Company" + "Adapter" into single step OR add "minimal setup" path.

**Updated Success Criteria (17-06):**
- Onboarding wizard completes in 3 steps (Welcome, Setup, Validation)
- Completion rate ≥ 80% (measure via analytics)
- "Minimal setup" option: Company name only, configure adapter later

**Updated Tasks (17-06):**
- Task 1: Merge CompanyStep + AdapterStep into SetupStep
- Task 2: Add "minimal setup" path (skip adapter config, show "Configure API Keys" CTA in dashboard)

**Files to Update:**
- `17-06-PLAN.md` — Update Task 1 (OnboardingWizard component), Task 2 (onboardingStore)

---

#### HIGH PRIORITY #3: Add Swipe Gesture Discoverability Hints (Plans 17-03, 17-06)

**Current:** Swipe gestures tested via BrowserStack but no first-run education.

**Problem:** Swipe gestures have 0% discoverability without hints.

**Fix:** Add onboarding hint OR contextual tooltip.

**Updated Success Criteria (17-06):**
- Onboarding includes "Gesture Tour" (Step 0) OR tooltip on first swipe
- Swipe gesture success rate ≥ 95% (measured via real device tests)

**Updated Tasks (17-06):**
- Task 1: Add GestureTourStep (interactive swipe demo) OR SwipeHintTooltip component
- Task 4: Track first swipe event, show tooltip if not yet shown

**Files to Update:**
- `17-06-PLAN.md` — Add Task: "Implement swipe gesture discoverability hints"

---

#### HIGH PRIORITY #4: Fix Color-Only Coding for Status Badges + QuotaBar (Plans 17-03, 17-04)

**Current:** Status badges (17-03) and QuotaBar (17-04) use color alone (Green/Yellow/Red).

**Problem:** WCAG 2.1 AA 1.4.1 violation — color not sole visual means.

**Fix:** Add icons alongside color.

**Updated Success Criteria (17-03):**
- Status badges include icons (CheckCircle, AlertTriangle, ErrorX)
- Screen reader announces icon + color ("Product Strategy is running - green check")

**Updated Success Criteria (17-04):**
- QuotaBar includes percentage text + icons
- Color coding reinforced with shape (check/warning/error)

**Updated Tasks (17-03):**
- Task 2: Update StatusBadge component to include icons

**Updated Tasks (17-04):**
- Task 3: Update QuotaBar component to include icons + percentage text

**Files to Update:**
- `17-03-PLAN.md` — Update Task 2 (StatusBadge component)
- `17-04-PLAN.md` — Update Task 3 (QuotaBar component)

---

#### MEDIUM PRIORITY #5: Add Cmd+K Discoverability Hint (Plan 17-05)

**Current:** Cmd+K shortcut mentioned but no visual hint in UI.

**Problem:** Keyboard shortcuts not discoverable for new users.

**Fix:** Add "Search... ⌘K" placeholder in search bar (if exists) OR onboarding hint.

**Updated Success Criteria (17-05):**
- Command palette shortcut hint visible in UI (search bar placeholder OR onboarding tooltip)
- New user activation rate (use command palette within first session) ≥ 40%

**Updated Tasks (17-05):**
- Task 2: Add shortcut hint to CommandPalette OR add hint to onboarding (17-06)

**Files to Update:**
- `17-05-PLAN.md` — Update Task 2 (CommandPalette dialog component)

---

### Risks Identified

| Risk | Severity | Plan(s) | Mitigation |
|------|----------|---------|------------|
| **Cognitive Overload (24-Brain Display)** | 🔴 CRITICAL | 17-03, 17-05 | Domain grouping + "Active Brains Only" default view |
| **Onboarding Drop-off (4 Steps)** | 🔴 CRITICAL | 17-06 | Reduce to 3 steps OR "minimal setup" path |
| **Swipe Gesture Undiscoverability** | 🟠 HIGH | 17-03, 17-06 | First-run gesture hints (onboarding or tooltips) |
| **WCAG 2.1 AA Compliance Gap** | 🟠 HIGH | 17-03, 17-04 | Add icons to status badges + QuotaBar before audit |
| **Real-Time Update Fatigue** | 🟡 MEDIUM | 17-04 | Batch updates OR "pause updates" button |
| **Cmd+K Undiscoverable** | 🟡 MEDIUM | 17-05 | Add placeholder hint OR onboarding tooltip |

---

### Recommendations

#### 1. Execute Phase 17 in 3 Waves (Add Domain Grouping to Wave 2)

**Current Plan:**
- Wave 1: Foundation (17-01, 17-02)
- Wave 2: Monitoring (17-03, 17-04)
- Wave 3: Polish (17-05, 17-06)

**Updated Wave 2 (Must Add):**
- Wave 2: Monitoring (17-03, 17-04) + **Domain grouping for 24-brain display**
- **Add Task:** "Implement domain grouping with collapsible sections" to 17-03
- **Add Task:** "Group brain commands by domain" to 17-05

---

#### 2. Add Cognitive Load Testing to 17-06 WCAG Audit

**New Test Cases:**
- **Task:** "Find all running brains" — Target: <5 seconds for 95th percentile
- **Task:** "Trigger Product Strategy brain via command palette" — Target: <3 seconds
- **Task:** "Check cost quota for current company" — Target: <2 seconds

**Why:** WCAG 2.1 AA covers visual/auditory/motor accessibility but NOT cognitive load. Cognitive load testing measures time-based performance (usability metric).

---

#### 3. Measure Onboarding Drop-off per Step (Analytics Required)

**Analytics Events to Track:**
- `onboarding_step_1_view` → `onboarding_step_1_complete`
- `onboarding_step_2_view` → `onboarding_step_2_complete`
- `onboarding_step_3_view` → `onboarding_step_3_complete`
- `onboarding_complete`

**Target Drop-off Rates:**
- Step 1 → Step 2: <10%
- Step 2 → Step 3: <15%
- Step 3 → Complete: <10%
- **Overall completion:** ≥80%

**Why:** Industry benchmark is ~20% drop-off per step. Measuring per-step drop-off identifies friction points.

---

#### 4. Validate Swipe Gesture Hints via User Testing (5 Participants Minimum)

**Test Protocol:**
1. Show onboarding hint (gesture tour OR tooltip)
2. Ask user to "reveal actions for this brain card"
3. Observe first swipe attempt
4. Measure success rate (gesture executed correctly on first try)

**Target:** ≥95% success rate

**Why:** Swipe gestures have 0% discoverability without hints. User testing validates hint effectiveness.

---

#### 5. Add Accessibility Regression Tests to CI/CD

**Automated Tests (Every PR):**
- axe-core scan (zero Level A violations)
- Color contrast validation (all text vs backgrounds)
- Touch target size validation (all ≥44x44px on mobile)

**Manual Tests (Before Merge):**
- Cognitive load testing (time-based tasks above)
- Keyboard navigation (all interactions, no mouse)
- Screen reader testing (NVDA, VoiceOver)

**Why:** Accessibility regression caught early = cheaper fixes. CI/CD automation prevents slip-ups.

---

### Conclusion

Phase 17 plans demonstrate strong accessibility awareness and mobile responsiveness, but **critical cognitive load issues** must be addressed before execution. The 24-brain display violates Miller's Law despite density mode mitigations. Onboarding wizard exceeds optimal length. Mobile swipe gestures lack discoverability patterns.

**Recommendation:** Apply all 5 must-fix changes above, re-run Brain #7 validation, THEN execute Phase 17 via `/mm:execute-phase 17`.

**UX Research Confidence: High** — Based on established UX principles (Miller's Law, Hick's Law, Nielsen heuristics, WCAG 2.1 AA).

**Next Steps:**
1. Apply must-fix changes to PLAN.md files (17-02 through 17-06)
2. Re-run Brain #7 validation on updated plans
3. Execute Phase 17 (if Brain #7 approves)

---

**Brain #2 (UX Research) consultation complete.**
**Output appended:** 2026-04-09
**Expert sources:** Don Norman (The Design of Everyday Things), Jakob Nielsen (10 Usability Heuristics), Laurie Hall (Information Architecture), George Miller (The Magical Number Seven), Hick (On the Rate of Gain of Information)

---

## Brain #3 (UI Design) Output

> **Expertise:** Alan Cooper (Interaction Design), Luke Wroblewski (Mobile/Web Form Design), Dan Saffer (Microinteractions)
> **Date:** 2026-04-09
> **Plans Reviewed:** 17-02, 17-03, 17-04, 17-05, 17-06

---

### Executive Summary

Phase 17 plans demonstrate **solid component decomposition** and **accessibility awareness**, but have **critical gaps in visual design completeness** and **interaction discoverability**. The OKLCH color system choice is excellent (perceptually uniform, future-proof), but typography, animation easing, and gesture affordances are missing. The 5-state system is incomplete (no disabled states), and color-only indicators violate WCAG 2.1 AA.

**Overall Score: 62/100**

---

### Component Architecture Evaluation (15/25)

**What's Working:**
- ✅ Clear component decomposition: StatusBadge, MetricCard, QuotaBar, CommandPalette
- ✅ StatusBadge reused across 17-03 and 17-04 (good reusability)
- ✅ Client Components properly marked with `use client` directive
- ✅ shadcn/ui base components leveraged (Dialog, Card, Button)

**Critical Gaps:**
1. **Atomic Design Levels Not Explicit** - Components mix atoms/molecules/organisms without clear hierarchy
   - `MetricCard` (17-04) could be an atom or molecule - ambiguous
   - `ActiveAgentsPanel` (17-03) is an organism but not labeled as such
   - **Fix:** Add comment headers to each component: `// Atom: StatusBadge`, `// Organism: ActiveAgentsPanel`

2. **Missing Generic Card Component** - Multiple card types (BrainCard, MetricCard) could extend a base
   - `BrainCard` (17-03), `MetricCard` (17-04) share structure (icon + content + actions)
   - **Opportunity:** Create generic `Card` atom with variants: `card="brain"`, `card="metric"`
   - **Benefit:** Consistent spacing, hover states, elevation across all cards

3. **Density Mode Pattern Not Generic** - Implemented per component instead of as reusable pattern
   - 17-03: Density modes for ActiveAgentsPanel
   - 17-04: Density modes for MetricCard
   - **Fix:** Create `useDensityMode` hook + `DensityMode` context provider

**Alan Cooper Principle Violation:** *"Visual Interface Builder"* - Components should be composable building blocks. Current plans have some reusability but miss composition opportunities.

---

### Visual Design Evaluation (12/25)

**What's Working:**
- ✅ OKLCH color system chosen (perceptually uniform, better than HSL for dark mode)
- ✅ Tonal elevation mentioned in 17-CONTEXT (sufficient for dark mode)
- ✅ Color coding for status (Green/Yellow/Red) - semantically clear

**Critical Gaps:**
1. **Typography Scale Undefined** - No type scale, line-height, or weight specifications
   - 17-CONTEXT lists "Typography scale: defined and applied" as criterion but no plan defines it
   - **Missing:** Modular scale (e.g., 1.250 or 1.333), line-height ratios (1.5 for body, 1.2 for headings)
   - **Impact:** Inconsistent sizing across components, haphazard visual hierarchy
   - **Fix:** Add to 17-01 or create separate `typography.ts` config:
     ```typescript
     export const typeScale = {
       xs: '0.75rem',   // 12px - captions
       sm: '0.875rem',  // 14px - body small
       base: '1rem',    // 16px - body
       lg: '1.125rem',  // 18px - body large
       xl: '1.25rem',   // 20px - h5
       '2xl': '1.5rem', // 24px - h4
       // ... with line-heights
     }
     ```

2. **Color-Only Indicators Violate WCAG** - StatusBadge uses color alone
   - 17-03: "Color coding: Gray (idle), Green (running), Blue (completed), Red (failed)"
   - **Problem:** 8% of men are color-blind (red/green confusion)
   - **Luke Wroblewski Principle:** *"Never use color as the only visual means of conveying information"*
   - **Fix:** Add icons + patterns:
     - Idle: Gray circle icon
     - Running: Green circle + pulse animation (already planned) ✅
     - Completed: Blue checkmark icon
     - Failed: Red X icon + hatched pattern

3. **Animation Easing Undefined** - Transitions mentioned but no easing functions
   - 17-03: "Add CSS transitions for smooth mode switching (200ms)" - easing not specified
   - 17-04: "Animation smooth on value changes (200ms transition)" - easing not specified
   - **Dan Saffer Principle:** Microinteractions need personality and purpose
   - **Fix:** Define easing in global CSS:
     ```css
     :root {
       --ease-out: cubic-bezier(0.215, 0.61, 0.355, 1); /* Standard */
       --ease-in-out: cubic-bezier(0.645, 0.045, 0.355, 1); /* Bidirectional */
       --ease-spring: cubic-bezier(0.34, 1.56, 0.64, 1); /* Playful */
     }
     ```

---

### Accessibility Evaluation (18/25)

**What's Working:**
- ✅ Touch targets ≥ 44x44px (17-02, 17-06) - WCAG 2.5.5 compliant
- ✅ ARIA live regions for status changes (17-03, 17-04)
- ✅ `prefers-reduced-motion` respected (17-03 ping animation)
- ✅ WCAG 2.1 AA audit planned (17-06)
- ✅ Focus trap in CommandPalette dialog (17-05)

**Critical Gaps:**
1. **Focus States Not Defined** - No focus ring specifications
   - 17-CONTEXT lists "Focus states: visible everywhere?" as criterion but no plan defines them
   - **Impact:** Keyboard users can't see what's focused
   - **Fix:** Add to global CSS (17-01):
     ```css
     *:focus-visible {
       outline: 2px solid oklch(0.5 0.2 250); /* Brand color */
       outline-offset: 2px;
       border-radius: 4px;
     }
     ```

2. **Keyboard Alternatives Missing for Swipe Gestures** - Mobile-only interaction
   - 17-03: "Add swipe gesture to reveal brain actions" - no keyboard alternative
   - 17-06: "Swipe gestures work on mobile panels" - no desktop keyboard alternative
   - **WCAG 2.1.1:** All functionality must be operable via keyboard
   - **Fix:** Add visible "Actions" button that appears on focus/hover (or Tab key)
     - Desktop: Tab to brain card → Enter → actions menu appears
     - Mobile: Swipe left → actions appear

3. **Color Contrast Ratios Not Specified** - OKLCH system good but ratios undefined
   - 17-CONTEXT: "Color contrast: 4.5:1 for text?" - listed as question, not requirement
   - **WCAG 2.1 AA Requirement:** 4.5:1 for normal text, 3:1 for large text (18pt+)
   - **Fix:** Add contrast validation to 17-06 audit:
     ```typescript
     // Add to axe-core config
     const contrastRules = {
       'normal-text': 4.5,
       'large-text': 3.0,
       'ui-components': 3.0
     };
     ```

---

### Interaction Design Evaluation (17/25)

**What's Working:**
- ✅ Drag-and-drop visual feedback (17-02: "opacity, lift effect")
- ✅ Ping animation for active brains (17-03)
- ✅ Keyboard navigation for CommandPalette (17-05: Arrow keys, Enter, Escape)
- ✅ Pull-to-refresh gesture (17-06)

**Critical Gaps:**
1. **Swipe Gestures Not Discoverable** - No visual affordances
   - 17-03: "Add swipe gesture to reveal brain actions" - how do users KNOW?
   - 17-06: "Left swipe: Reveal actions (edit, delete, archive)" - complex, two-directional
   - **Luke Wroblewski Principle:** *"Gestures must be discoverable via visual or haptic cues"*
   - **Problem:** Users won't swipe if they don't know it's possible
   - **Fix:** Add visual hints:
     - On first load: Show subtle animation hint ("Swipe left for actions")
     - Add overflow hint: Three dots `...` on right edge of card
     - Long-press preview: Hold down → preview actions (teach gesture)

2. **Two-Directional Swipe Complexity** - Left/right swipes do different things
   - 17-06: "Left swipe: Reveal actions" + "Right swipe: Quick actions"
   - **Problem:** Users won't remember two directions
   - **Luke Wroblewski Principle:** *"Simplicity wins over cleverness"*
   - **Fix:** Single-direction swipe (left only) + action menu:
     - Swipe left: Action sheet appears (Edit, Delete, Archive, Duplicate, Favorite)
     - Long-press: Same action sheet (alternative for accessibility)

3. **Animation Purpose Undefined** - Some animations decorative, not functional
   - 17-03: Ping animation for running brains ✅ (functional - shows activity)
   - 17-04: "Add animation on value changes" - purpose unclear
   - **Dan Saffer Principle:** Microinteractions should have purpose (feedback, guidance, delight)
   - **Fix:** Audit all animations:
     - Ping: ✅ Feedback (brain is active)
     - Density mode transition: ✅ Feedback (view changed)
     - Cost value update: ❓ Add purpose - highlight changed value (yellow flash 500ms)

---

### Plan-by-Plan Analysis

#### Plan 17-02: Multi-tenant Company Switcher
**UI Score: 18/25**

**Strengths:**
- Drag-and-drop with visual feedback (opacity, lift effect) ✅
- Status indicators (green/yellow/red dots) - semantically clear
- Touch targets ≥ 44x44px ✅

**Must-Fix:**
1. **Drag handle affordance unclear** - "Add drag handle icon on hover" - what does the icon look like?
   - **Fix:** Use six-dot icon `⋮⋮` (standard pattern, e.g., Gmail, Notion)
   - **Add tooltip:** "Drag to reorder" on hover

2. **Status indicators use color only** - Green/Yellow/Red dots need icons
   - **Fix:** Add icons inside dots (checkmark, warning, X)
   - **Add patterns:** Hatched fill for error state

3. **Collapse button state undefined** - What does collapsed state look like?
   - **Fix:** Document collapsed state (icons only, 60px width)
   - **Add transition:** Smooth width animation (300ms ease-out)

---

#### Plan 17-03: ActiveAgentsPanel with Density Modes
**UI Score: 16/25**

**Strengths:**
- StatusBadge with ping animation ✅ (functional feedback)
- Density modes (compact/normal/detailed) - good progressive disclosure
- RAF batching for 60fps ✅ (performance critical)

**Must-Fix:**
1. **Ping animation needs easing** - "CSS keyframes" mentioned but easing undefined
   - **Fix:** Define ping animation with easing:
     ```css
     @keyframes ping {
       0% { transform: scale(1); opacity: 1; }
       100% { transform: scale(2); opacity: 0; }
     }
     .ping {
       animation: ping 1s cubic-bezier(0, 0, 0.2, 1) infinite;
     }
     ```

2. **Density mode transition timing** - "200ms" mentioned but easing not specified
   - **Fix:** Use `ease-out` for mode switch (feels faster):
     ```css
     .density-transition {
       transition: all 200ms cubic-bezier(0.215, 0.61, 0.355, 1);
     }
     ```

3. **Status badge color-only** - Gray/Green/Blue/Red needs icons
   - **Fix:** Add icons (see Visual Design section)

---

#### Plan 17-04: Cost Dashboard with MetricCard + QuotaBar
**UI Score: 17/25**

**Strengths:**
- QuotaBar color coding (Green/Yellow/Red) - semantically clear
- ARIA live regions for budget warnings ✅
- Trend indicator (↑↓) - good addition

**Must-Fix:**
1. **QuotaBar animation easing undefined** - "200ms transition" needs easing
   - **Fix:** Use `ease-in-out` for value changes (feels smooth, not abrupt):
     ```css
     .quota-bar {
       transition: width 200ms cubic-bezier(0.645, 0.045, 0.355, 1);
     }
     ```

2. **Trend indicator color coding unclear** - "↑ green for decreased cost, ↓ red for increased"
   - **Problem:** Counterintuitive - usually ↑ = good (up), ↓ = bad (down)
   - **Luke Wroblewski Principle:** *"Match mental models, don't invert them"*
   - **Fix:** Use arrows to indicate cost direction (↑ = increased, ↓ = decreased):
     - ↓ Green = Cost decreased (good)
     - ↑ Red = Cost increased (bad)

3. **MetricCard density mode** - "Compact = 1 line, Normal = 3 lines" - what about detailed?
   - **Fix:** Define detailed mode (5 lines: tokens + duration + cost + trend + budget %)

---

#### Plan 17-05: Command Palette with Global Search
**UI Score: 20/25**

**Strengths:**
- Keyboard navigation (Arrow keys, Enter, Escape) ✅
- Focus trap in dialog ✅
- Fuzzy search with highlighting ✅
- Category grouping with icons ✅

**Must-Fix:**
1. **Dialog backdrop blur undefined** - "Overlay dialog" but backdrop style unclear
   - **Fix:** Specify backdrop:
     ```css
     .backdrop {
       background: oklch(0 0 0 / 0.5); /* 50% black */
       backdrop-filter: blur(4px); /* Subtle blur */
     }
     ```

2. **Selected item highlight undefined** - How do users know which item is selected?
   - **Fix:** Add clear visual indicator:
     ```css
     .selected-item {
       background: oklch(0.5 0.2 250 / 0.1); /* Brand color 10% */
       border-left: 2px solid oklch(0.5 0.2 250); /* Accent */
     }
     ```

3. **Command list virtualization threshold** - "If > 100 items, use react-window"
   - **Problem:** 50 commands planned (4 screens + 24 brains + actions + settings)
   - **Fix:** Set threshold to 75 items (safer margin):
     ```typescript
     const USE_VIRTUALIZATION_THRESHOLD = 75;
     ```

---

#### Plan 17-06: Onboarding Wizard + Mobile Polish
**UI Score: 15/25**

**Strengths:**
- WCAG 2.1 AA audit comprehensive ✅
- Touch targets ≥ 44x44px ✅
- Progress indicator (step 1 of 4) ✅

**Must-Fix:**
1. **Swipe gestures not discoverable** - See Interaction Design section
   - **Fix:** Add onboarding hint for swipe gestures
   - **Add overflow hint:** Three dots on card edges

2. **Two-directional swipe too complex** - Left/right swipes confusing
   - **Fix:** Single-direction swipe + action menu (see Interaction Design)

3. **Progress indicator visual unclear** - "step 1 of 4" - where is it positioned?
   - **Fix:** Define progress indicator layout:
     ```tsx
     <div class="progress-indicator">
       <div class="dots">
         <div class="dot active" /> <!-- Step 1 -->
         <div class="dot" />       <!-- Step 2 -->
         <div class="dot" />       <!-- Step 3 -->
         <div class="dot" />       <!-- Step 4 -->
       </div>
       <span class="label">Step 1 of 4</span>
     </div>
     ```

4. **Onboarding illustrations undefined** - "illustrations per step" - what style?
   - **Fix:** Define illustration style (line art, flat, 3D?)
   - **Recommendation:** Use simple line art (matches shadcn/ui minimal aesthetic)

---

### Cross-Plan Concerns

#### 1. Inconsistent Animation Easing
**Impact:** 3/5 plans
**Problem:** Transitions mentioned (200ms) but easing functions undefined
**Fix:** Add global easing variables to 17-01 (see Visual Design section)

#### 2. Color-Only Indicators
**Impact:** 2/5 plans (17-03, 17-04)
**Problem:** StatusBadge, QuotaBar use color alone
**Fix:** Add icons + patterns (see Visual Design section)

#### 3. Typography Scale Missing
**Impact:** 5/5 plans (all use text but no scale defined)
**Problem:** Inconsistent sizing, line-height, weights
**Fix:** Add type scale to 17-01 (see Visual Design section)

#### 4. Gesture Discoverability
**Impact:** 2/5 plans (17-03, 17-06)
**Problem:** Swipe gestures have no visual affordances
**Fix:** Add hints + overflow indicators (see Interaction Design section)

---

### Must-Fix Changes (Before Execution)

#### Plan 17-01: Three-Column Layout Foundation
1. **Add global easing variables** to CSS (see Visual Design section)
2. **Add typography scale** to `typography.ts` (see Visual Design section)
3. **Add focus ring styles** to global CSS (see Accessibility section)

#### Plan 17-02: Multi-tenant Company Switcher
1. **Specify drag handle icon** - Use six-dot `⋮⋮` with tooltip
2. **Add icons to status indicators** - Checkmark, warning, X inside dots
3. **Document collapsed state** - Icons only, 60px width, smooth transition

#### Plan 17-03: ActiveAgentsPanel
1. **Define ping animation easing** - `cubic-bezier(0, 0, 0.2, 1)`
2. **Add icons to status badges** - Not color alone (see Visual Design)
3. **Specify density mode transition** - `ease-out` 200ms

#### Plan 17-04: Cost Dashboard
1. **Fix trend indicator mental model** - ↑ = increased, ↓ = decreased
2. **Define QuotaBar easing** - `ease-in-out` 200ms
3. **Add MetricCard detailed mode** - 5 lines (not just 1/3)

#### Plan 17-05: Command Palette
1. **Specify backdrop blur** - `blur(4px)` + 50% black
2. **Define selected item highlight** - Accent border + tinted background
3. **Lower virtualization threshold** - 75 items (not 100)

#### Plan 17-06: Onboarding + Mobile
1. **Simplify swipe gestures** - Single-direction + action menu
2. **Add swipe gesture hints** - Overflow dots + first-load animation
3. **Define progress indicator** - Dot-based + label
4. **Specify illustration style** - Line art (matches shadcn/ui)

---

### Risks Identified

#### High Risk
1. **Color-only indicators** - WCAG violation, 8% of users affected
2. **Gesture discoverability** - Users won't use features they don't know exist
3. **Typography inconsistency** - No scale = haphazard visual hierarchy

#### Medium Risk
1. **Animation easing undefined** - Jerky transitions hurt perceived performance
2. **Focus states invisible** - Keyboard users can't navigate
3. **Two-directional swipe** - Too complex, users won't remember

#### Low Risk
1. **Drag handle affordance** - Minor, can add tooltip
2. **Virtualization threshold** - Unlikely to hit 100 commands in MVP

---

### Recommendations

#### Immediate Actions (Before Execution)
1. **Add typography scale to 17-01** - Type scale, line-heights, weights
2. **Add global easing variables** - `ease-out`, `ease-in-out`, `ease-spring`
3. **Add focus ring styles** - Visible focus indicators
4. **Fix color-only indicators** - Add icons to all status badges
5. **Simplify swipe gestures** - Single-direction + action menu
6. **Add gesture affordances** - Overflow dots + hints

#### Future Improvements (Post-MVP)
1. **Create generic Card component** - Reusable across BrainCard, MetricCard
2. **Create useDensityMode hook** - Generic density mode pattern
3. **Add animation library** - Framer Motion for complex transitions
4. **Conduct usability testing** - Validate gesture discoverability
5. **Add haptic feedback** - Vibrate on swipe completion (mobile)

---

### Brain #3 Final Score: 62/100

**Breakdown:**
- Component Architecture: 15/25 (partial Atomic Design, missing composition)
- Visual Design: 12/25 (OKLCH good, but missing typography, color-only issues)
- Accessibility: 18/25 (good intent, missing focus states, keyboard alternatives)
- Interaction Design: 17/25 (gestures not discoverable, easing undefined)

**Verdict:** Plans have solid foundation but need critical UI design fixes before execution. Add typography scale, fix color-only indicators, define easing functions, and add gesture affordances.

---

**Brain #3 (UI Design) consultation complete.**
**Output appended:** 2026-04-09

---

## Brain #1 (Product Strategy) Output — RETRY

### Score: 78/100

### Key Findings

**1. Strong User Value Stack**
- Plan 17-02 (Multi-tenant switcher) directly addresses enterprise need for company context switching
- Plan 17-03 (ActiveAgentsPanel) provides critical operational visibility for agent orchestration
- Plan 17-04 (Cost Dashboard) addresses real budget concerns in AI operations

**2. Prioritization Mostly Sound**
- 17-01 → 17-02 → 17-03 is correct order (layout → multi-tenant → monitoring)
- Cost Dashboard (17-04) should come BEFORE Command Palette (17-05) — budget visibility is more critical than convenience
- Onboarding (17-06) is correctly placed last — polish after core functionality

**3. Missing Time-to-Value Strategy**
- Plans lack incremental delivery milestones
- No "minimum viable" version defined per plan
- Can't ship partial value until ALL 5 plans complete

**4. Weak Validation Strategy**
- No user research planned before building
- No A/B testing mentioned for UX patterns
- Assumption that Paperclip patterns transfer 1:1 to MasterMind

**5. Enterprise Requirements Gap**
- Plan 17-02 mentions tenant isolation but no compliance/audit trail
- No RBAC (role-based access control) considerations
- Missing SSO/SLO integration for enterprise

### Must-Fix Changes

1. **Plan 17-02 (Multi-tenant):** Add enterprise auth requirements
   - Missing: SSO integration (SAML/OIDC)
   - Missing: RBAC per tenant (admin/member/viewer roles)
   - Missing: Audit trail for tenant switching
   - **Fix:** Add Task 5: "Implement Enterprise Auth Integration" with SSO, RBAC, audit logging

2. **Plan 17-03 (ActiveAgentsPanel):** Define user value metrics
   - Missing: What problem does this solve? (Agent monitoring → faster debugging?)
   - Missing: Success metrics (Time to detect failed agent? Reduction in alert fatigue?)
   - **Fix:** Add "User Value" section with problem statement, success metrics, measurable outcomes

3. **Plan 17-04 (Cost Dashboard):** Reorder before 17-05
   - Cost visibility is MORE critical than command palette convenience
   - Budget enforcement prevents runaway costs — higher business impact
   - **Fix:** Swap order: 17-04 → 17-05 (Cost Dashboard before Command Palette)

4. **All Plans:** Add incremental delivery milestones
   - Current: All-or-nothing delivery (can't ship until all 5 plans complete)
   - Missing: "Minimum Viable" definition per plan
   - **Fix:** Add "MVP Definition" section to each plan:
     - What's the minimum useful version?
     - What can be deferred to v2?
     - What's the 80/20 cutoff?

5. **Plan 17-06 (Onboarding):** Add validation strategy
   - No user research planned before building onboarding flow
   - No usability testing mentioned
   - **Fix:** Add Task 1: "User Research for Onboarding" — interview 5 enterprise users, validate assumptions

### Risks Identified

**High Risk**
1. **Paperclip pattern transfer assumption** — No validation that these patterns work for MasterMind users
2. **All-or-nothing delivery** — 5-month delay before any user value ships
3. **Missing enterprise requirements** — SSO, RBAC, audit trails critical for enterprise but not planned

**Medium Risk**
1. **Cost dashboard reordering** — Building convenience (17-05) before critical (17-04)
2. **No A/B testing strategy** — Launching UX patterns without validation
3. **Mobile complexity** — Swipe gestures (17-06) are high-risk without user testing

**Low Risk**
1. **Command palette scope creep** — 17-05 has 8 tasks, could be simplified
2. **Onboarding polish first** — 17-06 should be lower priority than core functionality

### Recommendations

**Immediate Actions (Before Execution)**
1. **Reorder plans:** 17-01 → 17-02 → 17-03 → 17-04 → 17-05 → 17-06 (Cost Dashboard before Command Palette)
2. **Add MVP definitions:** Define "minimum viable" version for each plan
3. **Add user research:** Interview 5 enterprise users before building onboarding (17-06)
4. **Add enterprise auth:** SSO, RBAC, audit trails to Plan 17-02
5. **Define success metrics:** Add measurable outcomes to each plan (e.g., "Time to detect failed agent < 5s")

**Strategic Pivots**
1. **Consider phased rollout:** Ship 17-01 + 17-02 as "MVP v1", then 17-03 + 17-04 as "MVP v2"
2. **Validate Paperclip patterns:** Run usability test on wireframes before building
3. **Simplify 17-05:** Command palette has 8 tasks — cut to 5 core tasks for MVP

**Post-MVP Improvements**
1. **Add analytics:** Track feature usage (e.g., How often is company switcher used? How many agents monitored?)
2. **A/B testing:** Test swipe gestures vs. button navigation on mobile
3. **Enterprise hardening:** Add SSO, RBAC, compliance features

---

**Brain #1 (Product Strategy) consultation complete.**
**Output appended:** 2026-04-09


---

## Brain #4 (Frontend) Output — RETRY

### Score: 72/100

### Key Findings

**1. State Management — Well Designed**
- 3 Zustand stores (company, brain, ui) are sufficient for this scope
- Immer middleware prevents accidental mutations
- localStorage sync via `storage` event is correct pattern
- **Good:** No prop drilling concerns — stores provide global access

**2. Performance — Critical Gaps**
- RAF batching mentioned in 17-03 but NOT implemented in task list
- 24-brain burst scenario: No React.memo optimization plan
- React Flow re-renders: No memo strategy for node data updates
- **Missing:** Performance budgets (Target: 60fps @ 24 brains, 100ms time-to-interactive)

**3. WebSocket Integration — Scalability Concerns**
- Single `wsDispatcher` singleton: Good pattern
- **Missing:** Connection pooling strategy (How many WS connections max?)
- **Missing:** Reconnection logic (What happens on network failure?)
- **Missing:** Backpressure handling (24 brains streaming = can UI keep up?)

**4. React Flow Integration — Partially Correct**
- Data prop only: Correct approach (let React Flow handle position)
- **Missing:** Position calculation strategy (Who owns it? React Flow or custom?)
- **Missing:** Node memoization (24 nodes @ 60fps = need React.memo)
- **Risk:** Cascade re-renders if brain data updates trigger parent re-renders

### Must-Fix Changes

1. **Plan 17-03 (ActiveAgentsPanel):** Add performance optimization tasks
   - **Missing:** RAF batching implementation details
   - **Missing:** React.memo for BrainCard components (24 brains = re-render risk)
   - **Missing:** Virtualization (if > 50 brains, need react-window)
   - **Fix:** Add Task 5: "Implement Performance Optimizations"
     - Subtask 5.1: Wrap BrainCard in React.memo with custom comparison
     - Subtask 5.2: Implement RAF batching in wsDispatcher (max 1 update per frame)
     - Subtask 5.3: Add virtualization if brain count > 50 (use react-window)
     - Subtask 5.4: Performance budget: 60fps @ 24-brain burst, measure with Chrome DevTools

2. **Plan 17-04 (Cost Dashboard):** Fix React Flow integration
   - **Problem:** "Data prop only" mentioned but no memoization strategy
   - **Missing:** React Flow node memoization (24 nodes with cost data = re-render cascade)
   - **Missing:** Position calculation ownership (React Flow dagre vs. custom?)
   - **Fix:** Add Task 6: "Optimize React Flow Performance"
     - Subtask 6.1: Wrap React Flow nodes in React.memo (compare by brainId + status)
     - Subtask 6.2: Use React Flow's `useNodesState` hook (let React Flow handle position)
     - Subtask 6.3: Debounce cost data updates (max 1 update per 500ms)
     - Subtask 6.4: Measure: 60fps @ 24 nodes with cost data streaming

3. **Plan 17-02 (Multi-tenant):** Add WebSocket error handling
   - **Missing:** What happens when WS connection drops during company switch?
   - **Missing:** Reconnection logic (exponential backoff?)
   - **Missing:** Queued actions during offline (sync when reconnect?)
   - **Fix:** Add Task 6: "Implement WebSocket Error Handling"
     - Subtask 6.1: Add WS connection status indicator (green/red dot in CompanyRail)
     - Subtask 6.2: Implement exponential backoff reconnection (1s, 2s, 4s, 8s, 15s max)
     - Subtask 6.3: Queue actions during offline (replay when reconnect)
     - Subtask 6.4: Show toast notification on WS failure

4. **All Plans:** Add performance budgets
   - **Missing:** No performance targets defined
   - **Risk:** Build features without measuring if they're fast enough
   - **Fix:** Add "Performance Budget" section to each plan:
     - Target: 60fps @ 24-brain burst (Plan 17-03)
     - Target: 100ms time-to-interactive (Plan 17-02)
     - Target: < 50ms React Flow node update (Plan 17-04)
     - Target: < 16ms command palette render (Plan 17-05)

5. **Plan 17-05 (Command Palette):** Add virtualization
   - **Problem:** "75 items threshold" mentioned but no virtualization
   - **Risk:** If user has 100 commands, render all = laggy input
   - **Fix:** Add Task 7: "Implement Command Virtualization"
     - Use `react-virtual` or `react-window` for command list
     - Render only visible commands + 5 buffer above/below
     - Measure: < 16ms render time @ 100 commands

### Risks Identified

**High Risk**
1. **No React.memo strategy** — 24 brains + 24 React Flow nodes = cascade re-render risk
2. **Missing RAF batching** — WebSocket updates can flood main thread, drop frames
3. **No performance budgets** — Building features without measuring if they're fast enough

**Medium Risk**
1. **WebSocket error handling** — No reconnection logic, offline UX undefined
2. **React Flow position calculation** — Ambiguous who owns it (React Flow vs. custom)
3. **Command palette virtualization** — 75 items threshold may be too high for 60fps

**Low Risk**
1. **Zustand store structure** — 3 stores are sufficient, no prop drilling risk
2. **localStorage sync** — `storage` event pattern is correct
3. **@dnd-kit performance** — Drag-and-drop library is well-optimized

### Recommendations

**Immediate Actions (Before Execution)**
1. **Add performance optimization tasks** to Plan 17-03 (RAF batching, React.memo, virtualization)
2. **Add WebSocket error handling** to Plan 17-02 (reconnection, queuing, status indicator)
3. **Fix React Flow memoization** in Plan 17-04 (wrap nodes in React.memo, use useNodesState)
4. **Add performance budgets** to all plans (60fps targets, measure with Chrome DevTools)
5. **Add command palette virtualization** to Plan 17-05 (react-virtual, < 16ms render)

**Strategic Pivots**
1. **Create performance testing suite:** Add Lighthouse CI to PR pipeline (catch perf regressions)
2. **Implement RAF batching globally:** Not just for ActiveAgentsPanel, but all WS updates
3. **Add performance monitoring:** Track Core Web Vitals (LCP, FID, CLS) in production

**Post-MVP Improvements**
1. **React Server Components:** Consider migrating to RSC for reduced JS bundle
2. **Suspense boundaries:** Add loading states for better perceived performance
3. **Code splitting:** Lazy load Command Palette, Onboarding (not critical path)

---

### Brain #4 Final Score: 72/100

**Breakdown:**
- State Management: 20/25 (Zustand stores well-designed, localStorage sync correct)
- Performance: 12/25 (critical gaps: no RAF batching, no React.memo, no budgets)
- WebSocket Integration: 15/25 (good singleton pattern, but missing error handling)
- React Flow Integration: 15/25 (data prop correct, but missing memoization strategy)
- Testing Strategy: 10/25 (no performance testing mentioned)

**Verdict:** Plans have solid foundation but CRITICAL performance optimizations missing. Add RAF batching, React.memo, virtualization, and performance budgets before execution. Risk of frame drops and cascade re-renders is HIGH without these fixes.

---

**Brain #4 (Frontend) consultation complete.**
**Output appended:** 2026-04-09
