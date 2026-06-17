# Memory Taxonomy and Routing

## 1. Propósito

Definir qué tipos de información existen en MasterMind, a qué capa pertenecen y cómo deben rutearse para evitar mezclar sesión, runtime, memoria persistente y conocimiento.

---

## 2. Tesis central

> El principal error de un sistema con memoria es guardar todo en el mismo lugar. La taxonomía correcta reduce ruido, baja costo de retrieval y evita contaminación de contexto.

---

## 3. Capas de destino

### A. Session Context

Va aquí:

- lo dicho en la conversación actual
- el subtask en curso
- el estado inmediato de ejecución

No se persiste como memoria durable salvo resumen posterior.

### B. Runtime State (`project_state`)

Va aquí:

- tasks
- task_runs
- artifacts
- checkpoints
- participants
- token usage
- decisiones runtime ligadas a ejecución

### C. Agent Operational Memory

Va aquí:

- preferencias del usuario
- estilo de respuesta
- restricciones operativas
- reglas locales del repo
- convenciones de trabajo

### D. Project Memory

Va aquí:

- decisiones relevantes del proyecto
- lessons learned
- incidentes
- fixes
- riesgos recurrentes
- resúmenes de sesiones

### E. Knowledge Memory

Va aquí:

- doctrina
- fuentes expertas destiladas
- playbooks
- patrones por niche
- heurísticas de brain

---

## 4. Tipos mínimos de memoria

### Tipos base

- `decision`
- `lesson`
- `incident`
- `fix`
- `pattern`
- `preference`
- `project_summary`
- `knowledge_note`
- `brain_feedback`
- `artifact_summary`

### Tipos por niche

La taxonomía debe permitir agregar tipos nuevos sin rediseñar el sistema.

Ejemplos:

#### Finanzas / inversiones
- `investment_thesis`
- `portfolio_observation`
- `risk_signal`
- `market_note`

#### Marketing / digital
- `campaign_learning`
- `channel_pattern`
- `audience_insight`
- `creative_postmortem`

---

## 5. Routing rules

### Regla 1

Si describe una ejecución viva, va a `project_state`.

### Regla 2

Si describe cómo debe operar el agente, va a operational memory.

### Regla 3

Si captura aprendizaje reusable o histórico, va a project/knowledge memory.

### Regla 4

Si el contenido es solo recuperación contextual para un prompt, eso es retrieval, no storage.

---

## 6. Dimensiones de scoping

Todo memory item debe poder scoping por:

- `project_id`
- `brain_id` opcional
- `niche`
- `memory_type`
- `visibility`
- `source_kind`

### Visibility mínima

- `private`
- `project`
- `org`
- `global`

---

## 7. Routing extensible por niche

Cada niche debe poder declarar:

- entidades propias
- tipos de memoria propios
- reglas de extracción propias
- boosts de retrieval propios
- harnesses que consumen esa memoria

Además, cada niche debe poder vivir como módulo independiente para futuros productos:

- memoria de inversiones
- memoria de marketing
- memoria de software delivery

sin obligar a desplegar todo MasterMind completo.

Ejemplo:

un niche de inversiones puede priorizar:

- trayectoria temporal
- señales de riesgo
- cambios de tesis

mientras marketing puede priorizar:

- campañas previas
- learnings por canal
- patrones de audiencia

---

## 8. Modularidad comercial

La taxonomía debe permitir empaquetar memoria por capability:

- memory core común
- packs de tipos por niche
- packs de routing por niche
- packs de retrieval por niche

Así, nuevos productos pueden compartir el core y diferenciarse por:

- entidades
- reglas
- score boosts
- evaluaciones

---

## 9. Resultado esperado

Que un agente sepa automáticamente:

- qué guardar
- dónde guardarlo
- con qué visibilidad
- qué retrieval usar luego

## Key Learnings:

1. La taxonomía de memoria debe separar claramente estado, preferencias, aprendizaje y conocimiento.
2. Los nuevos niches deben extender tipos y reglas de routing sin romper la base común.
3. El scoping por proyecto, brain, niche y visibilidad es obligatorio para que la memoria siga siendo útil al escalar.
4. La taxonomía también debe servir como base de empaquetado comercial por capability o por niche.
