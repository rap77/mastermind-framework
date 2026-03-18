# Escalation Protocol

**Purpose:** Define when and how the Orchestrator escalates to human intervention.

---

## What is Escalation?

Escalation is the **safety mechanism** of the MasterMind Framework. When the system cannot proceed autonomously, it pauses and requests human intervention.

**Escalation ≠ Failure**
- It's a guardrail against low-quality outputs
- It's a learning opportunity (precedents are created)
- It's rare (should happen <5% of tasks)

---

## Escalation Triggers

### Automatic Triggers

| Trigger | Description | Action |
|---------|-------------|--------|
| **3 consecutive rejections** | Brain #7 rejects same output 3 times | ESCALATE immediately |
| **Coherence failure** | Output contradicts previous outputs | ESCALATE immediately |
| **Unknown domain** | Brief is outside known expertise | ASK human |
| **Critical issue** | Brain #7 identifies safety/legal/ethical issue | ESCALATE immediately |
| **Timeout** | Brain doesn't respond within timeout | ESCALATE after retry |
| **Human request** | User explicitly asks for human review | ESCALATE on request |

### Manual Triggers

The Orchestrator may choose to escalate when:
- Brief is ambiguous even after clarification questions
- Multiple valid approaches exist with equal trade-offs
- User's request conflicts with best practices
- Technical constraints prevent implementation

---

## Escalation Process

```
┌─────────────────────────────────────────────────────────────┐
│  Escalation Trigger Activated                               │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│  Pause Execution                                            │
│  - Stop current task                                        │
│  - Save state for resume                                    │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│  Create Escalation Report                                   │
│  - What triggered escalation                                │
│  - What has been attempted                                  │
│  - Outputs seen so far                                      │
│  - Recommendation for human                                 │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│  Notify Human                                               │
│  - Present escalation report                                │
│  - Wait for intervention                                    │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│  Human Intervention                                         │
│  - Reviews context                                          │
│  - Provides resolution or guidance                          │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│  Create Precedent (if applicable)                           │
│  - Document what caused escalation                           │
│  - Document how it was resolved                             │
│  - Create rule for future                                  │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│  Resume Execution                                           │
│  - Apply human's resolution                                 │
│  - Continue from paused state                               │
└─────────────────────────────────────────────────────────────┘
```

---

## Escalation Report Format

```yaml
escalation_report:
  escalation_id: "ESC-XXX"
  timestamp: "YYYY-MM-DDTHH:MM:SSZ"
  severity: "low" | "medium" | "high" | "critical"

  trigger:
    type: "third_rejection" | "coherence_failure" | "unknown_domain" |
          "critical_issue" | "timeout" | "human_request" | "manual"
    description: "Human-readable explanation"

  context:
    plan_id: "PLAN-XXX"
    current_task_id: "TASK-XXX"
    current_brain_id: N
    flow_type: "full_product"
    position_in_flow: N

  brief:
    original: "[User's original input]"
    clarified: "[Expanded version if clarification was sought]"

  attempts:  # For rejection-based escalations
    total_attempts: 3
    attempt_1:
      timestamp: "..."
      output_summary: "..."
      veredict: "REJECT"
      score: 45
      feedback: "[...]"
    attempt_2:
      timestamp: "..."
      output_summary: "..."
      veredict: "REJECT"
      score: 52
      feedback: "[...]"
    attempt_3:
      timestamp: "..."
      output_summary: "..."
      veredict: "REJECT"
      score: 48
      feedback: "[...]"

  outputs_seen:  # Full outputs for reference
    - attempt: 1
      output: "[Full YAML output from attempt 1]"
    - attempt: 2
      output: "[Full YAML output from attempt 2]"
    - attempt: 3
      output: "[Full YAML output from attempt 3]"

  evaluation_summary:
    common_issues:
      - "Missing competitive analysis in all attempts"
      - "Persona not specific enough"
      - "Assumptions not declared"
    score_trend: [45, 52, 48]  # No improvement
    evaluator_note: "Brain #1 appears unable to produce acceptable output"

  recommendation: |
    Based on the pattern of rejections, it appears that:
    1. The brief may be unclear or incomplete
    2. Brain #1 may lack context specific to this domain
    3. Human guidance is needed to clarify expectations

    Suggested actions:
    1. Review brief with user for clarity
    2. Provide example of expected output
    3. Consider if this requires different expertise

  action_required:
    type: "guidance" | "override" | "clarification" | "example"
    description: "What human needs to provide"

  precedent_created: null  # Will be filled after resolution
```

---

## Human Response Format

After reviewing the escalation report, the human should respond:

```yaml
human_response:
  escalation_id: "ESC-XXX"
  timestamp: "YYYY-MM-DDTHH:MM:SSZ"
  responder: "human"  # or specific name/role

  action: "provide_guidance" | "override_evaluation" | "clarify_brief" | "provide_example" | "cancel_task"

  guidance: |
    [If action = provide_guidance]
    Specific instructions for the brain to follow.
    Can include examples, constraints, or corrections.

  override: |
    [If action = override_evaluation]
    "Ignore Brain #7's rejection, accept the output and continue."
    Optionally include reason for precedent creation.

  clarification: |
    [If action = clarify_brief]
    Expanded or corrected version of the original brief.

  example: |
    [If action = provide_example]
    Example of what the expected output should look like.

  cancel: false  # If true, stop execution entirely
```

---

## Post-Escalation Actions

### If Human Provides Guidance

1. Update task with human's guidance
2. Re-invoke the brain with:
   - Original task
   - Human's guidance as additional context
   - Reset rejection counter (fresh start with guidance)
3. Continue evaluation loop

### If Human Overrides Evaluation

1. Accept the current output despite #7's rejection
2. Log the override
3. Create precedent:
   ```yaml
   precedent:
     id: "PREC-XXX"
     issue: "Evaluator rejected output that human approved"
     resolution: "Human overrode evaluator, output accepted"
     decided_by: "human"
     rule_created: "In cases like [X], human judgment takes precedence"
   ```
4. Continue to next task

### If Human Clarifies Brief

1. Update brief with clarification
2. Restart task decomposition with clarified brief
3. May result in different flow or tasks

### If Human Cancels Task

1. Mark execution as "cancelled_by_human"
2. Save all outputs for reference
3. Ask for reason (for learning)

---

## Creating Precedents from Escalations

After EVERY escalation, create a precedent if:

1. **Pattern identified**: "This is the 3rd time this type of issue occurred"
2. **New rule learned**: "In future, do X when Y happens"
3. **Human preference**: "Human prefers approach A over B"

**Precedent Template:**

```yaml
precedent:
  id: "PREC-XXX"
  date: "YYYY-MM-DD"
  escalation_id: "ESC-XXX"

  issue: |
    Clear description of what caused the escalation.
    What went wrong? What was the pattern?

  resolution: |
    How did the human resolve it?
    What guidance was provided?

  decided_by: "human"
  role: "product_owner"  # Optional: specific role

  rule_created: |
    The rule derived from this escalation.
    "In future cases where [condition], do [action]."

  applies_to: ["brain-1"]  # Which brains this applies to
  context_tags: ["travel", "b2c", "marketplace"]  # When this applies

  condition: |
    When this condition is met, apply this precedent.

  action: |
    What to do when the condition is met.

  examples: []  # Optional: examples of when to apply

  occurrences: 1  # Increment each time this precedent is applied
```

---

## State Persistence

When escalation occurs:

1. **Save execution state:**
   ```yaml
   execution_state:
     plan_id: "PLAN-XXX"
     status: "escalated"
     escalation_id: "ESC-XXX"
     completed_tasks: ["TASK-001"]
     current_task: "TASK-002"
     paused_at: "YYYY-MM-DDTHH:MM:SSZ"
     state_snapshot: {...}  # Full state for resume
   ```

2. **Store in checkpoint:** `logs/checkpoints/PLAN-XXX_escalated.yaml`

3. **Resume capability:** Execution can be resumed from exact point

---

## Escalation Metrics

Track to improve system:

```yaml
escalation_metrics:
  period: "2026-02"
  total_escalations: N
  escalation_rate: "N%"  # escalations / total tasks

  by_trigger:
    third_rejection: N
    coherence_failure: N
    unknown_domain: N
    critical_issue: N
    timeout: N
    human_request: N
    manual: N

  by_brain:
    brain_1: N
    brain_2: N
    # ...

  by_severity:
    low: N
    medium: N
    high: N
    critical: N

  resolution_time:
    avg_minutes: N
    median_minutes: N

  precedents_created: N  # How many escalations became precedents
```

---

## Special Cases

### Case 1: Escalation Loop

If same task escalates multiple times:
1. After 2nd escalation: Require different human reviewer
2. After 3rd escalation: Suspend task, require root cause analysis

### Case 2: Conflicting Human Guidance

If Human A says X, Human B says Y:
1. Log both opinions
2. Escalate to designated authority
3. Create precedent only after consensus

### Case 3: Emergency Escalation

If critical issue detected (safety, legal, ethical):
1. IMMEDIATE escalation, highest priority
2. Bypass normal channels
3. Require prompt human response

---

**Version:** 1.0.0
**Last Updated:** 2026-02-24
