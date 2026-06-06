# Design — mm-harness-exception-expiration-metadata

## Architecture / Boundaries

This objective is policy-first. It defines how active-objective exceptions stop
applying in a machine-checkable way.

Primary touchpoints:

- `.mm-flow/planning/active-objective-exceptions.json`
- `.mm-flow/commands/mm/active-objective-state.py`
- planning/handoff guidance for exception authoring

## Technical Approach

### 1. Start from the current exception artifact

Current behavior:

- exception entries include `expires_when` as plain-language guidance
- runtime does not evaluate expiration semantics
- stale exceptions require manual cleanup

### 2. Choose one machine-checkable field

Phase 1 chooses one required machine field per exception entry:

- `expires_at_utc`

Why this option wins:

- deterministic and easy to compare in runtime
- no dependency on objective archive events or a richer state engine
- keeps the schema small while preserving `expires_when` for operator context

### 3. Runtime interpretation rule

Shared helpers should evaluate exception validity in this order:

1. schema validation, including `expires_at_utc`
2. UTC timestamp parsing
3. expiration check (`now < expires_at_utc`)
4. objective slug match + command/bundle scope match

If expiration metadata is missing, malformed, or expired, the exception must not match.

### 4. Smallest implementation surface

- `active-objective-state.py`
  - validate and normalize `expires_at_utc`
  - compare current UTC time against the parsed timestamp
- `.mm-flow/planning/active-objective-exceptions.json`
  - add `expires_at_utc` to the repo's bundle-aware example artifact
- tests
  - write active, expired, and invalid exception entries explicitly

## Dependencies

- archived objective `mm-harness-exception-command-bundle-metadata`
- current active-objective exception artifact contract
- current runtime exception matching helpers

## Validation Strategy

```bash
python3 .mm-flow/commands/mm/discover-contract-check.py --objective mm-harness-exception-expiration-metadata
python3 -m unittest tests.unit.test_mm_discover_workflow
```

T1 should make explicit:

- the chosen machine field
- how runtime treats missing/invalid/expired timestamps
- how operators still interpret the human-readable `expires_when`

## Important Tradeoffs

- **Determinism vs flexibility:** timestamps are simple and deterministic, but less expressive than state-based rules
- **Human guidance vs machine policy:** keeping both helps operators, but increases authoring surface
