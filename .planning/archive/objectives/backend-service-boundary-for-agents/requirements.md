# Requirements — backend-service-boundary-for-agents

## Problem / Purpose

Definir y aplicar el boundary entre agentes y la base de datos mediante herramientas semánticas
expuestas por el backend. Los agentes no deben hablar directamente con la DB — deben usar
capacidades semánticas del service layer.

Ver doc canónico: `docs/canonical/34-BACKEND-SERVICE-BOUNDARY-FOR-AGENTS.md`

## Stakeholders / Users

- Primary: agentes, brains y modelos que necesitan registrar o leer estado de proyecto
- Secondary: operadores humanos que usan el dashboard o comandos MM

## Audit — What Already Exists (T1 finding)

Los siguientes endpoints semánticos ya existen en `apps/api/mastermind_cli/api/routes/project_overview.py`:

| Capability (canonical) | HTTP endpoint | Status |
|---|---|---|
| `get_project_overview(project_id)` | `GET /api/projects/{project_id}/overview` | ✅ exists |
| `get_task_context_projection(task_id)` | `GET /api/projects/{project_id}/tasks/{task_id}/context-projection` | ✅ exists |
| `get_task_doctrine_projection(task_id)` | `GET /api/projects/{project_id}/tasks/{task_id}/doctrine-projection` | ✅ exists |
| `create_checkpoint(task_id, ...)` | `POST /api/projects/{project_id}/tasks/{task_id}/checkpoints` | ✅ exists |
| `record_decision(...)` | `POST /api/projects/{project_id}/decisions` | ✅ exists |
| `update_task_status(...)` (pause/complete) | `PATCH /api/projects/{project_id}/tasks/{task_id}/status` | ✅ exists |
| `get_token_usage(project_id)` | `GET /api/projects/{project_id}/token-usage` | ✅ exists (read only) |
| `record_token_usage(task_id, ...)` | — | ❌ missing |
| `record_backend_switch(...)` | — | ❌ missing |

## Scope — What T2 Delivers

El gap más pequeño y coherente que avanza el objetivo:

**`POST /api/projects/{project_id}/tasks/{task_id}/token-usage`**

Permite que un agente registre su consumo de tokens via el service layer (no directamente en DB).
Sigue el patrón de auditoría establecido por checkpoints y decisions.

`record_backend_switch` queda declarado pero fuera del scope mínimo (sin usuario activo).

## Out of Scope

- No rewrites de endpoints existentes.
- No `record_backend_switch` en este ciclo.
- No MCP server nuevo — los agentes acceden via HTTP.
- No cambios en el frontend.

## Non-negotiables

- Backend es la autoridad de estado y auditoría.
- El endpoint debe pasar por el service layer (no repo directo desde route).
- Tests TDD obligatorios.

## Objective-level Acceptance Criteria

- [x] El audit de boundary está documentado (T1).
- [ ] `POST /api/projects/{project_id}/tasks/{task_id}/token-usage` existe y pasa tests.
- [ ] El registro de token usage va a través del service layer con validación.
- [ ] Tests de regresión pasan sin cambios.
