# Finance Trading Brain Team

## 1. Objetivo

Definir el equipo base de brains financieros para el subnicho:

> **Trading + Algorithmic Trading + Investments**

con el fin de guiar al equipo de brains de software en la construcción del mejor software posible para este dominio.

## 2. Working Problem

Queremos construir software que:

- use data histórica
- genere hipótesis, señales o decisiones de inversión/trading
- valide esas hipótesis con rigor
- pueda eventualmente operar en mercado real
- mantenga control riguroso de riesgo, ejecución, auditoría y seguridad operacional

## 3. Principle

> Un buen sistema de trading no se construye con un solo brain financiero. Requiere un equipo de brains especializados que cubra estrategia, validez cuantitativa, riesgo, ejecución, governance y evaluación.

## 4. Base Financial Brain Team

## F1 — Trading Strategy & Market Hypothesis Brain

### Responsibility

Definir qué tipo de estrategias tienen sentido, en qué mercados, bajo qué supuestos y con qué horizonte temporal.

### Questions it answers

- ¿Qué edge se busca?
- ¿Qué mercado conviene atacar primero?
- ¿Qué hipótesis económica justifica la estrategia?

### Output

- strategy hypotheses
- market selection logic
- assumptions to validate

---

## F2 — Quant Research & Signal Validation Brain

### Responsibility

Determinar si una señal o hipótesis tiene robustez real o si es ruido.

### Questions it answers

- ¿Hay alpha real o overfitting?
- ¿Existe leakage?
- ¿La señal sobrevive out-of-sample / walk-forward?

### Output

- quant validation criteria
- robustness requirements
- signal rejection or conditional approval

---

## F3 — Risk Management & Position Sizing Brain

### Responsibility

Definir cuánto se puede arriesgar, bajo qué límites y cómo proteger el sistema de pérdidas destructivas.

### Questions it answers

- ¿Cuál es el sizing correcto?
- ¿Qué max drawdown es aceptable?
- ¿Qué límites deben bloquear la estrategia?

### Output

- risk rules
- sizing policies
- drawdown and kill-switch thresholds

---

## F4 — Portfolio Construction & Capital Allocation Brain

### Responsibility

Definir cómo se asigna capital entre estrategias, activos o exposiciones.

### Questions it answers

- ¿Conviene una sola estrategia o varias?
- ¿Cómo se distribuye el capital?
- ¿Qué correlaciones destruyen la diversificación aparente?

### Output

- allocation model
- diversification rules
- interaction constraints

---

## F5 — Market Microstructure & Execution Brain

### Responsibility

Asegurar que la estrategia sea ejecutable en condiciones de mercado realistas.

### Questions it answers

- ¿Los fills asumidos son realistas?
- ¿Qué slippage, spread y latency importan?
- ¿Qué order types y execution logic convienen?

### Output

- execution assumptions
- slippage model requirements
- broker/venue realism constraints

---

## F6 — Compliance, Audit & Trading Governance Brain

### Responsibility

Definir controles, approvals, trazabilidad y límites antes de operar con dinero real.

### Questions it answers

- ¿Qué approvals hacen falta?
- ¿Cómo se audita una orden?
- ¿Qué gates son obligatorios antes de live trading?

### Output

- governance rules
- audit requirements
- control gates

---

## F7 — Performance Analytics & Evaluator Brain

### Responsibility

Juzgar si el sistema realmente mejora y si la aparente performance es robusta.

### Questions it answers

- ¿La estrategia es robusta o solo atractiva?
- ¿Qué métricas importan de verdad?
- ¿Qué drift existe entre backtest, paper trading y live?

### Output

- evaluation rubric
- performance interpretation
- approval / conditional approval / rejection

## 5. Collaboration With Software Brains

El equipo financiero no construye solo; guía al equipo de software.

## Financial → Software mapping

| Financial Brain | Main Software Counterparts | What it influences |
|---|---|---|
| F1 Strategy | Product Strategy, Backend | problem framing, strategy model, feature scope |
| F2 Quant | Backend, QA | research engine, backtesting validation, statistical tests |
| F3 Risk | Backend, QA, DevOps | risk engine, limits, kill switches |
| F4 Portfolio | Backend | allocation engine, multi-strategy coordination |
| F5 Execution | Backend, DevOps | broker adapters, order lifecycle, execution engine |
| F6 Governance | QA, DevOps, Evaluator | audit trail, approvals, action gating |
| F7 Evaluator | Growth/Data, QA, Evaluator | metrics, robustness review, model drift |

## 6. Software Platform Modules Implied by This Team

Este equipo financiero implica que el software debería tener al menos:

1. historical data platform
2. research engine
3. backtesting engine
4. risk engine
5. execution engine
6. monitoring/control room
7. audit & governance layer

## 7. Decision Rights Draft

| Decision Type | Primary Owner Brain | Who Can Object | Who Can Veto |
|---|---|---|---|
| Strategy selection | F1 | F2, F3, F5, F7 | F3, F7 |
| Signal validity | F2 | F1, F3, F5, F7 | F2, F7 |
| Position sizing | F3 | F2, F4, F7 | F3, F7 |
| Capital allocation | F4 | F3, F7 | F3, F7 |
| Execution rollout | F5 | F2, F3, F6, F7 | F3, F6, F7 |
| Live trading approval | Shared | All | F3, F6, F7 |

## 8. MVP Recommendation

Para el MVP, este equipo base es suficiente para comenzar.

### Importante

No hace falta crear sub-brains más finos todavía (options, credit, fixed income, crypto microstructure, etc.) hasta validar este equipo base.

## 9. Strategic Decision

> El primer paso correcto para el nicho Finance/Trading no es crear un “Finance Brain”, sino crear un **Finance Trading Brain Team** que cubra estrategia, cuant, riesgo, portfolio, ejecución, governance y evaluación.

## 10. Next Steps

Siguientes artefactos recomendados:

1. `F1-TRADING-STRATEGY-BRAIN-SPEC.md`
2. `F2-QUANT-RESEARCH-BRAIN-SPEC.md`
3. `F3-RISK-MANAGEMENT-BRAIN-SPEC.md`
4. `F4-PORTFOLIO-ALLOCATION-BRAIN-SPEC.md`
5. `F5-EXECUTION-BRAIN-SPEC.md`
6. `F6-GOVERNANCE-BRAIN-SPEC.md`
7. `F7-PERFORMANCE-EVALUATOR-BRAIN-SPEC.md`
