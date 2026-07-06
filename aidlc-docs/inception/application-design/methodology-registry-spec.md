# Methodology Registry Spec

## Purpose

Define how MasterMind represents and selects development methodologies without
mixing them with low-level loops or transversal policies.

## Core Idea

The selector must choose a **route of work** composed from three layers:

1. **Harnesses** - major workflows such as Discovery, Onboarding, AI-DLC, SDD,
   or TDD.
2. **Loops** - execution repetitions such as tool, verify, review, recovery,
   or refactor.
3. **Policies** - cross-cutting rules such as Clean Code, Security, or
   Architecture constraints.

## Categories

### 1. Harnesses

Harnesses are the top-level methodologies the user can choose.

Examples:

- Discovery
- Onboarding
- AI-DLC
- SDD
- TDD
- Execution
- Verification
- Recovery

### 2. Loops

Loops are the repeated control units used inside a harness.

Examples:

- Tool Loop
- Goal Loop
- Verify Loop
- Review Loop
- Recovery Loop
- Refactor Loop

### 3. Policies

Policies are global constraints applied across harnesses.

Examples:

- Clean Code
- Security
- Architecture
- Naming
- Testing Discipline

## Classification Rules

- If the item defines a full workflow with its own start and finish, register
  it as a harness.
- If the item defines a repeated execution step, register it as a loop.
- If the item constrains behavior across multiple harnesses, register it as a
  policy.
- If an item can fit more than one layer, prefer the highest layer that keeps
  the smallest useful control surface.

## Suggested Mapping

- **SDD** -> harness
- **TDD** -> harness
- **Clean Code** -> policy
- **Verification** -> harness or loop, depending on whether it stands alone or
  is embedded inside another harness

## Required Metadata

Each methodology entry should declare:

- `methodology_id`
- `kind` (`harness`, `loop`, or `policy`)
- `name`
- `purpose`
- `inputs`
- `outputs`
- `prerequisites`
- `cost_level`
- `risk_level`
- `state`
- `version`
- `source_ref`
- `compatible_harnesses`
- `compatible_projects`

## Selection Rules

The selector must evaluate:

1. user intent
2. project maturity
3. task complexity
4. constraints
5. policy conflicts
6. reuse value

Selection must prefer the minimal route that satisfies the objective safely.

## Composition Rules

- A harness can include multiple loops.
- A policy can constrain many harnesses.
- A harness must never depend on a policy being implicit.
- A policy must never implement execution behavior by itself.

## Reuse Rules

- A new project may adopt a harness without adopting every policy.
- A policy may be enabled per project or per niche.
- The registry must keep harnesses reusable across projects through adapters.

## Acceptance Criteria

- The selector can differentiate harnesses, loops, and policies.
- `SDD` and `TDD` can be registered as first-class methodologies.
- `Clean Code` remains a policy, not a harness.
- The registry can support future methodologies without rewriting the core.
