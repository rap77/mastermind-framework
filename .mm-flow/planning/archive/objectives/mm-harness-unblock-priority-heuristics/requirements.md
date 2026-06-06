# Requirements — mm-harness-unblock-priority-heuristics

## Problem / Purpose

The roadmap now handles three states better:

- gate-ready recommendation
- gate-aware reranking
- explicit blocked-fallback when all dependency-ready candidates are blocked

The remaining gap is decision quality inside the blocked queue:

- when all dependency-ready candidates are gate-blocked, the harness still uses
  raw objective priority as the implied “what should I unblock first?” signal
- that may be acceptable, but it is not explicit, inspectable, or justified as
  an unblocking heuristic

This objective turns “which blocked objective should be unblocked first?” into
an explicit, deterministic heuristic instead of an accidental side-effect of
priority ordering.

## Stakeholders / Users

- **Primary:** maintainers evolving the MasterMind harness
- **Secondary:** operators facing an all-blocked queue and choosing what to
  unblock first
- **Tertiary:** future automation that needs structured unblocking guidance

## Scope

### In Scope

- define a deterministic heuristic for blocked-candidate recommendation
- expose unblock-priority reasoning in roadmap/handoff artifacts
- preserve the current gate enforcement boundaries

### Out of Scope

- do not auto-resolve blocked objectives
- do not redesign the main objective priority system from scratch
- do not introduce model-judged unblock ranking in this phase

## Non-negotiables

- unblock ordering must be deterministic
- gate enforcement remains unchanged
- another model/operator must be able to see *why* a blocked objective is being
  surfaced first

## Decisions Already Implied

- blocked fallback is already explicit
- the next step is not to relax blocking, but to improve blocked-queue guidance
- existing objective priority may be one input, but should not remain an
  unspoken heuristic

## Objective-level Acceptance Criteria

- [ ] blocked fallback recommendation includes explicit unblock-priority reasoning
- [ ] roadmap/handoff artifacts expose that reasoning deterministically
- [ ] activation/discover safety behavior remains unchanged
