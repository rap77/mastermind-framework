---
description: Consult ALL 7 MasterMind brains simultaneously via parallel Agent dispatch
argument-hint: "[your question requiring comprehensive multi-domain analysis]"
---

<objective>
Query all 6 domain brain agents simultaneously (parallel dispatch) and Brain #7 as evaluator after.
Returns: 6 domain expert perspectives + Brain #7 synthesis with Delta-Velocity score.

Architecture: Phase A (SYNC resolution) → Phase B (6 domain brains, 1 message) → Phase C (Brain #7 after all return).
Expected T1: ~90-110s vs previous ~210-270s sequential MCP.
</objective>

<context>
Project reality: @.planning/BRAIN-FEED.md
Domain feeds: @.planning/BRAIN-FEED-01-product.md @.planning/BRAIN-FEED-02-ux.md @.planning/BRAIN-FEED-03-ui.md @.planning/BRAIN-FEED-04-frontend.md @.planning/BRAIN-FEED-05-backend.md @.planning/BRAIN-FEED-06-qa.md
</context>

<process>

## Phase A — SYNC Tag Resolution (Pre-Dispatch)

Before dispatching, resolve inline SYNC tags for agents that have them.

Scan each domain feed for `[SYNC: BF-NN-ID]` tags. For each tag:
1. Open the owner feed (`.planning/BRAIN-FEED-{NN}-{domain}.md`)
2. Extract only the referenced section (search for the section ID)
3. Store as inline injection: `"INJECTED FROM BRAIN-FEED-{NN}: [text]"`
4. If section not found: log warning, continue without injection

Cross-talk rule: Brain #4's prompt gets BF-05 fragments ONLY. No other agent receives SYNC injections from other agents' feeds. Build a per-brain injection map.

## Phase B — Parallel Domain Dispatch (Single Orchestrator Message)

Dispatch these 6 domain brains SIMULTANEOUSLY in a SINGLE orchestrator message:

- `brain-01-product` — Include: global feed + domain feed + WHAT I NEED (product strategy perspective for: $ARGUMENTS)
- `brain-02-ux` — Include: global feed + domain feed + WHAT I NEED (UX/research perspective for: $ARGUMENTS)
- `brain-03-ui` — Include: global feed + domain feed + WHAT I NEED (UI/design perspective for: $ARGUMENTS)
- `brain-04-frontend` — Include: global feed + domain feed + [INJECTED BF-05 fragments if any] + WHAT I NEED (frontend architecture perspective for: $ARGUMENTS)
- `brain-05-backend` — Include: global feed + domain feed + WHAT I NEED (backend/API perspective for: $ARGUMENTS)
- `brain-06-qa` — Include: global feed + domain feed + WHAT I NEED (QA/reliability perspective for: $ARGUMENTS)

All 6 in one message. Wait for all to return.

## Phase C — Brain #7 Evaluation (After Phase B Completes)

Only after ALL 6 domain agents return: dispatch `brain-07-growth` with:

```
[DOMAIN AGENT OUTPUTS — paste all 6 returns]

[ANTI-MEDIOCRE CONSTRAINT]
Do NOT reconcile contradictions. Name the conflict. Pick the strongest expert position.

[WHAT I NEED]
Evaluate these 6 domain outputs. Return:
1. Global Rating (0-100) — health of this dispatch
2. Brain Alerts — Rating 1 or 2 violations
3. Consolidated View — synthesis naming all conflicts and picking winners
4. Delta-Velocity vs Phase 09 baselines (target: 3.5-4.5)
5. Human-review flags — cross-domain patterns for global feed (flag only, do NOT write)
```

</process>

<success_criteria>
- 6 domain brains returned expert perspectives simultaneously
- Brain #7 received all 6 outputs and returned synthesis with verdict
- Global BRAIN-FEED.md unchanged (READ-ONLY — agents do not write it)
- All recommendations grounded in codebase reality (not generic advice)
</success_criteria>
