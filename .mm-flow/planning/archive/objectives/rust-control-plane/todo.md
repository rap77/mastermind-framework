# Todo — rust-control-plane

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

- [x] T4: Define the next Rust control-plane slice
  - [x] T4.1: Review completed auth slice and remaining Rust gaps
  - [x] T4.2: Define the next slice end-to-end
  - [x] T4.3: Run validation for T4
  - depends_on: T3
  - validation: Refresh package continuity for the next Rust slice.

- [x] T5: Implement explicit AI-worker runtime boundary
  - [x] T5.1: Review requirements and design context for T5
  - [x] T5.2: Implement T5 end-to-end
  - [x] T5.3: Run validation for T5
  - depends_on: T4
  - validation: Run Rust validation for the worker-boundary slice.

- [x] T6: Close continuity for the next Rust slice
  - [x] T6.1: Review requirements and design context for T6
  - [x] T6.2: Refresh handoff and package state
  - [x] T6.3: Run validation for T6
  - depends_on: T5
  - validation: Refresh continuity and rerun discovery contract check.

- [x] T7: Define the next Rust control-plane slice
  - [x] T7.1: Review remaining Rust runtime and validation gaps
  - [x] T7.2: Define the next slice end-to-end
  - [x] T7.3: Run validation for T7
  - depends_on: T6
  - validation: Refresh package continuity for the next Rust slice.

- [x] T8: Restore the metrics latency validation baseline
  - [x] T8.1: Review requirements and design context for T8
  - [x] T8.2: Implement T8 end-to-end
  - [x] T8.3: Run validation for T8
  - depends_on: T7
  - validation: Run targeted Rust validation for the metrics slice.

- [x] T9: Close continuity for the metrics slice
  - [x] T9.1: Review requirements and design context for T9
  - [x] T9.2: Refresh handoff and package state
  - [x] T9.3: Run validation for T9
  - depends_on: T8
  - validation: Refresh continuity and rerun discovery contract check.

- [x] T10: Define the next Rust control-plane slice
  - [x] T10.1: Review remaining Rust validation gaps
  - [x] T10.2: Define the next slice end-to-end
  - [x] T10.3: Run validation for T10
  - depends_on: T9
  - validation: Refresh package continuity for the next Rust slice.

- [x] T11: Clarify the DLQ test environment contract
  - [x] T11.1: Review requirements and design context for T11
  - [x] T11.2: Implement T11 end-to-end
  - [x] T11.3: Run validation for T11
  - depends_on: T10
  - validation: Run targeted Rust validation for the DLQ test slice.

- [x] T12: Close continuity for the DLQ test slice
  - [x] T12.1: Review requirements and design context for T12
  - [x] T12.2: Refresh handoff and package state
  - [x] T12.3: Run validation for T12
  - depends_on: T11
  - validation: Refresh continuity and rerun discovery contract check.

- [x] T13: Define the next Rust control-plane slice
  - [x] T13.1: Review the remaining Rust runtime gap
  - [x] T13.2: Define the next slice end-to-end
  - [x] T13.3: Run validation for T13
  - depends_on: T12
  - validation: Refresh package continuity for the next Rust slice.

- [x] T14: Restore the typed AI-worker startup seam
  - [x] T14.1: Review requirements and design context for T14
  - [x] T14.2: Implement T14 end-to-end
  - [x] T14.3: Run validation for T14
  - depends_on: T13
  - validation: Run targeted Rust validation for the startup seam slice.

- [x] T15: Close continuity for the startup seam slice
  - [x] T15.1: Review requirements and design context for T15
  - [x] T15.2: Refresh handoff and package state
  - [x] T15.3: Run validation for T15
  - depends_on: T14
  - validation: Refresh continuity and rerun discovery contract check.

- [x] T16: Retain the initialized AI-worker client in runtime state
  - [x] T16.1: Review requirements and design context for T16
  - [x] T16.2: Implement T16 end-to-end
  - [x] T16.3: Run validation for T16
  - depends_on: T15
  - validation: Run targeted Rust validation for the retained-client slice.

- [x] T17: Close continuity for the retained-client slice
  - [x] T17.1: Review requirements and design context for T17
  - [x] T17.2: Refresh handoff and package state
  - [x] T17.3: Run validation for T17
  - depends_on: T16
  - validation: Refresh continuity and rerun discovery contract check.

- [x] T18: Use the retained AI-worker client for first dispatch
  - [x] T18.1: Review requirements and design context for T18
  - [x] T18.2: Implement T18 end-to-end
  - [x] T18.3: Run validation for T18
  - depends_on: T17
  - validation: Run targeted Rust validation for the first-dispatch slice.

- [x] T19: Close continuity for the first-dispatch slice
  - [x] T19.1: Review requirements and design context for T19
  - [x] T19.2: Refresh handoff and package state
  - [x] T19.3: Run validation for T19
  - depends_on: T18
  - validation: Refresh continuity and rerun discovery contract check.

- [x] T20: Fail closed for disabled and unavailable worker runtime modes
  - [x] T20.1: Review requirements and design context for T20
  - [x] T20.2: Implement T20 end-to-end
  - [x] T20.3: Run validation for T20
  - depends_on: T19
  - validation: Run targeted Rust validation for the degraded-runtime slice.

- [x] T21: Close continuity for the degraded-runtime slice
  - [x] T21.1: Review requirements and design context for T21
  - [x] T21.2: Refresh handoff and package state
  - [x] T21.3: Run validation for T21
  - depends_on: T20
  - validation: Refresh continuity and rerun discovery contract check.

- [x] T22: Clarify post-dispatch success semantics
  - [x] T22.1: Review requirements and design context for T22
  - [x] T22.2: Implement T22 end-to-end
  - [x] T22.3: Run validation for T22
  - depends_on: T21
  - validation: Run targeted Rust validation for the post-dispatch success slice.

- [x] T23: Close continuity for the post-dispatch semantics slice
  - [x] T23.1: Review requirements and design context for T23
  - [x] T23.2: Refresh handoff and package state
  - [x] T23.3: Run validation for T23
  - depends_on: T22
  - validation: Refresh continuity and rerun discovery contract check.

- [x] T24: Add durable audit surface for successful AI-worker responses
  - [x] T24.1: Review requirements and design context for T24
  - [x] T24.2: Implement T24 end-to-end
  - [x] T24.3: Run validation for T24
  - depends_on: T23
  - validation: Run targeted Rust validation for the durable-audit slice.

- [x] T25: Close continuity for the durable success-audit slice
  - [x] T25.1: Review requirements and design context for T25
  - [x] T25.2: Refresh handoff and package state
  - [x] T25.3: Run validation for T25
  - depends_on: T24
  - validation: Refresh continuity and rerun discovery contract check.

- [x] T26: Add durable audit surface for failed AI-worker responses
  - [x] T26.1: Review requirements and design context for T26
  - [x] T26.2: Implement T26 end-to-end
  - [x] T26.3: Run validation for T26
  - depends_on: T25
  - validation: Run targeted Rust validation for the failure-audit slice.

- [x] T27: Close continuity for the durable failure-audit slice
  - [x] T27.1: Review requirements and design context for T27
  - [x] T27.2: Refresh handoff and package state
  - [x] T27.3: Run validation for T27
  - depends_on: T26
  - validation: Refresh continuity and rerun discovery contract check.

- [x] T28: Clarify AI-worker audit event taxonomy
  - [x] T28.1: Review requirements and design context for T28
  - [x] T28.2: Implement T28 end-to-end
  - [x] T28.3: Run validation for T28
  - depends_on: T27
  - validation: Run targeted Rust validation for the taxonomy slice.

- [x] T29: Close continuity for the audit-taxonomy slice
  - [x] T29.1: Review requirements and design context for T29
  - [x] T29.2: Refresh handoff and package state
  - [x] T29.3: Run validation for T29
  - depends_on: T28
  - validation: Refresh continuity and rerun discovery contract check.

- [x] T30: Clarify AI-worker audit query ergonomics
  - [x] T30.1: Review requirements and design context for T30
  - [x] T30.2: Implement T30 end-to-end
  - [x] T30.3: Run validation for T30
  - depends_on: T29
  - validation: Run targeted Rust validation for the audit-query slice.

- [x] T31: Close continuity for the audit-query slice
  - [x] T31.1: Review requirements and design context for T31
  - [x] T31.2: Refresh handoff and package state
  - [x] T31.3: Run validation for T31
  - depends_on: T30
  - validation: Refresh continuity and rerun discovery contract check.

- [x] T32: Decide whether AI-worker needs a dedicated audit convenience surface
  - [x] T32.1: Review requirements and design context for T32
  - [x] T32.2: Implement T32 end-to-end
  - [x] T32.3: Run validation for T32
  - depends_on: T31
  - validation: Run targeted Rust validation for the audit-convenience slice.

- [x] T33: Close continuity for the audit-convenience decision slice
  - [x] T33.1: Review requirements and design context for T33
  - [x] T33.2: Refresh handoff and package state
  - [x] T33.3: Run validation for T33
  - depends_on: T32
  - validation: Refresh continuity and rerun discovery contract check.

- [x] T34: Decide whether rust-control-plane is ready to close
  - [x] T34.1: Review requirements and design context for T34
  - [x] T34.2: Implement T34 end-to-end
  - [x] T34.3: Run validation for T34
  - depends_on: T33
  - validation: Run discovery contract check for the close-or-continue decision.
