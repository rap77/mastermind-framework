# Design — mm-harness-roadmap-activation-gate-awareness

## Architecture / Boundaries

This objective extends the existing gate-aware lifecycle without adding a new
gate.

Current relevant components:

- `.mm-flow/commands/mm/discover-handler.py`
- `.mm-flow/commands/mm/activate-next-objective-handler.py`
- `.mm-flow/commands/mm/objective-context-check-handler.py`
- roadmap artifacts under `.mm-flow/planning/roadmap/`

The persisted gate artifact from the previous objective remains the canonical
signal:

- `docs/canonical/objective-specs/<slug>.gate.json`

## Technical Approach

### 1. Reuse existing gate inference

Do not reimplement gate validation rules in multiple places.

The queue/activation layer should reuse the same deterministic inference already
used by direct objective discover:

- no canonical objective → no gate preflight required
- canonical objective + no artifact / stale artifact → `NOT_RUN`
- gate artifact status `NEEDS_INPUT` → activation not ready
- gate artifact status `FAILED` → activation not ready
- gate artifact status `PASSED` → activation may continue

### 2. Surface queue-level readiness

At least one roadmap-facing artifact should expose more than raw
`recommended_next`/`ready_now`.

Candidate minimal surfaces:

1. roadmap JSON entries gain a lightweight `gate_status` field when inferable
2. root handoff mentions when the recommended objective is blocked by gate state
3. activation command prints preflight gate status before delegating to discover

Recommended phase-1 mix:

- add preflight gate-aware messaging/blocking to `activate-next-objective`
- add a lightweight gate-aware field or note to roadmap/handoff output where
  the recommended objective is discussed

### 3. Enforcement boundary

Recommended first boundary:

- roadmap generation: warning / visibility
- activate-next-objective: explicit preflight block with next command

This keeps broad roadmap generation stable while making the activation path less
surprising.

## Dependencies

- gate artifact contract from `mm-harness-lifecycle-gate-integration`
- roadmap generation in `discover-handler.py`
- activation entrypoint in `activate-next-objective-handler.py`

## Validation Strategy

Concrete checks should include:

```bash
python3 -m unittest tests.unit.test_mm_discover_workflow
python3 .mm-flow/commands/mm/discover-contract-check.py --objective mm-harness-roadmap-activation-gate-awareness
python3 .mm-flow/commands/mm/activate-next-objective-handler.py --quick
```

Need tests for at least:

- activation blocked when recommended objective has `NOT_RUN`
- activation blocked when recommended objective has `NEEDS_INPUT`
- activation still succeeds when there is no canonical objective
- roadmap/handoff output shows gate-aware guidance where relevant

## Important Tradeoffs

- **Visibility vs noise:** roadmap should surface useful readiness, not every
  internal detail
- **Blocking at activation vs roadmap time:** activation blocking is safer;
  roadmap warnings are lower-risk
- **Reuse vs duplication:** gate inference should stay centralized to avoid
  drift between discover and activation

## Files / Areas Likely Touched

- `.mm-flow/commands/mm/activate-next-objective-handler.py`
- `.mm-flow/commands/mm/discover-handler.py`
- `.mm-flow/README.md`
- `.mm-flow/planning/HANDOFF-CURRENT.md`
- tests around roadmap/activation behavior
