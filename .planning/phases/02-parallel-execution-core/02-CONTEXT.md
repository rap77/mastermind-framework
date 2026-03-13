# Phase 2: Parallel Execution Core - Context

**Gathered:** 2026-03-13
**Status:** Ready for planning

## Phase Boundary

Dependency-aware parallel brain execution with centralized task state tracking and graceful cancellation. This phase enables multiple brains to run simultaneously when independent, while respecting dependency constraints. Includes SQLite-based task state persistence and resource scheduling to avoid API rate limits.

**Out of scope:**
- Distributed task queues (Celery/RQ) — single-host asyncio only
- Multi-machine orchestration — deferred to v3.0+
- Auto-scaling infrastructure — single-tenant deployment
- Real-time collaborative editing — separate phase

**Requirements mapeados:** PAR-01 a PAR-09, PERF-01 (10 requirements)

## Implementation Decisions

### Dependency Resolution (Grafo DAG)

**Estrategia: Topological Sort Validation con `@model_validator`**

- Validación **estática** en tiempo de carga del YAML — flows.yaml con ciclos ni siquiera se instancian
- Algoritmo de **Kahn** o **DFS** integrado directamente en `model_validator` de Pydantic v2
- **Fast-fail early**: si hay un ciclo, se lanza `ValidationError` inmediato antes de gastar tokens de IA
- Output del validador: lista ordenada de brains para ejecución en orden topológico
- **Zero dependencies**: no usar networkx o librerías de ciencia de datos

**Ejemplo de implementación:**
```python
class FlowConfig(BaseModel):
    nodes: Dict[str, List[str]]  # brain_id -> lista de dependencias

    @model_validator(mode='after')
    def validate_dag(self) -> 'FlowConfig':
        # DFS para detectar ciclos
        visited = set()
        path = set()

        def visit(node):
            if node in path:
                raise ValueError(f"Ciclo detectado: {node}")
            if node not in visited:
                path.add(node)
                for dep in self.nodes.get(node, []):
                    visit(dep)
                path.remove(node)
                visited.add(node)

        for node in self.nodes:
            visit(node)
        return self
```

### Cancellation Semantics

**Estrategia: Cooperative Cancellation con Grace Period**

- **5 segundos de grace period** — brains in-flight tienen tiempo para guardar checkpoint en SQLite
- `asyncio.Event` o `CancellationToken` para propagar señal de cancelación
- Usuario pulsa Ctrl+C → Coordinator envía señal a todos los brains activos
- **Timeout**: después de 5 segundos, hard kill (fuerza bruta)
- Razón técnica: evitar transacciones corruptas en SQLite — COMMIT y cierre seguro de conexión

**Flujo:**
1. Usuario cancela → `coordinator.cancel()` se llama
2. Señal propagada a brains in-flight via `asyncio.Event`
3. Brain tiene 5s para llamar `_save_checkpoint()` y marcar `status='cancelled'`
4. Timeout → hard kill, marca `status='killed'`

### State Persistence

**Estrategia: Checkpoint-based (Atomic Transactions)**

- **Solo en transitions**: `running→completed`, `running→failed`, `running→cancelled`
- Una sola transacción atómica por brain
- `model_dump_json()` de Pydantic v2 → convertir resultado a string JSON
- Guardar en columna `result` de tabla SQLite `tasks`
- **No updates periódicos** — evitar `database is locked` con 23 brains escribiendo concurrentemente

**Recuperación de crash:**
- Si sistema se apaga → leer tabla `tasks`
- Brains en `status='completed'` → no re-ejecutar
- Brains en `status='running'` → asumir `failed` o `stale`, reiniciar si es necesario
- Brains en `status='pending'` → ejecutar

**Esquema SQLite:**
```sql
CREATE TABLE tasks (
    id TEXT PRIMARY KEY,
    brain_id TEXT NOT NULL,
    status TEXT NOT NULL,  -- pending, running, completed, failed, cancelled, killed
    progress TEXT,         -- JSON con progreso parcial
    result TEXT,           -- JSON con resultado final (model_dump_json)
    error TEXT,            -- Mensaje de error si falló
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);
```

### Error Handling (Propagación)

**Estrategia: Retry with Circuit Breaker + Blast Radius Controlado**

- **3 reintentos** con exponential backoff (1s, 2s, 4s) + jitter
- Si reintentos fallan → **Circuit Breaker** se abre
- **Blast radius controlado**: solo se cancelan dependientes directos del brain fallido
- Brains en ramas paralelas (independientes) siguen ejecutándose normalmente
- Reporte final: árbol de ejecución con nodos verdes (éxito) y rojos (fallo)

**Flujo:**
1. Brain A falla → coordinator detecta excepción
2. Reintentar 3 veces con backoff + jitter (evitar thundering herd)
3. Si sigue fallando → marcar `status='failed'`, abrir circuit breaker
4. **Poda del grafo**: brains que dependen de A pasan a `status='skipped'`
5. Brains independientes de A → continúan normalmente
6. UX final: "18 exitosos, 1 fallido, 4 cancelados por dependencias"

**Razón**: brains muy diversos (Marketing, Estrategia, etc.) — fallo en uno no debe detener análisis independiente

### Resource Scheduling & Rate Limiting

**Estrategia: Per-API Semaphores + Exponential Backoff (2 capas)**

**Capa 1: Preventiva (Per-API Semaphores)**
- `asyncio.Semaphore` por proveedor de API
- Configuración en `providers.yaml`:
  ```yaml
  providers:
    - name: notebooklm
      max_concurrent_calls: 2  # NotebookLM es restrictivo
    - name: claude
      max_concurrent_calls: 10 # Claude API tolera más
  ```
- Integración con Pydantic v2: `ProviderConfig` model carga `max_concurrent_calls`
- Coordinator crea semaphores: `semaphores = {p.name: asyncio.Semaphore(p.max_concurrent_calls) for p in config.providers}`

**Capa 2: Seguridad (Exponential Backoff with Jitter)**
- Si brain recibe `429 Too Many Requests` → no falla inmediatamente
- Espera exponencial: 1s, 2s, 4s, 8s... + jitter aleatorio (±20%)
- Jitter evita que todos los brains reintenten al mismo tiempo
- Middleware de reintentos en MCP wrapper

**Razón**: NotebookLM (MCP experimental) es más restrictivo que Claude API — semaphores per-API optimizan cada canal sin riesgo

### Claude's Discretion

- Valor exacto de `max_concurrent_calls` por proveedor (default: NotebookLM=2, Claude=10)
- Algoritmo de backoff (exponential vs linear)
- Cantidad de jitter (±20% es razonable, pero puede ajustarse)
- Política de Circuit Breaker (qué tan rápido se abre/cierra)

## Specific Ideas

- "Quiero evitar que un parpadeo en la conexión de red arruine un flujo de trabajo de 10 minutos" → Retry with Circuit Breaker
- "Si el brain de posts para redes sociales falla, no hay razón para detener el análisis financiero" → Blast radius controlado
- "5 segundos son suficientes para COMMIT seguro en SQLite" → Grace period basado en atomicidad de transacciones

## Existing Code Insights

### Reusable Assets

- **Pydantic v2 models** (Phase 1): `CoordinatorRequest`, `CoordinatorResponse`, `MCPRequest`, `MCPResponse` — ya tipados
- **`mastermind_cli/types/coordinator.py`**: modelos de datos para orquestación — extender con `FlowConfig` DAG model
- **`mastermind_cli/orchestrator/coordinator.py`**: orquestador secuencial existente — refactorizar para soportar paralelismo
- **Type-safe MCP wrapper** (Phase 1, Plan 03): `TypeSafeMCPWrapper` con runtime validation — reutilizar para reintentos con backoff

### Established Patterns

- **Async/await pattern**: todo el código usa asyncio — fácil migración a `asyncio.TaskGroup`
- **YAML configs**: `flows.yaml`, `brains.yaml`, `thresholds.yaml` ya existen — agregar `providers.yaml` para rate limiting
- **Click CLI**: comandos `mm orchestrate` ya existen — mantener compatibilidad CLI

### Integration Points

- **`mastermind_cli/orchestrator/coordinator.py`**: agregar `_execute_parallel()` método usando `asyncio.TaskGroup`
- **`mastermind_cli/commands/orchestrate.py`**: agregar flags `--parallel`, `--dry-run` para testing
- **SQLite database**: nuevo archivo `mastermind_cli/state/db.py` para task state store
- **Providers config**: nuevo archivo `mastermind_cli/config/providers.yaml` para rate limits

## Deferred Ideas

None — discussion stayed within phase scope.

---

*Phase: 02-parallel-execution-core*
*Context gathered: 2026-03-13*
