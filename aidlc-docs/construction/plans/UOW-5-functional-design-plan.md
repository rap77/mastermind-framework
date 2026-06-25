# Functional Design Plan — UOW-5 Core Runtime Contracts

## Scope

Diseñar el núcleo contractual que permita a MasterMind operar con
multi-harness y multi-loop sin depender de comportamiento implícito.

## Plan

- [x] Analizar cómo encaja el nuevo slice con `Coordinator`, `mm_flow` y
      `memory_layer`
- [x] Modelar entidades de dominio para task profiling, loop policy, harnesses,
      capabilities y envelopes
- [x] Definir reglas de negocio para loop selection, maker-checker split,
      envelope validity y recovery bounded
- [x] Definir el flujo lógico entre `HarnessRegistry`, `LoopSelector`,
      `CapabilityRegistry` y los harnesses de ejecución/verificación/recovery
- [x] Validar consistencia con los requisitos FR-11..FR-18 y NFR-8..NFR-10

## Clarification Status

No se agregaron preguntas `[Answer]:` en esta corrida porque el usuario ya
fijó explícitamente:

- que multi-harness y multi-loop deben quedar explícitos
- que la validación, aceptación y finalización deben modelarse por loop
- que el target state tipo ECC debe preservarse como dirección, sin inflar el
  scope inmediato
