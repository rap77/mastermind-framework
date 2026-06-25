# Component Methods

## CoordinatorAdapter

### `orchestrate_with_governance(...) -> dict[str, object]`
- Construye la intención, evalúa governance y delega al Coordinator si procede.

## HarnessRegistry

### `list_harnesses() -> list[HarnessDefinition]`
- Devuelve inventario de harnesses soportados.

### `get_harness(harness_id: str) -> HarnessDefinition | None`
- Recupera definición tipada de un harness.

## LoopSelector

### `select_loop(task: TaskProfile) -> LoopPolicy`
- Elige loop base y loops adicionales según complejidad, riesgo y verificabilidad.

### `should_require_review(task: TaskProfile) -> bool`
- Decide si aplicar maker-checker split.

## EnvelopeContract

### `build_envelope(...) -> ExecutionEnvelope`
- Crea el envelope canónico de una fase/harness.

## GovernanceInterceptor

### `evaluate(intention: Intention, context: TaskContext) -> PolicyVerdict`
- Ejecuta policies en secuencia y devuelve el primer bloqueo/pausa o allow final.

### `audit(intention: Intention, verdict: PolicyVerdict, source: str) -> None`
- Registra evidencia estructurada.

## ScopePolicy

### `check(intention: Intention, context: TaskContext) -> PolicyVerdict`
- Valida scope de archivos, rutas y targets afectados.

## RiskPolicy

### `check(...) -> PolicyVerdict`
- Clasifica acciones destructivas, irreversibles o de alta criticidad.

## SecretPolicy

### `check(...) -> PolicyVerdict`
- Detecta exposición o movimiento de secretos.

## BudgetEnforcer

### `pre_call(estimated_tokens: int, context: BudgetContext) -> PolicyVerdict`
- Evalúa consumo proyectado.

### `post_call(actual_tokens: int, context: BudgetContext) -> None`
- Actualiza contadores y persiste evidencia.

### `snapshot(context: BudgetContext) -> BudgetSnapshot`
- Devuelve estado actual de task/session budget.

## EvidenceChainWriter

### `append_event(event: AuditEvent) -> None`
- Escribe un evento append-only.

### `load_session_events(session_id: str) -> list[AuditEvent]`
- Devuelve eventos de la sesión.

## ExecutionHarness

### `execute(plan: ExecutionPlan, capabilities: CapabilitySet) -> ExecutionEnvelope`
- Ejecuta trabajo y devuelve artifacts/evidence tipados.

## VerificationHarness

### `verify(result: ExecutionEnvelope, criteria: AcceptanceCriteria) -> VerificationResult`
- Valida estado logrado con checks determinísticos.

## ReviewHarness

### `review(result: ExecutionEnvelope, rubric: ReviewRubric) -> ReviewResult`
- Ejecuta maker-checker / review fresh-context.

## RecoveryHarness

### `recover(failure: FailureRecord, policy: RecoveryPolicy) -> RecoveryDecision`
- Decide retry, patch, replan o escalate.

## EvalHarnessService

### `run_scorecard(corpus_id: str, qrel_set: str) -> EvalScorecard`
- Ejecuta scorer y produce métricas.

### `compare_to_baseline(scorecard: EvalScorecard, baseline_id: str) -> EvalDiff`
- Compara con baseline versionado.

## QrelGenerationSupport

### `extract_candidates(paths: list[str]) -> list[QrelCandidate]`
- Extrae queries/respuestas candidatas.

## CapabilityRegistry

### `resolve_for_task(task: TaskProfile) -> CapabilitySet`
- Devuelve harnesses, loops, brains, skills, MCPs y verificadores recomendados.

### `register_capability(definition: CapabilityDefinition) -> None`
- Registra o actualiza una capacidad tipada.

## OvernightSupervisor

### `run(tasks: list[TaskRef], mode: str = "cautious") -> OvernightRunResult`
- Ejecuta el loop cauteloso.

### `should_continue(state: OvernightState) -> bool`
- Evalúa continuación después de cada task.

### `generate_morning_report(state: OvernightState) -> MorningReport`
- Resume ejecución nocturna.

## ResumeCheckpointStore

### `write_checkpoint(state: ResumeState) -> None`
- Persiste checkpoint de reanudación.

### `load_latest() -> ResumeState | None`
- Recupera el último checkpoint válido.
