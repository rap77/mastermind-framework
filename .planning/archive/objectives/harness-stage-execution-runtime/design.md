# Design — harness-stage-execution-runtime

## Architecture / Boundaries

```text
ObjectiveProfile
  -> MultiHarnessSelector
  -> RunBundleComposer
  -> RunBundleValidator
  -> RunBundleStageExecutor
       -> StageGraphValidator
       -> StageScheduler
       -> CapabilityInvoker
       -> GateEvaluator
       -> EvidenceRecorder
       -> CheckpointStore
       -> RecoveryRouter
       -> ReplanService
  -> ExecutionEnvelope
```

- selector owns package/capability selection
- harness package owns stage declarations and domain semantics
- executor owns control flow and transitions
- verifier owns deterministic verdicts
- reviewer owns adversarial findings
- approver owns authorized decisions
- project state owns structured persistence and lineage
- `.planning` owns operational continuity

## Technical Approach

### Contract-first models

Extend runtime contracts additively with stage graph, evidence, approval,
checkpoint and replan records. Preserve existing `RunBundle` consumers through
an explicit compatibility graph rather than implicit coordinator behavior.

StageGraph uses versioned nodes, edges and declared loop records. Before RFC
8785/JCS plus SHA-256, unordered arrays are sorted by canonical IDs/tuples;
semantically meaningful order uses explicit ordinals or edges. Hash input covers
graph, profile, capabilities, policies and artifact contracts.

### Bundle materialization

Composer materializes stages and selected capabilities. Validator rejects
missing prerequisites, undeclared cycles, unknown policies and output paths with
no producer. Bundle hash covers the executable manifest.

### Stage scheduler

Select dependency-ready stages deterministically. Optional stages require a
decision record. A stage invokes only capabilities referenced by the bundle.

### Gates and evidence

Gate evaluator consumes typed evidence. Instruction artifacts and summaries do
not count as execution evidence. Approval policies can require human decisions
without hardcoding approval on every stage.

### Review support

Add `review` to package types and supporting selection. Verification checks
criteria; review searches for defects and risks with independent context.

### Checkpoint and resume

Persist run/stage state and fine-grained progress. Resume verifies objective,
bundle and profile hashes before continuing.

Project state is authoritative and atomically commits StageResult, evidence refs,
RunCheckpoint and outbox events under a transition idempotency key. `.planning`
and memory are retryable projections; RunBundles remain immutable inputs.

### Recovery and safe replanning

Recovery supports retry, patch, replan, rollback, escalate and stop with bounded
attempts. Replan performs impact analysis and invalidates downstream outputs.

## Dependencies

- `engineering-doctrine-layer`
- `artifact-versioning-and-lineage`
- `project-state-mvp`
- `docs/canonical/113-HARNESS-STAGE-EXECUTION-RUNTIME-CONTRACT.md`
- existing multi-harness selector/composer/validator
- existing project adapter, memory writer and runtime envelope

## Validation Strategy

- unit tests for models, graph validation, scheduling and gates
- unit tests for review package selection
- integration tests for HarnessRunExecutor bundle wiring
- checkpoint/resume and bundle mismatch cases
- recovery/replan invalidation cases
- compatibility tests for existing harness runs
- planning contract, JSON, ruff and targeted pytest checks
- no build command

## Important Tradeoffs

- one executor adds shared contract work but removes duplicated runtimes
- explicit stage metadata enlarges bundles but makes execution auditable
- compatibility graphs add migration code only where existing consumers require it
- package type `review` expands selection semantics but preserves a real boundary
- hash-checked resume may block stale runs, which is safer than silent continuation

## Risks and Mitigations

| Risk | Impact | Mitigation |
| --- | --- | --- |
| executor absorbs domain logic | critical | conformance tests and dependency rules |
| bundle selected but still ignored | critical | integration assertion on invoked stages |
| stale checkpoint resumes | high | bundle/profile hash validation |
| review duplicates verification | high | separate contracts and routing tests |
| replan leaves stale outputs valid | high | dependency impact graph and invalidation records |
| infinite recovery loop | high | attempts, tool and time budgets |
| legacy routes regress | high | explicit compatibility route and regression suite |

## Context Notes

- Objective implementation and consumer validation are complete.
- It remains a prerequisite for UI/UX, onboarding and Adaptive Delivery runtimes.
- It does not implement any domain harness.
- Consumer objectives remain independently planned and inactive.
