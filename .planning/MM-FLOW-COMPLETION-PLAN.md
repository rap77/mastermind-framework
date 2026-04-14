# MM-Flow Completion Plan

**Creado:** 2026-04-13
**Última actualización:** 2026-04-13 (v2 — análisis de 3 repos fuente)
**Estado:** PLAN ACTIVO — pendiente de ejecución
**Objetivo:** Llevar MM-Flow del estado actual (40% stubs) al 100% funcional, incorporando lo mejor de GSD, Paperclip y OpenClaw

---

## Análisis de Repos Fuente

MM-Flow fue diseñado combinando 3 proyectos existentes. Cada uno aportó algo, pero ninguno fue aprovechado al 100%.

### GSD (`~/.claude/get-shit-done/`)
**Propósito:** Orquestador de fases con agentes especializados. Estado en Markdown+YAML+git.

| Lo que MM-Flow YA tomó | Lo que MM-Flow NO tomó (pero debería) |
|------------------------|---------------------------------------|
| Estructura de fases y STATE.md | **Model profiles por rol** (quality/balanced/budget triplets) |
| Verification en cascada | **Sub-fases decimales** (1.1, 1.2, 2.1) — más granular que wave_1/wave_2 |
| Frontmatter YAML para metadata | **"Next X" queries** — siguiente sub-fase disponible automáticamente |
| — | **Nyquist auditing** — valida cobertura real antes de marcar completo |

**Debilidad de GSD que MM-Flow mejoró:** Estado en filesystem plano → reemplazado por PostgreSQL multi-tenant.

---

### Paperclip (`/home/rpadron/proy/paperclip/`)
**Propósito:** Orquestador empresarial de agentes IA con org charts, budgets y multi-tenancy.

| Lo que MM-Flow YA tomó | Lo que MM-Flow NO tomó (pero debería) |
|------------------------|---------------------------------------|
| Multi-tenancy (org/project/workspace) | **Agentes como entidades ricas** — role, capabilities, permissions, status |
| Schema relacional PostgreSQL | **Org chart** — reportsTo (Brain #7 reporta al orquestador) |
| — | **Cost/budget tracking por brain** — tokens consumidos por agente, no solo por backend |
| — | **Heartbeat + online status** — saber si un brain agent está disponible |
| — | **Budget limits por brain** — cuánto puede gastar Brain #3 en una fase antes de escalar |

**Debilidad de Paperclip que MM-Flow mejoró:** Routing de ejecución opaco → MM-Flow tiene brain_router explícito.

---

### OpenClaw (`/home/rpadron/proy/openclaw/`)
**Propósito:** Asistente multi-canal con dispatch por skills y plugin SDK.

| Lo que MM-Flow YA tomó | Lo que MM-Flow NO tomó (pero debería) |
|------------------------|---------------------------------------|
| Concepto de routing | **Channel dispatch pattern** — cada "canal" (CLI, skill, API) tiene su propio handler |
| — | **Plugin SDK desacoplado** — agregar nueva skill/canal sin tocar el core |
| — | **Session + conversation threading** — contexto que se mantiene dentro del hilo, no solo cross-session |
| — | **Progressive reply streaming** — status updates mientras ejecuta (Wave 1 completada ✅...) |
| — | **Central Agent Registry** — tabla de qué agentes existen, qué hacen, cuándo aplican |
| — | **Security-first routing** — allowlists de qué brain puede hacer qué acción |

**Debilidad de OpenClaw que MM-Flow mejoró:** Multi-workspace no claro → PostgreSQL multi-tenant resuelve eso.

---

## Gaps Nuevos Identificados (No estaban en el plan original)

Estos 5 gaps no existían en el diseño original de MM-Flow y ninguno de los 3 repos los resuelve bien. MM-Flow tiene que crearlos desde cero:

| Gap | Descripción | Prioridad |
|-----|-------------|-----------|
| **Central Agent Registry** | Tabla en DB con qué brains existen, sus capacidades, modelo asignado, cuándo aplican en el flujo | ALTA |
| **Dynamic Dispatch Engine** | Motor que lee fase+estado y despacha brains automáticamente según `config.yml` | ALTA |
| **Budget tracking por brain** | Tokens consumidos por cada brain (no solo por backend) — para governance | MEDIA |
| **Sub-fases decimales** | Granularidad 1.1, 1.2 en vez de wave_1/wave_2 — permite pausar/resumir más fino | MEDIA |
| **Progressive status streaming** | Feedback visible mientras ejecuta: "Brain #4 consultado ✅ → Brain #5..." | BAJA |

---

## Diagnóstico de Estado Actual

### ✅ Implementado y funciona
| Componente | Archivo | Observaciones |
|------------|---------|---------------|
| MultiBackendManager | `.mm-flow/multi_backend_manager.py` | Lógica real, bien escrita |
| BackendScheduler | `.mm-flow/backend_scheduler.py` | Reset cycle detection OK |
| TokenLimiter | `.mm-flow/token_limiter.py` | Tracking OK |
| StateMachine | `.mm-flow/state_machine.py` | Transiciones + record_phase_execution() |
| BrainRouter | `.mm-flow/brain_router.py` | Routing por keywords — primitivo, reemplazar |
| VerificationGates | `.mm-flow/verification_gates.py` | Checks heurísticos OK |
| EngramContextLoader | `.mm-flow/context_loader.py` | Parseo OK, Engram query stubbed |
| `mm-flow init` | cli/commands.py | Funciona (lee PostgreSQL) |
| `mm-flow status` | cli/commands.py | Tabla de backends OK |
| `mm-flow context` | cli/commands.py | Genera CONTEXT.md (con fallback) |
| SQL Schemas | docker/postgres/*.sql | Escritos. Schema principal YA en DB. Audit trail NO |
| Audit API | apps/api/routers/audit.py | Escrito (51.9K), NO wired en FastAPI |
| Engram Sync | apps/api/services/engram_sync.py | Escrito (44.3K), NO wired |
| PostgreSQL (mastermind) | docker-compose.yml | ✅ Levantado hoy. Schema principal presente |

### ❌ Stubs / Placeholders
| Componente | Problema | Impacto |
|------------|---------|---------|
| `mm-flow execute-phase` | Imprime "[Placeholder]", no ejecuta nada real | CRÍTICO |
| `mm-flow plan-phase` | Imprime "Would invoke", no invoca el skill | CRÍTICO |
| `night_mode._execute_subtask()` | Retorna output sintético | ALTO |
| `context_loader._try_engram_api_query()` | Stubbed — no puede llamar Engram desde CLI | ALTO |
| `brain_router.py` | Routing por keywords hardcodeados — no lee config.yml | ALTO |

### 🔴 Missing — diseñado pero no existe
| Feature | Impacto |
|---------|---------|
| Audit trail tables (phase_executions, decisions, etc.) | BLOQUEANTE para audit |
| Audit router NO wired en FastAPI | ALTO |
| `mm-flow-statusline.js` hook | MEDIO |
| `~/.claude/backends.sh` | MEDIO |
| `config.yml` brain routing rules | ALTO — BrainRouter lo necesita |
| Hook auto-save a Engram (problema original) | ALTO |
| Central Agent Registry (tabla en DB) | ALTO — nuevo gap |
| Dynamic Dispatch Engine | ALTO — nuevo gap |
| Budget tracking por brain | MEDIO — nuevo gap |

---

## El Problema Arquitectural Central

MM-Flow CLI es Python. Las skills de MM-Flow son Markdown ejecutadas por Claude Code.
**No hay puente entre ellos.**

```
CLI (Python)          Claude Code (Skills)
     │                      │
     │   ← sin puente →     │
     │                      │
mm-flow execute-phase    /mm:execute-phase
   [Placeholder]           [funciona]
```

**Modelo correcto (CLI como helper de estado, Claude como executor):**
1. Usuario corre `/mm:execute-phase N` en Claude Code
2. El skill llama `mm-flow execute-phase --phase N --start` (registra en DB)
3. Claude ejecuta el trabajo real
4. Al final el skill llama `mm-flow execute-phase --phase N --complete --commit <hash>`

El CLI NO necesita ejecutar fases — eso es trabajo de Claude.

---

## Plan de Completación — 5 Fases

---

### FASE 1: Infrastructure Foundation ✅ PARCIALMENTE COMPLETA
**Estado:** PostgreSQL levantado, schema principal presente. Falta audit trail.

#### Task 1.1: ✅ PostgreSQL levantado
```bash
docker compose up -d postgres  # ya ejecutado
```

#### Task 1.2: Aplicar Audit Trail schema (PENDIENTE)
```bash
docker exec -i mastermind-postgres-1 psql -U postgres -d mastermind_bd \
  < docker/postgres/mm-flow-audit.sql
```

**Verificación:**
```sql
-- Debe mostrar phase_executions, decisions, dev_sessions, verification_gates, artifacts, etc.
SELECT table_name FROM information_schema.tables
WHERE table_name IN ('phase_executions','decisions','audit_log','brain_feedback');
```

#### Task 1.3: Aplicar seed data actualizada
```bash
# Verificar que 'mastermind' y 'RAP-software' ya existen (sí existen)
# Solo aplicar seed si faltan workspaces con current_phase
docker exec -i mastermind-postgres-1 psql -U postgres -d mastermind_bd \
  -c "SELECT w.name, w.current_phase FROM workspaces w JOIN projects p ON w.project_id = p.id WHERE p.slug = 'mastermind';"
```

#### Task 1.4: Crear Central Agent Registry (tabla nueva)
```sql
-- Nueva tabla: no estaba en el diseño original
CREATE TABLE agent_registry (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  organization_id UUID NOT NULL REFERENCES organizations(id),
  brain_id INTEGER NOT NULL,          -- 1-7 (dev), 8-23 (marketing)
  name VARCHAR NOT NULL,              -- "Brain #1 (Product Strategy)"
  role VARCHAR NOT NULL,              -- "product_strategy", "ux_research", etc.
  capabilities TEXT[],                -- ["product_vision", "user_research", "prioritization"]
  model_quality VARCHAR DEFAULT 'balanced',  -- quality|balanced|budget (GSD pattern)
  model_budget VARCHAR DEFAULT 'haiku',      -- opus|sonnet|haiku
  applies_in TEXT[],                  -- ["DISCUSSION", "PLANNING"]
  is_barrier BOOLEAN DEFAULT FALSE,   -- TRUE = bloquea hasta aprobar (Brain #7)
  token_budget_per_phase INTEGER DEFAULT 10000,
  tokens_consumed_total INTEGER DEFAULT 0,
  status VARCHAR DEFAULT 'available', -- available|busy|offline
  last_heartbeat TIMESTAMP,
  created_at TIMESTAMP DEFAULT NOW(),
  UNIQUE(organization_id, brain_id)
);

-- Seed de los 7 dev brains
INSERT INTO agent_registry (organization_id, brain_id, name, role, capabilities, model_quality, applies_in, is_barrier) VALUES
  ((SELECT id FROM organizations WHERE slug = 'RAP-software'), 1, 'Brain #1 Product Strategy', 'product_strategy', ARRAY['vision','prioritization','roadmap'], 'quality', ARRAY['DISCUSSION'], FALSE),
  ((SELECT id FROM organizations WHERE slug = 'RAP-software'), 2, 'Brain #2 UX Research', 'ux_research', ARRAY['user_flows','wireframes','usability'], 'balanced', ARRAY['DISCUSSION'], FALSE),
  ((SELECT id FROM organizations WHERE slug = 'RAP-software'), 3, 'Brain #3 UI Design', 'ui_design', ARRAY['components','tokens','visual_design'], 'balanced', ARRAY['DISCUSSION'], FALSE),
  ((SELECT id FROM organizations WHERE slug = 'RAP-software'), 4, 'Brain #4 Frontend', 'frontend', ARRAY['react','typescript','state_management'], 'balanced', ARRAY['PLANNING'], FALSE),
  ((SELECT id FROM organizations WHERE slug = 'RAP-software'), 5, 'Brain #5 Backend', 'backend', ARRAY['api_design','database','architecture'], 'balanced', ARRAY['PLANNING'], FALSE),
  ((SELECT id FROM organizations WHERE slug = 'RAP-software'), 6, 'Brain #6 QA DevOps', 'qa_devops', ARRAY['testing','ci_cd','reliability'], 'balanced', ARRAY['PLANNING'], FALSE),
  ((SELECT id FROM organizations WHERE slug = 'RAP-software'), 7, 'Brain #7 Growth Evaluator', 'meta_evaluator', ARRAY['synthesis','critique','risk_assessment'], 'quality', ARRAY['DISCUSSION','PLANNING','VERIFICATION'], TRUE);
```

**Entregable:** `SELECT * FROM agent_registry;` retorna 7 filas.

---

### FASE 2: Wire the Bridge — CLI ↔ Skills (Día 2)
**Objetivo:** Skills `/mm:` llaman al CLI para registrar estado. CLI deja de ser placeholder.

#### Task 2.1: Agregar lifecycle flags al CLI
Modificar `cli/commands.py` — reemplazar el placeholder de `execute-phase` con operaciones reales:

```python
@cli.command()
@click.option("--phase", type=int, required=True)
@click.option("--start", is_flag=True, help="Mark phase as started, return execution_id")
@click.option("--complete", is_flag=True, help="Mark phase as completed")
@click.option("--commit", default=None, help="Git commit hash at completion")
@click.option("--tokens", type=int, default=0, help="Tokens consumed")
@click.option("--summary", default="", help="Execution summary")
def execute_phase(phase, start, complete, commit, tokens, summary):
    """Lifecycle management for phase execution."""
    ctx = _load_context()
    sm = StateMachine(ctx["org_id"], ctx["project_id"], ctx["workspace_id"], _db_url())

    if start:
        execution_id = sm.record_phase_execution(
            phase=phase, status="in_progress",
            state_data={"started_via": "skill"},
            backend_used=ctx.get("backend", "claude")
        )
        click.echo(f"execution_id:{execution_id}")  # parseable por el skill

    elif complete:
        sm.record_phase_execution(
            phase=phase, status="completed",
            state_data={"git_commit": commit, "summary": summary},
            backend_used=ctx.get("backend", "claude"),
            tokens_consumed=tokens
        )
        click.echo(f"✅ Phase {phase} marked complete")
```

#### Task 2.2: Reemplazar BrainRouter por Dynamic Dispatch Engine
El `brain_router.py` actual usa keywords hardcodeados. Reemplazar por dispatch que lee `config.yml`:

```python
class DynamicDispatchEngine:
    """Despacha brains según fase+estado leyendo config.yml y agent_registry."""

    def dispatch(self, phase: int, moment: str) -> list[dict]:
        """
        moment: DISCUSSION | PLANNING | EXECUTION_WAVE | VERIFICATION
        Retorna lista de brains a despachar + si son barrier o parallel
        """
        config = self._load_config()
        routing = config["brain_routing"][moment]
        brains = self._get_brains_from_registry(routing["brains"])
        return {
            "parallel": [b for b in brains if not b["is_barrier"]],
            "barrier": [b for b in brains if b["is_barrier"]],
        }
```

#### Task 2.3: Actualizar skills `/mm:execute-phase` y `/mm:plan-phase`
Los skills deben bookend la ejecución con llamadas CLI:
```bash
# Al inicio del skill:
EXEC_ID=$(mm-flow execute-phase --phase $PHASE --start | grep execution_id | cut -d: -f2)

# Al final del skill:
mm-flow execute-phase --phase $PHASE --complete \
  --commit $(git rev-parse HEAD) \
  --tokens $TOKENS_USED \
  --summary "Phase $PHASE completed via /mm:execute-phase"
```

**Entregable:** `/mm:execute-phase 19` → `SELECT * FROM phase_executions WHERE phase = 19;` retorna fila.

---

### FASE 3: Fix Context Persistence — El Problema Original (Día 2-3)
**Objetivo:** Contexto de sesión NUNCA se pierde, sin depender de que Claude recuerde guardar.

#### Task 3.1: Hook Stop → checkpoint local (seguro de vida)
Crear `~/.claude/hooks/mm-flow-checkpoint.js`:

```javascript
// Dispara en cada Stop (fin de respuesta Claude)
// Escribe .planning/SESSION-CHECKPOINT.md con:
//   - timestamp, saved: false
//   - último tool usado + archivos modificados
//   - decisiones detectadas por keywords ("decidimos", "vamos a", "mejor usar", "dale")
// No requiere MCP — es filesystem puro
```

Agregar a `settings.json`:
```json
"Stop": [{
  "hooks": [{
    "type": "command",
    "command": "node /home/rpadron/.claude/hooks/mm-flow-checkpoint.js"
  }]
}]
```

#### Task 3.2: SessionStart → detectar checkpoints sin guardar
Modificar `mm-flow-session-init.js` para:
1. Leer `.planning/SESSION-CHECKPOINT.md`
2. Si `saved: false` → inyectar warning en contexto:
   ```
   ⚠️ SESIÓN ANTERIOR SIN GUARDAR
   Última actividad: [timestamp]
   Decisiones detectadas: [lista]
   → Llamá mem_session_summary ANTES de continuar.
   ```

#### Task 3.3: UserPromptSubmit → recordatorio cada 10 mensajes
Agregar a settings.json matcher global que inyecte cada 10 mensajes:
```
[CHECKPOINT] ¿Hiciste decisiones o descubrimientos en los últimos intercambios?
Si sí → llamá mem_save AHORA. Si no → ignorar este mensaje.
```

#### Task 3.4: Fix context_loader — Engram real vía skill
`context_loader._try_engram_api_query()` es un stub y así debe quedarse en el CLI.
El fix correcto: el skill `/mm:plan-phase` llama `mem_search` nativamente (tiene acceso MCP)
y escribe CONTEXT.md. El CLI solo lee el archivo que el skill generó.

Flujo correcto:
```
/mm:plan-phase N
  → skill llama mem_search("phase N decisions")
  → skill escribe .planning/phases/N-*/CONTEXT.md
  → mm-flow plan-phase --phase N --context-ready  ← CLI registra artifact en DB
```

**Entregable:** Sesión termina → `SESSION-CHECKPOINT.md` existe con `saved: false`. Próxima sesión → warning visible.

---

### FASE 4: Wire Audit Trail + Config + Missing Pieces (Día 3-4)
**Objetivo:** Audit trail funcional, config.yml, credentials, statusline.

#### Task 4.1: Wire audit router en FastAPI
```python
# apps/api/main.py
from apps.api.routers import audit
app.include_router(audit.router, prefix="/api/audit", tags=["audit"])
```

**Verificación:** `curl http://localhost:8001/api/audit/projects/{id}/summary` → 200

#### Task 4.2: Crear `config.yml` con brain routing rules + model profiles (GSD pattern)
```yaml
# .planning/.mm-flow/config.yml

# Model profiles (tomado de GSD)
model_profiles:
  quality:   { model: claude-opus-4-6,   use_when: "critical decisions, Brain #7 barrier" }
  balanced:  { model: claude-sonnet-4-6, use_when: "standard domain brains" }
  budget:    { model: claude-haiku-4-5,  use_when: "context recovery, status checks" }

# Brain routing por momento del flujo
brain_routing:
  DISCUSSION:
    brains: [1, 2, 3]
    parallel: true
    barrier: [7]
    model_override: quality  # Brain #7 usa quality en DISCUSSION
  PLANNING:
    brains: [4, 5, 6]
    parallel: true
    barrier: [7]
  EXECUTION_WAVE:
    brains: [7]
    parallel: false
  VERIFICATION:
    brains: [7]
    parallel: false
    blocking: true  # No avanza hasta aprobación

# Verification gates
verification_gates:
  spec_coverage_threshold: 0.95
  max_gate_retries: 1
  escalate_on_failure: true

# Sub-fases (GSD pattern — más granular que wave_1/wave_2)
phase_granularity:
  use_decimals: true       # 1.1, 1.2, 1.3 en vez de wave_1, wave_2
  max_sub_phases: 9        # hasta 1.9 por fase
  auto_advance: true       # si 1.1 completa, avanza a 1.2 automáticamente
```

#### Task 4.3: Crear `~/.claude/backends.sh`
```bash
#!/bin/bash
# Carga credenciales de backends LLM
# Fuente: ~/.claude/secrets/ (gitignored)

export_claude_credentials() {
  [ -f ~/.claude/secrets/anthropic_key ] && \
    export ANTHROPIC_API_KEY="$(cat ~/.claude/secrets/anthropic_key)"
}

export_openrouter_credentials() {
  [ -f ~/.claude/secrets/openrouter_key ] && \
    export OPENROUTER_API_KEY="$(cat ~/.claude/secrets/openrouter_key)"
}

export_zai_credentials() {
  [ -f ~/.claude/secrets/zai_key ] && \
    export ZAI_API_KEY="$(cat ~/.claude/secrets/zai_key)"
}

export_all() {
  export_claude_credentials
  export_openrouter_credentials
  export_zai_credentials
}
```

#### Task 4.4: Crear `mm-flow-statusline.js` hook (OpenClaw pattern)
Inspirado en el progressive status de OpenClaw — feedback visible mientras trabaja:

```javascript
// PostToolUse hook — muestra después de cada tool call:
// [mm-flow] z.ai 180K/200K ▓▓▓▓▓▓▓▓░░ 90% | Phase 19 PLANNING | Brain #5 🟢
// Si > 80%: ⚠️  | Si > 95%: 🔴 switch inminente
```

---

### FASE 5: Adoptar Patrones Pendientes de los 3 Repos (Día 4-5)
**Objetivo:** Incorporar lo bueno que MM-Flow nunca tomó.

#### Task 5.1: Budget tracking por brain (Paperclip pattern)
Agregar a `agent_registry`: columna `tokens_consumed_total` ya está en el schema de Task 1.4.
Actualizar `DynamicDispatchEngine` para decrementar budget al despachar un brain:

```python
def consume_budget(self, brain_id: int, tokens_used: int):
    """Registra tokens consumidos por un brain en esta fase."""
    # UPDATE agent_registry SET tokens_consumed_total += tokens_used WHERE brain_id = ?
    # Si tokens_consumed_total > token_budget_per_phase * 3: escalar a usuario
```

#### Task 5.2: Heartbeat de brain agents (Paperclip pattern)
Agregar comando CLI:
```bash
mm-flow brain-status  # muestra tabla de brains con último heartbeat y tokens consumidos
```

#### Task 5.3: Sub-fases decimales en StateMachine (GSD pattern)
Extender `state_machine.py` para soportar fases decimales:
```python
sm.set_sub_phase(phase=19, sub=1)   # 19.1
sm.advance_sub_phase(phase=19)       # 19.1 → 19.2
sm.get_current_position()            # {"phase": 19, "sub": 2, "label": "19.2"}
```

#### Task 5.4: Plugin SDK básico (OpenClaw pattern)
Crear estructura que permita agregar nuevos canales/skills sin tocar el core:
```
.planning/.mm-flow/
├── plugins/
│   ├── __init__.py
│   ├── base_plugin.py       # Interfaz que todo plugin debe implementar
│   ├── slack_plugin.py      # Futuro: notificaciones via Slack
│   └── webhook_plugin.py    # Futuro: webhooks externos
```

Por ahora solo la estructura base. Los plugins concretos son futuros.

---

## Orden de Ejecución

```
FASE 1 (bloqueante para todo)
  ├── 1.2: Audit trail schema (SQL)
  ├── 1.3: Verificar seed data
  └── 1.4: Agent Registry tabla + seed 7 brains

FASE 2 (depende de FASE 1)
  ├── 2.1: CLI lifecycle flags (--start/--complete)
  ├── 2.2: Dynamic Dispatch Engine (reemplaza brain_router.py)
  └── 2.3: Skills wired con CLI bookends

FASE 3 (independiente — puede ir en paralelo con FASE 2)
  ├── 3.1: Stop hook → SESSION-CHECKPOINT.md
  ├── 3.2: SessionStart → detectar checkpoint pendiente
  ├── 3.3: UserPromptSubmit → recordatorio periódico
  └── 3.4: context_loader flow fix

FASE 4 (depende de FASE 1 para audit trail)
  ├── 4.1: Audit router wired en FastAPI
  ├── 4.2: config.yml con model profiles + brain routing
  ├── 4.3: backends.sh
  └── 4.4: statusline hook

FASE 5 (puede ir después de todo)
  ├── 5.1: Budget tracking por brain
  ├── 5.2: Heartbeat CLI command
  ├── 5.3: Sub-fases decimales
  └── 5.4: Plugin SDK estructura base
```

---

## Definition of Done

| Criterio | Verificación |
|---------|-------------|
| Audit trail tables creadas | `SELECT table_name FROM information_schema.tables WHERE table_name = 'phase_executions';` |
| Agent Registry con 7 brains | `SELECT count(*) FROM agent_registry;` → 7 |
| `mm-flow status` sin errores | `mm-flow status` |
| `/mm:execute-phase 19` registra en DB | `SELECT * FROM phase_executions WHERE phase = 19;` |
| Brain dispatch lee config.yml | `mm-flow dispatch --phase 19 --moment PLANNING` → brains 4,5,6 + barrier 7 |
| Sesión termina → checkpoint creado | `ls .planning/SESSION-CHECKPOINT.md` |
| Próxima sesión detecta checkpoint | Abrir sesión → ver warning |
| Audit router responde 200 | `curl http://localhost:8001/api/audit/.../summary` |
| Statusline visible | Abrir Claude Code → ver status en cada respuesta |
| Sub-fases funcionan | `mm-flow status --phase 19` → muestra 19.1, 19.2 |

---

## Estimación

| Fase | Duración | Complejidad |
|------|----------|-------------|
| FASE 1: Infrastructure | 1-2h | Baja (SQL + seed) |
| FASE 2: CLI ↔ Skills bridge | 3-4h | Media |
| FASE 3: Context persistence | 2-3h | Media (hooks) |
| FASE 4: Audit + config + extras | 2-3h | Baja-Media |
| FASE 5: Patrones pendientes | 3-4h | Media |
| **TOTAL** | **~12-15h** | — |

---

## Archivos a Crear/Modificar

### Crear (nuevos)
- `~/.claude/hooks/mm-flow-checkpoint.js` — Stop hook checkpoint local
- `~/.claude/backends.sh` — Credentials loader
- `.planning/.mm-flow/config.yml` — Brain routing + model profiles
- `.planning/.mm-flow/dispatch_engine.py` — Dynamic Dispatch Engine (reemplaza brain_router)
- `.planning/.mm-flow/plugins/__init__.py` — Plugin SDK base
- `.planning/.mm-flow/plugins/base_plugin.py` — Interfaz base

### Modificar (existentes)
- `.planning/.mm-flow/cli/commands.py` — `--start`/`--complete` flags, `brain-status`, `dispatch`
- `.planning/.mm-flow/state_machine.py` — Sub-fases decimales
- `.planning/.mm-flow/brain_router.py` — Deprecar, redirigir a dispatch_engine.py
- `~/.claude/hooks/mm-flow-session-init.js` — Detectar checkpoints sin guardar
- `~/.claude/settings.json` — Stop hook + UserPromptSubmit global
- `apps/api/main.py` — Wire audit router
- `.claude/skills/mm/execute-phase/SKILL.md` — CLI bookends
- `.claude/skills/mm/plan-phase/SKILL.md` — Engram nativo + CLI bookend

### Ejecutar (SQL, no código)
- `docker/postgres/mm-flow-audit.sql` — Audit trail tables
- SQL inline para `agent_registry` table + seed 7 brains

---

**v2 — Actualizado:** 2026-04-13 (incorpora análisis GSD + Paperclip + OpenClaw)
**Próximo paso:** FASE 1 — aplicar audit trail SQL + crear agent_registry
