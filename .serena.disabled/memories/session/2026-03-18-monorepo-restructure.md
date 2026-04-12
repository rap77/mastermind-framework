# Session 2026-03-18 — Monorepo Restructure + Frontend Planning

## Lo que se hizo

### Diagnóstico del frontend actual
- UI Alpine.js + Vanilla JS era funcional solo para CRUD básico
- WebSocket no conectado al crear tasks (TODO en dashboard.js:114)
- DAG no se renderizaba con datos reales
- Alpine script loading order bug corregido (x-data="dashboard" sin paréntesis, Alpine al final)
- Favicon 🧠 agregado via SVG data URI + CSP fix (img-src data:)

### Decisiones de arquitectura frontend
- Migrar a Next.js 16 + React 19 + TypeScript + Tailwind 4
- shadcn/ui para estructura funcional + Magic UI para momentos de impacto
- 4 pantallas diseñadas: Home (brief input), Routing (diagnóstico), Ejecución (sala de guerra), Resultados
- Routing semántico con Claude (reemplazar keyword matching de FlowDetector)

### Monorepo restructure (commit f4d1315)
- apps/api/ ← Python FastAPI + CLI (mastermind_cli, agents, tests, scripts)
- apps/web/ ← placeholder Next.js 16
- docker/api/Dockerfile ← build context apps/api (agrega agents/)
- docker/web/Dockerfile ← Next.js 16 multi-stage (node:22-alpine)
- docker/postgres/ ← pgvector placeholder para v3.0
- docker-compose.yml ← 2 servicios (api:8000, web:3000)
- docker-compose.dev.yml ← hot reload con volumes
- .github/workflows/ci.yml ← working-directory: apps/api
- 292 unit tests pasando desde nueva ubicación
- .pre-commit-config.yaml restaurado al root (debe estar en root para git hooks)

## Commits de sesión
- 08463ca: fix(auth): add jti — sesión anterior
- f4d1315: chore: restructure to monorepo
- 4248f66: wip: pre-frontend-v2.1 handoff

## Próxima sesión
1. /gsd:new-milestone para v2.1 (frontend + routing semántico + production hardening)
2. Lanzar brief a cerebros 2+3+4 via CLI: cd apps/api && uv run mm orchestrate run "..."
3. Usar outputs como specs para el nuevo frontend
4. Inicializar Next.js 16 en apps/web/
