---
source_id: "FUENTE-510"
brain: "brain-software-05-backend"
niche: "software-development"
title: "Radar Interno — Checklist de Evaluación y Anti-patrones del Cerebro #5"
author: "MasterMind Framework"
expert_id: "EXP-005"
type: "radar-interno"
language: "es"
year: 2026
url: ""
skills_covered: ["H1", "H2", "H3", "H4", "H5", "H6"]
distillation_date: "2026-02-27"
distillation_quality: "complete"
loaded_in_notebook: true
version: "1.0.0"
last_updated: "2026-02-27"
changelog:
  - version: "1.0.0"
    date: "2026-02-27"
    changes:
      - "Radar interno creado con checklist completo del Cerebro #5"
      - "Anti-patrones consolidados de todas las fuentes del cerebro"
status: "active"

habilidad_primaria: "Evaluación de calidad de código y decisiones de arquitectura backend"
habilidad_secundaria: "Detección de anti-patrones y deuda técnica"
capa: 3
capa_nombre: "Radar"
relevancia: "CRÍTICA — El radar es la herramienta de evaluación que usa el Cerebro #5 para validar outputs propios y del equipo."
---

# FUENTE-510: Radar Interno — Cerebro #5 Backend

## Tesis Central

> El Cerebro #5 no solo genera código y arquitecturas — también evalúa su calidad. Este radar es la herramienta de auto-evaluación que consolida los criterios de todas las fuentes del cerebro en checklists accionables. Un output del Cerebro #5 que pasa este radar tiene alta probabilidad de ser correcto, seguro, y mantenible.

---

## 1. Principios del Radar

> **P1: La Evaluación es Iterativa**
> No se evalúa una vez al final — se evalúa en cada decisión: al elegir un patrón, al escribir un test, al diseñar una API. El radar es un compañero continuo, no una auditoría puntual.

> **P2: Severidad Determina la Acción**
> Cada ítem del checklist tiene una severidad. CRÍTICO: bloquea el avance. ALTO: debe resolverse antes del merge. MEDIO: es deuda técnica documentada. El radar distingue entre errores que causan brechas de seguridad y olvidar un comentario.

> **P3: El Radar Evoluciona**
> Los anti-patrones se actualizan con cada post-mortem. Si un bug llega a producción, el radar se actualiza para que no vuelva a escapar.

---

## 2. Checklist de Arquitectura

### Capa de Dominio
```
✅ CRÍTICO: Las entidades de dominio NO importan nada de infraestructura (ORM, DB, HTTP)
✅ CRÍTICO: La Regla de Dependencia se respeta (dependencias apuntan hacia adentro)
✅ ALTO:    Los Aggregates tienen reglas de negocio encapsuladas (no en Services)
✅ ALTO:    Value Objects son inmutables y sin identidad propia
✅ MEDIO:   El código usa el Ubiquitous Language del dominio (nombres del negocio)
✅ MEDIO:   La estructura de carpetas refleja el dominio, no el framework
```

### Capa de Aplicación
```
✅ CRÍTICO: Los Use Cases no tienen lógica de infraestructura embebida
✅ ALTO:    Cada Use Case tiene una sola responsabilidad (SRP)
✅ ALTO:    Las dependencias se inyectan, no se instancian internamente
✅ MEDIO:   El Use Case tiene tests unitarios con mocks de repositorios
✅ MEDIO:   El Use Case tiene un output DTO separado del modelo de dominio
```

### Capa de Infraestructura
```
✅ CRÍTICO: No hay SQL con concatenación de strings (SQL Injection prevention)
✅ CRÍTICO: Los repositorios implementan interfaces definidas en el dominio
✅ ALTO:    El connection pool está configurado apropiadamente
✅ ALTO:    Los errores de infraestructura no exponen detalles técnicos al cliente
✅ MEDIO:   Las queries tienen índices en las columnas de filtro y join
```

---

## 3. Checklist de API

```
✅ CRÍTICO: Cada endpoint verifica autenticación Y autorización (ownership)
✅ CRÍTICO: El input del usuario está validado antes de procesarse
✅ CRÍTICO: Los errores no exponen stack traces ni detalles técnicos en producción
✅ ALTO:    Las colecciones tienen paginación (no retornar todos los registros)
✅ ALTO:    Los status codes HTTP son semánticamente correctos (201 create, 204 delete, etc.)
✅ ALTO:    Los errores tienen código de error legible por máquina y mensaje útil
✅ ALTO:    Los endpoints que modifican estado son idempotentes o tienen idempotency keys
✅ MEDIO:   La API sigue convenciones REST (sustantivos en URLs, verbos HTTP correctos)
✅ MEDIO:   Los cambios breaking generan una nueva versión de la API
✅ MEDIO:   Existe un contrato OpenAPI/Swagger actualizado
```

---

## 4. Checklist de Seguridad

```
✅ CRÍTICO: Los passwords se almacenan con bcrypt (cost≥12) o Argon2id
✅ CRÍTICO: Los JWTs tienen expiración corta (≤60 min) y los refresh tokens son rotativos
✅ CRÍTICO: No hay queries SQL construidas con concatenación de string + user input
✅ CRÍTICO: Los endpoints admin verifican rol de administrador explícitamente
✅ ALTO:    CORS tiene whitelist explícita, no wildcard (*)
✅ ALTO:    Las variables sensibles están en variables de entorno, no en el código
✅ ALTO:    Los errores en producción no exponen tecnología ni estructura interna
✅ ALTO:    El login tiene rate limiting (máx 5-10 intentos por IP/cuenta)
✅ MEDIO:   Las dependencias se auditan regularmente (npm audit, Dependabot)
✅ MEDIO:   Las acciones sensibles quedan en audit log
```

---

## 5. Checklist de Testing

```
✅ CRÍTICO: La lógica de negocio tiene tests unitarios (Use Cases y Domain Logic)
✅ ALTO:    Los repositorios tienen integration tests contra DB real
✅ ALTO:    Los endpoints críticos tienen E2E tests (auth, pagos, checkout)
✅ ALTO:    Cada bug corregido tiene un test que lo reproduce
✅ MEDIO:   Los tests corren en < 5 minutos localmente (sin E2E)
✅ MEDIO:   Los tests son independientes entre sí (no dependen del orden)
✅ MEDIO:   Los tests tienen nombres descriptivos del comportamiento esperado
```

---

## 6. Checklist de Performance

```
✅ CRÍTICO: No hay operaciones síncronas bloqueantes en el event loop de Node.js
✅ ALTO:    No hay N+1 queries (usar eager loading o joins explícitos)
✅ ALTO:    Las queries en tablas > 100K rows tienen índices apropiados
✅ ALTO:    El cache tiene TTL definido y estrategia de invalidación explícita
✅ MEDIO:   Las operaciones independientes usan Promise.all() (no await secuencial)
✅ MEDIO:   El procesamiento de archivos grandes usa Streams
✅ MEDIO:   El connection pool está dimensionado apropiadamente
```

---

## 7. Anti-patrones Consolidados del Cerebro #5

### Severidad CRÍTICA (bloquea el merge)

| # | Anti-patrón | Fuente | Señal de Detección |
|---|-------------|--------|-------------------|
| C1 | SQL Injection (concatenación de strings con user input) | FUENTE-509 | Buscar `query(... + variable)` o `WHERE ... ${variable}` |
| C2 | Passwords sin bcrypt/Argon2 (MD5, SHA, plaintext) | FUENTE-509 | Buscar `crypto.createHash('md5')` o `crypto.createHash('sha256')` para passwords |
| C3 | Violación de la Regla de Dependencia (dominio importa infraestructura) | FUENTE-501 | Buscar imports de ORM/DB en carpetas `domain/` o `application/` |
| C4 | Endpoint sin verificación de autenticación | FUENTE-509 | Endpoints sin middleware de auth en routes protegidas |
| C5 | Broken Access Control (no verifica ownership) | FUENTE-509 | Queries sin `AND user_id = $userId` en recursos del usuario |

### Severidad ALTA (debe resolverse antes del merge)

| # | Anti-patrón | Fuente | Señal de Detección |
|---|-------------|--------|-------------------|
| A1 | God Controller (lógica de negocio en el controller) | FUENTE-501, 504 | Controladores con > 30 líneas o con lógica condicional compleja |
| A2 | Anemic Domain Model (entidades sin comportamiento) | FUENTE-504, 507 | Entidades con solo getters/setters, toda lógica en Services |
| A3 | N+1 Query Problem | FUENTE-502, 504 | Loop con `await repository.findById()` dentro |
| A4 | No paginar colecciones | FUENTE-506 | Endpoints que retornan arrays sin `limit`/`offset` o cursor |
| A5 | JWT sin expiración o con expiración muy larga | FUENTE-509 | Payload JWT sin `exp` o con `exp` > 24h |
| A6 | Variables de entorno hardcodeadas | FUENTE-509 | Strings de conexión, secrets, API keys en el código |
| A7 | Stack traces expuestos en producción | FUENTE-509 | Error handler que retorna `err.stack` en la response |
| A8 | Await secuencial para operaciones independientes | FUENTE-508 | Múltiples `await` consecutivos que no dependen entre sí |

### Severidad MEDIA (deuda técnica documentada)

| # | Anti-patrón | Fuente | Señal de Detección |
|---|-------------|--------|-------------------|
| M1 | Estructura de carpetas por tipo, no por dominio | FUENTE-501 | Raíz con `controllers/`, `models/`, `services/` |
| M2 | Active Record en dominio complejo | FUENTE-504 | Entidades con `.save()`, `.find()` embebidos en el dominio |
| M3 | Tests que prueban implementación, no comportamiento | FUENTE-505 | Tests que verifican métodos fueron llamados, no outputs |
| M4 | God Aggregate (demasiadas entidades en un Aggregate) | FUENTE-507 | Aggregates con más de 5-7 entidades |
| M5 | Lenguaje del código diferente al lenguaje del negocio | FUENTE-507 | Términos técnicos donde el negocio usa términos de dominio |
| M6 | Dependencias sin auditar | FUENTE-509 | No tener Dependabot ni proceso de actualización |
| M7 | Sin índices en columnas de filtro frecuente | FUENTE-502 | Queries con `WHERE` en columnas sin índice en tablas grandes |

---

## 8. Scoring del Radar

Al evaluar un output del Cerebro #5, calcular el score:

```
Score = 100
- CRÍTICO incumplido: -20 puntos c/u
- ALTO incumplido:    -10 puntos c/u
- MEDIO incumplido:   -5 puntos c/u

Resultado:
≥ 90: APROBADO — Listo para producción
70-89: CONDICIONAL — Resolver ALTOs antes del merge
50-69: RECHAZADO — Requiere revisión significativa
< 50: RECHAZADO CRÍTICO — No mergear, rediseñar
```

---

## 9. Modelo Mental del Cerebro #5

### La Pregunta Central en Cada Decisión

Antes de cualquier decisión de diseño, el Cerebro #5 se pregunta:

1. **¿El dominio sigue siendo independiente?** (Clean Architecture)
2. **¿Escala si el tráfico se multiplica por 10?** (System Design)
3. **¿Qué pasa si este componente falla?** (Fault Tolerance)
4. **¿Un atacante puede abusar de esto?** (Security)
5. **¿Puedo testear esto sin infraestructura?** (Testability)
6. **¿Entendería esto en 6 meses?** (Maintainability)

Si alguna respuesta es "no" o "no sé", hay trabajo pendiente.

---

## Preguntas que el Cerebro puede responder (con este Radar)

1. ¿Está este código listo para ir a producción? ¿Qué falta?
2. ¿Tiene este diseño de API los problemas más comunes resueltos?
3. ¿Tiene este sistema las vulnerabilidades de seguridad más críticas mitigadas?
4. ¿Qué anti-patrones tiene este código y cuál es su severidad?
5. ¿Cuál es el score de calidad de este output del Cerebro #5?
6. ¿Qué deuda técnica tiene este sistema y cuál es la prioridad de pagarla?
