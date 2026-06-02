# Requirements — mm-harness-runtime-entrypoint-and-adapters

## Problem / Purpose

El flujo MM ya tiene un core útil en `.mm-flow/commands/mm/*.py`, pero la experiencia de uso sigue dependiendo demasiado del runtime:

- **Claude Code** usa slash commands `/mm:*`
- **Codex** no reconoce esos slash commands
- proyectos enlazados por symlink pueden quedar con adapters rotos o parciales

Este objetivo crea la **primera capa de entrypoint neutral del harness** para que el flujo pueda ejecutarse desde un comando estable independiente del modelo, mientras preserva compatibilidad con Claude y no rompe proyectos externos ya enlazados.

## Stakeholders / Users

- **Primary:** maintainers del harness MM
- **Secondary:** operadores que usan MM desde Claude Code, Codex o shell directo
- **Tertiary:** proyectos externos enlazados por symlink a `mastermind`

## Scope

### In Scope

- Definir e implementar un **entrypoint neutral** del harness (`mm` o equivalente explícito en `bin/`)
- Soportar al menos estos subcommands neutrales:
  - `discover`
  - `discover-contract-check`
  - `activate-next-objective`
  - `complete-task`
  - `continue-task`
  - `archive-objective`
  - `context-to-canonical`
- Diseñar el contrato del entrypoint neutral de forma que el siguiente paso del harness pueda introducir un nuevo gate entre `context-to-canonical` y `discover`, tentativamente:
  - `objective-context-check` (planned capability)
- Hacer que el entrypoint neutral delegue al core canónico:
  - `.mm-flow/commands/mm/*.py`
- Documentar claramente la separación:
  - **core canónico** (`.mm-flow`)
  - **adapter Claude** (`.claude`)
  - **uso shell/Codex**
- Mantener compatibilidad backward con Claude:
  - `/mm:*` sigue funcionando
  - `.claude/commands/mm/*` sigue siendo adapter válido
- Agregar validaciones/smoke tests mínimas para probar:
  - entrypoint neutral
  - dispatch correcto
  - compatibilidad Claude wrapper

### Out of Scope

- No rediseñar todo `discover`, `complete-task` o `archive-objective`
- No introducir un adapter formal completo de Codex con slash commands nativos
- No versionar todavía release channels del harness
- No reescribir todos los skills/agents del sistema
- No cambiar todavía schemas del ledger salvo que sea estrictamente necesario

## Non-negotiables

- `.mm-flow/commands/mm/*.py` sigue siendo el **source of truth** del flujo
- Los adapters no deben contener lógica de negocio del lifecycle
- No se rompe la compatibilidad de proyectos externos ya enlazados
- Los cambios delicados deben pensarse para rollout **between-task**, no mid-task
- Si falta un adapter/handler crítico, el flujo debe bloquearse en vez de continuar manualmente

## Decisions Already Implied

- El flujo no debe depender críticamente de slash commands
- El flujo no debe depender críticamente de hooks específicos del runtime
- Los modelos deben poder usar el mismo core vía shell/Python aunque el runtime no tenga UX equivalente a Claude
- El pipeline futuro del harness será:
  - `context-to-canonical`
  - `objective-context-check` *(nuevo gate planeado)*
  - `discover`
  - `discover-contract-check`
  - `complete-task`
  - `archive-objective`

## Objective-level Acceptance Criteria

- [ ] Existe un entrypoint neutral ejecutable del harness para shell/Codex
- [ ] El entrypoint neutral despacha correctamente a los handlers canónicos de `.mm-flow`
- [ ] Claude sigue funcionando como adapter sin duplicar lógica del core
- [ ] El uso recomendado queda documentado para Claude, Codex y shell directo
- [ ] Hay smoke tests o regresiones que prueban dispatch básico y compatibilidad
- [ ] El package deja claro el rollout seguro para no afectar proyectos externos en mitad de una task activa
