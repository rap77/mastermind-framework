# Requirements — mm-harness-multi-active-exception-metadata

## Problem / Purpose

The harness now defaults to one active objective at a time and explains blocked
fallbacks better. The next remaining coordination gap is whether the system can
support **intentional multi-active exceptions** without ambiguity.

Right now the harness only has:

- strict single-active behavior by default
- no explicit artifact for saying multiple active objectives are intentionally allowed
- no deterministic metadata for another model/operator to understand such an exception

This objective defines the smallest safe metadata contract for that exception
path before any handler behavior changes.

## Stakeholders / Users

- **Primary:** maintainers evolving advanced harness workflows
- **Secondary:** operators who may need controlled parallel objective work
- **Tertiary:** future automation that must distinguish default single-active from approved exceptions

## Scope

### In Scope

- define the default rule when no exception artifact exists
- choose one canonical artifact path for intentional multi-active exceptions
- define the minimum required fields another model/operator must be able to read
- define the conditions under which an exception stops applying
- define which lifecycle entrypoints must eventually honor the artifact

### Out of Scope

- do not enable unrestricted parallel objectives by default
- do not redesign task execution semantics broadly
- do not weaken existing single-active safety without explicit exception evidence
- do not implement handler-side recognition until the contract is explicit

## Non-negotiables

- single-active remains the default policy
- absence of exception metadata means normal blocking behavior stays in place
- any exception must be explicit, deterministic, and artifact-visible
- another model/operator must be able to tell which objectives may coexist and why
- the exception must have a clear stop condition so stale approvals do not linger forever

## Decisions Already Implied

- the next useful evolution after better blocked-queue guidance is controlled exception handling, not loosening policy silently
- exception metadata should live under `.mm-flow/planning/`, not in chat memory
- one root-level artifact is safer than per-objective ad hoc flags for phase 1 because it gives operators a single place to inspect

## Explicit Contract Chosen In T1

### Canonical artifact path

- `.mm-flow/planning/active-objective-exceptions.json`

### Default behavior

- if the file does not exist, is invalid, or contains no active exception that matches the requested coexistence set, the harness preserves the current single-active blocking behavior

### Minimum artifact shape

```json
{
  "version": 1,
  "exceptions": [
    {
      "id": "pair-discover-docs-and-handler-followup",
      "objective_slugs": [
        "mm-harness-multi-active-exception-metadata",
        "mm-harness-followup-objective"
      ],
      "reason": "Both objectives are intentionally coordinated and may remain active together.",
      "commands": [
        "discover --existing --objective",
        "activate-next-objective"
      ],
      "expires_when": "Archive either listed objective or remove the exception after the coordination window closes."
    }
  ]
}
```

### Field requirements

- `version`: integer schema version; required
- `exceptions`: list of exception entries; required
- `id`: stable searchable identifier for operator discussion and debugging; required
- `objective_slugs`: exact list of allowed concurrently active objective slugs; required; minimum length 2
- `reason`: human-readable explanation of why coexistence is allowed; required
- `commands`: explicit list of lifecycle entrypoints that should honor the exception; required
- `expires_when`: plain-language stop condition; required

### Interpretation rules

- objective coexistence is allowed only for the exact slug set named in one exception entry
- the artifact grants an exception only to commands explicitly listed in `commands`
- exceptions are opt-in and narrow; they do not imply general multi-active mode
- if multiple exception entries exist, each is evaluated independently

## Objective-level Acceptance Criteria

- [x] a deterministic exception model is defined
- [x] default single-active behavior remains preserved
- [x] the exception artifact path, required fields, and stop condition are explicit enough to implement safely
