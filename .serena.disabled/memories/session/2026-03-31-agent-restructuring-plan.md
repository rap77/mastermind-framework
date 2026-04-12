# Session: Agent Restructuring Plan — 2026-03-31

## What Was Done

### Auditoría completa del sistema
- **12 islas desconectadas** identificadas — ExperienceLogger (crítica), BrainEnvelope, StateLogger, TaskRepository, Memory/InterviewLogger, embedding stub, flow-definitions.yaml, precedents catalog, LegacyBrainAdapter, marketing brains config, evaluator configs
- **Dos sistemas paralelos** descubiertos: Claude Code Agents (`.claude/agents/mm/`) vs Python BrainExecutor (`apps/api/mastermind_cli/orchestrator/`) — completamente desconectados entre sí
- **Gap central:** TODO en `tasks.py:98` — POST /api/tasks crea record pero NO ejecuta nada
- **`create_experience_schema()` NO se llama en startup** — tabla `experience_records` no existe en producción

### Flujos que SÍ funcionan
- Login → JWT → páginas protegidas ✅
- GET /api/brains (24 brains, read-only) ✅
- API Key management ✅
- Token refresh + rotation ✅
- WebSocket infrastructure (lista pero en silencio — nadie emite eventos) ✅

### Decisiones arquitectónicas
- **Arquitectura UNIFICADA:** Claude Code Agents son la implementación, Python Coordinator los orquesta
- **nlm CLI = Tool nativa** del agente (CLI-as-a-Service, via Bash)
- **brain_memory.py** = script CLI puente entre Claude Agents (Bash) y ExperienceLogger (Python async)
- **Piloto: Brain #1** — Done = cita experiencias pasadas del ExperienceLogger
- **v3.0 en HOLD** hasta que los agentes funcionen correctamente

### Plan aprobado
6 fases guardadas en `/home/rpadron/.claude/plans/sprightly-conjuring-hartmanis.md`:
1. Agent Contract (brain_memory.py + modificar brain-01-product.md)
2. ExperienceLogger al startup + REST endpoint
3. API ↔ Coordinator Connection (resolver TODO tasks.py:98)
4. Brain-to-Brain Communication (brain_router.py)
5. Autonomía básica (POST /api/tasks/auto)
6. Replicar a brains #2-#7

## Key Technical Findings

- Brain #1 frontmatter ya tiene `tools: Read, Glob, Grep, Bash` (correcto)
- Solo hay que: eliminar `mcpServers: notebooklm-mcp` + agregar Protocolo de Memoria
- Notebook ID Brain #1: `f276ccb3-0bce-4069-8b55-eae8693dbe75` (de `mcp_integration.py` NOTEBOOK_IDS)
- `StatelessCoordinator.execute_flow()` existe y funciona — no hay que reescribirlo
- `ExperienceLogger.log_execution()` / `get_recent_by_brain()` ya implementados — no tocar

## Next Session
/clear → /sc:load → /gsd:resume-work → Implementar Fases 1+2 en paralelo
