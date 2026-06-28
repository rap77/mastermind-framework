# Planning Bridge Contract

## Purpose
Define how `.planning` communicates with the harness without becoming the
runtime itself.

## Bridge Responsibilities
- read planning intent
- translate objective/task markers into harness inputs
- write structured outputs back to planning artifacts
- preserve handoff and archival traceability
- pass project manifest and memory context into the runtime

## Inputs
- `.planning` objective or handoff context
- current status files
- active task or objective metadata
- project manifest
- memory snapshot
- harness capabilities

## Outputs
- harness-ready execution request
- updated status summary
- structured handoff note
- archive-ready completion record
- explicit bridge warnings for mismatches

## Invariants
- `.planning` remains the operational surface, not the execution engine
- the bridge must not destroy historical handoffs
- bridge output must be traceable back to the original planning intent
- the bridge must not invent hidden goals

## Translation Rules
- convert objective data into objective name, current UOW, constraints, expected outputs, and required checks
- convert harness results into updated status, summary, next action, verification outcome, and recovery notes

## Conflict Rules
- if `.planning` lacks a clear objective, stop and flag the bridge as incomplete
- if planning and memory disagree, prefer the explicit project manifest and record the mismatch
- if the handoff is stale or incomplete, mark it for review instead of silently continuing

## Success Criteria
- `.planning` can trigger a harness run
- harness results can be written back to planning artifacts
- the same bridge can support future projects through adapters
