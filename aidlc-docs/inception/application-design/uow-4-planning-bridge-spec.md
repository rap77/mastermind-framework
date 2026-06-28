# UOW-4 Functional Spec — Planning Bridge

## Purpose
Define the contract that translates `.planning` intent into harness input and
writes structured harness output back into planning artifacts.

## Problem Statement
The operational layer (`.planning`) and the execution layer (harness + memory)
must communicate without becoming the same system. Without a bridge, planning
remains manual; with a weak bridge, state drifts and gets reinterpreted.

## Bridge Responsibilities

- read objective and task state from `.planning`
- convert planning intent into harness-ready input
- pass project manifest and memory context to the harness
- write structured outputs back to planning artifacts
- preserve handoff and archive traceability

## Required Inputs

| Input | Source | Meaning |
|---|---|---|
| `ObjectiveState` | `.planning` | current work item and status |
| `HandoffState` | `.planning` | continuation context |
| `ProjectManifest` | UOW-1 | source-of-truth and scope rules |
| `MemorySnapshot` | UOW-3 | current resumable context |
| `HarnessCapabilities` | UOW-2 | what the runtime can execute |

## Required Outputs

| Output | Meaning |
|---|---|
| `HarnessRequest` | normalized input for runtime execution |
| `StructuredStatus` | machine-readable status update |
| `HandoffRecord` | resumable trace of the transition |
| `ArchiveRecord` | completion artifact for finished work |
| `BridgeWarnings` | explicit mismatches or missing data |

## Bridge Rules

### Read intent, do not invent it
The bridge must use existing planning state instead of guessing hidden goals.

### Preserve operational history
Handoffs and archives must remain traceable after translation.

### Write structured output
The bridge must not write only prose; it must write status fields that the next
run can parse.

### Keep separation of concerns
`.planning` remains the intent layer; the harness remains the executor.

## Translation Rules

### Objective to HarnessRequest
Convert the current objective into:
- objective name
- current UOW
- constraints
- expected outputs
- required checks

### Harness result to Planning update
Convert the envelope into:
- updated status
- summary
- next action
- verification outcome
- recovery notes

## Conflict Rules

### Missing objective
If `.planning` lacks a clear objective, stop and flag the bridge as incomplete.

### Conflicting state
If planning says one thing and memory says another, prefer the explicit project
manifest and record the mismatch.

### Stale handoff
If the handoff is stale or incomplete, mark it for review instead of silently
continuing.

## Acceptance Criteria

- The bridge can convert planning intent into a harness request.
- The bridge can write the result back without losing traceability.
- The bridge can detect and report mismatches.
- The bridge preserves the distinction between planning and execution.

## Failure Cases

### Example A — No objective
If there is no current objective in `.planning`, the bridge returns a warning
and does not fabricate one.

### Example B — Bad handoff
If the handoff state is incomplete, the bridge writes a structured warning and
requests clarification.

### Example C — Mismatch
If the manifest says one active project and `.planning` says another, block the
run until the mismatch is resolved.

## Implementation Notes

- Keep the bridge thin and explicit.
- Do not put execution policy in the bridge.
- Do not let the bridge become a second planner.
- The bridge only translates and records.
