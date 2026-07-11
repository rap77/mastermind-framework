# Adapter Boundary — harness-memory-unification

## Purpose
Define what belongs to the reusable platform and what belongs to the MasterMind-specific adapter.

## Adapter Responsibilities
- detect the active project and objective from the repo context
- load the project manifest and operational `.planning` state
- translate repo-specific planning details into bridge inputs
- route runtime outputs back into repo-specific handoff artifacts
- keep project-specific quirks out of the reusable harness core

## Reusable Platform Responsibilities
- select and run loops deterministically
- persist and retrieve memory
- emit canonical execution envelopes
- validate bridge and memory invariants

## Adapter Inputs
- repository path
- project manifest
- active `.planning` objective or handoff
- memory snapshot
- runtime capabilities

## Adapter Outputs
- bridge request payload
- repo-specific run summary
- updated planning handoff
- archive-ready completion note

## Invariants
- the adapter may know the repo; the core may not
- adapter-specific branching must stay thin and explicit
- the core runtime must remain reusable across repos
- historical planning artifacts must remain intact

## Success Criteria
- the harness core can be reused in another repo without changing the core contracts
- MasterMind-specific routing stays in the adapter boundary
- `.planning` write-back is structured, traceable, and non-destructive
