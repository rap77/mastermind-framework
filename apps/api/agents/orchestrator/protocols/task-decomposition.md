# Task Decomposition Protocol

**Purpose:** Define how the Orchestrator breaks user briefs into atomic, executable tasks.

---

## Input

User brief (free text):
- Could be a single sentence
- Could be a paragraph
- Could be a structured requirement
- Could be vague and need clarification

---

## Process

### Step 1: Understand the Brief

**What to extract:**
- **Intent**: What does the user want to achieve?
- **Scope**: Big picture (new product) or small (fix bug)?
- **Domain**: Software development? Marketing? Operations?
- **Constraints**: Time, budget, team, tech stack?

**Clarification Questions (if brief is vague):**
- "What problem does this solve?"
- "Who is the target user?"
- "What is the timeline?"
- "What are the must-have vs nice-to-have features?"

### Step 2: Classify the Work Type

**Flow Detection Matrix:**

| Brief Indicators | Flow | Brains Involved |
|------------------|------|-----------------|
| "new app", "startup", "product from scratch" | `full_product` | 1→2→3→4→5→6→7 |
| "validate idea", "is this good?", "market fit" | `validation_only` | 1→7 |
| "design", "prototype", "UX/UI" | `design_sprint` | 1→2→3→7 |
| "implement", "build", "code this feature" | `build_feature` | 4→5→6→7 |
| "optimize", "improve metrics", "growth" | `optimization` | 7→1 |

**No Match?**
- Ask user: "What type of work is this?"
- Present options with brief descriptions

### Step 3: Create Atomic Tasks

**Task Atomicity Test:**
A task is atomic if it:
1. Has a single, clear objective
2. Can be assigned to ONE brain
3. Produces ONE output artifact
4. Can be completed independently (except for dependencies)

**Task Template:**

```yaml
task_id: "TASK-XXX"
brain_id: N
title: "[Verb] [noun] for [context]"
description: |
  Clear description of what needs to be done.
  Include context, constraints, expected outcome.
inputs:
  brief: "[Original user brief excerpt]"
  context: "[Additional context from previous tasks]"
  constraints: "[Any limitations or boundaries]"
expected_output:
  schema: "[schema name from brains.yaml]"
  format: "yaml"
dependencies: ["TASK-YYY"]  # or [] if first task
priority: N  # 1-10 scale
estimated_effort: "X hours"
```

**Example Tasks:**

```yaml
# Task 1: Product Strategy
task_id: "TASK-001"
brain_id: 1
title: "Define product strategy for travel companion app"
description: |
  Analyze the opportunity for a travel companion app in Chile.
  Define target persona, core value proposition, key features.
inputs:
  brief: "App para encontrar compañeros de viaje en Chile"
  context: "New product, Chile market, social/travel domain"
  constraints: "MVP scope, lean startup approach"
expected_output:
  schema: "product-brief"
  format: "yaml"
dependencies: []
priority: 10
estimated_effort: "30 min"

# Task 2: UX Research
task_id: "TASK-002"
brain_id: 2
title: "Conduct UX research for travel companion app"
description: |
  Define user research plan, interview structure, journey map.
  Inputs from product brief: persona, value prop, key features.
inputs:
  brief: "App para encontrar compañeros de viaje en Chile"
  context: "From TASK-001: target persona defined"
  product_brief: "[Reference to TASK-001 output]"
expected_output:
  schema: "ux-research-report"
  format: "yaml"
dependencies: ["TASK-001"]
priority: 9
estimated_effort: "45 min"
```

### Step 4: Build Dependency Graph

**Rules:**
1. Tasks must be ordered by dependencies
2. Circular dependencies are FORBIDDEN
3. Output of task N = input of task N+1 (if dependent)

**Dependency Types:**

| Type | Description | Example |
|------|-------------|---------|
| `sequential` | Task N+1 needs task N's output | UX Research needs Product Strategy |
| `parallel` | Tasks are independent | Frontend and Backend can run in parallel (not in MVP) |
| `gate` | Task N+1 waits for N to pass evaluation | UI Design waits for Product Strategy approval |

**Visual Example (full_product):**

```
TASK-001 (Brain 1)
    ↓ (sequential)
TASK-002 (Brain 2)
    ↓ (sequential)
TASK-003 (Brain 3)
    ↓ (sequential)
TASK-004 (Brain 4)
    ↓ (sequential)
TASK-005 (Brain 5)
    ↓ (sequential)
TASK-006 (Brain 6)
    ↓ (sequential)
TASK-007 (Brain 7)
```

### Step 5: Calculate Priorities

**Priority Formula:**

```
priority = (dependency_weight * 0.4) +
           (impact_weight * 0.3) +
           (risk_weight * 0.2) +
           (effort_weight * 0.1)
```

**Weights:**

| Factor | Scoring |
|--------|---------|
| **Dependency** | Blocks N other tasks → 10, blocks 1 → 2, none → 0 |
| **Impact** | Critical for success → 10, nice-to-have → 2 |
| **Risk** | High uncertainty → 10, well-understood → 2 |
| **Effort** | Quick win → 10, major effort → 2 |

---

## Output: Execution Plan

```yaml
execution_plan:
  plan_id: "PLAN-XXX"
  date: "YYYY-MM-DD"
  flow_type: "full_product"

  brief:
    original: "[User's original input]"
    clarified: "[Expanded version after Q&A if needed]"

  tasks:
    - task_id: "TASK-001"
      brain_id: 1
      title: "Define product strategy"
      dependencies: []
      priority: 10
      estimated_effort: "30 min"

    - task_id: "TASK-002"
      brain_id: 2
      title: "Conduct UX research"
      dependencies: ["TASK-001"]
      priority: 9
      estimated_effort: "45 min"

    # ... more tasks

  summary:
    total_tasks: N
    estimated_duration: "X hours"
    critical_path: ["TASK-001", "TASK-002", ...]  # Tasks that determine overall duration
    risks: []  # Potential issues to watch
```

---

## Special Cases

### Case 1: Brief is Too Vague

**Input:** "I want an app"

**Response:**
1. Ask: "What problem does it solve?"
2. Ask: "Who is it for?"
3. Ask: "What makes it different?"
4. Wait for clarification
5. Then proceed with decomposition

### Case 2: Brief Spans Multiple Flows

**Input:** "Design and implement a dashboard for analytics"

**Response:**
1. This could be `design_sprint` + `build_feature`
2. Option A: Treat as `full_product` (simpler)
3. Option B: Ask user: "Do you want design AND code, or just design?"
4. Proceed based on answer

### Case 3: Brief Includes Existing Work

**Input:** "Here's the UX research, now design the UI"

**Response:**
1. Acknowledge existing work
2. Start from appropriate task (skip TASK-001, TASK-002)
3. Execution plan starts at TASK-003 (UI Design)

---

## Quality Checks

Before presenting execution plan:
- [ ] All tasks have unique task_ids
- [ ] All tasks have assigned brain_id
- [ ] All dependencies are valid (refer to existing tasks)
- [ ] No circular dependencies
- [ ] At least one task has no dependencies (entry point)
- [ ] All tasks have clear descriptions
- [ ] Estimated effort is reasonable

---

**Version:** 1.0.0
**Last Updated:** 2026-02-24
