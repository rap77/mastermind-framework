# NFR Design Plan — UOW-5 Core Runtime Contracts

## Scope

Incorporar los NFR de UOW-5 al diseño lógico del runtime para que
multi-harness + multi-loop opere con control bounded, continuidad y selección
determinista desde el primer slice.

## Plan

- [x] Mapear NFR-P5.* / NFR-S5.* / NFR-A5.* / NFR-R5.* / NFR-M5.* / NFR-O5.*
      a patrones runtime concretos
- [x] Definir patrones mínimos para selección determinista, bounded control,
      maker-checker y degraded-safe fallback
- [x] Definir componentes lógicos necesarios para aplicar esos patrones sin
      introducir infraestructura externa nueva
- [x] Validar que los componentes preserven adopción incremental sobre
      governance, budget y memory eval
- [x] Preparar artifacts de diseño listos para code generation del slice
      `envelope-contract-loop-selector-v1`

## Clarification Status

No se agregaron preguntas `[Answer]:` en esta corrida porque ya quedó fijado
en artifacts previos y feedback del usuario que:

- el runtime debe hacer explícito multi-harness y multi-loop
- el control debe ser mínimo pero suficiente
- los loops deben declarar validación, aceptación, finalización y escalación
- la continuidad debe depender de artifacts persistidos, no de memoria viva
- el target ECC-like se conserva como dirección futura, no como scope del MVP
