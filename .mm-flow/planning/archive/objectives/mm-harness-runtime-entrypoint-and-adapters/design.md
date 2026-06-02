# Design — mm-harness-runtime-entrypoint-and-adapters

## Architecture / Boundaries

Este objetivo formaliza tres capas:

### 1. Core Harness (source of truth)

Ubicación:
- `.mm-flow/commands/mm/*.py`

Responsabilidad:
- lifecycle real del flujo
- ledger/runtime state
- roadmap/objectives
- context-to-canonical
- archive / contract-check / complete-task

Regla:
> aquí vive la lógica del sistema

### 2. Runtime Entry Point (neutral)

Ubicación propuesta:
- `bin/mm`

Responsabilidad:
- aceptar subcommands neutrales (`mm discover`, `mm complete-task`, etc.)
- traducirlos al handler Python correcto
- mantener una superficie estable para runtimes sin slash commands

Regla:
> despacha, no decide

### 3. Runtime Adapters

Ubicaciones:
- Claude: `.claude/commands/mm/*`
- shell/Codex: `bin/mm`

Responsabilidad:
- invocar el mismo core
- adaptar UX, no semántica

Regla:
> el adapter no reimplementa la lógica de negocio

## Technical Approach

### Step 1 — definir contrato mínimo del CLI neutral

El entrypoint debe soportar esta forma:

```bash
mm discover --roadmap --existing
mm discover --existing --objective <slug> "<Title>"
mm discover-contract-check --objective <slug>
mm activate-next-objective
mm complete-task <TASK_ID>
mm continue-task <TASK_ID>
mm archive-objective [--objective <slug>]
mm context-to-canonical --type objective --name "<Title>"
```

El contrato debe dejar espacio explícito para el siguiente paso del harness, aunque no se implemente todavía en este objetivo:

```bash
mm objective-context-check --objective <slug-or-path>
```

Ese comando futuro validará/tighteneará el objetivo canónico generado por `context-to-canonical` antes de que `discover` lo convierta en package ejecutable.

La implementación puede ser un wrapper shell o Python, pero debe:
- resolver el project root
- llamar al handler correcto bajo `.mm-flow/commands/mm/`
- propagar exit codes
- no cambiar payloads ni estados del core

### Step 2 — mantener Claude como adapter fino

Claude puede seguir exponiendo:
- `/mm:discover`
- `/mm:complete-task`
- etc.

Pero esos wrappers deben alinearse con el entrypoint neutral y no desviar la semántica del core.

### Step 3 — documentar uso multi-runtime

Hay que dejar explícito:
- **canonical usage:** `mm ...`
- **Claude compatibility:** `/mm:*`
- **direct core fallback:** `python3 .mm-flow/commands/mm/<handler>.py ...`

## Dependencies

- Depends on el core MM actual bajo `.mm-flow/commands/mm/`
- Depends on la compatibilidad ya existente por symlink `.claude/*`

## Validation Strategy

### Required checks

```bash
python3 -m unittest tests.unit.test_mm_complete_task_handler_regressions
python3 -m unittest tests.unit.test_mm_discover_workflow
```

### New smoke checks expected from this objective

```bash
./bin/mm --help
./bin/mm discover --help
./bin/mm complete-task --help
./bin/mm context-to-canonical --help
```

If `bin/mm` is Python-based:

```bash
python3 bin/mm --help
```

## Important Tradeoffs

- **Wrapper shell vs wrapper Python:** shell is simpler, Python may be easier to keep cross-platform and testable
- **Preserve Claude UX vs normalize usage:** maintain Claude convenience, but document `mm` as canonical interface
- **Hot propagation risk:** changing adapters affects linked projects immediately, so rollout must avoid active in-progress tasks
- **Planned validation gate:** `context-to-canonical` no debe pasar directo a `discover` sin una futura validación de objetivo/contexto; este objetivo solo reserva el contract/entrypoint, no implementa todavía ese gate

## Rollout / Safety Notes

- Safe to propagate between completed tasks
- Avoid deploying adapter/core dispatch changes while another repo has a task actively mid-subtask
- This objective must not silently mutate the existing ledger formats unless separately justified

## Files / Areas Likely Touched

- `bin/mm` (new)
- `.mm-flow/commands/mm/*` (dispatch alignment only where needed)
- `.claude/commands/mm/*` (adapter alignment/documentation if needed)
- `.mm-flow/README.md`
- tests for CLI/adapter dispatch
