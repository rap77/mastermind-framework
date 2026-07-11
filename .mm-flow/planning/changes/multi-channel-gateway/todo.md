# Todo — multi-channel-gateway

## Execution Checklist

- [x] T1: Define and stabilize the slice
  - [x] T1.1: Review requirements and design context for T1
  - [x] T1.2: Implement T1 end-to-end
  - [x] T1.3: Run validation for T1
  - depends_on: none
  - validation: Review requirements/design/tasks package for consistency.

- [ ] T2: Implement the smallest coherent deliverable
  - [ ] T2.1: Review requirements and design context for T2
  - [ ] T2.2: Implement T2 end-to-end
  - [ ] T2.3: Run validation for T2
  - depends_on: T1
  - validation: Run targeted validation commands for the touched area.

- [ ] T3: Close the continuity loop
  - [ ] T3.1: Review requirements and design context for T3
  - [ ] T3.2: Implement T3 end-to-end
  - [ ] T3.3: Run validation for T3
  - depends_on: T2
  - validation: Refresh handoff and rerun discovery contract check.
