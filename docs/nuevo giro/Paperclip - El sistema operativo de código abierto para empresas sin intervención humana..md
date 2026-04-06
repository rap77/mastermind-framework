## _Si OpenClaw es el empleado, Paperclip es la empresa._

El panorama de los agentes de IA experimentó un cambio radical a principios de 2026. OpenClaw, el asistente de IA autónomo creado por Peter Steinberger, ya había demostrado que un solo agente podía reemplazar a un asistente personal completo. Podía gestionar la bandeja de entrada, extraer información de sitios web, enviar correos electrónicos y ejecutar tareas recurrentes de forma autónoma a través de WhatsApp, Telegram y Slack.

Pero un solo empleado no hace una empresa.

¿Qué ocurre cuando necesitas que diez agentes trabajen juntos: un redactor de marketing, un revisor de código, un gestor de correo electrónico y un analista de datos, todos alineados con los mismos objetivos comerciales y operando de forma autónoma? Ese es el problema de coordinación que Paperclip se creó para resolver.

## ¿Qué es un clip de papel?

Paperclip es un servidor Node.js de código abierto con un panel de control React que organiza equipos de agentes de IA en organizaciones estructuradas. Creado por el desarrollador anónimo @dotta, se lanzó el 4 de marzo de 2026 y superó las 30 000 estrellas en GitHub en tan solo tres semanas, convirtiéndose en uno de los repositorios de IA de código abierto de mayor crecimiento del trimestre.

Su origen es sorprendentemente práctico. @dotta dirigía un fondo de cobertura automatizado y se encontró con más de 20 pestañas de Claude Code abiertas simultáneamente. Sin contexto compartido. Sin seguimiento de costes. Sin forma de recuperar el estado tras un reinicio. Paperclip surgió de esa frustración.

El lema del repositorio lo dice todo: "Si puede recibir un latido, está contratado".

Paperclip no es un chatbot, ni un marco de agente único, ni un creador de flujos de trabajo de arrastrar y soltar. Modela empresas, con organigramas, objetivos, presupuestos y gobernanza. Se sitúa por encima de los entornos de ejecución de agentes individuales (Claude Code, OpenClaw, Codex, Cursor o cualquier agente compatible con HTTP) y proporciona la capa organizativa que les faltaba a los sistemas multiagente.

## Entendiendo OpenClaw: El agente que Paperclip orquesta

Para apreciar lo que hace Paperclip, primero hay que entender OpenClaw y el paradigma que introdujo.

OpenClaw (antes Clawdbot, luego Moltbot, tras las quejas de Anthropic por infracción de marca registrada que obligaron a cambiarle el nombre varias veces) es un asistente de IA autónomo de código abierto creado por Peter Steinberger. Se ejecuta localmente en tu ordenador y se conecta a tus aplicaciones de mensajería habituales. A diferencia de los chatbots basados ​​en la nube, que se reinician con cada sesión, OpenClaw mantiene una identidad y memoria persistentes mediante un sistema de archivos Markdown simples almacenados en tu disco duro.

## La arquitectura del espacio de trabajo

Cada agente de OpenClaw reside dentro de un directorio de espacio de trabajo, normalmente `~/.openclaw/workspace`, que contiene un conjunto de `.md`archivos que definen colectivamente la identidad y el comportamiento operativo del agente:

- **SOUL.md** es la capa de identidad. Define la personalidad, el estilo de comunicación, los valores y los límites de comportamiento del agente. Cada sesión comienza con OpenClaw leyendo este archivo. La documentación de OpenClaw lo describe como el agente "creándose a sí mismo mediante la lectura".
- **AGENTS.md** es la capa procedimental. Mientras que SOUL.md responde a la pregunta "¿quién eres?", AGENTS.md responde a la pregunta "¿qué haces y cómo?". Contiene reglas de flujo de trabajo, procedimientos operativos estándar (SOP) y lógica de decisión.
- **MEMORY.md** es la capa de persistencia. Aquí se acumulan patrones, preferencias y datos con el tiempo, lo que proporciona continuidad al agente entre sesiones.
- **HEARTBEAT.md** es la capa de autonomía. Define las tareas programadas en lenguaje natural, principalmente `cron`para tu agente. El demonio heartbeat se ejecuta cada 30 minutos por defecto.
- **El archivo TOOLS.md** describe a qué herramientas tiene acceso el agente y cómo utilizarlas.
- **El archivo USER.md** almacena información contextual sobre el operador humano: preferencias, estilo de comunicación, prioridades.
- **El archivo IDENTITY.md** contiene el nombre, la ID y los metadatos del agente para el enrutamiento.

Esta arquitectura de texto plano es una decisión de diseño deliberada. Todo se puede inspeccionar con cualquier editor de texto, se puede controlar mediante versiones con Git y es portable entre diferentes máquinas. Sin bases de datos ni formatos propietarios. Los archivos _son_ el motor.

## El mecanismo del latido cardíaco

El latido es lo que transforma a OpenClaw de un chatbot reactivo en un agente proactivo. Cada 30 minutos (configurable), el demonio Gateway activa al agente, que lee su lista de verificación HEARTBEAT.md y decide si algún elemento requiere atención. Si no hay nada que requiera atención, responde con `HEARTBEAT_OK`, que Gateway descarta silenciosamente. Si algo requiere atención, el agente actúa de forma autónoma.

Este es el mecanismo sobre el que se basa Paperclip. Cuando la documentación de OpenClaw indica que el agente puede actuar "sin necesidad de que se le solicite", se refiere a que el demonio de latidos proporciona una programación autónoma que se ejecuta independientemente de si un humano está interactuando activamente con el sistema.

## El problema de la escala

OpenClaw es excelente como agente autónomo individual. Pero las empresas reales no funcionan con un solo empleado. Cuando tienes cinco, diez o veinte agentes operando de forma independiente, cada uno con su propio SOUL.md, su propio ritmo cardíaco y su propia memoria, la coordinación se rompe rápidamente.

- No existe un contexto compartido entre los agentes.
- Sin seguimiento de costes en toda la flota
- No hay forma de recuperar el estado después de reiniciar el sistema.
- No existe ningún tipo de control sobre las acciones autónomas de los agentes.
- No existe alineación entre las acciones de los agentes individuales y los objetivos comerciales.

Este es precisamente el hueco que llena Paperclip.

## Arquitectura central de Paperclip

La arquitectura de Paperclip se basa en unos pocos elementos básicos clave que reflejan estructuras organizativas reales.

## El modelo de empresa

Cada despliegue comienza con la definición de la empresa: un nombre y una declaración de misión. Esta misión se propaga hacia abajo, de modo que cada objetivo, cada proyecto y cada tarea se remontan a ella. Cuando un agente toma un ticket, ve el historial completo:

"Estoy investigando anuncios de Facebook para Granola" (tarea actual)   
  → porque necesito crear anuncios de Facebook para nuestro software (padre)   
    → porque necesito aumentar los registros en  100 usuarios (padre)   
      → porque necesito ingresos de $ 2,000 esta semana (padre)→ porque nuestra misión es construir la aplicación de toma de notas con IA número 1  

Esta ejecución orientada a objetivos implica que los agentes siempre saben _por qué_ trabajan, no solo _qué_ hacer. Y en la práctica, esa distinción resulta ser muy importante.

## Organigramas y delegación

Paperclip implementa estructuras organizativas jerárquicas. Una configuración típica se ve así:

- **El director ejecutivo** recibe la misión de la empresa, la divide en objetivos estratégicos y los delega a sus subordinados directos.
- **El agente CTO** se encarga de las decisiones técnicas y delega las tareas de codificación a los agentes de ingeniería.
- **El agente de CMO** gestiona la estrategia de marketing, delega la creación de contenido y la ejecución de las campañas.
- **Los agentes de ingeniería** ejecutan tareas de codificación específicas asignadas por el CTO.
- **El agente de control de calidad** revisa los resultados de otros agentes antes de que lleguen a la revisión humana.

La delegación fluye automáticamente en todos los niveles del organigrama. Cuando el director ejecutivo crea un proyecto, este pasa al director de tecnología, quien lo divide en tareas para los ingenieros. Las solicitudes entre equipos se dirigen al agente más adecuado.

## Latidos del corazón en un clip de papel

Paperclip extiende el concepto de latido de OpenClaw a una capa de coordinación. Los agentes se activan según un cronograma, revisan su cola de trabajo, ejecutan las tareas asignadas e informan a sus superiores. La principal diferencia con los latidos independientes de OpenClaw es que Paperclip coordina _entre_ los agentes.

Entre latidos, los agentes permanecen inactivos. No se queman tokens ni se generan costos. Esto es muy diferente a tener agentes funcionando las 24 horas del día, los 7 días de la semana. Se asemeja más a que los empleados revisen su bandeja de entrada periódicamente.

## El sistema de boletos

En Paperclip, toda la comunicación se realiza mediante tickets estructurados. Cada instrucción, respuesta, llamada a herramienta y decisión se registra con trazabilidad completa. El sistema utiliza un registro de auditoría de solo adición: sin ediciones ni eliminaciones, total responsabilidad.

Esto es más importante de lo que parece. Cuando se ejecutan veinte agentes en sesiones de terminal sin procesar, no queda rastro de lo sucedido, no hay forma de auditar las decisiones ni mecanismo para averiguar por qué algo salió mal.

## Controles presupuestarios

Cada agente dispone de un presupuesto mensual de tokens. Al alcanzar el 80 % de utilización, Paperclip emite una advertencia. Al llegar al 100 %, el agente se pausa automáticamente y se bloquean las nuevas tareas. El operador humano (el «panel») puede anular este límite, pero el comportamiento predeterminado evita que los costes se disparen.

## Recibe las historias de Akshay Kalane en tu bandeja de entrada.

Regístrate gratis en Medium para recibir actualizaciones de este autor.

Suscribir

Recuérdame para iniciar sesión más rápido.

El seguimiento de costes funciona a varios niveles: por agente, por tarea, por proyecto, por objetivo y por empresa. Este nivel de detalle es crucial al gestionar un grupo de agentes que, en conjunto, podrían gastar cientos de dólares en créditos de API de la noche a la mañana.

## El sistema de adaptadores: cómo Paperclip se conecta con los agentes

Paperclip no impone ninguna preferencia sobre los entornos de ejecución de los agentes. Se conecta a los agentes mediante adaptadores, que son módulos conectables que unen la capa de orquestación de Paperclip con el entorno de ejecución en el que se ejecuta realmente el agente.

## Adaptador de proceso (agentes locales)

Para los agentes que se ejecutan en la misma máquina, Paperclip los crea como subprocesos. El `claude_local`adaptador, por ejemplo, inicia directamente las sesiones de Claude Code:

{   
  "adapterType" :  "process" ,   
  "adapterConfig" :  {   
    "adapter" :  "claude_local" ,   
    "model" :  "claude-sonnet-4-20250514" ,   
    "billingType" :  "api" ,   
    "sessionBehavior" :  "resume-or-new" ,   
    "heartbeatSchedule" :  {   
      "enabled" :  true ,   
      "intervalSec" :  1800   
    }   
  }   
}

Esta `sessionBehavior: "resume-or-new"`opción es digna de mención. Significa que los agentes reanudan el mismo contexto de tarea entre latidos en lugar de reiniciar desde cero cada vez.

## Adaptador HTTP (Agentes remotos)

Para los agentes que se ejecutan en infraestructuras separadas, incluidas las instancias remotas de OpenClaw, Paperclip se comunica mediante webhooks HTTP:

{   
  "adapterType" :  "http" ,   
  "adapterConfig" :  {   
    "url" :  "https://openclaw.example.com/invoke" ,   
    "method" :  "POST" ,   
    "headers" :  {   
      "Authorization" :  "Bearer {{OPENCLAW_TOKEN}}"   
    } ,   
    "timeoutMs" :  30000 ,   
    "payloadTemplate" :  {   
      "paperclip" :  {   
        "agentId" :  "{{agent.id}}" ,   
        "companyId" :  "{{company.id}}" ,   
        "runId" :  "{{run.id}}"   
      }   
    }   
  }   
}

Los secretos se almacenan cifrados en una `company_secrets`tabla y se inyectan en tiempo de ejecución. Nunca se incluyen de forma fija en la configuración del adaptador.

## Adaptador de puerta de enlace OpenClaw

Paperclip incluye un adaptador dedicado `openclaw_gateway`que se comunica con OpenClaw a través de su protocolo WebSocket Gateway. Este adaptador admite:

- Tramas de solicitud/respuesta estructuradas a través de WebSocket (ws:// o wss://)
- Autenticación basada en dispositivos mediante pares de claves Ed25519 con protocolo de enlace criptográfico.
- Persistencia de sesión con estrategias configurables (fija, por incidencia o por ejecución).
- Registros de eventos de transmisión analizados en formato de transcripción de Paperclip
- Emparejamiento automático en la primera conexión para una configuración sin problemas.

La configuración inicial requiere un paso de emparejamiento de dispositivos (ejecutando `openclaw devices approve --latest`), después del cual las claves de dispositivo persistentes eliminan las aprobaciones repetidas.

## Adaptadores de terceros

El modelo de adaptador es extensible. Nous Research, por ejemplo, publicó una herramienta `hermes-paperclip-adapter`que integra su agente Hermes (con más de 30 herramientas nativas, memoria persistente y compatibilidad con MCP) como un empleado de Paperclip. El adaptador ejecuta Hermes en modo de consulta única, captura la salida, analiza el uso de tokens e informa los resultados a Paperclip.

## Cómo configurar Paperclip: una guía práctica paso a paso.

## Requisitos previos

- Node.js 20+
- pnpm 9.15+ (para desarrollo desde el código fuente)
- No se requiere base de datos externa. Paperclip crea automáticamente una base de datos PostgreSQL integrada.

## Inicio rápido

La ruta más rápida es el comando de incorporación:

npx paperclipai a bordo -- sí

Esto instala todo, crea una base de datos local y abre el panel de control en `http://localhost:3100`. La configuración interactiva le guiará en la creación de su primera empresa.

## De la fuente

git clone https://github.com/paperclipai/paperclip.git   
cd paperclip   
pnpm instalar   
pnpm dev

Comandos de desarrollo útiles:

pnpm dev           # Desarrollo completo (API + UI, modo de observación)  
 pnpm dev:server    # Solo servidor  
 pnpm build         # Compilar todo  
 pnpm typecheck     # Verificación de tipos  
 pnpm test :run      # Ejecutar pruebas  
 pnpm db:generate   # Generar migración de base de datos  
 pnpm db:migrate    # Aplicar migraciones

## Creación de la primera empresa

Una vez que se inicie el panel de control:

1. **Define tu empresa.** Elige un nombre y define su misión.
2. **Establezca objetivos comerciales.** Por ejemplo, “Responder a todos los correos electrónicos de los clientes en 1 hora” o “Publicar 3 entradas de blog por semana”.
3. **Contrata un agente CEO.** Elige el entorno de ejecución que lo impulse (Claude, Codex, OpenClaw). El CEO ocupa la posición más alta en tu organigrama.
4. **Aprueba las contrataciones.** El director ejecutivo recomienda agentes adicionales. Tú apruebas cada uno y estableces presupuestos mensuales para fichas.
5. **Supervise desde el panel de control.** Observe cómo los agentes realizan sus tareas, controle los costos e intervenga cuando sea necesario.

## Integración de un agente de OpenClaw

Para conectar una instancia de OpenClaw existente:

1. En la interfaz de usuario de Paperclip, cree un nuevo agente con tipo de adaptador `openclaw_gateway`.
2. Configure la `gatewayUrl`conexión con el punto final WebSocket de su puerta de enlace OpenClaw.
3. Configure un token de autenticación en la configuración del adaptador.
4. Activar una carrera de activación.
5. En la primera conexión, apruebe el emparejamiento del dispositivo:`openclaw devices approve --latest`
6. Configure un valor persistente `devicePrivateKeyPem`en la configuración del adaptador para evitar tener que volver a aprobarlo después de reiniciar el sistema.

Una vez conectado, OpenClaw se convierte en un empleado más de la organización. Las tareas que se le asignan en Paperclip se envían a través del adaptador Gateway, y los resultados se registran en el sistema de incidencias y el registro de auditoría de Paperclip.

## Flujo de trabajo multiagente: un ejemplo real

Así podría ser el flujo de contenido para una agencia de marketing autónoma en Paperclip:

- **Estratega de contenido** : investigación de temas, openclaw_gateway, OpenClaw
- **Escritor** — Creación de borradores, proceso, Claude Code
- **Editor** — Revisión y perfeccionamiento, proceso, Claude Code
- **Editor** — Publicación final, http, webhook personalizado

El flujo funciona así:

1. El agente **del CEO** recibe el objetivo de "Publicar 3 entradas de blog por semana" y crea tareas para el estratega de contenido.
2. El **estratega de contenido** (OpenClaw) supervisa los temas de actualidad, investiga palabras clave y envía propuestas de temas como tickets.
3. El **escritor** selecciona los temas aprobados y elabora los borradores.
4. El **editor** revisa los borradores para comprobar su calidad y coherencia.
5. El **editor** publica el contenido aprobado a través de API externas.

Cada paso es un ticket. Cada transferencia queda registrada. Cada agente opera dentro de su presupuesto. El operador humano ve todo desde un único panel de control y solo interviene en los puntos de aprobación.

## Gobernanza y seguridad

## Puertas de aprobación

Determinadas acciones requieren aprobación humana por defecto. Por ejemplo, la contratación de nuevos agentes está sujeta a la aprobación de la junta directiva. Los cambios de configuración se versionan con soporte para reversión.

## Registro de auditoría

Cada conversación, decisión, llamada a herramienta y solicitud de API se registra en un historial de solo escritura. Nada se puede editar ni eliminar. Cuando surgen problemas con los sistemas de agentes autónomos (y surgirán), se necesita un registro completo de lo ocurrido y sus causas.

## Consideraciones de seguridad

Cisco ha señalado a OpenClaw como un riesgo potencial para la seguridad debido a sus amplios permisos de sistema y su vulnerabilidad a la inyección de comandos. La capa de gobernanza de Paperclip añade medidas de seguridad estructuradas: los límites presupuestarios restringen el alcance del impacto, los controles de aprobación limitan las decisiones autónomas y los registros de auditoría proporcionan trazabilidad. Sin embargo, estas son medidas de seguridad complementarias, no sustituyen el aislamiento adecuado de los agentes.

Cabe destacar que se identificó y corrigió una vulnerabilidad (CVE-2026–25253) en OpenClaw, y la integración con VirusTotal (v2026.2.6) ahora ofrece análisis de seguridad para las habilidades aportadas por la comunidad.

## Lo que viene: Clipmart y más allá

La hoja de ruta de Paperclip incluye **Clipmart** , un mercado donde los usuarios pueden descargar plantillas de empresas prediseñadas: agencias de contenido, mesas de negociación, estudios de desarrollo, todas con estructuras organizativas, configuraciones de agentes y habilidades integradas. Importación con un solo clic a tu instancia de Paperclip.

El concepto de “empresas importables y compartibles” podría convertirse en la característica más importante de la hoja de ruta. En lugar de configurar agentes desde cero, se descargaría una plantilla organizativa probada y se personalizaría. Es como una estrategia de captación de talento para equipos de agentes.

Otros puntos en la hoja de ruta:

- Integración del sistema de venta de entradas propio (conexión con las herramientas de gestión de proyectos existentes)
- Un sistema de complementos para ampliar las capacidades.
- **Modo Maximizador** , una función comentada en podcasts recientes por el creador que aún no se ha detallado por completo.

## ¿Cuándo se debe usar un clip?

**Paperclip tiene sentido cuando:**

- Gestionas cinco o más agentes de IA y necesitas coordinación.
- Usted desea un funcionamiento autónomo las 24 horas del día, los 7 días de la semana, con supervisión humana a nivel de la junta directiva.
- Necesitas visibilidad de los costos y control del presupuesto en todos los agentes.
- Necesitas un registro de auditoría para las decisiones y acciones de los agentes.
- Estás creando un negocio centrado en la IA con múltiples roles especializados.

**El clip de papel es excesivo cuando:**

- Solo necesitas un agente. Una sesión independiente de OpenClaw o Claude Code es suficiente.
- Necesitas una herramienta de revisión de código. Paperclip organiza el trabajo, no las solicitudes de extracción.
- Necesitas un creador de flujos de trabajo con la función de arrastrar y soltar. Paperclip modela organizaciones, no flujos de trabajo.

## El panorama general

2025 fue el año en que los agentes de IA individuales demostraron su valía. OpenClaw demostró que un agente autónomo, con el sistema de memoria y la programación de latidos adecuados, podía realizar un trabajo significativo sin supervisión constante.

Todo apunta a que 2026 será el año de las empresas de IA. La transición va desde las herramientas de un solo agente a la orquestación multiagente. Microsoft lanzó Copilot Cowork. Anthropic lanzó Claude Marketplace. Nvidia está desarrollando NemoClaw. Y proyectos de código abierto como Paperclip plantean una pregunta completamente diferente: ¿qué pasaría si prescindieras de un proveedor empresarial y crearas tu propia empresa?

La idea central de Paperclip es que el verdadero desafío en la IA multiagente no reside en hacer que los agentes individuales sean más inteligentes, sino en lograr que se coordinen. Y la coordinación es, en esencia, un problema de diseño organizacional: estructuras de informes, flujo de información, patrones de delegación, bucles de retroalimentación y vías de escalamiento.

Las herramientas aún están en fase inicial. Hay aspectos por pulir. Pero el modelo arquitectónico que trata a los sistemas multiagente como empresas en lugar de simples flujos de trabajo representa un cambio real en nuestra concepción de las fuerzas laborales de IA autónoma. Seguiré de cerca este sector durante los próximos meses.

_Paperclip es de código abierto, tiene licencia MIT y se aloja en servidores propios. No se requiere cuenta._

- **GitHub:** [github.com/paperclipai/paperclip](https://github.com/paperclipai/paperclip)
- **Sitio web:** [paperclip.ing](https://paperclip.ing/)