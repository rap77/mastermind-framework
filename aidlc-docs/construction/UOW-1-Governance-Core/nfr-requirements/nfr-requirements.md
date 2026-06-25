# NFR Requirements — UOW-1 Governance Core

## Purpose

Definir las cualidades operativas mínimas que debe cumplir el interceptor de governance para ser seguro, determinista y adoptable en el codebase actual sin romper el flujo existente.

## 1. Performance

### NFR-P1 — Bajo overhead de decisión
- La evaluación completa del `PolicySet` debe agregar menos del 5% del presupuesto total de una tarea.
- La evaluación debe usar reglas deterministas en memoria y evitar llamadas remotas en el camino crítico.

### NFR-P2 — Fast fail
- La primera policy que produzca `deny` o `pause_and_ask` debe cortar la cadena sin seguir evaluando policies restantes.
- La construcción de `Intention` y `TaskContext` debe usar solo datos ya disponibles en el contexto del caller o derivados localmente.

### NFR-P3 — Costo predecible
- La complejidad temporal de evaluación debe crecer linealmente con el número de policies configuradas.
- El release inicial debe mantener un `PolicySet` pequeño, fijo y ordenado.

## 2. Security

### NFR-S1 — Interceptación total de acciones de alto riesgo
- El 100% de acciones destructivas, writes a producción, operaciones sobre secretos y acciones sobre `main/master` debe pasar por governance antes de ejecutar side effects.

### NFR-S2 — Política deny-by-default para incertidumbre crítica
- Si faltan datos críticos para evaluar una intención de forma segura, el sistema no puede producir `allow`.
- El fallback mínimo permitido es `pause_and_ask`.

### NFR-S3 — Sin exposición de secretos en evidencia
- La evidencia persistida debe redactar o excluir secretos, tokens, cookies, headers sensibles y payloads equivalentes.
- Los eventos deben conservar trazabilidad suficiente sin almacenar credenciales reales.

## 3. Availability and Continuity

### NFR-A1 — Continuidad cross-session
- Las decisiones y evidencia de governance deben sobrevivir reinicios de proceso.
- La persistencia MVP debe ser append-only y legible para reanudación manual o automática.

### NFR-A2 — Comportamiento seguro ante falla
- Si el audit writer falla, la acción no debe delegarse al `Coordinator`.
- Fallas de persistencia deben generar un resultado bloqueante y trazable.

### NFR-A3 — Degradación segura
- La indisponibilidad de servicios futuros no críticos (por ejemplo stores alternos) no debe degradar la decisión a `allow`.
- El MVP debe poder operar con almacenamiento local JSON Lines sin dependencia de red.

## 4. Reliability and Determinism

### NFR-R1 — Determinismo fuerte
- Dada la misma `Intention`, `TaskContext` y orden de `PolicySet`, el veredicto debe ser idéntico.
- Las policies deben ser funciones puras respecto al veredicto.

### NFR-R2 — Trazabilidad replayable
- Toda decisión debe producir evidencia suficiente para reconstruir: intención evaluada, policy disparada, veredicto y razón.
- La evidencia debe ser parseable por morning reports, meta-loop y tooling de auditoría.

### NFR-R3 — Orden estable de evaluación
- El orden del `PolicySet` debe ser explícito, estable y testeado.
- Cambios al orden deben considerarse cambios de comportamiento observable.

## 5. Maintainability and Testability

### NFR-M1 — Backward compatibility
- `Coordinator` debe aceptar governance por constructor con default `None`.
- La feature debe poder deshabilitarse en tests o flujos legacy sin modificar callers existentes.

### NFR-M2 — Testabilidad aislada
- Cada policy debe poder probarse en aislamiento con fixtures de `Intention` y `TaskContext`.
- Deben existir tests de integración para cadena completa, short-circuit y fail-closed del audit writer.

### NFR-M3 — Evolución controlada
- El diseño debe permitir añadir/remover policies sin reescribir el `Coordinator`.
- La frontera entre interceptor, policies y writer de evidencia debe mantenerse explícita.

## 6. Operability

### NFR-O1 — Razones accionables
- `deny` y `pause_and_ask` deben devolver reason codes y mensajes comprensibles para operador o caller.

### NFR-O2 — Evidence shape estable
- El schema lógico del `AuditEvent` debe ser estable desde el MVP para evitar migraciones tempranas de consumidores.

### NFR-O3 — Observabilidad mínima
- El sistema debe poder contar decisiones por tipo de veredicto y policy disparada a partir del evidence chain sin procesamiento ambiguo.

## 7. Success Thresholds for UOW-1

- 100% de acciones de alto riesgo interceptadas antes del `Coordinator`
- 0 delegaciones a `Coordinator` sin evidencia persistida
- overhead de governance por debajo del 5% del budget de tarea
- tests deterministas para allow / deny / pause_and_ask / audit-failure
