# Canonization Loop and Final Summary

## 1. Propósito

Definir un loop cerrado para canonicación que acepta recomendaciones iterativas, ejecuta cambios pequeños y termina con un resumen completo auditable.

## 2. Tesis central

La canonicación debe sentirse rápida y cerrada: cada iteración recomienda, aplica, verifica y resume.

## 3. Cuándo usarlo

Usar este loop cuando:

- se está construyendo o refinando canon canónico
- el usuario quiere revisar recomendaciones antes de avanzar
- la salida debe terminar en un resumen completo de decisiones y acciones
- se quiere reducir sensación de latencia entre pasos

## 4. Ciclo operativo

### 4.1 Recolectar

Tomar el bloque actual de contexto, cambios o decisión a canonizar.

### 4.2 Recomendar

Emitir la siguiente acción concreta más útil.

### 4.3 Aceptar o ajustar

El usuario aprueba, corrige o cambia el rumbo.

### 4.4 Ejecutar

Aplicar el cambio pequeño y verificable.

### 4.5 Verificar

Confirmar que el cambio quedó consistente con el canon y con los artefactos relacionados.

### 4.6 Cerrar

Producir un cierre con estado claro.

## 5. Final summary obligatorio

Al cerrar cada ciclo, el loop debe emitir un resumen final con estas secciones:

- **Hecho**: qué se cambió
- **Decisión**: qué se decidió y por qué
- **Recomendación siguiente**: siguiente paso concreto
- **Resumen del bloque**: listado compacto de decisiones y acciones
- **Open items**: lo que quedó pendiente

## 6. Formato de salida recomendado

```text
HECHO:
- ...

DECISIÓN:
- ...

RECOMENDACIÓN SIGUIENTE:
- ...

RESUMEN DEL BLOQUE:
- ...

OPEN ITEMS:
- ...
```

## 7. Reglas

- no dejar el ciclo abierto sin cierre
- no omitir la recomendación siguiente
- no mezclar múltiples cambios grandes en una sola iteración
- no cerrar sin resumen final
- no saltar verificación cuando cambió el canon

## 8. Relación con otros loops

Este loop puede usar:

- Tool Loop para tareas puntuales
- Goal Loop para cerrar objetivos concretos
- Verification Loop para confirmar el resultado
- Reflection Loop cuando haga falta refinar
- Recovery Loop si surge un fallo

## 9. No-goals

- no reemplaza la planificación de alto nivel
- no sustituye el evidence loop o AI-DLC
- no sirve para cambios masivos sin partición
