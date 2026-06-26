# MasterMind Core Architecture

## 1. Propósito

Definir la base de MasterMind como sistema de **orquestación, planificación y ejecución de desarrollo** para múltiples nichos, cerebros especializados y workflows intercambiables.

## 2. Tesis central

> MasterMind no debe casarse con un solo workflow. Debe operar como un orquestador que selecciona el harness y el loop mínimo suficiente para cada objetivo.

## 3. Qué es MasterMind

MasterMind es:

- un sistema para crear y operar cerebros especializados por nicho
- un orquestador de trabajo técnico y de producto
- un runtime de desarrollo con memoria propia
- una biblioteca de harnesses y loops reutilizables
- una capa de trazabilidad, verificación y recovery

## 4. Qué no es MasterMind

- no es un agente genérico de conversación
- no es un único workflow obligatorio
- no es una memoria volátil de chat
- no es una copia completa de Hermes, ECC o AI-DLC
- no es una sola metodología de desarrollo

## 5. Misión del sistema

- Crear y operar cerebros especializados por nicho.
- Ejecutar desarrollo con control explícito, memoria propia y trazabilidad.
- Reducir consumo de tokens por contexto, entrada y salida.
- Reusar patrones, fuentes y decisiones sin perder continuidad.
- Mantener seguridad, auditabilidad y recovery.
- Permitir elegir el harness correcto según el objetivo.

## 6. Principios de diseño

- **Specialized brains first**: el valor está en cerebros por dominio, no en un agente genérico.
- **Harness selection over one-size-fits-all**: cada tarea elige el workflow apropiado.
- **Minimum sufficient control**: usar el nivel mínimo de control que la tarea requiere.
- **Deterministic edges**: decisiones críticas y límites se resuelven con reglas, no con prosa libre.
- **Memory by retrieval, not by dumping**: traer solo lo necesario al contexto.
- **Evidence over persuasion**: cada resultado importante debe dejar artefactos verificables.
- **Source-aware evolution**: toda fuente externa debe quedar versionada y evaluada.

## 7. Componentes nucleares

### A. Brain Layer

Especialistas por nicho y por función:

- estrategia de producto
- UX
- UI
- backend
- QA
- growth/data
- finanzas e inversiones
- marketing digital
- otros nichos futuros

### B. Harness Layer

Conjuntos de reglas, etapas y artefactos para ejecutar un tipo de trabajo.

### C. Loop Layer

Control iterativo: discovery, verification, review, recovery, heartbeat, etc.

### D. Memory Layer

Persistencia operacional y semántica en Postgres, con recuperación contextual bajo demanda.

### E. Capability Registry

Inventario consultable de brains, harnesses, loops, skills, MCPs, policies y verificadores.

### F. Source Registry

Inventario de fuentes externas, snapshots, deltas y decisiones de adopción.

## 8. Flujo operativo estándar

1. Se detecta el objetivo.
2. Se consulta el registry de capacidades.
3. Se selecciona el harness y el loop mínimo suficiente.
4. Se carga contexto desde memoria con filtros y resúmenes.
5. Se ejecuta.
6. Se verifica.
7. Se guarda aprendizaje/decisión.
8. Se archiva el resultado.

## 9. Criterios de selección

La selección debe considerar:

- complejidad
- riesgo
- verificabilidad
- costo de tokens
- necesidad de checker separado
- necesidad de MCP
- necesidad de memoria histórica
- valor de reuso posterior

## 10. Relación con AI-DLC

AI-DLC no reemplaza la arquitectura de MasterMind.
AI-DLC será uno de los harnesses del sistema, útil para discovery, requirements, design, construction, verification y archive.

## 11. Relación con Postgres, vectores y grafos

Postgres será la memoria operativa primaria.
pgvector u otra extensión vectorial podrá usarse para recuperación semántica.
Un grafo derivado puede añadirse después para navegación de relaciones y causalidad.

## 12. Primeros documentos dependientes

- `64-HARNESS-LIBRARY-AND-LOOP-TAXONOMY.md`
- `65-MEMORY-AND-CONTEXT-ARCHITECTURE.md`
- `66-SOURCE-REGISTRY-AND-DELTA-PROTOCOL.md`
