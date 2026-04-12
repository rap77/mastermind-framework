# Login 403 Error - Next.js 16 Standalone Docker

## Problem
Server Actions return error 403 with httpStatus 200 when executed from Docker standalone build.

## Error Details
```
Uncaught (in promise) {
  name: 'n',
  httpError: false,
  httpStatus: 200,
  httpStatusText: '',
  code: 403,
  …
}
```

## Diagnosis Results

### What Works ✅
1. **Backend API:** `curl -X POST http://localhost:8001/api/auth/login` devuelve tokens válidos
2. **Dev Server:** `pnpm dev` en puerto 3002 funciona perfectamente
3. **Connectivity:** `wget http://api:8001/` desde contenedor web funciona
4. **Login HTML:** Generado correctamente en `/app/.next/server/app/(auth)/login.html`
5. **Server Process:** Node escuchando en 0.0.0.0:3000 (verificado con netstat)

### What Fails ❌
1. **Standalone Build:** Server Actions en Docker standalone mode
2. **Error Location:** ANTES de que loginAction se ejecute (no logs de [loginAction])
3. **Client-side Error:** httpStatus: 200 pero code: 403 indica rechazo del cliente

## Hypothesis
**Next.js 16 Server Actions incompatibility with standalone output mode**

Evidence:
- `output: 'standalone'` en next.config.ts
- Dev server (no standalone) funciona
- Standalone build en Docker falla
- Error code 403 con status 200 sugiere validación del cliente fallando

## Attempted Fixes (None Worked)
1. ✗ Rebuild completo con --no-cache
2. ✗ serverActions.bodySizeLimit: '2mb'
3. ✗ useActionState → useFormState
4. ✗ Try/catch + console.log en loginAction
5. ✗ Root page redirect (/app/page.tsx → /login)

## Next Steps (Priority Order)
1. **Network Tab Analysis:** Abrir F12 → Network tab → intentar login → identificar request exacto que falla
2. **Downgrade Next.js:** Probar Next.js 15 si es un bug de versión
3. **Alternative Auth:** Considerar traditional API routes instead of Server Actions
4. **Check Middleware:** Revisar si hay middleware bloqueando requests

## Environment
- Next.js: 16.2.0
- Node: 22-alpine
- Output: standalone
- Runtime: Docker container
- Ports: 3001:3000 (host:container)

## Related Files
- apps/web/next.config.ts
- apps/web/src/app/(auth)/login/actions.ts
- apps/web/src/app/(auth)/login/page.tsx
- docker/web/Dockerfile
