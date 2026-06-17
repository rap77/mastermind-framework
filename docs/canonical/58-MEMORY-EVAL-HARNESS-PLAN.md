# Memory Eval Harness Plan

## 1. Propósito

Definir una disciplina de evaluación para la futura Memory Layer de MasterMind inspirada en BrainBench / gbrain-evals, de forma que los cambios en memoria y retrieval se puedan medir y no degraden silenciosamente.

---

## 2. Tesis central

> Una capa de memoria sin harness de evaluación termina optimizada por intuición. MasterMind necesita scorecards, qrels sellados y gates de regresión para confiar en su memoria.

---

## 3. Qué debe medir el harness

### A. Retrieval quality

- recall@k
- precision@k
- MRR
- nDCG

### B. Temporal correctness

- respuestas “as of”
- cambios de estado
- trayectoria correcta

### C. Provenance

- cita correcta
- evidencia correcta
- grounding suficiente

### D. Source isolation

- no filtración entre proyectos
- no filtración entre niches
- no filtración entre ámbitos privados y compartidos

### E. Learning reuse

- capacidad de reutilizar lessons/fixes previos
- reducción de errores repetidos

### F. Token efficiency

- tamaño de contexto recuperado
- costo de retrieval
- ahorro vs contexto manual/cold

---

## 4. Artefactos mínimos del harness

### A. Qrels sellados

Conjuntos de consultas y resultados esperados que el sistema bajo prueba no debe ver.

### B. Baselines versionados

Snapshots de retrieval y scorecards por versión.

### C. Evidence contract

Resumen estructurado para jueces automáticos, no tool traces crudos.

### D. Scorecards

Resultados comparables entre versiones y configuraciones.

---

## 5. Suites recomendadas

### Suite 1 — Project memory retrieval

Preguntas sobre:

- decisiones previas
- fixes previos
- incidentes previos
- artifacts relacionados

### Suite 2 — Temporal project evolution

Preguntas sobre:

- cómo cambió un proyecto
- qué pasó antes/después
- cuál decisión sustituyó a otra

### Suite 3 — Niche memory

Preguntas especializadas por niche:

- inversiones
- marketing
- software

### Suite 4 — Source isolation

Pruebas negativas:

- el proyecto A no debe ver memoria del B
- un niche no debe contaminar otro sin permiso

### Suite 5 — Think vs search

Comparar:

- solo búsqueda
- búsqueda + síntesis

---

## 6. Jueces

### Regla

Cuando sea posible:

- usar scoring determinista primero
- usar LLM judge solo donde haga falta

### Donde sí conviene LLM judge

- utilidad de síntesis
- groundedness
- calidad de citas
- comparación think vs search

---

## 7. Gates mínimos

Antes de cambiar la Memory Layer:

1. no bajar recall por debajo del baseline acordado
2. no empeorar aislamiento
3. no empeorar citation accuracy
4. no aumentar tokens sin mejora clara de calidad

---

## 8. Extensibilidad

Cada niche nuevo debe poder agregar:

- qrels propios
- corpora sintéticos
- probes temporales
- pruebas de aislamiento
- scorecards propios

Cada nuevo harness o workflow debe poder declarar:

- qué herramientas de memoria usa
- qué expectativas de grounding tiene
- qué suite lo valida

---

## 9. Resultado esperado

Que la memoria de MasterMind evolucione con:

- números comparables
- regresiones detectables
- evidencia pública dentro del repo
- confianza para escalar a nuevos niches y cerebros

## Key Learnings:

1. La evaluación de memoria debe cubrir más que recall: tiempo, aislamiento, citas y eficiencia.
2. Los qrels sellados y los baselines versionados son defensas clave contra autoengaño y regresiones silenciosas.
3. Cada niche y workflow futuro debe entrar al sistema con su propia superficie de evaluación.
