# /mm:discovery - Actualizado con AskUserQuestion UI

## Cambios en Sesión 2026-03-09

El comando `/mm:discovery` fue actualizado para usar `AskUserQuestion` con opciones tabuladas, similar a `/interview-me`.

## Nuevo Flujo

1. **Phase 1: Pre-Analysis** - Forked Explore agent analiza brief + codebase
2. **Phase 2: Generate Plan** - `coordinator.generate_discovery_plan(brief)` consulta Brain #8
3. **Phase 3: Conduct Interview** - `AskUserQuestion` con 2-4 opciones por pregunta
4. **Phase 4: Generate Deliverable** - Markdown + YAML + JSON

## Coordinator API Nuevo Método

```python
def generate_discovery_plan(brief: str, use_mcp: bool = False) -> Dict:
    """Generate discovery interview plan (public API for skills/CLI).

    Returns:
        - status: 'success' or 'fallback'
        - plan: dict with categories, questions, gaps
        - raw_response: raw Brain #8 response
        - method: 'mcp' or 'local'
    """
```

## Coverage Tracker

Se muestra antes de cada pregunta:
```
Coverage: Problem [done] | Users [in progress] | Platforms [pending] | Features [pending]
```

## Archivos Modificados

- `.claude/commands/mm/discovery.md` - Actualizado con formato AskUserQuestion
- `mastermind_cli/orchestrator/coordinator.py` - Agregado método público `generate_discovery_plan()`
