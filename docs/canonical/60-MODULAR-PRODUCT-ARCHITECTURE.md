# Modular Product Architecture

## 1. Propósito

Definir a MasterMind como una arquitectura modular y componible, donde cada capa principal pueda operar como producto independiente o como parte del stack completo.

---

## 2. Tesis central

> MasterMind no debe construirse como una única aplicación inseparable. Debe diseñarse como un sistema tipo lego, donde memoria, cerebros, retrieval, project management y harnesses puedan usarse juntos o por separado.

---

## 3. Por qué importa

Este principio habilita:

- menor acoplamiento interno
- adopción gradual por clientes o proyectos
- empaquetado comercial por capability
- extensibilidad por niche
- evolución independiente de módulos

---

## 4. Módulos estratégicos

## A. Brain Layer

Responsable de:

- especialización por brain
- prompts/sistemas por dominio
- routing de trabajo cognitivo
- evaluadores y brains auxiliares

Puede venderse o desplegarse como:

- pack de cerebros por niche
- motor experto de razonamiento

## B. Memory Layer

Responsable de:

- memoria persistente
- lessons learned
- incidentes
- decisiones
- conocimiento reusable
- preferencias y contexto operativo

Puede venderse o desplegarse como:

- memoria organizacional
- memoria de proyectos
- memoria por niche

## C. Retrieval Layer

Responsable de:

- hybrid search
- graph-aware retrieval
- semantic query cache
- evidence contract
- context projection

Puede venderse o desplegarse como:

- motor de retrieval contextual
- retrieval as a service para otros módulos

## D. Project State Layer

Responsable de:

- tasks
- task_runs
- artifacts
- checkpoints
- decisions runtime
- participants

Puede venderse o desplegarse como:

- project / execution management core
- operational state backend

## E. Workflow Harness Layer

Responsable de:

- MM-Flow
- objective lifecycle
- gates
- gap registry
- orchestración de trabajo

Puede venderse o desplegarse como:

- harness operativo para agentes
- workflow engine para proyectos asistidos por IA

## F. Eval Harness Layer

Responsable de:

- scorecards
- qrels
- benchmarks
- regression gates
- source isolation tests

Puede venderse o desplegarse como:

- quality harness para memory/retrieval/agents
- sistema de certificación interna de capacidades

---

## 5. Reglas de modularidad

### Regla 1

Cada módulo debe tener contrato explícito.

### Regla 2

Cada módulo debe poder ejecutarse sin depender de todos los demás.

### Regla 3

Las dependencias entre módulos deben ser:

- explícitas
- pequeñas
- reemplazables

### Regla 4

Los módulos no deben compartir tablas, modelos o APIs implícitamente.

### Regla 5

Los niches deben extender módulos existentes mediante packs, no forks del core.

---

## 6. Modo standalone vs integrado

## Standalone

Ejemplos:

- solo memoria
- solo retrieval
- solo project_state
- solo eval harness

## Integrado

Ejemplos:

- brains + memory
- memory + retrieval + eval
- project_state + workflow harness
- stack completo MasterMind

---

## 7. Producto base y product packs

## Core platform

El core debe incluir:

- contratos
- modelos compartidos mínimos
- auth/scoping
- observabilidad
- capability registry

## Packs

Los packs agregan especialización:

- niche packs
- brain packs
- retrieval packs
- workflow packs
- eval packs

Ejemplos:

### Niche pack: Inversiones

- entidades financieras
- investment memory taxonomy
- graph relations de portafolio
- evaluaciones de tesis/riesgo

### Niche pack: Marketing

- campaign entities
- audience memory taxonomy
- channel performance graph
- workflow pack de campañas

---

## 8. Contratos recomendados

Cada módulo debería tender a exponer algo como:

- `BrainAPI`
- `MemoryAPI`
- `RetrievalAPI`
- `ProjectStateAPI`
- `WorkflowHarnessAPI`
- `EvalHarnessAPI`

Con eso:

- un producto puede consumir otro
- un cliente puede comprar una parte
- un niche puede extender una capability sin romper el resto

---

## 9. Relación con nuevos niches

Los nuevos niches no deben requerir rediseñar el framework.

Deben poder agregar:

- nuevas entidades
- nuevos memory types
- nuevos boosts de retrieval
- nuevos graphs
- nuevos workflows
- nuevos benchmarks

mediante packs y registros, no mediante hardcode masivo.

---

## 10. Implicación para la implementación actual

Desde ahora, cualquier cambio grande debería evaluarse preguntando:

1. ¿a qué módulo pertenece?
2. ¿qué contrato expone?
3. ¿puede vivir standalone?
4. ¿qué packs lo extenderán en futuros niches?
5. ¿qué parte es core y qué parte es specialization?

---

## 11. Resultado esperado

Que MasterMind pueda evolucionar hacia:

- un framework completo
- una familia de productos
- un set de módulos reutilizables
- una plataforma extensible por niche y por capability

sin rehacer la arquitectura cada vez.

## Key Learnings:

1. El principio lego debe aplicarse al framework completo, no solo a la memoria.
2. La comercialización futura depende de contratos modulares claros entre brains, memory, retrieval, project_state, workflows y evals.
3. Los nuevos niches deben llegar como packs sobre módulos existentes, no como forks del core.
