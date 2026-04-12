# Session: Phase 17 Login Debug - 2026-04-08

## Status: BLOCKED - Login 403 Error

### Completed Work
✅ Phase 17.1 (Three-Column Layout Foundation) - Código completo
- 439/439 tests passing (+32 nuevos)
- ~640 LOC de código (components, stores, CSS)
- layoutStore (Zustand + Immer + persist)
- ThreeColumnLayout, CompanyRail, AppSidebar
- Responsive breakpoints, CSS variables
- Integration en protected layout

### Critical Blocker
🔴 **Login 403 Error - Next.js 16 Server Actions en Docker standalone**

**Error:** `Uncaught (in promise) {name: 'n', httpError: false, httpStatus: 200, httpStatusText: '', code: 403, …}`

**Diagnosis:**
- Backend funciona: `curl http://localhost:8001/api/auth/login` devuelve tokens válidos
- Dev server local funciona: `pnpm dev` en puerto 3002
- Conectividad web→api funciona: `wget http://api:8001/` desde contenedor
- Login HTML generado correctamente en build standalone
- Error ocurre ANTES de que loginAction se ejecute (no logs en contenedor)
- Problema ESPECÍFICO de Next.js 16 Server Actions en Docker standalone mode

**Files Modified (not committed):**
- `apps/web/src/stores/layoutStore.ts` (new)
- `apps/web/src/components/layout/ThreeColumnLayout.tsx` (new)
- `apps/web/src/components/layout/CompanyRail.tsx` (new)
- `apps/web/src/components/layout/AppSidebar.tsx` (new)
- `apps/web/src/app/page.tsx` (new - root redirect)
- `apps/web/src/app/(protected)/layout.tsx` (modified)
- `apps/web/src/app/(auth)/login/actions.ts` (modified - logging added)
- `apps/web/next.config.ts` (modified - serverActions config)

### Next Steps (Priority Order)
1. **DEBUG LOGIN 403** - Browser DevTools → Network tab → identificar request fallido
2. Manual verification de three-column layout (una vez login funcione)
3. Create 17-01-SUMMARY.md con validation results
4. Commit Phase 17.1 (SÓLO después de que login funcione)

### Environment
- Branch: master
- Last commit: 8279208 (wip: Phase 17 paused)
- Backend: http://localhost:8001 (healthy)
- Frontend: http://localhost:3001 (login broken)
- Dev server: http://localhost:3002 (works for testing)

### Brain #7 Approval
Phase 17 recibió 94/100 (unconditional approval) tras cumplir 4 condiciones:
- Mobile Testing Strategy ($39/month BrowserStack)
- RAF Validation Plan (PR blocking)
- Visual Regression Baseline (Playwright)
- Accessibility Audit (axe-core)
