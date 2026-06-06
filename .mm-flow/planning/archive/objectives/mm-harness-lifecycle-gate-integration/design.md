# Design — mm-harness-lifecycle-gate-integration

## Architecture / Boundaries

This objective does **not** create a new gate. It integrates an existing one
into the operational lifecycle.

### 1. Upstream intake flow

Current components:

- `.mm-flow/commands/mm/context-to-canonical-handler.py`
- `.mm-flow/commands/mm/objective-context-check-handler.py`
- `.mm-flow/commands/mm/discover-handler.py`

### 2. Integration surfaces

Likely touchpoints:

- `context-to-canonical` docs and next-command guidance
- `discover-handler.py` lifecycle messaging and/or objective ingestion rules
- README and handoff guidance
- possibly a lightweight artifact or deterministic rule to infer gate status

### 3. Enforcement boundary

This objective should define where enforcement belongs first.

Recommended first phase:

- **recommend or warn** in broad lifecycle paths
- **block** only where the gate status is directly relevant and deterministically
  checkable

## Technical Approach

### Step 1 — define gate-status inference

The lifecycle needs a deterministic answer to:

> Has this canonical objective passed `objective-context-check` yet?

Candidate minimal strategies:

1. infer from a sidecar artifact written by the gate
2. infer from deterministic rerun of the gate
3. infer from a status field added to the intake report or adjacent metadata

Chosen approach for this phase:

- `objective-context-check` writes
  `docs/canonical/objective-specs/<slug>.gate.json`
- the artifact stores `status`, `next_command`, and file references
- if the canonical markdown or intake report is newer than the gate artifact,
  the lifecycle treats the gate as stale / not rerun yet

### Step 2 — integrate guidance into lifecycle entrypoints

Likely first entrypoints:

- `context-to-canonical` next-command output
- `discover --roadmap --existing`
- any place that recommends activating/materializing a fresh canonical objective

The lifecycle should no longer imply:

- canonical objective → discover directly

without surfacing:

- run `objective-context-check` first

Concrete first integrations:

- `context-to-canonical --type objective` must point the operator to
  `/mm:objective-context-check --objective <slug>`
- `discover --existing --objective <slug>` checks the persisted gate artifact
  when a canonical objective exists for the same slug

### Step 3 — minimal enforcement policy

Expected first implementation:

- if a canonical objective has unresolved gate status:
  - stop materialization with explicit status and next command
- if gate status is known `NEEDS_INPUT` or `FAILED`:
  - do not pretend the objective is ready
- only introduce hard blocking where it is low-risk and unambiguous

Phase-1 enforcement boundary:

- objective discover path:
  - `NOT_RUN` / stale artifact -> block with rerun guidance
  - `NEEDS_INPUT` -> block with input guidance
  - `FAILED` -> block with repair/rerun guidance
  - `PASSED` -> continue
- roadmap generation remains guidance-only in this phase

## Dependencies

- `context-to-canonical-handler.py`
- `objective-context-check-handler.py`
- `discover-handler.py`
- existing canonical objective markdown/report convention

## Validation Strategy

Concrete checks should include:

```bash
python3 -m unittest tests.unit.test_mm_discover_workflow
python3 .mm-flow/commands/mm/objective-context-check-handler.py --help
python3 .mm-flow/commands/mm/discover-handler.py --roadmap --existing
```

Need tests for at least:

- lifecycle guidance when gate has not run
- lifecycle behavior when gate says `NEEDS_INPUT`
- compatibility with existing objective execution flow
- persisted gate artifact after `PASSED`
- context-to-canonical objective output points to the gate instead of discover

## Important Tradeoffs

- **Warning vs blocking:** warnings are safer; blocking is stronger but riskier
- **Persisted gate status vs recomputation:** persisted status is clearer; recomputation is simpler
- **Discover integration vs adapter-only messaging:** core integration is more robust, but must be incremental

## Files / Areas Likely Touched

- `.mm-flow/commands/mm/discover-handler.py`
- `.mm-flow/commands/mm/context-to-canonical-handler.py` or docs if next-step guidance changes
- `.mm-flow/commands/mm/objective-context-check-handler.py` (only if status artifact needs extension)
- `.mm-flow/README.md`
- tests around objective lifecycle guidance
