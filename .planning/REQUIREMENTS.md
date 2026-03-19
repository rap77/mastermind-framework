# Requirements: MasterMind Framework v2.1

**Defined:** 2026-03-18
**Core Value:** Expert AI collaboration that scales — War Room frontend brings real-time brain orchestration to life visually.

## v2.1 Requirements

### Foundation

- [x] **FND-01**: Developer can initialize apps/web/ with Next.js 16, Tailwind 4, shadcn/ui (new-york), and Magic UI — React Flow CSS loads correctly without style conflicts, Magic UI @keyframes animations verified working after install
- [x] **FND-02**: User can authenticate via login page with JWT stored as httpOnly cookie (proxy.ts route protection, CVE-2025-29927 mitigated)
- [x] **FND-03**: User is redirected to login when accessing any protected route without a valid JWT
- [x] **FND-04**: Frontend connects to FastAPI WebSocket at api:8000 directly from the browser without CORS errors (Docker networking configured)

### Backend Gaps

- [ ] **BE-01**: User can query `GET /api/brains` and receive all 24 brains with metadata: name, niche, status, uptime, last_called_at
- [ ] **BE-02**: User can query `GET /api/tasks/{id}/graph` and receive a React Flow compatible payload: `{ nodes[], edges[], layout_positions }` with initial node positions

### Schema Bridge

- [ ] **SB-01**: Developer can run a schema generator script that produces Zod types from Pydantic models in apps/api/ and outputs them to apps/web/src/types/api.ts — TypeScript errors surface immediately when backend models change

### WebSocket Layer

- [ ] **WS-01**: WebSocket connection is established once per session and shared across all screens — no reconnect on client-side navigation
- [ ] **WS-02**: UI remains responsive at 60fps when 24 brains fire events simultaneously — RAF/requestIdleCallback batching applied before Zustand state updates
- [ ] **WS-03**: Each brain tile and node updates independently via targeted Map<brainId, BrainState> selectors — no cascade re-renders across other tiles/nodes

### Command Center

- [ ] **CC-01**: User can submit a brief via cmdk modal with multi-line textarea and Cmd+Enter shortcut — full-screen modal style (not single-line command palette)
- [ ] **CC-02**: User sees all 24 brain tiles in a Magic UI Bento Grid with live status (idle / active / complete / error) fed from WebSocket events
- [ ] **CC-03**: Brain tiles animate visually when receiving WebSocket status events (pulse on active, checkmark on complete, red on error)

### The Nexus

- [ ] **NEX-01**: User sees a DAG of brain dependencies as a React Flow graph with custom shadcn/ui Card nodes (NODE_TYPES declared at module level)
- [ ] **NEX-02**: Nodes illuminate in real-time (border color, glow) as brains start, complete, or fail execution via WebSocket events
- [ ] **NEX-03**: User can click a node to see brain details without triggering accidental drag/pan — all interactive elements inside nodes use `nodrag nopan` CSS classes

### Strategy Vault

- [ ] **SV-01**: User can view a list of past executions with status, brief text, duration, and brain count
- [ ] **SV-02**: User can select an execution and view formatted Markdown output from each participating brain

### Engine Room

- [ ] **ER-01**: User can view live structured logs with virtual scrolling, level filtering (info/warn/error), and auto-follow — powered by react-logviewer connected to WebSocket
- [ ] **ER-02**: User can manage API keys for Claude/Gemini: view masked keys, create new, revoke existing
- [ ] **ER-03**: User can view the YAML configuration of any brain and copy it to clipboard

### UX

- [ ] **UX-01**: User can enter Focus Mode during active execution — sidebar collapses, idle brain tiles dim, active execution elements are highlighted

## v2.2 Requirements (Deferred)

### Production Hardening

- **HARD-01**: System runs behind HTTPS + nginx reverse proxy
- **HARD-02**: API endpoints have rate limiting per IP/user
- **HARD-03**: MM_SECRET_KEY is required from environment (no hardcoded fallback)
- **HARD-04**: Expired sessions are cleaned up automatically

### Semantic Routing

- **SEM-01**: System uses Claude as FlowDetector (replaces keyword matching)
- **SEM-02**: Routing decision includes confidence score and explanation

### Observability

- **OBS-01**: /health endpoint returns real database and WS status
- **OBS-02**: Structured logging with trace IDs across all components
- **OBS-03**: CI includes Trufflehog secret scanner

## Out of Scope

| Feature | Reason |
|---------|--------|
| HTMX/Alpine.js dashboard | Replaced by Next.js 16 — v2.0 preserved in git history |
| OpenAPI auto-generated TS client | Schema Bridge (Pydantic→Zod) is simpler and sufficient for v2.1 |
| WebSocket reconnection strategy | Deferred to v2.2 — not blocking v2.1 UX goals |
| Mobile responsive layout | Web-first priority; responsive polish in v2.2 |
| Real-time collaborative editing | v3.0+ |
| Multi-tenant SaaS | Single-tenant only for v2.x |

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| FND-01 | Phase 5 | Complete |
| FND-02 | Phase 5 | Complete |
| FND-03 | Phase 5 | Complete |
| FND-04 | Phase 5 | Complete |
| SB-01 | Phase 5 | Pending |
| WS-01 | Phase 5 | Pending |
| WS-02 | Phase 5 | Pending |
| WS-03 | Phase 5 | Pending |
| BE-01 | Phase 6 | Pending |
| CC-01 | Phase 6 | Pending |
| CC-02 | Phase 6 | Pending |
| CC-03 | Phase 6 | Pending |
| BE-02 | Phase 7 | Pending |
| NEX-01 | Phase 7 | Pending |
| NEX-02 | Phase 7 | Pending |
| NEX-03 | Phase 7 | Pending |
| SV-01 | Phase 8 | Pending |
| SV-02 | Phase 8 | Pending |
| ER-01 | Phase 8 | Pending |
| ER-02 | Phase 8 | Pending |
| ER-03 | Phase 8 | Pending |
| UX-01 | Phase 8 | Pending |

**Coverage:**
- v2.1 requirements: 22 total
- Mapped to phases: 22 ✅
- Unmapped: 0 ✅

---
*Requirements defined: 2026-03-18*
*Last updated: 2026-03-18 — traceability populated after roadmap creation*
