# Session 2026-03-18 — MCP Fixes + Momento 1 Complete

## Lo que se hizo

### Package Manager Rules (commits 2fb98ab)
- uv (Python) y pnpm (Node.js) obligatorios en todo el proyecto
- pip/npm/yarn eliminados de docs, scripts, installers
- CLAUDE.md actualizado, memoria persistente creada

### MCP Pipeline — 4 bugs corregidos (commit a0a11a4)
1. _check_claude_code() detecta nlm CLI (no CLAUDE_CODE_SESSION)
2. nlm syntax: "nlm query notebook <id> <query>" (posicional, no flags)
3. query_brain() agregado a MCPIntegration (protocolo MCPClient)
4. _parse_sections() strip "**" antes de parsear (NotebookLM usa **LABEL:**)

### Momento 1 completo
- MM_API_KEY: mmsk_ipUXq7O47uDs9j4XGZCXTuKJ08tK76FD (exportar en cada sesión)
- BRAIN-02-CONTEXT.md, BRAIN-03-CONTEXT.md, BRAIN-04-CONTEXT.md generados con MCP real

## Commits
- 2fb98ab: chore: enforce uv/pnpm package managers
- a0a11a4: fix(mcp): fix nlm integration + markdown bold labels
- 6f6f766: wip: 00-milestone-planning paused at task 3/3

## Próxima sesión
export MM_API_KEY="mmsk_ipUXq7O47uDs9j4XGZCXTuKJ08tK76FD"
/clear → /gsd:resume-work → gsd-roadmapper → ROADMAP.md v2.1
