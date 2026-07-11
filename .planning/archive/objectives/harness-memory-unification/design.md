# Design — harness-memory-unification

## Architecture / Boundaries
- Keep `apps/api/mastermind_cli/orchestrator/runtime_contracts/` as the reusable harness/runtime seam.
- Keep `apps/api/mastermind_cli/memory_layer/` as the reusable memory seam.
- Keep `.planning` as the operational input/output layer, not as the implementation layer.
- Keep adapters explicit so the harness can be reused in other repos without rewiring the core.

### Boundary map

```text
Planning Artifacts (.planning)
        │
        ▼
Planning Bridge / Adapter
        │
        ▼
Harness Runtime Contract  ─── Memory Contract
        │                         │
        └──────────────┬──────────┘
                       ▼
               Execution + Memory State
```

## Technical Approach
### 1. Manifest-first activation
- Define the project manifest before expanding implementation slices.
- Make the active objective and source-of-truth split explicit.

### 2. Contract-first decomposition
- Split harness, memory, and planning bridge into separate contracts.
- Keep each contract small enough that downstream code can depend on it without guessing.

### 3. Additive bridge
- Translate `.planning` into typed inputs/outputs.
- Preserve historical artifacts; do not rewrite the entire planning tree.

### 4. Explicit adapter boundary
- Keep repo-specific routing and path resolution outside the reusable core.
- Put `.planning` file reading/writing and project-detection concerns behind the adapter.
- Let the bridge consume structured inputs rather than raw filesystem quirks.

## Dependencies
- `aidlc-docs/inception/plans/harness-memory-roadmap.md`
- `aidlc-docs/inception/plans/project-manifest.md`
- existing runtime contract work in `apps/api/mastermind_cli/orchestrator/runtime_contracts/`

## Validation Strategy
- Validate the package structure before implementation.
- Keep later implementation slices backed by targeted API/unit tests.
- Refresh handoff state after each slice.

## Important Tradeoffs
- Prefer a narrow, explicit contract surface over a large flexible abstraction.
- Prefer incremental bridge compatibility over a full workflow migration.
- Keep memory and harness reusable independently even if the first integration is paired.

## Context Notes
- The roadmap’s first execution step is the project manifest.
- The objective should be approached as a platform foundation, not as another isolated feature.
