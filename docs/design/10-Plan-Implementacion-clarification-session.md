# PRD Clarification Session

**Source PRD**: 10-Plan-Implementacion-Claude-Code.md
**Session Started**: 2026-02-22
**Depth Selected**: Ultralong (35 questions)
**Total Questions**: 35
**Progress**: 35/35

---

## Session Log

## Question 1
**Category**: User/Stakeholder Clarity
**Ambiguity Identified**: No se especifica el modelo de negocio ni el roadmap de comercialización
**Question Asked**: ¿Quiénes son los usuarios finales del MasterMind Framework y cómo será utilizado?
**User Response**: Primero es para mi uso personal y probarlo bien con clientes para luego comercializarlo. Notas: Es un producto con fases: uso personal (ahora) → prueba con clientes (beta) → comercialización (producto final)
**Requirement Clarified**: Esto implica que el código debe estar limpio para eventual licenciamiento, y la arquitectura debe soportar multi-tenancy o deployment por cliente en el futuro

---

## Question 2
**Category**: Business Model & Technical Architecture
**Ambiguity Identified**: El plan actual no contempla arquitectura SaaS ni API-first
**Question Asked**: ¿Cómo visualizas el modelo de comercialización futuro?
**User Response**: SaaS por uso, tipo MCP, WEBMCP, por API o algo parecido. Notas: API-first, billing por uso, multi-tenancy
**Requirement Clarified**: Esto requiere reconsiderar la arquitectura actual. Necesitamos: API layer desde el inicio, sistema de autenticación/autorización, tracking de uso por cliente, rate limiting, y posiblemente un cambio de CLI a API-first con CLI como cliente

---

## Question 3
**Category**: Technical Architecture Phasing
**Ambiguity Identified**: No está claro si el CLI debe ser el MVP o si hay que construir API desde el inicio
**Question Asked**: Dado que el objetivo final es SaaS, ¿cómo debemos abordar la arquitectura técnica desde el inicio?
**User Response**: Fases separadas. Notas: MVP CLI local primero, SaaS como versión 2.0
**Requirement Clarified**: Esto simplifica el desarrollo inicial. El CLI puede ser la v1 sin considerar multi-tenancy. La migración a SaaS será una fase separada con su propio refactor. Esto valida que el plan actual es correcto para la fase 1

---

## Question 4
**Category**: Technical Dependencies
**Ambiguity Identified**: No está claro el estado actual de los MCP servers mencionados
**Question Asked**: El plan menciona MCP servers (NotebookLM, Context7, Sequential Thinking). ¿Qué estado tienen actualmente?
**User Response**: Están instalados en otro proyecto, hay que validar que funcionen en este sino hay que configurarlo. Notas: MCP servers existen en otro proyecto, migración/configuración pendiente
**Requirement Clarified**: La Fase 0 debe incluir validación de MCP servers. Si no funcionan, agregar una subtarea de configuración. Esto afecta el timeline estimado

---

## Question 5
**Category**: Technical Dependencies - Skills
**Ambiguity Identified**: No está claro si las skills están disponibles para este proyecto
**Question Asked**: ¿Dónde están actualmente las skills superpower/superclaude mencionadas en el plan?
**User Response**: Ambos - globales y locales mezclados. Notas: Skills existen en ~/.claude/skills/ y en otros proyectos
**Requirement Clarified**: Las skills globales deberían funcionar automáticamente. Las locales de otros proyectos pueden requerir copia o symlink si tienen lógica específica que necesitemos

---

## Question 6
**Category**: Content Validation - Cerebro #1 Sources
**Ambiguity Identified**: No está claro el estado real de las 10 fuentes del Cerebro #1
**Question Asked**: Las 10 fuentes del Cerebro #1 (Product Strategy) mencionadas en el plan, ¿qué estado tienen?
**User Response:** Aparentemente están listas para usar, pero me gustaría que las validaras y revisarás bien si cumplen el objetivo. Notas: Fuentes existen pero requieren validación contra estándares
**Requirement Clarified**: Agregar tarea de validación de fuentes existentes antes de Fase 3. Usar el criterio del plan (5 secciones, YAML completo, 3+ principios). Si no cumplen, actualizar antes de continuar

---

## Question 7
**Category**: External Service - NotebookLM
**Ambiguity Identified**: No está claro si el usuario tiene acceso a NotebookLM
**Question Asked**: ¿Qué estado tiene tu cuenta de NotebookLM y experiencia con esta herramienta?
**User Response**: Cuenta activa. Notas: Usuario ya tiene acceso a NotebookLM
**Requirement Clarified**: Fase 5 puede proceder sin obstáculo de cuenta. El usuario ya conoce o puede aprender la interfaz rápidamente

---

## Question 8
**Category**: Scope & Architecture - Multi-Domain Vision
**Ambiguity Identified**: El plan asume nicho único de software, pero la visión real es multi-nicho
**Question Asked**: El plan menciona 'Software Development' como nicho inicial. ¿Este es el único nicho o planeas expandir a otros?
**User Response**: La idea es crear una librería de cerebros multidisciplinarios, de cualquier nicho, que sean reutilizables combinables con otros cerebros llenos de conocimientos para lograr objetivos planteados desde creación de un software, hasta llevar de la mano el crecimiento de un cliente mediante marketing haciendo loops. Notas: Visión multi-nicho, cerebros combinables, feedback loops, librería reutilizable
**Requirement Clarified**: **CRITICAL** - Esto cambia la arquitectura significativamente. Necesitamos: 1) Estructura modular por nicho, 2) Protocolo de combinación de cerebros cross-nicho, 3) Sistema de feedback loops entre cerebros, 4) Marketplace/librería de cerebros como concepto central. El plan actual es solo para el PRIMER nicho (software), pero la arquitectura debe considerarse multi-nicho desde el inicio

---

## Question 9
**Category**: Architecture - Cross-Domain Brain Reusability
**Ambiguity Identified**: No está claro qué cerebros son reutilizables entre nichos
**Question Asked**: Cuando mencionas cerebros combinables de diferentes nichos, ¿cómo imaginas esa combinación?
**User Response**: Modelo híbrido: cerebros específicos por nicho (#2-#6: UX, UI, Frontend, Backend, QA/DevOps) vs cerebros reutilizables (#1 Product Strategy, #7 Growth & Data, Orquestador, Evaluador). Ejemplo: Product Strategy, Growth y los componentes de control se reutilizan en marketing y creación de contenido. Notas: Arquitectura híbrida - algunos cerebros genéricos, otros específicos por nicho
**Requirement Clarified**: Esto define la arquitectura: 1) Cerebros de "proceso" son compartidos (cross-domain), 2) Cerebros de "ejecución técnica" son específicos por nicho, 3) El orquestador debe poder seleccionar cerebros de diferentes nichos según el objetivo, 4) La estructura de carpetas debe reflejar esta distinción

---

## Question 10
**Category**: Architecture - Orchestrator Intelligence
**Ambiguity Identified**: El plan describe flujos predefinidos, pero no cómo el orquestador aprende
**Question Asked**: ¿Cómo debería funcionar el orquestador al recibir un brief? ¿Selecciona cerebros automáticamente o el usuario elige?
**User Response**: El orquestador debe interpretar el brief, seleccionar automáticamente los mejores cerebros para cumplir el objetivo, y tener capacidad de aprender de la experiencia. Notas: Orquestador inteligente con aprendizaje, no solo flujos predefinidos
**Requirement Clarified**: Esto añade complejidad: 1) El orquestador necesita NLP para interpretar briefs, 2) Sistema de recomendación de cerebros basado en el objetivo, 3) Mecanismo de learning (probablemente tracking de outcomes y refinamiento de selección), 4) Logging de decisiones para aprendizaje. Esto es más complejo que flujos predefinidos - requiere un sistema de "meta-learning"

---

## Question 11
**Category**: Architecture - Evaluator #7 Real-time Operation
**Ambiguity Identified**: No está claro qué significa "evalúa en tiempo real"
**Question Asked**: El Cerebro #7 (Evaluador) evalúa 'en tiempo real'. ¿Qué significa exactamente? ¿Interviene DURANTE el proceso o solo evalúa resultados?
**User Response:** Híbrido: en tiempo real redirige cuando ve mal rumbo, y post-output aprueba/rechaza/mejora. Notas: Dos modos - intervención activa durante proceso + evaluación final
**Requirement Clarified**: Esto define el sistema de evaluación: 1) Modo activo: monitoreo continuo con capacidad de intervención, 2) Modo pasivo: aprobación/rechazo de outputs, 3) Contador de rechazos (3 → escalar a humano), 4) Logging de intervenciones para aprendizaje del orquestador. El evaluador es como un "tech lead activo" más que un QA pasivo

---

## Question 12
**Category**: Architecture - Communication Protocol & Persistence
**Ambiguity Identified**: El plan define YAML para comunicación pero no especifica persistencia ni retrieval
**Question Asked**: El plan define un protocolo YAML para comunicación entre cerebros. ¿Este formato es suficiente o necesita expandirse?
**User Response:** No estoy seguro, pide recomendación experta. Sugiere BD vectorial o mixta (PostgreSQL + pgvector). Notas: Usuario abierto a recomendación técnica
**Requirement Clarified**: **RECOMENDACIÓN EXPERTA:** Arquitectura híbrida de 3 capas: 1) YAML para mensajes en tránsito (ligero, human-readable), 2) PostgreSQL + pgvector para persistencia (relacional para queries estructuradas, vectorial para búsqueda semántica), 3) Cola de mensajes (Redis/RabbitMQ) para orquestación asíncrona. Esto permite: logging completo, retrieval por contexto, análisis de patrones, y escalabilidad futura. Para v1 (CLI local): archivos YAML + SQLite simple. Para v2 (SaaS): migrar a PostgreSQL + pgvector + Redis

---

## Question 13
**Category**: Data Format - Source Files Structure
**Ambiguity Identified**: Confirmar que YAML front matter es el formato correcto para versionado
**Question Asked**: Para las fichas de fuentes maestras, ¿el formato de YAML front matter en Markdown es el correcto o preferís otro?
**User Response:** YAML front matter porque cada cerebro es actualizable y esa es la mejor manera de versionarlos. La desventaja de mantener YAML manualmente se resuelve con mastermind-cli automatizándolo. Notas: Usuario ya tiene clara la razón - versionado + automatización via CLI
**Requirement Clarified**: Confirma que el plan es correcto. El YAML front matter permite: 1) Versionado semántico en cada fuente, 2) Changelog integrado, 3) Git tracking por fuente, 4) CLI automation para updates. El comando `mastermind source update` del plan es precisamente la solución a la "desventaja" mencionada

---

## Question 14
**Category**: Automation - NotebookLM Loading Process
**Ambiguity Identified**: No está claro si la carga a NotebookLM es manual o automatizada
**Question Asked**: El plan describe `mastermind source export` para generar archivos limpios. ¿El proceso de carga a NotebookLM debería ser manual o automatizado?
**User Response:** No definido aún, pero existe notebooklm-mcp configurada que permite automatizar. Podría ser híbrido según requerimiento. Notas: MCP tool disponible para automatización, flexibilidad de modos
**Requirement Clarified**: Hay dos modos posibles: 1) Manual: `export` + drag&drop a NotebookLM (simple, transparente), 2) Automático: `export --auto-load` vía notebooklm-mcp (mágico, menos transparente). Recomendación: Implementar ambos, con manual por defecto y flag `--auto-load` para automatización. La Fase 5 debería incluir testing de notebooklm-mcp para validar que funciona

---

## Question 15
**Category**: CLI Usability - Command Naming
**Ambiguity Identified**: Confirmar nombre del comando CLI
**Question Asked**: El plan usa `mastermind` como nombre del comando CLI. ¿Este es el nombre final o querés algo más corto?
**User Response:** Usar `mastermind` con alias `mm` para acortar. Notas: Comando principal completo + alias para uso frecuente
**Requirement Clarified**: Configurar ambos: 1) `mastermind` como comando principal (claridad, documentación), 2) `mm` como alias (productividad diaria). En el setup del CLI se debe crear el alias automáticamente. Documentación debe usar `mastermind` (o `mm`) indicando equivalencia

---

## Question 16
**Category**: Localization - System Prompts Language
**Ambiguity Identified**: No está definido el idioma de los system prompts
**Question Asked**: Los system prompts de los agentes (Orquestador, Cerebros, Evaluador), ¿en qué idioma deben estar?
**User Response:** Inglés + bilingüe. Notas: Prompts en inglés, respuestas adaptadas al idioma del usuario
**Requirement Clarified**: System prompts en inglés (mejor performance con LLMs) con instrucción de detectar y responder en el idioma del input. Esto significa: 1) Base: prompts en inglés, 2) Instrucción: "Respond in the same language as the user's input", 3) Fuentes pueden estar en español (como están ahora), 4) Output de cerebros se adapta al usuario

---

## Question 17
**Category**: Architecture - Agent Output Format
**Ambiguity Identified**: No está claro el formato de output de los cerebros
**Question Asked**: Cuando un cerebro produce su output, ¿qué formato debería usar?
**User Response:** Depende del destino - Markdown para humanos, JSON para otras IAs. Pide recomendación. Notas: Usuario intuitivamente correcto, busca confirmación
**Requirement Clarified**: **RECOMENDACIÓN EXPERTA:** Formato híbrido三层 (3-layer): 1) Outer: JSON con metadata estructurada (brain, task_id, timestamp, confidence, status), 2) Middle: Campo "content" con Markdown para legibilidad humana, 3) Inner: Campo "data" con JSON/YAML para machine-processing. Ejemplo: `{"brain": "product-strategy", "content": "# Análisis\n...", "data": {"problems": [...], "metrics": [...]}}`. Esto permite: humanos leen Markdown, máquinas parsean JSON, un solo archivo sirve para ambos

---

## Question 18
**Category**: Data Architecture - Output Storage Strategy
**Ambiguity Identified**: No está definido el sistema de almacenamiento de outputs
**Question Asked**: ¿Dónde se almacenan los outputs de los cerebros y los logs de las sesiones?
**User Response:** Híbrido. Notas: Archivos + base de datos
**Requirement Clarified**: Estrategia híbrida de 3 capas: 1) Caliente (últimos 7 días): archivos JSON en `outputs/recent/` para acceso instantáneo, 2) Tibio (últimos 90 días): SQLite local en `db/mastermind.db` para queries y búsqueda, 3) Frío (+90 días o archivado): Export a JSON/parquet para backup o migración a PostgreSQL en v2 SaaS. Esto permite: fast access sin dependencias, queries estructuradas, y escalabilidad hacia SaaS

---

## Question 19
**Category**: AI/ML - Orchestrator Learning Roadmap
**Ambiguity Identified**: No está claro cómo evoluciona el sistema de aprendizaje del orquestador
**Question Asked**: El orquestador debe 'aprender de la experiencia'. ¿Qué nivel de complejidad tiene este sistema de aprendizaje?
**User Response:** Pide recomendación para empezar sencillo y escalar hasta ML completo. Notas: Roadmap evolutivo deseado
**Requirement Clarified**: **RECOMENDACIÓN EXPERTA - Roadmap de 4 fases:** Fase 1 (v0.1): Contadores simples en SQLite - qué cerebros se usaron, aprobaciones del #7, tiempo de ejecución. Fase 2 (v0.5): Patrones - tracking de outcomes por tipo de brief, correlaciones cerebro→outcome. Fase 3 (v1.0): Embeddings - vectorizar briefs y outcomes con pgvector para "briefs similares usaron estos cerebros". Fase 4 (v2.0 SaaS): ML - modelo entrenado que predice combinación óptima. CLAVE: Diseñar el schema de datos desde Fase 1 para soportar las siguientes sin migración compleja

---

## Question 20
**Category**: QA - Testing Strategy for AI Agents
**Ambiguity Identified**: No está definido cómo validar que un cerebro funciona correctamente
**Question Asked**: ¿Cómo se validará que un cerebro está funcionando correctamente? ¿Qué estrategia de testing?
**User Response:** Pide recomendación experta como ML/agent expert. Notas: Busca strategy ideal
**Requirement Clarified**: **RECOMENDACIÓN EXPERTA - Testing Pyramid para Agentes:** 1) **Unit**: Golden sets de 10 briefs conocidos → outputs esperados (test de regresión), 2) **Integration**: Flujo completo orquestador→cerebro→evaluador con briefs reales (test end-to-end), 3) **Evaluation**: Cerebro #7 juzga outputs de otros cerebros (meta-evaluación), 4) **Human**: Sesiones quincenales con clientes reales + feedback loop. Implementar: `mastermind brain test --unit` (golden sets), `mastermind brain test --integration` (flujo completo), `mastermind brain test --eval` (auto-evaluación #7)

---

## Question 21
**Category**: Content - Golden Sets for Testing
**Ambiguity Identified**: No hay golden sets definidos para testing
**Question Asked**: Para los golden sets de testing (briefs → outputs esperados), ¿tenés ejemplos reales de tu experiencia profesional?
**User Response:** No tiene briefs. Pide ayuda para crearlos. Sugiere crear habilidad/agente experto en briefs (onboarding wizard). Notas: Usuario propone Brief Wizard como feature
**Requirement Clarified**: **FEATURE IDEA BRILLIANTE**: Crear `mastermind brief` comando que guía al usuario a crear briefs de calidad. Output: brief estructurado + golden set para testing. MVP: 10 briefs hipotéticos del nicho software (ej: "App delivery food", "Dashboard analytics", "API payments"). PLUS: Brief wizard interactivo que pregunta: problema, audiencia, contexto, restricciones, criterios de éxito → genera brief structured

---

## Question 22
**Category**: Reliability - Error Handling Strategy
**Ambiguity Identified**: No está definido cómo manejar fallos de cerebros
**Question Asked**: ¿Qué debe hacer el sistema cuando un cerebro falla (timeout, error de API, output inválido)?
**User Response:** Sistema híbrido dependiendo del error. Notas: Estrategia adaptativa según tipo de fallo
**Requirement Clarified**: **Matriz de decisiones por tipo de error:** 1) **Timeout/rate limit**: Retry con exponential backoff (3 intentos), 2) **API error 5xx**: Retry (3 intentos), 3) **API error 4xx**: Fail fast + mensaje específico, 4) **Output inválido/vací**: Retry 1 vez con prompt alternativo, luego escalar, 5) **Rechazo #7 (3 veces)**: Escalar a humano con contexto completo, 6) **Error crítico**: Graceful degradation - output parcial + warnings. Cada error se loggea para aprendizaje del orquestador

---

## Question 23
**Category**: Operations - Human Escalation Mechanism
**Ambiguity Identified**: No está definido cómo notificar al humano cuando se necesita intervención
**Question Asked**: Cuando el sistema necesita escalar a un humano (3 rechazos del #7, error crítico), ¿cómo se notifica?
**User Response:** Distingue entre bloqueantes (detener flujo + notificar por email/WhatsApp/Telegram) vs recuperables (reintentar en horario específico). Ej: caída de red, fin de créditos. Pide opinión. Notas: Usuario entiende bien la diferencia entre errores críticos y transitorios
**Requirement Clarified**: **Tu intuición es correcta. Matriz ampliada:** 1) **Bloqueante (3 rechazos #7, error lógico crítico)**: Detener flujo + notificación multi-canal (email + preferencia del usuario: WhatsApp/Telegram/Slack), 2) **Recuperable scheduled (fin de créditos)**: Agendar reintentó para hora específica (cron-like), 3) **Recuperable transitorio (red, rate limit)**: Retry automático con backoff, 4) **Degradación (cerebro no disponible)**: Usar cerebro alternativo si existe, o output parcial + warning. Configurable por usuario: `config/notifications.yaml` con canales preferidos

---

## Question 24
**Category**: UX - Configuration Management
**Ambiguity Identified**: No está definido cómo se configura el sistema
**Question Asked**: ¿Cómo se configura el sistema (API keys, preferencias, canales de notificación, etc.)?
**User Response:** Híbrido. Notas: Wizard inicial + archivos YAML para cambios futuros
**Requirement Clarified**: **Flujo de configuración híbrido:** 1) **First run**: `mastermind init` wizard interactivo que pregunta API keys, preferencias, canales, 2) **Stored**: `~/.config/mastermind/config.yaml` (global) + `project/.mastermind/config.yaml` (local), 3) **Secrets**: `~/.config/mastermind/secrets.env` (nunca commit), 4) **Edit**: `mastermind config edit` abre en $EDITOR, 5) **Validate**: `mastermind config validate` checkea que todo esté OK. Esto permite: onboarding fácil + configuración editable + soporte multi-proyecto

---

## Question 25
**Category**: Release Management - Versioning Strategy
**Ambiguity Identified**: No está definida la estrategia de versionado del framework
**Question Asked**: ¿Qué estrategia de versionado usará el framework MasterMind?
**User Response:** Pide qué es lo más usado profesionalmente. Duda sobre Calver si hay varios releases por día. Notas: Usuario busca estándar profesional
**Requirement Clarified**: **ESTÁNDAR PROFESIONAL:** Uso **dual** según el tipo de componente: 1) **Framework (CLI, core)**: Semver estricto (v1.2.3) - major para breaking changes, minor para features, patch para fixes. Es el estándar para librerías/frameworks (ej. React, Next.js, pytest). 2) **Cerebros (contenido)**: Calver (2026.02) o Semver simple (v1.0, v1.1) - porque el contenido no tiene "breaking changes" en el sentido técnico. Para múltiples releases por día: usar patch (v1.2.3 → v1.2.4) o timestamp (v1.2.3-20260222-1430)

---

## Question 26
**Category**: Roadmap - Other Brains Implementation Order
**Ambiguity Identified**: No está definido cuándo implementar los cerebros 2-7
**Question Asked**: El plan especifica los cerebros 2-7 pero no cuándo implementarlos. ¿Cuál es el roadmap?
**User Response:** Core primero (#1 y #7), probarlos y optimizarlos, luego continuar en secuencia según necesidades. Notas: Enfoque pragmático - validar core antes de expandir
**Requirement Clarified**: **Roadmap por fases:** 1) **MVP (v0.1)**: Cerebros #1 (Product Strategy) + #7 (Growth/Evaluador) + Orquestador básico. Validar que el core loop funciona. 2) **v0.5**: Cerebro #2 (UX Research) si el feedback de clientes lo indica. 3) **v0.6-v1.0**: Implementar 3-6 según demanda y nichos a atacar. 4) **Multi-nicho**: Cuando software development esté completo, replicar #1+#7 para otros nichos (marketing, content, etc.). Criterio de "listo para siguiente": golden sets pasando + 5 clientes reales satisfechos

---

## Question 27
**Category**: Architecture - Orchestrator Nature & Knowledge Sources
**Ambiguity Identified**: No está claro si el Orquestador es un cerebro con fuentes o un router técnico
**Question Asked**: ¿El Orquestador es un cerebro más (con fuentes propias) o es un componente técnico de coordinación?
**User Response:** Debe orquestar, necesita habilidades definidas + fuentes propias + autoaprendizaje de fallas y éxitos. Pide opinión. Notas: Usuario ve orquestador como "meta-cerebro" con conocimiento propio
**Requirement Clarified**: **RECOMENDACIÓN EXPERTA:** Orquestador como **Meta-Cerebro Híbrido** con 3 capas: 1) **Technical routing**: Lógica de selección de cerebros según tipo de brief, 2) **Domain knowledge**: Fuentes sobre orquestación de equipos, gestión de proyectos, liderazgo (ej: "The Manager's Path", "Team Topologies"), 3) **Learning layer**: Tracking de outcomes (como discutimos en Q19). Fuentes sugeridas: gestión de equipos ágiles, sistemas de trabajo, patrones de orquestación, case studies de proyectos exitosos

---

## Question 28
**Category**: Architecture - Brain #7 Nature (Growth + Evaluator)
**Ambiguity Identified**: No está claro si #7 es un cerebro o dos componentes separados
**Question Asked**: El Cerebro #7 tiene doble rol: Growth & Data + Evaluador en tiempo real. ¿Es un cerebro o dos cosas separadas?
**User Response:** Es un cerebro que evoluciona, razona con datos acumulados. Evaluar es una habilidad (como aprobar/rechazar/redirigir). Necesita conocimientos de ciencia de datos, análisis, growth. Pide recomendaciones. Notas: #7 como Data Scientist + Growth Hacker + QA Lead
**Requirement Clarified**: **Cerebro #7 como "Meta-Cerebro Evolutivo":** 3 funciones unificadas bajo conocimiento de datos: 1) **Evaluator**: Analiza outputs de otros cerebros usando criterios de calidad (¿cumple el brief? ¿hay contradicciones? ¿es accionable?), 2) **Growth**: Busca optimizaciones, oportunidades de mejora, loops de feedback, 3) **Data**: Acumula y analiza datos de todas las interacciones. **Fuentes sugeridas:** Data Science (O'Neil), Lean Analytics (Croll), Growth Engineering (Eisenberg), Metrics-driven product, Testing & experimentation. #7 es el único cerebro que VE todo lo que pasa en el sistema

---

## Question 29
**Category**: UX - Brief Input Format & Discovery Process
**Ambiguity Identified**: No está definido el formato de brief ni el proceso de extracción
**Question Asked**: ¿Qué formato deben tener los briefs que los usuarios envían al sistema?
**User Response:** Sugiere agente/habilidad experta en brief que entreviste al usuario. El usuario a veces no está seguro de lo que quiere, el agente debe hacer preguntas y estructurar la info. Notas: Proceso de discovery interactivo
**Requirement Clarified**: **FEATURE CONFIRMADA - Brief Discovery Agent:** Dos modos: 1) **Interactive mode**: `mastermind brief` inicia entrevista Socrática (5-10 preguntas) - "¿Qué problema resuelves?", "¿Quiénes son tus usuarios?", etc. Al final genera brief estructurado. 2) **Template mode**: Usuario completa campos directamente. **Formato final de brief (YAML):** problem, users, context, constraints, success_criteria, budget, timeline. El Brief Agent vive ANTES del Orquestador - es como un "receptionist" que prepara el brief antes de entrar al sistema

---

## Question 30
**Category**: UX - User Interface Evolution
**Ambiguity Identified**: No está definido el tipo de interfaz de usuario
**Question Asked**: ¿Qué tipo de interfaz de usuario tendrá el framework?
**User Response:** Evolutivo. Notas: Progresión desde CLI hasta Web UI
**Requirement Clarified**: **Roadmap de UI por fases:** 1) **v0.1 (CLI Rich)**: Comandos con Rich library - colores, tablas, progress bars, spinners. Output estructurado pero interactivo. 2) **v0.5 (TUI)**: Terminal UI con Textual/tui - menús visuales, split panes, dashboards en terminal. 3) **v2.0 (Web SaaS)**: Dashboard web con React/Next.js - historial de briefs, gráficos de aprendizaje, configuración visual. CLAVE: Mantener paridad funcional - todo lo que se puede hacer en CLI debe tener equivalente Web

---

## Question 31
**Category**: Documentation - User Documentation Strategy
**Ambiguity Identified**: No está definido el sistema de documentación
**Question Asked**: ¿Qué tipo de documentación tendrá el framework para usuarios?
**User Response:** MD + GitBook. Notas: Markdown en GitHub + GitBook para docs externas
**Requirement Clarified**: **Estrategia de documentación dual:** 1) **GitHub (repo)**: README.md, docs/ con arquitectura, CONTRIBUTING.md, CHANGELOG.md. Para desarrolladores y contribuidores. 2) **GitBook (pública)**: Documentación de usuario - tutoriales, guías, reference de comandos, ejemplos de briefs, caso de uso. SEO-friendly, embeddable en web. 3) **CLI integrada**: `mastermind --help`, `mastermind docs [comando]` abre doc específica, `mastermind tutorial` inicia tour interactivo. Sync: GitBook puede leer desde repo GitHub o viceversa

---

## Question 32
**Category**: Legal - Framework Licensing
**Ambiguity Identified**: No está definida la licencia del código
**Question Asked**: ¿Qué licencia tendrá el código del framework?
**User Response:** Propietaria. Notas: Código cerrado para SaaS futuro
**Requirement Clarified**: **Licencia propietaria - Todos los derechos reservados:** Dado el objetivo de comercialización como SaaS, esto es correcto. Considerar: 1) Archivo LICENSE con términos de uso, 2) Para clientes: contrato de licencia por uso (no por código), 3) Para v2 SaaS: términos de servicio del servicio, 4) Para fuentes/brain-knowledge: considerar si son parte del IP o separables. **IMPORTANTE:** Asegurar que dependencias (CLI libs) sean compatibles con uso comercial

---

## Question 33
**Category**: Product - MVP Definition for Cerebro #1
**Ambiguity Identified**: No está definido qué constituye el MVP
**Question Asked**: ¿Qué constituye el MVP mínimo para poder decir 'el Cerebro #1 funciona'?
**User Response:** Plan completo (Fase 0-5). Notas: No shortcuts - implementar todo el plan
**Requirement Clarified**: **MVP = Plan Completo (Fase 0-5):** Esto significa ~8-10 horas de trabajo para tener Cerebro #1 operativo. **Checkpoint de "listo":** 1) Estructura creada (F1), 2) CLI funcional con todos los comandos (F2), 3) Fuentes validadas con YAML actualizado (F3), 4) System prompts creados (F4), 5) NotebookLM configurado y verificado (F5), 6) PRP-001 generado. **Definition of Done:** Usuario puede ejecutar `mastermind brief`, crear un brief, y obtener un output de Cerebro #1 que pase la evaluación de #7

---

## Question 34
**Category**: Metrics - Success Metrics Framework
**Ambiguity Identified**: No están definidas las métricas de éxito del framework
**Question Asked**: ¿Qué métricas definirán que el framework es exitoso?
**User Response:** Todas. Notas: Métricas técnicas, de usuario y de negocio
**Requirement Clarified**: **Framework de Métricas Triple:** 1) **Técnicas**: Golden sets pass rate (>95%), Tests pass rate (100%), Code coverage (>80%), Response time (<30s por brief), Error rate (<5%), 2) **Usuario**: Satisfaction score (>4/5), NPS (>50), Brief completion rate (>90%), Feature adoption, 3) **Negocio**: Conversión (free→paid), Retención (30d, 90d), ARPU, Churn (<5%/mes), Time-to-value (<1 semana). **Dashboard**: `mastermind metrics` muestra todas en tiempo real

---

## Question 35
**Category**: Strategy - Post-MVP Next Steps
**Ambiguity Identified**: No está definido qué hacer después del MVP
**Question Asked**: Una vez completado el MVP del Cerebro #1, ¿cuál es el siguiente paso inmediato?
**User Response:** Más cerebros. Notas: Seguir construyendo más cerebros antes de comercializar
**Requirement Clarified**: **Estrategia de "Build Before Sell":** 1) **Post-MVP inmediato**: Cerebro #2 (UX Research) siguiendo el mismo proceso que #1, 2) **Criterio de "listo para vender":** Mínimo 3 cerebros funcionando (#1, #2, #7) + golden sets + 5 casos de uso reales resueltos, 3) **Luego**: Comercializar a clientes beta con descuento "early adopters", 4) **Feedback loop**: Usar feedback de beta para iterar antes de launch público, 5) **Visión**: Construir 7 cerebros de software development + 2-3 nichos adicionales antes de scale
