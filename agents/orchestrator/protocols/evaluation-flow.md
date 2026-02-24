# Evaluation Flow Protocol

**Purpose:** Define how the Orchestrator iterates with Brain #7 (Critical Evaluator) to ensure quality.

---

## Overview

EVERY output from brains #1-6 MUST be evaluated by Brain #7 before:
1. Proceeding to the next brain in the flow
2. Delivering the final result to the user

This creates a **quality gate** after each brain.

---

## The Evaluation Loop

```
┌─────────────────────────────────────────────────────────────┐
│  Brain N (1-6) produces output                              │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│  Orchestrator sends output to Brain #7                      │
│  - Include: task_id, brain_id, full output, context         │
│  - Specify: evaluation_matrix to use                        │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│  Brain #7 evaluates                                         │
│  - Applies evaluation matrix                                │
│  - Checks for biases, completeness, quality, honesty        │
│  - Calculates score (0-100)                                  │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│  Brain #7 returns veredict:                                 │
│  - APPROVE (score >= 80)                                    │
│  - CONDITIONAL (60 <= score < 80)                           │
│  - REJECT (score < 60)                                      │
│  - ESCALATE (special cases)                                 │
└────────────────────┬────────────────────────────────────────┘
                     │
        ┌────────────┼────────────┐
        │            │            │
        ▼            ▼            ▼
    APPROVE     CONDITIONAL    REJECT/ESCALATE
        │            │            │
        ▼            ▼            ▼
   Continue    Apply      Re-assign or
   to next     notes      escalate
   brain       and
               continue/
               re-work
```

---

## Evaluation Request Format

```yaml
evaluation_request:
  request_id: "EVAL-XXX"
  timestamp: "YYYY-MM-DDTHH:MM:SSZ"

  task:
    task_id: "TASK-001"
    brain_id: 1
    brain_name: "Product Strategy"
    title: "Define product strategy for travel companion app"

  output:
    schema: "product-brief"
    content: |
      [Full YAML/JSON output from Brain #1]

  evaluation:
    matrix: "product-brief"  # From skills/evaluator/evaluation-matrices/
    criteria:
      - "completeness"
      - "quality"
      - "honesty"
      - "viability"

  context:
    flow: "full_product"
    position_in_flow: 1  # First task
    user_brief: "App para encontrar compañeros de viaje en Chile"
    previous_outputs: []  # None for first task
    precedents: []  # Relevant precedents if any

  rejection_info:
    current_count: 0  # 0, 1, or 2
    max_allowed: 3
    previous_feedback: []  # Feedback from previous rejections
```

---

## Handling Veredicts

### APPROVE (score >= 80)

**Action:**
1. Mark task as completed
2. Store output for next task
3. Continue to next brain in flow

**Update state:**
```yaml
task_status:
  task_id: "TASK-001"
  status: "completed"
  evaluation:
    veredict: "APPROVE"
    score: 87
    evaluated_at: "YYYY-MM-DDTHH:MM:SSZ"
  output_stored: true
```

### CONDITIONAL (60 <= score < 80)

**First, analyze #7's notes:**
- Are they **minor** (typos, formatting, small additions)?
  → Apply notes, mark complete, continue
- Are they **major** (missing sections, weak analysis)?
  → Return to brain with notes, increment rejection counter

**Action (minor notes):**
```yaml
task_status:
  task_id: "TASK-001"
  status: "completed_with_notes"
  evaluation:
    veredict: "CONDITIONAL"
    score: 72
    notes:
      - "Add specific metric for retention"
      - "Clarify pricing model"
  applied: true
```

**Action (major issues):**
```yaml
task_status:
  task_id: "TASK-001"
  status: "re_work"
  evaluation:
    veredict: "CONDITIONAL"
    score: 65
    notes:
      - "Missing competitive analysis section"
      - "Persona too generic"
  rejection_count: 1
```

### REJECT (score < 60)

**Action:**
1. Extract #7's feedback (specific, actionable)
2. Return task to same brain with:
   - Original output
   - #7's feedback
   - Relevant precedents (if any)
   - Rejection counter
3. Wait for revised output

**Re-assignment format:**
```yaml
task_revision:
  task_id: "TASK-001"
  brain_id: 1
  attempt: 2  # Second try

  original_output: |
    [What Brain #1 produced first]

  feedback:
    from: "brain-7"
    veredict: "REJECT"
    score: 45
    specific_issues:
      - "No specific persona defined"
      - "No competitive analysis"
      - "Missing 3 of 5 required sections"
      - "Assumptions not declared"
    suggestions:
      - "Define persona with age, location, pain points"
      - "Analyze at least 3 competitors"
      - "Complete all required sections"

  precedents_to_apply:
    - id: "PREC-012"
      rule: "Always declare assumptions explicitly in product briefs"

  rejection_count: 1
  max_rejections: 3
```

### ESCALATE

**Triggers for immediate escalation:**
1. Third consecutive rejection
2. Coherence failure (output contradicts previous outputs)
3. Unknown domain or scenario
4. Human explicitly requested
5. Brain #7 detects critical issue requiring human judgment

**Action:**
1. Pause execution immediately
2. Create escalation report
3. Notify human
4. Wait for intervention

**Escalation report:**
```yaml
escalation_report:
  escalation_id: "ESC-XXX"
  timestamp: "YYYY-MM-DDTHH:MM:SSZ"
  severity: "high"  # low, medium, high

  trigger:
    type: "third_rejection"  # or "coherence_failure", "unknown_domain", etc.
    description: "Brain #1 failed to produce acceptable output after 3 attempts"

  task:
    task_id: "TASK-001"
    brain_id: 1
    title: "Define product strategy"
    attempts: 3

  evaluation_history:
    - attempt: 1
      veredict: "REJECT"
      score: 45
      feedback: "[...]"
    - attempt: 2
      veredict: "REJECT"
      score: 52
      feedback: "[...]"
    - attempt: 3
      veredict: "REJECT"
      score: 48
      feedback: "[...]"

  outputs_seen: [...]  # All 3 outputs for reference

  recommendation: |
    Brain #1 appears to lack sufficient context or the brief may be unclear.
    Recommended actions:
    1. Review original brief with user
    2. Clarify specific requirements
    3. Consider if this is within Brain #1's domain

  action_required: "Human intervention needed"
```

---

## State Management

### Rejection Counter

Track per `(task_id, brain_id)`:
- Resets after successful completion
- Does NOT reset between sessions (persist in state)
- Resets to 0 if human intervenes

### Precedents Created

If #7 identifies a pattern:
```yaml
precedent_created:
  id: "PREC-XXX"
  pattern: "Brain #1 repeatedly omits competitive analysis"
  rule: "Always include competitive analysis in product briefs"
  applies_to: ["brain-1"]
  created_from: "evaluation_result"
```

### Quality Gates

Pass through gates defined in `thresholds.yaml`:
```yaml
quality_gates:
  - name: "strategy_gate"
    after_brain: 1
    passed: true
    score: 87
    minimum: 70
```

---

## Special Cases

### Case 1: Brain #7 Itself Needs Revision

If Brain #7 produces a low-quality evaluation:
- This is unusual (Brain #7 is the evaluator)
- Escalate immediately
- Human reviews both outputs

### Case 2: Multiple Brains in Parallel (Future)

If tasks can run in parallel (not in MVP):
- Evaluate each independently
- Wait for ALL to pass before continuing
- If one fails, others wait

### Case 3: User Overrides Evaluation

If user says "Ignore #7, continue anyway":
- Log the override
- Ask for reason (for precedent creation)
- Continue with user's decision
- DO NOT escalate (user is the ultimate authority)

---

## Logging

All evaluations are logged:
```yaml
evaluation_log:
  eval_id: "EVAL-XXX"
  timestamp: "YYYY-MM-DDTHH:MM:SSZ"
  task_id: "TASK-001"
  brain_id: 1
  veredict: "APPROVE"
  score: 87
  duration_ms: 450
  evaluator_version: "1.0.0"
```

Logs stored in: `logs/evaluations/`

---

**Version:** 1.0.0
**Last Updated:** 2026-02-24
