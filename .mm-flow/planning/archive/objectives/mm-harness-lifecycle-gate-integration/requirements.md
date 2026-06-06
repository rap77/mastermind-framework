# Requirements — mm-harness-lifecycle-gate-integration

## Problem / Purpose

The harness now has the pieces for the intake path:

- `context-to-canonical`
- `objective-context-check`
- `discover`

But those pieces are not yet integrated deeply enough into the lifecycle.
Today the new gate exists, yet the surrounding workflow can still:

- skip it silently
- recommend commands that bypass it
- fail to tell another model whether an objective has already passed it

This objective strengthens the lifecycle so the gate becomes part of the
operational path, not just an available standalone command.

## Stakeholders / Users

- **Primary:** maintainers evolving MM into a stronger harness
- **Secondary:** operators using Claude, Codex, or shell to open new objectives
- **Tertiary:** downstream tools and future automation that need a clear gate status

## Scope

### In Scope

- Integrate `objective-context-check` into the lifecycle guidance around:
  - `context-to-canonical`
  - `discover --roadmap --existing`
  - objective creation flows
  - docs / briefs / handoffs
- Define how the system records or infers whether a canonical objective has
  passed the gate
- Persist the gate verdict in a lightweight sidecar artifact adjacent to the
  canonical objective so another model/operator can inspect status without
  replaying chat context
- Decide and implement the minimal enforcement policy for this phase:
  - recommendation only
  - warning
  - blocking in selected paths
- Ensure the lifecycle reports clear next steps when:
  - gate has not run
  - gate failed
  - gate needs input
  - gate passed
- Keep compatibility with the current objective-package flow

### Out of Scope

- Do not redesign canonical markdown/report formats again
- Do not replace `discover` with `objective-context-check`
- Do not build a full persistent state machine for every canonical doc unless a
  small artifact is enough
- Do not introduce runtime-specific UX as the primary enforcement mechanism

## Non-negotiables

- The gate remains model/runtime agnostic
- `.mm-flow/commands/mm/*.py` remains the source of truth
- The lifecycle must not give contradictory guidance about whether the gate is
  optional or required
- Any enforcement introduced in this objective must be incremental and safe for
  existing projects
- Another model or operator must be able to tell from artifacts whether the gate
  is still pending
- If a canonical objective exists for the same slug, `discover --existing
  --objective <slug>` must not materialize a package unless the gate artifact is
  present and `PASSED`

## Decisions Already Implied

- The active harness flow should now be treated as:
  - `context-to-canonical`
  - `objective-context-check`
  - `discover`
  - `discover-contract-check`
  - `complete-task`
  - `archive-objective`
- This objective should likely begin with **warnings / guided enforcement**
  rather than a hard break everywhere
- Gate outcome must become visible in lifecycle artifacts, not only terminal output
- The first persisted artifact for this phase is
  `docs/canonical/objective-specs/<slug>.gate.json`
- For this phase, gate freshness is determined by artifact timestamps: if the
  canonical markdown/report is newer than the gate artifact, the lifecycle must
  treat the gate as not yet rerun

## Objective-level Acceptance Criteria

- [ ] lifecycle docs and guidance reflect `objective-context-check` as a real gate
- [ ] at least one lifecycle path warns or blocks when the gate has not been satisfied
- [ ] gate status is inferable from artifacts or deterministic checks
- [ ] the user/operator gets clear next-step guidance for `PASSED|FAILED|NEEDS_INPUT|not-yet-run`
- [ ] compatibility with the current objective execution flow is preserved
