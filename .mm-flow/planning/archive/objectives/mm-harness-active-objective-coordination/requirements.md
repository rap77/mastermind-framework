# Requirements — mm-harness-active-objective-coordination

## Problem / Purpose

The harness now has stronger lifecycle gates, but active objective coordination
is still inconsistent. During the last slices we observed that:

- `/mm:activate-next-objective` refuses to open a new objective when another
  directory already exists under `.mm-flow/planning/changes/`
- `discover --existing --objective <slug>` can still materialize a new package
  even when another active objective directory already exists
- root handoff and queue guidance can imply a different “current objective” than
  what the filesystem actually contains

This objective aligns objective creation/activation behavior so the harness
communicates a coherent single-writer policy or an explicit multi-active policy.

## Stakeholders / Users

- **Primary:** maintainers evolving the MasterMind harness
- **Secondary:** operators opening or resuming objectives from shell, Codex, or Claude
- **Tertiary:** future automation that assumes active objective state is coherent

## Scope

### In Scope

- Define the intended policy for multiple directories under
  `.mm-flow/planning/changes/`
- Make objective creation/activation surfaces enforce or clearly surface that
  policy consistently
- Ensure another model/operator can tell which objective is truly active and why
  a new one cannot be opened
- Keep compatibility with archived objectives and existing roadmap artifacts

### Out of Scope

- Do not redesign the entire roadmap system
- Do not add a global database/state machine for active objectives
- Do not remove archived multi-objective history
- Do not change task execution semantics beyond what is needed for active
  objective coordination

## Non-negotiables

- `.mm-flow/commands/mm/*.py` remains the source of truth
- Active-objective guidance must not contradict filesystem reality
- Enforcement should be incremental and deterministic
- Another model/operator must be able to recover using artifacts, not chat memory

## Decisions Already Implied

- The current behavior is inconsistent enough to justify a dedicated harness fix
- The next step should likely prefer one explicit policy:
  - **single active objective by default**, or
  - **multiple active objectives allowed only with explicit coordination metadata**
- `activate-next-objective` already behaves closer to a single-active-objective
  policy; discover/objective packaging should not silently diverge

## Objective-level Acceptance Criteria

- [ ] the policy for active objective coordination is explicit
- [ ] objective creation and activation surfaces behave consistently with that policy
- [ ] filesystem artifacts and handoff guidance identify the true active objective set
- [ ] targeted validation proves the coordination behavior and avoids ambiguous operator guidance
