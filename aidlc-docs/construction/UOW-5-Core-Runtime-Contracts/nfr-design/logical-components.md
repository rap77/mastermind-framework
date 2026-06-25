# Logical Components — UOW-5 Core Runtime Contracts

## Purpose

Definir los componentes lógicos mínimos que implementan los patrones NFR de
UOW-5 sin introducir infraestructura externa adicional en el MVP.

## 1. TaskProfileClassifier

### Responsibility
Normalizar la tarea en un `TaskProfile` consumible por selección.

### Inputs
- task request
- execution intent
- policy hints

### Outputs
- `TaskProfile`
- classification reasons

## 2. CapabilityRegistry

### Responsibility
Resolver el inventario tipado disponible para la tarea actual.

### Inputs
- registry definitions
- active environment
- task profile

### Outputs
- candidate capabilities
- filtered capabilities

## 3. HarnessRegistry

### Responsibility
Exponer harnesses soportados y sus restricciones/contratos.

### Inputs
- harness definitions
- compatibility constraints

### Outputs
- compatible harness set

## 4. LoopSelector

### Responsibility
Elegir `LoopPolicy` usando mínimo control suficiente.

### Inputs
- `TaskProfile`
- filtered capabilities
- compatible harnesses

### Outputs
- `LoopPolicy`
- selection rationale

## 5. EnvelopeContractValidator

### Responsibility
Validar que todo outcome relevante tenga shape estable antes de continuar.

### Inputs
- `ExecutionEnvelope`
- active loop policy

### Outputs
- valid/invalid verdict
- contract violations

## 6. ExecutionHarness

### Responsibility
Ejecutar el trabajo principal bajo la policy seleccionada.

### Inputs
- task payload
- `TaskProfile`
- `LoopPolicy`
- selected capabilities

### Outputs
- `ExecutionEnvelope`

## 7. VerificationHarness

### Responsibility
Aplicar validaciones estructuradas cuando la policy lo exija.

### Inputs
- execution envelope
- acceptance criteria
- verifier capabilities

### Outputs
- `VerificationPayload`
- updated `ExecutionEnvelope`

## 8. ReviewHarness

### Responsibility
Realizar maker-checker independiente para cambios no triviales o subjetivos.

### Inputs
- execution envelope
- review criteria
- reviewer capabilities

### Outputs
- review verdict
- risks / change requests
- updated `ExecutionEnvelope`

## 9. RecoveryHarness

### Responsibility
Aplicar la escalera bounded de recuperación.

### Inputs
- failed/warning envelope
- recovery policy
- attempt history

### Outputs
- `RecoveryDecision`
- updated loop policy when allowed

## 10. ContinuitySnapshotWriter

### Responsibility
Persistir el mínimo estado necesario para reanudar la tarea.

### Inputs
- task profile
- loop policy
- execution envelope
- artifact refs

### Outputs
- resumable snapshot refs

## Interaction Shape

`TaskProfileClassifier`
-> `CapabilityRegistry`
-> `HarnessRegistry`
-> `LoopSelector`
-> `ExecutionHarness`
-> (`VerificationHarness` / `ReviewHarness` when required)
-> `RecoveryHarness` when needed
-> `ContinuitySnapshotWriter`

## MVP Boundary

- No requiere nuevos servicios remotos.
- No requiere scheduler global ni HUD operatorio.
- No requiere paridad total entre todos los harnesses.
- Sí requiere contratos tipados, selección determinista y continuidad
  persistida.
