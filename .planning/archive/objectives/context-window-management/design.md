# Design — context-window-management

## Architecture / Boundaries
- `window_scheduler/context_fit.py` conserva la decisión canónica de fit y se
  extiende con contratos de presupuesto, no con lógica de provider.
- Un nuevo packager puro transforma segmentos estructurados en un payload por
  prioridad; no llama modelos ni persiste estado.
- `WindowSchedulerService` compone el fit de contexto con la policy existente al
  evaluar un switch; availability, riesgo y aprobación conservan su autoridad.
- Checkpoints existentes aportan objetivo, estado y siguiente paso. El contexto
  de reanudación transporta referencias a artifacts en lugar de history crudo.

## Technical Approach
1. Definir contratos inmutables para `ContextBudgetEstimate`, segmentos
   priorizados y resultado de packing.
2. Extender la evaluación de fit para consumir budget de input y output sin
   cambiar los cuatro estados ya publicados.
3. Implementar un packager determinístico que agrega niveles en orden y nunca
   omite segmentos core/decision-critical para satisfacer un límite.
4. Proyectar el verdict hacia el switch: `fits_cleanly` permite el candidato;
   `fits_with_compression` exige una estrategia declarada; `unsafe_fit` y
   `does_not_fit` bloquean o escalan según policy.
5. Persistir sólo las referencias y decision rationale necesarias para reanudar;
   no almacenar transcripts completos ni introducir una migración de provider
   registry hasta que el contrato esté validado.

## Dependencies
- Depends on `window-scheduler`
- `apps/api/mastermind_cli/window_scheduler/context_fit.py`
- `apps/api/mastermind_cli/window_scheduler/service.py`
- `apps/api/mastermind_cli/window_scheduler/policy.py`
- scheduler checkpoints y backend inventory existentes

## Validation Strategy
- `cd apps/api && uv run pytest -q tests/unit/test_context_fit.py`
- `cd apps/api && uv run pytest -q tests/unit/test_context_packager.py`
- `cd apps/api && uv run pytest -q tests/unit/test_window_scheduler_policy.py tests/unit/test_window_scheduler_service.py`
- `cd apps/api && uv run ruff check mastermind_cli/window_scheduler tests/unit/test_context_fit.py tests/unit/test_context_packager.py`
- `cd apps/api && uv run mypy mastermind_cli/window_scheduler`
- No ejecutar builds standalone.

## Important Tradeoffs
- Un packager determinístico no reemplaza la compresión semántica de un modelo,
  pero permite probar el límite de seguridad primero.
- Persistir perfiles de capacidad en la base ahora añade migración y riesgo; el
  primer slice usa perfiles explícitos y deja persistence versionada para una
  tarea posterior si los tests confirman el contract.
- Bloquear `unsafe_fit` puede reducir switches disponibles, pero evita pérdida
  silenciosa de decisiones críticas.

## Context Notes
- Canonical source: `docs/canonical/20-CONTEXT-WINDOW-MANAGEMENT-ARCHITECTURE.md`.
- El paquete no introduce tokenizers ni SDKs de proveedores; los token counts
  ingresan como estimaciones validadas.
