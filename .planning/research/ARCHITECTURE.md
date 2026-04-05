# Architecture Patterns — MasterMind v3.0

**Domain:** Enterprise Agent Orchestration Platform with Knowledge Distillation
**Researched:** 2026-04-04
**Overall confidence:** HIGH

## Executive Summary

MasterMind v3.0 introduces a **3-service architecture** (Rust Control Plane + Python Agent Runtime + Next.js Frontend) that builds incrementally on the existing v2.2 foundation. The integration strategy is **evolutionary, not revolutionary** — Python FastAPI remains the AI/knowledge layer, Rust handles performance-critical infrastructure, and Next.js evolves to match Paperclip's UX maturity.

**Key architectural insight:** The Rust Control Plane is a **thin orchestration wrapper** around existing Python brain agents, not a rewrite. Brain agents, knowledge distillation, and memory systems remain in Python. Rust only owns state management, real-time events, and multi-channel routing — areas where existing FastAPI WebSocket infrastructure has scalability limits.

---

## Recommended Architecture

### 3-Service Split

```
┌───────────────────────────────────────────────────────────────┐
│                     MasterMind v3.0                            │
│                                                                │
│  ┌──────────────────┐  ┌──────────────────┐  ┌─────────────┐ │
│  │   RUST CORE      │  │  PYTHON AI       │  │  NEXT.js    │ │
│  │   (Axum+Tokio)   │  │  (FastAPI v2.2)  │  │  16+        │ │
│  │                  │  │                  │  │  Paperclip  │ │
│  │  ▸ Control Plane │  │  ▸ 7 Brains      │  │  UX Fork    │ │
│  │  ▸ Real-time Hub │  │  ▸ Knowledge     │  │  ▸ Canvas   │ │
│  │  ▸ WebSockets    │  │  ▸ LangChain     │  │  ▸ Dashboard│ │
│  │  ▸ Adapter Reg.  │  │  ▸ NotebookLM    │  │  ▸ Monitor  │ │
│  │  ▸ Auth+JWT+RBAC │  │  ▸ Auto-learn    │  │             │ │
│  └────────┬─────────┘  └────────┬─────────┘  └──────┬──────┘ │
│           │                     │                     │         │
│           └──────────┬──────────┴─────────────────────┘         │
│                      │                                        │
│             ┌────────┴────────┐                               │
│             │  gRPC + Protobuf│ ← Type-safe contract          │
│             └────────┬────────┘                               │
│                      │                                        │
│  ┌────────────┐  ┌───┴─────────┐  ┌──────────────┐          │
│  │ PostgreSQL │  │  Redis      │  │  Adapters    │          │
│  │ + pgvector │  │  Pub/Sub    │  │  WhatsApp    │          │
│  │            │  │             │  │  Instagram   │          │
│  │            │  │             │  │  Email       │          │
│  └────────────┘  └─────────────┘  └──────────────┘          │
└───────────────────────────────────────────────────────────────┘
```

### Component Boundaries

| Component | Responsibility | Communicates With | Existing? |
|-----------|----------------|-------------------|-----------|
| **Rust Control Plane** | Auth, state management, WebSocket hub, adapter registry, cost tracking | Python Runtime (gRPC), Next.js (WebSocket + HTTP), PostgreSQL, Redis | NEW — Fase 1 |
| **Python Agent Runtime** | 7 brain agents, knowledge distillation, LangChain, NotebookLM, experience logging | Rust Control Plane (gRPC), PostgreSQL, vector stores (future) | EXISTING — v2.2 FastAPI, minimal wrapper changes |
| **Next.js Frontend** | Canvas, dashboard, monitoring, config forms, multi-channel inbox | Rust Control Plane (WebSocket + HTTP), Python Runtime (gRPC proxy via Rust) | EXISTING — v2.2, evolves to match Paperclip UX |

### Data Flow

**Current v2.2 flow:**
```
Next.js → FastAPI HTTP/WS → brain_router.py → brain agents → SQLite → WS response
```

**v3.0 flow:**
```
Next.js → Rust Control Plane (HTTP/WS)
    ↓
Rust routes to Python Agent Runtime via gRPC
    ↓
Python brain agents execute → PostgreSQL → experience_records
    ↓
Python gRPC callback → Rust
    ↓
Rust WebSocket broadcast → Next.js (pub/sub via Redis for scale)
```

**Key change:** Rust becomes the **routing and event hub**, Python becomes a **compute service** for AI/knowledge operations.

---

## Integration Points with Existing Architecture

### 1. Python Agent Runtime — Minimal Changes, Maximum Reuse

**What stays in Python (NO migration to Rust):**
- `mastermind_cli/orchestrator/brain_router.py` (23 tests) — brain routing logic
- `mastermind_cli/orchestrator/coordinator.py` (54.2K LOC) — orchestration engine
- `mastermind_cli/tools/brain_memory.py` — memory CLI
- `mastermind_cli/experience/` — experience logging
- `mastermind_cli/memory/` — brain memory system
- All 7 brain agent bundles (`.claude/agents/mm/`)

**What changes in Python:**
- **New gRPC server** (tonic-build for Python) — wraps existing orchestration logic
- **New gRPC client** (calls Rust Control Plane for state queries)
- **FastAPI routes deprecated** — all HTTP/WS goes through Rust, Python is gRPC-only
- **PostgreSQL client** — replace aiosqlite with SQLAlchemy/Alembic (async)

**Migration strategy:**
```python
# Existing v2.2 entry point
@app.post("/api/tasks")
async def create_task(...):
    result = await coordinator.run_brains(brief)
    return result

# v3.0 Python gRPC service
class BrainAgentService(brain_pb2_grpc.BrainAgentServicer):
    async def ExecuteBrain(self, request, context):
        # Reuse existing coordinator
        result = await coordinator.run_brains(
            brief=Brief.from_proto(request.brief)
        )
        return result.to_proto()
```

**Why this works:** The coordinator is already a pure function with minimal FastAPI dependencies. Extracting it to gRPC is a protocol change, not a logic rewrite.

### 2. Rust Control Plane — New Components

**New Rust modules (apps/control-plane/):**

| Module | Purpose | Integration Point |
|--------|---------|-------------------|
| `auth/` | JWT verification, RBAC, API keys | Migrate from `apps/api/mastermind_cli/auth/` |
| `websocket/` | Real-time hub, connection management | Replace FastAPI `websocket.py` (ThrottledBroadcaster → Tokio broadcast) |
| `execution/` | State machine for tasks, processes | Calls Python gRPC for brain execution |
| `adapters/` | Multi-channel routing (WhatsApp, IG, email) | NEW — sends messages to Python for NLP processing |
| `grpc/` | gRPC server (tonic) + Python client | Bridges Rust ↔ Python |
| `http/` | Axum HTTP routes for Next.js | Proxy to Python gRPC for brain operations |
| `postgres/` | SQLx queries, migrations, pgvector | Replace `state/database.py` |
| `cost/` | Token/cost tracking per brain | NEW — budget enforcement |

**Key Rust responsibilities:**
- **WebSocket hub** — replace FastAPI WebSocketManager with Tokio-based broadcast
- **State management** — PostgreSQL as source of truth (not SQLite)
- **Adapter registry** — dynamic routing to WhatsApp/IG/email providers
- **Auth middleware** — JWT verification, RBAC per organization
- **gRPC gateway** — all Python brain execution goes through Rust

### 3. Next.js Frontend — Evolution to Paperclip UX

**What stays:**
- `apps/web/src/stores/wsStore.ts` — WebSocket client (minor endpoint change)
- `apps/web/src/stores/brainStore.ts` — RAF batching, 60fps (no changes)
- `apps/web/src/app/(protected)/` — 4 screens (Command Center, Nexus, Strategy Vault, Engine Room)
- React Flow v12, Zustand 5, TanStack Query v5

**What evolves (Paperclip patterns):**
- **Layout** — three-column responsive with sidebar (`paperclip/ui/src/components/Layout.tsx`)
- **Real-time monitoring** — `ActiveAgentsPanel.tsx` (ping animation, live status)
- **Cost dashboard** — `BillerSpendCard.tsx` with `QuotaBar` (budget visualization)
- **Kanban board** — `KanbanBoard.tsx` for task management (@dnd-kit)
- **Command palette** — `CommandPalette.tsx` (Cmd+K quick actions)
- **Onboarding wizard** — `OnboardingWizard.tsx` (progressive setup)
- **Run transcript** — `RunTranscript` (multi-density streaming output)

**Integration changes:**
- WebSocket endpoint → `ws://rust-control-plane:3001/ws` (not FastAPI)
- HTTP API calls → Rust Axum server (proxies to Python via gRPC)
- TypeScript types → auto-generated from Protobuf (not handwritten Zod schemas)

### 4. PostgreSQL Migration — Schema Translation

**Existing SQLite schema (v2.2):**
```sql
-- tasks table (from state/database.py)
CREATE TABLE tasks (
    id TEXT PRIMARY KEY,
    brief TEXT NOT NULL,
    status TEXT NOT NULL,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

-- executions table
CREATE TABLE executions (
    id TEXT PRIMARY KEY,
    task_id TEXT NOT NULL,
    brain_id TEXT NOT NULL,
    status TEXT NOT NULL,
    progress_json TEXT,
    result_json TEXT,
    error TEXT,
    created_at TEXT,
    completed_at TEXT,
    FOREIGN KEY (task_id) REFERENCES tasks(id)
);

-- experience_records table
CREATE TABLE experience_records (
    id TEXT PRIMARY KEY,
    brain_id TEXT NOT NULL,
    interaction_type TEXT NOT NULL,
    input_summary TEXT NOT NULL,
    output_summary TEXT NOT NULL,
    created_at TEXT NOT NULL
);
```

**PostgreSQL v3.0 schema (enhanced):**
```sql
-- organizations table (NEW — multi-tenant)
CREATE TABLE organizations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    plan TEXT NOT NULL, -- free, pro, enterprise
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    rbac_policy JSONB -- permissions per role
);

-- tasks table (migrated + enhanced)
CREATE TABLE tasks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID NOT NULL REFERENCES organizations(id),
    user_id TEXT NOT NULL, -- from JWT sub
    brief JSONB NOT NULL, -- structured brief, not TEXT
    status TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- executions table (migrated + enhanced)
CREATE TABLE executions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    task_id UUID NOT NULL REFERENCES tasks(id),
    brain_id TEXT NOT NULL,
    status TEXT NOT NULL,
    progress_json JSONB,
    result_json JSONB,
    error TEXT,
    tokens_used INTEGER, -- NEW — cost tracking
    cost_usd DECIMAL(10, 4), -- NEW — cost tracking
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    completed_at TIMESTAMPTZ
);

-- experience_records table (migrated + enhanced)
CREATE TABLE experience_records (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    brain_id TEXT NOT NULL,
    organization_id UUID REFERENCES organizations(id), -- NEW — per-org learning
    interaction_type TEXT NOT NULL,
    input_summary TEXT NOT NULL,
    output_summary TEXT NOT NULL,
    delta_velocity REAL, -- NEW — improvement metric
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- activity_log table (NEW — event sourcing)
CREATE TABLE activity_log (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    task_id UUID REFERENCES tasks(id),
    execution_id UUID REFERENCES executions(id),
    event_type TEXT NOT NULL, -- brain_started, brain_completed, etc.
    event_data JSONB NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- indexes (performance)
CREATE INDEX idx_tasks_org ON tasks(organization_id);
CREATE INDEX idx_executions_task ON executions(task_id);
CREATE INDEX idx_executions_brain ON executions(brain_id);
CREATE INDEX idx_experience_org_brain ON experience_records(organization_id, brain_id);
CREATE INDEX idx_activity_task ON activity_log(task_id);
CREATE INDEX idx_activity_timestamp ON activity_log(created_at DESC);
```

**Migration strategy:**
1. **Vertical slice first** — migrate 1 table + 1 flow end-to-end
2. **Dual-write period** — FastAPI writes to SQLite + PostgreSQL (validate consistency)
3. **Switch reads** — Rust reads from PostgreSQL, Python still writes to both
4. **Deprecate SQLite** — Python writes to PostgreSQL only, remove SQLite code

### 5. gRPC + Protobuf — Type Sync Across 3 Languages

**Protobuf definitions (apps/proto/):**

```protobuf
// common.proto — shared types
syntax = "proto3";

package mastermind;

message Brief {
  string task_id = 1;
  string user_id = 2;
  string description = 3;
  map<string, string> context = 4;
  repeated string brain_keywords = 5;
}

message BrainResult {
  string brain_id = 1;
  string status = 2; // pending, running, completed, failed
  string output = 3;
  repeated string warnings = 4;
  int32 tokens_used = 5;
}

message TaskStatus {
  string task_id = 1;
  string status = 2;
  repeated BrainResult brain_results = 3;
  double total_cost_usd = 4;
}

// brain_agent.proto — Python service
service BrainAgentService {
  rpc ExecuteBrain(Brief) returns (BrainResult);
  rpc GetTaskStatus(string) returns (TaskStatus);
  rpc QueryKnowledge(QueryRequest) returns (QueryResponse);
}

message QueryRequest {
  string brain_id = 1;
  string query = 2;
  int32 k = 3; // top-k results
}

message QueryResponse {
  repeated string results = 1;
  repeated double scores = 2;
}

// control_plane.proto — Rust service
service ControlPlaneService {
  rpc CreateTask(CreateTaskRequest) returns (TaskStatus);
  rpc SubscribeTaskUpdates(TaskSubscription) returns (stream TaskUpdate);
  rpc RegisterAdapter(AdapterConfig) returns (AdapterStatus);
}
```

**Type generation:**

```bash
# Rust types (tonic + prost)
protoc --rust_out ./apps/control-plane/src/proto \
       --tonic_out ./apps/control-plane/src/proto \
       -I apps/proto \
       apps/proto/*.proto

# Python types (betterproto)
protoc --python_out=./apps/api/mastermind_cli/proto \
       --betterproto_out=./apps/api/mastermind_cli/proto \
       -I apps/proto \
       apps/proto/*.proto

# TypeScript types (protoc-gen-es)
protoc --es_out=./apps/web/src/proto \
       -I apps/proto \
       apps/proto/*.proto
```

**Result:** One field change → compilation error in all 3 languages. No more drift between Pydantic, Zod, and Rust structs.

---

## Patterns to Follow

### Pattern 1: Vertical Slice for Rust Integration

**What:** Build 1 API path end-to-end before committing to the 3-service split.

**When:** Fase 1 (Foundation Upgrade) — Week 1-2.

**Example:**
```rust
// Rust Control Plane — minimal Axum server
use axum::{routing::post, Router};

#[tokio::main]
async fn main() {
    let app = Router::new()
        .route("/api/tasks", post(create_task))
        .layer(axum::middleware::from_fn(auth_middleware));

    let listener = tokio::net::TcpListener::bind("0.0.0.0:3001").await.unwrap();
    axum::serve(listener, app).await.unwrap();
}

async fn create_task(
    Json(brief): Json<Brief>,
    extension(py_client): Extension<PythonGrpcClient>,
) -> Json<TaskStatus> {
    // Call Python via gRPC
    let result = py_client.execute_brain(&brief).await;
    Json(result)
}
```

**Verification criteria:**
- [ ] Next.js can call `/api/tasks` on Rust (not FastAPI)
- [ ] Rust calls Python gRPC successfully
- [ ] Task status stored in PostgreSQL (not SQLite)
- [ ] WebSocket events flow Rust → Next.js

**Why:** Reduces risk. If Rust velocity < 0.5x Python, we can fall back to "Rust as WebSocket hub only" (escape hatch from PRP).

### Pattern 2: Adapter Pattern for Multi-Channel

**What:** Rust trait `BrainAdapter` for pluggable channel providers.

**When:** Fase 3 (Multi-Channel Gateway).

**Example:**
```rust
#[async_trait]
pub trait BrainAdapter: Send + Sync {
    async fn send_message(&self, msg: Message) -> Result<AdapterResponse>;
    async fn query_knowledge(&self, query: &str) -> Result<Vec<KnowledgeFragment>>;
    fn channel_type(&self) -> ChannelType;
}

pub struct WhatsAppAdapter {
    api_key: String,
    phone_number_id: String,
}

#[async_trait]
impl BrainAdapter for WhatsAppAdapter {
    async fn send_message(&self, msg: Message) -> Result<AdapterResponse> {
        // Call WhatsApp Business API
        let client = reqwest::Client::new();
        client.post(format!("https://graph.facebook.com/v19.0/{}/messages", self.phone_number_id))
            .header("Authorization", format!("Bearer {}", self.api_key))
            .json(&msg)
            .send()
            .await?;
        Ok(AdapterResponse::success())
    }

    fn channel_type(&self) -> ChannelType {
        ChannelType::WhatsApp
    }
}

// Adapter Registry
pub struct AdapterRegistry {
    adapters: HashMap<String, Box<dyn BrainAdapter>>,
}

impl AdapterRegistry {
    pub async fn route_message(&self, msg: Message) -> Result<AdapterResponse> {
        let adapter = self.adapters.get(&msg.channel_id).ok_or("Adapter not found")?;
        adapter.send_message(msg).await
    }
}
```

**Why:** Allows dynamic registration of new channels without core logic changes. WhatsApp, Instagram, email, Odoo — all implement the same trait.

### Pattern 3: Event Sourcing for Activity Log

**What:** Immutable `activity_log` table as source of truth for all brain operations.

**When:** Fase 1 (PostgreSQL migration).

**Example:**
```sql
-- Immutable append-only log
INSERT INTO activity_log (task_id, event_type, event_data)
VALUES ('uuid-123', 'brain_started', '{"brain_id": "brain-01", "timestamp": "2026-04-04T10:00:00Z"}');

INSERT INTO activity_log (task_id, event_type, event_data)
VALUES ('uuid-123', 'brain_completed', '{"brain_id": "brain-01", "output": "...", "tokens": 1500}');

-- Reconstruct task state from events
SELECT * FROM activity_log WHERE task_id = 'uuid-123' ORDER BY created_at ASC;
```

**Rust query (SQLx compile-time verified):**
```rust
use sqlx::FromRow;

#[derive(FromRow)]
struct ActivityEvent {
    id: Uuid,
    task_id: Uuid,
    event_type: String,
    event_data: Jsonb,
    created_at: DateTime<Utc>,
}

let events = sqlx::query_as::<_, ActivityEvent>(
    "SELECT * FROM activity_log WHERE task_id = $1 ORDER BY created_at ASC"
)
.bind(task_id)
.fetch_all(pool)
.await?;
```

**Why:** Enables analytics, audit trails, and learning from history. Reconstruct state at any point in time (temporal queries).

---

## Anti-Patterns to Avoid

### Anti-Pattern 1: Rewriting Python Brain Logic in Rust

**What:** Porting `coordinator.py`, `brain_router.py`, or agent logic to Rust.

**Why bad:**
- **Huge velocity cost** — Python AI code is working, Rust rewrite is months of work
- **Lost expertise** — 7 brains have distilled knowledge in Python prompts
- **Unclear performance win** — brain execution is I/O-bound (API calls), not CPU-bound

**Instead:**
- Rust calls Python via gRPC for brain operations
- Python stays as AI/knowledge service
- Rust only owns state management, events, routing

### Anti-Pattern 2: Direct Next.js → Python gRPC Calls

**What:** Frontend bypasses Rust, calls Python gRPC directly.

**Why bad:**
- **Bypasses auth middleware** — Rust JWT checks circumvented
- **No unified event hub** — WebSocket updates fragmented
- **Tight coupling** — Next.js needs Python gRPC client, complicates deployment

**Instead:**
- Next.js calls Rust HTTP/WebSocket only
- Rust routes to Python via internal gRPC
- Single entry point = simpler security model

### Anti-Pattern 3: Monolithic Protobuf File

**What:** All 50+ message types in one `mastermind.proto` file.

**Why bad:**
- **Slow compilation** — any change rebuilds entire proto
- **Unclear boundaries** — Python, Rust, Next.js concerns mixed

**Instead:**
```
apps/proto/
├── common.proto      # Brief, BrainResult, TaskStatus
├── brain_agent.proto # Python service definitions
├── control_plane.proto # Rust service definitions
└── frontend.proto    # Next.js types only
```

### Anti-Pattern 4: PostgreSQL Before gRPC Contract

**What:** Migrate database schema before defining gRPC interfaces.

**Why bad:**
- **Schema drift** — Python and Rust develop divergent data models
- **Integration pain** — gRPC mismatch requires schema rework

**Instead:**
1. Define Protobuf contracts first (Fase 1, Week 1)
2. Generate types in all 3 languages
3. Implement PostgreSQL schema to match proto types
4. Build migration scripts from SQLite → PostgreSQL

---

## Scalability Considerations

| Concern | At 100 users | At 10K users | At 1M users |
|---------|--------------|--------------|-------------|
| **WebSocket connections** | Rust Tokio (single host) | Rust + Redis pub/sub (3 hosts) | Rust cluster + Redis Cluster |
| **PostgreSQL** | Single instance + pgbench | Primary + 2 replicas | Patroni cluster + PgBouncer |
| **Python gRPC** | 1 FastAPI container | 3 containers (load balanced) | Autoscaling pool + queue |
| **Knowledge distillation** | In-memory experience_records | Redis cache + PostgreSQL | Separate vector DB (Qdrant) |
| **Multi-channel adapters** | 1 WhatsApp API key | Rate-limited per org | Adapter pool per region |

**Key scaling point:** Rust Control Plane is stateless (except WebSocket connections). Scale horizontally by adding more Rust instances behind a load balancer. Python gRPC services can scale independently.

---

## Migration Path — Build Order

### Phase 0: Fork Paperclip UI (1-2 weeks)
**Goal:** Copy frontend, rebrand to MasterMind.

**Tasks:**
1. Copy `/home/rpadron/proy/paperclip/ui/` → `apps/web-v3/`
2. Replace Paperclip API calls with placeholder endpoints
3. Rebrand colors, logos, texts
4. Verify 10 UX patterns work (see PAPERCLIP-UX-AUDIT.md)

**Deliverable:** `apps/web-v3/` with MasterMind branding, non-functional API calls.

### Phase 1: Vertical Slice — Rust + gRPC + PostgreSQL (3-4 weeks)
**Goal:** Prove 3-service architecture with 1 flow end-to-end.

**Tasks:**
1. **Define Protobuf contracts** (`apps/proto/common.proto`, `brain_agent.proto`)
2. **Bootstrap Rust Control Plane** (Axum + Tokio + tonic + SQLx)
3. **Implement Python gRPC wrapper** (betterproto, wraps existing coordinator)
4. **PostgreSQL migration** — migrate `tasks` table only
5. **Wire 1 flow:** Next.js → Rust → Python gRPC → PostgreSQL → Rust WS → Next.js

**Deliverable:** `/api/tasks/create` works end-to-end with 3 services. WebSocket updates flow correctly.

**Success criteria:**
- [ ] Rust receives HTTP request, validates JWT
- [ ] Rust calls Python via gRPC
- [ ] Python executes brain, returns result
- [ ] Rust stores result in PostgreSQL
- [ ] Rust broadcasts WebSocket event
- [ ] Next.js receives WS event, updates UI

### Phase 2: Rust WebSocket Hub + Real-time Canvas (2-3 weeks)
**Goal:** Replace FastAPI WebSocket with Tokio-based hub, build React Flow canvas.

**Tasks:**
1. **Rust WebSocket server** (tokio-tungstenite)
2. **Redis pub/sub** for cross-service broadcast
3. **React Flow canvas** (nodes = brains, edges = routing rules)
4. **Real-time updates** (ping animation, live status)

**Deliverable:** Canvas shows live brain execution with WebSocket updates.

### Phase 3: Multi-Channel Gateway (3-4 weeks)
**Goal:** WhatsApp + Instagram + email adapters in Rust.

**Tasks:**
1. **Adapter trait** (`BrainAdapter` with `send_message`, `query_knowledge`)
2. **WhatsApp adapter** (Meta Graph API)
3. **Instagram DM adapter** (Meta Graph API)
4. **Email gateway** (lettre + imap crates)
5. **Unified inbox UI** (Paperclip `RunTranscript` pattern)

**Deliverable:** Send message via WhatsApp, receive response, route to Python for NLP, respond.

### Phase 4: Knowledge Distillation Engine (3-4 weeks)
**Goal:** Brains learn from interactions.

**Tasks:**
1. **Experience analytics dashboard** (patterns per brain)
2. **Auto-learning loop** (Brain #7 evaluates → feedback → adjustment)
3. **Template generation** (successful interactions → reusable templates)

**Deliverable:** Experience records show delta-velocity improvements. Templates marketplace v1.

### Phase 5: Template Marketplace + Enterprise (4-6 weeks)
**Goal:** Scale to multiple verticals.

**Tasks:**
1. **Multi-tenant RBAC** (per-organization isolation)
2. **Template marketplace** (Clipmart-style gallery)
3. **Enterprise adapters** (Odoo, Notion, custom webhooks)
4. **Billing + usage tracking**

**Deliverable:** 5 paying customers, 10 templates, multi-tenant isolation verified.

---

## Integration Checklist

### New Components (Build from Scratch)
- [ ] Rust Control Plane (apps/control-plane/)
- [ ] Protobuf definitions (apps/proto/)
- [ ] PostgreSQL schema + migrations
- [ ] Redis pub/sub for WebSocket scaling
- [ ] Multi-channel adapters (WhatsApp, IG, email)
- [ ] gRPC Python wrapper (apps/api/mastermind_cli/proto/)

### Modified Components (Evolve Existing)
- [ ] Python FastAPI → Python gRPC service (minimal changes to coordinator)
- [ ] SQLite → PostgreSQL (migration scripts)
- [ ] Next.js API calls → Rust endpoints (update TanStack Query hooks)
- [ ] WebSocket client → Rust Control Plane (change endpoint URL)
- [ ] TypeScript types → Protobuf-generated (remove Zod schemas)

### Unchanged Components (Reuse as-Is)
- [ ] 7 brain agent bundles (`.claude/agents/mm/`)
- [ ] `brain_router.py` (routing logic)
- [ ] `coordinator.py` (orchestration engine)
- [ ] `brain_memory.py` CLI
- [ ] `experience_records` logging (enhanced with PostgreSQL)
- [ ] Zustand stores (wsStore, brainStore)
- [ ] React Flow DAG (Nexus screen)

---

## Confidence Assessment

| Area | Confidence | Notes |
|------|------------|-------|
| **3-service architecture** | HIGH | Clear separation: Rust (infra), Python (AI), Next.js (UX). Proven pattern (Paperclip does similar Rust/TS split). |
| **gRPC type sync** | HIGH | Protobuf is industry standard. tonic (Rust) + betterproto (Python) + protoc-gen-es (TS) are mature. |
| **PostgreSQL migration** | HIGH | SQLx compile-time queries prevent runtime SQL errors. Alembic handles migrations safely. |
| **Rust WebSocket hub** | MEDIUM | Tokio-tungstenite is proven, but need to test Ghost Mode buffer equivalent. |
| **Multi-channel adapters** | MEDIUM | Trait pattern is sound, but WhatsApp/IG API approval is external dependency. |
| **Knowledge distillation** | HIGH | Leverages existing `experience_records` + brain_memory.py. PostgreSQL schema supports per-org learning. |

**Gaps to validate:**
- **Rust velocity vs Python** — Vertical slice (Phase 1) will confirm if Rust development is fast enough
- **WebSocket Ghost Mode in Rust** — Need to replicate ThrottledBroadcaster + buffer behavior in Tokio
- **gRPC latency overhead** — Measure Python ←→ Rust call latency. If > 50ms, consider direct Next.js → Python for hot paths

---

## Sources

### Internal Documentation (HIGH confidence)
- `.planning/PROJECT.md` — Existing architecture, v2.2 feature set
- `.planning/BRAIN-FEED.md` — Architecture invariants, patterns proven in production
- `docs/nuevo giro/PRP MasterMind v3.0 — Plataforma de Orquestación con Knowledge Distillation.md` — v3.0 vision, Rust/Python split rationale
- `docs/nuevo giro/PAPERCLIP-UX-AUDIT.md` — 10 UX patterns to copy from Paperclip

### Codebase Analysis (HIGH confidence)
- `apps/api/mastermind_cli/orchestrator/coordinator.py` (54.2K LOC) — Orchestration engine to wrap in gRPC
- `apps/api/mastermind_cli/orchestrator/brain_router.py` (23 tests) — Brain routing logic
- `apps/api/mastermind_cli/api/websocket.py` — ThrottledBroadcaster, Ghost Mode buffer
- `apps/api/mastermind_cli/state/database.py` — SQLite schema to migrate
- `apps/web/src/stores/wsStore.ts` — WebSocket client (endpoint change only)
- `apps/web/src/stores/brainStore.ts` — RAF batching (no changes)

### External References (MEDIUM confidence — search limit reached, general knowledge)
- Axum web framework — https://github.com/tokio-rs/axum
- Tokio async runtime — https://tokio.rs/
- tonic gRPC for Rust — https://github.com/hyperium/tonic
- betterproto for Python — https://github.com/danielgtaylor/python-betterproto
- SQLx compile-time SQL — https://github.com/launchbadge/sqlx
- React Flow v12 — https://reactflow.dev/

**Note:** WebSearch limit reached (429 error). Architecture recommendations based on internal documentation + codebase analysis + general knowledge of Rust/Python/TypeScript ecosystems. Validation via Context7 for specific libraries would increase confidence to HIGH.
