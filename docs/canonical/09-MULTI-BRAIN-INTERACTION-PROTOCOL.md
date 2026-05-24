# Multi-Brain Interaction Protocol

## 1. Objetivo

Definir cómo múltiples brains deben interactuar, debatir, desafiar supuestos, sintetizar posiciones y tomar decisiones o acciones sin caer en caos, ruido o falsas convergencias.

## 2. Principio central

> Los brains no deben “hablar libremente” entre sí sin estructura. Deben operar bajo un protocolo formal de colaboración, crítica y decisión.

+Sin protocolo, un sistema multi-brain degenera en:

- redundancia
- groupthink
- contradicciones no resueltas
- falsa inteligencia colectiva
- acciones mal autorizadas

## 3. Preguntas que resuelve este protocolo

- ¿Quién participa en un problema dado?
- ¿Qué hace cada brain primero?
- ¿Cuándo pueden criticarse entre sí?
- ¿Quién decide qué?
- ¿Quién puede vetar?
- ¿Cuándo una decisión se transforma en acción?

## 4. Tipos de interacción

### A. Analysis

Cada brain produce una lectura inicial independiente desde su disciplina.

### B. Cross-Critique

Los brains cuestionan supuestos, evidencias, riesgos y vacíos de otros brains.

### C. Defense

Un brain responde objeciones sobre su recomendación.

### D. Synthesis

Se integran acuerdos, desacuerdos, riesgos y opciones.

### E. Decision

Se emite un veredicto o recomendación de acción.

### F. Action Gating

Se verifica si la decisión está autorizada para convertirse en acción real.

## 5. Flujo base

```text
1. Frame problem
2. Parallel analysis
3. Cross-critique
4. Synthesis
5. Decision
6. Gate before action
7. Execute
8. Review outcome
9. Learn
```

## 6. Etapas del protocolo

## Etapa 1 — Problem Framing

### Objetivo

Asegurar que todos debaten el mismo problema.

### Responsable

- Orchestrator
- o Brain de estrategia/producto

### Output esperado

- problem statement
- objetivo
- contexto
- restricciones
- criterios de éxito
- tipo de decisión requerida

### Regla

No se inicia el debate hasta que el problema esté formulado con precisión suficiente.

---

## Etapa 2 — Parallel First-Pass Analysis

### Objetivo

Obtener análisis independientes antes de cualquier influencia cruzada.

### Regla crítica

Cada brain analiza por separado.

### Beneficios

- reduce groupthink
- preserva diversidad epistemológica
- evita que un brain dominante sesgue al resto

### Output esperado por brain

- posición inicial
- supuestos
- riesgos detectados
- recomendación provisional
- confidence / uncertainty

---

## Etapa 3 — Structured Cross-Critique

### Objetivo

Hacer que los brains desafíen explícitamente el razonamiento de otros.

### Cada brain debe responder

1. ¿Qué supuesto del otro brain me parece débil?
2. ¿Qué evidencia falta?
3. ¿Qué riesgo no está cubierto?
4. ¿Qué conclusión me parece prematura?
5. ¿Qué cambiaría mi posición?

### Regla

La crítica debe dirigirse a:

- supuestos
- evidencia
- riesgos
- inconsistencias
- gating de acción

No a opiniones vagas.

---

## Etapa 4 — Synthesis Layer

### Objetivo

Convertir múltiples posiciones en una estructura de decisión clara.

### Responsable

- Orchestrator
- Synthesis Brain
- o Brain #7 con soporte estructurado

### Debe producir

#### A. Agreements

Qué cosas están consensuadas

#### B. Disagreements

Qué sigue en disputa

#### C. Gaps

Qué información o evidencia falta

#### D. Options

Qué caminos existen

#### E. Blocked Actions

Qué acciones no pueden ejecutarse todavía

---

## Etapa 5 — Decision Protocol

No todas las decisiones se toman igual.

### Tipo A — Decision by Ownership

Si una decisión pertenece claramente a un brain, ese brain es el owner.

Ejemplos:

- sizing → Risk Brain
- slippage realism → Execution Brain
- auditability controls → Compliance Brain

### Tipo B — Decision by Synthesis

Si la decisión cruza disciplinas, requiere síntesis multi-brain.

Ejemplo:

- pasar de paper trading a live capital

### Tipo C — Decision by Veto

Algunas acciones deben poder ser bloqueadas por brains críticos.

Ejemplos:

- Risk puede vetar live deployment
- Compliance puede vetar operación sin controles
- Evaluator puede vetar por evidencia insuficiente

---

## Etapa 6 — Action Gating

### Objetivo

Evitar que una decisión se convierta automáticamente en acción sin control.

### Regla

Una acción importante requiere:

- decisión emitida
- evidencia suficiente
- gates cumplidos
- ausencia de veto activo

### Ejemplos de gates

- tests completados
- validación estadística suficiente
- riesgo aceptable
- slippage model realista
- compliance controls listos
- observabilidad lista
- approvals registrados

## 7. Roles funcionales de un brain dentro de una interacción

Cada brain puede operar en uno o varios modos:

### 1. Analyst

Produce análisis inicial

### 2. Critic

Cuestiona supuestos y vacíos

### 3. Defender

Responde objeciones sobre su propuesta

### 4. Decider

Toma decisión en su área de ownership

### 5. Veto Holder

Puede bloquear acciones peligrosas

### 6. Evaluator

Juzga la calidad del proceso y del resultado

## 8. Decision Rights Matrix

Se recomienda definir explícitamente una matriz como esta por dominio:

| Tipo de decisión | Brain owner | Quiénes pueden objetar | Quién puede vetar |
|---|---|---|---|
| Strategic direction | Strategy Brain | Quant, Risk, Evaluator | Risk, Evaluator |
| Signal validity | Quant Brain | Strategy, Risk, Execution | Quant, Evaluator |
| Position sizing | Risk Brain | Quant, Portfolio, Evaluator | Risk, Evaluator |
| Execution rollout | Execution Brain | Quant, Risk, Compliance | Risk, Compliance, Evaluator |
| Live deployment approval | Shared | Todos | Risk, Compliance, Evaluator |

## 9. Decision Record

Cada decisión importante debe registrar:

- problem statement
- options considered
- participating brains
- positions by brain
- objections
- unresolved risks
- final verdict
- gates required
- action taken
- timestamp / trace / reviewer

## 10. Debate quality rules

### Regla 1

No permitir debate libre simultáneo sin estructura.

### Regla 2

Primero análisis independiente, luego crítica cruzada.

### Regla 3

Toda objeción debe referirse a:

- supuesto
- evidencia
- riesgo
- inconsistencia
- acción bloqueada

### Regla 4

Toda recomendación importante debe declarar:

- nivel de confianza
- principal riesgo
- evidencia faltante
- condición de reversión

## 11. Ejemplo aplicado a trading algorítmico

### Problema

“¿Debemos activar una estrategia X en mercado real?”

### Secuencia

#### F1 Strategy

Evalúa si la hipótesis estratégica tiene sentido económico.

#### F2 Quant

Valida robustez estadística, leakage, overfitting y out-of-sample.

#### F3 Risk

Define límites, drawdown tolerable, sizing y escenarios de pérdida.

#### F4 Portfolio

Revisa correlaciones, exposición agregada y capital allocation.

#### F5 Execution

Evalúa slippage, liquidez, latency, order behavior y broker realism.

#### F6 Compliance / Governance

Revisa logs, approvals, kill switch, audit trail y controls.

#### F7 Evaluator

Emite estado final:

- APPROVED
- APPROVED WITH CONDITIONS
- NEEDS MORE EVIDENCE
- REJECTED

## 12. Output esperado del protocolo

El resultado no debe ser solo una “opinión grupal”.

Debe ser:

- una decisión estructurada
- con ownership
- con objeciones visibles
- con riesgos pendientes
- con gates claros
- con trazabilidad

## 13. Riesgos que este protocolo busca evitar

- consenso artificial
- dominancia de un brain
- ambigüedad de ownership
- despliegues prematuros
- aprendizaje de malas decisiones
- pérdida de trazabilidad

## 14. Integración con aprendizaje

Después de cada ciclo:

- se registra qué posición fue correcta
- qué objeciones fueron útiles
- qué gates evitaron errores
- qué brains acertaron o subestimaron riesgos

Eso alimenta la **Experience Memory** de cada brain y del sistema.

## 15. Decisión canónica sugerida

> Todo sistema multi-brain de MasterMind debe operar con un protocolo explícito de framing, análisis paralelo, crítica cruzada, síntesis, decisión, veto y action gating.

## 16. Próximos documentos derivados

1. `DECISION-RIGHTS-MATRIX-TEMPLATE.md`
2. `DECISION-RECORD-TEMPLATE.md`
3. `DOMAIN-SPECIFIC-INTERACTION-PROTOCOLS.md`
