# 47. Brain-Assisted Planning and Execution Flow

## Purpose

This document explains how MasterMind's software-development brains should participate in the hybrid planning and execution workflow.

The goal is not to let brains “chat freely” about planning.

The goal is to give each brain a **clear role** in:
- roadmap discovery
- objective packaging
- execution validation
- continuity across models

---

## Core Principle

Brains should support the workflow in a **structured, role-based way**.

They should help answer specific planning questions such as:
- what should be built next?
- what is the correct architecture?
- what are the technical risks?
- how should the work be decomposed?
- what must be verified before calling it done?

They should not replace the planning artifacts.

The artifacts remain the source of truth.

---

## Relevant Software-Development Brains

For planning and execution flow, the most important software-development brains are:

1. **Brain #1 — Product / Strategy**
2. **Brain #4 — Backend**
3. **Brain #5 — Frontend**
4. **Brain #6 — QA / DevOps**
5. **Brain #7 — Growth / Evaluator**

Optional supporting roles may later include:
- Platform Architecture meta-brain
- Runtime & LLM Ops meta-brain
- Governance & Safety meta-brain
- Product Operations meta-brain

---

## Role of Each Brain in the Workflow

## Brain #1 — Product / Strategy

### Owns
- objective framing
- MVP relevance
- user-facing value
- scope boundaries
- prioritization

### Helps answer
- is this objective necessary for MVP?
- what problem does it solve?
- is this a real objective or just technical noise?
- what is in scope vs out of scope?

### Main outputs it influences
- `requirements.md`
- roadmap prioritization
- objective summaries

---

## Brain #4 — Backend

### Owns
- backend architecture decisions
- data/service boundaries
- API and persistence design
- integration constraints

### Helps answer
- what backend workstreams are real objectives?
- what backend dependencies exist between objectives?
- what would be the cleanest backend shape for the objective?
- what implementation risks must appear in the design?

### Main outputs it influences
- `design.md`
- task dependency design
- backend task breakdown

---

## Brain #5 — Frontend

### Owns
- user interface execution shape
- interaction architecture
- dashboard/application workflows
- frontend implementation realism

### Helps answer
- what UI workstreams should exist?
- which objective slices produce visible user value?
- how should frontend work be sequenced?
- what UX-specific constraints should appear in the design?

### Main outputs it influences
- `design.md`
- UI/UX sections of `requirements.md`
- frontend task breakdown

---

## Brain #6 — QA / DevOps

### Owns
- acceptance verification strategy
- testing gates
- release reliability
- failure-mode thinking

### Helps answer
- what acceptance criteria are actually verifiable?
- which tasks need stronger testing before execution?
- what validation commands should appear in handoff?
- what would make this objective incomplete even if code exists?

### Main outputs it influences
- acceptance criteria in `tasks.md`
- testing sections in `design.md`
- validation commands in `HANDOFF-CURRENT.md`

---

## Brain #7 — Growth / Evaluator

### Owns
- quality of synthesis
- detection of weak plans
- identification of over-complexity or under-scoping
- final evaluation of roadmap/objective quality

### Helps answer
- is this roadmap coherent?
- is the active objective too large or too vague?
- are we missing critical MVP work?
- is the plan execution-ready or still fuzzy?

### Main outputs it influences
- roadmap sanity checks
- active-objective gatekeeping
- handoff quality
- final “ready for execution” judgment

---

## Brain Participation by Workflow Step

## Step A — Roadmap Discovery

### Primary brains
- Brain #1
- Brain #7

### Supporting brains
- Brain #4
- Brain #5
- Brain #6

### Pattern

1. Brain #1 proposes candidate objectives from declared intent.
2. Brain #4 and #5 validate whether those objectives map to real technical/UI workstreams.
3. Brain #6 flags validation and execution risks.
4. Brain #7 evaluates whether the resulting roadmap is coherent and MVP-focused.

### Output
- objective roadmap
- dependency ordering
- MVP inclusion / exclusion decisions

---

## Step B — Objective Packaging

### Primary brains
- Brain #1
- Brain #4
- Brain #5
- Brain #6

### Pattern

1. Brain #1 frames the objective and defines scope.
2. Brain #4 defines backend design implications.
3. Brain #5 defines frontend design implications.
4. Brain #6 defines verifiable acceptance and testing expectations.
5. Brain #7 checks whether the package is actually execution-ready.

### Output
- `requirements.md`
- `design.md`
- `tasks.md`
- `HANDOFF-CURRENT.md`

---

## Step C — Task Execution

### Primary brains
- Brain #4 or Brain #5 depending on domain
- Brain #6
- Brain #7

### Pattern

1. Execution follows `tasks.md`, not free-form invention.
2. Backend-leaning tasks are guided mainly by Brain #4 logic.
3. Frontend-leaning tasks are guided mainly by Brain #5 logic.
4. Brain #6 governs testing and completion standards.
5. Brain #7 evaluates whether the completed task really matches the objective.

### Output
- implemented code
- updated `todo` / progress state
- verification state
- updated handoff

---

## Step D — Resume / Handoff

### Primary brains
- Brain #6
- Brain #7

### Pattern

1. Brain #6 ensures the handoff has enough validation context.
2. Brain #7 ensures the handoff is coherent and does not hide unresolved uncertainty.

### Output
- trustworthy `HANDOFF-CURRENT.md`
- exact next recommended task
- known blockers and risks

---

## Required Brain Questions by Artifact

## For `requirements.md`

Ask at least:
- Brain #1: Why does this objective matter for MVP?
- Brain #7: Is the scope focused enough to execute safely?

## For `design.md`

Ask at least:
- Brain #4: What architecture and boundary decisions matter most?
- Brain #5: What user-facing or frontend design constraints matter most?
- Brain #6: What testability or deployment constraints must be explicit?

## For `tasks.md`

Ask at least:
- Brain #4/#5: What is the correct dependency order?
- Brain #6: Which acceptance criteria are verifiable?
- Brain #7: Is the breakdown small and concrete enough for another model to execute?

## For `HANDOFF-CURRENT.md`

Ask at least:
- Brain #6: What validation context must be preserved?
- Brain #7: What exact next task should be recommended?

---

## Brain Rights in the Flow

### Brain #1 may challenge
- objective priority
- scope creep
- MVP relevance

### Brain #4 may challenge
- backend architecture inconsistency
- missing infrastructure dependencies
- unrealistic service/data assumptions

### Brain #5 may challenge
- UI sequencing mistakes
- poor UX decomposition
- frontend work hidden inside backend-heavy tasks

### Brain #6 may veto
- unverifiable acceptance criteria
- task completion claims without evidence
- unsafe release assumptions

### Brain #7 may veto
- roadmap incoherence
- objective package too vague for execution
- execution declared complete without enough proof

---

## What Brains Should Not Do

Brains should not:
- replace the plan artifacts with free-form discussion
- create undocumented scope changes during execution
- let vague tasks pass just because they sound reasonable
- declare work complete without acceptance evidence
- force another model to reconstruct intent from chat history

---

## Recommended Operating Rule

A model should not move from discovery to implementation unless the relevant brains have helped produce a package that is:

1. strategically justified
2. technically coherent
3. decomposed into executable tasks
4. verifiable
5. resumable

---

## Practical Example

For objective `project-state-realtime`:

- Brain #1 says: this is needed because live visibility is part of the operational promise.
- Brain #4 says: backend event streaming and event contracts must exist first.
- Brain #5 says: the UI should consume filtered events, not raw logs.
- Brain #6 says: acceptance must include event delivery and failure handling checks.
- Brain #7 says: the objective is valid only if the task breakdown is concrete enough to resume across model windows.

This produces a stronger objective package than any single model improvising alone.

---

## Summary

The software-development brains should support the hybrid workflow by contributing clear role-based judgment at each step:

- Brain #1 → objective meaning and priority
- Brain #4 → backend realism and dependencies
- Brain #5 → frontend realism and UX sequencing
- Brain #6 → verifiability and operational safety
- Brain #7 → synthesis quality and go/no-go judgment

This makes the workflow more robust, especially when work must continue across multiple models and sessions.
