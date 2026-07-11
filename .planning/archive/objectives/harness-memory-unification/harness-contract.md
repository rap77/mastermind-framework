# Harness Contract — harness-memory-unification

## Purpose
Define the execution contract for the reusable harness core so the runtime can select, run, verify, review, and recover without ad hoc decisions.

## Core Runtime Elements
- `HarnessCore`
- `LoopSelector`
- `ExecutionEnvelope`
- `CapabilityRegistry`
- `VerificationHarness`
- `ReviewHarness`
- `RecoveryHarness`

## Responsibilities
- select the smallest safe loop for the current work item
- resolve required capabilities before execution
- execute verification, review, and recovery deterministically
- emit structured run results
- preserve loop state boundaries

## Inputs
- project manifest
- active objective or slice
- operational context from `.planning`
- available capabilities and policies
- current memory state

## Outputs
- selected loop
- selected capabilities
- execution envelope
- verification result
- review result, if needed
- recovery decision, if needed
- final run summary

## Invariants
- one active objective per run
- deterministic loop selection for the same context
- no silent fallback when context is ambiguous
- no direct coupling to a single repo layout
- verification and review remain separate decisions

## Loop Rules
- choose the smallest loop set that can safely complete the objective
- emit the reason for the chosen loop
- require explicit failure handling when the objective cannot be classified

## Envelope Contract
- `status`
- `summary`
- `artifacts`
- `risks`
- `next_actions`
- `verification`
- `recovery`

## Success Criteria
- the harness can decide what to run without human re-interpretation
- the harness can explain why it selected a loop
- the harness can resume from persisted state
- the harness can expose a canonical run envelope to the bridge and memory
