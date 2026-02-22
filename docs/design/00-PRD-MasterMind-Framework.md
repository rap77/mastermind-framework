# MasterMind Framework — PRD (Product Requirements Document)

**Versión:** 1.0
**Fecha:** Febrero 2026
**Nicho Inicial:** Desarrollo de Software
**Fase:** 1 — Diseño Arquitectónico
**Clasificación:** Confidencial — Uso Interno

---

## 1. Visión del Producto

MasterMind Framework es una **arquitectura cognitiva modular** que permite crear Cerebros Especializados por nicho. Cada cerebro es un repositorio de conocimiento estructurado, alimentado con el saber destilado de los expertos más reconocidos mundialmente, diseñado para ser consultado por agentes autónomos o equipos de agentes que resuelven problemas reales con criterio profesional.

**No son asistentes obedientes. Son expertos capaces de cuestionar, corregir, decir NO, y pedir más información.**

---

## 2. Problema que Resuelve

Hoy cualquiera puede darle un prompt a una IA y pedirle que "cree un software" o "haga un plan de marketing". El resultado es genérico, superficial, y sin criterio profesional.

MasterMind Framework resuelve esto creando un **equipo digital de expertos** donde cada cerebro:

- Tiene conocimiento destilado de los mejores del mundo en su disciplina
- Opera con criterios de decisión profesionales, no solo información
- Puede rechazar inputs incompletos o incoherentes
- Se comunica con otros cerebros bajo protocolos claros
- Es evaluado por un meta-cerebro que impide que el sistema se autoengañe

---

## 3. Arquitectura de Alto Nivel

### 3.1 Las 3 Capas del Sistema

| Capa | Función | Tecnología Fase 1 | Tecnología Futura |
|------|---------|-------------------|-------------------|
| **Repositorio Semántico** | Almacena conocimiento destilado por cerebro | NotebookLM (vía MCP) | RAG profesional propio (ChromaDB/Qdrant + LangChain) |
| **Puente de Consulta** | Conecta agentes con repositorios | MCP Server (notebooklm-mcp-cli) | API RAG propia |
| **Agentes Especializados** | Ejecutan tareas con criterio experto | Claude Code (subagents + skills) | Multi-agent orchestration framework |

### 3.2 Flujo de Ejecución

```
Brief del CEO/Usuario
    ↓
Orquestador Central (decide qué cerebro(s) intervienen)
    ↓
Cerebro Asignado consulta NotebookLM vía MCP
    ↓
Procesa con system prompt experto + criterios de decisión
    ↓
Cerebro #7 (Growth/Data) evalúa en TIEMPO REAL cada paso
    ↓
Output validado → siguiente cerebro o entrega final
    ↓
Si falla validación → iteración automática
```

### 3.3 NotebookLM vs RAG Profesional — Ruta de Migración

**¿Por qué empezar con NotebookLM?**

- Ya está funcionando en tu entorno WSL vía MCP
- Cero configuración de embeddings, chunking, o infraestructura
- Permite generar audios, videos, infografías, mapas mentales
- Suficiente para Fase 1 con pocos cerebros

**¿Por qué migrar a RAG propio en el futuro?**

| Aspecto | NotebookLM | RAG Profesional |
|---------|-----------|-----------------|
| Control del chunking | Ninguno | Total (por tokens, semántico, por sección) |
| Metadata filtering | Básico | Avanzado (filtrar por experto, habilidad, tipo) |
| Cross-notebook queries | No soportado | Consulta multi-cerebro simultánea |
| Fine-tuning retrieval | No | Ajustar relevancia, re-ranking, HyDE |
| Versionado de conocimiento | Manual | Automático con timestamps y diffs |
| Independencia | Depende de Google | 100% propio |
| Escalabilidad | ~50 fuentes por cuaderno | Ilimitado |

**Estrategia:** Diseñar las Fichas de Fuentes Maestras en formato portable (Markdown + YAML front matter) que sirvan tanto para NotebookLM hoy como para ingestión en RAG futuro.

---

## 4. Orden de los Cerebros (Flujo Estándar de Desarrollo de Software)

El flujo sigue el ciclo real de creación de producto. No es una línea recta, es un ciclo donde el Cerebro #7 retroalimenta a todos:

| # | Cerebro | Rol | Pregunta que Responde |
|---|---------|-----|----------------------|
| 1 | **Product Strategy** | Define QUÉ y POR QUÉ | ¿Qué construimos y para quién? |
| 2 | **UX Research & Strategy** | Define la EXPERIENCIA | ¿Cómo debe sentirse y funcionar? |
| 3 | **UI Design** | Define lo VISUAL | ¿Cómo se ve y se comunica? |
| 4 | **Frontend Architecture** | CONSTRUYE la interfaz | ¿Cómo interactúa el usuario? |
| 5 | **Backend & Systems** | CONSTRUYE la lógica | ¿Cómo funciona internamente? |
| 6 | **QA & DevOps** | GARANTIZA estabilidad | ¿Cómo se mantiene vivo y sano? |
| 7 | **Growth & Data** | EVOLUCIONA todo (meta-cerebro en tiempo real) | ¿Está funcionando? ¿Qué mejoramos? |

**Complementos transversales (no son cerebros del flujo, son infraestructura):**

- **Orquestador Central:** Asigna, prioriza, evalúa, activa iteraciones
- **Evaluador Crítico:** Poder de veto independiente sobre cualquier output

---

## 5. Formato Estándar de Cada Cerebro

Cada cerebro se compone de los siguientes documentos (detallados en el archivo `01-Plantilla-Cerebro.md`):

| Archivo | Propósito |
|---------|-----------|
| `README.md` | Índice: visión, alcance, dependencias, escenarios de activación |
| `brain-spec.yaml` | Definición formal: 5 capas, inputs/outputs, criterios, autoridad |
| `knowledge-map.md` | Mapa de habilidades requeridas → expertos → fuentes asignadas |
| `experts-directory.md` | Fichas biográficas de cada experto con justificación de selección |
| `master-sources.md` | Índice de todas las fuentes maestras con metadata bibliográfica |
| `sources/FUENTE-001-titulo.md` | Ficha individual por fuente (conocimiento destilado) |
| `use-cases.md` | Escenarios de activación y casos de uso concretos |
| `evaluation-criteria.md` | Cómo se mide la calidad del output |
| `notebook-config.json` | Mapeo técnico al NotebookLM (notebook_id, source_ids) |

---

## 6. Las 5 Capas de Cada Cerebro

Cada cerebro se estructura internamente con 5 capas cognitivas que van de lo teórico a lo operativo:

1. **Base Conceptual:** Principios fundamentales del dominio. Es el "por qué" profundo.
2. **Frameworks Operativos:** Métodos y herramientas prácticas. Es el "cómo" estructurado.
3. **Modelos Mentales:** Formas de pensar y analizar. Es la "lente" con la que ve el mundo.
4. **Criterios de Decisión:** Cómo resolver trade-offs profesionales. Es lo que separa un experto de un asistente.
5. **Mecanismo de Retroalimentación:** Cómo mide y mejora su propio desempeño. Es lo que permite evolución.

---

## 7. Diseño del Orquestador Central

### 7.1 Qué es

El Orquestador no es un cerebro más. Es el **sistema nervioso central** que decide:

- Qué cerebro interviene ante cada tarea
- En qué orden
- Con qué prioridad
- Cuándo escalar a intervención humana
- Cuándo iterar vs avanzar

### 7.2 Cómo asigna tareas y define prioridades

```yaml
orchestrator_logic:
  input: brief_del_usuario
  steps:
    1_classify:
      action: "Analizar el brief e identificar tipo de tarea"
      categories:
        - strategy (→ Cerebro 1)
        - research_ux (→ Cerebro 2)
        - design (→ Cerebro 3)
        - build_frontend (→ Cerebro 4)
        - build_backend (→ Cerebro 5)
        - deploy_test (→ Cerebro 6)
        - optimize (→ Cerebro 7)
        - multi_phase (→ secuencia de cerebros)

    2_decompose:
      action: "Si es multi_phase, descomponer en tareas atómicas"
      output: "Lista ordenada de tareas con cerebro asignado"

    3_execute:
      action: "Invocar cerebro(s) en orden"
      rules:
        - Cada cerebro recibe input en formato estándar
        - Cerebro #7 evalúa cada output en tiempo real
        - Si #7 rechaza, el cerebro original itera
        - Si después de 3 iteraciones no pasa, escalar a humano

    4_deliver:
      action: "Consolidar outputs y entregar al usuario"
```

### 7.3 Cómo evalúa calidad

El Orquestador delega la evaluación de calidad al Cerebro #7 y al Evaluador Crítico usando estos criterios universales:

| Criterio | Pregunta | Quién evalúa |
|----------|----------|--------------|
| Coherencia | ¿Es consistente con los inputs recibidos? | Evaluador Crítico |
| Completitud | ¿Se cubren todos los aspectos requeridos? | Evaluador Crítico |
| Calidad profesional | ¿Un experto humano aprobaría esto? | Cerebro #7 |
| Viabilidad | ¿Es implementable con recursos disponibles? | Cerebro #7 |
| Alineación estratégica | ¿Contribuye a los objetivos del proyecto? | Orquestador |

### 7.4 Cómo activa interacciones entre cerebros

Cuando un cerebro necesita input de otro (ej: Frontend necesita clarificación de UX):

```
Cerebro solicitante → Orquestador (petición formal con contexto)
    ↓
Orquestador evalúa si es válida la petición
    ↓
Orquestador invoca cerebro consultado con contexto necesario
    ↓
Cerebro consultado responde con output formateado
    ↓
Orquestador entrega respuesta al solicitante
    ↓
Cerebro #7 valida la coherencia de la interacción
```

---

## 8. Diseño del Cerebro #7 como Evaluador en Tiempo Real

### 8.1 Diferencia con los otros cerebros

Los cerebros 1-6 **producen**. El Cerebro #7 **observa, cuestiona, y obliga a evolucionar**.

Está presente en cada paso del flujo, no al final. Funciona como un "observador inteligente" que:

- Recibe copia de cada output generado por cualquier cerebro
- Lo evalúa contra criterios de calidad, coherencia, y alineación
- Puede aprobar, pedir iteración, o escalar
- Detecta patrones de error recurrentes entre cerebros
- Propone optimizaciones basadas en datos acumulados

### 8.2 Cómo cuestiona outputs

```yaml
brain_7_evaluation:
  on_each_output:
    checks:
      - "¿El output responde la pregunta original o se desvió?"
      - "¿Hay suposiciones no validadas?"
      - "¿Contradice outputs anteriores de otros cerebros?"
      - "¿Hay información faltante crítica?"
      - "¿El nivel de detalle es suficiente para el siguiente cerebro?"

    possible_actions:
      APPROVE: "Output pasa al siguiente cerebro"
      REQUEST_ITERATION: "Devolver al cerebro con feedback específico"
      REQUEST_CLARIFICATION: "Pedir más información al usuario vía Orquestador"
      FLAG_CONFLICT: "Señalar contradicción con otro cerebro"
      ESCALATE: "Requiere intervención humana"
```

### 8.3 Cómo aprende y evoluciona

Cada evaluación genera un registro:

```yaml
evaluation_log:
  timestamp: "2026-02-21T14:30:00Z"
  brain_evaluated: "frontend"
  task_id: "PROJ-001-task-04"
  verdict: "REQUEST_ITERATION"
  reason: "El componente propuesto no considera el estado de error definido por UX"
  pattern_detected: "Frontend omite edge cases de UX en 3 de últimas 5 tareas"
  recommendation: "Agregar checklist de edge cases al handoff UX→Frontend"
```

Con el tiempo, estos logs permiten:
- Detectar debilidades recurrentes por cerebro
- Proponer mejoras al knowledge base
- Ajustar criterios de evaluación
- Identificar gaps en las fuentes maestras

---

## 9. Comunicación entre Cerebros y Resolución de Conflictos

### 9.1 Protocolo de Comunicación

Todo intercambio entre cerebros sigue un formato estándar:

```yaml
message:
  from: "brain_id"
  to: "brain_id"
  type: "output | request | rejection | approval"
  task_id: "referencia única"
  version: "1.0"
  content:
    summary: "Resumen ejecutivo del output"
    detail: "Contenido completo"
    assumptions: ["lista de suposiciones"]
    dependencies: ["qué necesita del cerebro siguiente"]
    confidence: "high | medium | low"
```

### 9.2 Autoridad de Cada Cerebro

| Cerebro | Puede rechazar output de | No puede rechazar output de | Poder de veto sobre |
|---------|--------------------------|----------------------------|---------------------|
| #1 Product Strategy | Ninguno (es el primero) | Ninguno | Alcance y prioridades |
| #2 UX Research | #1 si el brief es incompleto | — | Experiencia de usuario |
| #3 UI Design | #2 si la arquitectura de info es ambigua | #1 | Coherencia visual |
| #4 Frontend | #3 si el diseño no es implementable | #1, #2 | Viabilidad técnica frontend |
| #5 Backend | #4 si los requisitos de API son imposibles | #1, #2, #3 | Viabilidad técnica backend |
| #6 QA/DevOps | #4, #5 si no cumplen estándares de calidad | #1 | Estabilidad y seguridad |
| #7 Growth/Data | **TODOS** (evaluador en tiempo real) | — | Calidad y coherencia global |

### 9.3 Resolución de Conflictos de Criterio

Cuando dos cerebros discrepan:

```
Paso 1: Cerebro #7 analiza ambas posiciones
Paso 2: #7 verifica contra knowledge base de ambos cerebros
Paso 3: Si puede resolver con evidencia → emite veredicto
Paso 4: Si no puede resolver → escala al Orquestador
Paso 5: Orquestador presenta opciones al CEO/usuario con pros y contras
Paso 6: CEO decide y la decisión queda documentada como precedente
```

Los precedentes se acumulan y se convierten en **reglas de criterio** que el sistema aprende para resolver conflictos similares en el futuro sin intervención humana.

---

## 10. Stack Tecnológico

### Fase 1 (Actual)

| Componente | Tecnología |
|-----------|-----------|
| Entorno | WSL (Linux) |
| LLM Principal | Claude (vía Claude Code, suscripción) |
| Repositorio Semántico | NotebookLM |
| Puente MCP | notebooklm-mcp-cli |
| MCP adicionales | Context7, Sequential Thinking |
| Skills | Superpower, SuperClaude, Vercel best practices |
| Runtime | Node.js (vía nvm), Python (vía uv) |
| Framework web (proyecto paralelo) | Next.js 16 + React 19 |
| Control de versiones | Git |

### Fase Futura (RAG Propio)

| Componente | Tecnología Propuesta |
|-----------|---------------------|
| Vector DB | ChromaDB (local, open source) o Qdrant |
| Embeddings | OpenAI text-embedding-3-small o local con sentence-transformers |
| Orchestration | LangChain / LangGraph |
| Metadata store | SQLite o PostgreSQL |
| API | FastAPI (Python) |
| Monitoreo | LangSmith o custom logging |

---

## 11. Límites Claros de Fase 1

### SÍ se hace en Fase 1

- Diseño arquitectónico completo (este documento)
- Plantilla estándar de cerebro con todos sus archivos
- Método de selección de expertos documentado
- Proceso de destilación de fuentes definido
- Fichas de fuentes maestras para Cerebro #1 (Product Strategy) con ISBNs reales
- Estructura filesystem implementada
- System prompts para Orquestador, Evaluador, y Cerebro #1
- Casos de uso e historias de usuario para Cerebro #1
- Configuración MCP básica funcional

### NO se hace en Fase 1

- Alimentación completa de los 7 cerebros (se hará incrementalmente)
- Interfaz web o dashboard
- Multi-tenancy operativo
- RAG profesional propio (se usa NotebookLM)
- Automatización completa sin intervención humana
- Nichos adicionales (Marketing Digital, etc.)
- Métricas y analytics del sistema

---

## 12. Riesgos y Mitigación

| Riesgo | Impacto | Mitigación |
|--------|---------|------------|
| Sobre-ingeniería en Fase 1 | Alto | Límites claros. Empezar con 1 cerebro perfecto, luego replicar. |
| Cargar conocimiento sin destilar | Alto | Fichas de fuentes maestras con proceso de destilación formal. |
| Cerebros que no se comunican | Crítico | Protocolo estándar de comunicación definido desde día 1. |
| Sistema que se autoengaña | Crítico | Cerebro #7 como evaluador en tiempo real + Evaluador Crítico. |
| Dependencia de NotebookLM | Medio | Fichas portables + ruta de migración a RAG propio documentada. |
| Deuda técnica por vibe coding | Alto | Brain-spec.yaml obliga diseño antes de ejecución. |

---

## 13. Hoja de Ruta

### Fase 1A — Fundación (Semanas 1-4)

1. Implementar estructura filesystem completa
2. Crear Cerebro #1 (Product Strategy) con todas sus fichas
3. Configurar MCP con NotebookLM
4. Escribir system prompts (Orquestador + Cerebro #1)
5. Probar flujo: brief → Product Strategy → output validado

### Fase 1B — Expansión (Semanas 5-12)

1. Crear cerebros 2-4 (UX, UI, Frontend)
2. Implementar Cerebro #7 como evaluador en tiempo real
3. Probar flujo multi-cerebro con proyecto real de la agencia
4. Refinar protocolos de comunicación

### Fase 1C — Completitud (Semanas 13-20)

1. Crear cerebros 5-6 (Backend, QA/DevOps)
2. Implementar resolución automática de conflictos
3. Documentar lecciones aprendidas
4. Evaluar migración a RAG profesional

---

## 14. Índice de Documentos del Framework

| # | Archivo | Contenido |
|---|---------|-----------|
| 00 | `00-PRD-MasterMind-Framework.md` | Este documento (PRD principal) |
| 01 | `01-Plantilla-Cerebro.md` | Plantilla estándar para crear cualquier cerebro |
| 02 | `02-Metodo-Seleccion-Expertos.md` | Criterios y proceso para elegir expertos mundiales |
| 03 | `03-Proceso-Destilacion-Fuentes.md` | Cómo extraer conocimiento esencial de cada fuente |
| 04 | `04-Plantilla-Ficha-Fuente-Maestra.md` | Formato estándar para documentar cada fuente |
| 05 | `05-Cerebro-01-Product-Strategy.md` | Cerebro #1 completo con expertos y fuentes |
| 06 | `06-Cerebros-02-a-07-Specs.md` | Especificaciones de cerebros 2-7 |
| 07 | `07-Orquestador-y-Evaluador.md` | Diseño detallado del Orquestador y Evaluador Crítico |
| 08 | `08-Casos-de-Uso-e-Historias.md` | Casos de uso e historias de usuario |
| 09 | `09-Filesystem-Structure.md` | Estructura de carpetas lista para implementar |
