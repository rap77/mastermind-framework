# Phase 08: DAG Visualization Architecture

**Decision Date:** 2026-03-23
**Status:** APPROVED (architecture sound, needs UX validation, backend implementation pending)
**Depends on:** Phase 08-01 Backend DAG Enhancement

## The Decision

**What:** Nexus visualization will show dynamic task DAGs in n8n-style workflow pattern
**Why:** Scales with niche growth (50+ brains in v2.2), shows actual execution context, familiar UX
**How:** Master node → Niche cluster nodes → Brain executor nodes

## Pattern Details

### Node Hierarchy
```
Master (Task/Brief)
  ├─ Niche Cluster (Frontend)
  │   ├─ Brain Executor (specific brain working now)
  │   └─ Brain Executor
  └─ Niche Cluster (Backend)
      ├─ Brain Executor
      └─ Brain Executor
```

### Execution Modes (on edges)
- **Parallel:** Nodes render vertically stacked (↓) — brains work simultaneously
- **Sequential:** Nodes render horizontally aligned (→) — brains work in sequence

### Data Requirements from Backend
```json
{
  "nodes": [
    { "id": "task-brief", "type": "master", "label": "Brief text" },
    { "id": "niche-frontend", "type": "niche_cluster", "label": "Frontend" },
    { "id": "brain-04", "type": "brain_executor", "niche": "frontend", "execution_mode": "parallel" }
  ],
  "edges": [
    { "source": "task-brief", "target": "niche-frontend" },
    { "source": "niche-frontend", "target": "brain-04", "execution_mode": "parallel" }
  ]
}
```

## Implementation Path

1. **Phase 08-01:** Backend enhancement
   - Add niche clustering to GraphEdge response
   - Add execution_mode to nodes/edges
   - Return real task DAGs (not all 24 brains)

2. **Phase 08 later:** Frontend Nexus update (if needed)
   - May just work with new data (depends on backend structure)
   - Test with real task DAG response

## Why This Works at Scale

- **v2.1:** 24 brains (7 software + 16 marketing)
- **v2.2:** 50+ brains (multiple nichos)
- **Static approach:** All 50+ always visible → cluttered, confusing
- **Dynamic approach:** Only active brains per task → clean, focused, scales infinitely

## UX Validation Pending

Needs Brain #2 (UX Research) + Brain #3 (UI Design) validation:
- Is n8n pattern familiar enough?
- How to show parallel vs sequential visually?
- Focus Mode interaction patterns?
- Performance with 50+ nodes?

Do NOT start implementation until UX approves.

## Risk Assessment

**Low risk:** Backend implementation is straightforward (add fields to response)
**Medium risk:** Frontend rendering (React Flow can handle it, but needs testing)
**Validation required:** UX approval before committing to design details
