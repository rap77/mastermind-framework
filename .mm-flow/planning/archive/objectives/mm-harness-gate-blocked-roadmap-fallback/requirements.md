# Requirements — mm-harness-gate-blocked-roadmap-fallback

## Problem / Purpose

The roadmap now reranks toward gate-ready objectives when possible. The
remaining gap is what to do when **every** dependency-ready candidate is still
gate-blocked.

Without explicit fallback guidance, the roadmap can still look deceptively
actionable:

- it recommends an objective
- activation blocks later
- the operator has to infer that no directly activatable option exists

This objective makes that all-blocked state explicit in roadmap outputs while
keeping activation safely blocked.

## Stakeholders / Users

- **Primary:** maintainers evolving the MasterMind harness
- **Secondary:** operators reading roadmap output and using
  `/mm:activate-next-objective`
- **Tertiary:** future automation that needs to distinguish “recommended and
  ready” from “recommended fallback but blocked”

## Scope

### In Scope

- mark when `recommended_next` is only a blocked fallback
- emit clear roadmap/handoff guidance for the all-blocked case
- preserve activation blocking for the fallback recommendation

### Out of Scope

- do not automatically choose a non-ready objective outside dependency rules
- do not auto-run `objective-context-check`
- do not redesign the full roadmap artifact schema beyond minimal fallback fields

## Non-negotiables

- blocked fallback recommendations must be explicit, not implicit
- activation remains blocked until gate conditions are satisfied
- roadmap still chooses deterministically among blocked candidates

## Decisions Already Implied

- if at least one gate-ready candidate exists, it should still win
- only when every dependency-ready candidate is blocked should the roadmap mark
  a blocked fallback
- blocked fallback is a recommendation-quality signal, not permission to bypass
  the gate

## Objective-level Acceptance Criteria

- [x] roadmap artifacts mark when `recommended_next` is a blocked fallback
- [x] handoff/guidance explain that all dependency-ready candidates are blocked
- [x] activation remains blocked for the fallback recommendation
