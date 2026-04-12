# GSD Analysis + Custom Framework Vision

**Date:** 2026-03-22
**Status:** Research complete, documented in `.planning/research/GSD-FRAMEWORK-ANALYSIS.md`

## Key Findings

GSD = 12 agents + 30 workflows + gsd-tools.cjs. Strengths: goal-backward methodology, wave parallelization, atomic commits, deviation rules, revision loops. All worth keeping.

Limitations: hardcoded to software dev, no agent registry, no plugin system, no DSL, no brain integration, fixed checkpoint types, manual context inheritance, 1500-3000 line agent prompts.

## Custom Framework Vision (v3.0+)

MasterMind Workflow Framework — niche-agnostic, brain-integrated:
1. Declarative orchestration DSL (YAML workflows, not bash scripts)
2. Pluggable agent registry (add domain agents without touching orchestrator)
3. Brain integration layer (intermediary protocol at every gate)
4. Domain-agnostic verification (pluggable anti-pattern detectors per niche)
5. Niche-specific flow templates (software dev, marketing, design, etc.)
6. Custom checkpoint types (brain-approval, customer-feedback, stakeholder-review)
7. Accumulated learning via two-level BRAIN-FEED

## Evolution Path
- v2.1: Use GSD as-is + mm:brain-context skill (current)
- v2.2: Brain agents (subagents) — still on top of GSD
- v3.0: Custom framework replaces GSD workflows — keeps strengths, adds brain integration + niche support
