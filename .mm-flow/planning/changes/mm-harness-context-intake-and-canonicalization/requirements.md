# Requirements — mm-harness-context-intake-and-canonicalization

## Problem / Purpose

`context-to-canonical` already exists, but it is still too lightweight to be the
reliable intake layer of the harness. Today it can generate a canonical
document, but it does **not** yet provide a strong contract for:

- the structured input it accepts
- the evidence it gathers from the repo
- how it reports confidence and context gaps
- how it escalates to structured user questions when context is insufficient
- how downstream discovery can tell whether the generated canonical objective is
  ready to materialize into an execution package

This objective strengthens that intake layer without replacing the existing MM
flow.

## Stakeholders / Users

- **Primary:** maintainers evolving MM as a model-agnostic harness
- **Secondary:** human operators using Claude, Codex, or shell workflows
- **Tertiary:** downstream handlers like `discover`, `discover-contract-check`,
  and future intake-validation gates

## Scope

### In Scope

- Define a **structured intake contract** for `context-to-canonical`
- Define a **structured output contract** for canonical generation
- Improve `context-to-canonical` so it can explicitly classify intent such as:
  - `feature`
  - `bugfix`
  - `refactor`
  - `capability`
- Add a machine-readable report alongside the markdown canonical output
- Surface:
  - evidence sources
  - inferred assumptions
  - missing context
  - confidence level
- Introduce a structured interview mode for cases where repo evidence is not
  enough
- Ensure the strengthened output is usable as the future upstream contract for
  the planned `objective-context-check` gate

### Out of Scope

- Do not implement the full `objective-context-check` command in this objective
- Do not redesign the whole `discover` pipeline
- Do not rewrite unrelated canonical docs or archived planning material
- Do not add runtime-specific slash-command features as the primary solution

## Non-negotiables

- `.mm-flow/commands/mm/*.py` remains the source of truth
- The intake layer must stay model/runtime agnostic
- Canonical generation must distinguish between:
  - evidence from the repo
  - inferred assumptions
  - unanswered questions
- The flow must degrade safely: if context is insufficient, it should ask
  structured questions rather than fabricate certainty
- The resulting contracts must be usable by another model or a human operator
  without chat-memory dependency

## Decisions Already Implied

- `context-to-canonical` complements the existing flow; it does not replace
  `discover`
- The future harness flow remains:
  - `context-to-canonical`
  - `objective-context-check` *(planned next gate)*
  - `discover`
  - `discover-contract-check`
  - `complete-task`
  - `archive-objective`
- The current objective should make that future gate easier to implement by
  standardizing the intake/output contracts now

## Objective-level Acceptance Criteria

- [ ] `context-to-canonical` has an explicit structured input contract
- [ ] canonical generation emits both markdown and a structured machine-readable
      report
- [ ] the report distinguishes evidence, assumptions, gaps, and confidence
- [ ] there is a structured interview path for insufficient-context cases
- [ ] the package clearly explains how this work feeds the future
      `objective-context-check` gate
- [ ] validation commands are concrete enough for another model to run
