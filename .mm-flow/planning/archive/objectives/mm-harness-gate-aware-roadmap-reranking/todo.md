# Todo — mm-harness-gate-aware-roadmap-reranking

## Execution Checklist

- [x] T1: Define and stabilize the slice
  - [x] T1.1: Review requirements and design context for T1
  - [x] T1.2: Implement T1 end-to-end
  - [x] T1.3: Run validation for T1
  - depends_on: none
  - validation: Review requirements/design/tasks package for consistency.

- [x] T2: Implement the smallest coherent deliverable
  - [x] T2.1: Review requirements and design context for T2
  - [x] T2.2: Implement T2 end-to-end
  - [x] T2.3: Run validation for T2
  - depends_on: T1
  - validation: Run targeted validation commands for the touched area.

- [x] T3: Close the continuity loop
  - [x] T3.1: Review requirements and design context for T3
  - [x] T3.2: Implement T3 end-to-end
  - [x] T3.3: Run validation for T3
  - depends_on: T2
  - validation: Refresh handoff and rerun discovery contract check.
