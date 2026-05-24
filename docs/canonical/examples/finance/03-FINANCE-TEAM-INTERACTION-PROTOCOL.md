# Finance Team Interaction Protocol

## 1. Objetivo

Definir cómo interactúan, debaten, escalan y toman decisiones los brains financieros del equipo base de trading/investments, y cómo coordinan con los brains de desarrollo de software.

## 2. Principio central

> En finance/trading, la calidad no depende solo de tener brains especializados, sino de que interactúen con un protocolo que convierta hipótesis en decisiones gobernadas y acciones seguras.

## 3. Participating Finance Brains

- **F1** Trading Strategy & Market Hypothesis
- **F2** Quant Research & Signal Validation
- **F3** Risk Management & Position Sizing
- **F4** Portfolio Construction & Capital Allocation
- **F5** Market Microstructure & Execution
- **F6** Compliance, Audit & Trading Governance
- **F7** Performance Analytics & Evaluator

## 4. Participating Software Brains

Los cerebros financieros trabajan coordinados con un equipo base de software:

- Product Strategy
- Backend
- QA / DevOps
- Growth / Evaluator
- opcionalmente UX / Frontend / UI cuando el producto lo requiera

## 5. Core Decision Loop

```text
Problem / Opportunity
→ Strategic Framing (F1)
→ Quant Validation (F2)
→ Risk Constraints (F3)
→ Portfolio Logic (F4)
→ Execution Realism (F5)
→ Governance Gates (F6)
→ Performance Evaluation (F7)
→ Decision
→ Software Translation
→ Paper / Simulated / Live Progression
→ Outcome Review
→ Learning Capture
```

## 6. Stages of Interaction

## Stage 1 — Opportunity / Problem Framing

### Lead brain

**F1 Strategy**

### Goal

Convertir una idea vaga en una hipótesis estratégica falsable.

### Output

- target market
- asset class
- horizon
- edge hypothesis
- assumptions to test

### Software interaction

- Product Strategy Brain ayuda a traducir la hipótesis en objetivo de sistema/producto

---

## Stage 2 — Quant Challenge

### Lead brain

**F2 Quant**

### Goal

Determinar si la hipótesis tiene evidencia cuantitativa seria.

### Main tasks

- define validation bar
- reject leakage / overfitting
- specify test design
- mark insufficient evidence

### Output

- quant validity status
- required tests
- go / no-go / conditional progression

### Software interaction

- Backend define data/research engine requirements
- QA define reproducibility and validation checks

---

## Stage 3 — Risk Constraint Layer

### Lead brain

**F3 Risk**

### Goal

Determinar si una idea válida sigue siendo demasiado peligrosa.

### Main tasks

- define risk envelope
- position sizing logic
- veto thresholds
- drawdown and kill-switch conditions

### Output

- risk rules
- veto conditions
- safe progression constraints

### Software interaction

- Backend + QA/DevOps translate this into a risk engine, hard limits and kill switches

---

## Stage 4 — Portfolio Layer

### Lead brain

**F4 Portfolio**

### Goal

Determinar cómo encaja la estrategia dentro de una cartera o un marco de capital allocation.

### Main tasks

- concentration checks
- diversification logic
- interactions with other strategies/exposures

### Output

- allocation guidance
- portfolio-level warnings

### Software interaction

- Backend translate into portfolio state logic and capital allocation components

---

## Stage 5 — Execution Realism

### Lead brain

**F5 Execution**

### Goal

Determinar si el edge sobrevive a condiciones de mercado realistas.

### Main tasks

- slippage realism
- spread and liquidity constraints
- order behavior logic
- broker/venue constraints

### Output

- execution model assumptions
- paper-to-live blockers

### Software interaction

- Backend + DevOps define execution engine, broker adapters, order lifecycle, retries and monitoring

---

## Stage 6 — Governance and Safe Progression

### Lead brain

**F6 Governance**

### Goal

Asegurar que no haya operación seria sin trazabilidad, approvals y gates.

### Main tasks

- approval policy
- audit trail requirements
- escalation requirements
- live-trading governance

### Output

- gates
- approvals
- audit requirements
- blockers for unsafe progression

### Software interaction

- Backend + QA/DevOps define audit log, approval flow, kill switches, traceability

---

## Stage 7 — Performance Judgment

### Lead brain

**F7 Evaluator**

### Goal

Juzgar si el sistema realmente merece avanzar.

### Main tasks

- interpret performance
- detect fragility
- compare backtest / paper / live drift
- issue verdict

### Output

- APPROVED
- APPROVED WITH CONDITIONS
- NEEDS MORE EVIDENCE
- REJECTED

### Software interaction

- Growth/Data + QA support metrics, dashboards, drift analysis and reporting

## 7. Interaction Rules Between Finance Brains

### Rule 1 — Sequential ownership with challenge

Cada stage tiene un owner, pero los demás brains pueden objetar.

### Rule 2 — No skipping quant/risk/governance

Ninguna estrategia avanza directamente de idea a live.

### Rule 3 — F3, F6 and F7 have structural veto power

- **F3** vetoes unsafe risk
- **F6** vetoes ungoverned progression
- **F7** vetoes unjustified confidence

### Rule 4 — Attractive performance does not override controls

Buenas métricas no anulan governance, risk o execution realism.

## 8. Interaction Rules With Software Brains

### Finance brains define:

- what is meaningful
- what is dangerous
- what must be validated
- what must be controlled

### Software brains define:

- how it becomes a system
- how it becomes testable
- how it becomes observable
- how it becomes deployable

### Core translation rule

Finance brains own **domain correctness**.
Software brains own **system realization**.

## 9. Decision Rights Matrix

| Decision Type | Primary Owner | Objectors | Veto Holders |
|---|---|---|---|
| Strategy hypothesis | F1 | F2, F3, F5, F7 | F3, F7 |
| Signal validity | F2 | F1, F3, F5, F7 | F2, F7 |
| Position sizing | F3 | F2, F4, F7 | F3, F7 |
| Allocation model | F4 | F3, F7 | F3, F7 |
| Execution rollout | F5 | F2, F3, F6, F7 | F3, F6, F7 |
| Live trading approval | Shared | All | F3, F6, F7 |

## 10. Progression Model

El paso natural del sistema debe ser:

```text
Idea
→ Research
→ Backtest
→ Paper Trading
→ Controlled Live
→ Scaled Live
```

### No stage transition happens without:

- current-stage evidence
- explicit risk acceptance
- execution realism
- governance approval
- evaluation verdict

## 11. Minimal Artifacts Per Cycle

Cada ciclo serio debería producir:

- strategy thesis
- quant validation note
- risk envelope
- portfolio allocation note
- execution assumptions
- governance gate list
- evaluation verdict
- decision record

## 12. Failure Modes This Protocol Is Designed to Prevent

- good-looking but fake alpha
- hidden execution fragility
- overconfidence from backtests
- risk-blind progression
- governance-free live deployment
- poor translation from finance thinking into software

## 13. MVP Recommendation

For the MVP, this protocol is sufficient if it can guide one serious finance/trading workflow from:

- hypothesis
- to structured judgment
- to software requirements
- to gated progression logic

## 14. Strategic Decision

> The finance/trading pilot should not be executed as isolated specialist opinions, but as a staged interaction protocol with explicit ownership, objections, vetoes and software translation points.
