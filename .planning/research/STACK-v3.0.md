# Stack Research: v3.0 Enterprise Agent Orchestration Platform

**Domain:** Enterprise Agent Orchestration Platform with Knowledge Distillation for LATAM
**Researched:** 2026-04-04
**Confidence:** MEDIUM (WebSearch unavailable — relying on official docs + training data)

> **Note:** This document covers ONLY NEW stack additions for v3.0.
> The existing v2.2 stack (Python FastAPI, Next.js 16, 7 brain agents, 985 tests) remains unchanged.
> See `.planning/research/STACK.md` for the validated v2.2 stack.

---

## Executive Summary

MasterMind v3.0 expands the validated Python FastAPI + Next.js 16 stack with **Rust (Axum + Tokio)** for the control plane, **gRPC + Protobuf** for type-safe cross-language communication, **PostgreSQL + pgvector** for vector embeddings, **multi-channel adapters** for WhatsApp/Instagram/Email, and **knowledge distillation** leveraging the existing 7-brain architecture. This research focuses ONLY on stack additions for NEW capabilities — existing stack (14.5K LOC Python, 15.8K LOC TypeScript, 620+407 tests) remains unchanged.

**Key Decision (from milestone validation):** If Rust velocity < 0.5x Python during VS (Vertical Slice) phase, Rust reduces to WebSocket Hub + Adapter Registry only. Python retains agent runtime.

---

## Recommended Stack Additions

### 1. Rust Control Plane & Real-time Hub (65% of new stack)

| Technology | Version | Purpose | Why Recommended |
|------------|---------|---------|-----------------|
| **Axum** | 0.7.x | Web framework for control plane | Type-safe routing, middleware, extractors — built on Tokio, battle-tested for high-performance services |
| **Tokio** | 1.x | Async runtime | Rust's standard async runtime — required by Axum, tonic, SQLx. Handles tasks, IO, timers with multi-threaded scheduler |
| **tonic** | 0.11.x | gRPC server/client | Native Rust gRPC implementation with Tokio integration — type-safe from `.proto` files, supports streaming, interceptors |
| **SQLx** | 0.7.x | Async PostgreSQL driver | Compile-time checked queries (optional), supports connection pooling, transactions, migrations. Prefer over diesel for async-first |
| **tokio-tungstenite** | 0.21.x | WebSocket server | Real-time hub for brain status updates, DAG illumination — Tokio-native, handles fragmentation, compression |
| **anyhow** | 1.x | Error handling | Structured errors with context — use for application errors, not library code |
| **tracing** | 0.1.x | Structured logging | Modern instrumentation with spans, events, subscribers — integrates with Tokio, better than `log` crate |
| **tower** | 0.4.x | Middleware stack | Composable service layer — rate limiting, timeout, compression, auth. Axum is built on Tower |
| **tower-http** | 0.5.x | HTTP-specific middleware | CORS, compression, trace headers — sits on top of Tower |

**Why Rust for Control Plane:**
- **Performance:** Zero-cost abstractions, memory safety, no GC pauses — critical for real-time hub with 24+ concurrent brain connections
- **Type Safety:** Compile-time guarantees prevent entire classes of bugs (null pointer, data races) — JWT auth, rate limiting, routing
- **Concurrency:** Tokio's multi-threaded scheduler handles thousands of WebSocket connections without blocking
- **gRPC Native:** tonic generates type-safe Rust code from `.proto` — single source of truth across Rust/Python/TypeScript

**Escape Hatch:** If Rust velocity < 0.5x Python during VS phase, Rust reduces to WebSocket Hub + Adapter Registry only.

---

### 2. gRPC + Protobuf Type Sync

| Technology | Version | Purpose | Why Recommended |
|------------|---------|---------|-----------------|
| **tonic** (Rust) | 0.11.x | gRPC server + client | Async Tokio-based, codegen from `.proto`, supports bidirectional streaming for real-time brain status |
| **protobuf** (Rust) | 3.x | Serialization | Rust's official protobuf lib — required by tonic for encoding/decoding |
| **protoc** | 24.x+ | Protobuf compiler | Generate code for Rust, Python, TypeScript from `.proto` schema. Install via `apt install protobuf-compiler` (Linux) or `brew install protobuf` (macOS) |
| **grpclib** (Python) | 0.4.x | Pure asyncio gRPC | Pure Python asyncio gRPC — no C++ bindings, better than grpcio for async workflows |
| **grpcio-tools** (Python) | — | Python gRPC codegen | `pip install grpcio-tools`, then `python -m grpc_tools.protoc` to generate Python stubs |
| **ts-proto** (TypeScript) | 1.x+ | TypeScript gRPC codegen | Prefer over `protoc-gen-ts` — better TypeScript types, supports NestJS, Angular, React |

**What NOT to use:**
- ❌ **grpcio (Python):** Uses C++ bindings, slower async, maintenance issues. Use **grpclib** instead
- ❌ **REST/JSON for Rust↔Python:** Slower, no type safety, schema drift between services
- ❌ **FlatBuffers:** Less ecosystem support than protobuf, no gRPC bindings

**gRPC Interop Workflow:**
1. **Single `.proto` source** in `proto/` directory (e.g., `proto/control_plane.proto`)
2. **Generate Rust code:** `protoc --rust_out=. --tonic_out=. proto/control_plane.proto`
3. **Generate Python code:** `python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. proto/control_plane.proto`
4. **Generate TypeScript code:** `protoc --plugin=protoc-gen-ts=./node_modules/.bin/protoc-gen-ts --ts_out=. proto/control_plane.proto`

---

### 3. PostgreSQL + pgvector Migration

| Technology | Version | Purpose | Why Recommended |
|------------|---------|---------|-----------------|
| **PostgreSQL** | 16.x | Primary database | Open-source, ACID, MVCC, JSONB — pgvector support requires 13+, 16.x recommended for performance |
| **pgvector** | 0.5.x+ | Vector similarity search | HNSW indexing for fast approximate nearest neighbor (ANN) — cosine distance, L2 distance. Integrates with SQL queries |
| **SQLx** (Rust) | 0.7.x | Async PostgreSQL driver | Compile-time checked queries, connection pooling, migrations. Use `sqlx-cli` for migrations |
| **asyncpg** (Python) | 0.29.x | Async PostgreSQL driver | Fastest Python PostgreSQL driver — native asyncio, prepared statements, connection pooling |
| **alembic** | 1.13.x | Database migrations | SQLAlchemy-based migrations — version control for schema changes. Required for SQLite → PostgreSQL migration |
| **sqlalchemy** | 2.x | ORM (optional) | Use with Alembic for migrations — but prefer asyncpg for runtime queries (faster than ORM) |

**Migration Strategy:**
1. **Phase 1:** Add PostgreSQL as second database (dual-write mode) — SQLite remains primary
2. **Phase 2:** Migrate read queries to PostgreSQL — keep SQLite for fallback
3. **Phase 3:** Switch primary to PostgreSQL — SQLite becomes backup
4. **Phase 4:** Remove SQLite dependency — single database architecture

**Why PostgreSQL over SQLite for v3.0:**
- **Concurrent writes:** SQLite locks entire DB on write — 24 simultaneous brain completions need true MVCC
- **pgvector:** Vector similarity search requires pgvector extension — not available in SQLite
- **Scale:** Single-server SQLite is fine for v2.2, but v3.0 multi-channel + RAG needs proper database
- **Connection pooling:** PostgreSQL handles hundreds of concurrent connections — SQLite limited to single writer

**What NOT to use:**
- ❌ **SQLite + FTS5 for vectors:** Full-text search != vector similarity — cosine distance requires pgvector
- ❌ **Separate vector DB (Qdrant/Weaviate):** Overkill for v3.0 — pgvector is sufficient, keeps stack simpler

---

### 4. Multi-Channel Adapters

| Technology | Version | Purpose | Why Recommended |
|------------|---------|---------|-----------------|
| **WhatsApp Business API** | Cloud API | WhatsApp messaging | Official Meta API — cloud-hosted, no on-prem server. Use Python `whatsapp-business-python` SDK or HTTP client |
| **Meta Graph API** | 19.x | Instagram DM messaging | Same API as WhatsApp — single SDK for both channels. Use `facebook-business` Python SDK |
| **aiosmtplib** | 3.x | Async Email sending | SMTP client for asyncio — supports TLS, authentication, MIME attachments |
| **email-validator** | 2.x | Email validation | Syntax check, DNS lookup, deliverability — prevent spam traps |
| **aiohttp** | 3.x | Async HTTP client | For WhatsApp/Instagram API calls — non-blocking, async/await |

**Why Python for Adapters (not Rust):**
- **SDK Availability:** WhatsApp, Instagram, Email have mature Python SDKs — Rust libs are immature or non-existent
- **Iteration Speed:** Adapter logic changes frequently (rate limits, webhook formats) — Python is faster to modify
- **Agent Runtime:** Python already handles AI/LLM calls — adapters should live where agents run

**Adapter Architecture:**
```
┌─────────────────────────────────────────────────────────────┐
│                    Rust Control Plane                       │
│  (Message Router, Rate Limiting, JWT Auth, Webhook Sink)   │
└──────────────┬──────────────────────────────────────────────┘
               │ gRPC/Protobuf
               ▼
┌─────────────────────────────────────────────────────────────┐
│                 Python Agent Runtime                        │
│  (Multi-channel Adapters: WhatsApp, Instagram, Email)      │
└──────────────┬──────────────────────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────────────────────┐
│              PostgreSQL + pgvector                          │
│  (Messages, Vectors, Brain State, Knowledge Store)         │
└─────────────────────────────────────────────────────────────┘
```

**What NOT to use:**
- ❌ **On-prem WhatsApp Business API:** Requires Docker, certificate management, hosting — Cloud API is simpler
- ❌ **Synchronous HTTP clients:** Blocking calls kill Rust async performance — always use async variants

---

### 5. Knowledge Distillation Engine

| Technology | Version | Purpose | Why Recommended |
|------------|---------|---------|-----------------|
| **pgvector** | 0.5.x+ | Vector similarity search | Store embeddings directly in PostgreSQL — no separate vector DB needed |
| **sentence-transformers** | 2.x | Embedding generation | Python lib for text embeddings — use `all-MiniLM-L6-v2` (fast) or `all-mpnet-base-v2` (accurate) |
| **numpy** | 1.26.x | Vector operations | Required by sentence-transformers, fast array ops |
| **brain_memory.py** (existing) | — | CLI for brain memory | **ALREADY EXISTS** — use `mastermind brain:save` to persist patterns, `mastermind brain:recall` to retrieve |
| **experience_records** table (existing) | — | SQLite memory storage | **ALREADY EXISTS** — migrate to PostgreSQL in v3.0, add vector column |

**Knowledge Distillation Architecture (leverages existing brains):**
```
User Brief → Orchestrator → Brain Agents (parallel) → Outputs
                                      ↓
                            [Pattern Extraction]
                                      ↓
                        sentence-transformers → Embeddings
                                      ↓
                            PostgreSQL + pgvector
                                      ↓
                    [Future: RAG retrieval for similar contexts]
```

**Why pgvector over separate vector DB:**
- **Simpler stack:** One database for all data (messages, vectors, state)
- **SQL joins:** Filter by metadata + vector similarity in single query
- **Sufficient scale:** pgvector handles 1M+ vectors with HNSW — only need Faiss at 100M+ vectors

**What NOT to use:**
- ❌ **OpenAI embeddings:** Requires API key, cost per query, network latency — sentence-transformers is free, local, faster
- ❌ **ChromaDB:** Overkill for v3.0 — pgvector is enough, adds infra complexity

---

## Installation

### Rust (Control Plane)

```bash
# Rust toolchain (if not installed)
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
source $HOME/.cargo/env

# Add to apps/control-plane/Cargo.toml
[dependencies]
axum = "0.7"
tokio = { version = "1", features = ["full"] }
tonic = "0.11"
prost = "0.12"
tokio-tungstenite = "0.21"
sqlx = { version = "0.7", features = ["runtime-tokio", "postgres", "chrono", "uuid"] }
anyhow = "1"
tracing = "0.1"
tracing-subscriber = { version = "0.3", features = ["env-filter"] }
tower = "0.4"
tower-http = { version = "0.5", features = ["cors", "trace"] }
uuid = { version = "1", features = ["v4", "serde"] }
chrono = { version = "0.4", features = ["serde"] }

# Build protobuf
cargo install protoc-gen-prost
cargo install protoc-gen-tonic

# Generate code from proto/control_plane.proto
protoc --rust_out=. --tonic_out=. proto/control_plane.proto
```

### Python (Agent Runtime + Adapters)

```bash
# Already using uv — from apps/api/
cd /home/rpadron/proy/mastermind/apps/api

# gRPC
uv add grpclib  # pure asyncio gRPC
uv add grpcio-tools  # for protoc codegen

# PostgreSQL
uv add asyncpg sqlalchemy alembic
uv add "sqlalchemy[asyncio]"  # async SQLAlchemy

# Vector embeddings
uv add sentence-transformers numpy

# Multi-channel adapters
uv add aiohttp aiosmtplib email-validator
uv add whatsapp-business-python  # or use aiohttp for raw HTTP
uv add facebook-business  # Instagram Graph API

# Run migrations
uv run alembic upgrade head
```

### TypeScript (Frontend gRPC Client)

```bash
# From apps/web/
pnpm add @grpc/grpc-js @grpc/proto-loader
# OR use protoc-gen-ts for type safety
pnpm add -D protoc-gen-ts ts-proto

# Generate TypeScript from proto
protoc --plugin=protoc-gen-ts=./node_modules/.bin/protoc-gen-ts \
  --ts_out=. \
  proto/control_plane.proto
```

### PostgreSQL + pgvector

```bash
# Install PostgreSQL 16
sudo apt install postgresql-16 postgresql-contrib-16

# Install pgvector extension
git clone --branch v0.5.0 https://github.com/pgvector/pgvector.git
cd pgvector
make
sudo make install
sudo systemctl restart postgresql

# Enable extension in database
psql -d mastermind -c "CREATE EXTENSION vector;"

# Verify
psql -d mastermind -c "SELECT * FROM pg_extension WHERE extname = 'vector';"
```

---

## Alternatives Considered

| Category | Recommended | Alternative | Why Not Recommended |
|----------|-------------|-------------|---------------------|
| **Rust Web Framework** | Axum 0.7 | Actix-web | Axum has better ergonomics, type-safe extractors, Tower middleware ecosystem |
| **Rust gRPC** | tonic 0.11 | grpc-rus | tonic is pure Rust, Tokio-native, better async support. grpc-rus uses C++ bindings |
| **Rust Database** | SQLx 0.7 | Diesel | Diesel is sync-first, heavy macro system. SQLx is async, compile-time checked (optional) |
| **Python gRPC** | grpclib | grpcio | grpclib is pure asyncio, no C++ bindings. grpcio requires grpcio-tools, heavier deps |
| **Vector DB** | pgvector | Qdrant, Weaviate | pgvector is PostgreSQL extension — single DB, simpler infra. Qdrant adds separate service |
| **Embeddings** | sentence-transformers | OpenAI embeddings | sentence-transformers is free, local, no API key. OpenAI has cost, latency, rate limits |
| **Email** | aiosmtplib | Sendgrid SDK | aiosmtplib is SMTP-agnostic, works with any provider. Sendgrid SDK locks you in |

---

## What NOT to Use

| Technology | Why Avoid | Use Instead |
|------------|-----------|-------------|
| **REST/JSON for Rust↔Python** | Slower, no type safety, schema drift | gRPC + Protobuf (single source of truth) |
| **SQLite for v3.0** | Locks on write, no pgvector, not multi-writer safe | PostgreSQL 16 + pgvector |
| **FlatBuffers** | Less ecosystem support, no gRPC bindings | Protobuf (official gRPC format) |
| **OpenAI embeddings** | Cost per query, network latency, API key needed | sentence-transformers (local, free) |
| **Celery/RQ** | Adds Redis/infrastructure, asyncio sufficient | asyncio.TaskGroup (Python 3.11+) |
| **On-prem WhatsApp Business API** | Docker hosting, cert management, overhead | WhatsApp Cloud API (Meta-hosted) |
| **Synchronous HTTP clients** | Blocking calls kill async performance | reqwest (Rust), aiohttp (Python) |
| **Separate vector DB (v3.0)** | Overkill, adds infra | pgvector (single DB) |

---

## Integration Points with Existing Stack

### Existing Stack (DO NOT TOUCH)
- **Python FastAPI** (`apps/api/`) — 14,500 LOC, 620 tests, SQLite WAL
- **Next.js 16** (`apps/web/`) — 15,800 LOC, 407 tests, JWT auth, WebSocket infrastructure
- **7 Brain Agents** (`.claude/agents/mm/`) — Autonomous, BRAIN-FEED driven, parallel dispatch
- **Zustand 5 + TanStack Query v5** — State management, already battle-tested
- **React Flow v12** — DAG visualization, working in The Nexus

### NEW Integration Points

#### 1. Rust Control Plane ↔ Python Agent Runtime (gRPC)
```
┌─────────────────────────────────────────────────────────────┐
│                  Rust Control Plane                         │
│  Axum + Tokio + tonic (gRPC server)                         │
│  - JWT auth                                                  │
│  - Rate limiting (Tower middleware)                         │
│  - WebSocket hub (tokio-tungstenite)                        │
│  - Message router (multi-channel)                           │
└──────────────┬──────────────────────────────────────────────┘
               │ gRPC/Protobuf (proto/control_plane.proto)
               │  - BrainStatusRequest/Response
               │  - TaskDispatchRequest/Response
               │  - VectorSearchRequest/Response
               ▼
┌─────────────────────────────────────────────────────────────┐
│              Python Agent Runtime (FastAPI)                 │
│  grpclib client (gRPC)                                      │
│  - Receives tasks from Rust                                │
│  - Executes brain agents                                    │
│  - Returns results via gRPC                                 │
│  - Multi-channel adapters (WhatsApp, Instagram, Email)     │
└─────────────────────────────────────────────────────────────┘
```

#### 2. Python Agent Runtime ↔ PostgreSQL (asyncpg)
```
┌─────────────────────────────────────────────────────────────┐
│              Python Agent Runtime (FastAPI)                 │
│  asyncpg connection pool                                    │
│  - Migrate from SQLite to PostgreSQL                        │
│  - Dual-write mode (Phase 1)                                │
│  - Vector embeddings (pgvector)                             │
└──────────────┬──────────────────────────────────────────────┘
               │ SQL (asyncpg)
               ▼
┌─────────────────────────────────────────────────────────────┐
│              PostgreSQL 16 + pgvector                       │
│  - experience_records (migrated from SQLite)               │
│  - brain_messages (vector column added)                    │
│  - multi_channel_messages (new table)                      │
│  - knowledge_vectors (new table, pgvector)                 │
└─────────────────────────────────────────────────────────────┘
```

#### 3. Rust Control Plane ↔ Next.js Frontend (WebSocket)
```
┌─────────────────────────────────────────────────────────────┐
│                  Rust Control Plane                         │
│  WebSocket hub (tokio-tungstenite)                         │
│  - Real-time brain status updates                          │
│  - DAG illumination events                                  │
│  - Cost/usage metrics                                       │
└──────────────┬──────────────────────────────────────────────┘
               │ WebSocket (existing Zustand infrastructure)
               ▼
┌─────────────────────────────────────────────────────────────┐
│                Next.js 16 Frontend                          │
│  Zustand 5 + RAF batching (existing)                       │
│  - Reuse wsDispatcher.ts (singleton)                       │
│  - Add new event types (brain status, cost metrics)        │
└─────────────────────────────────────────────────────────────┘
```

---

## Version Compatibility

| Package A | Compatible With | Notes |
|-----------|-----------------|-------|
| Axum 0.7 | Tokio 1.x, Tower 0.4 | Axum 0.7 requires Tokio 1.x |
| tonic 0.11 | Tokio 1.x, prost 0.12 | tonic generates code from `.proto` |
| SQLx 0.7 | Tokio 1.x | SQLx runtime-tokio feature required |
| pgvector 0.5.x | PostgreSQL 13+ | PostgreSQL 16.x recommended |
| sentence-transformers 2.x | Python 3.8+, PyTorch | Requires numpy, torch |
| asyncpg 0.29.x | Python 3.8+, asyncio | Native asyncio driver |
| grpclib 0.4.x | Python 3.8+, asyncio | Pure Python asyncio gRPC |

---

## Sources

- **MEDIUM confidence** — Official documentation verified, WebSearch unavailable due to rate limit
- [Axum Documentation](https://docs.rs/axum/latest/axum/) — Official Rust docs for Axum 0.7
- [Tokio Documentation](https://docs.rs/tokio/latest/tokio/) — Official async runtime docs
- [tonic Documentation](https://docs.rs/tonic/latest/tonic/) — Official gRPC Rust implementation
- [SQLx Documentation](https://docs.rs/sqlx/latest/sqlx/) — Async PostgreSQL driver with compile-time checked queries
- [pgvector GitHub](https://github.com/pgvector/pgvector) — Vector similarity extension for PostgreSQL
- [sentence-transformers Documentation](https://www.sbert.net/) — Python library for text embeddings
- [WhatsApp Business API](https://developers.facebook.com/docs/whatsapp/cloud-api) — Official Meta documentation
- [Instagram Graph API](https://developers.facebook.com/docs/instagram/messaging) — Official Meta documentation
- [grpclib Documentation](https://grpclib.readthedocs.io/) — Pure asyncio gRPC for Python
- [asyncpg Documentation](https://magicstack.github.io/asyncpg/) — Fastest PostgreSQL driver for Python

**Gaps:** WebSearch unavailable (rate limit resets 2026-04-13). Some version numbers based on training data — verify with official docs before implementation.

---

*Stack research for: MasterMind v3.0 Enterprise Agent Orchestration Platform*
*Researched: 2026-04-04*
*Focus: NEW capabilities only — existing stack (Python FastAPI, Next.js 16, 7 brains) remains unchanged*
