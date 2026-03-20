---
status: resolved
phase: 05-foundation-auth-ws
source: 05-00-SUMMARY.md, 05-01-SUMMARY.md, 05-02-SUMMARY.md, 05-03-SUMMARY.md, 05-04-SUMMARY.md
started: 2026-03-20T00:00:00Z
updated: 2026-03-20T03:40:00Z
---

## Current Test

[testing complete]

## Tests

### 1. Cold Start Smoke Test
expected: Detener todos los contenedores Docker (docker compose down). Limpiar estado efímero si existe. Iniciar la aplicación desde cero (docker compose up -d). Esperado: Ambos contenedores (api y web) inician sin errores, healthcheck pasa, y la aplicación responde (curl http://localhost:3000/login devuelve HTML).
result: pass

### 2. Next.js 16 Build — Sin errores TypeScript
expected: Ejecutar `cd apps/web && pnpm build`. Esperado: Build completa exitosamente sin errores de TypeScript. Output muestra "✓ Compiled" o similar, no hay errores de compilación.
result: pass

### 3. Login Page — Renderiza correctamente
expected: Visitar http://localhost:3000/login (en navegador). Esperado: Login page visible con campos username/password, botón de submit shadcn/ui styling, no errores de consola.
result: pass

### 4. Login — Autenticación funcional
expected: En la página /login, ingresar credenciales válidas (username/password) y hacer submit. Esperado: Redirección a / (página protegida), cookies httpOnly almacenadas (verificable en DevTools → Application → Cookies).
result: pass

### 5. Auth Guard — Ruta protegida redirige a /login
expected: 1) Cerrar sesión o limpiar cookies. 2) Visitar http://localhost:3000/ directamente. Esperado: Redirección automática a /login, no acceso a contenido protegido sin autenticación.
result: pass

### 6. JWT Verification — Dual-layer working
expected: Estar logueado. Abrir DevTools → Network. Recargar la página. Esperado: Request a / devuelve 200, headers incluyen cookies, no redirección a /login. (Prueba que proxy.ts + AuthGuardLayout ambos verifican JWT correctamente).
result: pass

### 7. CORS — FastAPI acepta requests desde localhost:3000
expected: En DevTools → Console, no debería haber errores de CORS como "blocked by CORS policy". Requests a /api/auth/login desde el frontend deberían completar exitosamente.
result: pass

### 8. Zod Schema Generator — Produce tipos válidos
expected: Ejecutar `cd apps/web && pnpm run generate:types`. Esperado: Script corre sin errores, apps/web/src/types/api.ts se actualiza con schemas Zod válidos (LoginRequest, TokenResponse, BrainEvent, WSMessage).
result: pass

### 9. WebSocket Store — SSR-safe init
expected: Ejecutar `cd apps/web && pnpm build`. Esperado: Build completa sin errores "ReferenceError: window is not defined" o similar. (Prueba que wsStore no inicializa WebSocket a nivel módulo).
result: pass

### 10. Brain Store — RAF batching funciona
expected: Estar logueado, visitar http://localhost:3000/. Hacer clic en "Simulate 24 Brain Events" button en la test page. Esperado: UI actualiza 24 tiles sin freeze perceptible, animación suave a 60fps (no se congela el navegador).
result: pass
fixed_by: "Plan 05-04 — Immer mutation error fixed in updateBrain()"
verified: "2026-03-20T03:40:00Z"

### 11. Targeted Selectors — Single brain update no cascade
expected: En la test page con 24 brain tiles, observar que solo el tile específico se actualiza cuando un brain individual cambia de estado (no todos los 24 tiles re-render).
result: pass
verified: "2026-03-20T03:40:00Z"

### 12. WS Token Handoff — /api/auth/token endpoint
expected: Estar logueado. Ejecutar `curl -X GET http://localhost:3000/api/auth/token -H "Cookie: access_token=..."`. Esperado: 200 con token en JSON response, o 401 si cookie inválida. (Prueba que endpoint lee httpOnly cookie server-side).
result: pass

### 13. Rate Limiting — /api/auth/token DoS protection
expected: Ejecutar `for i in {1..15}; do curl -s http://localhost:3000/api/auth/token; done` (más de 10 requests). Esperado: Después de 10 requests, responses retornan 429 status con header "Retry-After".
result: pass

## Summary

total: 13
passed: 13
issues: 0
pending: 0
skipped: 0

## Gaps

- truth: "Brain Store RAF batching funciona — 24 brain events actualizan UI sin freeze a 60fps"
  status: resolved
  reason: "Fixed in plan 05-04: updateBrain() now mutates state inside set() callback with mutable Immer draft"
  severity: major
  test: 10
  root_cause: "Línea 28 en brainStore.ts muta estado congelado por Immer (get()._queue.push(brain)) en lugar de usar set() con draft state mutable"
  artifacts:
    - path: "apps/web/src/stores/brainStore.ts"
      issue: "Direct mutation of frozen state object outside of Immer's set()"
      line: 28
      fix: "Moved all mutations inside set(state => { ... }) callback"
  missing: []
  fix_plan: "05-04-PLAN.md"
  fix_summary: "05-04-SUMMARY.md"
