# Services

## 1. Loop Selection Service

### Role
Servicio que decide qué loop y qué grado de control necesita cada tarea.

### Orchestration Pattern
1. recibe brief + contexto + intención
2. clasifica complejidad, riesgo y verificabilidad
3. selecciona loop base
4. añade verification/review/recovery loops cuando corresponda
5. devuelve política de ejecución al orquestador

## 2. Capability Resolution Service

### Role
Servicio que consulta el `CapabilityRegistry` para seleccionar capacidades útiles
según objetivo y constraints.

### Orchestration Pattern
1. recibe tipo de tarea
2. filtra capabilities incompatibles o de alto costo innecesario
3. prioriza harnesses, brains, skills, MCPs y verificadores
4. devuelve set mínimo útil

## 3. Governance Service

### Role
Servicio lógico que reúne `GovernanceInterceptor`, `PolicySet`, `BudgetEnforcer` y `EvidenceChainWriter`.

### Orchestration Pattern
1. Construye `Intention`
2. Ejecuta policies en orden
3. Evalúa budget proyectado
4. Persiste evidencia
5. Devuelve veredicto al `CoordinatorAdapter`

## 4. Execution Service

### Role
Servicio que orquesta trabajo ejecutable sobre código/artefactos usando el
Execution Harness.

### Orchestration Pattern
1. recibe loop policy + capabilities seleccionadas
2. ejecuta trabajo
3. persiste artifacts y envelope
4. delega a verification/review según policy

## 5. Verification Service

### Role
Servicio que materializa verification loops y criterios de aceptación.

### Orchestration Pattern
1. recibe artifacts/resultados
2. ejecuta checks determinísticos
3. compara contra acceptance criteria
4. devuelve pass/fail + evidence

## 6. Review Service

### Role
Servicio independiente para maker-checker split.

### Orchestration Pattern
1. recibe artifacts y contexto resumido
2. realiza review fresh-context o adversarial
3. produce findings y decisión
4. bloquea o aprueba continuidad

## 7. Recovery Service

### Role
Servicio que aplica recovery loops bounded.

### Orchestration Pattern
1. clasifica fallo
2. intenta local retry si aplica
3. intenta local patch si aplica
4. pide replan si el fallo es estructural
5. escala a humano si supera límites

## 8. Evaluation Service

### Role
Servicio responsable del ciclo de evaluación offline.

### Orchestration Pattern
1. Carga corpus estable
2. Carga qrels sellados
3. Ejecuta scorer
4. Produce scorecard JSON
5. Compara contra baseline y devuelve pass/fail

## 9. Meta-loop Analysis Service

### Role
Servicio analítico ligero que consume audit trail + métricas y genera propuestas.

### Orchestration Pattern
1. Revisa eventos post-sesión
2. Detecta patrones repetidos
3. Clasifica propuesta como menor o de gobernanza crítica
4. Dispara regression tests si aplica
5. Escala a humano cuando corresponde

## 10. Overnight Execution Service

### Role
Servicio coordinador del modo nocturno cauteloso.

### Orchestration Pattern
1. Selecciona tarea
2. Pide veredicto a governance
3. Ejecuta tarea
4. Escribe checkpoint
5. Reevalúa continuidad
6. Genera morning report al finalizar

## 11. Persistence Service

### Role
Unifica accesso a JSON Lines MVP y futura migración a PostgreSQL.

### Orchestration Pattern
- interfaz estable de append/load/list
- implementación inicial file-based
- backend futuro PostgreSQL sin romper consumidores
