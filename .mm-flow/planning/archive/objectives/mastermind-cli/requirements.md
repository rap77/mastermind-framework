# Requirements — mastermind-cli

## Problem / Purpose
CLI entry point for MasterMind workflow execution outside of Claude Code.

- **Slash commands** (`/mm:complete-task`, `/mm:discover`, etc.) → for when you're already inside Claude Code
- **CLI** (`mastermind` / `mm`) → for terminal, scripts, CI, or when you're not in a Claude Code session

Both share the same Python handlers. The CLI is a thin wrapper that exposes the handlers to the shell.

---

## Scope
- Framework lifecycle commands: `init`, `new-canonical`, `extract-objectives`
- Objective lifecycle commands: `discover`, `execute`, `status`, `archive`, `validate`, `activate`
- Utilities: `config`, `--version`

## Out of Scope
- Direct brain consultation (use `/mm:brain-context` instead)
- Source management (handled by `tools/mastermind-cli/`)
- Database migrations (handled by Rust Control Plane)

## Non-negotiables
- Handlers live in `.mm-flow/commands/mm/` (authoritative location)
- Slash commands live in `.mm-flow/commands/mm/*.md` (symlinked from `.claude/commands/mm/`)
- Both entry points MUST produce identical results
- No breaking changes to existing handler signatures

---

## Planned Tasks

### Framework Lifecycle (instalacion + canonical docs)

| Priority | Command | Slash | Handler | Estado |
|----------|---------|-------|---------|--------|
| P0 | `mm init` | `/mm:init` | `init-handler.py` | ✅ Ya existe |
| P0 | `mm new-canonical` | `/mm:new-canonical` | `new-canonical-handler.py` | 🔜 Nuevo — implementado |
| P0 | `mm extract-objectives` | `/mm:extract-objectives` | `extract-objectives-handler.py` | 🔜 Nuevo — implementado |

### Objective Lifecycle

| Priority | Command | Slash | Handler | Estado |
|----------|---------|-------|---------|--------|
| P0 | `mm discover` | `/mm:discover` | `discover-handler.py` | ✅ Ya existe |
| P0 | `mm execute` | `/mm:complete-task` | `complete-task-handler.py` | ✅ Ya existe |
| P0 | `mm status` | `/mm:status` | task-progress.json (directo) | ✅ Ya existe |
| P1 | `mm archive` | `/mm:archive-objective` | `archive-objective-handler.py` | ✅ Ya existe |
| P1 | `mm validate` | `/mm:validate` | `discover-contract-check.py` | ✅ Ya existe |
| P1 | `mm activate` | `/mm:activate-next-objective` | `activate-next-objective-handler.py` | ✅ Ya existe |

### Utilities

| Priority | Command | Notas |
|----------|---------|-------|
| P2 | `mm config` | Configurar settings (brain registry, etc.) |
| P2 | `mm --version` | Version del CLI |

---

## Objective-level Acceptance Criteria
- [ ] The objective has an execution-ready package with requirements, design, tasks, and handoff.
- [ ] The implementation slice advances the target objective without breaking adjacent flows.
- [ ] Validation commands are documented and usable by another model or human operator.

_Enriched from canonical doc: `48-MM-CLI-DESIGN.md`_
