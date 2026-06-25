# Business Rules — UOW-1 Governance Core

## Rule Group 1 — Scope

### BR-1.1
Una intención solo puede ejecutarse si todos sus targets están dentro del scope permitido de la tarea.

### BR-1.2
Si una intención toca archivos sensibles no listados en el scope explícito, el sistema debe devolver `deny`.

### BR-1.3
Cambios en CI, deploy, infra, billing, auth o migrations fuera del task scope son denegados.

## Rule Group 2 — Secrets

### BR-2.1
Cualquier intención que exponga o mueva secretos, tokens, cookies o headers de autenticación debe ser denegada.

### BR-2.2
La presencia de paths o patrones equivalentes a `.env`, credenciales cloud o API keys dispara `deny`.

## Rule Group 3 — Risk

### BR-3.1
Operaciones destructivas irreversibles (`rm -rf`, `git reset --hard`, `git clean -fdx`, borrado masivo) se deniegan siempre.

### BR-3.2
Acciones de side effects externos no reversibles requieren deny salvo que exista un modo dry-run validado y aprobación explícita; en ausencia de ambos, deny.

## Rule Group 4 — Production Writes

### BR-4.1
Writes a producción (`POST/PUT/PATCH/DELETE`) sin dry-run y aprobación explícita se deniegan.

### BR-4.2
Reads a producción no se bloquean por esta regla si no mutan estado y están dentro del scope operativo permitido.

## Rule Group 5 — Main Branch Protection

### BR-5.1
Push, merge, release o tagging a `main/master` sin aprobación explícita se deniega.

## Rule Group 6 — Large Change Approval

### BR-6.1
Si el cambio proyectado afecta >20 archivos, >500 LOC netos o directorios sensibles, el veredicto es `pause_and_ask`.

### BR-6.2
La aprobación humana puede convertir ese `pause_and_ask` en `allow`, pero nunca sobreescribe una regla de `deny`.

## Rule Group 7 — Auditability

### BR-7.1
Toda evaluación debe persistir evidencia append-only.

### BR-7.2
No puede existir delegación al `Coordinator` sin evento de evaluación asociado.

## Rule Group 8 — Determinism

### BR-8.1
Las reglas de governance se ejecutan sin consultas a LLM.

### BR-8.2
Dados la misma `Intention` y el mismo `TaskContext`, el veredicto debe ser idéntico.

## Rule Group 9 — Error Handling

### BR-9.1
Si una policy no puede evaluarse con seguridad por datos faltantes críticos, el resultado debe degradar a `pause_and_ask`, no a `allow`.

### BR-9.2
Si el audit writer falla, la ejecución no debe continuar a `Coordinator` porque se pierde trazabilidad mínima.
