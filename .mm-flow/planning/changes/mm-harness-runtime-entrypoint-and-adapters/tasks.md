# Tasks — mm-harness-runtime-entrypoint-and-adapters

## Execution Rules

- Execute tasks in dependency order unless parallelization is explicitly safe.
- Update this file and the handoff when a task is completed or blocked.
- Each task must declare purpose, dependencies, likely file touchpoints, validation commands, and acceptance criteria.
- Treat this objective as **harness-sensitive**: prefer changes that are additive and safe between tasks in linked projects.

## T1: Tighten the objective package and define the CLI contract

### Purpose

Convert this package from a generic scaffold into an execution-ready harness objective by defining the exact CLI contract, compatibility boundaries, and rollout constraints.

### Depends On

None

### Parallelizable

no

### Files / Areas Likely Touched

- `requirements.md`
- `design.md`
- `tasks.md`
- `todo.md`
- `HANDOFF-CURRENT.md`

### Validation Commands

```bash
python3 .mm-flow/commands/mm/discover-contract-check.py --objective mm-harness-runtime-entrypoint-and-adapters
```

### Acceptance Criteria

- [x] The package defines the canonical CLI contract (`mm ...`) explicitly
- [x] Core vs adapters boundaries are documented concretely
- [x] Rollout and compatibility constraints are explicit
- [x] The future `context-to-canonical → objective-context-check → discover` sequence is documented as part of the harness contract
- [x] Remaining tasks are specific enough to execute without improvisation

## T2: Implement the neutral `mm` entrypoint

### Purpose

Add the first neutral runtime entrypoint so shell/Codex can drive the harness without relying on Claude slash commands.

### Depends On

T1

### Parallelizable

no

### Files / Areas Likely Touched

- `bin/mm` (new)
- `.mm-flow/commands/mm/*` (only minimal dispatch helpers if needed)
- `.mm-flow/README.md`

### Validation Commands

```bash
python3 -m unittest tests.unit.test_mm_discover_workflow
python3 -m unittest tests.unit.test_mm_complete_task_handler_regressions
./bin/mm --help
./bin/mm discover --help
./bin/mm complete-task --help
```

### Acceptance Criteria

- [x] `mm` exists as a neutral entrypoint
- [x] `mm` dispatches to the core handlers for the agreed subcommands
- [x] Exit codes are preserved from the underlying handlers
- [x] Help output makes the neutral interface discoverable

## T3: Align adapters and add cross-runtime smoke coverage

### Purpose

Ensure Claude remains a thin compatibility layer and add minimal tests/documentation proving the same lifecycle can be invoked from Claude wrappers and the neutral entrypoint.

### Depends On

T2

### Parallelizable

no

### Files / Areas Likely Touched

- `.claude/commands/mm/*` (only if dispatch alignment is needed)
- `.mm-flow/README.md`
- tests for wrapper/entrypoint compatibility
- `HANDOFF-CURRENT.md`

### Validation Commands

```bash
python3 -m unittest tests.unit.test_mm_discover_workflow
python3 -m unittest tests.unit.test_mm_complete_task_handler_regressions
python3 .claude/commands/mm/complete-task-handler.py --help
./bin/mm complete-task --help
```

### Acceptance Criteria

- [ ] Claude wrappers still work after the neutral CLI is introduced
- [ ] Shell/Codex usage is documented explicitly
- [ ] Basic cross-runtime smoke coverage exists
- [ ] Handoff explains that the next harness objective is the context-intake/objective-context-check improvement
