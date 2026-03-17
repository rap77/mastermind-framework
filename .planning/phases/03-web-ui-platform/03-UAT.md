---
status: testing
phase: 03-web-ui-platform
source: 03-01-SUMMARY.md, 03-02-SUMMARY.md, 03-03-SUMMARY.md
started: 2026-03-17T00:00:00Z
updated: 2026-03-17T01:00:00Z
---

## Current Test

number: 4
name: Refresh token rotation
expected: |
  Usando el refresh_token del login, POST /api/auth/refresh devuelve nuevos tokens.
  El refresh_token original queda inválido (segundo uso devuelve 401).
awaiting: user response

## Tests

### 1. Cold Start Smoke Test
expected: Correr `uv run uvicorn mastermind_cli.api.app:get_app --factory --host 0.0.0.0 --port 8000`. Servidor levanta sin errores. `curl http://localhost:8000/` responde con status 200.
result: pass

### 2. Login API
expected: `curl -X POST http://localhost:8000/api/auth/login -H "Content-Type: application/json" -d '{"username":"admin","password":"admin"}` devuelve access_token y refresh_token. Sin usuario en DB, debería existir algún mecanismo para crearlo.
result: pass

### 3. Token protege rutas
expected: `curl http://localhost:8000/api/tasks` sin Authorization header responde 401 Unauthorized.
result: pass

### 4. Refresh token rotation
expected: Usando el refresh_token, `POST /api/auth/refresh` devuelve nuevos tokens. El refresh_token original queda inválido (segundo uso devuelve 401).
result: [pending]

### 5. Task creation
expected: `POST /api/tasks` con JWT válido y body `{"brief":"test","flow":{"brains":[]}}` crea una tarea y devuelve su ID con status 201.
result: [pending]

### 6. Session isolation
expected: Crear dos usuarios diferentes (si es posible). Las tareas creadas por usuario A no aparecen en `GET /api/tasks` del usuario B.
result: [pending]

### 7. WebSocket connection
expected: Conectar a `ws://localhost:8000/ws/tasks/{task_id}?token={jwt}`. Conexión acepta. Un mensaje de update llega al crear/cambiar estado de la tarea.
result: [pending]

### 8. DAG graph endpoint
expected: `GET /api/tasks/{id}/graph` con JWT válido devuelve JSON con `nodes`, `edges`, `max_level`. Para tarea sin flow_config devuelve arrays vacíos (no 404).
result: [pending]

### 9. Dashboard HTML accesible
expected: `curl http://localhost:8000/` o `http://localhost:8000/index.html` sirve el HTML del dashboard (login form visible). Los archivos CSS y JS se cargan correctamente en el browser.
result: [pending]

### 10. Export desde dashboard
expected: Con una tarea completada visible en el dashboard, los botones "Export JSON", "Export YAML", "Export Markdown" descargan archivos con el resultado.
result: [pending]

### 11. Responsive design
expected: Abrir el dashboard en viewport mobile (375px) vía DevTools. El layout cambia a columna única. El sidebar se oculta. Los touch targets son ≥44px.
result: [pending]

### 12. Audit log
expected: Hacer un `POST /api/tasks` o `POST /api/auth/login`. Luego verificar que la acción quedó registrada en `audit_log` (vía SQL directo o endpoint si existe).
result: [pending]

## Summary

total: 12
passed: 3
issues: 0
pending: 9
skipped: 0

## Gaps

[none yet]
