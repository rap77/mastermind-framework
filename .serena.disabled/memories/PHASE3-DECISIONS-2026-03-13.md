# MasterMind Framework v2.0 - Phase 3 Decisions

**Date:** 2026-03-13
**Type:** project
**Topic:** Phase 3 Web UI Platform - Implementation Decisions

---

## Real-time Updates Architecture

### Streaming Strategy: Smart Focus + Throttled

**Core Concept:**
- Only the focused/hovered brain streams full tokens
- Other 22 brains send only metadata (status, progress %)
- Batch update every 300ms with single JSON payload

**Why This Works:**
- Network: Minimal bandwidth (1 stream vs 23)
- CPU: 1 render per 300ms vs 23×60 per second
- UX: Still see "thinking" animation for all brains

### Reconnection Strategy: Ghost Mode 3-Tier

| Duration | Strategy | User Experience |
|----------|----------|-----------------|
| < 30s | Server buffer (100 events in memory) | Transparent, no data loss |
| 30s-5min | Ghost Mode (desaturated UI + counter) | Visual feedback, changes highlighted on return |
| > 5min | Manual refresh / error | Explicit action needed |

**Ghost Mode Implementation:**
- UI opacity: 0.6 (desaturated)
- Counter: "Last sync: 2m ago" pulsing
- On return: Highlight changes ("Brain #7 completed while you were away")
- Overlay: "Reconnecting..." (non-blocking)

**SQLite of Phase 2 Makes This Free:**
- No server-side state needed in memory
- Reconnect with `last_event_id` → query transitions table
- History already persisted from Phase 2

### Fallback: Smart Degradation (Hybrid Polling)

**Adaptive Frequency:**
- 23 brains running → aggressive polling (1-2s)
- System idle after 3 no-change attempts → relaxed polling (10s)
- New user interaction → back to aggressive

**Implementation:**
- Reuse GET /api/tasks/state endpoints from Ghost Mode
- Compatible with any proxy/firewall (HTTP only)
- Transparent: user doesn't notice SSE failed

---

## Observability & Debugger

### Logs Panel: Fixed Bottom Drawer

**Why This Layout:**
- WSL2/CLI users are trained to look DOWN for output
- Collapsible drawer: hide when all good, expand when debugging
- Multitasking: see graph colors change above + text scroll below

**Filter Pill:**
- Default: "Filter: All Brains"
- Click node → "Filter: Brain #5"
- Instant noise reduction

### Trace Back: Ripple Effect (Hover Insight)

**How It Works:**
1. Hover over failed node
2. All non-ancestors fade (opacity 0.3)
3. Ancestor path highlights (thick red lines)
4. Failed node pulses with red glow
5. Bottom Drawer auto-highlights first failed ancestor's error

**"Analyze Root Cause" Button:**
- Only appears when there's a failure
- Click → zooms to origin + illuminates full path
- Zero visual noise when all is green

### SQLite Inspector: Interactive SQL Console

**Use Cases:**
- `SELECT * FROM brain_states WHERE status = 'failed'`
- Export CSV/JSON for external analysis
- Manual correction: stuck "running" → "failed"

**Safety:**
- Read-only suggested (to prevent corruption)
- Export before any manual edits
- Warnings before destructive queries

---

## Mobile Responsiveness

### Strategy: Tactical Mirror (Hybrid)

**Mobile View:**
- Header: "Running 15/23" global status
- List-View: vertical, ordered by execution flow
- Large indicators: ✅❌🔵 circles (tap-friendly)
- Tap item → expand mini-viewer (last 5 log lines)
- Floating button → Static graph snapshot (PNG/SVG)

**Desktop View:**
- Full interactive graph (23 nodes)
- Bento Grid layout
- Bottom drawer logs

### Desktop First Priority

**Why:**
- Zira is a productivity tool for developers
- 90% of usage will be at Ubuntu workstation
- WSL2 workflow: dashboard as secondary monitor while coding
- Mobile is "lifesaver" for kitchen/coffee breaks

**Implementation:**
- 90% effort: perfect desktop experience (Bento Grid, Graph, Logs)
- 10% effort: Tailwind CSS for mobile usable (not obsessed)
- No native apps (web-only)

---

## Auth & Sessions (Recap)

### Hybrid Mechanism

| Interface | Mechanism | Duration |
|-----------|-----------|----------|
| **Web UI** | JWT (Access 30min + Refresh 24h) | Refresh token rotation |
| **CLI** | API Keys (Personal Access Tokens) | Persistent (protected by Linux user) |

### Session Timeout: Context-Aware

| Context | Timeout | Behavior |
|---------|---------|----------|
| **CLI** | Never expires | Protected by Linux user permissions |
| **Web UI idle** | 1 hour | Standard inactivity timeout |
| **Web UI during execution** | Extended automatically | Silent refresh while brains running |
| **Tab closed** | 30 min | Session dies on close |

### Storage: Encrypted DB Store (Vault Pattern)

- All in SQLite: `users` + `api_keys` + `sessions` tables
- Sensitive fields encrypted at rest (ENV_VAR master key)
- SQL relations: users ↔ api_keys ↔ executions
- Consistent with Phase 2 (SQLite for task state)

---

## Dashboard Layout (Recap)

### Hybrid Command Center (IDE Style)

```
┌─────────────┬────────────────────────────────────────┐
│             │ ┌───────────┬──────────┬────────────┐ │
│  Sidebar    │ │           │          │            │ │
│  (Flows)    │ │   60%     │   20%    │    20%     │ │
│             │ │  Graph    │ Metrics  │ Providers  │ │
│             │ └───────────┴──────────┴────────────┘ │
├─────────────┼────────────────────────────────────────┤
│             │  ┌──────────────────────────────────┐ │
│             │  │  Logs (Bottom Drawer)             │ │
│             │  │  Filter: [All Brains | Brain #5] │ │
│             │  └──────────────────────────────────┘ │
└─────────────┴────────────────────────────────────────┘
```

### Graph Visualization: CI/CD Style

- Library: React Flow (D3-based, backend-agnostic)
- Layout: Left-to-right dependency flow
- Stages: Vertical topological ordering
- Critical path: Instantly visible

### Node States

| State | Color | Animation | Hover |
|-------|-------|-----------|-------|
| Pending | 🔳 Gray | None | Show dependencies |
| Running | 🔵 Blue | Spinner/Progress | Show current % |
| Completed | 🟢 Green | None | Show output summary |
| Failed | 🔴 Red | Pulse | "Analyze Root Cause" button |
| Skipped | 🟡 Yellow | None | Show reason (dep failed) |

### Theme: System-Adaptive

- Auto-detect OS/browser preference
- Dynamic accents by state:
  - Rest: Blue-gray
  - All good: Emerald green
  - Critical failure: Neon red

**Palette "Cyber-Modern":**
- Backgrounds: #0F172A (deep)
- Borders: Subtle + soft glow
- Typography: JetBrains Mono or Geist Mono

---

## Technical Stack

### Backend
- **Framework:** FastAPI (async)
- **Real-time:** SSE (Server-Sent Events)
- **Auth:** JWT (access + refresh with rotation)
- **State:** SQLite (aiosqlite, WAL mode)

### Frontend
- **Core:** HTMX/Alpine.js (simple, no build step) OR React/Svelte (complex)
- **Graph:** React Flow (D3-based)
- **Styling:** Tailwind CSS (responsive utilities)

### Integration with Phase 2
- `TaskRepository` for state queries
- `TaskRecord` Pydantic models
- SQLite as source of truth for resync

---

## Implementation Notes

**Claude's Discretion (flexible areas):**
- Exact throttling value (300ms is reasonable but adjustable)
- Server buffer size (100 events ~30s)
- Ghost Mode thresholds (30s, 5min can be tuned)
- Adaptive polling frequency (1s, 2s, 10s - configurable)
- Static snapshot format (PNG, SVG, PDF)
- Mobile mini-viewer line count (5 lines is suggestion)

**Key Principles:**
- Desktop-first: 90% effort on workstation experience
- API & CLI priority: Dashboard is consumer, not core
- Phase 2 reuse: SQLite makes resync almost free
- WSL2 workflow: Terminal-trained UX expectations

---

**For planner reference:** All decisions locked. Ready for `/gsd:plan-phase 3`.
