---
source_id: "FUENTE-502"
brain: "brain-software-05-backend"
niche: "software-development"
title: "Designing Data-Intensive Applications: The Big Ideas Behind Reliable, Scalable, and Maintainable Systems"
author: "Martin Kleppmann"
expert_id: "EXP-005"
type: "book"
language: "en"
year: 2017
isbn: "978-1449373320"
url: "https://dataintensive.net"
skills_covered: ["H2", "H4", "H5"]
distillation_date: "2026-02-27"
distillation_quality: "complete"
loaded_in_notebook: true
version: "1.0.0"
last_updated: "2026-02-27"
changelog:
  - version: "1.0.0"
    date: "2026-02-27"
    changes:
      - "Ficha creada con destilación completa"
      - "Formato estándar del MasterMind Framework"
status: "active"

habilidad_primaria: "Sistemas distribuidos y bases de datos a escala"
habilidad_secundaria: "Decisiones de almacenamiento: SQL vs NoSQL, consistencia vs disponibilidad"
capa: 1
capa_nombre: "Base Conceptual"
relevancia: "CRÍTICA — La biblia de sistemas de datos modernos. Cubre todo lo que el Cerebro #5 necesita para decidir cómo almacenar, procesar y mover datos."
gap_que_cubre: "Criterios profundos para decisiones de bases de datos, replicación, particionado y procesamiento de streams"
---

# FUENTE-502: Designing Data-Intensive Applications (DDIA)

## Tesis Central

> Los sistemas modernos no fallan por falta de CPU — fallan por complejidad en el manejo de datos: inconsistencias, particiones de red, lecturas lentas, escrituras conflictivas. Entender los trade-offs reales (no los que dice el marketing) de cada tecnología de datos es la habilidad más valiosa de un backend engineer.
> Es el mapa de todos los trade-offs que importan cuando los datos crecen.

---

## 1. Principios Fundamentales

> **P1: Fiabilidad, Escalabilidad y Mantenibilidad son el Triángulo Base**
> — Fiabilidad: el sistema funciona correctamente incluso cuando algo falla (hardware, software, humano).
> — Escalabilidad: el sistema puede manejar carga creciente de forma razonable.
> — Mantenibilidad: personas distintas al autor original pueden operar y evolucionarlo.
> *Contexto de aplicación: Al inicio del diseño. Preguntarse explícitamente cuál de los tres es la prioridad en este contexto. Un script interno prioriza mantenibilidad. Un sistema de pagos, fiabilidad.*

> **P2: El Teorema CAP es un Trade-off, No una Elección**
> En presencia de una partición de red (P), debes elegir entre Consistencia (C) o Disponibilidad (A). No puedes tener ambas. CP: el sistema rechaza requests para no dar datos incorrectos (ZooKeeper, HBase). AP: el sistema da respuestas potencialmente desactualizadas (Cassandra, DynamoDB).
> *Contexto de aplicación: Al seleccionar una base de datos distribuida. ¿Qué es peor para el negocio: datos incorrectos o sistema caído?*

> **P3: ACID No es Todo o Nada**
> Atomicidad, Consistencia, Aislamiento y Durabilidad son propiedades deseables, pero cada base de datos las implementa de forma diferente. "Isolation" en PostgreSQL no es lo mismo que en MySQL. Conocer los niveles de aislamiento (Read Uncommitted → Serializable) es esencial para evitar bugs sutiles en producción.
> *Contexto de aplicación: Siempre que haya transacciones concurrentes. Los bugs de race condition en producción casi siempre son problemas de aislamiento.*

> **P4: Encodings y Schemas Evolucionan**
> Los datos viven más que el código. Un schema que no soporta evolución forward/backward compatible bloquea los deployments. JSON sin schema da flexibilidad pero oculta incompatibilidades. Protobuf y Avro dan lo mejor de los dos mundos.
> *Contexto de aplicación: Al diseñar la capa de comunicación entre servicios. Si cambiar un campo rompe clientes existentes, el schema no es compatible hacia atrás.*

> **P5: Batch vs Stream es una Distinción Fundamental**
> El procesamiento batch (Hadoop, Spark) trabaja sobre datos acumulados. El procesamiento stream (Kafka, Flink) trabaja sobre eventos en tiempo real. La mayoría de los sistemas modernos necesitan ambos. Los dos tienen trade-offs de latencia vs throughput vs fault-tolerance.
> *Contexto de aplicación: Al diseñar pipelines de datos. Batch para reportes históricos. Stream para alertas y reacciones en tiempo real.*

---

## 2. Frameworks y Metodologías

### Framework 1: Decision Tree de Base de Datos

**Propósito:** Elegir la tecnología de almacenamiento correcta para cada caso de uso.
**Cuándo usar:** Al iniciar un proyecto o al agregar un nuevo componente de datos.

**Pasos:**
1. **¿El patrón de acceso es principalmente por clave primaria?** → Key-Value store (Redis, DynamoDB) para alta performance.
2. **¿Los datos tienen relaciones complejas entre entidades?** → Base de datos relacional (PostgreSQL). Las joins son el superpoder de SQL.
3. **¿El schema cambia frecuentemente o es heterogéneo?** → Document store (MongoDB). Útil cuando cada documento tiene estructura diferente.
4. **¿Necesitas búsqueda full-text o por similitud?** → Search engine (Elasticsearch, Meilisearch).
5. **¿El patron es write-heavy y lecturas son simples?** → Columnar store (Cassandra) para alta disponibilidad de escritura.
6. **¿Necesitas recorridos de grafos?** → Graph DB (Neo4j). Las joins de N niveles en SQL son prohibitivas.
7. **¿Es datos de series de tiempo?** → TimeSeries DB (InfluxDB, TimescaleDB). Optimizadas para ese patrón.

**Output esperado:** Selección de tecnología justificada en el patrón de acceso, no en preferencias personales o hype.

---

### Framework 2: Estrategia de Replicación y Particionado

**Propósito:** Diseñar cómo los datos se distribuyen para escalar lecturas y escrituras.
**Cuándo usar:** Cuando una sola máquina no puede manejar la carga de datos.

**Pasos:**
1. **Identifica el bottleneck:** ¿Lecturas, escrituras, o almacenamiento?
2. **Para lecturas:** Replicación (1 leader + N followers). Las lecturas se distribuyen a followers. Las escrituras van al leader.
3. **Para escrituras o volumen:** Particionado (sharding). Dividir datos por rango de clave o hash.
4. **Elige la estrategia de replicación:** Síncrona (durabilidad pero latencia), Asíncrona (performance pero lag), Semi-síncrona (balance).
5. **Define quién resuelve conflictos de escritura:** Last Write Wins, CRDTs, o resolución manual.
6. **Monitorea replication lag:** Si el follower está muy atrás, las lecturas darán datos obsoletos.

**Output esperado:** Plan de escalado de datos con trade-offs explícitos documentados.

---

## 3. Modelos Mentales

| Modelo | Descripción | Aplicación Práctica |
|--------|-------------|---------------------|
| **Logs como Fuente de Verdad** | Un append-only log de eventos es la representación más duradera y flexible de los datos. Las bases de datos derivadas (SQL, search index, cache) son vistas materializadas de ese log. | Al diseñar sistemas complejos: el log de Kafka es la verdad. PostgreSQL es una vista derivada. |
| **Lectura vs Escritura Optimizada** | No hay una estructura de datos perfecta para ambas. B-Trees son balance. LSM-Trees son rápidos en escritura. Column stores son rápidos en lectura analítica. | Elegir el engine según si el workload es OLTP (operacional) u OLAP (analítico). |
| **Idempotencia** | Una operación idempotente puede ejecutarse múltiples veces con el mismo resultado. Esencial en sistemas distribuidos donde los retries son inevitables. | Siempre diseñar operaciones de API como idempotentes. Usar idempotency keys en pagos y operaciones críticas. |
| **Backpressure** | Cuando un consumer es más lento que el producer, el sistema necesita un mecanismo para señalar "ve más despacio". Sin backpressure, los buffers explotan. | En Kafka, el lag del consumer group es la métrica de backpressure. Si crece indefinidamente, agregar consumers o optimizar procesamiento. |
| **Partición de Fallas** | En un sistema distribuido, los nodos pueden fallar y los mensajes pueden perderse. La pregunta no es "si" fallará, sino "cuando" y "cómo manejar el fallo". | Diseñar para el caso de fallo, no para el caso exitoso. ¿Qué pasa si el servicio de pagos no responde? |

---

## 4. Criterios de Decisión

| Situación | Prioriza | Sobre | Por qué |
|-----------|----------|-------|---------|
| Sistema financiero, inventario | Consistencia fuerte (CP) | Disponibilidad | Datos incorrectos son peor que sistema caído en contextos donde el dinero o el stock importa. |
| Red social, feeds, analytics | Disponibilidad (AP) | Consistencia fuerte | Un like que tarda en propagarse es aceptable. Un feed caído es inaceptable. |
| Datos relacionales con joins complejos | PostgreSQL | MongoDB | Las relaciones complejas necesitan joins. MongoDB lo puede hacer pero es forzado. |
| Alto volumen de escrituras, lectura simple por clave | Cassandra / DynamoDB | PostgreSQL | Cassandra escala escrituras horizontalmente. PostgreSQL tiene un solo writer por default. |
| Cache de sesiones, rate limiting | Redis | Any DB | Redis en memoria es 10-100x más rápido que cualquier DB en disco para operaciones simples. |
| Búsqueda full-text o fuzzy | Elasticsearch / Meilisearch | LIKE queries en SQL | LIKE '%term%' no usa índices. Los search engines usan inverted indexes diseñados para esto. |

---

## 5. Anti-patrones

| Anti-patrón | Por qué es malo | Qué hacer en su lugar |
|-------------|-----------------|----------------------|
| **N+1 Query Problem** | Por cada registro en una lista, se hace una query adicional. 100 usuarios = 101 queries. La DB se destruye. | Usar JOINs o eager loading del ORM. Analizar queries con EXPLAIN. |
| **No usar índices** | Queries lentas en tablas grandes. Un SELECT sin índice es un full table scan. Con 10M rows, es catastrófico. | Agregar índices en columnas usadas en WHERE, JOIN, ORDER BY. Monitorear slow query log. |
| **Transacciones largas** | Bloquean rows/tables por mucho tiempo. Otros queries esperan. Latencia escala con el tiempo de la transacción. | Mantener transacciones cortas. Mover lógica de negocio fuera de la transacción cuando es posible. |
| **Usar MongoDB porque "el schema cambia mucho"** | El schema siempre converge. Los documentos anidados sin schema crean inconsistencias silenciosas que son pesadillas de debuggear. | Si los datos tienen relaciones, usar PostgreSQL. Si realmente el schema varía (ej: metadata de productos), usar JSONB en PostgreSQL. |
| **Sincronizar servicios via DB compartida** | Dos servicios escriben/leen la misma DB. Ahora están acoplados. Un cambio de schema rompe ambos. | Servicios se comunican via API o mensajes. Cada servicio es dueño de sus datos. |

---

## 6. Casos y Ejemplos Reales

### Caso 1: Twitter — El Problema del Fanout

- **Situación:** Cuando un usuario con 10M followers tuitea, ¿cómo mostrarlo a todos en su feed?
- **Decisión 1 (Pull):** Al abrir el feed, calcular todos los tweets de las personas que sigues. Con 10M followers de celebridades, demasiado costoso.
- **Decisión 2 (Push/Fanout on write):** Al publicar, escribir el tweet en el "mailbox" de cada follower. 10M followers = 10M escrituras. Lento para celebridades.
- **Solución:** Híbrido. Usuarios normales con fanout on write. Celebridades con pull en el momento de lectura y merge.
- **Lección:** No hay una solución universal. El patrón de acceso (lectura vs escritura) determina la arquitectura.

### Caso 2: WhatsApp — Simplicidad y Escala

- **Situación:** 2 millones de conexiones concurrentes por servidor con solo 50 ingenieros.
- **Decisión:** Usar Erlang (diseñado para sistemas concurrentes) en lugar de Node o Java. Base de datos simple, sin joins complejos.
- **Resultado:** La simplicidad del modelo de datos permitió escala extrema con equipo pequeño.
- **Lección:** La tecnología correcta para el patrón de acceso específico supera al "stack popular".

### Caso 3: Equipo Startup — N+1 en Producción

- **Situación:** La página de órdenes de un e-commerce carga en 8 segundos. Base de datos pequeña todavía.
- **Decisión:** Después de monitorear, se detectaron 1,847 queries para cargar 50 órdenes con sus productos.
- **Resultado:** Al usar `include` del ORM correctamente (eager loading), la misma página cargó en 0.3 segundos.
- **Lección:** N+1 es el error más común y más silencioso. Siempre monitorear el número de queries, no solo el tiempo total.

---

## Conexión con el Cerebro #5

| Habilidad del Cerebro | Aporte de esta fuente |
|-----------------------|----------------------|
| Selección de base de datos | Decision tree completo para elegir la tecnología según el patrón de acceso |
| Diseño de sistemas distribuidos | CAP theorem, replicación y particionado con trade-offs explícitos |
| Performance de queries | Indexing, N+1, transacciones largas como anti-patrones con soluciones |
| Arquitectura de eventos | Kafka como log de verdad, batch vs stream como paradigmas |
| Consistencia vs disponibilidad | Framework de decisión para sistemas financieros vs sistemas sociales |
| Idempotencia | Modelo mental fundamental para APIs y operaciones críticas |

---

## Preguntas que el Cerebro puede responder

1. ¿Cuándo usar PostgreSQL vs MongoDB vs DynamoDB? ¿Cómo decido?
2. ¿Qué es el teorema CAP y cómo afecta mi elección de base de datos?
3. ¿Por qué mi aplicación hace demasiadas queries a la base de datos?
4. ¿Cómo escalo una base de datos cuando una sola máquina no alcanza?
5. ¿Cuándo necesito Kafka o un message queue en lugar de llamadas directas entre servicios?
6. ¿Cómo diseño una operación que sea segura de reintentar (idempotente)?
