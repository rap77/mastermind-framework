Este **Documento de Requisitos del Producto (PRD)** consolida la infraestructura central de **Paperclip** (orquestación de agentes, gobernanza y multi-inquilino) con la evolución tecnológica y visual que hemos discutido: el rendimiento de **Rust**, la inteligencia de **Python**, y la interfaz visual de **n8n**.

---

# PRD: AAF (Agent-Aware Flows) - Versión 2.0

## 1. Visión del Producto

AAF es una plataforma de orquestación diseñada para gestionar **"compañías con cero humanos"**. A diferencia de los flujos de automatización estáticos, AAF utiliza **agentes autónomos** que razonan, aprenden y se comunican a través de un **organigrama empresarial dinámico**, todo gestionado desde una interfaz visual intuitiva y conectada a ecosistemas empresariales globales (Odoo, ERPs, Social Media).

---

## 2. Arquitectura de Sistema y Stack Tecnológico

Para resolver los cuellos de botella de la arquitectura original de tres capas (Node/Express/React), el nuevo stack se divide por responsabilidades:

- **Orquestador de Misión Crítica (Core):** Escrito en **Rust**. Hereda la lógica del `heartbeatService` de Paperclip para gestionar el ciclo de vida de los agentes (queued → running → succeeded/failed) con una concurrencia masiva y latencia mínima.
- **Motor de Inteligencia y Autoaprendizaje:** Escrito en **Python (FastAPI)**. Maneja la lógica de razonamiento profundo, el procesamiento de lenguaje natural y el bucle de aprendizaje basado en el historial de `activity_log`.
- **Interfaz de Usuario (UI):** **React + React Flow**. Una evolución del Dashboard actual hacia un lienzo (canvas) visual donde los agentes son nodos animados.
- **Capa de Datos:** **PostgreSQL + Drizzle ORM**. Mantiene la estructura de aislamiento por compañía (`company_id`).

---

## 3. Especificaciones de Funcionalidades Principales

### 3.1. Orquestación Visual de Agentes (Inspirado en n8n)

- **Canvas Dinámico:** Los agentes no se listan en tablas, sino que se arrastran al canvas. Las conexiones representan la jerarquía de mando (`reports_to`).
- **Nodos Autónomos:** Cada nodo es un agente con "Skills" (Habilidades). Al activarse, el nodo muestra una **animación de flujo** que indica el paso de datos en tiempo real.
- **Visual Debugger:** Si un agente falla, el nodo se resalta en rojo. Al hacer clic, se despliega el **Run Transcript** que muestra el pensamiento de la IA y el punto exacto de error en el log de ejecución.

### 3.2. Integraciones y Conectividad Multicanal

- **Entrada Multicanal (Inbound):** Agentes especializados capaces de recibir triggers desde webhooks de **Odoo**, mensajes de **Meta (WhatsApp/FB)** o cambios en **Notion**.
- **Salida Inteligente (Outbound):** Basado en el sistema de **Adapters** de Paperclip (HTTP/Process), el agente puede decidir el canal de salida más efectivo (ej. actualizar un registro en el ERP o enviar un reporte por correo).
- **Integración con ERP (Odoo/Otros):** Agentes con habilidades nativas para realizar llamadas a la API de Odoo, mapeando datos del negocio directamente al flujo autónomo.

### 3.3. Autoaprendizaje y Auditoría

- **Bucle de Retroalimentación:** Los agentes analizan sus propios `heartbeatRuns` pasados para ajustar sus estrategias. Si un humano ("The Board") corrige una acción, el agente de Python registra este cambio para no repetir el error.
- **Auditoría de "The Board":** Interfaz de aprobación para decisiones de alto impacto (hiring, grandes gastos).

---

## 4. Seguridad y Gobernanza

- **Aislamiento Multi-inquilino:** Se mantiene la estricta separación por `company_id` en todas las rutas y servicios.
- **Vault de Credenciales:** Mejora el sistema de `agent_api_keys`. Las llaves de Odoo, Google y Meta se almacenan en un componente de Rust cifrado, accesible solo durante la ejecución del agente en un sandbox seguro.
- **Modo Autenticado Obligatorio:** Para despliegues de producción con integraciones de terceros, se requiere autenticación robusta mediante sesiones (mejorando el modelo `authenticated` original).

---

## 5. Casos de Uso (Historias de Usuario)

1. **Automatización de Ventas ERP:** "Como dueño de una empresa, quiero que cuando entre un lead por Meta, un agente investigue su perfil, lo registre en Odoo y asigne una tarea en Notion al agente de ventas, todo visible en un mapa animado".
2. **Resolución de Errores Autónoma:** "Como operador técnico, quiero que si el agente de Odoo falla por un error de API, el sistema me muestre visualmente por qué falló y use el autoaprendizaje para reintentar con parámetros ajustados".

---

## 6. Preguntas de Contexto Final para la IA Desarrolladora

Para que la IA proceda con el desarrollo del código, confirmemos:

- **¿Protocolo de Comunicación?:** ¿Usaremos gRPC para la comunicación Rust-Python para garantizar que los tipos de datos de los agentes sean idénticos en ambos lados?
- **¿Nivel de Sandboxing?:** ¿Deseas que cada agente corra en un contenedor Docker efímero para máxima seguridad al interactuar con las páginas web y aplicaciones de terceros?

**Acción realizada:** He generado el PRD completo integrando la base técnica de Paperclip con las mejoras de rendimiento (Rust), IA (Python), visualización (estilo n8n) e integraciones empresariales (Odoo/Multicanal).

---
Genial, vamos directo: te dejo algo que puedas pasar casi tal cual a código. Asumo backend tipo REST y front SPA.

---

## 1. Estructura de carpetas sugerida

Algo simple para empezar (ejemplo Node/TS, pero aplica a otros stacks):

text

`backend/   src/    agents/      discoveryAgent.ts      architectureAgent.ts      planningAgent.ts      agentFactory.ts      agentEvaluator.ts      orchestrator.ts    models/      project.ts      vision.ts      architecture.ts      roadmap.ts      backlog.ts      agentDefinition.ts      agentLog.ts    routes/      projects.ts      agents.ts      orchestrator.ts    services/      llmClient.ts      agentRunner.ts      eventBus.ts    index.ts frontend/   src/    pages/      ProjectsList.tsx      NewProjectWizard.tsx      ProjectDashboard.tsx    components/      Chat.tsx      VisionView.tsx      ArchitectureView.tsx      RoadmapView.tsx      AgentsView.tsx    api/      projects.ts      agents.ts      orchestrator.ts`

A partir de aquí, vamos con las APIs.

---

## 2. API REST – Proyectos y flujo principal

## 2.1. Crear proyecto

`POST /api/projects`

Body:

json

`{   "name": "Plataforma que diseña y construye con agentes",  "description": "Plataforma de agentes para diseñar proyectos de software",  "type": "saas" }`

Respuesta:

json

`{   "id": "proj_123",  "name": "Plataforma que diseña y construye con agentes",  "description": "Plataforma de agentes para diseñar proyectos de software",  "type": "saas",  "status": "idea" }`

---

## 2.2. Obtener proyectos

`GET /api/projects`

Respuesta:

json

`[   {    "id": "proj_123",    "name": "Plataforma que diseña y construye con agentes",    "status": "vision_defined"  } ]`

---

## 2.3. Obtener detalle de un proyecto

`GET /api/projects/:projectId`

Respuesta (ejemplo):

json

`{   "id": "proj_123",  "name": "Plataforma que diseña y construye con agentes",  "description": "Plataforma de agentes para diseñar proyectos de software",  "type": "saas",  "status": "planning",  "vision": { ... },  "architecture": { ... },  "roadmap": { ... },  "backlog": { ... } }`

---

## 3. API para el Agente de Descubrimiento (chat + visión)

## 3.1. Enviar mensajes al chat de descubrimiento

`POST /api/projects/:projectId/discovery/chat`

Body:

json

`{   "message": "Quiero una plataforma que use agentes para diseñar software.",  "role": "user" }`

Respuesta:

json

`{   "messages": [    {      "role": "user",      "content": "Quiero una plataforma que use agentes para diseñar software."    },    {      "role": "assistant",      "content": "Perfecto. ¿Qué tipo de usuarios la usarían primero?"    }  ] }`

(Internamente llamas a `DiscoveryAgent` con el historial almacenado en DB.)

---

## 3.2. Generar documento de visión

`POST /api/projects/:projectId/discovery/generate-vision`

Body:

json

`{}`

Respuesta:

json

`{   "vision": {    "project_id": "proj_123",    "problem": "Los founders no saben cómo estructurar sus proyectos de software.",    "target_users": "Empresas de software y emprendedores tecnicos.",    "business_goals": [      "Reducir tiempo de definicion de proyectos",      "Mejorar calidad de arquitectura inicial"    ],    "main_features": [      "Chat guiado de descubrimiento",      "Diseno automatico de arquitectura",      "Roadmap y backlog inicial"    ],    "non_goals": [      "No reemplazar completamente al equipo tecnico"    ],    "constraints": [      "MVP en menos de 3 meses"    ]  } }`

---

## 4. API para Arquitectura y Roadmap

## 4.1. Generar arquitectura (Arquitecto)

`POST /api/projects/:projectId/architecture/generate`

Body:

json

`{   "tech_preferences": ["typescript", "react"],  "constraints": ["budget_moderate"] }`

Respuesta:

json

`{   "architecture": {    "project_id": "proj_123",    "modules": [      {        "name": "Web frontend",        "description": "Interfaz para founders y equipos.",        "type": "frontend",        "dependencies": []      },      {        "name": "Backend API",        "description": "Gestion de proyectos, agentes y estados.",        "type": "backend",        "dependencies": ["Database"]      }    ],    "suggested_stack": {      "frontend": "React",      "backend": "NodeJS / NestJS",      "database": "PostgreSQL",      "infra": "Docker + cloud",      "integrations": []    },    "mvp_scope": [      "Flujo de creacion de proyecto",      "Chat de descubrimiento",      "Generacion basica de vision y arquitectura"    ],    "risks": [      "Complejidad de orquestacion de agentes",      "Costos de LLM"    ]  } }`

---

## 4.2. Generar roadmap y backlog (Planificador)

`POST /api/projects/:projectId/planning/generate`

Body:

json

`{   "time_horizon_weeks": 12,  "team_size": 3 }`

Respuesta:

json

`{   "roadmap": {    "project_id": "proj_123",    "phases": [      {        "name": "Fase 1 - MVP",        "goal": "Tener la plataforma basica funcionando.",        "duration_estimate_weeks": 6,        "milestones": [          "Crear modelo de datos",          "Implementar flujo de descubrimiento",          "Generar vision y arquitectura"        ]      }    ]  },  "backlog": {    "project_id": "proj_123",    "items": [      {        "id": "BL-1",        "title": "Crear estructura de proyecto backend",        "description": "Configurar proyecto base con API REST.",        "phase": "Fase 1 - MVP",        "priority": "must",        "tags": ["backend"],        "dependencies": []      }    ]  } }`

---

## 5. API para agentes (definición y evaluación)

## 5.1. Crear agentes (Agent Factory)

`POST /api/projects/:projectId/agents/define`

Body:

json

`{   "requirements": [    "Necesito un agente que hable con el usuario y genere la vision.",    "Necesito un agente que a partir de la vision genere una arquitectura."  ] }`

Respuesta:

json

`{   "agents": [    {      "id": "agent_discovery",      "name": "Agente de descubrimiento",      "role": "descubrimiento_producto",      "goal": "Entender la idea del usuario y generar una vision estructurada.",      "inputs": ["user_messages", "project_context"],      "outputs": ["VisionDocument"],      "tools": ["llm", "project_store"],      "constraints": ["no inventar datos de negocio sin aclararlo"]    },    {      "id": "agent_architecture",      "name": "Agente arquitecto",      "role": "arquitectura_plataforma",      "goal": "Disenar la arquitectura MVP.",      "inputs": ["VisionDocument", "tech_preferences", "constraints"],      "outputs": ["ArchitectureProposal"],      "tools": ["llm", "patterns_library"],      "constraints": ["sugerir tecnologias razonables para el equipo"]    }  ] }`

---

## 5.2. Logs y evaluación de agentes

**Registrar logs de ejecución**

`POST /api/agent-logs`

Body:

json

`{   "agent_id": "agent_discovery",  "project_id": "proj_123",  "input_summary": "Conversacion inicial con founder.",  "output_summary": "VisionDocument generado.",  "success": true,  "feedback": null }`

**Evaluar agentes**

`POST /api/projects/:projectId/agents/evaluate`

Body:

json

`{}`

Respuesta:

json

`{   "insights": [    {      "agent_id": "agent_discovery",      "issues_detected": [],      "common_failure_patterns": [],      "strengths": ["Genera buenas visiones a partir de poca informacion."],      "suggested_improvements": [        "Hacer mas preguntas sobre restricciones de tiempo y presupuesto."      ]    }  ] }`

---

## 6. API del Orquestador (opcional pero útil)

## 6.1. Disparar eventos al orquestador

`POST /api/orchestrator/events`

Body:

json

`{   "project_id": "proj_123",  "event_type": "user_action",  "event_name": "vision_confirmed",  "payload": {} }`

Respuesta:

json

`{   "next_agent": "agent_architecture",  "params": {    "project_id": "proj_123"  } }`

Luego tu backend llama internamente a `ArchitectureAgent` con esos parámetros.

---

## 7. Cómo lo usaría en la práctica (tú ahora)

1. Monta un backend con solo estos endpoints:
    
    - `POST /projects`
        
    - `POST /projects/:id/discovery/chat`
        
    - `POST /projects/:id/discovery/generate-vision`
        
    - `POST /projects/:id/architecture/generate`
        
    - `POST /projects/:id/planning/generate`
        
2. Implementa un front muy simple con:
    
    - Lista de proyectos
        
    - Wizard de nuevo proyecto + chat
        
    - Vistas de visión / arquitectura / roadmap mostrando los JSON de respuesta bonitos.
        
3. Por detrás, cada agente puede ser:
    
    - Una función que prepara un prompt y llama al LLM
        
    - Recibe el input (Vision, Arquitectura, etc.) y devuelve el schema que definimos.
        

Si me dices qué stack exacto quieres usar (por ejemplo: Node/Nest + React, o Laravel + Vue, etc.), en el próximo mensaje puedo darte un ejemplo de código de un endpoint y la “función agente” para que tengas el esqueleto real.