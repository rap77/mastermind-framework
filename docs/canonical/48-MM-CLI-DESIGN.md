# 48 — MasterMind CLI Design

## Purpose

CLI entry point for MasterMind workflow execution outside of Claude Code.

- **Slash commands** (`/mm:complete-task`, `/mm:discover`, etc.) → for when you're already inside Claude Code
- **CLI** (`mastermind` / `mm`) → for terminal, scripts, CI, or when you're not in a Claude Code session

Both share the same Python handlers. The CLI is a thin wrapper that exposes the handlers to the shell.

---

## Invocación

```bash
# Global install
mastermind <command> [args]
mm <command> [args]          # alias

# Project-local (uv run)
uv run mastermind <command> [args]

# Con Docker
docker run mastermind/mastermind:latest <command> [args]
```

---

## Dual Interface: CLI + Slash Commands

Every command exists in TWO interfaces that share the same handler:

```
┌─────────────────────────────────────┐
│           CLI (terminal)             │
│  mm <command> [args]                 │
└─────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────┐
│         Python Handler               │
│  .mm-flow/commands/mm/<name>.py     │
└─────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────┐
│        Slash Command (Claude Code)   │
│  /mm:<command> [args]               │
└─────────────────────────────────────┘
```

Both interfaces call the **same handler**. The CLI adds argparse + output formatting. The slash command is the Claude Code wrapper.

---

## Comandos

### Framework Lifecycle

| CLI | Slash Command | Descripción |
|-----|---------------|-------------|
| `mm init` | `/mm:init` | Instala mm-flow en un proyecto nuevo |
| `mm new-canonical <title>` | `/mm:new-canonical <title>` | Crea doc canonical desde template |
| `mm extract-objectives` | `/mm:extract-objectives` | Extrae objectives desde canonical docs |

### Objective Lifecycle

| CLI | Slash Command | Descripción |
|-----|---------------|-------------|
| `mm discover [idea]` | `/mm:discover` | De idea a plan objetivo |
| `mm execute <task-id>` | `/mm:complete-task <task-id>` | Ejecutar objective o task |
| `mm status` | `/mm:status` | Ver progreso actual |
| `mm archive <objective>` | `/mm:archive-objective <objective>` | Archivar objective completado |
| `mm activate` | `/mm:activate-next-objective` | Activar siguiente objective |
| `mm validate <objective>` | `/mm:validate` | Validar contrato de un objective |

### Utilities

| CLI | Slash Command | Descripción |
|-----|---------------|-------------|
| `mm help` | (built-in) | Help general |
| `mm --version` | (built-in) | Versión del CLI |

### Formato de output

```bash
# Default: texto human-readable
mm status
mm discover "nueva feature"

# JSON: machine-readable (para scripts, CI, agentes)
mm status --json
mm validate --objective mm-flow-cli --json
```

### Códigos de salida

| Code | Significado |
|------|-------------|
| `0` | Success |
| `1` | Error genérico |
| `2` | Objective no encontrado |
| `3` | Validación fallida |
| `4` | Task bloqueada o incompleta |

---

## Installation

### Global (recomendado para devs)

```bash
# Con uv
uv pip install -e .

# Con pip
pip install -e .

# Alias permanente en shell
alias mm='mastermind'
```

### Local por proyecto

```bash
# En el proyecto, sin instalar globalmente
uv run mastermind discover "mi idea"
```

### CI / Docker

```dockerfile
FROM python:3.14-slim
COPY . /app
RUN pip install -e /app
ENTRYPOINT ["mastermind"]
```

---

## Arquitectura

```
mastermind/                          # Paquete Python
├── __main__.py                     # Entry: python -m mastermind
├── cli.py                          # argparse + subparsers (薄wrapper)
├── commands/                       # Wrappers thin → handlers
│   ├── init.py                     # → init-handler.py
│   ├── new_canonical.py            # → new-canonical-handler.py
│   ├── extract_objectives.py       # → extract-objectives-handler.py
│   ├── discover.py                 # → discover-handler.py
│   ├── execute.py                  # → complete-task-handler.py
│   ├── status.py                   # → task-progress.json (direct read)
│   ├── archive.py                  # → archive-objective-handler.py
│   ├── activate.py                 # → activate-next-objective-handler.py
│   └── validate.py                 # → discover-contract-check.py
│
.mm-flow/                           # Framework (mono-repo)
└── commands/mm/                    # Handlers reales (authoritative)
    ├── init-handler.py
    ├── new-canonical-handler.py
    ├── extract-objectives-handler.py
    ├── discover-handler.py
    ├── complete-task-handler.py
    ├── archive-objective-handler.py
    ├── activate-next-objective-handler.py
    └── discover-contract-check.py

.claude/commands/mm/                # Slash command wrappers (Claude Code)
├── init.md
├── new-canonical.md
├── extract-objectives.md
├── discover.md
├── complete-task.md
├── archive-objective.md
├── activate-next-objective.md
└── discover-contract-check.md
```

### Principios de diseño

1. **Dual interface** — Cada command existe en CLI y slash command, mismo handler subyacente
2. **No reescribir lógica** — Cada command es un wrapper que llama al handler Python correspondiente
3. **Idempotencia** — Los commands pueden ejecutarse múltiples veces sin side effects
4. **Fail fast** — Validación temprana, mensajes de error claros
5. **Output estructurado** — `--json` para consumo programático, texto para humanos

---

## Comandos en detalle

### `mm init` / `/mm:init`

Instala mm-flow en un proyecto nuevo o ya existente. Crea la estructura de directorios y copia los handlers.

```bash
# CLI
mm init
mm init --path ./mi-proyecto

# Slash (Claude Code)
/mm:init
/mm:init --path ./mi-proyecto

# Handler:
python3 .mm-flow/commands/mm/init-handler.py
```

**Output esperado:**
```
✅ MasterMind initialized
📁 Created: .mm-flow/
📁 Created: .mm-flow/commands/mm/
📁 Created: .mm-flow/planning/
📁 Created: .mm-flow/planning/changes/
📁 Created: .mm-flow/planning/archive/
📋 Copying handlers... done
💡 Next: mm new-canonical "Mi primer objective"
```

**¿Qué crea?**
- `.mm-flow/` — directorio principal
- `.mm-flow/commands/mm/` — handlers del framework
- `.mm-flow/planning/changes/` — objectives activos
- `.mm-flow/planning/archive/` — objectives completados
- `.claude/commands/mm/` — slash command wrappers

**Flags:**
- `--path <dir>` — path al proyecto (default: cwd)
- `--force` — sobreescribir si ya existe

---

### `mm new-canonical <title>` / `/mm:new-canonical <title>`

Crea un doc canonical nuevo desde el template. Este doc es el **source of truth** para luego extraer objectives.

```bash
# CLI
mm new-canonical "Sistema de autenticación JWT"
mm new-canonical "API de pagos con Stripe"

# Slash (Claude Code)
/mm:new-canonical "Sistema de autenticación JWT"

/mm:new-canonical  # interactivo: pide el título
```

**Handler:**
```bash
python3 .mm-flow/commands/mm/new-canonical-handler.py "Sistema de autenticación JWT"
```

**Output esperado:**
```
✅ Canonical doc created
📄 docs/canonical/49-SISTEMA-DE-AUTENTICACION-JWT.md
📋 Template: canonical-template.md
💡 Next: mm extract-objectives
```

**Template generado incluye:**
- Título y propósito
- Stakeholders
- Scope (in/out)
- Non-negotiables
- Acceptance criteria
- Arquitectura propuesta
- Tasks preliminares

**¿Por qué desde canonical doc?**
```
Canonical Doc (source of truth)
    │
    ▼
mm extract-objectives
    │
    ▼
.mm-flow/planning/changes/<objective>/
    ├── requirements.md
    ├── design.md
    ├── tasks.md
    └── HANDOFF-CURRENT.md
```

---

### `mm extract-objectives` / `/mm:extract-objectives`

Extrae uno o más objectives desde los canonical docs. Genera el package completo en `.mm-flow/planning/changes/<objective>/`.

```bash
# CLI — extraer todos los canonical docs nuevos
mm extract-objectives

# Extraer uno específico
mm extract-objectives "Sistema de autenticación JWT"

# Slash (Claude Code)
/mm:extract-objectives
/mm:extract-objectives "Sistema de autenticación JWT"

# Handler:
python3 .mm-flow/commands/mm/extract-objectives-handler.py
```

**Output esperado:**
```
🔍 Scanning docs/canonical/ for new objectives...
✅ Extracted: Sistema de autenticación JWT
📁 Created: .mm-flow/planning/changes/autenticacion-jwt/
   ├── requirements.md
   ├── design.md
   ├── tasks.md
   └── HANDOFF-CURRENT.md
✅ Extracted: API de pagos
📁 Created: .mm-flow/planning/changes/api-pagos/
💡 Next: mm execute T1 (autenticacion-jwt)
```

**Reglas:**
- Solo extrae canonical docs que NO tengan objective equivalente en `.mm-flow/planning/changes/`
- Si el objective ya existe, lo skipped (idempotente)
- Genera tasks desde el campo `## Tasks` del canonical doc

---

### `mm discover [idea]` / `/mm:discover`

De idea a plan objetivo. Crea el package en `.mm-flow/planning/changes/<objective>/`.

```bash
# CLI
mm discover "API de autenticación"
mm discover --objective mi-objetivo
mm discover --quick "fix bug"

# Slash (Claude Code)
/mm:discover "API de autenticación"
/mm:discover --quick "fix bug"

# Handler:
python3 .mm-flow/commands/mm/discover-handler.py "API de autenticación"
```

**Output esperado (texto):**
```
🔍 Discovery: "API de autenticación"
✅ Objective creado: api-auth
📁 Package: .mm-flow/planning/changes/api-auth/
📋 Tasks: T1, T2, T3 definidos
💡 Next: mm execute T1
```

**Output `--json`:**
```json
{
  "status": "created",
  "objective": "api-auth",
  "plan_path": ".mm-flow/planning/changes/api-auth/tasks.md",
  "tasks": ["T1", "T2", "T3"],
  "next_command": "mm execute T1"
}
```

---

### `mm execute <task-id>` / `/mm:complete-task`

Ejecuta una task completa (subtasks T.x.1, T.x.2, T.x.3) via task-executor agent.

```bash
# CLI
mm execute T1
mm execute T2 --continue    # reanudar desde checkpoint
mm execute T3 --background  # detach y retorna immediately

# Slash (Claude Code)
/mm:complete-task T1
/mm:complete-task T2 --continue
/mm:complete-task T3 --background

# Handler:
python3 .mm-flow/commands/mm/complete-task-handler.py T1
```

**Output esperado:**
```
▶️  Ejecutando T1...
✅ T1.1 completed (2m)
✅ T1.2 completed (5m)
⏳ T1.3 running...
🔔 Task-executor launched in background
📊 Monitor: tail -f .mm-flow/planning/task-progress.json
```

---

### `mm status` / `/mm:status`

Ver progreso actual del objective activo o de uno específico.

```bash
# CLI
mm status
mm status --objective mm-flow-cli
mm status --json

# Slash (Claude Code)
/mm:status
/mm:status --objective mm-flow-cli

# Handler: lee directo task-progress.json (no handler externo)
```

**Output esperado:**
```
📋 Objective: mm-flow-cli
🎯 Task actual: T2 (in progress)

| Task | Status | Progress |
|------|--------|----------|
| T1   | ✅ Done | 3/3     |
| T2   | ⏳ In progress | 2/3 |
| T3   | ⏸ Pending | blocked by T2 |

📊 ETA: ~10m para T2
```

---

### `mm archive <objective>` / `/mm:archive-objective`

Archiva un objective completado. Lo mueve de `.mm-flow/planning/changes/<objective>/` a `.mm-flow/planning/archive/objectives/<objective>/`.

```bash
# CLI
mm archive mm-flow-cli
mm archive mm-flow-cli --summary-only  # solo validación

# Slash (Claude Code)
/mm:archive-objective mm-flow-cli
/mm:archive-objective mm-flow-cli --summary-only

# Handler:
python3 .mm-flow/commands/mm/archive-objective-handler.py --objective mm-flow-cli
```

**Output esperado:**
```
✅ Objective mm-flow-cli archivado
📦 Destino: .mm-flow/planning/archive/objectives/mm-flow-cli/
🔔 Next: mm activate
```

---

### `mm validate <objective>` / `/mm:validate`

Valida el contrato de un objective (estructura, completitud, archive-safety).

```bash
# CLI
mm validate mm-flow-cli
mm validate mm-flow-cli --json

# Slash (Claude Code)
/mm:validate mm-flow-cli
/mm:validate mm-flow-cli --json

# Handler:
python3 .mm-flow/commands/mm/discover-contract-check.py --objective mm-flow-cli
```

**Output esperado:**
```
🔍 Validando: mm-flow-cli
✅ Contract check passed
📋 Estructura: requirements.md ✅, design.md ✅, tasks.md ✅, HANDOFF-CURRENT.md ✅
✅ Archive-safe
```

### `mm activate` / `/mm:activate-next-objective`

Activa el siguiente objective disponible en la cola.

```bash
# CLI
mm activate

# Slash (Claude Code)
/mm:activate-next-objective

# Handler:
python3 .mm-flow/commands/mm/activate-next-objective-handler.py
```

**Output esperado:**
```
🎯 Activating next objective...
📋 Next: context-projection
✅ Objective activated: context-projection
📁 Package: .mm-flow/planning/changes/context-projection/
💡 Next: mm execute T1
```

---

## Integración con Claude Code

El CLI **NO reemplaza** los slash commands. Son capas distintas:

```
┌─────────────────────────────────────┐
│           Usuario                    │
└─────────────────────────────────────┘
          │              │
          ▼              ▼
   Claude Code      Terminal / CI
          │              │
          ▼              ▼
   /mm:discover      mm discover
   /mm:execute       mm execute
   /mm:status        mm status
   /mm:init          mm init
   /mm:new-canonical mm new-canonical
   /mm:extract-obj   mm extract-objectives
          │              │
          └──────┬───────┘
                 ▼
         Python Handlers
         (.mm-flow/commands/mm/)
```

### Cuándo usar cada uno

| Contexto | Usar |
|----------|------|
| Ya estás en Claude Code | `/mm:discover`, `/mm:complete-task`, etc. |
| Terminal standalone | `mm discover`, `mm execute` |
| CI/CD pipeline | `mm validate`, `mm status --json` |
| Scripts externos | `mm execute T1 --json` |
| Docker / contenedores | `docker run mastermind:latest ...` |

---

## Roadmap de Commands

### Framework Lifecycle (instalación + canonical docs)

| Priority | Command | Slash | Handler | Estado |
|----------|---------|-------|---------|--------|
| P0 | `mm init` | `/mm:init` | `init-handler.py` | 🔜 Nuevo — implementar |
| P0 | `mm new-canonical` | `/mm:new-canonical` | `new-canonical-handler.py` | 🔜 Nuevo — implementar |
| P0 | `mm extract-objectives` | `/mm:extract-objectives` | `extract-objectives-handler.py` | 🔜 Nuevo — implementar |

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
| P2 | `mm --version` | Versión del CLI |

---

## Diseño de argumentos comunes

```bash
# Flags globales
--json          # Output machine-readable
--verbose (-v)  # Más detalle
--quiet (-q)    # Menos output
--dry-run       # Simular sin ejecutar
--help (-h)     # Help del command

# Flags por command
--objective <slug>   # Objective target
--continue           # Reanudar desde checkpoint
--background        # Detach y retornar immediately
```

---

## Error handling

```bash
# Ejemplos de errores

mm execute T99
# ❌ Error: Task 'T99' not found in objective 'mm-flow-cli'
# 💡 Run: mm status --objective mm-flow-cli

mm archive no-existe
# ❌ Error: Objective 'no-existe' not found
# 💡 Run: mm status

mm validate mm-flow-cli --json
# {
#   "status": "failed",
#   "error": "objective_not_found",
#   "objective": "no-existe",
#   "suggestion": "Run: mm status"
# }
```

---

## Validación

### Smoke test

```bash
# Después de instalar
mastermind --version    # o --help
mm --help

# Verificar que responde
mm status --json
```

### Test de integración

```bash
# 1. Crear objective de test
mm discover "test objective" --json

# 2. Ejecutar task
mm execute T1 --json

# 3. Ver status
mm status --json

# 4. Validar
mm validate test-objective --json

# 5. Archivar
mm archive test-objective --json
```

---

## Archivo: `pyproject.toml` snippet

```toml
[project]
name = "mastermind"
version = "0.1.0"
description = "MasterMind workflow CLI"
requires-python = ">=3.14"
entry-points = [
    "mastermind = mastermind.cli:main",
]
[project.scripts]
mastermind = "mastermind.cli:main"
mm = "mastermind.cli:main"  # alias
```

---

## Archivo: `mastermind/__main__.py`

```python
"""Entry point: python -m mastermind"""
from mastermind.cli import main

if __name__ == "__main__":
    main()
```

---

## Archivo: `mastermind/cli.py` (estructura)

```python
import argparse
import sys

COMMANDS = {
    "discover": ".mm-flow/commands/mm/discover-handler.py",
    "execute": ".mm-flow/commands/mm/complete-task-handler.py",
    "status": None,  # read task-progress.json directly
    "archive": ".mm-flow/commands/mm/archive-objective-handler.py",
    "activate": ".mm-flow/commands/mm/activate-next-objective-handler.py",
    "validate": ".mm-flow/commands/mm/discover-contract-check.py",
}

def main():
    parser = argparse.ArgumentParser(prog="mastermind")
    parser.add_argument("command", choices=list(COMMANDS.keys()))
    parser.add_argument("args", nargs=argparse.REMAINDER)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--verbose", "-v", action="store_true")
    args = parser.parse_args()

    # Dispatch to handler...
    sys.exit(0)

if __name__ == "__main__":
    main()
```

---

## Decisiones tomadas

1. **Wrappers, no reescritura** — Cada command delega al handler Python existente. No hay lógica duplicada.

2. **Alias `mm`** — Más corto de escribir, igual de claro en contexto de proyecto.

3. **Dual installation** — Global para devs activos, local/uv run para CI y proyectos共享.

4. **JSON output** — Consume programable por agentes y pipelines. El default texto es para humanos.

5. **Coexistencia con slash commands** — Slash commands para UX en Claude Code, CLI para terminal/scripts/CI.

6. **Fail fast** — Validación en cada command antes de invocar el handler.

---

## Siguiente paso

Crear un objective nuevo para construir el CLI basándose en este diseño. El objective debe:

1. Crear `mastermind/` con `__main__.py` + `cli.py` como thin wrapper
2. Implementar `init`, `new-canonical`, `extract-objectives` handlers (P0)
3. Crear los slash command `.md` para cada command nuevo
4. Crear `pyproject.toml` con entry points
5. Validar con smoke test: `mm --help` y `mm status --json`

Flujo recomendado:

```
mm new-canonical "MasterMind CLI"
    ↓
mm extract-objectives
    ↓
mm execute T1, T2, T3 (construir CLI)
    ↓
mm archive mastermind-cli
```
