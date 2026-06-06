# Design — mm-harness-exception-authoring-drift-reduction

## Architecture / Boundaries

This objective is policy-first. It defines how to reduce manual drift in
exception authoring while keeping runtime semantics deterministic.

Primary touchpoints:

- `.mm-flow/planning/active-objective-exceptions.json`
- `.mm-flow/planning/active-objective-command-bundles.json`
- a dedicated validation helper under `.mm-flow/commands/mm/`
- planning/handoff guidance for authoring

## Technical Approach

### 1. Start from the current authoring pain

Current behavior:

- exception entries require both `expires_when` and `expires_at_utc`
- command relationships may also depend on a separate bundle artifact
- operators can accidentally keep human and machine fields inconsistent

### 2. Choose validation + canonical phrasing

Phase 1 chooses the smallest safe change:

- no new generation workflow
- no hidden templating engine
- one validator script plus one canonical `expires_when` prefix rule

Canonical human field form:

- `Expires at <expires_at_utc> — <plain-language context>`

This keeps the machine timestamp visible directly in the human field, reducing drift while preserving readability.

### 3. Smallest implementation surface

- add a validation helper script, for example:
  - `.mm-flow/commands/mm/validate-active-objective-exceptions.py`
- validate:
  - exception artifact structure
  - `expires_at_utc` parseability
  - `expires_when` prefix consistency
  - command-bundle artifact structure when present
- update the repo example artifact to the canonical `expires_when` form
- update handoff/docs to recommend running the validator after editing exception artifacts

### 4. Why this is the smallest safe step

- it reduces the highest-frequency drift without introducing a new authoring toolchain
- it keeps the true machine policy explicit in the artifact itself
- it does not change runtime matching semantics

## Dependencies

- archived objective `mm-harness-exception-expiration-metadata`
- current exception and command-bundle artifacts
- current runtime fail-closed matching behavior

## Validation Strategy

```bash
python3 .mm-flow/commands/mm/discover-contract-check.py --objective mm-harness-exception-authoring-drift-reduction
python3 .mm-flow/commands/mm/validate-active-objective-exceptions.py
```

T1 should make explicit:

- the chosen drift source reduced first (`expires_when` vs `expires_at_utc`)
- the canonical human-field format
- why validation is safer than generation for phase 1

## Important Tradeoffs

- **Ergonomics vs transparency:** validation is less magical and keeps the policy visible, but requires operators to fix issues manually
- **Validation vs generation:** validation is the smaller safe step; generation can be a later gap if drift remains costly
