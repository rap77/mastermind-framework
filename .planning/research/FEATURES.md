# Feature Research: MasterMind War Room Frontend (v2.1)

**Domain:** Real-time AI orchestration dashboard — "War Room" for parallel brain execution
**Researched:** 2026-03-19
**Confidence:** HIGH (verified with React Flow docs, Magic UI source, multiple current sources)

---

## Context: What Already Exists (Do Not Re-Build)

The backend is production-ready. These are DONE:

| Backend Capability | Status | Notes |
|-------------------|--------|-------|
| FastAPI + JWT auth + refresh rotation | DONE | Token expiry 30min, refresh 24h |
| WebSocket server | DONE | Events: `brain_step_started`, `brain_step_completed`, `execution_finished` |
| 24 brains parallel execution (4.65x speedup) | DONE | DAG via asyncio.TaskGroup |
| Execution tracking + brain outputs in SQLite WAL | DONE | 0.39ms status queries |
| REST API for orchestration, history, config | DONE | FastAPI, Pydantic v2 |

Frontend replaces Alpine.js/HTMX dashboard. All data comes from the existing API.

---

## Feature Landscape

### Table Stakes (Users Expect These)

Features that, if missing, make the product feel broken or unfinished.

| Feature | Why Expected | Complexity | Backend Dependency |
|---------|--------------|------------|--------------------|
| Brief textarea with submit button | Users need to initiate executions | LOW | `POST /api/orchestrate` |
| Brain status tiles (pending/active/complete/error) | Can't use a war room without status visibility | MEDIUM | WebSocket `brain_step_*` events |
| DAG nodes change appearance on state change | If nodes don't react to events, graph is useless | MEDIUM | WebSocket + React Flow `setNodes` |
| Strategy Vault — list past executions + view outputs | Users need to retrieve brain outputs | LOW | `GET /api/executions` |
| Engine Room — live log stream | Operators expect logs for debugging | MEDIUM | WebSocket log events |
| Single WebSocket connection (not per-component) | Multiple connections to same WS endpoint will fail at scale | MEDIUM | Zustand store pattern |
| Auth gate (login → JWT in localStorage) | Backend requires JWT; frontend without auth = 401 everywhere | LOW | `POST /api/auth/login` |
| Error state handling per brain tile | Silent failures are unacceptable | LOW | `brain_step_failed` event |
| Responsive layout (≥768px) | War rooms are used on varied screens | LOW | CSS only |
| Dark mode | Developer tools universally dark-themed | LOW | Tailwind `dark:` variant |

### Differentiators (Competitive Advantage)

Features that make this "war room" feel alive vs. a generic dashboard.

| Feature | Value Proposition | Complexity | Notes |
|---------|-------------------|------------|-------|
| Bento Grid with live pulse animations on active brains | Spatial layout makes 24 brains scannable at a glance; pulse signals "this is happening" | MEDIUM | Magic UI BentoGrid + CSS `animate-pulse` per status |
| React Flow nodes illuminate on WS events | Visual causality — watching the DAG execute in real-time is the core "wow" | HIGH | `NodeStatusIndicator` from `@xyflow/react`, Zustand bridge |
| Raycast-style command input (full-screen overlay, keyboard-first) | Feels intentional, not a form; matches how power users work | MEDIUM | `cmdk` or shadcn Command + textarea expansion |
| Progressive AI output rendering (token streaming, not page load) | Perceived speed: watching a brain "think" is more engaging than waiting | HIGH | Server-Sent Events or WS streaming + `streamdown` or `react-markdown` with memoization |
| Brain status badge coloring in Bento Grid matches DAG node state | Visual consistency = users trust the UI faster | LOW | Single source of truth in Zustand, both screens subscribe |
| Strategy Vault — diff view between two executions | Agencies need to compare "this brief vs last brief" | HIGH | Custom diff component |
| Engine Room — filter logs by brain name + level | 24 brains generate noise; filtering by brain reduces cognitive load | MEDIUM | Client-side filter against `brain_name` in log payload |
| Time-to-first-output metric visible in Command Center | Shows value immediately: "Brain #1 responded in 1.2s" | LOW | Timestamp delta from execution_started to first brain_step_completed |

### Anti-Features (Commonly Requested, Often Problematic)

| Feature | Why Requested | Why Problematic | Alternative |
|---------|---------------|-----------------|-------------|
| One WebSocket connection per component | "Simplest" to implement in each component | N connections to FastAPI WS endpoint; state desync between components; reconnect storms | Zustand WS Dispatcher: single connection, per-component `subscribe(eventType, cb)` |
| Polling as WebSocket fallback | "What if WS disconnects?" | Adds 10x server load, defeats real-time purpose, creates stale-state UX | Exponential backoff reconnection in Zustand store; 3 retries then show "reconnecting…" banner |
| D3.js for DAG (keep from v2.0) | Already familiar, why switch? | Zero React integration — all imperative DOM; state sync nightmare with React; React Flow exists | React Flow — built for React, NodeStatusIndicator built-in, Zustand integration documented |
| Infinite scroll in Strategy Vault | "Show all executions" | Executions are large (24 brain outputs each); infinite scroll = unbounded memory | Pagination (20 per page) + search by date/brief text |
| Editable YAML in browser with no validation | "Let me edit brain configs in-place" | Invalid YAML silently breaks brains; users won't know until execution fails | Monaco editor + YAML schema validation, save blocked on parse error |
| Auto-refresh entire page on WS disconnect | "At least something happens" | Kills in-flight animations, loses form state, terrible UX | Reconnect indicator banner only; page state preserved |
| SSE for everything (abandon WebSocket) | "SSE is simpler for streaming" | Backend already uses WS; switching means rewriting FastAPI handlers | Keep WS for bidirectional control events; SSE only if adding server-push streaming of brain outputs specifically |
| Tabs per brain in Strategy Vault | "See each brain's output in its own tab" | 24 tabs is unusable tab-soup | Accordion/collapsible sections within single execution view |

---

## Screen-Specific Feature Analysis

### Screen 1: Command Center

**Purpose:** Brief submission + live status overview of all 24 brains.

**Table Stakes:**
- Textarea with ≥3 lines visible, grow-on-type behavior
- Submit triggers `POST /api/orchestrate` with brief text
- Disable submit during active execution (prevent double-submission)
- Bento Grid showing all 24 brains with name + current status

**UX Pattern — Raycast-style Command Input:**

The `cmdk` library (shadcn Command wrapper) provides keyboard-first modal overlay. For a "brief" (multi-line, freeform text), the correct pattern is NOT a command palette — those are for single-line actions. The correct pattern is:

1. **Command palette to OPEN the brief modal** — `⌘K` / `Ctrl+K` opens full-screen overlay
2. **Inside the modal: textarea** — auto-focused, `Cmd+Enter` submits, `Escape` closes
3. **Context selector above textarea** — choose niche (Software Dev / Marketing) before submitting

This matches Linear's issue creation (command to open, structured form inside) and avoids the anti-pattern of trying to submit a paragraph via a search-style input.

**Differentiator:** Add "brain group pre-selection" — toggle which of the 24 brains to include before submitting. Checkbox grid in the command modal. Medium complexity, high value for agencies running partial flows.

**Bento Grid — Magic UI vs custom CSS Grid:**

Magic UI BentoGrid (`magicui.design/docs/components/bento-grid`) is a React component built on CSS Grid under the hood, with Framer Motion animations included. The tradeoffs:

| Criterion | Magic UI BentoGrid | Custom CSS Grid |
|-----------|-------------------|-----------------|
| Setup time | 5 minutes (copy-paste) | 2-4 hours (layout logic) |
| Animations | Included (hover, scale, glow) | Write from scratch |
| Tile sizing | Predefined `col-span` variants | Full control |
| Bundle size | ~15KB (Framer Motion already in stack) | ~0KB extra |
| Customization | Props-based, limited | Total control |
| Status-reactive styling | Requires wrapping with custom logic | First-class CSS var |
| `className` injection | Yes (className prop per item) | N/A |

**Recommendation: Use Magic UI BentoGrid** as the structural shell, inject Tailwind status classes (`border-blue-500 animate-pulse` for active, `border-green-500` for complete, etc.) via the `className` prop per brain tile. Framer Motion is already in the stack (React Flow uses it). Zero extra bundle cost.

**Brain tile content:**
- Brain name (truncated at 20 chars)
- Status badge (pending/active/complete/error) with color
- Execution time (if complete)
- Output preview (first 80 chars of output, truncated)
- Click → opens Strategy Vault filtered to that brain's last output

### Screen 2: The Nexus (DAG Visualization)

**Purpose:** Real-time directed acyclic graph showing brain execution flow, nodes illuminate as events arrive.

**React Flow Patterns for Real-Time Node State:**

React Flow's recommended architecture for real-time updates uses **Zustand as the shared state bridge** (documented officially at `reactflow.dev/learn/advanced-use/state-management`). The pattern:

```
WebSocket event → Zustand store action → React Flow re-reads nodes from store
```

Critical constraint from React Flow docs: **you must create a new node object (spread) to trigger re-renders** — mutating node data in place does NOT work.

**Node state machine for brains:**

| State | Visual | CSS | Animation |
|-------|--------|-----|-----------|
| `pending` | Grey border, muted text | `opacity-50` | None |
| `active` | Blue border, bright text | `border-blue-400` | `NodeStatusIndicator` with `status="loading"` (spinning border) |
| `complete` | Green border, checkmark icon | `border-green-400` | Brief scale pulse on transition (Framer Motion `animate={{ scale: [1, 1.05, 1] }}`) |
| `error` | Red border, X icon | `border-red-400` | `NodeStatusIndicator` with `status="error"` |

`NodeStatusIndicator` is a built-in React Flow UI component (`@xyflow/react`) that wraps custom nodes and handles the `loading`/`success`/`error`/`initial` states with built-in border-spin animation. Use it — don't build this manually.

**Edge animation on activation:**

When a brain completes, its outgoing edges to dependent brains should animate (dashed animated stroke). React Flow supports `animated: true` on edges, which renders a CSS `stroke-dashoffset` animation. Flip `animated` to `true` in the Zustand store when `brain_step_completed` fires for the source node.

**Layout:**

24 nodes is a medium-size DAG. Use React Flow's `dagre` layout algorithm (`@dagrejs/dagre` + `reactflow-dagre-layout`). Run layout once on mount, don't re-layout on status changes (only data changes, not positions).

**Performance note:** With 24 nodes and frequent WS updates, use `useStore` selector to only re-render the specific node that changed, not the entire graph. The Zustand + React Flow pattern handles this correctly when using `updateNodeData()` from React Flow's internal API (added in React Flow 12).

### Screen 3: Strategy Vault

**Purpose:** Browse execution history, view brain outputs.

**Patterns for progressive/streamed AI output display:**

Outputs are stored in SQLite (not streamed to the Vault — the Vault shows completed results). However, if brain outputs are long (they often are), the display pattern matters.

**Pattern: Accordion + Markdown rendering with memoization**

Each brain output is stored as text (likely Markdown). Use:
1. `react-markdown` with memoization (Vercel AI SDK cookbook pattern) — prevents re-render cascade when parent updates
2. `rehype-highlight` for code blocks inside outputs
3. Collapsible accordion per brain (24 brains = don't show all at once)
4. Copy-to-clipboard per brain output (one button, no friction)

**If outputs stream during execution (future WS enhancement):**
Use `streamdown` (Vercel's open-source, `github.com/vercel/streamdown`) — handles incomplete markdown tokens without visual glitches. Drop-in replacement for `react-markdown`. Handles unterminated code blocks, partial links, etc.

**Execution list view:**
- Sort by date DESC (most recent first)
- Show: brief text (truncated 100 chars), timestamp, total brains, execution time, status
- Filter: by niche, by date range, by status
- Search: full-text on brief content (client-side filtering is fine for <1000 executions)
- Pagination: 20 per page — do NOT use infinite scroll (brain outputs are large)

**Diff view (differentiator, defer to v2.1.1):**
Compare two execution results side-by-side. Use `diff` npm package + custom rendering. Medium complexity, high agency value. Defer to after core Vault is working.

### Screen 4: Engine Room

**Purpose:** Structured log viewer, API key management, brain YAML config.

**Log Viewer Pattern — Virtual Scrolling:**

For a real-time log stream from 24 parallel brains, logs can accumulate fast (thousands of entries per execution). Virtual scrolling is mandatory, not optional.

**Library recommendation: `react-logviewer` (melloware fork of react-lazylog)**

- Virtual scrolling via `react-virtualized` under the hood
- Loads logs from WebSocket natively (`websocket` prop)
- ANSI color support (brain logs may use `rich` output from Python)
- Follow mode (auto-scroll to bottom as new logs arrive)
- Search/filter built-in
- Copy line on click
- GitHub: `melloware/react-logviewer`, actively maintained as of 2025

**Why not TanStack Virtual with custom implementation:**
TanStack Virtual is more flexible but requires building the entire log rendering pipeline manually (line parsing, ANSI coloring, follow mode, search). `react-logviewer` has all of this. Use the library.

**Log level color conventions (match Python `logging` module):**

| Level | Color | Tailwind Class |
|-------|-------|----------------|
| DEBUG | Grey | `text-slate-400` |
| INFO | White | `text-slate-100` |
| WARNING | Yellow | `text-yellow-400` |
| ERROR | Red | `text-red-400` |
| CRITICAL | Red bold | `text-red-500 font-bold` |
| BRAIN_START | Blue | `text-blue-400` |
| BRAIN_COMPLETE | Green | `text-green-400` |

**Filter controls (must-have):**
- Level filter (checkbox: DEBUG/INFO/WARNING/ERROR)
- Brain name filter (dropdown, multi-select)
- Clear logs button (local only — doesn't delete from backend)
- Download logs as `.txt`

**API Key Management:**
- List API keys with masked display (`sk-...xxxx`)
- Create new key (modal, label required)
- Revoke key (confirmation dialog)
- Never show full key after creation (show once, then mask)
- Backend dependency: `GET/POST/DELETE /api/keys` — verify this exists in v2.0 API

**Brain YAML Config:**
- Read-only list of brain YAML files with Monaco editor viewer
- Edit mode: Monaco with YAML language support (`monaco-editor` + `@monaco-editor/react`)
- Validate on change: parse YAML client-side (use `yaml` npm package), block save if invalid
- Save triggers `PUT /api/brains/{brain_id}/config`

---

## Feature Dependencies

```
[WebSocket Dispatcher (Zustand)]
    ├──required by──> [Command Center — live brain tiles]
    ├──required by──> [The Nexus — node illumination]
    └──required by──> [Engine Room — live log stream]

[Auth (JWT in Zustand/localStorage)]
    └──required by──> ALL screens (401 without it)

[Command Center — brief submission]
    └──enables──> [The Nexus — execution to visualize]
                      └──enables──> [Strategy Vault — execution to view]

[React Flow + dagre layout]
    └──requires──> [Execution DAG shape from API]
                      (GET /api/executions/{id}/dag or inferred from brain dependencies)

[Strategy Vault — output rendering]
    └──requires──> [GET /api/executions/{id} with brain outputs]

[Engine Room — YAML editor]
    └──requires──> [GET/PUT /api/brains/{id}/config — verify in FastAPI backend]
```

### Dependency Notes

- **WebSocket Dispatcher must be built first** — 3 of 4 screens depend on it. If built per-component, refactoring cost is high.
- **Auth before any screen** — Every API call needs JWT. Build login page + token storage before building screens.
- **The Nexus requires knowing the DAG shape** — The frontend needs the brain dependency graph structure. Verify `GET /api/executions/{id}/dag` or equivalent exists in the FastAPI backend. If not, this needs a new endpoint.
- **Strategy Vault has no WS dependency** — It reads completed data from REST. Can be built offline from the WS work.

---

## MVP Definition

### Launch With (v2.1 core)

Minimum viable "war room" — must validate the concept end-to-end.

- [ ] **Auth gate** — Login page, JWT in Zustand, axios interceptor for token refresh
- [ ] **WebSocket Dispatcher** — Zustand store, single connection, `subscribe(event, cb)` API, reconnect logic
- [ ] **Command Center** — Bento Grid with 24 brain tiles + status colors + command input modal
- [ ] **The Nexus** — React Flow DAG, nodes change state on WS events via `NodeStatusIndicator`
- [ ] **Strategy Vault** — Execution list + individual execution view with accordion brain outputs
- [ ] **Engine Room (logs only)** — `react-logviewer` wired to WS log events, filter by level

### Add After Validation (v2.1.x)

Features to add once core is working and used.

- [ ] **Engine Room — API key management** — List/create/revoke keys UI
- [ ] **Engine Room — YAML editor** — Monaco + YAML validation, save to API
- [ ] **Brain group pre-selection in Command modal** — Choose which brains to include
- [ ] **Execution diff view in Strategy Vault** — Compare two runs

### Future Consideration (v2.2+)

- [ ] **Execution replay** — Step through a past execution in the DAG (time-travel)
- [ ] **Brain analytics** — Which brains are slowest, error rates, token usage
- [ ] **Custom Bento Grid layout** — Drag-resize tiles, persist layout to localStorage
- [ ] **Collaborative viewing** — Multiple users watching same execution (read-only)
- [ ] **SSE streaming of brain outputs** — Watch brain write its output token-by-token during execution

---

## Feature Prioritization Matrix

| Feature | User Value | Implementation Cost | Priority |
|---------|------------|---------------------|----------|
| Auth gate | HIGH (blocking) | LOW | P1 |
| WebSocket Dispatcher (Zustand) | HIGH (enabling) | MEDIUM | P1 |
| Command Center — Bento Grid | HIGH (first impression) | MEDIUM | P1 |
| Command Center — brief submission | HIGH (core loop) | LOW | P1 |
| The Nexus — DAG with node states | HIGH (the "wow") | HIGH | P1 |
| Strategy Vault — execution list | HIGH (users need outputs) | LOW | P1 |
| Strategy Vault — output view | HIGH (core value) | MEDIUM | P1 |
| Engine Room — log viewer | MEDIUM (debugging) | MEDIUM | P1 |
| Edge animation on brain activation | MEDIUM (polish) | LOW | P2 |
| Engine Room — API keys | MEDIUM (operations) | LOW | P2 |
| Engine Room — YAML editor | MEDIUM (config) | MEDIUM | P2 |
| Brain pre-selection in command modal | MEDIUM (power users) | MEDIUM | P2 |
| Execution diff view | MEDIUM (agency use case) | HIGH | P3 |
| Execution replay / time-travel | LOW (nice to have) | HIGH | P3 |
| Brain analytics | LOW (premature) | HIGH | P3 |

---

## Competitor Feature Analysis

Comparing against tools users compare to MasterMind visually.

| Feature | LangSmith Studio | Prefect UI | Airflow UI | Our War Room |
|---------|-----------------|------------|------------|--------------|
| Command input modal | ❌ None | ❌ None | ❌ None | ✅ Raycast-style cmdk |
| Bento Grid status tiles | ❌ List view | ❌ List view | ❌ Table | ✅ Magic UI animated tiles |
| DAG node illumination on events | ✅ State coloring | ✅ State coloring | ✅ State coloring | ✅ + animation (NodeStatusIndicator) |
| Real-time log stream | ✅ Yes | ✅ Yes | ⚠️ Polling | ✅ react-logviewer + WS |
| Brain output Markdown rendering | ✅ Yes | ❌ No | ❌ No | ✅ react-markdown + memoization |
| Domain-specific brain vocabulary | ❌ Generic tasks | ❌ Generic flows | ❌ Generic tasks | ✅ "Cerebros", briefs, niches |

**Key differentiator:** The command center + bento grid combination is unique to this product. Workflow orchestration tools universally use table/list views. The spatial bento layout with real-time status illumination is the visual identity of the war room.

---

## Technical Complexity Notes by Screen

### Screen complexity ranking (highest → lowest effort)

1. **The Nexus** (HIGH) — React Flow + Zustand bridge + WS events + DAG layout algorithm + edge animation. Most moving parts.
2. **WebSocket Dispatcher** (MEDIUM-HIGH) — Singleton Zustand store, reconnect logic, typed event subscriptions, cleanup on unmount. Foundation for 3 screens.
3. **Command Center** (MEDIUM) — Bento Grid layout with 24 dynamic tiles, status subscriptions per tile, command modal with cmdk.
4. **Engine Room** (MEDIUM) — react-logviewer WS integration, filter controls, Monaco editor for YAML (two independent sub-features).
5. **Strategy Vault** (LOW-MEDIUM) — Mostly data fetching + Markdown rendering. No real-time. Simplest screen.

### The Nexus — known implementation pitfalls

- **Simultaneous node updates cause freezes** — React Flow issue #4779. Fix: batch WS events in Zustand, apply in single `setNodes` call, not one call per event.
- **dagre layout must run once, not on every update** — Re-running layout resets positions; users lose context. Run on mount only, preserve positions on state changes.
- **React Flow internal `updateNodeData` vs manual `setNodes`** — In React Flow 12+, use `updateNodeData(id, data)` from `useReactFlow()` for partial updates. Faster than full `setNodes` map on every event.

### WebSocket Dispatcher — known pitfalls

- **Connection race on mount** — Multiple components mounting simultaneously all try to connect. Use a module-level singleton pattern in Zustand (connection created once, reused).
- **Stale closure in event handlers** — WS `onmessage` captures stale Zustand state. Fix: use `useStore.getState()` directly inside handlers, not `state` from `set`.
- **Cleanup on page unload vs component unmount** — Don't close the WS connection on component unmount (other components need it). Only close on explicit logout or `beforeunload`.

---

## Sources

- [React Flow State Management docs](https://reactflow.dev/learn/advanced-use/state-management) — Zustand bridge pattern, HIGH confidence
- [React Flow Node Status Indicator](https://reactflow.dev/ui/components/node-status-indicator) — Built-in status states (loading/success/error/initial), HIGH confidence
- [React Flow updateNodeData issue #4779](https://github.com/xyflow/xyflow/issues/4779) — Simultaneous update freeze, MEDIUM confidence (GitHub issue, not resolved docs)
- [Magic UI Bento Grid](https://magicui.design/docs/components/bento-grid) — Component structure and props, HIGH confidence
- [Bento Grids for AI Dashboards — Baltech](https://baltech.in/blog/bento-grids-for-ai-dashboards/) — Tile hierarchy patterns, MEDIUM confidence
- [Vercel Streamdown](https://github.com/vercel/streamdown) — Streaming Markdown renderer, HIGH confidence
- [react-logviewer (melloware)](https://github.com/melloware/react-logviewer) — Log viewer with WS + ANSI, HIGH confidence
- [TanStack Virtual comparison](https://borstch.com/blog/development/comparing-tanstack-virtual-with-react-window-which-one-should-you-choose) — Virtualization library comparison, MEDIUM confidence
- [shadcn Command component](https://ui.shadcn.com/docs/components/radix/command) — cmdk integration, HIGH confidence
- [Vercel AI SDK — Markdown chatbot with memoization](https://ai-sdk.dev/cookbook/next/markdown-chatbot-with-memoization) — Memoized Markdown rendering pattern, HIGH confidence
- [Command Palette UX patterns](https://uxpatterns.dev/patterns/advanced/command-palette) — Command palette design principles, MEDIUM confidence
- [LangGraph Studio visualization](https://mem0.ai/blog/visual-ai-agent-debugging-langgraph-studio) — Competitor DAG visualization patterns, MEDIUM confidence

---

*Feature research for: MasterMind War Room Frontend (v2.1)*
*Researched: 2026-03-19*
*Confidence: HIGH — all major claims verified against official documentation or current sources*
