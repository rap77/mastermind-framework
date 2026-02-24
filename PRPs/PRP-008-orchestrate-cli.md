# PRP-008: CLI `mm orchestrate` Implementation

**Status:** In Progress
**Priority:** High
**Estimated:** 2-3 hours
**Dependencies:** PRP-003 (System Prompts), PRP-004 (NotebookLM), PRP-005 (Brain #7), PRP-006 (Orchestrator)

---

## Overview

Implementar el comando **`mm orchestrate`** para automatizar el flujo del Orquestador Central desde la línea de comandos.

---

## Objectives

### Primary
1. **Comando `mm orchestrate <brief>`** — Ejecutar orquestador con brief
2. **Flow detection automático** — Clasificar brief y seleccionar flujo
3. **Execution plan generation** — Crear plan de tareas en YAML
4. **Integration con NotebookLM MCP** — Consultar Cerebro #1 automáticamente
5. **Output delivery** — Entregar resultado consolidado al usuario

### Secondary
6. **`mm orchestrate --file <brief.md>`** — Leer brief desde archivo
7. **`mm orchestrate --flow <flow>`** — Forzar flujo específico
8. **`mm orchestrate --dry-run`** — Generar plan sin ejecutar
9. **`mm orchestrate --continue <plan-id>`** — Continuar ejecución pausada

---

## Implementation Plan

### Phase 1: CLI Command Structure (30 min)

#### 1.1 Nueva estructura de comandos

```python
# tools/mastermind-cli/mastermind_cli/commands/orchestrate.py

@orchestrate.command()
@click.argument('brief', required=False)
@click.option('--file', '-f', type=click.Path(exists=True), help='Read brief from file')
@click.option('--flow', type=click.Choice(['full_product', 'validation_only', 'design_sprint', 'build_feature', 'optimization', 'technical_review']), help='Force specific flow')
@click.option('--dry-run', is_flag=True, help='Generate plan without executing')
@click.option('--continue', 'continue_plan', type=str, help='Continue from existing plan')
@click.option('--output', '-o', type=click.Path(), help='Save output to file')
def orchestrate(brief, file, flow, dry_run, continue_plan, output):
    """Orchestrate brains to process user brief."""
    # Implementation
```

### Phase 2: Flow Detection Logic (30 min)

```python
# tools/mastermind-cli/mastermind_cli/orchestrator/flow_detector.py

class FlowDetector:
    """Detects which flow to use based on brief content."""

    FLOW_TRIGGERS = {
        'full_product': [
            'nuevo proyecto', 'app completa', 'producto desde cero',
            'startup', 'crear una app', 'nuevo producto'
        ],
        'validation_only': [
            'validar idea', 'es buena idea', 'viabilidad',
            'feedback concepto', 'market fit'
        ],
        'design_sprint': [
            'diseñar', 'prototipar', 'wireframe', 'mockup',
            'design sprint', 'diseño de interfaz'
        ],
        'build_feature': [
            'implementar', 'construir', 'codificar', 'feature',
            'desarrollar', 'programar'
        ],
        'optimization': [
            'optimizar', 'mejorar', 'crecimiento', 'métricas',
            'performance', 'retención'
        ],
        'technical_review': [
            'auditoría técnica', 'revisión de código', 'qa',
            'seguridad', 'refactor'
        ]
    }

    def detect(self, brief: str) -> str:
        """Detect flow from brief text."""
        # Count matches for each flow
        # Return flow with highest match count
```

### Phase 3: Execution Plan Generator (30 min)

```python
# tools/mastermind-cli/mastermind_cli/orchestrator/plan_generator.py

class PlanGenerator:
    """Generates execution plans from briefs."""

    def generate(self, brief: str, flow_type: str) -> dict:
        """Generate execution plan."""
        return {
            'plan_id': self._generate_id(),
            'date': datetime.now().isoformat(),
            'flow_type': flow_type,
            'brief': {
                'original': brief,
                'clarified': self._clarify(brief)
            },
            'tasks': self._generate_tasks(flow_type, brief),
            'summary': {
                'total_tasks': len(tasks),
                'estimated_duration': self._estimate_duration(tasks)
            }
        }
```

### Phase 4: NotebookLM Integration (45 min)

```python
# tools/mastermind-cli/mastermind_cli/orchestrator/brain_executor.py

class BrainExecutor:
    """Executes brain tasks via NotebookLM MCP."""

    def execute_brain_1(self, task: dict) -> dict:
        """Execute Product Strategy brain via NotebookLM."""
        # Load system prompt
        # Construct query from task
        # Call NotebookLM via MCP
        # Parse response
        # Return output

    def evaluate_via_brain_7(self, output: dict, task: dict) -> dict:
        """Evaluate output via Brain #7."""
        # Load evaluator skill
        # Apply evaluation matrix
        # Return veredict
```

### Phase 5: Output Formatter (30 min)

```python
# tools/mastermind-cli/mastermind_cli/orchestrator/output_formatter.py

class OutputFormatter:
    """Formats orchestrator outputs for human consumption."""

    def format_execution_plan(self, plan: dict) -> str:
        """Format execution plan for display."""

    def format_evaluation_result(self, result: dict) -> str:
        """Format evaluation result for display."""

    def format_final_deliverable(self, report: dict) -> str:
        """Format final deliverable for display."""
```

### Phase 6: Main Orchestration Loop (45 min)

```python
# tools/mastermind-cli/mastermind_cli/orchestrator/coordinator.py

class Coordinator:
    """Main orchestration coordinator."""

    def orchestrate(self, brief: str, flow=None, dry_run=False):
        """Main orchestration entry point."""
        # 1. Detect or validate flow
        # 2. Generate execution plan
        # 3. If dry_run: print plan and exit
        # 4. For each task:
        #    a. Execute brain
        #    b. Evaluate via #7
        #    c. Handle veredict
        #    d. Track rejections
        # 5. Deliver final result
```

---

## Files to Create/Modify

| Archivo | Acción | Purpose |
|---------|--------|---------|
| `mastermind_cli/commands/orchestrate.py` | Create | CLI command |
| `mastermind_cli/orchestrator/__init__.py` | Create | Package |
| `mastermind_cli/orchestrator/flow_detector.py` | Create | Flow detection |
| `mastermind_cli/orchestrator/plan_generator.py` | Create | Plan generation |
| `mastermind_cli/orchestrator/brain_executor.py` | Create | Brain execution via MCP |
| `mastermind_cli/orchestrator/output_formatter.py` | Create | Output formatting |
| `mastermind_cli/orchestrator/coordinator.py` | Create | Main coordination |
| `mastermind_cli/commands/__init__.py` | Modify | Register orchestrate command |

---

## Success Criteria

- [ ] `mm orchestrate "quiero crear una app"` funciona
- [ ] Detecta flujo correctamente
- [ ] Genera execution plan en YAML
- [ ] Integra con NotebookLM MCP para Cerebro #1
- [ ] Evalúa vía Cerebro #7
- [ ] Entrega resultado formateado
- [ ] `--dry-run` genera plan sin ejecutar
- [ ] `--file` lee brief desde archivo
- [ ] `--flow` forza flujo específico

---

## Out of Scope (Future PRPs)

- Implementación de cerebros 2-6 (sus propios PRPs)
- Persistencia de estado (checkpoint/resume)
- Dashboard web de ejecución
- Multi-brief processing
- Batch processing

---

## Examples

### Example 1: Basic usage

```bash
$ mm orchestrate "quiero crear una app para encontrar compañeros de viaje"

# Flow detected: full_product
# Generating execution plan...
# Plan ID: PLAN-2026-02-24-001
# Tasks: 7
#
# TASK-001: Product Strategy
# → Executing Brain #1 via NotebookLM...
# → Output received
# → Evaluating via Brain #7...
# → Veredict: CONDITIONAL (score: 72)
# → Applying notes, continuing...
#
# [Final deliverable displayed]
```

### Example 2: Dry run

```bash
$ mm orchestrate --dry-run "validar idea de app de viajes"

# Flow detected: validation_only
#
# Execution Plan:
# Plan ID: PLAN-DRY-001
# Flow: validation_only
# Tasks: 2
#
# TASK-001:
#   Brain: Product Strategy
#   Title: "Validar idea de app de viajes"
#   Priority: 10
#
# TASK-002:
#   Brain: Growth & Data (Evaluator)
#   Title: "Evaluar viabilidad"
#   Priority: 10
#
# Estimated duration: 45 min
#
# Dry run complete. Use `mm orchestrate` without --dry-run to execute.
```

### Example 3: Force flow

```bash
$ mm orchestrate --flow validation_only "mi app idea"

# Flow: validation_only (forced)
# [Executes with validation_only flow]
```

### Example 4: From file

```bash
$ cat brief.md
Quiero crear una marketplace freelance
para desarrolladores latinoamericanos.

$ mm orchestrate --file brief.md

# Reading brief from brief.md...
# [Executes orchestration]
```

---

## Notes

- Para PRP-008, solo implementaremos `validation_only` flow completamente
- Los otros flows funcionarán pero fallarán en cerebros 2-6 (no implementados)
- Esto permite testing inmediato del orquestador con briefs reales
- Los cerebros 2-6 se implementarán en PRPs futuros

---

## References

- `PRPs/PRP-006-orchestrator.md` — Orchestrator specification
- `agents/orchestrator/system-prompt.md` — Orchestrator system prompt
- `agents/orchestrator/config/flows.yaml` — Flow definitions
- `tools/mastermind-cli/` — Existing CLI structure
