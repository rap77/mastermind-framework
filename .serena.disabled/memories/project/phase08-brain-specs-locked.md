# Phase 08: Locked Brain Specifications (2026-03-23)

Complete specification summary from 5 domain brain consultation for Phase 08 planning.

## API Contracts (Backend #5)

**GraphEdge Response:**
```typescript
{
  nodes: [
    { id: "master", type: "master" },
    { id: "niche-xyz", type: "niche_cluster", niche_id: "marketing" },
    { id: "brain-01", type: "brain_executor", parentId: "niche-xyz", niche_id: "marketing" }
  ],
  edges: [
    { source: "master", target: "niche-xyz", data: { execution_mode: "sequential" } },
    { source: "niche-xyz", target: "brain-01", data: { execution_mode: "parallel" } }
  ]
}
```

**Execution History:** cursor-based pagination, JSONB snapshots
**API Keys:** show-once, bcrypt hash, Redis revocation
**Performance:** <1s load, eager loading, gzip, RAF batching

## UX Interaction Patterns (UX #2)

- **Logs:** motion signifier (lateral slide), chromatic mapping, pin isolation
- **Scrubber:** milestone snapping, log sync (YouTube-like), replay mode visual
- **Focus:** Esc affordance (top-right corner), keyboard hint label, sidebar anti-affordance

## Design Tokens (UI #3)

- **Colors:** categorical (blue software, purple marketing), via icons
- **Animations:** 0.5s pulse (cubic-bezier), dotted borders, grayscale ghost
- **Accessibility:** 4.5:1 contrast minimum, 44px hitbox (mobile)

## Frontend Architecture (Frontend #4)

- **Sub-graphs:** `extent: 'parent'`, manual expand, prevent thrash
- **Performance:** Web Workers for dagre <100ms, viewport-only rendering
- **Components:** separate BrainNode/NicheClusterNode, ReplayNexus dedicated
- **State:** useReplayStore, React 19 useTransition for smoothness

## QA Benchmarks (QA #6)

- 50-node DAG <100ms
- Filter <50ms
- Snapshot jump <150ms
- Focus toggle <16ms (60fps)
- E2E: incident simulation, CRUD, idempotence

## Sequencing

1. **08-01 (CRITICAL):** Backend DAG enhancement (provides data for 08-02/03/04)
2. **08-02:** Strategy Vault (uses 08-01 graph data)
3. **08-03:** Engine Room Logs (independent, uses WS)
4. **08-04:** Focus Mode (integrates 08-02/03)

## Deferred to v2.1.1

- Engine Room (API keys + YAML viewer) — lower priority CRUD, can defer if timeline tight
- Animated DAG replay (prefer Snapshot Scrubbing milestone-based approach)
- Heatmap/analytics on brain usage (requires historical metrics)
