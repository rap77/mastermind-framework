---
name: ui-ux-routing
description: Routes OpenCode UI/UX work to the appropriate installed design skills. Use when a MasterMind task involves pages, components, prototypes, design systems, accessibility reviews, or animation polish; this adapter is not the executable MM-Flow harness.
metadata:
  author: mastermind
  version: "1.0.0"
---

# UI/UX Skill Routing Adapter

Use this OpenCode adapter to route UI/UX work through the smallest set of
specialized skills that can complete the task safely. The executable harness is
specified in
[`docs/canonical/110-UI-UX-HARNESS-RUNTIME-CONTRACT.md`](../../../docs/canonical/110-UI-UX-HARNESS-RUNTIME-CONTRACT.md)
and will live under `.mm-flow/harness-library/` when implemented.

## Project Boundaries

Before designing:

1. Read the active objective and relevant project requirements.
2. Inspect the existing UI, design system, stack, and component conventions.
3. Apply the UI/UX doctrine from
   [`docs/canonical/22-ENGINEERING-DOCTRINE-LAYER.md`](../../../docs/canonical/22-ENGINEERING-DOCTRINE-LAYER.md).
4. Follow the canonical runtime contract in
   [`docs/canonical/110-UI-UX-HARNESS-RUNTIME-CONTRACT.md`](../../../docs/canonical/110-UI-UX-HARNESS-RUNTIME-CONTRACT.md).
5. Keep project state, scope, and tasks in the main project harness. This
   adapter helps produce design artifacts and implementation changes; it does
   not create a parallel task system.

## Route The Request

| Request | Required Skills | Optional Skills |
| --- | --- | --- |
| Production page/component implementation | `frontend-design` | stack-specific skills, `emil-design-eng` |
| Design direction or design system | `ui-ux-pro-max` | `frontend-design` |
| High-fidelity HTML prototype, slides, infographic, or video export | `huashu-design` | `emil-design-eng` |
| Accessibility or interface compliance review | `web-design-guidelines` | `frontend-code-review` |
| Motion implementation or polish | `emil-design-eng` | `apple-design`, `review-animations` |
| Codebase-wide motion audit and plans | `improve-animations` | none |

Load only the required skills for the current phase. Do not load all design
skills by default.

## Workflow

### 1. Intake

Establish:

- user and business goal
- target screen or flow
- production implementation vs. visual prototype
- existing brand and design assets
- target devices and accessibility requirements
- framework and design-system constraints

Ask one concise question only when a missing answer changes the implementation
direction. Otherwise inspect the repository and proceed.

### 2. Context

Inspect before creating:

- existing components and tokens
- typography, color, spacing, and motion conventions
- responsive behavior
- loading, empty, error, and permission states
- active objective acceptance criteria

Preserve an established visual language. Use design exploration only when the
project has no usable direction or the user explicitly requests alternatives.

### 3. Direction

For system-level direction, load `ui-ux-pro-max` and generate a concise design
system or page direction. Treat its output as a recommendation, not as project
truth. Existing project tokens and explicit user constraints win.

The installed `ui-ux-pro-max` guidance contains a React Native-only stack
assumption. Ignore that assumption in MasterMind. Detect the target stack from
the files being changed and load the corresponding stack-specific skills.

For ambiguous visual work, produce a small number of meaningfully different
directions. Do not ask the user to choose between labels without showing the
visual consequences.

### 4. Produce

- Use `frontend-design` for production UI.
- Use `huashu-design` for prototypes and visual artifacts, not production apps
  with backend behavior.
- Use stack-specific skills when changing framework code.
- Keep implementation responsive on mobile and desktop.
- Include necessary interaction and edge states.

### 5. Craft

Load `emil-design-eng` when motion or interaction feel materially affects the
experience. Add `apple-design` only for gesture-driven, spring-based, spatial,
or material interactions. Prefer restraint over decorative motion.

### 6. Review

For production UI, run a final review with `web-design-guidelines`. Fetch its
current upstream rules as required by that skill. Add `review-animations` when
motion exists.

Resolve high-confidence findings before delivery. Report unresolved tradeoffs
with file and line references.

### 7. Runtime Validation

For browser-facing work, validate the actual rendered result when browser tools
are available:

- desktop and mobile layouts
- keyboard and focus behavior
- console errors
- loading and empty states
- reduced-motion behavior when animation exists

## Completion Contract

UI/UX work is complete only when:

- the output satisfies the active objective
- the visual direction is intentional and project-consistent
- mobile and desktop behavior are valid
- accessibility and interaction guardrails pass
- production code uses project conventions
- remaining risks or unverified runtime behavior are stated explicitly

## Anti-Patterns

- Loading every design skill for every request
- Replacing project tokens with a generated design system without evidence
- Using `huashu-design` as the production application architecture
- Treating visual polish as a substitute for usability
- Reviewing source code without checking rendered behavior when runtime tools
  are available
- Creating a separate UI/UX roadmap disconnected from the active objective
