# Moment 1 — Before ROADMAP

**When:** Before `/gsd:new-milestone` — you're about to define phases for a new milestone cycle.

**Goal:** Brains #1 (Product) and #7 (Evaluator) inform the phase structure with expert knowledge. You provide the project reality so they don't give you a generic answer.

---

## Step 1 — Read Current Reality

```bash
cat .planning/PROJECT.md           # What this is, requirements, constraints
cat .planning/BRAIN-FEED.md        # Accumulated patterns (if exists)
cat .planning/ROADMAP.md           # Previous roadmap (if exists)

# If phases exist, read last 2 SUMMARY.md files:
ls .planning/phases/*/SUMMARY.md | tail -2 | xargs cat
```

Extract:
- What was completed (features, patterns, tech decisions)
- What's deferred or known gaps
- Hard constraints (performance targets, security requirements)
- Current milestone brief (what the user wants to build next)

---

## Step 2 — Build Context Block

```
Project: MasterMind Framework — [current milestone name]
Stack: [from BRAIN-FEED.md or PROJECT.md]

[COMPLETED REALITY]
Milestone [prev]: [brief summary of what exists]
Proven patterns: [2-3 key architectural decisions]
Known gaps: [what was deferred]

[MILESTONE BRIEF]
Goal: [what this milestone needs to achieve]
Constraints: [hard limits — perf, security, timeline, scope]

[CORRECTED ASSUMPTIONS]
[What might Brain #1 assume wrong about the current state?]
[What scope creep risks should Brain #7 be aware of?]
```

---

## Step 3 — Query Brain #1 and Brain #7 in Parallel

**Brain #1 — Product Strategy** (`f276ccb3-0bce-4069-8b55-eae8693dbe75`)

Ask about phase structure and prioritization:
```
[context block from Step 2]

[WHAT I NEED]
I'm breaking this milestone into 3-5 phases. Help me:
1. Validate the phase order — is this the right sequence given dependencies?
2. Identify any phase that tries to do too much (scope risk)
3. Flag any missing phase — what am I not thinking about?
Focus: phase boundaries and sequencing. Not implementation details.
```

**Brain #7 — Growth/Data Evaluator** (`d8de74d6-7028-44ed-b4d4-784d6a9256e6`)

Ask about risk and blind spots:
```
[context block from Step 2]

[WHAT I NEED]
Evaluate this milestone plan with your critical lens:
1. Planning Fallacy risks — what am I underestimating?
2. Omission Bias — what critical phases am I not including?
3. Systems Thinking — what feedback loops or dependencies am I missing?
No generic advice. Give me specific concerns about this milestone structure.
```

---

## Step 4 — Filter Responses

For each concern raised:

| Concern type | Action |
|-------------|--------|
| Phase scope too large | Split it or identify what to defer |
| Missing phase identified | Add to ROADMAP with clear goal |
| Already covered elsewhere | Mark ✅ skip |
| Risk that's acceptable | Document as known constraint |

---

## Step 5 — Synthesize into ROADMAP Input

Update or inform the ROADMAP structure:
- Phase order (validated by Brain #1)
- Success criteria per phase (Brain #7's metrics lens)
- Known risks per phase (Brain #7's Planning Fallacy flags)

Write a brief synthesis comment in the ROADMAP:
```markdown
<!-- Milestone validated by Brain #1 + Brain #7 on [date] -->
<!-- Key insights: [2-3 bullet points] -->
```

---

## Done When

- [ ] Brain #1 validates phase sequence and boundaries
- [ ] Brain #7 identifies blind spots and Planning Fallacy risks
- [ ] All concerns filtered (✅ solved / 📅 deferred / 🔴 integrated)
- [ ] ROADMAP reflects brain insights (not just initial plan)
