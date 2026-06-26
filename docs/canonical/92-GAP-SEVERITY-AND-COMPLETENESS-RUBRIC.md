# Gap Severity and Completeness Rubric

## 1. Propósito

Definir cómo clasificar gaps y qué nivel de completitud es suficiente para seguir avanzando.

## 2. Tesis central

No todos los gaps bloquean igual. La severidad decide si se pregunta, se posterga o se detiene el flujo.

## 3. Gap severity

### 3.1 Critical

- bloquea la especificación
- afecta scope, comportamiento central o seguridad
- requiere cierre antes de seguir

### 3.2 Important

- impacta la calidad de la spec o del diseño
- idealmente se cierra antes de implementación

### 3.3 Optional

- mejora el contexto
- puede quedar para iteración posterior

## 4. Completeness levels

### 4.1 Full

- cubre objetivo, alcance, decisiones principales y restricciones

### 4.2 Near-full

- cubre lo esencial
- faltan detalles no bloqueantes

### 4.3 Partial

- hay estructura útil pero faltan piezas clave

### 4.4 Insufficient

- no permite generar una spec confiable

## 5. Operational rule

- `Critical gaps > 0` => no spec
- `Important gaps` => prefer interview o nueva evidencia
- `Optional gaps` => registrar, pero no bloquear

## 6. No-goals

- no llamar “completo” a algo con huecos críticos
- no mezclar opcional con bloqueante
- no seguir por inercia cuando la cobertura es insuficiente
