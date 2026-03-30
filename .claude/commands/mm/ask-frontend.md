---
description: Consult Frontend brain about frontend architecture and implementation
argument-hint: "[your question about frontend, React, Next.js, state management, performance]"
---

<objective>
Query the Frontend brain (Brain #4) via Agent dispatch. Brain #4 has cross-domain context injected
from the Backend feed via SYNC tags — this enriches its architectural recommendations.
</objective>

<context>
Project reality: @.planning/BRAIN-FEED.md
Domain feed: @.planning/BRAIN-FEED-04-frontend.md
Backend feed (for SYNC resolution): @.planning/BRAIN-FEED-05-backend.md
</context>

<process>

## Phase A — SYNC Tag Resolution

Brain #4's feed has SYNC tags pointing to BRAIN-FEED-05-backend.md.

1. Read `.planning/BRAIN-FEED-04-frontend.md` — scan for `[SYNC: BF-05-XXX]` tags
2. For each tag found, read the referenced section from `.planning/BRAIN-FEED-05-backend.md`
3. Extract only the referenced section (not the full backend feed)
4. Prepare inline injection: `"INJECTED FROM BRAIN-FEED-05: [extracted text]"`
5. If a section is not found: log warning, continue without injection

## Phase B — Dispatch brain-04-frontend

Dispatch `brain-04-frontend` using the Task tool:

```
Task(
    subagent_type="brain-04-frontend",
    prompt="""
[IMPLEMENTED REALITY]
[Paste relevant entries from global + frontend feeds]

[CROSS-DOMAIN CONTEXT — INJECTED FROM BRAIN-FEED-05]
[Paste the resolved BF-05 sections here, if any SYNC tags were found]

[WHAT I NEED]
$ARGUMENTS

Focus: Frontend architecture specific to Next.js 16 App Router + React 19 + @xyflow/react v12 + Zustand 5.
Performance invariants: O(1) selectors, RAF batching, no unnecessary re-renders.
No generic React patterns. Specific to THIS codebase.
"""
)
```

</process>

<success_criteria>
- Frontend brain received cross-domain Backend context via SYNC injection
- Architecture recommendations specific to the implemented stack
- Performance patterns cited from BRAIN-FEED-04
</success_criteria>
