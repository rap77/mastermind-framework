# Session 2026-03-17 — UAT Phase 3 + Infrastructure Fixes

## Estado al cierre
UAT Phase 3 en progreso. Tests 1-3 pasados. Test 4 (rotation) bug encontrado + fix pendiente de commit.

## Commits de sesión
- `d31917b` fix(infra): static files, admin seed, docker-compose
- `cc3db2d` fix(api): db_path dependency_overrides en create_app
- `cd35d74` chore(tooling): pyrightconfig.json
- `eb6b121` fix(types): 4 errores Pyright
- `30f624f` wip: UAT phase 3 paused at test 4/12

## Bugs encontrados y arreglados
1. **get_db_path hardcodeaba :memory:** — routes abrían DB vacía. Fix: `app.dependency_overrides[get_db_path] = lambda: db_path` en `create_app()`
2. **JWT sin jti:** — tokens creados en el mismo segundo eran idénticos → rotación inválida. Fix: `"jti": str(uuid.uuid4())` en ambos token creators. **Pendiente de commit** (en working tree: `mastermind_cli/api/routes/auth.py`)
3. **static files comentados:** — dashboard HTML no se servía. Fix: `app.mount("/static", ...)` + ruta `/dashboard`
4. **Dockerfile CMD incorrecto:** — usaba `mastermind-cli dashboard` inexistente. Fix: `uvicorn mastermind_cli.api.app:get_app --factory`
5. **Admin seed faltaba:** — `create_auth_schema()` prometía seed pero no lo hacía. Fix: seed con `MM_ADMIN_PASSWORD` env var

## Pyright setup
- `pyrightconfig.json` creado con `venvPath: "."`, `venv: ".venv"`, `pythonVersion: "3.14"`
- Errores corregidos: `flow_config: FlowConfig | None`, `_extract_brief(input: Any)`, `__all__` cleanup, `JSONEncoder.default(o:)`

## Docker
- `docker-compose.yml` creado — volumen `mastermind_data`, puerto 8000, healthcheck
- Container corriendo en localhost:8000
- Credenciales: admin / admin (MM_ADMIN_PASSWORD env)

## Próxima sesión
1. `git add mastermind_cli/api/routes/auth.py && git commit -m "fix(auth): add jti to JWT tokens"`
2. `docker compose build --no-cache && docker compose up -d`
3. Continuar UAT desde test 5 (Claude ejecuta curls directamente)
4. Tests restantes: task creation, session isolation, WebSocket, DAG graph, dashboard HTML, export, responsive, audit log
