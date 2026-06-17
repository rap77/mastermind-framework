# Memory Layer Architecture

## 1. Propósito

Definir la arquitectura objetivo de una capa de memoria propia de MasterMind que reemplace la dependencia operativa en Engram y sirva como base durable para contexto, aprendizaje, continuidad y retrieval de bajo costo.

---

## 2. Tesis central

> MasterMind debe poseer su propia memoria persistente, separando claramente runtime state, memory state y retrieval state, para reducir dependencia de terceros, bajar consumo de tokens y mejorar continuidad entre sesiones, cerebros y nichos.

---

## 3. Qué NO es esta capa

- no es solo RAG
- no es solo `project_state`
- no es solo un log de sesiones
- no es solo preferencias del usuario

La Memory Layer vive **encima** del estado canónico y **debajo** de los agentes.

---

## 4. Capas del sistema

### A. Session Context

Contexto efímero de la conversación o run actual.

### B. Runtime State

Estado estructurado y canónico de ejecución:

- proyectos
- tasks
- task_runs
- artifacts
- checkpoints
- participants
- decisions

Esto sigue viviendo principalmente en `project_state`.

### C. Memory Layer

Memoria persistente reutilizable:

- decisiones relevantes
- lessons learned
- errores comunes
- fixes exitosos
- preferencias operativas
- contexto resumido de proyectos
- conocimiento reusable por niche / brain

### D. Retrieval Layer

Mecanismos para recuperar memoria:

- búsqueda híbrida
- graph traversal
- query cache semántico
- reranking
- proyecciones de contexto

---

## 5. Componentes de la Memory Layer

### A. Memory API

Contrato único del framework:

- `save_memory_item`
- `search_memory`
- `get_memory_context`
- `save_session_summary`
- `save_preference`
- `link_memory_to_runtime`

### B. Memory Store

Persistencia primaria en Postgres.

### C. Memory Projection Jobs

Procesos que convierten señales del sistema en memoria durable.

### D. Memory Retrieval Engine

Busca y rankea items relevantes para agentes, dashboards y evaluadores.

### E. Memory Graph

Relaciones entre entidades de memoria y runtime.

---

## 6. Principios

1. MasterMind es dueño de su memoria.
2. La memoria no depende del proveedor de LLM.
3. El estado canónico y la memoria no se colapsan en una sola tabla.
4. El retrieval es una capacidad encima de la memoria, no su definición.
5. La arquitectura debe ser extensible a nuevos niches, cerebros y harnesses.
6. Cada capa debe poder operar como módulo independiente o como parte del stack completo.

---

## 7. Modularidad tipo lego

MasterMind debe diseñarse como un sistema componible.

Eso implica que estas capacidades puedan existir:

- separadas
- combinadas por pares
- o integradas en un producto completo

### Módulos base esperados

- `brains`
- `memory`
- `project_state`
- `retrieval`
- `eval_harness`
- `workflow_harness`

### Ejemplos de empaquetado futuro

- producto de memoria solamente
- producto de project/work management solamente
- producto de brains especializados por niche
- stack integrado completo para organizaciones

### Regla de diseño

Cada módulo debe exponer:

- contrato claro
- límites claros
- dependencias explícitas
- modo standalone y modo integrado

---

## 8. Escalabilidad y extensibilidad

La capa debe soportar crecimiento en tres ejes:

### A. Nuevos niches

Ejemplos futuros:

- finanzas / inversiones
- marketing / digital
- ventas
- legal
- research

Cada niche podrá introducir:

- nuevos tipos de memoria
- nuevas entidades
- nuevas relaciones
- nuevas reglas de retrieval

### B. Nuevos cerebros

Cada brain debe poder:

- tener su propio scope de memoria
- consultar memoria compartida y memoria específica
- publicar nueva memoria derivada de su trabajo

### C. Nuevos harnesses / workflows

La memoria no debe depender de un solo flujo.

Debe poder alimentar:

- MM-Flow
- War Room
- runners batch
- evaluadores
- futuros orchestrators por niche

---

## 9. Resultado esperado

Permitir que MasterMind responda con poco contexto bruto:

- qué sabemos ya
- qué aprendimos antes
- qué errores no debemos repetir
- qué evidencia respalda una decisión
- qué memoria aplica a este niche, brain y proyecto

## Key Learnings:

1. La Memory Layer debe ser una capacidad propia del framework, no un adaptador permanente a una memoria externa.
2. `project_state` y memoria persistente cumplen funciones distintas y deben seguir separadas.
3. La extensibilidad por niche, brain y harness debe ser un requisito fundacional, no un parche posterior.
4. La arquitectura objetivo debe permitir comercializar módulos aislados o combinados sin rediseñar el sistema.
