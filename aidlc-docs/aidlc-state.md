# AI-DLC State — Multi-Harness Architecture

## Project
- Name: Multi-Harness Architecture
- Source: `Product-Definition/`
- Project Type: Brownfield feature on existing system
- Current Phase: CONSTRUCTION
- Current Stage: Completed UOW-5 verification-review-recovery-v1 build and test

## Project Manifest
- project_name: MasterMind Unified Harness + Memory
- canonical_scope: reusable harness core, memory core, and project adapters
- source_of_truth_ai_dlc: true
- source_of_truth_planning: true
- active_objective: harness-core-runtime-v1
- active_uow: UOW-2
- project_root: /home/rpadron/proy/mastermind
- operational_layer: .planning
- design_layer: aidlc-docs
- memory_layer: Engram persistent memory
- harness_layer: apps/api/mastermind_cli and tools/mastermind-cli
- adapter_name: mastermind-adapter
- bridge_contract: aidlc-docs/inception/plans/planning-bridge-contract.md

## Extension Configuration
| Extension | Enabled | Decided At |
|---|---|---|
| None declared | No | Requirements Analysis |

## Stage Progress
### 🔵 INCEPTION PHASE
- [x] Workspace Detection
- [ ] Reverse Engineering (not executed in this run; direct code/doc inspection used as working context)
- [x] Requirements Analysis
- [x] Application Design
- [x] Units Generation

### 🟢 CONSTRUCTION PHASE
- [x] Functional Design — UOW-1 Governance Core
- [x] NFR Requirements — UOW-1 Governance Core
- [x] NFR Design — UOW-1 Governance Core
- [x] Code Generation — UOW-1 Governance Core
- [x] Code Generation — UOW-2 Budget Persistence
- [x] Build and Test
- [x] Code Generation — UOW-3 Memory Eval Harness
- [x] Build and Test — UOW-3 Memory Eval Harness
- [x] Code Generation — memory-reranking-v1
- [x] Build and Test — memory-reranking-v1
- [x] Functional Design — UOW-5 Core Runtime Contracts
- [x] NFR Requirements — UOW-5 Core Runtime Contracts
- [x] NFR Design — UOW-5 Core Runtime Contracts
- [x] Code Generation — UOW-5 Core Runtime Contracts
- [x] Build and Test — UOW-5 Core Runtime Contracts
- [x] Functional Design — UOW-5 verification-review-recovery-v1
- [x] NFR Requirements — UOW-5 verification-review-recovery-v1
- [x] NFR Design — UOW-5 verification-review-recovery-v1
- [x] Code Generation — UOW-5 verification-review-recovery-v1
- [x] Build and Test — UOW-5 verification-review-recovery-v1

## Current Status
- Last completed stage: Build and Test — UOW-5 verification-review-recovery-v1
- Current working stage: Operations placeholder reviewed; next slice selection pending
- Next recommended stage: Start next UOW-5 slice for persistence/continuity/multi-loop resume seams
- Unified initiative kickoff: `manifest-contract-bridge-v1` defined for harness + memory reuse across projects
- Draft artifacts created for the unified initiative: project manifest, harness contract, memory contract, and planning bridge contract
- Application design drafted for the unified harness + memory architecture
- Unit-of-work map drafted for the unified harness + memory architecture
- UOW-1 implementation plan drafted for the project manifest and source-of-truth rules
- UOW-1 functional spec drafted with exact manifest fields, validation rules, and conflict handling
- UOW-2 functional spec drafted for harness core contracts, loop selection, envelope, verification, review, and recovery
- UOW-3 functional spec drafted for memory core, checkpoints, decisions, retrieval, and resume rules
- UOW-4 functional spec drafted for the planning bridge between `.planning` and the harness runtime
- UOW-5 functional spec drafted for project adapter and end-to-end integration
- UOW-1 code generation plan drafted for the project manifest and source-of-truth rules
- UOW-4 planning bridge + project adapter now implemented in `apps/api/mastermind_cli/mm_flow/`
- UOW-2 harness core runtime now implemented in `apps/api/mastermind_cli/orchestrator/runtime_contracts/`
- Notes:
  - Product discovery inputs are in `Product-Definition/`.
  - Open questions OQ-1 through OQ-8 were resolved in inception artifacts.
  - User stories were not generated in this run; units were derived from requirements and application design.
  - Governance core slice is in place: deterministic policy boundary, JSONL evidence writer, and Coordinator integration are implemented in `tools/mastermind-cli` and wired through the API runtime.
  - Budget persistence slice is in place: append-only JSONL ledger, restart recovery, threshold verdicts, and Coordinator pre/post enforcement are implemented.
  - Pytest smoke marker configured: `-m smoke` now selects governance, budget, orchestration, and e2e smoke modules.
  - Verified suites currently pass via project-local runners: `tools/mastermind-cli` targeted governance/budget/orchestration tests and `apps/api` governance wiring/task execution tests.
  - `scripts/test-governance-slices.sh` is the canonical entrypoint for this verification because cross-package venv reuse caused false dependency failures.
  - Build and Test artifacts for the implemented governance/budget slice are now in `aidlc-docs/construction/build-and-test/`.
  - UOW-3 remained mostly decoupled from runtime execution and now includes `EvalHarnessService`, a shared retrieval baseline, and an explicit vector-candidate seam that preserves the stable `MemoryStore.search(...)` caller contract.
  - Retrieval v1 now covers lexical retrieval, optional vector candidates, simple fusion, and a deterministic baseline that stays green under semantic fusion.
  - `memory-reranking-v1` is now closed with noop + heuristic reranking over stable Retrieval v1 results.
  - `memory-graph-recall-v1` is now closed with a noop seam plus deterministic `StaticMemoryGraphRecallProvider` expansion over related memories.
  - Focused regression is green after graph recall wiring: `tests/unit/test_memory_graph_recall.py`, `tests/unit/test_memory_layer_postgres_store.py`, and `tests/unit/test_memory_eval_harness.py`.
  - Research from ECC, gentle-ai, and NotebookLM is now captured in `aidlc-docs/inception/research/multi-harness-loop-engineering-synthesis.md`.
  - The architecture direction is now explicitly **multi-harness + multi-loop**, not just governance/budget/retrieval slices.
  - New core design targets were added to requirements/application design: Harness Registry, Loop Selector, Envelope Contract, Verification/Review/Recovery Harnesses, and Capability Registry.
  - The target state remains a model-agnostic system with continuity across backend/model switches, but the immediate implementation focus should stay on the core runtime contracts rather than full ECC-style operator-surface parity.
  - NFR Design artifacts for UOW-5 now map requirements into concrete runtime patterns: deterministic selection pipeline, stable envelope contract, maker-checker separation, bounded recovery ladder, safe degradation, and persisted continuity boundary.
  - Code Generation planning for UOW-5 now scopes the first executable slice to `apps/api/mastermind_cli/orchestrator/runtime_contracts/` plus minimal `StatelessCoordinator` wiring, keeping the legacy coordinator and richer recovery loops out of the MVP cut.
  - `envelope-contract-loop-selector-v1` is now implemented in the API runtime with deterministic registries, loop policy selection, stable execution envelopes, coordinator metadata wiring, focused unit coverage, and no disruption to existing orchestration flows.
  - Build and Test artifacts for UOW-5 now define focused verification for runtime contracts, stateless coordinator wiring, bounded-control regression checks, and the local `UV_CACHE_DIR=/tmp/uv-cache` workaround required in this environment.
  - Operations remains a placeholder in AI-DLC for this repo; no deployment workflow was executed in this run.
  - The next intended UOW-5 slice is `verification-review-recovery-v1`, focused on making verification, maker-checker, and bounded recovery executable rather than declarative.
  - Functional design for the next UOW-5 slice now defines deterministic local verification, rubric-based maker-checker review, and bounded recovery decisions over the existing stateless runtime seam.
  - NFR requirements for the next UOW-5 slice now constrain verification/review/recovery to remain local, bounded, deterministic, and incrementally integrated into the stateless coordinator seam.
  - NFR design for the next UOW-5 slice now maps those constraints into conditional harness activation, local deterministic review/verification, recovery-as-decision-engine, restrictive final verdict synthesis, and isolated harness testing.
  - Code Generation planning for `verification-review-recovery-v1` now scopes the slice to new local harness modules plus minimal `StatelessCoordinator` wiring, preserving the envelope contract and avoiding legacy-coordinator expansion.
  - `verification-review-recovery-v1` is now implemented with local deterministic harnesses, bounded recovery decisions, final envelope synthesis, and focused tests over the stateless seam.
  - Build and Test artifacts for `verification-review-recovery-v1` now cover the new verification/review/recovery harnesses, restrictive final verdict synthesis, focused `36 passed` regression, and the same local `UV_CACHE_DIR=/tmp/uv-cache` workaround.
  - A minimal Operations placeholder note now lives at `aidlc-docs/operations/operations-placeholder.md` so the workflow closes cleanly without inventing non-existent deployment work.
