# Guía: Usar MasterMind Framework en Proyectos Externos

## Opción 1: Script de Evaluación (Recomendado)

### Instalación Rápida

```bash
# Clona el framework (si no lo tienes)
git clone https://github.com/rap77/mastermind-framework.git
cd mastermind-framework

# Instala dependencias
uv sync

# ¡Listo!
```

### Uso Básico

```bash
# 1. Evaluar el brief de ejemplo
uv run python scripts/evaluar_proyecto.py --example

# 2. Evaluar tu propio brief (inline)
uv run python scripts/evaluar_proyecto.py --brief "
Mi app de delivery de comida saludable.
Problema: La gente no tiene tiempo de cocinar saludable.
Solución: App que conecta con cocinadores locales.
Evidencia: 20 personas entrevistadas.
Métricas: D30 retention >20%
"

# 3. Evaluar desde archivo
uv run python scripts/evaluar_proyecto.py --file mi_brief.md

# 4. Con NotebookLM real (requiere nlm CLI login previo)
uv run python scripts/evaluar_proyecto.py --example --mcp

# 5. Flujo completo (todos los cerebros)
uv run python scripts/evaluar_proyecto.py --example --flow full_product
```

### Template de Brief

Crea `mi_brief.md`:

```markdown
# [Nombre de tu Proyecto]

## Problema
¿Qué dolor resuelves? Sé específico.
- ¿Quién tiene el problema?
- ¿Con qué frecuencia ocurre?
- ¿Qué soluciones actuales usan?

## Solución
¿Cómo lo resuelves?
- Describe tu propuesta
- ¿Por qué es mejor que lo actual?

## Usuario Objetivo
¿Quién es tu usuario?
- Segmento específico
- Contexto de uso

## Evidencia
¿Cómo validaste?
- Entrevistas: X personas
- Observaciones: qué viste
- Datos: métricas de mercado

## Métricas Objetivo
- D7 retention: >X%
- D30 retention: >X%
- Activation rate: >X%
- NPS: >X

## Monetización (si aplica)
- Freemium/Pago/Enterprise
- Pricing estimado
```

---

## Opción 2: Queries Directas a Cerebros (Via Claude Code)

Si estás en Claude Code, puedes hacer queries directas:

### A Cerebro #1 (Product Strategy)

```
Usa el MCP de NotebookLM para consultar el cerebro de Product Strategy:

notebook_id: f276ccb3-0bce-4069-8b55-eae8693dbe75

Query:
"Evalúa este brief de producto SaaS B2B:
[PEGAR BRIEF]

Responde con:
1. ¿El problema está bien definido?
2. ¿La evidencia es suficiente?
3. ¿Las métricas son realistas?
4. Recomendaciones específicas"
```

### B Cerebro #7 (Growth & Data - Evaluator)

```
Usa el MCP de NotebookLM para consultar el cerebro evaluador:

notebook_id: d8de74d6-7028-44ed-b4d5-784d6a9256e6

Query:
"Evalúa este brief usando las frameworks de Kohabi (FUENTE-713) y Croll (FUENTE-714):
[PEGAR BRIEF]

Responde en YAML con:
- veredict: APPROVE/CONDITIONAL/REJECT
- score: 0-156
- critical_issues: lista
- whats_good: lista
- recommendations: lista"
```

---

## Opción 3: Integración en Tu Proyecto

Crea un archivo `evaluar_con_mastermind.py` en TU proyecto:

```python
#!/usr/bin/env python3
"""
Evalúa mi proyecto usando MasterMind Framework.
"""
import subprocess
import sys

# Tu brief del proyecto
MI_BRIEF = """
[PEGAR TU BRIEF AQUÍ]
"""

def evaluar():
    """Ejecuta la evaluación."""
    result = subprocess.run(
        [
            "uv", "run", "python",
            "/path/to/mastermind-framework/scripts/evaluar_proyecto.py",
            "--brief", MI_BRIEF,
            "--mcp"  # Comenta si no quieres NotebookLM real
        ],
        capture_output=True,
        text=True
    )

    print(result.stdout)
    print(result.stderr)

    # Exit code indica calidad del brief
    # 0 = APPROVE, 1 = CONDITIONAL, 2 = REJECT
    return result.returncode

if __name__ == "__main__":
    exit_code = evaluar()
    print(f"\nExit code: {exit_code}")
    print("0 = APPROVE ✓")
    print("1 = CONDITIONAL ⚠")
    print("2 = REJECT ✗")
    sys.exit(exit_code)
```

---

## Interpretación de Resultados

### Veredictos

| Veredicto | Significado | Acción |
|-----------|-------------|--------|
| **APPROVE** | Brief sólido | Avanzar con desarrollo |
| **CONDITIONAL** | Bueno pero necesita ajustes | Iterar y re-evaluar |
| **REJECT** | Problemas serios | Revisar desde cero |

### Score

| Rango | Calidad |
|-------|---------|
| 130-156 | Excellent |
| 100-129 | Good |
| 70-99 | Needs work |
| 40-69 | Weak |
| 0-39 | Reject |

---

## Ejemplo Real: Freelancers App

```bash
# Ejecutar
uv run python scripts/evaluar_proyecto.py --example --mcp

# Resultado esperado:
# Veredict: CONDITIONAL
# Score: ~70/156
#
# Critical issues:
# - Sample size (12 entrevistas) es bajo
# - Competencia no mencionada
# - No hay pricing basado en valor
#
# Recommendations:
# - Aumentar sample a 30+ entrevistas
# - Investigar soluciones actuales
# - Validar willingness-to-pay real
```

---

## Troubleshooting

### Error: "MCP not available"
```bash
# Instala y autentica nlm CLI
pip install nlm
nlm login

# Reintenta con --mcp
```

### Error: "Module not found"
```bash
# Asegúrate de estar en el directorio correcto
cd /path/to/mastermind-framework
uv sync
```

### Score siempre es 0
- Sin `--mcp`, el modo mock puede dar resultados inconsistentes
- Usa `--mcp` para evaluations reales con NotebookLM

---

## Tips para Buenos Briefs

1. **Evidencia cuantitativa**: Números, no opiniones
   - ❌ "La gente lo quiere"
   - ✅ "15/20 entrevistados dijeron que pagarían $10/mes"

2. **Métricas realistas**: Basadas en benchmarks
   - ❌ "D30 retention 90%"
   - ✅ "D30 retention >20% (benchmark B2C)"

3. **Problema específico**: No todo para todos
   - ❌ "App para ser más productivo"
   - ✅ "App de time tracking para freelancers con 3-10 clientes"

4. **Evidencia de validación**: No asumas, comprueba
   - ❌ "Mi amigo dijo que es buena idea"
   - ✅ "12 freelancers entrevistados, 10 dicen que es top pain"

---

## NotebookLM IDs (Referencia)

| Cerebro | ID | Propósito |
|---------|-----|-----------|
| #1 Product Strategy | f276ccb3-0bce-4069-8b55-eae8693dbe75 | ¿Qué construir y por qué? |
| #2 UX Research | ea006ece-00a9-4d5c-91f5-012b8b712936 | ¿Cómo debe funcionar? |
| #3 UI Design | 8d544475-6860-4cd7-9037-8549325493dd | ¿Cómo se ve? |
| #4 Frontend | 85e47142-0a65-41d9-9848-49b8b5d2db33 | ¿Cómo se construye? |
| #5 Backend | c6befbbc-b7dd-4ad0-a677-314750684208 | ¿Cómo escala? |
| #6 QA/DevOps | 74cd3a81-1350-4927-af14-c0c4fca41a8e | ¿Cómo se despliega? |
| #7 Growth/Data | d8de74d6-7028-44ed-b4d5-784d6a9256e6 | ¿Está funcionando? |

---

¿Quieres que te ayude a evaluar un proyecto específico?
