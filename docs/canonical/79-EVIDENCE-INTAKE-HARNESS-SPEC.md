# Evidence Intake Harness Spec

## 1. Propósito

Definir un harness fuente-agnóstico para ingerir evidencia de repositorios, páginas de producto, documentos, libros, sistemas existentes y otras referencias útiles.

## 2. Tesis central

MasterMind no aprende solo de repos. Aprende de cualquier evidencia que permita extraer patrones, capacidades, restricciones y anti-patterns con suficiente confianza.

## 3. Alcance

Este harness se usa cuando la entrada puede venir de:

- repositorios
- páginas de producto
- sistemas existentes
- documentación técnica
- libros
- artículos
- notas internas
- entrevistas o transcripciones

## 4. Entradas

El harness acepta:

- `evidence_id`
- tipo de fuente
- ubicación de la fuente
- snapshot o extracto
- objetivo del análisis
- contexto del usuario
- constraints de tokens, seguridad y tiempo

## 5. Salidas

Cada ejecución debe producir:

- resumen breve
- capabilities detectadas
- anti-patterns detectados
- restricciones
- supuestos explícitos
- nivel de confianza
- gaps potenciales
- candidate canon blocks

## 6. Flujo

### 6.1 Capture

Tomar la evidencia exacta o el extracto mínimo representativo.

### 6.2 Normalize

Convertir la evidencia en un formato comparable:

- resumen
- metadatos
- ideas clave
- términos importantes

### 6.3 Extract

Extraer:

- patrones
- funciones
- flujos
- restricciones
- riesgos
- anti-patterns

### 6.4 Canonize

Transformar lo útil en bloques canónicos reutilizables.

### 6.5 Score

Asignar confianza y relevancia a cada hallazgo.

## 7. Reglas

- no asumir que una fuente es completa
- no mezclar evidencia con decisión final
- no guardar texto bruto sin síntesis
- no limitar el intake a repositorios
- no pasar a spec si faltan gaps críticos

## 8. Token policy

El harness debe operar con:

- resumen primero
- metadata primero
- top-k extracción
- evidencia mínima suficiente
- no re-leer todo si ya existe un resumen confiable

## 9. Relación con otros componentes

Este harness alimenta:

- gap detection
- clarification loop
- source registry
- capability registry
- memory layer
- canonical docs

## 10. No-goals

- no reemplazar al usuario cuando falta información
- no inferir specs completos desde una evidencia incompleta
- no convertir cualquier texto en una verdad canónica sin validación
