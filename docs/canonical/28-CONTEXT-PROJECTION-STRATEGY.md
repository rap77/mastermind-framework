# Context Projection Strategy

## 1. Propósito

Definir cómo MasterMind construye contexto útil, compacto y actualizado para agentes y humanos a partir del estado estructurado del proyecto.

---

## 2. Tesis central

> Los agentes no deberían reconstruir el contexto leyendo archivos dispersos o arrastrando historiales largos; deberían recibir una proyección contextual generada desde la fuente de verdad del proyecto.

---

## 3. Qué es una Context Projection

Es una vista derivada, normalmente en JSON, que reúne solo el contexto necesario para una tarea, run o decisión.

Debe combinar:

- estado actual
- artefactos relevantes
- decisiones críticas
- checkpoint vigente
- doctrina aplicable
- restricciones activas
- siguiente paso

---

## 4. Tipos de proyección

### A. Task Context Projection

Para ejecutar una tarea concreta.

Incluye:
- objetivo
- estado
- dependencias
- blockers
- criteria
- next step

### B. Run Context Projection

Para una ejecución activa.

Incluye:
- policy activa
- backend actual
- checkpoint actual
- switches relevantes
- budget de contexto

### C. Decision Context Projection

Para debatir o registrar una decisión.

Incluye:
- problem statement
- opciones
- constraints
- decisiones previas relacionadas
- brains participantes

### D. Human Review Projection

Para UI/dashboard humano.

Incluye:
- resumen
- estado actual
- bloqueos
- tareas activas
- costos/tiempo
- next actions

---

## 5. Componentes de la proyección

### 1. Core Identity
- project_id
- task_id o run_id
- current actor
- timestamp

### 2. Objective Layer
- objetivo actual
- definición de done
- criterio de éxito

### 3. State Layer
- status
- blockers
- dependencies
- active step

### 4. Decision Layer
- decisiones críticas vigentes
- objeciones abiertas
- vetos o gates

### 5. Doctrine Layer
- reglas obligatorias
- metodología activa
- restricciones de arquitectura

### 6. Artifact Layer
- specs relevantes
- tasks relacionadas
- validations/reviews relevantes

### 7. Continuity Layer
- último checkpoint
- next step
- open questions

---

## 6. Reglas de construcción

### Regla 1
Incluir solo lo relevante al scope actual.

### Regla 2
Priorizar estado estructurado y artefactos antes que transcript bruto.

### Regla 3
Siempre incluir next step claro.

### Regla 4
Separar contexto obligatorio de contexto opcional.

### Regla 5
La doctrina aplicable debe entrar junto al contexto.

---

## 7. Capas de prioridad

### Nivel 1 — Mandatory
- objetivo
- estado actual
- checkpoint
- reglas obligatorias
- siguiente paso

### Nivel 2 — Decision critical
- decisiones relacionadas
- blockers
- constraints
- criterios de completitud

### Nivel 3 — Supporting
- historial corto útil
- artefactos secundarios
- notas relevantes

### Nivel 4 — Nice to have
- historial largo
- referencias menos inmediatas

---

## 8. Relación con context windows

La proyección debe poder adaptarse según el budget disponible del backend.

### Si sobra budget
se agrega supporting context.

### Si falta budget
se preserva mandatory + decision critical y se resume el resto.

---

## 9. Relación con Doctrine Projection

La Context Projection no debe venir sola.

Cada ejecución importante debería recibir:

- `context_projection`
- `doctrine_projection`

A veces pueden viajar juntas como una sola estructura de trabajo.

---

## 10. Ejemplo de forma JSON simplificada

```json
{
  "project": {
    "project_id": "mastermind",
    "adapter_id": "finance-trading-pilot"
  },
  "task": {
    "task_id": "task-f2-expert-pack",
    "objective": "Refinar el expert pack de F2",
    "status": "in_progress",
    "next_step": "Validar cobertura anti-overfitting"
  },
  "state": {
    "blockers": [],
    "dependencies": ["task-finance-team-specs"],
    "checkpoint_id": "chk-099"
  },
  "decisions": [
    "Finance se trata como niche team, no como brain único"
  ],
  "doctrine": {
    "methodology": "SDD",
    "mandatory_rules": [
      "Expert pack debe justificar cobertura y gaps"
    ]
  },
  "artifacts": [
    "F2-QUANT-RESEARCH-BRAIN-SPEC.md",
    "03-FINANCE-TEAM-INTERACTION-PROTOCOL.md"
  ]
}
```

---

## 11. Principios

1. La proyección debe ser legible por modelo y por humano.
2. El contexto debe ser derivado, no improvisado.
3. El sistema debe poder regenerarlo en cualquier momento.
4. Debe reducir consumo de tokens sin perder continuidad crítica.

---

## 12. Beneficios

- menor dependencia de historial largo
- mejor switching entre modelos
- mejor continuidad tras pausas
- menos consumo de tokens
- mejor trazabilidad de qué contexto influyó en qué output

---

## 13. Próximos artefactos recomendados

1. `29-INITIAL-POSTGRES-SCHEMA-SLICE.md`
2. `30-DASHBOARD-INFORMATION-ARCHITECTURE.md`
3. `31-DOCTRINE-PROJECTION-FORMAT.md`

## Key Learnings:

1. El contexto útil debe generarse desde estado estructurado, no reensamblarse manualmente desde archivos dispersos.
2. La proyección debe combinar estado, decisiones, artefactos, checkpoint y doctrina.
3. La calidad del runtime multi-modelo depende mucho de la calidad de estas proyecciones.
