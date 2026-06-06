# Design — mm-harness-multi-active-exception-metadata

## Architecture / Boundaries

This objective is about policy and artifact design first, not broad execution
changes.

Likely touchpoints:

- `.mm-flow/commands/mm/active-objective-state.py`
- `.mm-flow/commands/mm/discover-handler.py`
- `.mm-flow/commands/mm/activate-next-objective-handler.py`
- planning artifacts / handoff metadata

## Technical Approach

### 1. Keep single-active as baseline

The current default remains correct for safety and determinism.

### 2. Use one root-level exception artifact

Phase 1 chooses a single root planning artifact:

- `.mm-flow/planning/active-objective-exceptions.json`

Why this option wins over the other candidates:

- one inspection point is simpler for operators than checking multiple objective packages
- it avoids asymmetric per-objective compatibility flags
- it keeps phase-1 logic narrow: exact-set matching plus command scoping

### 3. Exception entries model allowed coexistence directly

Each exception entry should answer all operator questions without consulting chat
history:

- which objectives may coexist?
- why is coexistence allowed?
- which commands honor it?
- when does it stop applying?

The chosen minimal entry shape is:

```json
{
  "id": "pair-discover-docs-and-handler-followup",
  "objective_slugs": ["objective-a", "objective-b"],
  "reason": "Why the pair is intentionally active together.",
  "commands": ["discover --existing --objective", "activate-next-objective"],
  "expires_when": "Archive either listed objective or remove the exception when the coordination window closes."
}
```

### 4. Recognition rules stay narrow

Future handler logic should treat the artifact conservatively:

- missing file => no exception
- invalid JSON => no exception
- slug set mismatch => no exception
- command not listed => no exception
- exact match => allow the named coexistence set only

That keeps the failure mode aligned with the current single-active default.

### 5. Canonical parser ownership

The parser for `active-objective-exceptions.json` should live in:

- `.mm-flow/commands/mm/active-objective-state.py`

Why:

- that module already owns coordination helpers for active-objective decisions
- `discover-handler.py` and `activate-next-objective-handler.py` can both import the same deterministic interpretation
- it avoids duplicating exception parsing in multiple entrypoints

Phase-1 helper responsibilities should be:

- load and validate the root exception artifact
- normalize slug sets and command names
- answer whether a requested coexistence set is allowed for a given command
- return matched exception metadata for operator-visible explanations

### 6. Command touchpoints to honor the contract

The smallest coherent touchpoints are:

1. `discover --existing --objective <slug>`
   - before blocking on another active objective, ask `active-objective-state.py`
     whether the current active slug set plus requested slug is explicitly allowed
   - if allowed, continue and surface which exception matched
   - if not allowed, preserve current blocking behavior

2. `activate-next-objective`
   - before failing on an existing active objective package, ask the same helper
     whether the active slug set plus recommended slug is explicitly allowed
   - if allowed, continue and surface the matched exception metadata
   - if not allowed, preserve current blocking behavior

3. roadmap generation stays unchanged in phase 1
   - roadmap can mention exception capability later, but it should not start
     recommending multi-active states before runtime entrypoints honor the artifact

### 7. Operator-visible explanation path

When an exception matches, the honoring command should expose:

- `STATUS: PASSED` or the normal success path for that command
- `ACTIVE_OBJECTIVE_EXCEPTION: <id>`
- `ALLOWED_OBJECTIVES: <comma-separated slugs>`
- one line with the `reason`
- one line with `expires_when`

When no exception matches, the current blocking text should remain the fallback.

### 8. Deferred follow-up gaps recorded now

These are intentionally **not** solved in this objective, but must remain visible
for follow-up work:

- **Machine-checkable expiration:** `expires_when` is plain text in phase 1; a later objective may add structured expiration rules.
- **Richer scope than exact slug sets:** phase 1 only supports explicit named sets; broader patterns would need stronger safety rules.
- **Roadmap awareness of exceptions:** roadmap should stay conservative until runtime entrypoints can honor exceptions safely.

## Dependencies

- current single-active coordination behavior
- planning/handoff artifact conventions
- ability to read root planning artifacts before deciding whether another active objective blocks progression

## Validation Strategy

Concrete checks for T1/T2/T3 stay lightweight:

```bash
python3 .mm-flow/commands/mm/discover-contract-check.py --objective mm-harness-multi-active-exception-metadata
```

T2 is complete when:

- parser ownership is explicit
- command touchpoints are explicit
- operator explanation output is explicit
- deferred sub-gaps are recorded for later follow-up

## Important Tradeoffs

- **Flexibility vs safety:** exceptions improve advanced workflows but increase coordination complexity
- **Root artifact vs local flags:** a root artifact is less flexible than per-objective metadata, but much clearer for operators in phase 1
- **Plain-language expiration vs computed TTL:** plain-language `expires_when` is easier to adopt first; a machine-checked expiration is a later gap

## Files / Areas Likely Touched

- `.mm-flow/planning/changes/mm-harness-multi-active-exception-metadata/*`
- possibly `.mm-flow/README.md` and coordination handlers in later implementation
