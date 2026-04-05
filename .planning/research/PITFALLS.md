# Domain Pitfalls

**Domain:** Enterprise Agent Orchestration Platform with Knowledge Distillation (v3.0)
**Researched:** 2026-04-06
**Context:** SUBSEQUENT MILESTONE — Adding Rust + gRPC + PostgreSQL + Multi-channel to existing Python/TypeScript monorepo

---

## Critical Pitfalls

Mistakes that cause rewrites, major issues, or complete failure of the v3.0 milestone.

### Pitfall 1: Big Bang Rewrite — Sunk Cost Fallacy

**What goes wrong:** Attempting to rebuild the entire system in Rust/PostgreSQL before validating value. The "we'll migrate everything" mindset creates a 6-month+ black hole with no shipping, no customer feedback, and mounting technical debt in both old and new systems.

**Why it happens:**
- Excitement about new technology (Rust performance, PostgreSQL features)
- Desire to "fix everything" at once
- Underestimation of integration complexity
- False belief that "doing it right" means rewriting from scratch

**Consequences:**
- Zero shipping for months while competitors ship features
- Team burnout from "perfectionism paralysis"
- Old system atrophies (security updates, bug fixes stop)
- New system accumulates its own technical debt before launch
- Deadline pressure → cut corners → production incidents
- **Project abandonment** (see: Netscape rewrote from scratch, took 4 years, lost market share to IE)

**Prevention:**

1. **Strangler Fig Pattern** — Migrate incrementally, NOT Big Bang
   - Phase 0: Fork UI only (no backend changes)
   - Phase 1: Vertical slice — 1 API path end-to-end through Rust → gRPC → Python
   - Validate 3-service architecture BEFORE committing to full migration
   - Each phase MUST ship value, not just infrastructure

2. **Escape Hatch Activated** — If Rust velocity < 0.5x Python after Phase 1:
   - Rust ONLY for WebSocket Hub + Adapter Registry (performance-critical only)
   - Python remains for ALL business logic, auth, database access
   - Accept that "perfect stack" is enemy of "shipped product"

3. **No Parallel Development** — Don't build "v2" alongside "v1"
   - Each component is migrated once, replaced in-place
   - Feature flags to route traffic: old implementation vs new implementation
   - Kill switch: revert to old system if new system fails

4. **Weekly Value Delivery** — Every phase MUST deliver user-facing value
   - Phase 0: New UI (visible improvement)
   - Phase 1: Faster API response (performance win)
   - Phase 2: Real-time canvas (new capability)
   - If a phase is 100% infrastructure → restructure

**Detection:**
- Milestone timeline extends beyond 4 months without shipping
- "We're almost done" for 8+ weeks
- Growing list of "blockers" preventing any deployment
- Team morale dropping, "this is taking forever" sentiment

**Phase to Address:** Phase 0 (Fork UI) — Set strangler fig pattern before writing any Rust code

---

### Pitfall 2: Type Synchronization Drift — gRPC Contract Nightmares

**What goes wrong:** Protobuf definitions diverge from actual Rust/Python/TypeScript implementations. "It compiles on my machine" becomes epidemic. Field renames in Rust but not Python. Optional fields added to TypeScript but not Protobuf. Silent data corruption follows.

**Why it happens:**
- Manual updates to `.proto` files without regenerating all 3 languages
- "Quick hack" in one language, "I'll update the proto later"
- No CI gate preventing compilation if proto is out of sync
- Multiple developers working on different services independently

**Consequences:**
- Runtime crashes: Python expects `user_id` (string), Rust sends `userId` (i32)
- Silent data loss: Optional fields dropped because type mismatch
- Debugging hell: Error in Rust service → Python gRPC client → TypeScript frontend — where's the bug?
- Deploy failures: Production Rust service has proto v1.2, Python has v1.3 → connection refused

**Prevention:**

1. **Single Source of Truth**
   ```bash
   # Directory structure (ENFORCE)
   proto/
   ├── common/
   │   ├── auth.proto          # Auth messages shared by all services
   │   ├── brain_agent.proto   # Brain agent execution contracts
   │   └── events.proto        # WebSocket event types
   └── build.sh                # Regenerates all 3 languages
   ```

2. **Generated Code is Read-Only**
   - `proto/gen/rust/` — **NEVER EDIT** (tonic + prost generated)
   - `proto/gen/python/` — **NEVER EDIT** (betterproto generated)
   - `proto/gen/typescript/` — **NEVER EDIT** (protoc-gen-es generated)
   - Git pre-commit hook: reject modifications to `gen/` directories

3. **CI Gate — Proto Sync Check**
   ```yaml
   # .github/workflows/proto-sync.yml
   - name: Regenerate proto
     run: proto/build.sh --check-only
   # If generated code differs from committed → FAIL
   # Forces: update proto → regenerate → commit all together
   ```

4. **Field Naming Convention — Protobuf Style Guide**
   - Use `snake_case` for field names in `.proto` (not camelCase)
   - Rust mapping: `snake_case` → `snake_case` (no conversion)
   - Python mapping: `snake_case` → `snake_case` (no conversion)
   - TypeScript mapping: `snake_case` → `snake_case` (enforce via lint rule)
   - **WHY:** Avoids "userId" vs "user_id" confusion across languages

5. **Versioned Protobuf Contracts**
   ```
   v1/auth.proto (STABLE) — Never change breaking
   v2/auth.proto (DRAFT) — Iterate here
   ```
   - Once deployed to production → v1 is frozen forever
   - Breaking changes → create v2, support both during migration
   - Deprecate v1 after all services updated

**Detection:**
- Manual protobuf editing in one language without regenerating others
- "Works locally but fails in CI" (proto out of sync)
- Runtime gRPC errors: "field not found", "type mismatch"
- Deploy script includes "skip proto check" flag

**Phase to Address:** Phase 1 (Foundation Upgrade) — BEFORE writing first gRPC service, set up proto sync CI gate

---

### Pitfall 3: SQLite → PostgreSQL Migration — Data Loss & Query Failures

**What goes wrong:** Schema migration succeeds but queries fail in production. SQLite permissiveness masks SQL errors that PostgreSQL rejects. Silent data truncation, case sensitivity issues, and transaction differences cause corruption.

**Why it happens:**
- SQLite is **permissive** (allows implicit type conversions, flexible column types)
- PostgreSQL is **strict** (type-safe, no implicit conversions)
- No testing against PostgreSQL until production migration
- Assumption: "SQL is SQL" — false, dialect differences are massive

**Consequences:**
- **Data Loss:** SQLite allows `INSERT "text" INTO INTEGER column` (truncates to 0), PostgreSQL rejects → migration halts
- **Query Failures:** SQLite `LIKE` is case-insensitive by default, PostgreSQL is case-sensitive → search returns 0 results
- **Transaction Isolation:** SQLite allows `SELECT` inside transaction before `COMMIT`, PostgreSQL with `READ COMMITTED` sees different data → race conditions
- **Performance Collapse:** SQLite `SELECT * FROM brain_records WHERE brain_id = 1` uses index (fast), PostgreSQL same query does sequential scan (slow) → missing `ANALYZE`

**Prevention:**

1. **Test Against PostgreSQL in Development — NEVER SQLite**
   ```bash
   # .env.development
   DATABASE_URL=postgresql://localhost:5432/mastermind_dev
   # NOT sqlite:///./mastermind.db
   ```
   - From Phase 1 Day 1, ALL dev environments use PostgreSQL
   - SQLite only for local scripts (NOT application logic)
   - Docker Compose: PostgreSQL service always running

2. **SQLAlchemy Alembic Migrations — Hand-Rolled SQL is Forbidden**
   ```python
   # migration/001_initial_schema.py
   def upgrade():
       # ✅ SAFE — Alembic generates dialect-specific SQL
       op.create_table(
           'brain_records',
           sa.Column('id', sa.Integer(), primary_key=True),
           sa.Column('brain_id', sa.Integer(), sa.ForeignKey('brains.id'), nullable=False),
           sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()')),
       )
   ```

   ```python
   # ❌ UNSAFE — Raw SQL assumes SQLite behavior
   def upgrade():
       op.execute("CREATE TABLE brain_records (id INTEGER PRIMARY KEY, brain_id INTEGER)")
   ```

3. **Type Mapping Audit — SQLite vs PostgreSQL**
   | SQLite | PostgreSQL | Migration Issue |
   |--------|-----------|-----------------|
   | `INTEGER` | `INTEGER` | ✅ Safe |
   | `TEXT` | `VARCHAR` or `TEXT` | ✅ Safe if `TEXT` |
   | `BOOLEAN` | `BOOLEAN` | ⚠️ SQLite stores `0`/`1`, PostgreSQL requires `TRUE`/`FALSE` |
   | `DATETIME` | `TIMESTAMPTZ` | ⚠️ SQLite no timezone, PostgreSQL requires timezone-aware |
   | `JSON` | `JSONB` | ✅ Safe if using SQLAlchemy's `JSONB` type |

4. **Case Insensitivity — PostgreSQL `CITEXT` Extension**
   ```sql
   -- SQLite: LIKE is case-insensitive by default
   SELECT * FROM brains WHERE name LIKE '%product%';

   -- PostgreSQL: LIKE is case-sensitive, use CITEXT
   CREATE EXTENSION citext;
   CREATE TABLE brains (name CITEXT); -- Case-insensitive text
   SELECT * FROM brains WHERE name LIKE '%product%';
   ```

5. **Migration Dry-Run — Production Test on Copy**
   ```bash
   # 1. Dump production SQLite
   sqlite3 mastermind.db .dump > prod_dump.sql

   # 2. Load into PostgreSQL staging
   psql staging_mastermind < prod_dump.sql

   # 3. Run Alembic migrations on staging
   alembic upgrade head --sql

   # 4. Verify data integrity
   python scripts/verify_migration.py --source sqlite --target postgres
   ```

**Detection:**
- Migration test suite passes on SQLite but fails on PostgreSQL
- "Works in dev, breaks in prod" (dev uses SQLite, prod uses PostgreSQL)
- Alembic migration includes `op.execute()` with raw SQL
- `SELECT` queries return 0 results after migration (case sensitivity issue)

**Phase to Address:** Phase 1 (Foundation Upgrade) — Set up PostgreSQL in dev from day 1, write migration tests

---

### Pitfall 4: Multi-Channel Webhook Reliability — Silent Message Loss

**What goes wrong:** WhatsApp/Instagram/Email webhooks arrive but are silently dropped. No retry, no dead letter queue, no monitoring. Customers report "we sent messages but got no response" — support nightmare.

**Why it happens:**
- Webhook handlers return 200 OK but crash during processing (async task fails)
- No persistent queue — in-memory messages lost on restart
- Rate limiting from Meta/WhatsApp → webhook rejected, no retry
- "We'll add monitoring later" → never happens

**Consequences:**
- **Silent Data Loss:** 1000s of webhooks processed successfully but never stored
- **Customer Churn:** "Your platform doesn't work" (it works, but messages lost)
- **Compliance Risk:** GDPR — lost customer data in webhooks
- **Debugging Hell:** "Can you resend that webhook?" (Meta doesn't keep logs beyond 24h)

**Prevention:**

1. **Webhook Handler = Write-First, Process-Later**
   ```rust
   // Axum webhook handler (Rust)
   async fn whatsapp_webhook(
       State(pool): State<PgPool>,
       Json(payload): Json<WebhookPayload>,
   ) -> Result<StatusCode, Error> {
       // ✅ Step 1: Persist IMMEDIATELY
       pool.execute("INSERT INTO webhook_queue (payload, created_at) VALUES ($1, NOW())", &[&payload]).await?;

       // ✅ Step 2: Return 200 OK (Meta happy)
       Ok(StatusCode::OK)
   }

   // Background worker processes queue
   async fn process_webhooks(pool: PgPool) {
       loop {
           let webhook = pool.fetch_one("SELECT * FROM webhook_queue WHERE processed = false ORDER BY created_at LIMIT 1").await?;
           process_webhook(webhook).await?;
           pool.execute("UPDATE webhook_queue SET processed = true WHERE id = $1", &[webhook.id]).await?;
       }
   }
   ```

2. **Dead Letter Queue — Failed Webhooks**
   ```sql
   CREATE TABLE webhook_dlq (
       id SERIAL PRIMARY KEY,
       payload JSONB NOT NULL,
       error_message TEXT,
       retry_count INT DEFAULT 0,
       last_retry_at TIMESTAMPTZ,
       created_at TIMESTAMPTZ DEFAULT NOW()
   );

   -- Retry strategy: exponential backoff
   -- retry 1: 1 min delay
   -- retry 2: 5 min delay
   -- retry 3: 30 min delay
   -- retry 4+: human investigation
   ```

3. **Idempotency — Deduplicate Webhooks**
   ```rust
   // Meta may retry webhooks (if response timeout)
   // Use webhook_id as unique constraint
   INSERT INTO webhook_queue (webhook_id, payload, created_at)
   VALUES ($1, $2, NOW())
   ON CONFLICT (webhook_id) DO NOTHING; -- Ignore duplicate
   ```

4. **Monitoring — Webhook Health Dashboard**
   - Metrics: `webhooks_received_total`, `webhooks_processed_total`, `webhooks_failed_total`
   - Alert: If `webhooks_failed_total > 100` in 5 minutes → page on-call
   - Grafana dashboard: Queue depth, processing lag, error rate by channel

5. **Testing Without Sandbox — Mock Webhook Server**
   ```bash
   # Dev environment: ngrok tunnel to local Rust service
   ngrok http 3000

   # Meta sandbox sends to https://abc123.ngrok.io/webhook/whatsapp
   # Local Axum receives webhook, writes to dev PostgreSQL
   ```

**Detection:**
- Webhook handler has async processing in the same function as HTTP response
- No `webhook_queue` table (or equivalent persistence)
- Production incident: "webhooks stopped working but no errors in logs"
- Meta developer dashboard shows "Webhook delivery failed" with 500 errors

**Phase to Address:** Phase 3 (Multi-Channel Gateway) — BEFORE connecting to real WhatsApp API, build webhook queue + DLQ

---

### Pitfall 5: Vite → Next.js Rebuild — Architecture Mismatch

**What goes wrong:** Attempting to "migrate" Paperclip's Vite frontend to Next.js App Router by copying components. Runtime failures pile up: `useEffect` runs on server, `window` is undefined, routing doesn't work. "Fork" becomes a 3-month rewrite from scratch.

**Why it happens:**
- **Vite** = Client-side only, `useEffect` runs in browser, `window` always available
- **Next.js App Router** = Server Components by default, no `window`, no `useEffect`
- Paperclip uses **Vite + React Router** — incompatible with Next.js App Router
- Assumption: "It's all React, how different can it be?" — VERY different

**Consequences:**
- **Component Rewrites Required:** 90% of Paperclip components need changes for Next.js
- **SSR Incompatibility:** Components using `window`, `localStorage`, `useEffect` break on server
- **Routing Mismatch:** React Router `<Route>` vs Next.js `file-system` routing — completely different
- **State Management:** Vite uses pure client-side state, Next.js requires Server Component + Client Component split
- **3-Month Delay:** What was promised as "2-week fork" becomes "3-month rebuild"

**Prevention:**

1. **Accept Reality — NOT a Fork, a Pattern Extraction**
   - DO NOT copy Paperclip code directly — it won't work in Next.js App Router
   - Extract UX patterns (not code): three-column layout, active agents panel, cost dashboard
   - Rebuild components using Next.js patterns: Server Components for data, Client Components for interactivity

2. **Component Architecture — Server vs Client Split**
   ```tsx
   // ✅ Server Component (default) — data fetching, NO interactivity
   // apps/web/app/dashboard/page.tsx
   export default async function DashboardPage() {
       const agents = await fetchAgents(); // Server-side fetch
       return <AgentList agents={agents} />; // Pass to Client Component
   }

   // ✅ Client Component — interactivity, NO data fetching
   // apps/web/src/components/AgentList.tsx
   'use client';
   export function AgentList({ agents }: { agents: Agent[] }) {
       const [selected, setSelected] = useState(null);
       return <div onClick={() => setSelected(...)}>...</div>;
   }
   ```

3. **Pattern Library — Paperclip UX, Next.js Implementation**
   | Paperclip Pattern | Next.js Implementation |
   |-------------------|------------------------|
   | Three-column layout (Vite) | Server Component with async data fetch |
   | Active Agents Panel (WebSocket) | Client Component with Zustand store |
   | Agent Config Form (useState) | Server Action (form POST) |
   | Cost Dashboard (useEffect) | Server Component + React Query for refresh |

4. **Incremental Migration — One Screen at a Time**
   - Week 1: Dashboard screen (Server Component, no WebSocket yet)
   - Week 2: Command Center screen (Client Component for interactivity)
   - Week 3: WebSocket integration (Zustand store, React Flow canvas)
   - Week 4: Multi-channel inbox (Server Actions for form submission)

5. **Testing Strategy — E2E Tests Guide Migration**
   ```typescript
   // Playwright test defines expected UX behavior
   test('dashboard shows active agents', async ({ page }) => {
       await page.goto('/dashboard');
       await expect(page.locator('.agent-tile')).toHaveCount(7);
   });

   // Implementation details (Vite vs Next.js) don't matter
   // Focus on UX outcome, not code similarity
   ```

**Detection:**
- "We'll just copy the Vite components" → IMMEDIATE red flag
- Next.js build error: `window is not defined` → component not marked `'use client'`
- `useEffect` runs in Server Component → wrong architecture
- Git history shows `cp -r paperclip/ui/src apps/web/src` → this will fail

**Phase to Address:** Phase 0 (Fork Paperclip UI) — Document "Pattern Extraction, Not Code Copy" before touching any frontend code

---

## Moderate Pitfalls

Mistakes that cause significant delays but are recoverable with course correction.

### Pitfall 6: RAG Integration — Embedding Quality Degradation

**What goes wrong:** Knowledge distillation accumulates low-quality patterns. Brains learn from their own mistakes, creating a feedback loop of bad advice. "Delta-Velocity" metric shows decline, not improvement.

**Why it happens:**
- No validation that experience_record is "successful" before storing
- Human corrections not tracked — brain repeats same mistake
- Embeddings stale (old knowledge never updated)
- No deduplication — same pattern stored 100 times

**Prevention:**
- **Success Filter:** Only log experiences with `human_rating >= 4/5` or `auto_score > 0.8`
- **Correction Tracking:** If human overrides brain output → flag as anti-pattern, store as negative example
- **Embedding Refresh:** Weekly re-embedding of outdated patterns (timestamp > 90 days)
- **Deduplication:** Semantic similarity check before inserting (if cosine_sim > 0.95 → skip)

**Detection:**
- Brain suggestions getting worse over time (subjective user feedback)
- Delta-Velocity metric: `T3_brain < T3_baseline` (agent slower than manual)
- `experience_records` table grows by 10K+ rows per week (too much noise)

**Phase to Address:** Phase 4 (Knowledge Distillation Engine) — Build success filters before first experience log

---

### Pitfall 7: 3-Service Distributed System — Observability Gaps

**What goes wrong:** Rust service fails but Python/TypeScript don't know. Request timeout, no error logged. Debugging requires checking 3 different log streams. "It's slow" but which service is the bottleneck?

**Why it happens:**
- No distributed tracing (correlation IDs lost across service boundaries)
- Logs in 3 different formats (Rust `tracing`, Python `structlog`, Next.js `console.log`)
- No unified dashboard — need to open 3 terminals to debug one request
- "We'll add tracing later" → never happens

**Prevention:**

1. **Correlation ID — Inject at Edge, Propagate Everywhere**
   ```rust
   // Rust Control Plane (edge service)
   use uuid::Uuid;

   #[derive(Debug, Clone)]
   pub struct Metadata {
       pub request_id: Uuid, // Generate on first request
       pub user_id: Option<i32>,
   }

   // Pass to Python via gRPC metadata
   let request = tonic::Request::new(brain_execution_request);
   request.metadata_mut().insert("x-request-id", metadata.request_id.to_string());
   ```

   ```python
   # Python Agent Runtime
   request_id = request.metadata.get("x-request-id")
   logger.bind(request_id=request_id).info("Processing brain execution")
   ```

2. **Structured Logging — JSON Format Everywhere**
   ```rust
   // Rust: tracing + tracing-subscriber JSON formatter
   tracing::info!(
       request_id = %metadata.request_id,
       brain_id = %brain.id,
       duration_ms = execution_time.as_millis(),
       "Brain execution completed"
   );
   ```

   ```python
   # Python: structlog
   log.info("brain_execution_completed",
       request_id=request_id,
       brain_id=brain.id,
       duration_ms=execution_time
   )
   ```

   ```typescript
   // Next.js: pino or winston JSON logging
   logger.info({
       request_id,
       brain_id: brain.id,
       duration_ms: executionTime
   }, "Brain execution completed");
   ```

3. **OpenTelemetry Distributed Tracing**
   ```toml
   # Cargo.toml (Rust)
   [dependencies]
   opentelemetry = "0.21"
   tracing-opentelemetry = "0.22"
   ```

   ```python
   # requirements.txt (Python)
   opentelemetry-api==1.21.0
   opentelemetry-sdk==1.21.0
   ```

   - Single trace spans across Rust → Python → TypeScript
   - Grafana Tempo UI: See request waterfall (which service is slow)

4. **Unified Observability Dashboard**
   - Grafana: Metrics (Prometheus) + Logs (Loki) + Traces (Tempo)
   - Alert: If p95 latency > 5s in any service → page on-call
   - Service Health: `/health` endpoint in all 3 services (Rust, Python, Next.js)

**Detection:**
- Debugging requires SSH into 3 servers to check logs
- "Which service is causing the timeout?" → can't answer without manual trace
- Logs not queryable (grep only, no structured fields)
- No graphs for latency, error rate, request volume

**Phase to Address:** Phase 2 (Orchestration Canvas) — Add distributed tracing BEFORE building real-time canvas (canvas needs traces)

---

### Pitfall 8: Marketplace Before Validation — Build Trap

**What goes wrong:** Building template marketplace, multi-tenant RBAC, billing infrastructure before having 3 paying customers. Zero usage, wasted engineering, "if we build it they will come" fallacy.

**Why it happens:**
- Excitement about "platform" features (marketplace sounds sexy)
- Assumption: "Competitors have marketplace, we need it too"
- Fear: "If we don't build marketplace, we can't scale"
- Reality: **Paperclip has marketplace, zero paying customers** (red flag ignored)

**Prevention:**

1. **CONDITIONAL Gate — LOI Before Marketplace**
   - Milestone: "Template Marketplace + Multi-tenant" is BLOCKED until:
     - ✅ 3 LATAM SME interviews completed
     - ✅ 1 Letter of Intent (LOI) signed (customer commits to pay)
     - ✅ Customer agrees to pay for marketplace feature (validation, not assumption)
   - If gate not met → marketplace deferred to v3.1+

2. **Single-Tenant First — Multi-Tenant Later**
   - v3.0: Single company per deployment (simpler, faster)
   - v3.1+: Multi-tenant ONLY if > 5 paying customers request it
   - Don't build RBAC until you have > 1 organization

3. **Template Marketplace = GitHub Repository, Not SaaS**
   - Phase 4: Templates stored in `mastermind-templates/` GitHub repo
   - Users `git clone` templates, import to their instance
   - No billing, no authentication, no marketplace UI
   - If templates get > 100 GitHub stars → build SaaS marketplace in v3.1

4. **Customer Discovery — 3 Interviews Before Code**
   - Interview LATAM SMEs: "Would you pay $50/mo for a template marketplace?"
   - If answer: "No, we build our own templates" → marketplace is waste
   - If answer: "Yes, but only if it has X" → build X, not full marketplace

**Detection:**
- PRD includes "multi-tenant" and "marketplace" but zero customer interviews
- Competitive analysis: "Paperclip has it, we need it" → copycat trap
- Engineering team building billing before first payment
- No LOI from any customer, but marketplace sprint already planned

**Phase to Address:** Phase 5 (Template Marketplace) — DO NOT START until LOI gate passed

---

## Minor Pitfalls

Mistakes that cause annoyance but are quickly fixed.

### Pitfall 9: Rust Learning Curve — Maintenance Risk

**What goes wrong:** AI writes Rust code during development (fast), but 6 months later human must debug (slow). No one on team knows Rust ownership, lifetimes, async/await. Debugging `borrow checker` errors takes hours.

**Why it happens:**
- "AI will write the Rust" — true during initial development
- **BUT:** Production incidents require human debugging
- Rust has steep learning curve (ownership, lifetimes, `Send`/`Sync`)
- If team doesn't know Rust → every bug is a day-long investigation

**Prevention:**
- **Escape Hatch:** If Rust velocity < 0.5x Python → Rust only for WebSocket Hub + Adapter Registry
- **At Least One Human Rust Expert:** Hire, contract, or train ONE person who owns Rust service
- **Rust is NOT for Business Logic:** Python handles all complex domain logic (brains, knowledge distillation)
- **Rust = Infrastructure Only:** Auth, WebSocket, database access (all standard patterns)

**Detection:**
- "How do I fix this borrow checker error?" asked daily
- Rust PR review takes 3+ hours (vs 30 min for Python)
- On-call rotation refuses to cover Rust service (no one knows how to debug)

**Phase to Address:** Phase 1 (Foundation Upgrade) — Measure Rust vs Python velocity, activate escape hatch if needed

---

### Pitfall 10: PostgreSQL pgvector Over-Engineering

**What goes wrong:** Installing pgvector extension, building vector search, embedding all brain knowledge — but never using it. v3.0 ships with RAG infrastructure, zero production queries.

**Why it happens:**
- "We'll need vector search later" (future-proofing)
- Excitement about AI/RAG buzzwords
- Paperclip doesn't have it → "differentiator" (but unvalidated)
- Reality: **7 brains with NotebookLM is sufficient for v3.0**

**Prevention:**
- **v3.0: NO pgvector** — Use existing 7 brains + NotebookLM
- **v3.1+: ADD pgvector** — ONLY if: experience_records > 10K AND search is slow
- Don't install pgvector until you have a proven performance problem

**Detection:**
- `pgvector` in `requirements.txt` but no queries use it
- Embedding script runs but no dashboard searches embeddings
- "We'll use this in v3.1" → you're building for imaginary users

**Phase to Address:** Phase 4 (Knowledge Distillation) — Remove pgvector from scope, use existing NotebookLM

---

## Phase-Specific Warnings

| Phase Topic | Likely Pitfall | Mitigation |
|-------------|---------------|------------|
| **Phase 0: Fork UI** | Architecture mismatch (Vite → Next.js) | Pattern extraction, NOT code copy. Rebuild with Server Components. |
| **Phase 1: Rust + gRPC** | Type sync drift | Proto sync CI gate BEFORE writing first gRPC service. |
| **Phase 1: PostgreSQL** | Data loss in migration | Test against PostgreSQL from day 1, never SQLite in dev. |
| **Phase 2: Real-time Hub** | Observability gaps | Add distributed tracing BEFORE building canvas. |
| **Phase 3: Multi-channel** | Webhook message loss | Webhook queue + DLQ BEFORE connecting to WhatsApp API. |
| **Phase 4: Knowledge Distillation** | Low-quality RAG | Success filters BEFORE logging first experience. |
| **Phase 5: Marketplace** | Build trap (no validation) | LOI gate BEFORE writing marketplace code. |

---

## Sources

### High Confidence (Official Documentation & Project Context)
- **Project Context Files** (HIGH confidence — read directly):
  - `.planning/PROJECT.md` — Existing v2.2 stack, technical debt, known issues
  - `.planning/BRAIN-FEED.md` — Anti-patterns tried and rejected (v2.2)
  - `docs/nuevo giro/PRP MasterMind v3.0.md` — Stack DEFINITIVO, Rust/Python split, escape hatch

- **Official Documentation** (HIGH confidence — authoritative sources):
  - **Tonic gRPC:** https://docs.rs/tonic/latest/tonic/ — Rust gRPC framework
  - **Axum:** https://docs.rs/axum/latest/axum/ — Rust web framework
  - **SQLx:** https://docs.rs/sqlx/latest/sqlx/ — Compile-time checked SQL for Rust
  - **Alembic:** https://alembic.sqlalchemy.org/en/latest/ — Database migration tool for Python
  - **Next.js App Router:** https://nextjs.org/docs/app — Official Next.js documentation

### Medium Confidence (Established Patterns)
- **Strangler Fig Pattern:** Martin Fowler's incremental migration strategy — NOT Big Bang rewrite
- **Big Bang Rewrite Failures:** Netscape rewrite (4 years, lost market share) — cautionary tale
- **SQLite vs PostgreSQL:** Type strictness differences, case sensitivity, transaction isolation
- **Webhook Best Practices:** Idempotency, dead letter queues, write-first-process-later pattern

### Low Confidence (Needs Validation — Web Search Unavailable)
- **Rust Python integration patterns:** tonic + betterproto specifics (web search limit exhausted)
- **WhatsApp Business API webhook reliability:** Meta platform specifics (web search unavailable)
- **pgvector performance at scale:** Vector DB benchmarks (web search unavailable)
- **Multi-channel architecture patterns:** WhatsApp + IG + email integration patterns (web search unavailable)

**Note:** Web search was unavailable (weekly/monthly limit exhausted at 2026-04-13 18:30:03). Some findings based on general software engineering knowledge, project context, and established patterns. **Verify with official docs before implementing.**

---

*Pitfalls research for: MasterMind Framework v3.0 — Enterprise Agent Orchestration Platform*
*Researched: 2026-04-06*
*Confidence: HIGH (project context) + MEDIUM (established patterns) + LOW (web search unavailable)*
