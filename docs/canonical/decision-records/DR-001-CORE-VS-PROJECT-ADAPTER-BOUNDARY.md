# DR-001 — Core vs Project Adapter Boundary

## 1. Decision Metadata

- **Decision ID:** DR-001
- **Date:** 2026-05-23
- **Status:** Approved with Conditions
- **Related project:** MasterMind
- **Related niche:** Framework / External Adoption / MVP
- **Related phase / workflow:** MVP Core Definition

## 2. Problem Statement

MasterMind needs a clear boundary between:

- what belongs to the reusable framework core
- what belongs to a specific project using the framework

Without this distinction, the system risks:

- copying the repo into every project
- polluting the core with project-specific logic
- making external adoption confusing
- weakening reuse and maintainability

## 3. Decision Type

- [x] Architecture
- [x] Project Adoption
- [x] Governance / Control

## 4. Why This Decision Is Needed

This decision is required before external adoption can become real and repeatable.

It also determines:

- what MasterMind is as a product/framework
- what should be generalized
- what should stay local to projects

## 5. Options Considered

### Option A — Treat most of the repo as reusable core

- **Description:** Promote nearly all major structures, docs and patterns into a broad reusable core.
- **Benefits:** maximizes reuse; fewer decisions per project
- **Risks:** bloated core; high coupling; hard external onboarding; weak boundaries

### Option B — Use a strict Core + Project Adapter split

- **Description:** Keep only reusable framework capabilities in core; push project-specific context, constraints, integrations and decisions into a project adapter layer.
- **Benefits:** clearer reuse model; cleaner external adoption; lower contamination risk
- **Risks:** requires more explicit packaging and onboarding discipline

### Option C — Project-first with minimal core

- **Description:** Keep the core very small and let most structure live inside each project.
- **Benefits:** local flexibility
- **Risks:** duplication, weak learning promotion, no strong framework identity

## 6. Participating Brains

- Platform Architecture Brain
- Agent Runtime & LLM Ops Brain
- Product Operations Brain
- Governance & Safety Brain
- Knowledge Distillation Brain

## 7. Positions by Brain

### Platform Architecture Brain

- **Position:** Strongly favors Option B
- **Main argument:** reusable capability must justify promotion to core; project-specific logic should not pollute the platform
- **Confidence:** High
- **Main concern:** a vague split will reintroduce structural entropy

### Agent Runtime & LLM Ops Brain

- **Position:** Favors Option B
- **Main argument:** runtime/provider abstractions should live in core, but project-specific backend choices and credentials belong in adapters
- **Confidence:** High
- **Main concern:** if runtime details leak into projects inconsistently, provider strategy becomes incoherent

### Product Operations Brain

- **Position:** Favors Option B with explicit onboarding aids
- **Main argument:** external adoption is only viable if projects know exactly what they must bring vs what the core already provides
- **Confidence:** High
- **Main concern:** strict boundaries without clear starter kits will create adoption friction

### Governance & Safety Brain

- **Position:** Favors Option B
- **Main argument:** governance must distinguish reusable control rules from project-local risk rules; otherwise auditability becomes ambiguous
- **Confidence:** High
- **Main concern:** projects may bypass core controls if boundaries are unclear

### Knowledge Distillation Brain

- **Position:** Favors Option B
- **Main argument:** doctrinal assets, templates and distillation standards should be reusable core; niche/project-specific corpora belong in adapters until generalized
- **Confidence:** High
- **Main concern:** weak boundaries will contaminate reusable doctrine with local noise

## 8. Objections / Cross-Critique

- Product Operations Brain objected that Option B could become too abstract unless paired with a project-start kit.
- Runtime Brain warned that “strict split” must not force duplication of provider/routing logic into each project.
- Governance Brain objected to any model where project-local teams can silently override core control patterns without a visible decision record.

## 9. Missing Evidence / Open Gaps

- No external adoption pilot has yet tested the proposed split.
- No concrete project adapter template exists yet.
- No worked example yet shows what “minimum project-local package” looks like.

## 10. Final Decision

- **Selected option:** Option B — strict Core + Project Adapter split
- **Decision owner:** Platform Architecture Brain
- **Decision rationale:** This gives MasterMind the clearest reusable identity while preserving room for project-local specialization. It also best supports adoption, governance and future learning promotion back to core.

## 11. Veto / Conditional Approval

- **Was there a veto?** No
- **Who could veto?** Governance & Safety Brain, Evaluator
- **Conditions before action:**
  1. define a concrete project adapter model
  2. define starter-kit artifacts
  3. define promotion rules from project-local to core

## 12. Action Gates

- Gate 1: `13-EXTERNAL-PROJECT-ADOPTION-MODEL.md` must stay aligned with this decision
- Gate 2: a first project-adapter template/example must be created
- Gate 3: one external-project scenario must test this split

## 13. Action Taken

- **Action status:** Pending gates
- **Action description:** Treat canonical docs, templates, meta-brains, reusable protocols, and reusable doctrine as core; treat project context, local integrations, local constraints, local decisions and local knowledge as project-adapter material unless explicitly promoted

## 14. Reversal Conditions

This decision should be revisited if:

- external adoption proves too heavy or confusing
- projects require far more local duplication than expected
- reusable core becomes too abstract to be practical

## 15. Learning Capture

- **Observation:** the framework now has enough structure to make real architectural decisions via meta-brain synthesis
- **Pattern:** adoption concerns consistently force clearer boundary design
- **Heuristic candidate:** if a capability is reusable across multiple projects and improves coordination, doctrine or runtime behavior, it belongs in core; otherwise keep it in the project adapter until proven reusable

## 16. Links / Artifacts

- `docs/canonical/10-MVP-EXECUTION-PLAN.md`
- `docs/canonical/13-EXTERNAL-PROJECT-ADOPTION-MODEL.md`
- `docs/canonical/meta-brains/01-PLATFORM-ARCHITECTURE-BRAIN.md`
- `docs/canonical/meta-brains/02-AGENT-RUNTIME-LLM-OPS-BRAIN.md`
- `docs/canonical/meta-brains/04-PRODUCT-OPERATIONS-BRAIN.md`
- `docs/canonical/meta-brains/05-GOVERNANCE-SAFETY-BRAIN.md`
