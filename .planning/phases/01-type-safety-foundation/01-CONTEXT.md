# Phase 1: Type Safety Foundation - Context

**Gathered:** 2026-03-13
**Status:** Ready for planning

## Phase Boundary

Infraestructura de type-safety para MasterMind Framework v2.0 — crear modelos Pydantic v2 para todas las estructuras de datos, habilitar mypy --strict mode, y establecer validación runtime. Este trabajo es interno del desarrollador, no visible para el usuario final.

**Out of scope:**
- Modificar el comportamiento de los 23 brains existentes
- Cambiar la funcionalidad de CLI commands
- Alterar el formato de archivos de configuración YAML

**Requirements mapeados:** TS-01 a TS-07 (7 requirements)

## Implementation Decisions

### Estrategia Pydantic v2

**Migración:**
- Big-bang migration con Test-First para core modules + Feature-based para periphery
- **Orden:** Escribir tests primero para core (coordinator.py, mcp_wrapper.py), luego migrar feature-vertical slices
- **Herramienta:** `bump-pydantic` CLI tool para automatizar migración v1→v2
- **Safety net:** pydantic.v1 shim durante migración híbrida (periphery → core)

**MCP responses (NotebookLM):**
- Enfoque evolutivo con `model_config = ConfigDict(extra='allow')` de Pydantic v2
- Campos conocidos validados estrictamente, campos extra preservados automáticamente
- Ventaja: Más limpio que campo `raw` manual, self-documenting

**Brain outputs legacy:**
- Normalizer pattern con fallbacks inteligentes
- `normalize_brain_output(raw_yaml: str) -> StandardSchema`
- Try-except global: YAML parse error → fallback a `{"raw_text": raw_yaml}`
- `StandardSchema` rellena huecos: `id`, `content`, `version` (legacy vs nuevo)

**YAML configs (brains.yaml, flows.yaml, thresholds.yaml):**
- **Discriminated Unions** con `Field(discriminator="type")`
- `Annotated[Union[SearchBrain, OpenAIBrain], Field(discriminator="type")]`
- Ideal para 23 brains heterogéneos con parámetros diferentes
- Ejemplo: brain type "vector-search" requiere `top_k`, type "generative" requiere `temperature`

**JSON schemas externos:**
- **SchemaExporter** con `model_json_schema()` dinámico
- Registro centralizado de modelos → `/schemas/{category}` endpoint
- `Field(description="...", examples=[...])` → exportado directamente a JSON Schema
- Código = documentación técnica para terceros (self-documenting)

### Alcance mypy strict

**Estrategia de habilitación:**
- **Tiered Enforcement** — niveles de severidad graduales
- Fase 1: `disallow_untyped_defs` (firmas tipadas)
- Fase 2: `no_implicit_optional`, `warn_return_any` (cuerpos de funciones)
- Fase 3: `warn_unused_ignores` (limpieza de ignores)

**Configuración por módulo:**
```toml
[[tool.mypy.overrides]]
module = "mastermind_cli.orchestrator.*"
strict = true

[[tool.mypy.overrides]]
module = "mastermind_cli.brains_legacy.*"
strict = false
```

**Política de `# type: ignore`:**
- **Semantic Scoping** — códigos de error específicos obligatorios
- Mal: `# type: ignore`
- Bien: `# type: ignore[union-attr] # Brain legacy retorna Union[dict, str]`
- **Clean as you touch:** Si editas una función con ignore, intentar resolverlo
- **Config:** `show_error_codes = true`, `warn_unused_ignores = true`

**TypedDict vs Pydantic:**
- **TypedDict como Legacy Bridge** para datos solo lectura de sistemas no controlados
- Outputs de 23 brains legacy → TypedDict (no muta datos originales)
- Comunicación interna (coordinator ↔ mcp_wrapper) → Pydantic models
- **Unpacking pattern:** `BrainModel(**brain_data)` para validación bajo demanda

**Plugin:**
- `pydantic.mypy` instalado para validar constructores v2 correctamente
- Esencial: Pydantic v2 depende de este plugin para type checking preciso

### Validación Runtime

**Dónde validar:**
- **Integrity Checkpoints** — validación en puntos de transformación de datos
- **Boundaries:** CLI input, MCP responses, brain outputs
- **Core logic:** `@validate_call` decorator de Pydantic v2 en funciones críticas del coordinator
- **Internal code:** Confía en tipos (sin validación redundante)

**Ejemplo `@validate_call`:**
```python
from pydantic import validate_call

@validate_call
def process_brain_evaluation(brain_id: str, score: float):
    # Pydantic valida tipos en runtime cada llamada
    # "0.8" → float (coerce), "alto" → ValidationError
    pass
```

**Manejo de ValidationError:**
- **Graceful Degradation** por módulo:
  - **Auth:** Fail-fast (seguridad crítica)
  - **Brains:** Fallback a valores seguros por defecto + marcar como "Degraded/Unverified"
  - **CLI:** Strict + Recovery (mensajes diferenciados por severidad)

**Ejemplo Catch & Fallback:**
```python
try:
    config = BrainConfig(**raw_yaml)
except ValidationError as e:
    logger.error(f"Error en brain {raw_yaml.get('id')}: {e.json()}")
    config = BrainConfig.get_default_safe_config()  # Fallback seguro
```

**Mensajes de error:**
- **Contextual Diagnostics** (estilo compilador Rust) para configs
- Mostrar extracto del archivo con flecha apuntando a línea + sugerencia de corrección
- **Hybrid verbose mode:** `--verbose` muestra JSON technical, default muestra human-readable
- **Implementación:** Iterar `e.errors()` + rich/click para formateo amigable

### CLI Boundary Types

**Click integration:**
- **Pydantic-to-Click Bridge** con generación dinámica de `@click.option`
- Leer modelos Pydantic → auto-generar CLI params
- Single source of truth: modelo Pydantic define nombre, tipo, default, help
- **Librerías:** typer (Click + Pydantic) o pydantic-cli
- **TypeAdapter validation:**
```python
class PydanticParam(click.ParamType):
    def __init__(self, model):
        self.adapter = TypeAdapter(model)

    def convert(self, value, param, ctx):
        try:
            return self.adapter.validate_python(value)
        except ValidationError as e:
            self.fail(f"Error: {e.errors()[0]['msg']}", param, ctx)
```

**Coordinator API:**
- **Entry point:** Typed methods (mejor para AI codegen tools)
  - `orchestrate(brief: BriefModel, flow: FlowModel) -> ResultModel`
- **Brain consumption:** Protocol-based Interface
  - `@runtime_checkable class Validatable(Protocol)`
  - Máxima flexibilidad, desacoplamiento de Pydantic
  - Brains legacy pueden ser clases planas, TypedDict, o BaseModel

**Brain outputs dinámicos:**
- **Self-Describing Metadata** + Factory Pattern + Generic Wrapper
- Cada brain retorna manifiesto: `brain_id`, `version`, `schema`
- Factory lee manifiesto → selecciona Pydantic model correcto
- **Generic wrapper:**
```python
T = TypeVar("T", bound=BaseModel)

class BrainResponse(BaseModel, Generic[T]):
    brain_id: str
    version: str
    content: T  # Tipado según genérico

def parse_output(raw_data: dict) -> BrainResponse[Any]:
    schema = registry.get_schema(raw_data["brain_id"], raw_data["version"])
    return BrainResponse(
        brain_id=raw_data["brain_id"],
        version=raw_data["version"],
        content=schema(**raw_data["content"])
    )
```

### Testing Strategy (Bonus)

**Type testing:**
- **Integration Snapshots** con `pytest-regressions` para 23 brains
  - `data_regression.check(parsed_model.model_dump())`
  - Detecta breaking changes silenciosos
  - Sube coverage 30%→50% rápidamente
- **mypy test suite** para Coordinator generics/protocols
- **Hypothesis** (property-based) para edge cases en Core/Auth
  - Probar con strings vacíos, Unicode extraño, números gigantes

**MCP responses testing:**
- **Contract Proxy** + VCR Dual Mode
  - Contract: Esquemas JSON generados con `model_json_schema()`
  - VCR: `--record-mode=once` para actualizar cassettes localmente
  - CI: Cassettes deterministas (no llamadas reales a MCP)
  - Tests validan robustez del Validation Layer, no contenido semántico

**Coverage goals:**
- **Logic-Path Coverage** > line percentage
- 100% de rutas críticas: success + known errors (ValidationError, MCP connection fail)
- **Coverage diferenciado:**
  - Brains legacy: 50% (snapshots + pragmatic)
  - Coordinator/2FA: 80%+ (critical system paths)

## Specific Ideas

**Principios arquitectónicos:**
- "Evolutivo, no revolucionario" — cada decisión permite migración gradual
- "The show must go on" — Graceful Degradation antes de fallar
- "Código = documentación" — `model_json_schema()`, Field descriptions, Type hints

**Referencias técnicas:**
- Pydantic v2 `ConfigDict(extra='allow')` para MCP responses evolutivos
- `bump-pydantic` CLI tool para migración automatizada
- `typer` library (Click + Pydantic integration)
- `pytest-regressions` para snapshot testing
- `pytest-recording` para VCR cassettes

## Existing Code Insights

### Reusable Assets

**Pydantic models existentes:**
- `mastermind_cli/memory/models.py` → `EvaluationEntry`, `Issue`, `EvaluationScore`, `EvaluationVerdict`
- **Nota:** Usan Pydantic v1 — será migrado a v2 en Phase 1
- **Patrón a seguir:** Field descriptions, Enum classes, validation logic

**Type hints existentes:**
- `coordinator.py`: `Optional[Dict]`, `Dict[str, Any]` — no estricto
- Necesita migración a tipos específicos: `Dict[str, BrainOutput]`

**Testing infrastructure:**
- `pytest` configurado, coverage al 30%
- E2E tests existentes en `tests/test-briefs/`
- **Patrón a extender:** snapshots para brain outputs

### Established Patterns

**Error handling:**
- CLI: `click.echo("Error: ...", err=True)` + `raise click.Abort()`
- Orchestrator: `{"status": "error", "error": "message"}` return dict
- **Patrón a mejorar:** ValidationError → rich-formatted context diagnostics

**Configuration:**
- YAML parsing con `pyyaml.safe_load()`
- **Patrón a reemplazar:** YAML → Discriminated Unions Pydantic models

### Integration Points

**MCP integration:**
- `mastermind_cli/orchestrator/mcp_integration.py` — NotebookLM client
- `mastermind_cli/orchestrator/mcp_wrapper.py` — Bridge Python ↔ MCP tools
- **Integración target:** Type-safe MCP wrapper con Pydantic validation

**CLI entry point:**
- `mastermind_cli/commands/orchestrate.py` — Click command
- **Integración target:** Pydantic-to-Click Bridge para params validados

**Coordinator:**
- `mastermind_cli/orchestrator/coordinator.py` — Main orchestration logic
- **Integración target:** Typed methods + Protocol-based brain consumption

## Deferred Ideas

**Out of scope para Phase 1:**
- Implementar Web UI (Phase 3)
- Parallel execution de brains (Phase 2)
- ML-based optimization (v3.0+)
- Full RAG vector DB (v3.0+)

**Noted para roadmap backlog:**
- Hot-reload de brains sin reiniciar
- Type-aware auto-completion en Web UI (Monaco editor)
- Custom metrics dashboard (success rate, brain usage charts)

## Claude's Discretion

**Areas donde Claude tiene flexibilidad:**
- Orden exacto de flags de mypy en Tiered Enforcement
- Nombres específicos de campos en modelos Pydantic (si siguen convenciones)
- Cantidad de snapshots tests vs unit tests para alcanzar coverage goals
- Formato exacto de mensajes de error human-readable (si contienen información necesaria)

**Principios rectores:**
- Preferir type safety sobre conveniencia a corto plazo
- Mantener backward compatibility con 23 brains existentes
- Priorizar calidad sobre velocidad en core modules (Coordinator, Auth)
- Ser pragmático con legacy code (brains)

---

*Phase: 01-type-safety-foundation*
*Context gathered: 2026-03-13*
