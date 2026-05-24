# Collaboration and RBAC Model

## 1. Propósito

Definir cómo participan humanos y agentes en un mismo proyecto, con roles, permisos y handoffs auditables.

---

## 2. Qué resuelve

- trabajo en equipo humano + agentes
- ownership claro por tarea
- approvals
- permisos para costos, overrides y automatización
- handoffs limpios entre participantes

---

## 3. Participantes

### Humanos
- owner
- architect
- implementer
- reviewer
- approver
- observer

### Agentes / brains
- planner
- executor
- critic
- evaluator
- synthesizer

---

## 4. Permisos mínimos

- ver proyecto
- editar artefactos
- aprobar decisiones
- lanzar runs automáticos
- autorizar costos altos
- aprobar overrides de doctrina
- aprobar acciones de alto riesgo

---

## 5. Handoffs

Todo handoff debe registrar:

- origen
- destino
- tarea
- motivo
- checkpoint asociado
- next step

---

## 6. Principios

1. Todo proyecto debe tener ownership humano explícito.
2. Ninguna automatización crítica sin permisos claros.
3. Humanos y agentes deben verse como participantes del mismo flujo.
4. Los handoffs son artefactos de continuidad, no mensajes informales.

## Key Learnings:

1. La colaboración real requiere roles y permisos, no solo actividad compartida.
2. Los handoffs deben ser estructurados y auditables.
3. El sistema debe gobernar tanto intervención humana como autonomía agente.
