# Brain Selection Reference

## Brain Directory (Software Dev Niche)

| ID | Brain | Notebook ID | Domain | Key Experts |
|----|-------|-------------|--------|-------------|
| 1 | Product Strategy | `f276ccb3-0bce-4069-8b55-eae8693dbe75` | Vision, discovery, prioritization | Cagan, Torres, Ries, Doerr |
| 2 | UX Research | `ea006ece-00a9-4d5c-91f5-012b8b712936` | User flows, interactions, usability | Norman, Nielsen, Hall |
| 3 | UI Design | `8d544475-6860-4cd7-9037-8549325493dd` | Visual design, components, accessibility | Cooper, Wroblewski, Saffer |
| 4 | Frontend | `85e47142-0a65-41d9-9848-49b8b5d2db33` | Architecture, performance, state | Abramov, Markbåge |
| 5 | Backend | `c6befbbc-b7dd-4ad0-a677-314750684208` | APIs, data modeling, infra | Fowler, Evans |
| 6 | QA/DevOps | `74cd3a81-1350-4927-af14-c0c4fca41a8e` | Testing strategy, CI/CD, reliability | Humble, Majors |
| 7 | Growth/Data (Evaluator) | `d8de74d6-7028-44ed-b4d5-784d6a9256e6` | Validation, systems thinking, metrics | Balfour, Kohavi, Munger |

> Brain #8 (Master Interviewer) — notebook_id: `5330e845-29dc-4219-9d7e-c1ccb4851bb3` — for discovery sessions only.

## Quick Selection

| Question type | Brains |
|---------------|--------|
| Should we build this? What's the value? | #1 + #7 |
| How do users flow through this? | #2 |
| How should it look, feel, animate? | #3 |
| How do we build the frontend? | #4 (+ #2 if UX-heavy) |
| How do we build the backend? | #5 (+ #6 if infra-heavy) |
| How do we test / monitor this? | #6 |
| Is this plan good? What's missing? | #7 (always last) |
| Visual + interaction decisions together | #2 + #3 in parallel |
| Full-stack feature | #4 + #5 in parallel → #6 → #7 |

## Standard Sequences by Phase Type

### Frontend-heavy phase (e.g., The Nexus)
```
Moment 2: #2 (UX) + #3 (UI) + #4 (Frontend) + #6 (QA) — all in parallel
Moment 3: #7 validates — cascade gaps to domain brain
```

### Backend-heavy phase (e.g., API endpoints)
```
Moment 2: #5 (Backend) + #6 (QA/DevOps) in parallel
Moment 3: #7 validates
```

### Full product feature
```
Moment 2: #1 → then #2 + #3 + #4 + #5 in parallel → #6 → #7
```

### Architecture / Roadmap decision
```
Moment 1: #1 + #7 in parallel
```

## Cascade Rules

When Brain-07 raises a concern in Moment 3:

| Concern domain | Cascade to |
|---------------|-----------|
| Visual design gap | #3 UI Design |
| UX flow gap | #2 UX Research |
| Frontend architecture gap | #4 Frontend |
| Backend contract gap | #5 Backend |
| Test strategy gap | #6 QA/DevOps |
| Value/priority concern | #1 Product Strategy |

**Important:** Cascade with the same `[IMPLEMENTED REALITY]` block. Don't start fresh.

## Agent Dispatch Pattern

All brain consultation uses the `Agent` tool with the appropriate `subagent_type`:

```
Agent(
    subagent_type="brain-04-frontend",
    prompt="[IMPLEMENTED REALITY] + [CORRECTED ASSUMPTIONS] + [WHAT I NEED]"
)
```

Each brain agent is autonomous — it:
1. Reads its own `BRAIN-FEED-NN-domain.md` + global `BRAIN-FEED.md`
2. Queries its NotebookLM notebook via MCP (configured in agent frontmatter)
3. Filters response against codebase (Read, Grep, Glob tools)
4. Writes insights to its own domain feed
5. Returns structured output to the orchestrator

**No CLI or direct MCP calls needed** — agents handle everything internally.

### Cross-Brain Communication (Option D)

Brain #7 does NOT receive domain outputs inline. Instead:
1. Orchestrator writes domain outputs to `NN-BRAIN-OUTPUTS.md`
2. Brain #7 reads the file as part of its evaluation protocol
3. Orchestrator stays thin — receives only the verdict

```
Agent(
    subagent_type="brain-07-growth",
    prompt="Read .planning/phases/NN-name/NN-BRAIN-OUTPUTS.md before evaluating. [context]"
)
```
