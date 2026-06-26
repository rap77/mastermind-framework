# Source Ingestion, Diff, and Update Workflow

## 1. Propósito

Definir cómo MasterMind captura una fuente externa nueva o actualizada, compara su delta, decide qué adoptar y preserva el análisis para no perderlo con cambios futuros.

## 2. Tesis central

Las fuentes externas no se integran “una vez y ya”. Se ingieren como snapshots versionadas, se comparan contra la versión anterior y dejan trazabilidad durable en docs canónicos, registry y memoria.

## 3. Cuándo se usa

Este workflow se usa cuando:

- aparece una fuente nueva
- una fuente existente publica una nueva versión
- cambian capabilities, riesgos o anti-patterns
- hay que revalidar una adopción anterior
- se quiere comparar Hermes, ECC, gentle-ai u otros repos con el core de MasterMind

## 4. Entradas mínimas

El workflow acepta:

- `source_id`
- URL, repo o path
- snapshot actual o commit/tag
- snapshot previa, si existe
- objetivo de análisis
- criterios de adopción
- constraints de tokens, seguridad y alcance

## 5. Salidas mínimas

Cada ejecución debe producir:

- snapshot registrada
- diff resumido
- capabilities detectadas
- anti-patterns detectados
- estado de adopción
- decisión razonada
- actualización canónica si aplica
- escritura de memoria durable
- auditoría de cambios

## 6. Flujo operativo

### 6.1 Captura

1. Registrar la fuente.
2. Tomar snapshot exacta.
3. Guardar hash, commit, tag o ref equivalente.
4. Asociar fecha de captura y propósito.

### 6.2 Normalización

1. Resumir la snapshot.
2. Extraer capabilities.
3. Extraer anti-patterns.
4. Extraer restricciones y dependencias.
5. Reducir el texto a contexto mínimo útil.

### 6.3 Comparación

1. Buscar snapshot anterior.
2. Comparar capabilities.
3. Comparar riesgos.
4. Comparar costos de integración.
5. Comparar compatibilidad con el core.
6. Identificar cambios materiales.

### 6.4 Decisión

Clasificar cada hallazgo como:

- `adopted`
- `adapted`
- `candidate`
- `rejected`
- `deprecated`

La decisión debe registrar:

- por qué se eligió
- qué se conserva
- qué se modifica
- qué se descarta
- qué riesgo nuevo aparece

### 6.5 Canonicalización

Si el delta cambia la arquitectura o el plan:

- actualizar doc canónico correspondiente
- crear o actualizar decision record
- actualizar source registry
- actualizar memory durable
- enlazar la fuente con la decisión

## 7. Regla de no pérdida

Nada importante se queda solo en el chat.

Si una fuente cambió, el sistema debe conservar:

- snapshot anterior
- snapshot nueva
- delta resumido
- decisión tomada
- razón de la decisión
- impacto sobre MasterMind

## 8. Política de actualización

### 8.1 Lo que nunca se debe hacer

- sobrescribir el análisis previo sin delta
- perder snapshots históricas
- borrar una decisión vieja sin sucesora
- reemplazar un artefacto canónico sin trazabilidad
- asumir que la nueva versión conserva automáticamente lo útil

### 8.2 Lo que sí se debe hacer

- registrar el cambio mínimo necesario
- conservar el contexto de adopción
- actualizar solo los docs afectados
- revalidar si cambió el costo o el riesgo
- mantener el resumen corto para ahorrar tokens

## 9. Relación con otros artefactos

Este workflow alimenta:

- `66-SOURCE-REGISTRY-AND-DELTA-PROTOCOL.md`
- `72-SOURCE-REGISTRY-SCHEMA.md`
- `74-CAPABILITY-REGISTRY-SERVICE.md`
- `75-MEMORY-RETRIEVAL-SERVICE.md`
- `76-AI-DLC-HARNESS-SPEC.md`

## 10. Adaptación para Hermes y otros repos

Para Hermes, ECC, gentle-ai y futuros repos:

1. capturar snapshot estable
2. resumir memoria, harnesses, MCP, workflows y artefactos
3. separar lo que es core, opcional y anti-pattern
4. comparar contra la arquitectura de MasterMind
5. decidir adopción, adaptación o rechazo
6. documentar delta para futuras versiones

## 11. Criterios de adopción

Una capability externa solo entra al core si cumple varias de estas condiciones:

- reduce tokens
- mejora trazabilidad
- mejora seguridad
- se puede versionar
- no rompe la arquitectura de cerebros especializados
- encaja con el selector de harness
- no agrega complejidad innecesaria

## 12. Token policy

El workflow debe operar con:

- resumen primero
- metadata primero
- top-k contexto
- snapshots pequeñas
- decisiones explícitas
- sin re-leer todo si solo cambió una parte

## 13. No-goals

- no convertir la fuente externa en la arquitectura principal
- no duplicar todo lo que existe en el repo externo
- no perder el historial por una actualización nueva
- no hacer migraciones implícitas
- no guardar contexto bruto sin síntesis

## 14. Resultado esperado

Con este workflow, MasterMind puede volver a revisar Hermes u otras fuentes en el futuro sin perder:

- qué se analizó
- qué se adoptó
- qué se rechazó
- por qué
- en qué snapshot exacta se basó la decisión
