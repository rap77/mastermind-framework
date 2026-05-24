# Doctrine Projection Format

## 1. Propósito

Definir el formato mínimo que MasterMind debe proyectar hacia agentes y humanos para comunicar la doctrina aplicable a una tarea, run o decisión.

---

## 2. Tesis central

> La doctrina no debe vivir solo como documentos; debe poder convertirse en una proyección estructurada, corta, auditable y utilizable en tiempo de ejecución.

---

## 3. Qué debe contener una Doctrine Projection

### A. Identity
- `project_id`
- `task_id` o `run_id`
- `scope`
- `generated_at`

### B. Methodology
- metodología activa (`SDD`, `TDD`, `hybrid`, `fast_path`)
- razón de selección
- fases obligatorias

### C. Mandatory Rules
- reglas obligatorias aplicables
- severidad
- criterio de cumplimiento

### D. Recommended Rules
- reglas recomendadas
- patrones preferidos
- hints de implementación

### E. Architecture Constraints
- límites de capas
- patrones permitidos o prohibidos
- restricciones de integración

### F. Quality Gates
- validaciones requeridas antes de completar
- revisiones obligatorias
- verificaciones exigidas

### G. Exception Policy
- qué puede exceptuarse
- quién puede aprobar
- cuándo debe pausar

---

## 4. Principios

1. La proyección debe ser más corta que la doctrina fuente.
2. Debe contener solo lo aplicable al scope actual.
3. Debe distinguir obligatorio de recomendado.
4. Debe ser legible por modelos y humanos.

---

## 5. Relación con Context Projection

La Doctrine Projection acompaña a la Context Projection.

### Context Projection responde
- qué está pasando
- qué sigue
- con qué artefactos

### Doctrine Projection responde
- cómo debe ejecutarse
- qué metodología aplica
- qué reglas son obligatorias
- qué gates deben pasarse

---

## 6. Formato JSON simplificado

```json
{
  "identity": {
    "project_id": "mastermind",
    "task_id": "task-runtime-schema",
    "scope": "task",
    "generated_at": "2026-05-23T10:00:00-04:00"
  },
  "methodology": {
    "active": "SDD",
    "reason": "cross-cutting architectural change",
    "required_phases": ["spec", "design", "implementation", "review"]
  },
  "mandatory_rules": [
    {
      "rule_id": "arch-core-adapter-boundary",
      "summary": "No mezclar lógica reusable del core con lógica local del adapter",
      "severity": "mandatory",
      "check": "validate touched modules stay within declared boundary"
    }
  ],
  "recommended_rules": [
    {
      "rule_id": "artifact-first-context",
      "summary": "Priorizar artefactos y estado estructurado sobre transcript bruto"
    }
  ],
  "architecture_constraints": [
    "Persist runtime state in Postgres hybrid model",
    "Use JSON projections for agent consumption"
  ],
  "quality_gates": [
    "Decision record updated if architecture changes",
    "Checkpoint continuity preserved",
    "Telemetry path identified"
  ],
  "exception_policy": {
    "human_approval_required_for_overrides": true,
    "pause_if_mandatory_rule_cannot_be_met": true
  }
}
```

---

## 7. Niveles de proyección

### Nivel 1 — Minimal Doctrine Projection

Para tareas pequeñas o bajo pressure:
- metodología activa
- 3 a 5 reglas obligatorias
- quality gates

### Nivel 2 — Standard Doctrine Projection

Para la mayoría de las tareas:
- metodología
- reglas obligatorias y recomendadas
- constraints arquitectónicas
- gates
- exception policy

### Nivel 3 — High-Risk Doctrine Projection

Para tareas sensibles:
- todo lo anterior
- ownership de aprobación
- pause conditions
- criteria de override

---

## 8. Regla de ensamblaje

La proyección doctrinal debe generarse combinando, en orden:

1. doctrina global
2. doctrina del proyecto
3. doctrina del nicho
4. policy de fase/tipo de tarea
5. overrides aprobados

---

## 9. Qué NO hacer

- pasar documentos doctrinales completos al modelo
- mezclar reglas obligatorias con sugerencias sin marcar diferencia
- ocultar excepciones o overrides activos
- dejar la metodología implícita

---

## 10. Próximos artefactos recomendados

1. `32-INITIAL-API-SURFACE.md`
2. `33-DASHBOARD-REALTIME-EVENTS.md`
3. `34-DOCTRINE-RULE-SCHEMA.md`

## Key Learnings:

1. La doctrina debe poder convertirse en una estructura ejecutable y breve.
2. Separar obligatorio, recomendado y excepciones es esencial para gobernanza real.
3. La metodología activa debe viajar explícitamente con cada tarea importante.
