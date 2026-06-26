# Evidence Contradiction Resolution Policy

## 1. Propósito

Definir cómo MasterMind maneja contradicciones entre fuentes, extractos, respuestas del usuario o versiones de una misma fuente.

## 2. Tesis central

Una contradicción no se ignora; se clasifica, se prioriza y se resuelve antes de pasar a spec.

## 3. Tipos de contradicción

### 3.1 Source vs source

Dos fuentes dicen cosas incompatibles.

### 3.2 Version vs version

Una fuente nueva cambia o revierte una decisión previa.

### 3.3 Source vs user answer

La fuente sugiere algo y el usuario confirma otra cosa.

### 3.4 Internal contradiction

Una misma fuente se contradice a sí misma.

## 4. Severity

- **Critical**: bloquea spec
- **Important**: requiere aclaración o nueva evidencia
- **Minor**: puede registrarse sin bloquear

## 5. Resolution flow

1. identificar la contradicción
2. clasificar tipo y severidad
3. buscar la fuente más confiable o más reciente
4. pedir aclaración al usuario si sigue dudoso
5. registrar la decisión y el delta

## 6. Resolution outcomes

- keep latest
- keep most authoritative
- prefer user intent
- mark unresolved
- split into alternatives

## 7. Rules

- no pasar una contradicción crítica por alto
- no asumir que lo nuevo siempre reemplaza lo viejo
- no resolver sin dejar trazabilidad

## 8. No-goals

- no forzar una decisión falsa
- no esconder contradicciones detrás de lenguaje vago
- no borrar la historia del conflicto
