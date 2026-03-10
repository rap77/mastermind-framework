---
source_id: "FUENTE-607"
brain: "brain-software-06-qa-devops"
niche: "software-development"
title: "Site Reliability Engineering: How Google Runs Production Systems"
author: "Betsy Beyer, Chris Jones, Jennifer Petoff, Niall Richard Murphy (eds.)"
expert_id: "EXP-607"
type: "book"
language: "en"
year: 2016
isbn: "978-1491929124"
url: "https://sre.google/sre-book/table-of-contents/"
skills_covered: ["H5", "H8"]
distillation_date: "2026-02-27"
distillation_quality: "complete"
loaded_in_notebook: true
version: "1.1.0"
last_updated: "2026-02-27"
changelog:
  - version: "1.1.0"
    date: "2026-02-27"
    changes:
      - "Cargada en NotebookLM (notebook ID: 74cd3a81-1350-4927-af14-c0c4fca41a8e)"
  - version: "1.0.0"
    date: "2026-02-27"
    changes:
      - "Ficha creada para cubrir GAP de gestión de incidentes y SRE"
      - "Formato estándar del MasterMind Framework"
status: "active"

habilidad_primaria: "Gestión de incidentes: on-call, runbooks, postmortems y escalation"
habilidad_secundaria: "SRE como disciplina: toil elimination, error budgets operativos y confiabilidad como práctica de ingeniería"
capa: 2
capa_nombre: "Frameworks"
relevancia: "CRÍTICA — Cubre el GAP de gestión de incidentes. Observability Engineering define los SLOs y las alertas; el SRE Book define qué hacer cuando la alerta suena: cómo responder, escalar, resolver y aprender de los incidentes. Es gratuito y online."
gap_que_cubre: "Gestión de incidentes (on-call, runbooks, postmortems, escalation) — cubierto parcialmente por Observability Engineering pero sin el proceso operativo completo"
---

# FUENTE-607: Site Reliability Engineering (Google SRE Book)

## Tesis Central

> La confiabilidad de un sistema no es una propiedad que se consigue una vez: es el resultado de una práctica de ingeniería continua. Los ingenieros de SRE (Site Reliability Engineering) aplican principios de software a los problemas de operaciones: automatizan el trabajo repetitivo (toil), definen SLOs como contrato de confiabilidad, y gestionan los incidentes como sistemas a mejorar, no como emergencias a sobrevivir. El objetivo no es cero incidentes sino recuperarse tan rápido que el usuario apenas lo note.

---

## 1. Principios Fundamentales

> **P1: El toil es el enemigo del SRE — automatizar o eliminar el trabajo manual repetitivo**
> "Toil" es el trabajo operativo manual, repetitivo, automatable, reactivo, y sin valor duradero. Si un SRE pasa más del 50% de su tiempo en toil (ejecutar scripts manualmente, responder alertas no accionables, hacer configuraciones repetitivas), la organización está fallando. El tiempo ahorrado de toil se reinvierte en automatización que elimina más toil.
> *Contexto: Hacer un inventario del trabajo del equipo. Clasificar cada tarea: ¿es toil? ¿Puede automatizarse? ¿Debe eliminarse? El toil no escalado destruye la productividad del equipo a medida que el sistema crece.*

> **P2: El error budget es el mecanismo de balance entre velocidad e confiabilidad**
> Si el SLO es 99.9%, el error budget es 0.1% del tiempo (≈43 minutos/mes). Mientras haya error budget disponible, el equipo puede deployar con libertad. Cuando se agota, el equipo congela releases y trabaja en confiabilidad. Este mecanismo convierte el debate "velocidad vs. estabilidad" en una política objetiva, no política.
> *Contexto: El error budget requiere acuerdo previo entre ingeniería y negocio. Sin ese acuerdo, cuando se agota el budget, la discusión vuelve a ser subjetiva. El acuerdo es: "si se agota el budget, paramos features."*

> **P3: Los incidentes deben tener un Incident Commander claro**
> Durante un incidente, el mayor peligro no es la falta de conocimiento técnico sino la falta de coordinación: todos hacen cosas en paralelo, nadie sabe qué está probando el otro, se pisan los cambios. El Incident Commander (IC) no arregla el problema técnico: coordina al equipo, comunica a stakeholders, y mantiene el orden.
> *Contexto: Antes del primer incidente grave, definir: ¿quién es el IC? ¿Cómo se declara un incidente? ¿Cómo se escala? Improvisar durante el incidente es la causa más común de incidentes que duran horas cuando deberían durar minutos.*

> **P4: Postmortems blameless son la unidad de aprendizaje organizacional**
> Un postmortem sin culpa no significa que nadie sea responsable: significa que la causa raíz siempre se encuentra en el sistema, no en la persona. "El operador borró la base de datos" no es una causa raíz: "el sistema permitía borrar la base de datos de producción con un comando sin confirmación ni backup automático" sí lo es.
> *Contexto: Todo incidente con impacto a usuarios requiere un postmortem escrito y compartido. Los postmortems son activos de la organización: revelan patrones sistémicos que se acumulan con el tiempo.*

> **P5: La confiabilidad se diseña desde la arquitectura, no se añade después**
> Los sistemas altamente confiables tienen redundancia, graceful degradation, timeouts, circuit breakers, y fallbacks diseñados desde el inicio. Añadir confiabilidad a un sistema ya en producción es posible pero 10x más costoso. La pregunta es: ¿qué pasa si este componente falla? debe responderse en el diseño.
> *Contexto: En el design review de cualquier sistema nuevo, preguntar explícitamente: ¿qué pasa si la base de datos no responde? ¿Si el servicio externo X está caído? ¿Si hay un spike de 10x el tráfico normal?*

---

## 2. Frameworks y Metodologías

### Framework 1: Gestión de Incidentes — El Proceso Completo

**Propósito:** Responder a incidentes de forma coordinada, rápida y sin caos, independientemente de la severidad.
**Cuándo usar:** Siempre que una alerta indique impacto a usuarios o riesgo de impacto inminente.

**Paso 1 — Detección y declaración:**
- La alerta suena (o alguien reporta el problema)
- La primera persona en responder evalúa: ¿hay impacto real a usuarios?
- Si sí → declara el incidente formalmente (en Slack, PagerDuty, o el canal designado)
- Asigna un Incident Commander (puede ser quien lo detectó inicialmente)
- Define la severidad inicial (SEV1: crítico/down, SEV2: degradado, SEV3: impacto menor)

**Paso 2 — Comunicación inicial (dentro de los primeros 5 minutos):**
- El IC notifica a los stakeholders relevantes: "Tenemos un SEV2 en el servicio de checkout. Impacto estimado: 15% de usuarios no pueden completar compras. Investigando. Próxima actualización en 15 minutos."
- Comunicar antes de tener respuestas es correcto: la ausencia de comunicación en un incidente es peor que comunicar incertidumbre.

**Paso 3 — Investigación y mitigación:**
- Los ingenieros trabajan en paralelo pero el IC coordina: "Tú investiga los logs del servicio A. Tú verifica la base de datos. Yo monitoreo el error rate."
- Principio: **mitigar primero, investigar después.** Si hay un rollback disponible, hacer el rollback aunque no se entienda la causa raíz. El servicio primero.
- El IC mantiene un timeline en tiempo real (en el canal del incidente o en un doc compartido)

**Paso 4 — Resolución y cierre:**
- El error rate vuelve a niveles normales
- El IC declara el incidente cerrado
- Comunicación final a stakeholders: duración total, impacto estimado, acción tomada
- Se designa el dueño del postmortem (normalmente quien llevó la investigación técnica)

**Paso 5 — Postmortem (dentro de las 48-72 horas):**
- Ver Framework 2

**Output esperado:** Timeline documentado del incidente, comunicaciones enviadas, y postmortem programado.

---

### Framework 2: Postmortem Blameless — Estructura y Proceso

**Propósito:** Extraer aprendizaje sistémico de cada incidente para que no se repita.
**Cuándo usar:** Todo incidente SEV1 o SEV2, y los SEV3 que tengan lecciones relevantes. Hacerlo dentro de 48-72 horas mientras los detalles están frescos.

**Estructura del documento de postmortem:**

```markdown
# Postmortem: [Título descriptivo del incidente]
**Fecha:** YYYY-MM-DD
**Duración:** X horas Y minutos
**Severidad:** SEV1/SEV2/SEV3
**Dueño:** [Nombre]
**Estado:** Borrador / En revisión / Finalizado

## Resumen ejecutivo (2-3 oraciones)
Qué pasó, cuánto duró, cuál fue el impacto, qué lo causó.

## Impacto
- Usuarios afectados: estimado X% por Y minutos
- Transacciones fallidas: estimado N
- Impacto de negocio: $X en revenue perdido (si se puede calcular)

## Timeline de eventos
| Hora | Evento |
|------|--------|
| 14:03 | Primera alerta disparada (latencia p99 > 2s) |
| 14:07 | Ingeniero on-call detecta la alerta |
| 14:09 | Incidente declarado SEV2 |
| ... | ... |
| 15:47 | Rollback completado, error rate vuelve a 0.1% |
| 15:52 | Incidente cerrado |

## Causa raíz
Descripción técnica de qué falló y por qué. Usar 5 Whys para llegar al sistema:
- ¿Por qué el servicio falló? → Timeout en la conexión a la DB
- ¿Por qué hubo timeout? → El pool de conexiones estaba exhausto
- ¿Por qué se exhaustó? → Un deploy nuevo introdujo una query N+1 que multiplicó las conexiones
- ¿Por qué pasó el deploy? → El pipeline no tiene tests de performance que detecten queries N+1
- ¿Por qué no hay esos tests? → Nunca se definieron como parte del Definition of Done

## Qué salió bien
- La alerta disparó en menos de 3 minutos del inicio del problema
- El IC coordinó bien la comunicación con stakeholders
- El rollback fue ejecutado correctamente en 8 minutos

## Qué salió mal
- El pipeline no detectó la regresión de performance antes del deploy
- La comunicación inicial tardó 15 minutos (debería ser < 5)
- No había runbook para este tipo de fallo

## Action items
| Acción | Dueño | Fecha límite | Prioridad |
|--------|-------|--------------|-----------|
| Agregar tests de N+1 queries al pipeline | [Nombre] | YYYY-MM-DD | P1 |
| Crear runbook para "pool de conexiones exhausto" | [Nombre] | YYYY-MM-DD | P1 |
| Documentar proceso de comunicación inicial | [Nombre] | YYYY-MM-DD | P2 |
```

**Reglas del postmortem:**
- Nunca mencionar nombres en el contexto de "quién causó el problema"
- Los action items tienen dueño y fecha límite — sin esto son decoración
- El postmortem se comparte con toda la organización de ingeniería
- Se hace una revisión de los action items en 30 días

**Output esperado:** Documento finalizado, compartido, con action items asignados y trackeados.

---

## 3. Modelos Mentales

| Modelo | Descripción | Aplicación Práctica |
|--------|-------------|---------------------|
| **Toil vs. Engineering work** | El toil es trabajo manual, repetitivo y sin valor duradero. El engineering work crea sistemas que reducen futuro toil. El 50/50 es el balance objetivo: si el equipo gasta más del 50% en toil, está en un ciclo donde el toil genera más toil. | Inventariar el trabajo semanal del equipo. Etiquetar cada tarea como toil o engineering. Si la proporción está mal, priorizar automatización como trabajo de ingeniería formal, no como "algo que haremos cuando tengamos tiempo." |
| **The Wheel of Misfortune** | Ejercicio de simulación: el equipo practica responder a incidentes ficticios (game day). Un "villain" introduce un fallo en staging; el equipo responde como si fuera real. Se evalúa la coordinación, los runbooks, y las herramientas. | Hacer un game day trimestral. Es la única forma de saber si los runbooks funcionan y si el equipo sabe coordinarse bajo presión antes de que ocurra un incidente real. |
| **Cascading failures** | Los sistemas distribuidos fallan en cascada: el servicio A lentifica → las conexiones al servicio B se agotan → B falla → C empieza a fallar. El fallo original puede ser pequeño; el impacto, masivo. | Al hacer un postmortem de un incidente en cascada, identificar dónde estaba el circuit breaker que debería haber cortado la cascada. Si no había, añadirlo es el action item más importante. |
| **Graceful degradation** | En lugar de fallar completamente cuando un componente no funciona, el sistema degrada su funcionalidad: el buscador muestra resultados cacheados, el checkout desactiva las recomendaciones pero sigue procesando pagos. | Al diseñar un servicio, definir explícitamente: ¿cuál es el comportamiento degradado si cada dependencia falla? Implementar los fallbacks antes del primer incidente, no durante. |

---

## 4. Criterios de Decisión

| Situación | Prioriza | Sobre | Por qué |
|-----------|----------|-------|---------|
| Incidente activo: causa raíz desconocida pero hay rollback disponible | Hacer el rollback inmediatamente | Seguir investigando para entender la causa antes de revertir | El servicio primero. La causa raíz puede investigarse con el sistema estable. Cada minuto de investigación con usuarios impactados tiene costo real. |
| On-call: alerta a las 3am que no tiene impacto real a usuarios | Silenciar la alerta y crear un ticket para arreglarla mañana | Quedarse despierto investigando | Las alertas sin impacto real son toil puro y destruyen la calidad de vida del equipo. Una alerta que no requiere acción inmediata no debería existir. |
| ¿Hacer postmortem de un SEV3 menor? | Sí, si reveló un patrón sistémico nuevo | No, si fue un incidente aislado bien entendido | Los incidentes menores frecuentes suelen ser señal de un problema sistémico mayor. Tres SEV3 del mismo tipo son más importantes que un SEV1 aislado. |
| Error budget agotado: ¿deployar un fix crítico de seguridad? | Sí, con el acuerdo explícito de las partes | No deployar nada hasta el próximo mes | El error budget es una política, no una ley física. Los fixes de seguridad críticos son excepciones documentadas. Lo importante es que la excepción sea explícita y consensuada. |

---

## 5. Anti-patrones

| Anti-patrón | Por qué es malo | Qué hacer en su lugar |
|-------------|-----------------|----------------------|
| **"Heroe on-call" — una sola persona que sabe cómo arreglar todo** | Cuando esa persona no está disponible, los incidentes duran horas. Además, el héroe se quema inevitablemente. Es un SPOF humano que eventualmente falla. | Documentar runbooks para los incidentes más frecuentes. Hacer rotación de on-call obligatoria. Hacer que los runbooks los escriba quien responde al incidente, no el experto original. |
| **Postmortems que se hacen pero cuyos action items nadie hace** | El postmortem se convierte en teatro: se documenta el problema, se prometen arreglos, y el siguiente incidente es el mismo. La organización pierde fe en el proceso. | Los action items del postmortem van al backlog como tickets de P1 con fecha límite. Se revisan en 30 días. Si no se hicieron, se discute en la retrospectiva. |
| **On-call sin runbooks = on-call con pánico** | Sin runbooks, cada respuesta a un incidente requiere que el ingeniero on-call reconstruya el conocimiento desde cero bajo presión. Los tiempos de resolución son impredecibles y dependen de quién esté on-call. | Para cada alerta que dispara frecuentemente, debe existir un runbook: "Si ves esta alerta, haz estos pasos. Si esos pasos no resuelven, escala a X." El runbook lo escribe quien respondió al incidente más reciente. |
| **Alertar sobre síntomas internos, no sobre impacto a usuario** | "CPU al 80%" no significa que el usuario esté teniendo una mala experiencia. Puede ser completamente normal. Estas alertas crean alert fatigue sin valor. | Alertar sobre síntomas de experiencia de usuario: error rate > umbral del SLO, latencia p99 > umbral del SLO, tasa de transacciones exitosas < umbral. Si el usuario está bien, el sistema está bien. |
| **Culpar a personas en el postmortem** | Destruye la seguridad psicológica. Los próximos incidentes se ocultarán o minimizarán para evitar ser el culpable. El sistema no mejora porque los problemas se esconden. | El postmortem es blameless: "el sistema permitió que X ocurriera" en lugar de "X cometió un error." Los nombres aparecen en el timeline de hechos, no en el análisis de causas. |

---

## 6. Casos y Ejemplos Reales

### Caso 1: Google — El origen de SRE y el primer error budget

- **Situación:** Google necesitaba escalar sus operaciones sin escalar proporcionalmente el equipo de operaciones. El modelo tradicional (equipo de ops que gestiona infraestructura) no escalaba.
- **Decisión:** Ben Treynor Sloss (VP Engineering) creó el concepto de SRE: ingenieros de software que se enfocan en confiabilidad, con un límite explícito del 50% de tiempo en toil. El resto se invierte en automatización. El error budget nació de la necesidad de un mecanismo objetivo para decidir cuánto tiempo invertir en features vs. confiabilidad.
- **Resultado:** Google puede operar servicios a escala masiva (Gmail, Search, YouTube) con equipos de SRE proporcionalmente pequeños. El SRE Book documenta sus prácticas y se convirtió en el estándar de la industria.
- **Lección:** SRE no es "renombrar a ops." Es una función de ingeniería con un mandato claro: automatizar el toil y mejorar la confiabilidad sistémicamente.

### Caso 2: Stripe — Postmortems como activos de la organización

- **Situación:** Stripe tiene miles de clientes procesando pagos. Un incidente que afecta el procesamiento de pagos tiene impacto directo en ingresos de sus clientes. La presión para no tener incidentes es enorme.
- **Decisión:** Adoptaron una cultura de postmortems blameless y los publican internamente con la organización completa. Crearon una base de datos de postmortems buscable donde cualquier ingeniero puede ver qué falló en el pasado.
- **Resultado:** La base de datos de postmortems permite detectar patrones: si el mismo tipo de fallo aparece 3 veces en distintos servicios, es una señal de un problema sistémico en la plataforma. Esto permitió arreglar problemas de raíz antes de que causaran incidentes en más servicios.
- **Lección:** Los postmortems son más valiosos como colección que como documentos individuales. Los patrones emergen cuando se puede buscar y analizar múltiples postmortems.

### Caso 3: Atlassian — Game Days para preparación de incidentes

- **Situación:** El equipo de Jira Cloud sabía que tenían runbooks y alertas, pero nunca los habían probado bajo presión real. La preocupación era: ¿los runbooks realmente funcionan? ¿El equipo sabe coordinarse?
- **Decisión:** Implementaron Game Days trimestrales: un "villain" introduce un fallo controlado en staging, el equipo responde como si fuera un incidente real de producción. Se evalúa todo: detección, comunicación, coordinación, runbooks, tiempo de resolución.
- **Resultado:** En el primer Game Day descubrieron que 3 de sus runbooks tenían instrucciones desactualizadas. El tiempo promedio de resolución en Game Days bajó de 45 minutos a 12 minutos en 4 trimestres. Cuando llegó el primer incidente real de SEV1, el equipo lo resolvió en 8 minutos.
- **Lección:** Los runbooks y los procesos de incidentes deben practicarse regularmente. La presión de un incidente real no es el momento de aprender.

---

## Conexión con el Cerebro #6

| Habilidad del Cerebro | Aporte de esta fuente |
|------------------------|----------------------|
| H5 — Gestión de incidentes y postmortems | Esta fuente es la referencia definitiva de gestión de incidentes: el proceso completo (detección → IC → mitigación → postmortem), los runbooks, la escalation, y la cultura de blameless postmortems. |
| H8 — SRE como disciplina (toil, error budgets operativos) | Define qué es SRE, cómo se diferencia de DevOps, el concepto de toil y el mecanismo operativo del error budget como política de balance velocidad/confiabilidad. |

---

## Preguntas que el Cerebro puede responder

1. ¿Cómo estructuramos la respuesta a un incidente cuando todo el mundo está haciendo cosas en paralelo y nadie sabe el estado?
2. ¿Qué debe contener un runbook para que sea útil a las 3am bajo presión?
3. ¿Cómo hacemos postmortems que realmente generen cambios, no solo documentación?
4. ¿Cómo definimos las severidades de incidentes y cuándo escalar?
5. ¿Qué es un Game Day y cómo lo organizamos para preparar al equipo?
6. ¿Cómo convencemos al equipo de que el tiempo en automatización es más valioso que el tiempo respondiendo alertas?
