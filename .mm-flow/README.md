# mm-flow

Framework de orquestación de desarrollo agnóstico al modelo LLM.

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

- `/mm:complete-task <id>` — Ejecutar tasks con pipeline TDD
- `/mm:complete-task <id> --continue` — Continuar desde checkpoint
- `/mm:archive-objective <slug>` — Archivar objective completado
- `/mm:activate-next-objective` — Activar siguiente objective del roadmap
- `/mm:discover-contract-check --objective <slug>` — Validar planning contract
- `/mm:safe-commit` — Commit con validación

## Installation

```bash
# En proyecto nuevo
./.mm-flow/installer/install.sh --target /path/proyecto

# Instalar con brain pack
BRAINS_NICHE=software-development ./.mm-flow/installer/install.sh --target /path/proyecto
```

## Brain Integration

Los brain packs se instalan desde `brains/<niche>/` y se activan via `brain-router.yaml`.

## Modelo Agnóstico

El framework funciona con cualquier LLM CLI (Claude Code, Codex, Gemini CLI, etc.) porque:
- Commands son scripts de shell puros
- Agents usan YAML + Markdown (no vendor-specific)
- Skills son Markdown con front matter

## Versión

1.0.0 — Framework base de orquestación
