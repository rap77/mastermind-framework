# MM-Flow Completion Plan

**Creado:** 2026-04-13
**Última actualización:** 2026-04-14 (v4 — todos los items del brain council resueltos)
**Estado:** PLAN ACTIVO — aprobado brain council, pendiente de ejecución
**Objetivo:** Llevar MM-Flow del estado actual (40% stubs) al 100% funcional, incorporando lo mejor de GSD, Paperclip y OpenClaw

---

## Análisis de Repos Fuente

MM-Flow fue diseñado combinando 3 proyectos existentes. Cada uno aportó algo, pero ninguno fue aprovechado al 100%.

### GSD (`~/.claude/get-shit-done/`)
**Propósito:** Orquestador de fases con agentes especializados. Estado en Markdown+YAML+git.

| Lo que MM-Flow YA tomó | Lo que MM-Flow NO tomó (pero debería) |
|------------------------|---------------------------------------|
| Estructura de fases y STATE.md | **Model profiles por rol** (quality/balanced/budget triplets) |
| Verification en cascada | **"Next X" queries** — siguiente sub-fase disponible automáticamente |
| Frontmatter YAML para metadata | **Nyquist auditing** — valida cobertura real antes de marcar completo |

**Debilidad de GSD que MM-Flow mejoró:** Estado en filesystem plano → reemplazado por PostgreSQL multi-tenant.

---

### Paperclip (`/home/rpadron/proy/paperclip/`)
**Propósito:** Orquestador empresarial de agentes IA con org charts, budgets y multi-tenancy.

| Lo que MM-Flow YA tomó | Lo que MM-Flow NO tomó (pero debería) |
|------------------------|---------------------------------------|
| Multi-tenancy (org/project/workspace) | **Agentes como entidades ricas** — role, capabilities, permissions, status |
| Schema relacional PostgreSQL | **Org chart** — reportsTo (Brain #7 reporta al orquestador) |
| — | **Cost/budget tracking por brain** — absorbido en FASE 2 Task 2.2 (DynamicDispatchEngine) |

**Debilidad de Paperclip que MM-Flow mejoró:** Routing de ejecución opaco → MM-Flow tiene brain_router explícito.

---

### OpenClaw (`/home/rpadron/proy/openclaw/`)
**Propósito:** Asistente multi-canal con dispatch por skills.

| Lo que MM-Flow YA tomó | Lo que MM-Flow NO tomó (pero debería) |
|------------------------|---------------------------------------|
| Concepto de routing | **Channel dispatch pattern** — cada "canal" (CLI, skill, API) tiene su propio handler |
| — | **Session + conversation threading** — contexto que se mantiene dentro del hilo, no solo cross-session |
| — | **Progressive reply streaming** — status updates mientras ejecuta |
| — | **Central Agent Registry** — tabla de qué agentes existen, qué hacen, cuándo aplican |
| — | **Security-first routing** — allowlists de qué brain puede hacer qué acción |

**Debilidad de OpenClaw que MM-Flow mejoró:** Multi-workspace no claro → PostgreSQL multi-tenant resuelve eso.

---

## Gaps Nuevos Identificados (No estaban en el plan original)

| Gap | Descripción | Prioridad |
|-----|-------------|-----------|
| **Central Agent Registry** | Tabla en DB con qué brains existen, sus capacidades, modelo asignado, cuándo aplican en el flujo | ALTA |
| **Dynamic Dispatch Engine** | Motor que lee fase+estado y despacha brains automáticamente según `config.yml` | ALTA |
| **Progressive status streaming** | Feedback visible mientras ejecuta: "Brain #4 consultado ✅ → Brain #5..." | BAJA |

> **Nota:** Budget tracking por brain y sub-fases decimales fueron evaluados como Build Trap (ver FASE 5 eliminada).

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
| Audit API | apps/api/routers/audit.py | Escrito (51.9K), **YA wired en app.py line 212** |
| phase_executions table | apps/api/services/database.py:416 | **YA EXISTE** — no crear de nuevo |
| Engram Sync | apps/api/services/engram_sync.py | Escrito (44.3K), NO wired |
| PostgreSQL (mastermind) | docker-compose.yml | ✅ Levantado. Schema principal presente |

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
| Audit API: 0/13 rutas con JWT auth | BLOQUEANTE — producción insegura |
| `mm-flow-statusline.js` hook | MEDIO — existe parcialmente (ver FASE 4) |
| `~/.claude/backends.sh` | MEDIO |
| `config.yml` brain routing rules + loader | ALTO — DynamicDispatchEngine lo necesita |
| Hook auto-save a Engram (problema original) | ALTO |
| Central Agent Registry (tabla en DB) | ALTO — nuevo gap |
| Dynamic Dispatch Engine | ALTO — nuevo gap |

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

## SLIs y Métricas de Éxito

```
SLI-1 (CLI Activation Rate — OEC principal):
  % de phase starts que incluyen mm-flow --start en primeros 60s
  Target: >80%
  Medido via: session_logs table (FASE 1 schema)
  Alerta si: <50% a las 2 semanas → CLI no adoptado → FASE 1-3 tiene ROI cero

SLI-2 (Brain #7 Barrier Latency):
  P95 de evaluación del barrier (domain outputs → verdict)
  Target: <20s
  Hard limit: 30s (asyncio.wait_for timeout)
  Alerta si: P95 >45s → T1 > 300s profitability threshold superado

SLI-3 (Dispatch Correctness Rate):
  % dispatches con brain set correcto vs oracle table por moment
  Target: >95%
  Oracle: PLANNING → [4,5,6] + barrier [7], DISCUSSION → [1,2,3] + barrier [7]
  Medido via: unit tests con tabla oracle explícita en FASE 2

SLI-4 (Checkpoint Fidelity):
  % sesiones post-checkpoint que llegan a primera respuesta sustantiva sin preguntar contexto
  Target: >90%
  Medido: manual spot-check semanal, binary pass/fail por sesión

SLI-5 (Audit Auth Coverage):
  % rutas audit.py con Depends(get_current_user_any)
  Target: 100% antes de cerrar FASE 4
  Actualmente: 0/13 = 0%
  Medido: grep count + test automático en CI

Guardrail — agent_registry isolation:
  Seed dos veces en CI → COUNT(*) = 7 por proyecto
  Si assertion falla → FASE 1 DoD no satisfecha

Dependencia chicken-and-egg documentada:
  agent_registry DEBE estar seeded antes de que DynamicDispatchEngine pueda despachar.
  FASE 1 (Task 1.4) BLOQUEA FASE 2 (Task 2.2).
```

---

## Plan de Completación — 4 Fases

> **Nota:** FASE 5 fue eliminada como Build Trap. Budget tracking absorbido en FASE 2 Task 2.2. Heartbeat presupone brains como procesos independientes (no existen así). Sub-fases decimales no reducen T1. Plugin SDK presupone canal externo no planificado.

---

### FASE 1: Infrastructure Foundation ✅ PARCIALMENTE COMPLETA
**Estado:** PostgreSQL levantado, schema principal presente. Falta audit trail, agent_registry, config loader.

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

> **NOTA:** `phase_executions` YA EXISTE en `apps/api/services/database.py:416`. Verificar antes de re-crear.

#### Task 1.3: Aplicar seed data actualizada
```bash
# Verificar que 'mastermind' y 'RAP-software' ya existen (sí existen)
# Solo aplicar seed si faltan workspaces con current_phase
docker exec -i mastermind-postgres-1 psql -U postgres -d mastermind_bd \
  -c "SELECT w.name, w.current_phase FROM workspaces w JOIN projects p ON w.project_id = p.id WHERE p.slug = 'mastermind';"
```

#### Task 1.4: Crear Central Agent Registry (tabla nueva)

> **CRÍTICO — Multi-tenancy:** `UNIQUE(org_id, brain_id)` rompe multi-tenancy.
> Con esa constraint, Brain #1 de Proyecto A y Brain #1 de Proyecto B
> son la MISMA FILA — comparten budget y execution history.
> La constraint correcta es `(organization_id, project_id, brain_id)`.

```sql
-- Nueva tabla: no estaba en el diseño original
CREATE TABLE agent_registry (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  organization_id UUID NOT NULL REFERENCES organizations(id),
  project_id UUID NOT NULL REFERENCES projects(id),
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
  UNIQUE(organization_id, project_id, brain_id)  -- correcto: aislamiento multi-tenant
);

-- Seed de los 7 dev brains — idempotente con DO $$ guard + ON CONFLICT DO NOTHING
DO $$ BEGIN
  INSERT INTO agent_registry (organization_id, project_id, brain_id, name, role, capabilities, model_quality, applies_in, is_barrier)
  VALUES
    (
      (SELECT id FROM organizations WHERE slug = 'RAP-software'),
      (SELECT id FROM projects WHERE slug = 'mastermind'),
      1, 'Brain #1 Product Strategy', 'product_strategy',
      ARRAY['vision','prioritization','roadmap'], 'quality', ARRAY['DISCUSSION'], FALSE
    ),
    (
      (SELECT id FROM organizations WHERE slug = 'RAP-software'),
      (SELECT id FROM projects WHERE slug = 'mastermind'),
      2, 'Brain #2 UX Research', 'ux_research',
      ARRAY['user_flows','wireframes','usability'], 'balanced', ARRAY['DISCUSSION'], FALSE
    ),
    (
      (SELECT id FROM organizations WHERE slug = 'RAP-software'),
      (SELECT id FROM projects WHERE slug = 'mastermind'),
      3, 'Brain #3 UI Design', 'ui_design',
      ARRAY['components','tokens','visual_design'], 'balanced', ARRAY['DISCUSSION'], FALSE
    ),
    (
      (SELECT id FROM organizations WHERE slug = 'RAP-software'),
      (SELECT id FROM projects WHERE slug = 'mastermind'),
      4, 'Brain #4 Frontend', 'frontend',
      ARRAY['react','typescript','state_management'], 'balanced', ARRAY['PLANNING'], FALSE
    ),
    (
      (SELECT id FROM organizations WHERE slug = 'RAP-software'),
      (SELECT id FROM projects WHERE slug = 'mastermind'),
      5, 'Brain #5 Backend', 'backend',
      ARRAY['api_design','database','architecture'], 'balanced', ARRAY['PLANNING'], FALSE
    ),
    (
      (SELECT id FROM organizations WHERE slug = 'RAP-software'),
      (SELECT id FROM projects WHERE slug = 'mastermind'),
      6, 'Brain #6 QA DevOps', 'qa_devops',
      ARRAY['testing','ci_cd','reliability'], 'balanced', ARRAY['PLANNING'], FALSE
    ),
    (
      (SELECT id FROM organizations WHERE slug = 'RAP-software'),
      (SELECT id FROM projects WHERE slug = 'mastermind'),
      7, 'Brain #7 Growth Evaluator', 'meta_evaluator',
      ARRAY['synthesis','critique','risk_assessment'], 'quality',
      ARRAY['DISCUSSION','PLANNING','VERIFICATION'], TRUE
    )
  ON CONFLICT DO NOTHING;
END $$;
```

**Guardrail CI:** Seed dos veces → `SELECT COUNT(*) FROM agent_registry WHERE project_id = (SELECT id FROM projects WHERE slug = 'mastermind')` → debe retornar 7 (no 14).

**Entregable:** `SELECT count(*) FROM agent_registry WHERE project_id = (SELECT id FROM projects WHERE slug = 'mastermind');` → 7.

#### Task 1.5: Crear config.yml loader + config.yml con model profiles [NUEVO — BLOQUEANTE para FASE 2]

> **Por qué en FASE 1:** DynamicDispatchEngine (FASE 2 Task 2.2) lee config.yml.
> Sin loader en FASE 1, FASE 2 no puede cerrar su DoD.
> Feedback loop detectado: sin loader, engine usa seed data y aparece funcional,
> pero config changes en FASE 4 nunca conectan.

**Archivo:** `.planning/.mm-flow/config.yml`

```yaml
# Model profiles (tomado de GSD)
model_profiles:
  quality:
    model: claude-opus-4-6
    use_when: "critical decisions, Brain #7 barrier"
  balanced:
    model: claude-sonnet-4-6
    use_when: "standard domain brains"
  budget:
    model: claude-haiku-4-5
    use_when: "context recovery, status checks"

# Brain routing por momento del flujo
brain_routing:
  DISCUSSION:
    brains: [1, 2, 3]
    parallel: true
    barrier: [7]
    model_override: quality
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
    blocking: true

# Verification gates
verification_gates:
  spec_coverage_threshold: 0.95
  max_gate_retries: 1
  escalate_on_failure: true
```

**Loader:** `.planning/.mm-flow/config_loader.py`

```python
from dataclasses import dataclass
from typing import Literal
import yaml
import logging

logger = logging.getLogger(__name__)

@dataclass
class ModelProfile:
    model: str
    use_when: str

@dataclass
class BrainRoutingRule:
    brains: list[int]
    parallel: bool
    barrier: list[int]
    model_override: str | None = None
    blocking: bool = False

@dataclass
class MMFlowConfig:
    model_profiles: dict[str, ModelProfile]
    brain_routing: dict[str, BrainRoutingRule]
    verification_gates: dict

class ConfigError(Exception):
    pass

VALID_MODEL_KEYS = {"quality", "balanced", "budget"}
VALID_MOMENTS = {"DISCUSSION", "PLANNING", "EXECUTION_WAVE", "VERIFICATION"}

_DEFAULTS = {
    "model_profiles": {
        "quality":  {"model": "claude-opus-4-6",   "use_when": "critical decisions"},
        "balanced": {"model": "claude-sonnet-4-6", "use_when": "standard brains"},
        "budget":   {"model": "claude-haiku-4-5",  "use_when": "context recovery"},
    },
    "brain_routing": {
        "DISCUSSION":     {"brains": [1,2,3], "parallel": True,  "barrier": [7]},
        "PLANNING":       {"brains": [4,5,6], "parallel": True,  "barrier": [7]},
        "EXECUTION_WAVE": {"brains": [7],     "parallel": False, "barrier": []},
        "VERIFICATION":   {"brains": [7],     "parallel": False, "barrier": [], "blocking": True},
    },
    "verification_gates": {"spec_coverage_threshold": 0.95, "max_gate_retries": 1},
}

def load_config(path: str = ".planning/.mm-flow/config.yml") -> MMFlowConfig:
    """
    Loader de config.yml con fallback a defaults.

    - missing file → usa defaults (no crash, log warning)
    - malformed YAML → raise ConfigError con mensaje descriptivo
    - unknown model key → raise ConfigError
    """
    try:
        with open(path) as f:
            raw = yaml.safe_load(f)
        if raw is None:
            logger.warning(f"config.yml vacío en {path} — usando defaults")
            raw = {}
    except FileNotFoundError:
        logger.warning(f"config.yml no encontrado en {path} — usando defaults")
        raw = {}
    except yaml.YAMLError as e:
        raise ConfigError(f"config.yml malformado en {path}: {e}") from e

    # Merge con defaults
    data = {**_DEFAULTS, **raw}

    # Validar model keys
    profiles_raw = data.get("model_profiles", _DEFAULTS["model_profiles"])
    for key in profiles_raw:
        if key not in VALID_MODEL_KEYS:
            raise ConfigError(f"model_profiles contiene clave desconocida: '{key}'. Válidas: {VALID_MODEL_KEYS}")

    model_profiles = {
        k: ModelProfile(model=v["model"], use_when=v.get("use_when", ""))
        for k, v in profiles_raw.items()
    }

    routing_raw = data.get("brain_routing", _DEFAULTS["brain_routing"])
    brain_routing = {
        moment: BrainRoutingRule(
            brains=v["brains"],
            parallel=v.get("parallel", True),
            barrier=v.get("barrier", []),
            model_override=v.get("model_override"),
            blocking=v.get("blocking", False),
        )
        for moment, v in routing_raw.items()
    }

    return MMFlowConfig(
        model_profiles=model_profiles,
        brain_routing=brain_routing,
        verification_gates=data.get("verification_gates", _DEFAULTS["verification_gates"]),
    )
```

**Tests requeridos** (pytest):
```python
def test_missing_file_uses_defaults():
    config = load_config("/nonexistent/path.yml")
    assert "quality" in config.model_profiles

def test_malformed_yaml_raises_config_error():
    # crear tmp file con YAML inválido
    with pytest.raises(ConfigError, match="malformado"):
        load_config(path_to_bad_yaml)

def test_unknown_model_key_raises_config_error():
    # config con key "premium" (no válida)
    with pytest.raises(ConfigError, match="clave desconocida"):
        load_config(path_to_unknown_key_yaml)
```

---

### FASE 2: Wire the Bridge — CLI ↔ Skills (Día 2)
**Objetivo:** Skills `/mm:` llaman al CLI para registrar estado. CLI deja de ser placeholder.

> **Chicken-and-egg:** FASE 1 Task 1.4 (agent_registry) y Task 1.5 (config loader)
> DEBEN completarse antes de que FASE 2 Task 2.2 pueda cerrar su DoD.

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
    # Guard: mutuamente excluyentes
    if start and complete:
        raise click.UsageError("--start y --complete son mutuamente excluyentes")

    ctx = _load_context()
    sm = StateMachine(ctx["org_id"], ctx["project_id"], ctx["workspace_id"], _db_url())

    if start:
        import asyncio
        execution_id = asyncio.run(sm.record_phase_execution_async(
            phase=phase, status="in_progress",
            state_data={"started_via": "skill"},
            backend_used=ctx.get("backend", "claude")
        ))
        click.echo(f"execution_id:{execution_id}")  # parseable por el skill
        # Actualizar runtime-state.json para mm-flow-statusline.js
        _write_runtime_state(
            phase=phase,
            moment="EXECUTION_WAVE",
            brain=0,
            state="ACTIVE",
            backend=ctx.get("backend", "claude"),
        )

    elif complete:
        import asyncio
        asyncio.run(sm.record_phase_execution_async(
            phase=phase, status="completed",
            state_data={"git_commit": commit, "summary": summary},
            backend_used=ctx.get("backend", "claude"),
            tokens_consumed=tokens
        ))
        # Limpiar runtime-state.json al completar la fase
        _write_runtime_state(
            phase=phase,
            moment="COMPLETED",
            brain=0,
            state="IDLE",
            backend=ctx.get("backend", "claude"),
        )
        click.echo(f"Phase {phase} marked complete")
```

#### Task 2.2: Reemplazar BrainRouter por Dynamic Dispatch Engine

El `brain_router.py` actual usa keywords hardcodeados. Reemplazar por dispatch que lee `config.yml`.

**Tipos Pydantic v2 strict (contrato compartido):**

```python
from pydantic import BaseModel, ConfigDict
from typing import Literal

class BrainDispatch(BaseModel):
    model_config = ConfigDict(strict=True)
    brain_id: int
    role: str
    model_profile: Literal["quality", "balanced", "budget"]
    is_barrier: bool

class DispatchResult(BaseModel):
    model_config = ConfigDict(strict=True)
    moment: Literal["DISCUSSION", "PLANNING", "EXECUTION_WAVE", "VERIFICATION"]
    parallel: list[BrainDispatch]
    barrier: list[BrainDispatch]
    budget_remaining: int       # pre-dispatch check absorbido desde FASE 5 (eliminada)
    execution_id: str

class BudgetExceededError(Exception):
    pass

class DynamicDispatchEngine:
    """Despacha brains según fase+estado leyendo config.yml y agent_registry."""

    def __init__(self, config_path: str = ".planning/.mm-flow/config.yml"):
        from .config_loader import load_config
        self.config = load_config(config_path)

    def dispatch(
        self,
        phase: int,
        moment: Literal["DISCUSSION", "PLANNING", "EXECUTION_WAVE", "VERIFICATION"]
    ) -> DispatchResult:
        routing = self.config.brain_routing[moment]
        brains = self._get_brains_from_registry(routing.brains)
        barrier_brains = self._get_brains_from_registry(routing.barrier)

        budget_remaining = self._check_budget(brains)

        return DispatchResult(
            moment=moment,
            parallel=[b for b in brains if not b.is_barrier],
            barrier=barrier_brains,
            budget_remaining=budget_remaining,
            execution_id=self._new_execution_id(),
        )

    def _check_budget(self, brains: list[BrainDispatch]) -> int:
        """
        Retorna tokens restantes.
        Raises BudgetExceededError si >80% consumido.
        Pre-dispatch budget check absorbido de FASE 5 (eliminada como Build Trap).
        """
        total_consumed = sum(getattr(b, 'tokens_consumed_total', 0) for b in brains)
        total_budget = sum(getattr(b, 'token_budget_per_phase', 10000) for b in brains)
        if total_budget > 0 and total_consumed > total_budget * 0.8:
            raise BudgetExceededError(
                f"Budget al {total_consumed/total_budget:.0%} — requiere aprobación"
            )
        return total_budget - total_consumed
```

**SLI-2 (Brain #7 Barrier Latency) — instrumentación requerida:**
```python
import asyncio
import time

async def call_barrier_with_sli(self, barrier_brains: list[BrainDispatch], outputs: dict) -> dict:
    """
    SLI-2: P95 barrier latency < 20s. Hard limit: 30s.
    Si P95 > 45s → T1 > 300s → plan agent-unprofitable.
    """
    t_start = time.monotonic()
    try:
        result = await asyncio.wait_for(
            self._invoke_barrier(barrier_brains, outputs),
            timeout=30.0  # hard limit: 30s
        )
    except asyncio.TimeoutError:
        logger.warning(
            "Brain #7 barrier timeout (>30s) — continuando en modo degradado. "
            "SLI-2 violado."
        )
        result = {"verdict": "DEGRADED", "timeout": True}
    finally:
        elapsed = time.monotonic() - t_start
        # Loguear en phase_executions.state_data para tracking P95
        self._log_barrier_latency(elapsed)
    return result
```

**Oracle table para SLI-3 (tests):**
```python
DISPATCH_ORACLE = {
    "DISCUSSION":     {"parallel_brains": [1,2,3], "barrier_brains": [7]},
    "PLANNING":       {"parallel_brains": [4,5,6], "barrier_brains": [7]},
    "EXECUTION_WAVE": {"parallel_brains": [7],     "barrier_brains": [], "sequential": True},
    "VERIFICATION":   {"parallel_brains": [7],     "barrier_brains": [], "sequential": True},
}
```

**Contrato compartido con frontend — Zod schema `CostUpdateEvent`:**

El backend envía `CostUpdateEvent` via WebSocket. El frontend DEBE validar con Zod antes de actualizar el store — `data as CostUpdateEvent` es unsafe.

Archivo: `apps/web/src/types/api.ts` (agregar junto a los tipos existentes)

```typescript
import { z } from "zod"

// Schema Zod — validación runtime del WS event (reemplaza "data as CostUpdateEvent")
export const CostUpdateEventSchema = z.object({
  type: z.literal("cost_update"),
  brain_id: z.number().int().min(1).max(7),
  tokens_used: z.number().int().nonneg(),
  tokens_remaining: z.number().int().nonneg(),
  model_profile: z.enum(["quality", "balanced", "budget"]),
  execution_id: z.string().uuid(),
  timestamp: z.string().datetime(),
})

export type CostUpdateEvent = z.infer<typeof CostUpdateEventSchema>
```

En `apps/web/src/stores/wsStore.ts`, reemplazar el unsafe cast:
```typescript
// ANTES (unsafe):
const event = data as CostUpdateEvent

// DESPUÉS (safe):
const parsed = CostUpdateEventSchema.safeParse(data)
if (!parsed.success) {
  console.warn("CostUpdateEvent inválido:", parsed.error)
  return
}
const event = parsed.data
```

> **Nota Brain #4:** Este schema es el contrato compartido. Si `DispatchResult` en Python cambia,
> `CostUpdateEventSchema` debe actualizarse en el mismo PR — son el mismo contrato en dos capas.

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

**Arquitectura split (JS thin dispatcher + Python testeable):**

```
~/.claude/hooks/mm-flow-stop.js     ← thin JS dispatcher (intesteable en CI)
  → detecta write tool calls en transcript
  → llama `python3 ~/.mm-flow/checkpoint_writer.py`

~/.mm-flow/checkpoint_writer.py    ← lógica Python real (testeable en CI)
  → recibe contexto del hook via stdin/args
  → escribe .planning/SESSION-CHECKPOINT.md
  → testeable con pytest sin Claude Code runtime
```

> **Justificación:** hooks en `~/.claude/hooks/` son intesteables en GitHub Actions.
> JavaScript hook = thin dispatcher. Python = lógica real testeable.

**Trigger — write-tool-call detection (NO "cada 10 mensajes"):**

```javascript
// mm-flow-stop.js
// Detectar en data.transcript si en últimos 10 messages hay tool calls de:
//   - Edit, Write, MultiEdit → write operations
//   - Bash con mutación (crear archivo, modificar, etc.)
// Si al menos 1 write operation detectada → disparar checkpoint_writer.py
// Si cero write operations → skip (debugging session, reads only → no trigger)

const recentMessages = data.transcript.slice(-10);
const hasWriteOps = recentMessages.some(msg =>
  msg.tool_calls?.some(tc =>
    ["Edit", "Write", "MultiEdit"].includes(tc.name) ||
    (tc.name === "Bash" && /\b(tee|> |>>\s|\btouch\b|\bmkdir\b)\b/.test(tc.input?.command || ""))
  )
);

if (hasWriteOps) {
  const { execSync } = require("child_process");
  execSync(`python3 ~/.mm-flow/checkpoint_writer.py`, { input: JSON.stringify(data) });
}
```

Agregar a `settings.json`:
```json
"Stop": [{
  "hooks": [{
    "type": "command",
    "command": "node /home/rpadron/.claude/hooks/mm-flow-stop.js"
  }]
}]
```

#### Task 3.2: SessionStart → detectar checkpoints sin guardar
Modificar `mm-flow-session-init.js` para:
1. Leer `.planning/SESSION-CHECKPOINT.md`
2. Si `saved: false` Y timestamp > 48h → inyectar warning:
   ```
   SESION ANTERIOR SIN GUARDAR
   Última actividad: [timestamp]
   Decisiones detectadas: [lista]
   → Llama mem_session_summary ANTES de continuar.
   ```
3. Si `saved: false` Y timestamp < 48h → inyectar warning ligero (no bloqueante)

#### Task 3.3: PostToolUse → write-tool-call detection (NO "cada 10 mensajes")

> `mm-flow-context-monitor.js` YA EXISTE (191 líneas). EXTENDER, no crear.

```
ACCIÓN: En PostToolUse hook (mm-flow-context-monitor.js)
- Escanear data.transcript para write tool calls (Edit/Write/Bash mutation) en últimos 10 mensajes
- Si ≥1 write operation encontrada → inyectar recordatorio de checkpoint
- Si 0 write operations → skip
- Razón: sesiones read-only (debugging, exploración) no necesitan checkpoint reminder
```

Mensaje a inyectar cuando detecta writes:
```
[CHECKPOINT] Detecté cambios en archivos en los últimos intercambios.
¿Hiciste decisiones o descubrimientos importantes?
Si sí → llama mem_save AHORA. Si no → ignorar este mensaje.
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

**Entregable:** Sesión termina con write ops → `SESSION-CHECKPOINT.md` existe con `saved: false`. Próxima sesión → warning visible.

---

### FASE 4: Wire Audit Trail + JWT Auth + Missing Pieces (Día 3-4)
**Objetivo:** Audit trail funcional, JWT auth en rutas, credentials, statusline extendida.

#### Task 4.1: Agregar JWT auth a los 13 endpoints de apps/api/routers/audit.py

> **CONTEXTO:** audit router YA está wired en `apps/api/app.py` line 212 con try/except fallback.
> NO es necesario wired — YA ESTÁ. La tarea real es la seguridad.
>
> **PROBLEMA:** 13 route functions en `audit.py` tienen CERO `Depends(get_current_user_any)`.
> CI reporta verde porque `tests/api/` NO está en el step `level2-tests` de `ci.yml`.
> La señal verde del CI es activamente engañosa — las rutas llegan a producción sin auth.

**IMPLEMENTACIÓN:**
```python
# 1. Agregar a cada una de las 13 route functions:
current_user: User = Depends(get_current_user_any)

# Ejemplo:
@router.get("/projects/{project_id}/summary")
async def get_audit_summary(
    project_id: UUID,
    current_user: User = Depends(get_current_user_any),  # ← AGREGAR
    db: AsyncSession = Depends(get_db),
):
    ...
```

**Tests requeridos:**
```python
# tests/api/test_audit_routes.py — mínimo 26 tests:
# 13 tests: sin token → 401
# 13 tests: con token válido → 200/respuesta correcta

def test_audit_summary_without_token_returns_401(client):
    response = client.get("/api/audit/projects/some-id/summary")
    assert response.status_code == 401

def test_audit_summary_with_valid_token_returns_200(client, auth_headers):
    response = client.get("/api/audit/projects/some-id/summary", headers=auth_headers)
    assert response.status_code == 200
```

**CI gate — agregar a `.github/workflows/ci.yml`:**
```yaml
# Agregar tests/api/ al step level2-tests
- name: level2-tests
  run: |
    cd apps/api
    uv run pytest tests/api/ tests/unit/ -v

# Test de conteo automático en CI:
def test_all_audit_routes_have_auth():
    """Cuenta rutas sin Depends(get_current_user_any) y falla si > 0."""
    import ast, pathlib
    source = pathlib.Path("apps/api/routers/audit.py").read_text()
    tree = ast.parse(source)
    routes_without_auth = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.AsyncFunctionDef, ast.FunctionDef)):
            for decorator in node.decorator_list:
                if isinstance(decorator, ast.Attribute) and decorator.attr in ("get","post","put","delete","patch"):
                    # verificar que tiene Depends(get_current_user_any) en args
                    has_auth = any(
                        "get_current_user_any" in ast.unparse(arg)
                        for arg in node.args.defaults + node.args.kw_defaults
                        if arg is not None
                    )
                    if not has_auth:
                        routes_without_auth.append(node.name)
    assert len(routes_without_auth) == 0, f"Rutas sin auth: {routes_without_auth}"
```

**SLI-5 checkpoint:** `grep -c "get_current_user_any" apps/api/routers/audit.py` → target: 13.

#### Task 4.2: ~~config.yml~~ → MOVIDO a FASE 1 Task 1.5

Esta tarea fue movida a FASE 1 porque DynamicDispatchEngine (FASE 2) depende del loader.
Ver Task 1.5 para implementación completa.

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

#### Task 4.4: EXTENDER mm-flow-statusline.js (NO crear — ya existe)

> `~/.claude/hooks/mm-flow-statusline.js` EXISTE (74 líneas, 2.5K).
> Implementación actual: model | branch | dirname | context bar% con thresholds ANSI.
> **ACCIÓN: EXTENDER, NO reemplazar.**

```
- Preservar líneas 24-43 (context window percentage logic con thresholds 50/65/80%)
- Agregar: phase state, active brain, backend identity

Formato objetivo:
[mm-flow] z.ai 180K/200K ▓▓▓▓▓▓▓▓░░ 90% | Phase 19 PLANNING | Brain #5 [ACTIVE]
```

**Estado del brain — ANSI color + text label (NO emoji — falla en terminales restringidas):**
```javascript
const BRAIN_STATES = {
  ACTIVE:  "\x1b[32m[ACTIVE]\x1b[0m",    // verde
  BARRIER: "\x1b[33m[BARRIER]\x1b[0m",   // ámbar
  IDLE:    "\x1b[2m[IDLE]\x1b[0m",       // dim
  OFFLINE: "\x1b[31m[OFFLINE]\x1b[0m",   // rojo
};
```

**Data source:** `.planning/.mm-flow/runtime-state.json` (escrito por CLI en --start/--complete).
**NO consultar DB** — latencia inaceptable en cada respuesta (200-500ms por query).

**runtime-state.json schema:**
```json
{
  "current_phase": 19,
  "current_moment": "PLANNING",
  "active_brain": 5,
  "brain_state": "ACTIVE",
  "backend": "z.ai",
  "updated_at": "ISO timestamp"
}
```

CLI debe escribir runtime-state.json en `--start` y `--complete`:
```python
import json
from pathlib import Path

def _write_runtime_state(phase: int, moment: str, brain: int, state: str, backend: str):
    """Escribe runtime-state.json para mm-flow-statusline.js."""
    runtime_state = {
        "current_phase": phase,
        "current_moment": moment,
        "active_brain": brain,
        "brain_state": state,
        "backend": backend,
        "updated_at": datetime.now().isoformat(),
    }
    Path(".planning/.mm-flow/runtime-state.json").write_text(json.dumps(runtime_state, indent=2))
```

---

## Orden de Ejecución

```
FASE 1 (bloqueante para todo)
  ├── 1.2: Audit trail schema (SQL)
  ├── 1.3: Verificar seed data
  ├── 1.4: Agent Registry tabla + seed 7 brains [UNIQUE(org,project,brain)]
  └── 1.5: config.yml loader + config.yml [NUEVO — BLOQUEA FASE 2 Task 2.2]

FASE 2 (depende de FASE 1 completa — chicken-and-egg)
  ├── 2.1: CLI lifecycle flags --start/--complete [asyncio.run + mutex guard]
  ├── 2.2: DynamicDispatchEngine [DispatchResult Pydantic v2 strict + pre-dispatch budget + SLI-2]
  └── 2.3: Skills wired con CLI bookends

FASE 3 (independiente — puede ir en paralelo con FASE 2)
  ├── 3.1: Stop hook mm-flow-stop.js [thin JS + Python checkpoint_writer.py]
  ├── 3.2: SessionStart → stale checkpoint detection (>48h warning)
  ├── 3.3: write-tool-call detection [NO "cada 10 mensajes"]
  └── 3.4: context_loader flow fix

FASE 4 (depende de FASE 1 para audit trail)
  ├── 4.1: JWT auth en 13 rutas audit.py [REEMPLAZA "wire router"] + 26 tests + CI gate
  ├── 4.2: ~~config.yml~~ → MOVIDO a FASE 1 Task 1.5
  ├── 4.3: backends.sh
  └── 4.4: EXTENDER mm-flow-statusline.js [NO crear — ya existe]

FASE 5 — CORTADA (Build Trap detectado por Brain #1/#7)
  - Budget tracking: absorbido en FASE 2 Task 2.2
  - Heartbeat: brains no son procesos independientes
  - Sub-fases decimales: no reduce T1
  - Plugin SDK: canal externo no planificado
```

---

## Definition of Done

| Criterio | Verificación |
|---------|-------------|
| Audit trail tables creadas | `SELECT table_name FROM information_schema.tables WHERE table_name IN ('phase_executions','decisions','audit_log');` |
| Agent Registry 7 brains por proyecto | `SELECT count(*) FROM agent_registry WHERE project_id = (SELECT id FROM projects WHERE slug = 'mastermind')` → 7 |
| UNIQUE constraint correcto | `INSERT` mismo brain dos veces → segundo falla con `unique violation` |
| config.yml loader no crashea con missing file | `pytest test_config_loader.py::test_missing_file_uses_defaults` → PASS |
| mm-flow status sin errores | `mm-flow status` |
| `/mm:execute-phase 19` registra en DB | `SELECT * FROM phase_executions WHERE phase = 19;` |
| DispatchResult es Pydantic v2 strict | `isinstance(result, DispatchResult)` → True |
| Brain dispatch lee config.yml | `mm-flow dispatch --phase 19 --moment PLANNING` → brains 4,5,6 + barrier 7 |
| Sesión termina → checkpoint creado | `ls .planning/SESSION-CHECKPOINT.md` |
| Próxima sesión detecta checkpoint | Abrir sesión → ver warning |
| 13 rutas audit.py con JWT | `grep -c "get_current_user_any" apps/api/routers/audit.py` → 13 |
| tests/api/ en CI | `grep "tests/api" .github/workflows/ci.yml` → existe |
| Statusline extendida (no reemplazada) | `git diff ~/.claude/hooks/mm-flow-statusline.js` → solo adiciones a líneas 24-43+ |
| runtime-state.json existe | `ls .planning/.mm-flow/runtime-state.json` |
| Seed idempotente | Correr seed dos veces → COUNT=7 por proyecto (no 14) |

---

## Estimación

| Fase | Duración | Complejidad |
|------|----------|-------------|
| FASE 1: Infrastructure | 2-3h | Media (SQL + seed + config loader con tests) |
| FASE 2: CLI ↔ Skills bridge | 3-4h | Media |
| FASE 3: Context persistence | 2-3h | Media (hooks + Python extractor) |
| FASE 4: JWT Auth + extras | 3-4h | Media-Alta (13 rutas + 26 tests + CI) |
| **TOTAL** | **~10-14h** | — |

> **Ahorro vs v2:** ~3h por eliminar FASE 5 (Build Trap). Total reducido de 12-15h a 10-14h.

---

## Archivos a Crear/Modificar

### Crear (nuevos)
- `~/.claude/hooks/mm-flow-stop.js` — Stop hook thin dispatcher
- `~/.mm-flow/checkpoint_writer.py` — Lógica Python testeable del checkpoint
- `~/.claude/backends.sh` — Credentials loader
- `.planning/.mm-flow/config.yml` — Brain routing + model profiles
- `.planning/.mm-flow/config_loader.py` — Loader con fallback + ConfigError
- `.planning/.mm-flow/dispatch_engine.py` — Dynamic Dispatch Engine (reemplaza brain_router)
- `.planning/.mm-flow/runtime-state.json` — Estado runtime para statusline (generado por CLI)
- `apps/api/tests/api/test_audit_routes.py` — 26 tests JWT auth

### Modificar (existentes)
- `.planning/.mm-flow/cli/commands.py` — `--start`/`--complete` flags con asyncio.run + mutex + runtime-state write
- `.planning/.mm-flow/brain_router.py` — Deprecar, redirigir a dispatch_engine.py
- `~/.claude/hooks/mm-flow-session-init.js` — Detectar checkpoints sin guardar
- `~/.claude/hooks/mm-flow-context-monitor.js` — write-tool-call detection (no cada 10 msgs)
- `~/.claude/hooks/mm-flow-statusline.js` — EXTENDER (preservar líneas 24-43)
- `~/.claude/settings.json` — Stop hook
- `apps/api/routers/audit.py` — 13 Depends(get_current_user_any)
- `.github/workflows/ci.yml` — Agregar tests/api/ al step level2-tests
- `.claude/skills/mm/execute-phase/SKILL.md` — CLI bookends
- `.claude/skills/mm/plan-phase/SKILL.md` — Engram nativo + CLI bookend

### Ejecutar (SQL, no código)
- `docker/postgres/mm-flow-audit.sql` — Audit trail tables
- SQL inline para `agent_registry` table + seed 7 brains con `DO $$ ... ON CONFLICT DO NOTHING`

---

**v3 — Actualizado:** 2026-04-14 (correcciones brain council 7 agentes)
**Próximo paso:** FASE 1 — aplicar audit trail SQL + crear agent_registry + config.yml loader
