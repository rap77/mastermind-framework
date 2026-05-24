# DR-002 — Subscription Window Strategy

## 1. Decision Metadata

- **Decision ID:** DR-002
- **Date:** 2026-05-23
- **Status:** Approved with Conditions
- **Related project:** MasterMind
- **Related niche:** Runtime / Multi-LLM / External Adoption
- **Related phase / workflow:** MVP Runtime Strategy

## 2. Problem Statement

MasterMind must support multiple model providers and accounts, including subscription-backed usage that is limited by time windows (e.g. 5-hour availability windows).

The framework needs a strategy for:

- detecting exhaustion of a subscription window
- recording when the backend is expected to become available again
- checkpointing work before switching
- failing over to another available backend/account
- supporting both manual and automatic execution modes
- leaving an auditable trace for next-day review

## 3. Decision Type

- [x] Runtime / LLM Ops
- [x] Governance / Control
- [x] Project Adoption

## 4. Why This Decision Is Needed

Without this decision, MasterMind cannot safely or effectively:

- exploit multiple subscriptions across providers
- run long overnight sessions
- preserve continuity of work across backend exhaustion
- keep clear human-readable traces of automatic execution

## 5. Options Considered

### Option A — Single active provider only, no automatic switching

- **Description:** Use one subscription or provider at a time and stop when it is exhausted.
- **Benefits:** simple, predictable
- **Risks:** wastes available capacity across other subscriptions; weak overnight autonomy

### Option B — Automatic failover with checkpointing and audit trail

- **Description:** Detect exhaustion, checkpoint the current work, record next availability, switch to the next eligible backend, and continue under configurable execution modes.
- **Benefits:** maximizes available capacity; enables overnight work; preserves continuity and traceability
- **Risks:** adds runtime complexity; requires strong governance and clear modes

### Option C — Hybrid failover only between some backends, otherwise pause

- **Description:** Switch automatically only across a constrained subset, then ask the user when reaching cost/risk boundaries.
- **Benefits:** more controlled than full automation
- **Risks:** may reduce autonomy if too conservative; still needs most of the scheduling machinery

## 6. Participating Brains

- Agent Runtime & LLM Ops Brain
- Governance & Safety Brain
- Platform Architecture Brain
- Product Operations Brain

## 7. Positions by Brain

### Agent Runtime & LLM Ops Brain

- **Position:** Strongly favors Option B
- **Main argument:** multi-provider support is incomplete without explicit failover, availability tracking, and execution-mode controls
- **Confidence:** High
- **Main concern:** switching without checkpoint discipline would create broken continuity

### Governance & Safety Brain

- **Position:** Supports Option B only with strict controls
- **Main argument:** automatic switching is acceptable if auditable, gated, and configurable by execution mode
- **Confidence:** High
- **Main concern:** silent backend changes without traceability or human escalation thresholds are unsafe

### Platform Architecture Brain

- **Position:** Supports Option B
- **Main argument:** this belongs in the reusable core as a scheduling capability, not as ad hoc project logic
- **Confidence:** High
- **Main concern:** implementation must be modular: registry, availability tracker, switch policy, checkpointing, audit

### Product Operations Brain

- **Position:** Supports Option B with a Hybrid default
- **Main argument:** users need a practical default that enables overnight work without surprising them
- **Confidence:** High
- **Main concern:** a fully automatic system without clear next-day reporting would hurt trust and adoption

## 8. Objections / Cross-Critique

- Governance & Safety objected to any design where automatic switching happens without checkpoint creation and event logging.
- Product Operations objected to “automatic everything” as a default if users cannot easily review what happened.
- Runtime Brain objected to any design that treats subscription windows as merely manual notes rather than first-class availability state.

## 9. Missing Evidence / Open Gaps

- No implemented scheduler exists yet.
- Availability detection may differ across providers and may initially need heuristics.
- No morning review report format has been defined yet.

## 10. Final Decision

- **Selected option:** Option B, with Hybrid as the recommended default execution mode
- **Decision owner:** Agent Runtime & LLM Ops Brain
- **Decision rationale:** MasterMind should support automatic failover across subscription windows and providers, but under explicit execution modes, mandatory checkpointing, and auditable event trails.

## 11. Veto / Conditional Approval

- **Was there a veto?** No
- **Who could veto?** Governance & Safety Brain, Evaluator
- **Conditions before action:**
  1. define scheduler architecture
  2. define execution modes policy
  3. require checkpoint + audit log before backend switch

## 12. Action Gates

- Gate 1: a `Window Scheduler` architecture document must exist
- Gate 2: execution modes must be explicitly defined (`pause_and_ask`, `automatic_cycle`, `hybrid`)
- Gate 3: every switch must produce a checkpoint reference and audit event
- Gate 4: high-risk actions must remain pausable even in automatic mode

## 13. Action Taken

- **Action status:** Pending gates
- **Action description:** MasterMind will adopt a subscription-window-aware multi-backend runtime strategy with:
  - account/provider registry
  - availability tracking
  - checkpoint-before-switch
  - auditable backend transitions
  - configurable manual/automatic/hybrid execution modes

## 14. Reversal Conditions

This decision should be revisited if:

- switching causes too much task degradation or context loss
- provider heuristics are too unreliable
- users consistently prefer explicit pause workflows over automatic cycling

## 15. Learning Capture

- **Observation:** runtime strategy must include account/window management, not only provider/model selection
- **Pattern:** overnight autonomy requires checkpointing, not just backend redundancy
- **Heuristic candidate:** if a backend can become unavailable on a known or inferable window, it must be treated as scheduled capacity, not constant availability

## 16. Links / Artifacts

- `docs/canonical/meta-brains/02-AGENT-RUNTIME-LLM-OPS-BRAIN.md`
- `docs/canonical/meta-brains/05-GOVERNANCE-SAFETY-BRAIN.md`
- `docs/canonical/13-EXTERNAL-PROJECT-ADOPTION-MODEL.md`
- `docs/canonical/15-MINIMAL-ORCHESTRATION-PATH.md`
