# Execution Modes Policy

## 1. Propósito

Definir los modos de ejecución canónicos que gobiernan cómo MasterMind puede continuar, pausar, cambiar de backend o escalar al usuario durante tareas largas, especialmente bajo el Window Scheduler.

---

## 2. Definición

> Los Execution Modes son políticas explícitas de autonomía operativa que determinan hasta dónde puede actuar MasterMind sin confirmación humana y bajo qué condiciones debe detenerse, preguntar o continuar automáticamente.

---

## 3. Por qué hace falta esta policy

MasterMind necesita equilibrar:

- continuidad de trabajo
- aprovechamiento de ventanas de suscripción
- control humano
- seguridad de acciones
- confianza del operador

Sin una policy explícita, la automatización puede volverse impredecible o demasiado conservadora.

---

## 4. Modos canónicos

### Mode A — `pause_and_ask`

El sistema se detiene ante eventos relevantes y solicita decisión humana.

#### Comportamiento esperado

- crea checkpoint
- registra evento
- resume solo después de confirmación humana

#### Cuándo usarlo

- tareas sensibles
- debugging delicado
- cambios caros o irreversibles
- primeras pruebas de un project adapter

#### Beneficios

- máxima supervisión
- menor sorpresa operativa

#### Riesgos

- baja autonomía
- poco aprovechamiento nocturno

---

### Mode B — `automatic_cycle`

El sistema continúa automáticamente mientras existan backends elegibles y no se crucen límites de policy.

#### Comportamiento esperado

- checkpoint antes de cada switch
- cambio automático entre backends elegibles
- reintentos programados
- reporte matutino obligatorio

#### Cuándo usarlo

- trabajo nocturno
- tareas largas de construcción o documentación
- operaciones de bajo riesgo relativo

#### Beneficios

- máxima utilización de capacidad disponible
- mejor continuidad sin presencia humana

#### Riesgos

- más complejidad operativa
- mayor dependencia de buenas policies y auditoría

---

### Mode C — `hybrid`

El sistema cambia automáticamente dentro de límites definidos, pero pausa cuando aparece una frontera de costo, riesgo, gobernanza o ambigüedad.

#### Comportamiento esperado

- automático entre suscripciones permitidas
- pausa al entrar a fallbacks costosos
- pausa al enfrentar acciones de alto riesgo
- pausa si la confianza del scheduler es baja

#### Cuándo usarlo

- modo diario recomendado
- overnight controlado
- equipos que quieren autonomía sin perder supervisión

#### Beneficios

- equilibrio entre continuidad y control
- más confianza para adopción real

#### Riesgos

- requiere políticas de frontera bien definidas

---

## 5. Modo recomendado por defecto

### Recomendación canónica

> El modo por defecto recomendado para MasterMind es `hybrid`.

### Razón

Porque:

- permite aprovechar múltiples ventanas de suscripción
- reduce sorpresas frente a costos o riesgos inesperados
- facilita trabajo autónomo nocturno con mejores guardrails

---

## 6. Tipos de frontera que obligan pausa o escalación

### A. Costo

Ejemplos:

- pasar de subscription a API paga
- activar un backend de costo alto
- exceder presupuesto de ejecución configurado

### B. Riesgo

Ejemplos:

- acción con impacto productivo alto
- ejecución real en sistemas sensibles
- cambios de alta criticidad

### C. Gobernanza

Ejemplos:

- falta de aprobación para tarea crítica
- ausencia de evidencia suficiente
- falta de audit trail previo

### D. Incertidumbre operativa

Ejemplos:

- estimación de reset con baja confianza
- checkpoint incompleto
- error repetido sin diagnóstico claro

---

## 7. Matriz de comportamiento resumida

| Situación | pause_and_ask | automatic_cycle | hybrid |
|---|---|---|---|
| Ventana agotada con backend alterno elegible | Pause | Switch | Switch |
| Fallback a API paga | Pause | Switch si policy lo permite | Pause por defecto |
| Acción de alto riesgo | Pause | Pause si gate lo exige | Pause |
| Todos los backends agotados | Pause | Wait or Pause | Wait or Pause |
| Checkpoint incompleto | Pause | Pause | Pause |
| Overnight run de bajo riesgo | Opcional | Sí | Sí |

---

## 8. Controles mínimos por modo

### Controles comunes a todos

- checkpoint antes de switch
- evento de auditoría por transición
- límites de costo y riesgo configurables
- posibilidad de revisión posterior

### Controles extra para `automatic_cycle`

- reporte matutino obligatorio
- máximo de switches por run
- fallbacks explícitamente permitidos

### Controles extra para `hybrid`

- fronteras de pausa documentadas
- reglas claras de cuándo escalar al humano

---

## 9. Configuración mínima sugerida

```yaml
execution_policy:
  mode: "hybrid"
  overnight_mode: true
  max_switches_per_run: 6
  allow_paid_api_fallback: false
  require_human_for_high_risk_actions: true
  max_cost_tier: "medium"
  pause_on_low_confidence_reset: true
```

---

## 10. Reglas canónicas

### Regla 1
Ningún modo permite cambiar backend sin checkpoint.

### Regla 2
Ningún modo elimina la obligación de audit trail.

### Regla 3
Las acciones de alto riesgo deben seguir siendo pausable incluso bajo automatización.

### Regla 4
Si la política del proyecto no está definida, se usa `hybrid`.

### Regla 5
Todo overnight run debe dejar un resumen revisable por humanos.

---

## 11. Señales para cambiar de modo

### Moverse hacia `pause_and_ask`

Cuando:

- el proyecto entra en etapa crítica
- el costo potencial sube
- la confianza en el scheduler baja
- hay errores repetidos o gaps de auditoría

### Moverse hacia `automatic_cycle`

Cuando:

- las tareas son rutinarias
- los checkpoints son robustos
- el costo está controlado
- el reporte matutino ya es confiable

### Mantener `hybrid`

Cuando:

- se quiere productividad sostenida con límites claros
- el proyecto combina autonomía con puntos de control

---

## 12. Relación con Project Adapters

Cada Project Adapter puede ajustar:

- límites de costo
- límites de riesgo
- backends permitidos
- tareas que siempre requieren humano

Pero no debe redefinir los modos canónicos del core.

---

## 13. Relación con DR-002

Este documento cumple el Gate 2 definido en:

- `docs/canonical/decision-records/DR-002-SUBSCRIPTION-WINDOW-STRATEGY.md`

Sigue pendiente:

- reforzar el mínimo auditable por switch como decisión o spec explícita

---

## 14. Próximos artefactos recomendados

1. `DR-003-BACKEND-SWITCH-AUDIT-MINIMUMS.md`
2. `MORNING-REPORT-TEMPLATE.md`
3. `WINDOW-SCHEDULER-DATA-SCHEMA.md`
4. `RUN-POLICY-EXAMPLES.md`

## Key Learnings:

1. La automatización útil no depende solo de cambiar de backend, sino de definir hasta dónde puede actuar el sistema sin supervisión.
2. `hybrid` es el mejor modo por defecto porque equilibra autonomía, costo y confianza.
3. Las fronteras de pausa deben estar definidas por costo, riesgo, gobernanza e incertidumbre operativa.
