# mm-flow

Framework de orquestación de desarrollo lo más agnóstico posible al runtime de modelo.

## Estructura

```
.mm-flow/
├── commands/          # Python handlers + slash command docs
│   └── mm/            # /mm:complete-task, /mm:archive-objective, etc.
├── agents/            # Agentes de ejecución (task-executor, tester, etc.)
│   └── mm/
├── skills/            # Skills de orquestación (discover, review, etc.)
│   └── mm/
├── planning/          # Estructura de planning para objectives
│   ├── changes/       # Objectives activos
│   └── archive/       # Objectives completados
├── config/
│   ├── framework.yaml # Configuración principal
│   └── brain-router.yaml # Integración opcional de brains
└── installer/
    └── install.sh     # Script de instalación
```

## Commands Disponibles

### Canonical neutral entrypoint

- `./bin/mm discover ...`
- `./bin/mm discover-contract-check --objective <slug>`
- `./bin/mm activate-next-objective`
- `./bin/mm complete-task <objective/task>`
- `./bin/mm continue-task <objective/task>`
- `./bin/mm archive-objective [--objective <slug>]`
- `./bin/mm context-to-canonical ...`
- `./bin/mm objective-context-check --objective <slug-or-path>`

### Claude compatibility layer

- `/mm:complete-task <id>` — Ejecutar tasks con pipeline TDD
- `/mm:complete-task <id> --continue` — Continuar desde checkpoint
- `/mm:archive-objective <slug>` — Archivar objective completado
- `/mm:activate-next-objective` — Activar siguiente objective del roadmap
- `/mm:context-to-canonical` — Convertir contexto real del proyecto en docs canónicos
- `/mm:objective-context-check` — Validar/tightenear el objetivo canónico antes de `discover`
- `/mm:discover-contract-check --objective <slug>` — Validar planning contract
- `/mm:safe-commit` — Commit con validación

## Installation

```bash
# En proyecto nuevo
./.mm-flow/installer/install.sh --target /path/proyecto

# Instalar con brain pack
BRAINS_NICHE=software-development ./.mm-flow/installer/install.sh --target /path/proyecto
```

After installation:

- generic runtime path: `.mm-flow/commands/mm/*.py`
- Claude Code compatibility path: `.claude/commands/mm/*`
- neutral shell/Codex entrypoint: `bin/mm`

## Cross-runtime Usage

### Shell / Codex

Use the neutral entrypoint as the canonical interface:

```bash
./bin/mm context-to-canonical --type objective --name "Add OAuth login" --interview
./bin/mm objective-context-check --objective add-oauth-login
./bin/mm discover --existing --objective add-oauth-login "Add OAuth login"
./bin/mm discover --roadmap --existing
./bin/mm complete-task mm-harness-objective-context-check/T2 --brief
./bin/mm continue-task mm-harness-objective-context-check/T2
```

### Claude Code

Claude can keep using slash commands as a thin adapter over the same core:

```text
/mm:context-to-canonical --type objective --name "Add OAuth login" --interview
/mm:objective-context-check --objective add-oauth-login
/mm:discover --existing --objective add-oauth-login "Add OAuth login"
/mm:discover --roadmap --existing
/mm:complete-task mm-harness-objective-context-check/T2 --brief
/mm:continue-task mm-harness-objective-context-check/T2
```

### Direct core fallback

If a runtime has no adapter/CLI integration, invoke the handlers directly:

```bash
python3 .mm-flow/commands/mm/context-to-canonical-handler.py --type objective --name "Add OAuth login" --interview
python3 .mm-flow/commands/mm/objective-context-check-handler.py --objective add-oauth-login
python3 .mm-flow/commands/mm/discover-handler.py --existing --objective add-oauth-login "Add OAuth login"
python3 .mm-flow/commands/mm/discover-handler.py --roadmap --existing
python3 .mm-flow/commands/mm/complete-task-handler.py mm-harness-objective-context-check/T2 --brief
```

`objective-context-check` now persists a lightweight
`docs/canonical/objective-specs/<slug>.gate.json` artifact. If a matching
canonical objective exists, `discover --existing --objective <slug>` will stop
until that artifact exists and is `PASSED`.

Roadmap generation now also surfaces gate-aware queue status in
`.mm-flow/planning/roadmap/objectives.{md,json}`. If the recommended objective
has a matching canonical objective whose gate is `NOT_RUN`, `NEEDS_INPUT`, or
`FAILED`, `/mm:activate-next-objective` stops early with the exact next gate
command instead of failing later inside discover.

When multiple `ready_now` objectives exist, roadmap recommendation now prefers
the highest-priority objective that is also gate-ready (`NO_CANONICAL` or
`PASSED`). Gate-blocked objectives still appear in roadmap artifacts with their
status; they are just not preferred when a directly activatable alternative
exists.

If **all** dependency-ready objectives are gate-blocked, the roadmap still
surfaces one deterministic fallback recommendation, but marks it as blocked
fallback guidance. `/mm:activate-next-objective` remains blocked until some
candidate becomes gate-ready.

Blocked fallback recommendations now also include explicit **unblock-priority
reasoning** based on deterministic factors already available to the harness
(currently priority score, downstream unlock count, and gate status).

Objective packaging now defaults to **one active objective package at a time**.
If a different directory already exists under `.mm-flow/planning/changes/`,
`/mm:discover --existing --objective <slug>` blocks and tells the operator to
resume, complete, or archive the active objective before opening another one.

## Brain Integration

Los brain packs se instalan desde `brains/<niche>/` y se activan via `brain-router.yaml`.

## Modelo Agnóstico

El framework busca funcionar con cualquier LLM CLI (Claude Code, Codex, Gemini CLI, etc.) porque:
- Los handlers son scripts Python invocables desde shell
- Los agentes/skills son Markdown con protocolo legible por cualquier runtime
- El flujo principal puede ejecutarse sin depender de una API de subagents específica

## Planned Harness Flow

Objetivo objetivo/feature nuevo (flujo target):

```text
context-to-canonical
→ objective-context-check
→ discover
→ discover-contract-check
→ complete-task
→ archive-objective
```

Si un runtime soporta subagentes, puede usar los documentos de `agents/` como
protocolos opcionales. Si no los soporta, los handlers siguen siendo ejecutables
directamente.

## Versión

1.0.0 — Framework base de orquestación
