# Morning Report Template

## 1. Propósito

Definir la plantilla mínima para revisar una ejecución automática o nocturna de MasterMind al día siguiente.

El objetivo es que un operador humano pueda entender rápidamente:

- qué trabajo se hizo
- qué backends se usaron
- cuándo hubo switches o pausas
- qué quedó pendiente
- si hubo errores, costos o riesgos relevantes

---

## 2. Principio rector

> Un morning report debe permitir reconstruir la ejecución automática sin exigir lectura de logs crudos.

---

## 3. Cuándo debe generarse

Generar morning report cuando ocurra cualquiera de estas condiciones:

- una ejecución usa `automatic_cycle`
- una ejecución usa `hybrid` con trabajo nocturno
- hubo uno o más backend switches
- el sistema quedó pausado o bloqueado esperando acción humana

---

## 4. Estructura mínima

```md
# Morning Report — [run_id]

## Project
- project_id:
- adapter:
- date:
- execution_mode:

## Summary
- start_time:
- end_time:
- final_status:
- tasks_advanced:
- tasks_blocked:

## Backends Used
| backend | provider | auth_mode | used_from | used_to | reason_stopped |
|---|---|---|---|---|---|

## Switch Events
| time | from | to | reason | checkpoint_id | outcome |
|---|---|---|---|---|---|

## Checkpoints Created
- checkpoint_id:
  - task:
  - next_step:

## Errors / Warnings
- ...

## Cost / Risk Notes
- ...

## Pending Human Decisions
- ...

## Suggested Next Action
- ...
```

---

## 5. Secciones obligatorias

### A. Project

Debe identificar:

- proyecto
- adapter relevante
- run id
- fecha exacta
- modo de ejecución usado

### B. Summary

Debe resumir:

- hora de inicio y fin
- estado final (`completed`, `paused`, `waiting_for_window`, `failed`)
- qué tareas avanzaron
- qué quedó pendiente

### C. Backends Used

Debe mostrar claramente:

- backend
- proveedor
- modo de autenticación
- intervalo aproximado de uso
- motivo de salida

### D. Switch Events

Debe resumir cada switch sin obligar a leer el audit log completo.

### E. Checkpoints Created

Debe señalar dónde puede retomarse el trabajo.

### F. Errors / Warnings

Debe listar:

- errores de backend
- estimaciones de reset dudosas
- límites de costo o riesgo tocados
- reintentos fallidos

### G. Pending Human Decisions

Debe dejar explícito qué necesita intervención humana.

### H. Suggested Next Action

Debe proponer el siguiente movimiento más razonable.

---

## 6. Señales de mala calidad del report

El report está mal si:

- no se entiende por qué cambió de backend
- no se sabe dónde retomar
- no se ve el estado final real
- mezcla demasiados logs crudos con poco resumen
- no distingue errores de bloqueos normales

---

## 7. Relación con otros artefactos

Este template debe alimentarse de:

- `backend_switch` events
- checkpoints
- availability tracker
- run policy activa
- estado final de la orquestación

---

## 8. Relación con DR-002 y DR-003

Este documento operacionaliza la parte humana de:

- `DR-002-SUBSCRIPTION-WINDOW-STRATEGY.md`
- `DR-003-BACKEND-SWITCH-AUDIT-MINIMUMS.md`

---

## 9. Ejemplo breve

```md
# Morning Report — night-run-001

## Project
- project_id: mastermind
- adapter: finance-trading-pilot
- date: 2026-05-23
- execution_mode: hybrid

## Summary
- start_time: 2026-05-23T00:05:00-04:00
- end_time: 2026-05-23T05:42:00-04:00
- final_status: paused_for_user
- tasks_advanced: 3
- tasks_blocked: 1

## Backends Used
| backend | provider | auth_mode | used_from | used_to | reason_stopped |
|---|---|---|---|---|---|
| claude-sub-01 | claude | subscription | 00:05 | 02:14 | window_exhausted |
| codex-sub-01 | codex | subscription | 02:16 | 05:42 | reached_cost_boundary |

## Switch Events
| time | from | to | reason | checkpoint_id | outcome |
|---|---|---|---|---|---|
| 02:15 | claude-sub-01 | codex-sub-01 | window_exhausted | chk-099 | switched |

## Checkpoints Created
- checkpoint_id: chk-099
  - task: finance expert-pack refinement
  - next_step: validate expert coverage for F2 and F3

## Errors / Warnings
- reset time for claude-sub-01 inferred heuristically with low confidence

## Cost / Risk Notes
- paid API fallback was not used

## Pending Human Decisions
- approve whether to continue using codex-sub-01 next night

## Suggested Next Action
- review checkpoint chk-099 and decide if claude-sub-01 should remain priority 1
```

---

## 10. Próximos artefactos recomendados

1. `19-WINDOW-SCHEDULER-DATA-SCHEMA.md`
2. `20-RUN-POLICY-EXAMPLES.md`

## Key Learnings:

1. La revisión humana del día siguiente necesita resumen estructurado, no logs crudos.
2. El morning report cierra el ciclo de confianza entre automatización nocturna y supervisión humana.
3. Un buen reporte siempre debe responder: qué se hizo, por qué se cambió, dónde retomar y qué decidir ahora.
